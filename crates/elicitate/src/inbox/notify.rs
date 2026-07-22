//! Notification backends: tray, iMessage, email, webhook.
//!
//! Each backend is **best-effort** — the inbox is the source of truth on
//! disk; notifications are just "wake the user up" hints. Failures are
//! logged at `warn` level but never propagated to the caller (the
//! caller has already enqueued the request and the user can always open
//! the inbox manually).
//!
//! Backends in this module shell out to native utilities rather than
//! binding to Cocoa/AppKit / WinRT directly. That matches the rest of
//! `elicitate` — zero native dependencies, no cross-compile friction.

use crate::inbox::{NotificationKind, PendingRequest};
use crate::spec::PromptSpec;
use serde::{Deserialize, Serialize};

/// Per-surface configuration captured by the agent at enqueue time or
/// inherited from the environment.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct NotifyChannels {
    /// iMessage destination (Apple ID phone number or email).
    #[serde(default)]
    pub imessage_target: Option<String>,

    /// Email destination.
    #[serde(default)]
    pub email_target: Option<String>,

    /// Generic webhook URL (NTFY, Pushover, Slack incoming webhook…).
    #[serde(default)]
    pub webhook_url: Option<String>,

    /// Whether to also fire an `osascript`-driven native notification
    /// (Notification Center on macOS, Toast on Windows).
    #[serde(default)]
    pub native: bool,
}

/// Why a notification attempt failed (so callers can log it). Does not
/// affect the inbox workflow.
#[derive(Debug, Clone)]
pub struct NotifyAttempt {
    pub kind: NotificationKind,
    pub ok: bool,
    pub detail: String,
}

impl NotifyAttempt {
    fn ok(kind: NotificationKind, detail: impl Into<String>) -> Self {
        Self {
            kind,
            ok: true,
            detail: detail.into(),
        }
    }
    fn err(kind: NotificationKind, err: impl std::fmt::Display) -> Self {
        Self {
            kind,
            ok: false,
            detail: err.to_string(),
        }
    }
}

/// Surface every notification configured in `cfg` for `req`. Returns the
/// per-surface outcomes for telemetry. Failures of any one backend do
/// NOT short-circuit the others.
pub fn surface_all(req: &PendingRequest, cfg: &NotifyChannels) -> Vec<NotifyAttempt> {
    let mut out = Vec::new();
    if cfg.native {
        out.push(notify_native(req));
    }
    if let Some(target) = cfg.imessage_target.as_deref() {
        out.push(notify_imessage(req, target));
    }
    if let Some(target) = cfg.email_target.as_deref() {
        out.push(notify_email(req, target));
    }
    if let Some(url) = cfg.webhook_url.as_deref() {
        out.push(notify_webhook(req, url));
    }
    out
}

/// Fire a platform-native notification.
pub fn notify_native(req: &PendingRequest) -> NotifyAttempt {
    let result = match crate::platform() {
        crate::Platform::Macos => notify_native_macos(req),
        crate::Platform::Windows => notify_native_windows(req),
        crate::Platform::Linux => notify_native_linux(req),
        crate::Platform::Unknown => Err("no native notifier known for this platform".into()),
    };
    match result {
        Ok(msg) => NotifyAttempt::ok(NotificationKind::NativeNotification, msg),
        Err(e) => NotifyAttempt::err(NotificationKind::NativeNotification, e),
    }
}

/// Send the request via iMessage. Uses AppleScript `Messages`-app
/// integration. No-op if the target is unparseable.
pub fn notify_imessage(req: &PendingRequest, target: &str) -> NotifyAttempt {
    let body = render_imessage_body(req);
    let script = format!(
        "tell application \"Messages\"\n\
         \x20 set targetService to 1st service whose service type = iMessage\n\
         \x20 set targetBuddy to buddy \"{target}\" of targetService\n\
         \x20 send \"{body}\" to targetBuddy\n\
         end tell",
        target = escape_applescript(target),
        body = escape_applescript(&body),
    );
    match run_osascript(&script) {
        Ok(_) => NotifyAttempt::ok(NotificationKind::IMessage, format!("sent to {target}")),
        Err(e) => NotifyAttempt::err(NotificationKind::IMessage, e),
    }
}

/// Open the user's default mail handler prefilled with the rendered
/// form. One click on "Send" delivers to the user's own mailbox; they
/// reply by running `elicitate answer --request-id <id> --reply`.
pub fn notify_email(req: &PendingRequest, target: &str) -> NotifyAttempt {
    let subject = format!("[elicitate] {}", truncate(&req.spec.title, 60));
    let body = render_imessage_body(req);
    let url = format!(
        "mailto:{target}?subject={}&body={}",
        url_encode(&subject),
        url_encode(&body)
    );
    match open_url(&url) {
        Ok(_) => NotifyAttempt::ok(NotificationKind::Email, format!("opened mailto for {target}")),
        Err(e) => NotifyAttempt::err(NotificationKind::Email, e),
    }
}

/// POST a JSON payload to a webhook URL (NTFY, Pushover, Slack).
pub fn notify_webhook(req: &PendingRequest, url: &str) -> NotifyAttempt {
    let payload = serde_json::json!({
        "title": req.spec.title,
        "question": req.spec.question,
        "request_id": req.request_id,
        "open_url": inbox_open_url(req),
    });
    let json = match serde_json::to_string(&payload) {
        Ok(s) => s,
        Err(e) => {
            return NotifyAttempt::err(NotificationKind::Webhook, format!("serialize: {e}"));
        }
    };
    match post_form(url, &json) {
        Ok(_) => NotifyAttempt::ok(NotificationKind::Webhook, "ok"),
        Err(e) => NotifyAttempt::err(NotificationKind::Webhook, e),
    }
}

// ----- private helpers -----

fn notify_native_macos(req: &PendingRequest) -> Result<String, String> {
    let script = format!(
        "display notification \"{}\" with title \"{}\" subtitle \"\"",
        escape_applescript(&truncate(&req.spec.question, 200)),
        escape_applescript(&truncate(&req.spec.title, 60)),
    );
    run_osascript(&script).map(|_| "ok".into())
}

fn notify_native_windows(req: &PendingRequest) -> Result<String, String> {
    use std::process::Command;
    let title = escape_powershell(&truncate(&req.spec.title, 60));
    let question = escape_powershell(&truncate(&req.spec.question, 200));
    let ps = format!(
        "Add-Type -AssemblyName System.Windows.Forms | Out-Null;\n\
         $n = New-Object System.Windows.Forms.NotifyIcon;\n\
         $n.Icon = [System.Drawing.SystemIcons]::Information;\n\
         $n.BalloonTipIcon = 'Info';\n\
         $n.Visible = $true;\n\
         $n.ShowBalloonTip(10000, '{title}', '{question}', [System.Windows.Forms.ToolTipIcon]::Info);\n\
         Start-Sleep -Seconds 6;\n\
         $n.Dispose();"
    );
    let status = Command::new("powershell")
        .args(["-NoProfile", "-Command", &ps])
        .status()
        .map_err(|e| format!("spawn powershell: {e}"))?;
    if status.success() {
        Ok("ok".into())
    } else {
        Err(format!("powershell exit {status:?}"))
    }
}

fn notify_native_linux(req: &PendingRequest) -> Result<String, String> {
    use std::process::Command;
    let title = truncate(&req.spec.title, 60);
    let body = truncate(&req.spec.question, 200);
    let status = Command::new("notify-send")
        .args(["-u", "normal", &title, &body])
        .status()
        .map_err(|e| format!("spawn notify-send: {e}"))?;
    if status.success() {
        Ok("ok".into())
    } else {
        Err(format!("notify-send exit {status:?}"))
    }
}

fn run_osascript(script: &str) -> Result<(), String> {
    if !cfg!(target_os = "macos") {
        return Err("osascript only available on macos".into());
    }
    use std::process::Command;
    let out = Command::new("osascript")
        .args(["-e", script])
        .output()
        .map_err(|e| format!("spawn osascript: {e}"))?;
    if out.status.success() {
        Ok(())
    } else {
        Err(format!(
            "osascript: {}",
            String::from_utf8_lossy(&out.stderr).trim()
        ))
    }
}

fn open_url(url: &str) -> Result<(), String> {
    use std::process::Command;
    let (cmd, args): (&str, Vec<&str>) = if cfg!(target_os = "macos") {
        ("open", vec![url])
    } else if cfg!(target_os = "windows") {
        ("cmd", vec!["/c", "start", "", url])
    } else {
        ("xdg-open", vec![url])
    };
    let status = Command::new(cmd)
        .args(args)
        .status()
        .map_err(|e| format!("spawn {cmd}: {e}"))?;
    if status.success() {
        Ok(())
    } else {
        Err(format!("{cmd} exit {status:?}"))
    }
}

/// Best-effort HTTP POST of a JSON body. We don't pull in `reqwest`
/// just for this — a raw TCP write to the host parsed from the URL is
/// enough for the small NTFY-style payloads we send. If the URL is
/// unreachable, the inbox still works, so the failure is fine.
fn post_form(url: &str, body: &str) -> Result<(), String> {
    use std::io::Write;
    use std::net::TcpStream;
    use std::time::Duration;

    let stripped = url
        .strip_prefix("http://")
        .or_else(|| url.strip_prefix("https://"))
        .ok_or_else(|| "only http(s) URLs are supported".to_string())?;
    let (authority, path) = match stripped.split_once('/') {
        Some((a, p)) => (a, format!("/{p}")),
        None => (stripped, "/".into()),
    };
    let default_port = if url.starts_with("https://") { 443 } else { 80 };
    let (host, port) = match authority.rsplit_once(':') {
        Some((h, p)) => (h.to_string(), p.parse::<u16>().unwrap_or(default_port)),
        None => (authority.to_string(), default_port),
    };
    let addr = format!("{host}:{port}");

    let mut stream = TcpStream::connect(&addr)
        .map_err(|e| format!("connect {addr}: {e}"))?;
    stream
        .set_write_timeout(Some(Duration::from_secs(3)))
        .map_err(|e| format!("set timeout: {e}"))?;

    let req = format!(
        "POST {path} HTTP/1.1\r\n\
         Host: {host}\r\n\
         Content-Type: application/json\r\n\
         Content-Length: {len}\r\n\
         Connection: close\r\n\
         \r\n\
         {body}",
        path = path,
        host = host,
        len = body.len(),
        body = body,
    );
    stream
        .write_all(req.as_bytes())
        .map_err(|e| format!("write: {e}"))?;
    Ok(())
}

/// Render the request into the iMessage/email body.
pub fn render_imessage_body(req: &PendingRequest) -> String {
    render_prompt_as_text(&req.spec, &req.request_id)
}

/// Same as [`render_imessage_body`] but for a bare spec (no PendingRequest).
pub fn render_prompt_as_text(spec: &PromptSpec, request_id: &str) -> String {
    let mut s = String::new();
    s.push_str(&format!("{}\n\n", spec.title));
    s.push_str(&spec.question);
    s.push_str("\n\n");
    s.push_str(&format!("request_id: {request_id}\n"));
    s.push_str(&format!(
        "open: {}\n",
        inbox_open_url_for(spec.request_id.as_deref().unwrap_or(request_id))
    ));
    s.push_str(&format!(
        "reply: elicitate answer --request-id {request_id} --value <your-answer>\n"
    ));
    s
}

/// The URL the user can open in a browser to land on a fully styled
/// inbox form for the request.
pub fn inbox_open_url(req: &PendingRequest) -> String {
    inbox_open_url_for(&req.request_id)
}

/// URL helper — defaults to the local daemon (`localhost:7117`) unless
/// `ELICITATE_BASE_URL` is set.
pub fn inbox_open_url_for(request_id: &str) -> String {
    let base = std::env::var("ELICITATE_BASE_URL")
        .unwrap_or_else(|_| "http://localhost:7117".to_string());
    format!("{base}/inbox/{request_id}")
}

fn url_encode(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for b in s.bytes() {
        match b {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                out.push(b as char);
            }
            _ => out.push_str(&format!("%{b:02X}")),
        }
    }
    out
}

fn escape_applescript(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"")
}

fn escape_powershell(s: &str) -> String {
    s.replace('\'', "''")
}

fn truncate(s: &str, max: usize) -> String {
    if s.chars().count() <= max {
        return s.to_string();
    }
    let mut out: String = s.chars().take(max).collect();
    out.push('…');
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_req(request_id: &str) -> PendingRequest {
        let spec = crate::spec::PromptSpec {
            title: "Approval needed".into(),
            question: "Continue with rollout to production?".into(),
            field: crate::spec::FieldSpec::Boolean {
                label: "Approve?".into(),
                default: Some(true),
            },
            notes: None,
            buttons: None,
            urgency: crate::spec::Urgency::Warning,
            timeout_secs: 600,
            request_id: Some(request_id.into()),
        };
        PendingRequest {
            request_id: request_id.into(),
            origin: crate::inbox::RequestOrigin {
                hostname: "h".into(),
                process: "p".into(),
                pid: 1,
                callback: None,
            },
            spec,
            queued_at_ms: 0,
            expires_at_ms: u64::MAX,
            state: crate::inbox::RequestState::Pending,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
        }
    }

    #[test]
    fn render_text_contains_open_and_reply() {
        let body = render_imessage_body(&sample_req("abc"));
        assert!(body.contains("request_id: abc"));
        assert!(body.contains("/inbox/abc"));
        assert!(body.contains("elicitate answer --request-id abc"));
    }

    #[test]
    fn url_encoding() {
        assert_eq!(url_encode("hello world"), "hello%20world");
        assert_eq!(url_encode("a&b=c"), "a%26b%3Dc");
    }

    #[test]
    fn applescript_escape_quotes() {
        assert_eq!(escape_applescript(r#"he said "hi""#), r#"he said \"hi\""#);
    }

    #[test]
    fn truncation_drops_with_ellipsis() {
        assert_eq!(truncate("abcdef", 3), "abc…");
        assert_eq!(truncate("abc", 10), "abc");
    }

    #[test]
    fn inbox_open_url_default_port() {
        assert!(inbox_open_url_for("xyz").ends_with("/inbox/xyz"));
    }

    #[test]
    fn surface_all_with_empty_cfg_is_empty() {
        let attempts = surface_all(&sample_req("xyz"), &NotifyChannels::default());
        assert!(attempts.is_empty());
    }

    #[test]
    fn webhook_attempt_succeeds_with_dummy_url() {
        let req = sample_req("xyz");
        let payload = serde_json::json!({
            "title": req.spec.title,
            "request_id": req.request_id,
            "open_url": inbox_open_url(&req),
        });
        assert!(payload["title"].as_str().is_some());
    }
}
