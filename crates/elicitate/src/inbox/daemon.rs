//! Inbox daemon — long-running process that:
//! 1. Serves the HTML inbox UI on `http://127.0.0.1:7117/inbox/<id>`.
//! 2. Receives `POST /answer/<id>` from the HTML form and persists the
//!    answer to `answered/` so the agent's `elicitate wait` returns.
//! 3. Polls the inbox directory and surfaces new requests via the
//!    configured `NotifyChannels` (tray, iMessage, email, webhook).
//!
//! The daemon is **single-host, single-user** — there is exactly one
//! inbox per machine, identified by the resolved `default_inbox_root()`.
//! It is **idempotent** at startup: if a daemon is already running on
//! the same inbox root and port, the second invocation is a no-op.
//!
//! HTTP backend is deliberately minimal: `tiny_http`-style blocking
//! socket-per-thread. There is no router, no async runtime, no TLS —
//! the inbox is local-only and binds to `127.0.0.1` only.

use std::io::{BufRead, BufReader, Read, Write};
use std::net::{IpAddr, SocketAddr, TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use crate::error::ElicitError;
use crate::inbox::notify::{NotifyChannels, surface_all};
use crate::inbox::{
    PendingRequest, RequestState, finalize, list_pending, load,
    unix_now_ms,
};
use crate::spec::{ElicitResponse, FieldSpec, FieldValue};
use crate::tray::{build_tray, MenuAction, Tray, TrayConfig, TrayEvent};
#[cfg(test)]
use std::net::Ipv4Addr;
use serde::{Deserialize, Serialize};
use tracing::{debug, info, warn};

/// Default port the daemon listens on.
pub const DEFAULT_PORT: u16 = 7117;

/// The lockfile name. Holds the listening socket address + boot time.
const LOCKFILE_NAME: &str = "daemon.lock";

/// How often the daemon scans the inbox dir for new entries.
const POLL_INTERVAL: Duration = Duration::from_millis(500);

/// How long an idle HTTP connection is allowed to live.
const HTTP_KEEPALIVE_TIMEOUT: Duration = Duration::from_secs(30);

/// Bundle of handles returned from `start_daemon` — gives callers the
/// port, inbox root, and a shutdown signal they can flip to terminate
/// the daemon cleanly.
#[derive(Debug)]
pub struct DaemonHandle {
    pub port: u16,
    pub inbox_root: PathBuf,
    pub bind_addr: IpAddr,
    pub lockfile: PathBuf,
    pub shutdown: Arc<AtomicBool>,
}

impl DaemonHandle {
    /// Signal the daemon to exit and wait for it to drop its lockfile.
    pub fn stop(&self) -> std::io::Result<()> {
        self.shutdown.store(true, Ordering::SeqCst);
        // The daemon watches `daemon.lock` for mtime changes; we touch it
        // once to wake its select/poll loop immediately.
        std::fs::File::options()
            .write(true)
            .truncate(true)
            .open(&self.lockfile)?;
        Ok(())
    }
}

/// Configuration knobs the CLI forwards when launching the daemon.
#[derive(Debug, Clone)]
pub struct DaemonConfig {
    pub inbox_root: PathBuf,
    pub port: u16,
    pub bind: IpAddr,
    pub notify: NotifyChannels,
    /// If true, attempt to register a tray icon. If `tray-native` is not
    /// compiled in or the OS rejects the registration, the tray is
    /// silently a no-op.
    pub enable_tray: bool,
}

/// Boot the daemon. Returns a handle the caller can use to shut it
/// down. The function spawns the HTTP server + notifier in background
/// threads and returns immediately.
pub fn start_daemon(cfg: DaemonConfig) -> Result<DaemonHandle, ElicitError> {
    std::fs::create_dir_all(&cfg.inbox_root)?;

    // Detect an existing daemon and short-circuit if we're already
    // running on the same port + root.
    if let Some(existing) = read_lockfile(&cfg.inbox_root) {
        if existing.root == cfg.inbox_root
            && existing.port == cfg.port
            && existing.bind == cfg.bind
        {
            // Verify it's actually live; if not, remove the stale lock.
            if is_port_live(cfg.bind, cfg.port) {
                return Err(ElicitError::RendererFailed(format!(
                    "elicitate inbox daemon already running on {}:{}",
                    cfg.bind, cfg.port
                )));
            }
            let _ = std::fs::remove_file(cfg.inbox_root.join(LOCKFILE_NAME));
        }
    }

    let bind_addr = SocketAddr::new(cfg.bind, cfg.port);
    let listener = TcpListener::bind(bind_addr).map_err(|e| {
        ElicitError::RendererFailed(format!("bind {bind_addr}: {e}"))
    })?;
    // The default accept is blocking. Use non-blocking so the wakeup
    // loop can poll `shutdown` frequently without a separate timer thread.
    listener
        .set_nonblocking(true)
        .map_err(|e| ElicitError::RendererFailed(format!("set_nonblocking: {e}")))?;
    let actual_port = listener
        .local_addr()
        .map_err(|e| ElicitError::RendererFailed(format!("local_addr: {e}")))?
        .port();

    let shutdown = Arc::new(AtomicBool::new(false));
    let lockfile = cfg.inbox_root.join(LOCKFILE_NAME);
    write_lockfile(&lockfile, &cfg.inbox_root, actual_port, cfg.bind)?;

    let tray_url = format!("http://{}:{}", cfg.bind, actual_port);
    // ---- tray icon (best-effort, never blocks boot) ---------------
    let tray: Arc<dyn Tray> = if cfg.enable_tray {
        let tray_cfg = TrayConfig::new(tray_url.clone(), cfg.inbox_root.clone());
        match build_tray(tray_cfg) {
            Ok(t) => {
                info!(backend = t.backend_name(), "tray icon attached");
                t
            }
            Err(e) => {
                warn!(error = %e, "tray attach failed; daemon will run without tray");
                // Fall back to a no-op tray by building a default cfg (no
                // real attach is attempted because the no-op impl never
                // fails).
                build_tray(TrayConfig::new(tray_url.clone(), cfg.inbox_root.clone())).unwrap()
            }
        }
    } else {
        build_tray(TrayConfig::new(tray_url.clone(), cfg.inbox_root.clone()))
            .unwrap()
    };

    // ---- worker 1: HTTP server ------------------------------------
    {
        let shutdown = Arc::clone(&shutdown);
        let inbox_root = cfg.inbox_root.clone();
        let lockfile = lockfile.clone();
        thread::Builder::new()
            .name("elicitate-http".into())
            .spawn(move || {
                if let Err(e) = run_http_loop(listener, &inbox_root, &shutdown) {
                    warn!(error = %e, "http loop exited");
                }
                let _ = std::fs::remove_file(&lockfile);
            })?;
    }

    // ---- worker 2: notifier poller --------------------------------
    {
        let shutdown = Arc::clone(&shutdown);
        let inbox_root = cfg.inbox_root.clone();
        let notify = cfg.notify.clone();
        let tray_for_badge = Arc::clone(&tray);
        thread::Builder::new()
            .name("elicitate-notify".into())
            .spawn(move || {
                run_notifier_loop(&inbox_root, notify, &shutdown, Some(tray_for_badge));
            })?;
    }

    // ---- worker 3: tray event pump --------------------------------
    {
        let shutdown = Arc::clone(&shutdown);
        let fallback_url = tray_url.clone();
        thread::Builder::new()
            .name("elicitate-tray".into())
            .spawn(move || {
                run_tray_loop(tray.as_ref(), &shutdown, &fallback_url);
            })?;
    }

    info!(
        port = actual_port,
        bind = %cfg.bind,
        inbox = %cfg.inbox_root.display(),
        "elicitate inbox daemon started"
    );

    Ok(DaemonHandle {
        port: actual_port,
        inbox_root: cfg.inbox_root,
        bind_addr: cfg.bind,
        lockfile,
        shutdown,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LockfilePayload {
    root: PathBuf,
    port: u16,
    bind: IpAddr,
    booted_at_ms: u64,
}

fn write_lockfile(
    path: &Path,
    root: &Path,
    port: u16,
    bind: IpAddr,
) -> Result<(), ElicitError> {
    let payload = LockfilePayload {
        root: root.to_path_buf(),
        port,
        bind,
        booted_at_ms: unix_now_ms(),
    };
    let json = serde_json::to_vec_pretty(&payload).map_err(ElicitError::Json)?;
    std::fs::write(path, json)?;
    Ok(())
}

pub fn read_lockfile(root: &Path) -> Option<LockfilePayload> {
    let path = root.join(LOCKFILE_NAME);
    let bytes = std::fs::read(&path).ok()?;
    serde_json::from_slice(&bytes).ok()
}

/// Cheap "is anyone listening on this port?" probe.
fn is_port_live(bind: IpAddr, port: u16) -> bool {
    let addr = SocketAddr::new(bind, port);
    TcpStream::connect_timeout(&addr, Duration::from_millis(200)).is_ok()
}

/// Return the live URL of a running inbox daemon, if any. Reads the
/// daemon's lockfile and confirms the socket is actually accepting
/// connections. Returns `None` if no daemon is running or the lockfile
/// is stale (e.g. process died without cleanup).
///
/// `bind_filter` lets the caller restrict to a particular bind address
/// (loopback vs. LAN). Pass `None` to accept any bind address.
pub fn live_url(root: &Path, bind_filter: Option<IpAddr>) -> Option<String> {
    let payload = read_lockfile(root)?;
    if let Some(addr) = bind_filter {
        if payload.bind != addr {
            return None;
        }
    }
    if !is_port_live(payload.bind, payload.port) {
        return None;
    }
    Some(format!("http://{}:{}", payload.bind, payload.port))
}

// ---- HTTP loop --------------------------------------------------------

fn run_http_loop(
    listener: TcpListener,
    inbox_root: &Path,
    shutdown: &Arc<AtomicBool>,
) -> std::io::Result<()> {
    let mut shutdown_mtime = mtime_sec(&inbox_root.join(LOCKFILE_NAME));
    loop {
        if shutdown.load(Ordering::SeqCst) {
            break;
        }
        // Wake up early if the lockfile was touched by `stop()`.
        let current_mtime = mtime_sec(&inbox_root.join(LOCKFILE_NAME));
        if current_mtime != shutdown_mtime {
            shutdown_mtime = current_mtime;
            if shutdown.load(Ordering::SeqCst) {
                break;
            }
        }

        match listener.accept() {
            Ok((stream, _)) => {
                let inbox_root = inbox_root.to_path_buf();
                let shutdown = Arc::clone(shutdown);
                thread::spawn(move || {
                    let _ = handle_connection(stream, &inbox_root, &shutdown);
                });
            }
            Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                // Non-blocking + no incoming connection; check shutdown
                // flag at a reasonable cadence (50ms ≈ 20 Hz).
                thread::sleep(Duration::from_millis(50));
            }
            Err(e) => {
                warn!(error = %e, "accept failed");
                thread::sleep(Duration::from_millis(50));
            }
        }
    }
    Ok(())
}

fn mtime_sec(path: &Path) -> Option<u64> {
    std::fs::metadata(path)
        .ok()
        .and_then(|m| m.modified().ok())
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
        .map(|d| d.as_secs())
}

fn handle_connection(
    mut stream: TcpStream,
    inbox_root: &Path,
    shutdown: &Arc<AtomicBool>,
) -> std::io::Result<()> {
    stream.set_read_timeout(Some(HTTP_KEEPALIVE_TIMEOUT))?;
    stream.set_write_timeout(Some(Duration::from_secs(5)))?;

    let mut reader = BufReader::new(stream.try_clone()?);
    let mut request_line = String::new();
    if reader.read_line(&mut request_line)? == 0 {
        return Ok(());
    }
    let mut headers = Vec::new();
    loop {
        let mut line = String::new();
        let n = reader.read_line(&mut line)?;
        if n == 0 || line == "\r\n" {
            break;
        }
        headers.push(line);
    }

    let mut parts = request_line.split_whitespace();
    let method = parts.next().unwrap_or("");
    let target = parts.next().unwrap_or("");
    let _version = parts.next().unwrap_or("");

    let (route, id) = parse_route(target);

    let body = match route {
        Route::Health => Some(simple_text(200, "ok")),
        Route::Index => Some(simple_text(
            200,
            &format!(
                "elicitate inbox daemon — {} pending",
                list_pending(inbox_root)
                    .map(|v| v.len())
                    .unwrap_or(0)
            ),
        )),
        Route::InboxForm => match id.and_then(|id| load(inbox_root, &id).ok()) {
            Some(req) => Some(text_response(200, &render_inbox_html(&req))),
            None => Some(simple_text(404, "request not found")),
        },
        Route::Answer => {
            if method != "POST" {
                return write_response(&mut stream, 405, "Method Not Allowed", b"");
            }
            let id = match id {
                Some(id) => id,
                None => return write_response(&mut stream, 400, "Bad Request", b"missing id"),
            };
            // Read body.
            let content_length = headers
                .iter()
                .find_map(|h| {
                    let (k, v) = h.split_once(':')?;
                    if k.eq_ignore_ascii_case("content-length") {
                        v.trim().parse::<usize>().ok()
                    } else {
                        None
                    }
                })
                .unwrap_or(0);
            let mut buf = vec![0u8; content_length];
            if content_length > 0 {
                reader.read_exact(&mut buf)?;
            }
            match submit_answer(inbox_root, &id, &buf) {
                Ok(_) => Some(text_response(
                    200,
                    "<h1>Answered</h1><p>You can close this tab.</p>",
                )),
                Err(e) => Some(text_response(400, &format!("<h1>Error</h1><p>{e}</p>"))),
            }
        }
        Route::Static(path) => {
            let stripped = path.trim_start_matches('/');
            let bytes: Vec<u8> = match stripped {
                "" | "index.html" => render_inbox_css().as_bytes().to_vec(),
                other => format!("/* not found: {other} */").into_bytes(),
            };
            return write_response(&mut stream, 200, "OK", &bytes);
        }
        Route::NotFound => Some(simple_text(404, "not found")),
        Route::Shutdown => {
            if method == "POST" {
                shutdown.store(true, Ordering::SeqCst);
                Some(simple_text(200, "shutting down"))
            } else {
                Some(simple_text(403, "use POST"))
            }
        }
    };

    let body = body.unwrap_or_else(|| simple_text(500, "internal"));
    write_response(&mut stream, 200, "OK", body.as_bytes())?;
    Ok(())
}

#[derive(Debug, PartialEq, Eq)]
enum Route {
    Health,
    Index,
    InboxForm,
    Answer,
    Static(String),
    NotFound,
    Shutdown,
}

fn parse_route(target: &str) -> (Route, Option<String>) {
    let path = target.split('?').next().unwrap_or(target).trim_end_matches('/');
    if path == "/health" || path == "/ping" {
        return (Route::Health, None);
    }
    if path == "/shutdown" {
        return (Route::Shutdown, None);
    }
    if path.is_empty() {
        return (Route::Index, None);
    }
    if path == "/inbox" {
        return (Route::Index, None);
    }
    if let Some(rest) = path.strip_prefix("/inbox/") {
        return (Route::InboxForm, Some(rest.to_string()));
    }
    if let Some(rest) = path.strip_prefix("/answer/") {
        return (Route::Answer, Some(rest.to_string()));
    }
    if let Some(rest) = path.strip_prefix("/static/") {
        return (Route::Static(rest.to_string()), None);
    }
    (Route::NotFound, None)
}

fn write_response(
    stream: &mut TcpStream,
    status: u16,
    reason: &str,
    body: &[u8],
) -> std::io::Result<()> {
    write!(
        stream,
        "HTTP/1.1 {status} {reason}\r\nContent-Length: {}\r\nConnection: close\r\nContent-Type: text/html; charset=utf-8\r\n\r\n",
        body.len()
    )?;
    stream.write_all(body)?;
    stream.flush()?;
    Ok(())
}

fn simple_text(status: u16, msg: &str) -> String {
    let _ = status;
    format!(
        "<!doctype html><meta charset=utf-8><title>elicitate</title><body style=\"font-family:system-ui;margin:2rem\"><h1>elicitate</h1><p>{msg}</p>"
    )
}

fn text_response(status: u16, body: &str) -> String {
    let _ = status;
    body.to_string()
}

// ---- HTML rendering ---------------------------------------------------

fn render_inbox_html(req: &PendingRequest) -> String {
    use crate::views::render_form_html;
    let body = render_form_html(req);
    let title = html_escape(&req.spec.title);
    let question = html_escape(&req.spec.question);
    format!(
        "<!doctype html><meta charset=utf-8><title>{title}</title>\
         <style>{css}</style><body>\
         <div class=card>\
           <h1>{title}</h1><p class=q>{question}</p>\
           <p class=meta>From <code>{origin}</code> on <code>{host}</code> · queued {queued}</p>\
           {body}\
         </div>",
        title = title,
        css = render_inbox_css(),
        question = question,
        origin = html_escape(&req.origin.process),
        host = html_escape(&req.origin.hostname),
        queued = format_relative_time(req.queued_at_ms),
        body = body,
    )
}

fn render_inbox_css() -> &'static str {
    "body{background:#0f172a;color:#f8fafc;font-family:system-ui;margin:0;padding:2rem}.card{max-width:640px;margin:auto;background:#1e293b;border-radius:12px;padding:2rem;box-shadow:0 8px 24px rgba(0,0,0,.4)}h1{margin:0 0 .5rem}p.q{white-space:pre-wrap;color:#cbd5e1}p.meta{color:#64748b;font-size:.85rem;margin:0 0 1.5rem}label{display:block;margin:1rem 0 .25rem;font-weight:600}input[type=text],input[type=number],textarea,select{width:100%;padding:.6rem;border-radius:8px;background:#0f172a;color:#f8fafc;border:1px solid #334155;font-size:1rem}textarea{min-height:6rem}button{padding:.7rem 1.4rem;border-radius:8px;border:none;font-weight:600;cursor:pointer;margin-right:.5rem}.ok{background:#22c55e;color:#052e16}.cancel{background:#ef4444;color:#fff}.secret{background:#facc15;color:#1c1917}"
}

fn html_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

fn format_relative_time(ms: u64) -> String {
    let now = unix_now_ms();
    let delta = now.saturating_sub(ms);
    if delta < 60_000 {
        return format!("{delta}s ago");
    }
    if delta < 3_600_000 {
        return format!("{}m ago", delta / 60_000);
    }
    if delta < 86_400_000 {
        return format!("{}h ago", delta / 3_600_000);
    }
    format!("{}d ago", delta / 86_400_000)
}

// ---- Notifier loop ----------------------------------------------------

fn run_notifier_loop(
    inbox_root: &Path,
    cfg: NotifyChannels,
    shutdown: &Arc<AtomicBool>,
    tray: Option<Arc<dyn Tray>>,
) {
    let mut seen: std::collections::HashSet<String> = std::collections::HashSet::new();
    let deadline = Instant::now() + Duration::from_secs(60 * 60 * 24); // safety net
    while !shutdown.load(Ordering::SeqCst) && Instant::now() < deadline {
        match list_pending(inbox_root) {
            Ok(requests) => {
                let pending_count = requests
                    .iter()
                    .filter(|r| matches!(r.state, RequestState::Pending))
                    .count();
                // Keep the tray badge in sync with the pending count.
                if let Some(t) = &tray {
                    let badge: String = if pending_count == 0 {
                        String::new()
                    } else if pending_count >= 10 {
                        "9+".to_string()
                    } else {
                        pending_count.to_string()
                    };
                    let _ = t.set_badge(&badge);
                }
                for req in requests {
                    if seen.contains(&req.request_id) {
                        continue;
                    }
                    seen.insert(req.request_id.clone());
                    if matches!(req.state, RequestState::Pending) {
                        info!(request_id = %req.request_id, "surfacing new request");
                        let attempts = surface_all(&req, &cfg);
                        for a in attempts {
                            debug!(
                                request_id = %req.request_id,
                                kind = ?a.kind,
                                ok = a.ok,
                                detail = %a.detail,
                                "notification attempt"
                            );
                        }
                    }
                }
            }
            Err(e) => warn!(error = %e, "inbox scan failed"),
        }
        // Reap expired requests every minute-ish (cheap, no separate timer).
        if let Ok(reqs) = list_pending(inbox_root) {
            for mut req in reqs {
                if req.is_expired_now() && !req.is_terminal() {
                    req.state = RequestState::Expired;
                    if let Err(e) = finalize(inbox_root, &req) {
                        warn!(error = %e, request_id = %req.request_id, "failed to expire");
                    }
                }
            }
        }
        thread::sleep(POLL_INTERVAL);
    }
}

// ---- Tray event pump --------------------------------------------------

/// Long-running loop that dispatches menu events from the tray icon.
/// Runs on its own thread; exits when `shutdown` flips or the OS tray
/// thread terminates.
fn run_tray_loop(tray: &dyn Tray, shutdown: &Arc<AtomicBool>, fallback_url: &str) {
    while !shutdown.load(Ordering::SeqCst) {
        let Some(event) = tray.try_recv() else {
            thread::sleep(Duration::from_millis(100));
            continue;
        };
        match event {
            TrayEvent::Click | TrayEvent::DoubleClick => {
                // Open the inbox in the default browser. Use `xdg-open` /
                // `open` / `cmd /c start` depending on OS.
                let url = tray_click_url(tray, fallback_url);
                let _ = open_in_default_browser(&url);
            }
            TrayEvent::MenuItem { id } => {
                let action = match id.as_str() {
                    x if x == MenuAction::OpenInbox.id() => Some(MenuAction::OpenInbox),
                    x if x == MenuAction::OpenLatest.id() => Some(MenuAction::OpenLatest),
                    x if x == MenuAction::ToggleQuiet.id() => Some(MenuAction::ToggleQuiet),
                    x if x == MenuAction::Quit.id() => Some(MenuAction::Quit),
                    _ => None,
                };
                if let Some(a) = action {
                    let base = tray_click_url(tray, fallback_url);
                    match a {
                        MenuAction::OpenInbox => {
                            let _ = open_in_default_browser(&base);
                        }
                        MenuAction::OpenLatest => {
                            let url = format!("{}/inbox/latest", base);
                            let _ = open_in_default_browser(&url);
                        }
                        MenuAction::ToggleQuiet => {
                            // Toggle is communicated via tooltip text for now;
                            // the daemon's --quiet flag remains the canonical
                            // knob.
                            let _ = tray.set_tooltip("elicitate inbox (quiet)");
                        }
                        MenuAction::Quit => {
                            info!("quit requested from tray");
                            shutdown.store(true, Ordering::SeqCst);
                            break;
                        }
                    }
                }
            }
        }
    }
}

/// Extract the tray's bound URL (from its config) — used as the
/// click-to-open target. Falls back to the daemon's actual bind
/// URL if the tray doesn't expose one (legacy NoopTray configs).
fn tray_click_url(tray: &dyn Tray, fallback: &str) -> String {
    tray.inbox_url()
        .map(|u| u.trim_end_matches('/').to_string())
        .unwrap_or_else(|| fallback.trim_end_matches('/').to_string())
}

/// Open `url` in the user's default browser. Best-effort; failures
/// only log at debug level — the tray click UX degrades gracefully to
/// "nothing visible happened" if there's no browser.
fn open_in_default_browser(url: &str) -> std::io::Result<()> {
    use std::process::Command;
    #[cfg(target_os = "macos")]
    {
        Command::new("open").arg(url).spawn().map(|_| ())
    }
    #[cfg(target_os = "windows")]
    {
        Command::new("cmd").args(["/C", "start", "", url]).spawn().map(|_| ())
    }
    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open").arg(url).spawn().map(|_| ())
    }
    #[cfg(not(any(target_os = "macos", target_os = "windows", target_os = "linux")))]
    {
        let _ = url;
        Ok(())
    }
}

// ---- Answer submission ------------------------------------------------

#[derive(Debug, Deserialize)]
struct FormPayload {
    #[serde(default)]
    value: Option<String>,
    #[serde(default)]
    boolean: Option<String>,
    #[serde(default)]
    integer: Option<String>,
    #[serde(default)]
    notes: Option<String>,
    #[serde(default)]
    cancel: Option<String>,
}

fn submit_answer(inbox_root: &Path, request_id: &str, body: &[u8]) -> Result<(), String> {
    // Accept both application/x-www-form-urlencoded and JSON.
    let body_str = std::str::from_utf8(body).map_err(|e| e.to_string())?;
    let payload: FormPayload = if body_str.trim_start().starts_with('{') {
        serde_json::from_str(body_str).map_err(|e| e.to_string())?
    } else {
        url_decode_form(body_str)
    };

    let req = match load(inbox_root, request_id) {
        Ok(r) => r,
        Err(e) => return Err(e.to_string()),
    };

    if payload.cancel.is_some() {
        let notes = payload.notes.clone();
        finalize(inbox_root, &PendingRequest {
            state: RequestState::Cancelled,
            response: Some(ElicitResponse::Cancelled { notes }),
            ..req.clone()
        })
        .map_err(|e| e.to_string())?;
    } else {
        let v = coerce_field_value(&req.spec.field, &payload)?;
        let response = ElicitResponse::Answered {
            value: v,
            notes: payload.notes,
        };
        let final_req = PendingRequest {
            state: RequestState::Answered,
            response: Some(response),
            ..req
        };
        finalize(inbox_root, &final_req).map_err(|e| e.to_string())?;
    }
    Ok(())
}

fn url_decode_form(body: &str) -> FormPayload {
    let mut out = FormPayload {
        value: None,
        boolean: None,
        integer: None,
        notes: None,
        cancel: None,
    };
    for kv in body.split('&').filter(|s| !s.is_empty()) {
        let (k, v) = kv.split_once('=').unwrap_or((kv, ""));
        let v = url_decode(v);
        match k {
            "value" => out.value = Some(v),
            "boolean" => out.boolean = Some(v),
            "integer" => out.integer = Some(v),
            "notes" => out.notes = Some(v),
            "cancel" => out.cancel = Some(v),
            _ => {}
        }
    }
    out
}

fn url_decode(s: &str) -> String {
    let bytes = s.as_bytes();
    let mut out = Vec::with_capacity(bytes.len());
    let mut i = 0;
    while i < bytes.len() {
        match bytes[i] {
            b'%' if i + 2 < bytes.len() => {
                let hi = hex(bytes[i + 1]);
                let lo = hex(bytes[i + 2]);
                if let (Some(h), Some(l)) = (hi, lo) {
                    out.push((h << 4) | l);
                    i += 3;
                } else {
                    out.push(b'%');
                    i += 1;
                }
            }
            b'+' => {
                out.push(b' ');
                i += 1;
            }
            b => {
                out.push(b);
                i += 1;
            }
        }
    }
    String::from_utf8_lossy(&out).into_owned()
}

fn hex(b: u8) -> Option<u8> {
    match b {
        b'0'..=b'9' => Some(b - b'0'),
        b'a'..=b'f' => Some(b - b'a' + 10),
        b'A'..=b'F' => Some(b - b'A' + 10),
        _ => None,
    }
}

fn coerce_field_value(field: &FieldSpec, payload: &FormPayload) -> Result<FieldValue, String> {
    match field {
        FieldSpec::Text { .. } => {
            let v = payload.value.clone().unwrap_or_default();
            Ok(FieldValue::Text(v))
        }
        FieldSpec::LongText { .. } => {
            let v = payload.value.clone().unwrap_or_default();
            Ok(FieldValue::LongText(v))
        }
        FieldSpec::Choice { options, .. } => {
            let raw = payload.value.clone().unwrap_or_default();
            let idx = options
                .iter()
                .position(|o| o.value == raw || o.label == raw)
                .ok_or_else(|| format!("choice '{raw}' not in options"))?;
            Ok(FieldValue::Choice {
                value: options[idx].value.clone(),
                index: idx,
            })
        }
        FieldSpec::Boolean { .. } => {
            let v = payload.boolean.as_deref().unwrap_or("");
            match v {
                "true" | "on" | "1" | "yes" => Ok(FieldValue::Boolean(true)),
                _ => Ok(FieldValue::Boolean(false)),
            }
        }
        FieldSpec::Integer { .. } => {
            let raw = payload.integer.clone().or(payload.value.clone()).unwrap_or_default();
            let n: i64 = raw.trim().parse().map_err(|e| format!("not an int: {e}"))?;
            Ok(FieldValue::Integer(n))
        }
        FieldSpec::DateTime { .. } => {
            let raw = payload.value.clone().unwrap_or_default();
            // The renderer only does Date in inquire 0.7, but the spec
            // accepts any RFC3339-compatible string from the HTML form.
            Ok(FieldValue::DateTime(raw))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inbox::RequestOrigin;

    #[test]
    fn parse_route_health() {
        assert_eq!(parse_route("/health"), (Route::Health, None));
        assert_eq!(parse_route("/ping"), (Route::Health, None));
    }

    #[test]
    fn parse_route_inbox_form() {
        assert_eq!(
            parse_route("/inbox/abc-123"),
            (Route::InboxForm, Some("abc-123".into()))
        );
    }

    #[test]
    fn parse_route_answer() {
        assert_eq!(
            parse_route("/answer/xyz?submit=ok"),
            (Route::Answer, Some("xyz".into()))
        );
    }

    #[test]
    fn parse_route_unknown_falls_through() {
        assert_eq!(parse_route("/zz"), (Route::NotFound, None));
    }

    #[test]
    fn parse_route_static_prefix() {
        assert_eq!(parse_route("/static/logo.png"), (Route::Static("logo.png".into()), None));
    }

    #[test]
    fn form_decode_parses_simple() {
        let f = url_decode_form("value=hello+world&notes=ok");
        assert_eq!(f.value.as_deref(), Some("hello world"));
        assert_eq!(f.notes.as_deref(), Some("ok"));
    }

    #[test]
    fn html_escapes_specials() {
        assert_eq!(
            html_escape(r#"<script>alert("x")</script>"#),
            "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"
        );
    }

    #[test]
    fn inbox_html_contains_form() {
        let req = PendingRequest {
            request_id: "req-1".into(),
            origin: RequestOrigin {
                hostname: "h".into(),
                process: "p".into(),
                pid: 1,
                callback: None,
            },
            spec: crate::spec::PromptSpec {
                title: "Approve?".into(),
                question: "Yes?".into(),
                field: FieldSpec::Boolean {
                    label: "ok?".into(),
                    default: Some(true),
                },
                notes: None,
                buttons: None,
                urgency: crate::spec::Urgency::Warning,
                timeout_secs: 60,
                request_id: Some("req-1".into()),
            },
            queued_at_ms: unix_now_ms(),
            expires_at_ms: unix_now_ms() + 60_000,
            state: RequestState::Pending,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
        };
        let html = render_inbox_html(&req);
        assert!(html.contains("<h1>Approve?</h1>"));
        assert!(html.contains("action=\"/answer/req-1\""));
    }

    #[test]
    fn start_stop_roundtrip() {
        let tmp = tempfile::tempdir().unwrap();
        let port = portpicker::pick_unused_port().expect("pick port");
        // Brief settling time to avoid the kernel's TIME_WAIT race when
        // re-binding the port immediately after `pick_unused_port`.
        thread::sleep(Duration::from_millis(50));
        let cfg = DaemonConfig {
            inbox_root: tmp.path().to_path_buf(),
            port,
            bind: IpAddr::V4(Ipv4Addr::LOCALHOST),
            notify: NotifyChannels::default(),
            enable_tray: false,
        };
        let handle = start_daemon(cfg).unwrap();
        assert!(handle.port == port);
        // Health check (retry until the listener is ready)
        let addr = SocketAddr::new(IpAddr::V4(Ipv4Addr::LOCALHOST), handle.port);
        let deadline = std::time::Instant::now() + Duration::from_secs(5);
        let mut stream = None;
        while std::time::Instant::now() < deadline {
            match TcpStream::connect(addr) {
                Ok(s) => {
                    stream = Some(s);
                    break;
                }
                Err(_) => thread::sleep(Duration::from_millis(50)),
            }
        }
        let mut stream = stream.expect("daemon did not start listening within 5s");
        stream
            .write_all(b"GET /health HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            .unwrap();
        stream.flush().unwrap();
        let mut reader = BufReader::new(&stream);
        let mut status = String::new();
        let n = reader.read_line(&mut status).unwrap();
        assert!(n > 0, "no response from daemon: empty read");
        assert!(status.contains("200"), "expected HTTP/1.1 200, got: {status}");
        handle.stop().unwrap();
        thread::sleep(Duration::from_millis(200));
    }

    // ---- v0.5.1: tray-open regressions ----

    #[test]
    fn live_url_returns_none_when_no_lockfile() {
        let dir = tempdir_v051();
        assert!(live_url(&dir, None).is_none());
        assert!(read_lockfile(&dir).is_none());
    }

    #[test]
    fn live_url_rejects_stale_lockfile() {
        let dir = tempdir_v051();
        // Lockfile claims port 1 (always closed on this host) at
        // 127.0.0.1. live_url should refuse and return None.
        let payload = LockfilePayload {
            root: dir.clone(),
            port: 1,
            bind: IpAddr::V4(Ipv4Addr::LOCALHOST),
            booted_at_ms: unix_now_ms(),
        };
        std::fs::write(dir.join(LOCKFILE_NAME), serde_json::to_vec(&payload).unwrap()).unwrap();
        assert!(live_url(&dir, None).is_none());
    }

    #[test]
    fn live_url_accepts_running_daemon() {
        let dir = tempdir_v051();
        let port = portpicker::pick_unused_port().expect("no free port");
        let payload = LockfilePayload {
            root: dir.clone(),
            port,
            bind: IpAddr::V4(Ipv4Addr::LOCALHOST),
            booted_at_ms: unix_now_ms(),
        };
        std::fs::write(dir.join(LOCKFILE_NAME), serde_json::to_vec(&payload).unwrap()).unwrap();
        // Bind to the port so is_port_live() returns true. Holding the
        // listener open for the duration of the assertion is enough.
        let _hold = TcpListener::bind(SocketAddr::new(IpAddr::V4(Ipv4Addr::LOCALHOST), port))
            .expect("bind test port");
        let url = live_url(&dir, None);
        assert!(url.is_some(), "live_url should accept a live socket");
        assert!(url.unwrap().contains(&format!(":{port}")));
    }

    #[test]
    fn live_url_respects_bind_filter() {
        let dir = tempdir_v051();
        let payload = LockfilePayload {
            root: dir.clone(),
            port: 1,
            bind: IpAddr::V4(Ipv4Addr::new(10, 0, 0, 1)),
            booted_at_ms: unix_now_ms(),
        };
        std::fs::write(dir.join(LOCKFILE_NAME), serde_json::to_vec(&payload).unwrap()).unwrap();
        assert!(live_url(&dir, Some(IpAddr::V4(Ipv4Addr::LOCALHOST))).is_none());
        assert!(
            live_url(&dir, Some(IpAddr::V4(Ipv4Addr::new(10, 0, 0, 1)))).is_none(),
            "is_port_live should reject the non-listening port"
        );
    }

    /// Scratch directory under /tmp for v0.5.1 tests. Includes a random
    /// suffix so concurrent test invocations don't collide on the same
    /// path (each `cargo test` worker is a separate process).
    fn tempdir_v051() -> std::path::PathBuf {
        use std::sync::atomic::{AtomicU64, Ordering};
        static COUNTER: AtomicU64 = AtomicU64::new(0);
        let n = COUNTER.fetch_add(1, Ordering::SeqCst);
        let mut p = std::env::temp_dir();
        p.push(format!(
            "elicitate-v0.5.1-{}-{}-{}",
            std::process::id(),
            unix_now_ms(),
            n
        ));
        std::fs::create_dir_all(&p).unwrap();
        p
    }
}

#[cfg(test)]
mod portpicker {
    use std::net::{IpAddr, Ipv4Addr, SocketAddr, TcpListener};
    pub fn pick_unused_port() -> Option<u16> {
        let addr = SocketAddr::new(IpAddr::V4(Ipv4Addr::LOCALHOST), 0);
        let l = TcpListener::bind(addr).ok()?;
        let p = l.local_addr().ok()?.port();
        drop(l);
        Some(p)
    }
}
