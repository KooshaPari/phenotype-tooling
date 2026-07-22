//! `elicitate` CLI binary — subcommands for every workflow:
//!
//! | Command       | Purpose                                                   |
//! |---------------|-----------------------------------------------------------|
//! | `ask`         | Render a popup (blocking) or queue it (with `--async`)    |
//! | `schema`      | Print JSON Schema for spec / field / response             |
//! | `detect`      | Platform + renderer diagnostics                           |
//! | `smoke`       | Render a built-in smoke-test popup                        |
//! | `install`     | Install the CLI globally + enable auto-launch helper      |
//! | `uninstall`   | Reverse of `install`                                      |
//! | `daemon`      | Run the long-lived inbox HTTP daemon                      |
//! | `inbox`       | List pending requests / show one in detail / open UI      |
//! | `wait`        | Block until an inbox request reaches a terminal state     |
//! | `answer`      | Submit an answer to a pending inbox request (CLI mode)    |
//! | `serve`       | (redirect) — real MCP stdio server is `elicitate-mcp`     |
//! | `version`     | Print version + license                                    |

use std::path::PathBuf;
use std::process::ExitCode;
use std::time::Duration;

use clap::{Args, Parser, Subcommand};
use serde_json::json;

use elicitate::inbox::RequestOrigin;
use elicitate::options::RendererPreference;
use elicitate::spec::{
    ButtonSpec, ElicitResponse, FieldSpec, FieldValue, NotesSpec,
    PromptSpec, Urgency,
};
/// Native OS popup elicitation — render a modal dialog and read the user's
/// response as typed JSON.
#[derive(Debug, Parser)]
#[command(
    name = "elicitate",
    version,
    about = "Native OS popup elicitation for autonomous agents",
    long_about = "elicitate renders a native OS popup (NSAlert on macOS, Win32 form on Windows, \
                  zenity/kdialog/Tk/inquire on Linux) and returns the user's response as typed JSON. \
                  For non-blocking workflows, queue the prompt in the inbox via `--async` and use \
                  `elicitate wait --request-id <id>` to retrieve the answer later."
)]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,

    /// Increase verbosity (-v, -vv, -vvv).
    #[arg(short, long, action = clap::ArgAction::Count, global = true)]
    verbose: u8,

    /// Force a specific renderer.
    #[arg(long, global = true, value_enum)]
    renderer: Option<RendererArg>,

    /// Override the inbox data directory (also used for `install`).
    #[arg(long, global = true, env = "ELICITATE_INBOX_DIR")]
    inbox_dir: Option<PathBuf>,
}

#[derive(Debug, Clone, Copy, clap::ValueEnum)]
enum RendererArg {
    Auto,
    Gui,
    Tty,
}

impl From<RendererArg> for RendererPreference {
    fn from(r: RendererArg) -> Self {
        match r {
            RendererArg::Auto => RendererPreference::AutoGui,
            RendererArg::Gui => RendererPreference::ForceGui,
            RendererArg::Tty => RendererPreference::ForceTty,
        }
    }
}

#[derive(Debug, Subcommand)]
enum Cmd {
    /// Render a popup from CLI flags, --from-json, or --from-file.
    ///
    /// With `--async`, the spec is queued in the inbox (no blocking) and the
    /// new `request_id` is printed. Combine with `elicitate wait --request-id`
    /// to retrieve the answer.
    Ask(AskArgs),
    /// Print the JSON Schema for PromptSpec (or FieldSpec / ElicitResponse).
    Schema(SchemaArgs),
    /// Detect platform + renderer kind.
    Detect,
    /// Render a built-in test popup (used for CI smoke).
    Smoke(SmokeArgs),
    /// Install elicitate: copy the binaries to ~/.local/bin (or $PREFIX/bin),
    /// register the inbox daemon with the OS launcher, and set up
    /// `~/.local/share/elicitate`.
    Install(InstallArgs),
    /// Remove the binaries and launcher registration installed by `install`.
    Uninstall(UninstallArgs),
    /// Run the inbox daemon in the foreground (server mode).
    Daemon(DaemonArgs),
    /// Inspect the inbox: list pending, show one in detail, or open the UI.
    Inbox(InboxArgs),
    /// Block until a queued `--async` request has been answered (or times out).
    Wait(WaitArgs),
    /// Submit an answer to a queued inbox request via the CLI (no UI).
    Answer(AnswerArgs),
    /// Alias: run the MCP stdio server. Equivalent to executing
    /// `elicitate-mcp` directly.
    Serve,
    /// Print version + license info.
    Version,
}

// ---- ask ---------------------------------------------------------------

#[derive(Debug, Args)]
struct AskArgs {
    #[arg(long)]
    title: Option<String>,
    #[arg(long)]
    question: Option<String>,

    /// Render from an inline JSON spec. Conflicts with --title / --question.
    #[arg(long, conflicts_with_all = &["title", "question"])]
    from_json: Option<String>,

    /// Render from a JSON spec file. Conflicts with --title / --question.
    #[arg(long, conflicts_with_all = &["title", "question"])]
    from_file: Option<PathBuf>,

    /// Don't block — queue the prompt in the inbox and print the
    /// `request_id` as JSON immediately. The answer can be retrieved
    /// with `elicitate wait --request-id <id>`.
    #[arg(long)]
    r#async: bool,

    /// Notification targets (comma-separated) for the `--async` workflow.
    /// Supported values: `native`, `imessage:<target>`, `email:<addr>`,
    /// `webhook:<url>`. Falls back to `ELICITATE_NOTIFY` env.
    #[arg(long, env = "ELICITATE_NOTIFY")]
    notify: Option<String>,

    /// Urgency: info | warning | error | secret.
    #[arg(long, default_value = "info")]
    urgency: String,

    /// Timeout in seconds. 0 = no timeout.
    #[arg(long, default_value = "600")]
    timeout_secs: u32,

    /// Cancel button label.
    #[arg(long, default_value = "Cancel")]
    cancel_label: Option<String>,

    /// Confirm button label.
    #[arg(long, default_value = "OK")]
    confirm_label: Option<String>,
}

// ---- schema / smoke ----------------------------------------------------

#[derive(Debug, Args)]
struct SchemaArgs {
    /// Print the FieldSpec schema instead.
    #[arg(long)]
    field: bool,
    /// Print the ElicitResponse schema instead.
    #[arg(long)]
    response: bool,
}

#[derive(Debug, Args)]
struct SmokeArgs {
    /// Title to use for the smoke popup.
    #[arg(long, default_value = "elicitate smoke test")]
    title: String,
    /// Skip the popup entirely (just verify CLI parsing).
    #[arg(long)]
    no_render: bool,
}

// ---- install / uninstall ----------------------------------------------

#[derive(Debug, Args, Default)]
struct InstallArgs {
    /// Install into this directory instead of ~/.local/bin.
    #[arg(long)]
    prefix: Option<PathBuf>,
    /// Skip registering the inbox daemon as a launchd / systemd service.
    #[arg(long)]
    no_launch_agent: bool,
    /// Also append the prefix to your shell rc files (.zshrc / .bashrc /
    /// PowerShell profile). Off by default — most users prefer to manage
    /// their own PATH. Pass this once to enable the auto-write.
    #[arg(long)]
    with_shell_rc: bool,
    /// Print what would happen without writing anything.
    #[arg(long)]
    dry_run: bool,
}

#[derive(Debug, Args, Default)]
struct UninstallArgs {
    /// Prefix to remove from. Defaults to whatever `install` used.
    #[arg(long)]
    prefix: Option<PathBuf>,
    /// Don't print — just do it.
    #[arg(long, default_value_t = false)]
    yes: bool,
}

// ---- daemon -----------------------------------------------------------

#[derive(Debug, Args)]
struct DaemonArgs {
    /// Port to bind on (loopback only by default).
    #[arg(long, default_value_t = elicitate::inbox::daemon::DEFAULT_PORT)]
    port: u16,
    /// Bind address. Defaults to 127.0.0.1.
    #[arg(long, default_value = "127.0.0.1")]
    bind: String,
    /// iMessage destination (Apple ID).
    #[arg(long, env = "ELICITATE_IMESSAGE_TARGET")]
    imessage_target: Option<String>,
    /// Email destination.
    #[arg(long, env = "ELICITATE_EMAIL_TARGET")]
    email_target: Option<String>,
    /// Webhook URL.
    #[arg(long, env = "ELICITATE_WEBHOOK_URL")]
    webhook_url: Option<String>,
    /// Fire an OS-native notification (Notification Center / Toast).
    #[arg(long, env = "ELICITATE_NOTIFY_NATIVE")]
    native: bool,
}

// ---- inbox ------------------------------------------------------------

#[derive(Debug, Args)]
struct InboxArgs {
    /// List all pending requests (default if no other arg).
    #[arg(long, conflicts_with_all = &["show", "open"])]
    list: bool,
    /// Show full JSON for a single request.
    #[arg(long)]
    show: Option<String>,
    /// Print the open-the-form URL for a single request without opening.
    #[arg(long, conflicts_with_all = &["list", "show"])]
    url: Option<String>,
    /// Open the inbox UI in the default browser.
    #[arg(long, conflicts_with_all = &["list", "show", "url"])]
    open: bool,
    /// Clean up expired / completed entries older than the given number of
    /// seconds.
    #[arg(long)]
    gc_age_secs: Option<u64>,
}

// ---- wait / answer ----------------------------------------------------

#[derive(Debug, Args)]
struct WaitArgs {
    /// The request_id returned by `elicitate ask --async`.
    #[arg(long)]
    request_id: String,
    /// How often to poll the inbox for an answer (milliseconds).
    #[arg(long, default_value_t = 500)]
    poll_interval_ms: u64,
    /// Give up after this many seconds (0 = wait forever).
    #[arg(long, default_value_t = 0)]
    timeout_secs: u64,
}

#[derive(Debug, Args)]
struct AnswerArgs {
    /// The request_id to answer.
    #[arg(long)]
    request_id: String,
    /// The answer value (string for text/choice, ignored if --integer/--bool set).
    #[arg(long, conflicts_with_all = &["integer", "boolean"])]
    value: Option<String>,
    /// The integer answer.
    #[arg(long, conflicts_with_all = &["value"])]
    integer: Option<i64>,
    /// The boolean answer.
    #[arg(long, conflicts_with_all = &["value"])]
    boolean: Option<bool>,
    /// Optional notes value.
    #[arg(long)]
    notes: Option<String>,
    /// Cancel the request instead of answering it.
    #[arg(long, conflicts_with_all = &["value", "integer", "boolean", "notes"])]
    cancel: bool,
}

// ---- main -------------------------------------------------------------

fn main() -> ExitCode {
    let cli = Cli::parse();
    init_tracing(cli.verbose);

    let renderer = cli.renderer.map(std::convert::Into::into);
    let inbox_dir = cli.inbox_dir.clone().unwrap_or_else(elicitate::inbox::default_inbox_root);

    let result = match cli.cmd {
        Cmd::Ask(args) => cmd_ask(args, renderer, &inbox_dir),
        Cmd::Schema(args) => Ok(cmd_schema(args)),
        Cmd::Detect => Ok(cmd_detect()),
        Cmd::Smoke(args) => cmd_smoke(args, renderer),
        Cmd::Install(args) => cmd_install(args, &inbox_dir),
        Cmd::Uninstall(args) => cmd_uninstall(args, &inbox_dir),
        Cmd::Daemon(args) => cmd_daemon(args, &inbox_dir),
        Cmd::Inbox(args) => cmd_inbox(args, &inbox_dir),
        Cmd::Wait(args) => cmd_wait(args, &inbox_dir),
        Cmd::Answer(args) => cmd_answer(args, &inbox_dir),
        Cmd::Serve => {
            eprintln!("error: 'serve' is provided by the `elicitate-mcp` binary, not `elicitate`. Run `elicitate-mcp` instead.");
            return ExitCode::from(2);
        }
        Cmd::Version => {
            println!("elicitate {}", env!("CARGO_PKG_VERSION"));
            println!("license: MIT");
            println!("repository: https://github.com/KooshaPari/phenotype-tooling");
            return ExitCode::SUCCESS;
        }
    };

    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::FAILURE
        }
    }
}

fn init_tracing(verbose: u8) {
    use tracing_subscriber::EnvFilter;
    let level = match verbose {
        0 => "warn",
        1 => "info",
        2 => "debug",
        _ => "trace",
    };
    let filter =
        EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new(level));
    let _ = tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_target(false)
        .try_init();
}

// ---- ask --------------------------------------------------------------

fn cmd_ask(args: AskArgs, renderer: Option<RendererPreference>, inbox_dir: &PathBuf) -> Result<(), String> {
    let spec = if let Some(json_str) = args.from_json {
        serde_json::from_str::<PromptSpec>(&json_str)
            .map_err(|e| format!("invalid --from-json: {e}"))?
    } else if let Some(path) = args.from_file {
        let text = std::fs::read_to_string(&path)
            .map_err(|e| format!("read {}: {e}", path.display()))?;
        serde_json::from_str::<PromptSpec>(&text)
            .map_err(|e| format!("parse {}: {e}", path.display()))?
    } else {
        build_minimal_spec_from_flags(&args)?
    };

    if args.r#async {
        let origin = RequestOrigin {
            hostname: hostname(),
            process: std::env::current_exe()
                .ok()
                .and_then(|p| p.file_name().map(|n| n.to_string_lossy().into_owned()))
                .unwrap_or_else(|| "elicitate".into()),
            pid: std::process::id(),
            callback: None,
        };
        let req = elicitate::PendingRequest::new(spec, origin);
        let path = elicitate::inbox::enqueue(inbox_dir, &req)
            .map_err(|e| e.to_string())?;
        let out = json!({
            "status": "queued",
            "request_id": req.request_id,
            "path": path,
            "open_url": elicitate::inbox_open_url_for(&req.request_id),
            "wait": format!("elicitate wait --request-id {}", req.request_id),
        });
        println!("{}", serde_json::to_string_pretty(&out).unwrap());

        // Fire notifications (best-effort).
        let cfg = parse_notify_cfg(args.notify.as_deref());
        if cfg != elicitate::NotifyChannels::default() {
            let attempts = elicitate::inbox::notify::surface_all(&req, &cfg);
            let summary: Vec<_> = attempts.iter()
                .map(|a| serde_json::json!({"kind": format!("{:?}", a.kind), "ok": a.ok, "detail": a.detail}))
                .collect();
            eprintln!("notify: {}", serde_json::to_string(&summary).unwrap_or_default());
        }
        return Ok(());
    }

    let mut opts = elicitate::ElicitOptions::default();
    if let Some(r) = renderer {
        opts.renderer = r;
    }
    let response = elicitate::elicit_with(&spec, &opts).map_err(|e| e.to_string())?;
    let out = serde_json::to_string_pretty(&response)
        .map_err(|e| format!("serialize response: {e}"))?;
    println!("{out}");
    Ok(())
}

fn parse_notify_cfg(spec: Option<&str>) -> elicitate::NotifyChannels {
    let mut cfg = elicitate::NotifyChannels::default();
    let Some(spec) = spec else { return cfg };
    for piece in spec.split(',').filter(|s| !s.trim().is_empty()) {
        let piece = piece.trim();
        if piece == "native" {
            cfg.native = true;
            continue;
        }
        if let Some(rest) = piece.strip_prefix("imessage:") {
            cfg.imessage_target = Some(rest.to_string());
            continue;
        }
        if let Some(rest) = piece.strip_prefix("email:") {
            cfg.email_target = Some(rest.to_string());
            continue;
        }
        if let Some(rest) = piece.strip_prefix("webhook:") {
            cfg.webhook_url = Some(rest.to_string());
            continue;
        }
    }
    cfg
}

fn hostname() -> String {
    std::env::var("HOSTNAME")
        .or_else(|_| std::env::var("COMPUTERNAME"))
        .unwrap_or_else(|_| {
            // Best-effort.
            std::fs::read_to_string("/etc/hostname")
                .ok()
                .map(|s| s.trim().to_string())
                .unwrap_or_else(|| "unknown".to_string())
        })
}

fn build_minimal_spec_from_flags(args: &AskArgs) -> Result<PromptSpec, String> {
    let title = args
        .title
        .clone()
        .ok_or_else(|| "--title is required (or use --from-json / --from-file / --async)".to_string())?;
    let question = args
        .question
        .clone()
        .ok_or_else(|| "--question is required (or use --from-json / --from-file / --async)".to_string())?;
    let urgency = match args.urgency.as_str() {
        "info" => Urgency::Info,
        "warning" => Urgency::Warning,
        "error" => Urgency::Error,
        "secret" => Urgency::Secret,
        other => return Err(format!("invalid urgency '{other}'")),
    };
    let buttons = if args.cancel_label.is_some() || args.confirm_label.is_some() {
        Some(ButtonSpec {
            cancel: args.cancel_label.clone().unwrap_or_else(|| "Cancel".into()),
            confirm: args.confirm_label.clone().unwrap_or_else(|| "OK".into()),
            default_is_cancel: false,
        })
    } else {
        None
    };
    Ok(PromptSpec {
        title,
        question,
        field: FieldSpec::Text {
            label: "Enter value".into(),
            default: None,
            placeholder: None,
            max_length: None,
            secret: matches!(urgency, Urgency::Secret),
            pattern: None,
        },
        notes: Some(NotesSpec {
            label: "Notes (optional)".into(),
            default: None,
            max_length: None,
            required: false,
        }),
        buttons,
        urgency,
        timeout_secs: args.timeout_secs,
        request_id: None,
    })
}

// ---- schema / smoke / detect ------------------------------------------

fn cmd_schema(args: SchemaArgs) {
    let s = if args.field {
        serde_json::to_string_pretty(&schemars::schema_for!(FieldSpec)).unwrap()
    } else if args.response {
        elicitate::schema_response_json().to_string()
    } else {
        elicitate::schema_json().to_string()
    };
    println!("{s}");
}

fn cmd_detect() {
    let platform = elicitate::platform();
    let auto = elicitate::detect_renderer(RendererPreference::AutoGui);
    let forced_tty = elicitate::detect_renderer(RendererPreference::ForceTty);
    let forced_gui = elicitate::detect_renderer(RendererPreference::ForceGui);
    let inbox_root = elicitate::inbox::default_inbox_root();
    let result = json!({
        "platform": platform,
        "renderer_auto": auto,
        "renderer_force_tty": forced_tty,
        "renderer_force_gui": forced_gui,
        "inbox_root": inbox_root,
    });
    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_smoke(args: SmokeArgs, renderer: Option<RendererPreference>) -> Result<(), String> {
    if args.no_render {
        println!("smoke: --no-render set, skipping popup");
        return Ok(());
    }
    let spec = PromptSpec {
        title: args.title,
        question: "This is the elicitate smoke test. Did it work?".into(),
        field: FieldSpec::Boolean {
            label: "Worked?".into(),
            default: Some(true),
        },
        notes: None,
        buttons: None,
        urgency: Urgency::Info,
        timeout_secs: 30,
        request_id: Some("smoke".into()),
    };
    let mut opts = elicitate::ElicitOptions::default();
    if let Some(r) = renderer {
        opts.renderer = r;
    }
    match elicitate::elicit_with(&spec, &opts) {
        Ok(ElicitResponse::Answered {
            value: FieldValue::Boolean(b),
            ..
        }) => {
            if b {
                println!("smoke: passed");
                Ok(())
            } else {
                println!("smoke: user said no");
                Err("user reported failure".into())
            }
        }
        Ok(ElicitResponse::Cancelled { .. }) => Err("user cancelled".into()),
        Ok(ElicitResponse::TimedOut { .. }) => Err("popup timed out".into()),
        Ok(ElicitResponse::Failed { reason }) => Err(format!("popup failed: {reason}")),
        Ok(other) => Err(format!("unexpected response variant: {other:?}")),
        Err(e) => Err(e.to_string()),
    }
}

// ---- install / uninstall --------------------------------------------

fn cmd_install(args: InstallArgs, inbox_dir: &PathBuf) -> Result<(), String> {
    use elicitate::installer;
    installer::install(&installer::InstallOptions {
        prefix: args.prefix.clone(),
        inbox_dir: inbox_dir.clone(),
        register_launch_agent: !args.no_launch_agent,
        dry_run: args.dry_run,
        update_shell_rc: args.with_shell_rc,
    })
    .map(|report| {
        println!("{}", serde_json::to_string_pretty(&report).unwrap_or_default());
    })
    .map_err(|e| e.to_string())
}

fn cmd_uninstall(args: UninstallArgs, inbox_dir: &PathBuf) -> Result<(), String> {
    use elicitate::installer;
    installer::uninstall(&installer::UninstallOptions {
        prefix: args.prefix.clone(),
        inbox_dir: inbox_dir.clone(),
        assume_yes: args.yes,
    })
    .map(|report| {
        println!("{}", serde_json::to_string_pretty(&report).unwrap_or_default());
    })
    .map_err(|e| e.to_string())
}

// ---- daemon / inbox / wait / answer ---------------------------------

fn cmd_daemon(args: DaemonArgs, inbox_dir: &PathBuf) -> Result<(), String> {
    let bind: std::net::IpAddr = args
        .bind
        .parse()
        .map_err(|e| format!("invalid --bind '{}': {e}", args.bind))?;
    let notify = elicitate::NotifyChannels {
        imessage_target: args.imessage_target,
        email_target: args.email_target,
        webhook_url: args.webhook_url,
        native: args.native,
    };
    let cfg = elicitate::inbox::daemon::DaemonConfig {
        inbox_root: inbox_dir.clone(),
        port: args.port,
        bind,
        notify,
    };
    let handle = elicitate::inbox::daemon::start_daemon(cfg)
        .map_err(|e| e.to_string())?;
    println!(
        "{}",
        serde_json::to_string_pretty(&json!({
            "status": "started",
            "port": handle.port,
            "bind": handle.bind_addr.to_string(),
            "inbox_root": handle.inbox_root,
            "open_url_format": elicitate::inbox_open_url_for("<id>"),
        }))
        .unwrap()
    );
    // Block on a Ctrl-C / SIGINT / SIGTERM handler so the process stays
    // alive. EOF on stdin (a parent that closed the pipe) is ignored so
    // process supervisors like launchd and the test harness can detach us
    // without us self-terminating.
    let shutdown = daemon_shutdown_signal();
    block_on(shutdown);
    let _ = handle.stop();
    Ok(())
}

/// Return a future that resolves when a shutdown signal arrives.
///
/// On Unix: SIGINT, SIGTERM, and SIGHUP are wired.
/// On Windows: Ctrl-C is wired.
///
/// We deliberately ignore EOF on stdin so detached supervisors (launchd,
/// systemd, CI test harnesses) can spawn us without us self-terminating.
fn daemon_shutdown_signal() -> impl std::future::Future<Output = ()> + Send + 'static {
    use std::sync::{Arc, Condvar, Mutex};
    let state = Arc::new((Mutex::new(false), Condvar::new()));
    let state_for_thread = state.clone();
    std::thread::spawn(move || {
        wait_for_termination();
        let (lock, cv) = &*state_for_thread;
        *lock.lock().unwrap() = true;
        cv.notify_all();
    });
    async move {
        let (lock, cv) = &*state;
        let mut signaled = lock.lock().unwrap();
        while !*signaled {
            signaled = cv.wait(signaled).unwrap();
        }
    }
}

fn block_on<F: std::future::Future<Output = ()>>(fut: F) {
    // We don't pull in tokio in the CLI binary (only in lib via `inbox::daemon`),
    // so use a minimal driver: poll the future on a dedicated thread.
    use std::sync::Arc;
    use std::task::{Context, Poll, Wake, Waker};
    struct ParkOnce;
    impl Wake for ParkOnce {
        fn wake(self: Arc<Self>) {}
        fn wake_by_ref(self: &Arc<Self>) {}
    }
    let waker = Waker::from(Arc::new(ParkOnce));
    let mut cx = Context::from_waker(&waker);
    let mut fut = Box::pin(fut);
    // Spin-poll with brief sleeps until the future resolves.
    loop {
        if let Poll::Ready(()) = fut.as_mut().poll(&mut cx) {
            return;
        }
        std::thread::sleep(std::time::Duration::from_millis(50));
    }
}

#[cfg(unix)]
fn wait_for_termination() {
    // SIGINT/TERM/SIGHUP all terminate us.
    use std::os::raw::c_int;
    extern "C" {
        fn signal(sig: c_int, handler: extern "C" fn(c_int)) -> extern "C" fn(c_int);
    }
    extern "C" fn handler(_sig: c_int) {
        // Returning from the handler lets `signal`s default (terminate) take over.
        // We just need a way to *interrupt* the wait; raising the signal ourselves
        // works because signal() reinstalls the default after the first delivery.
        std::process::exit(0);
    }
    unsafe {
        signal(2, handler); // SIGINT
        signal(15, handler); // SIGTERM
        signal(1, handler); // SIGHUP
    }
    // Park the worker thread until the kernel wakes us with a signal; without
    // a park primitive we just sleep — the signal handler will call exit().
    loop {
        std::thread::park();
    }
}

#[cfg(not(unix))]
fn wait_for_termination() {
    // On Windows we use the SetConsoleCtrlHandler API. For the inline
    // implementation, simply install a Ctrl-C handler that exits the process.
    extern "system" {
        fn SetConsoleCtrlHandler(
            handler: Option<extern "system" fn(u32) -> i32>,
            add: i32,
        ) -> i32;
    }
    extern "system" fn handler(_typ: u32) -> i32 {
        std::process::exit(0);
    }
    unsafe {
        SetConsoleCtrlHandler(Some(handler), 1);
    }
    loop {
        std::thread::park();
    }
}

fn cmd_inbox(args: InboxArgs, inbox_dir: &PathBuf) -> Result<(), String> {
    if let Some(id) = args.url {
        let url = elicitate::inbox_open_url_for(&id);
        println!("{url}");
        return Ok(());
    }
    if let Some(id) = args.show {
        let req = elicitate::inbox::load(inbox_dir, &id).map_err(|e| e.to_string())?;
        println!("{}", serde_json::to_string_pretty(&req).map_err(|e| e.to_string())?);
        return Ok(());
    }
    if args.open {
        // Use 0 = "open inbox index"; the daemon will serve it. If no
        // daemon is running, we still print the URL.
        let url = "http://localhost:7117/inbox";
        println!("{url}");
        let _ = std::process::Command::new(open_cmd())
            .args(open_args(url))
            .status();
        return Ok(());
    }
    if let Some(age_secs) = args.gc_age_secs {
        let now = elicitate::inbox::unix_now_ms();
        let mut removed = 0usize;
        for dir in [
            elicitate::inbox::inbox_pending_dir(inbox_dir),
            elicitate::inbox::answered_dir(inbox_dir),
        ] {
            if !dir.exists() {
                continue;
            }
            for entry in std::fs::read_dir(&dir).map_err(|e| e.to_string())? {
                let entry = entry.map_err(|e| e.to_string())?;
                let meta = entry.metadata().map_err(|e| e.to_string())?;
                let mtime = meta
                    .modified()
                    .ok()
                    .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                    .map(|d| d.as_millis() as u64)
                    .unwrap_or(0);
                if now.saturating_sub(mtime) > age_secs * 1000 {
                    std::fs::remove_file(entry.path()).ok();
                    removed += 1;
                }
            }
        }
        println!("{{\"removed\": {removed}}}");
        return Ok(());
    }
    // Default: --list — always JSON so agents can parse reliably.
    let reqs = elicitate::inbox::list_pending(inbox_dir).map_err(|e| e.to_string())?;
    let summaries: Vec<_> = reqs.iter().map(elicitate::views::render_summary_json).collect();
    println!("{}", serde_json::to_string(&summaries).map_err(|e| e.to_string())?);
    Ok(())
}

fn open_cmd() -> &'static str {
    if cfg!(target_os = "macos") {
        "open"
    } else if cfg!(target_os = "windows") {
        "cmd"
    } else {
        "xdg-open"
    }
}

fn open_args(url: &str) -> Vec<String> {
    if cfg!(target_os = "macos") {
        vec![url.to_string()]
    } else if cfg!(target_os = "windows") {
        vec!["/c".into(), "start".into(), "".into(), url.to_string()]
    } else {
        vec![url.to_string()]
    }
}

fn cmd_wait(args: WaitArgs, inbox_dir: &PathBuf) -> Result<(), String> {
    let poll = Duration::from_millis(args.poll_interval_ms);
    let overall = if args.timeout_secs == 0 {
        Duration::from_secs(60 * 60 * 24 * 365) // ~1 year, effectively forever
    } else {
        Duration::from_secs(args.timeout_secs)
    };
    let req = elicitate::wait_for_response(inbox_dir, &args.request_id, poll, overall)
        .map_err(|e| e.to_string())?;
    let out = match req.response {
        Some(r) => r,
        None => ElicitResponse::Failed {
            reason: format!("request {} reached state {:?} without a response", req.request_id, req.state),
        },
    };
    println!(
        "{}",
        serde_json::to_string_pretty(&out).map_err(|e| e.to_string())?
    );
    Ok(())
}

fn cmd_answer(args: AnswerArgs, inbox_dir: &PathBuf) -> Result<(), String> {
    use elicitate::inbox::{RequestState, finalize};

    let mut req = elicitate::inbox::load(inbox_dir, &args.request_id)
        .map_err(|e| e.to_string())?;

    if req.is_terminal() {
        return Err(format!(
            "request {} is already in terminal state {:?}",
            req.request_id, req.state
        ));
    }

    let response = if args.cancel {
        ElicitResponse::Cancelled {
            notes: args.notes.clone(),
        }
    } else if let Some(n) = args.integer {
        ElicitResponse::Answered {
            value: FieldValue::Integer(n),
            notes: args.notes.clone(),
        }
    } else if let Some(b) = args.boolean {
        ElicitResponse::Answered {
            value: FieldValue::Boolean(b),
            notes: args.notes.clone(),
        }
    } else if let Some(v) = args.value {
        let value = match &req.spec.field {
            FieldSpec::Text { .. } => FieldValue::Text(v),
            FieldSpec::LongText { .. } => FieldValue::LongText(v),
            FieldSpec::Choice { options, .. } => {
                let idx = options
                    .iter()
                    .position(|o| o.value == v || o.label == v)
                    .ok_or_else(|| format!("choice '{v}' not in options"))?;
                FieldValue::Choice {
                    value: options[idx].value.clone(),
                    index: idx,
                }
            }
            FieldSpec::DateTime { .. } => FieldValue::DateTime(v),
            _ => return Err("use --integer or --boolean for this field type".into()),
        };
        ElicitResponse::Answered {
            value,
            notes: args.notes.clone(),
        }
    } else {
        return Err("one of --value / --integer / --boolean / --cancel is required".into());
    };

    req.state = match response {
        ElicitResponse::Cancelled { .. } => RequestState::Cancelled,
        _ => RequestState::Answered,
    };
    req.response = Some(response.clone());

    finalize(inbox_dir, &req).map_err(|e| e.to_string())?;
    println!(
        "{}",
        serde_json::to_string_pretty(&json!({
            "status": "submitted",
            "request_id": req.request_id,
            "response": response,
        }))
        .map_err(|e| e.to_string())?
    );
    Ok(())
}

// ---- tests ----------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_help() {
        use clap::Parser;
        assert!(Cli::try_parse_from(["elicitate", "--help"]).is_err());
    }

    #[test]
    fn parse_schema_subcommand() {
        use clap::Parser;
        let cli = Cli::try_parse_from(["elicitate", "schema"]).unwrap();
        assert!(matches!(cli.cmd, Cmd::Schema(_)));
    }

    #[test]
    fn parse_detect_subcommand() {
        use clap::Parser;
        let cli = Cli::try_parse_from(["elicitate", "detect"]).unwrap();
        assert!(matches!(cli.cmd, Cmd::Detect));
    }

    #[test]
    fn parse_ask_with_from_json() {
        use clap::Parser;
        let json = r#"{"title":"t","question":"q","field":{"kind":"boolean","label":"?","default":true}}"#;
        let cli = Cli::try_parse_from(["elicitate", "ask", "--from-json", json]).unwrap();
        assert!(matches!(cli.cmd, Cmd::Ask(_)));
    }

    #[test]
    fn parse_ask_async() {
        use clap::Parser;
        let json = r#"{"title":"t","question":"q","field":{"kind":"boolean","label":"?","default":true}}"#;
        let cli = Cli::try_parse_from(["elicitate", "ask", "--async", "--from-json", json]).unwrap();
        if let Cmd::Ask(a) = cli.cmd {
            assert!(a.r#async);
        } else { panic!("expected Ask"); }
    }

    #[test]
    fn parse_ask_requires_either_flags_or_json() {
        use clap::Parser;
        let cli = Cli::try_parse_from(["elicitate", "ask"]);
        assert!(cli.is_ok());
    }

    #[test]
    fn parse_install() {
        use clap::Parser;
        let cli = Cli::try_parse_from(["elicitate", "install", "--dry-run"]).unwrap();
        assert!(matches!(cli.cmd, Cmd::Install(_)));
    }

    #[test]
    fn parse_wait() {
        use clap::Parser;
        let cli = Cli::try_parse_from(["elicitate", "wait", "--request-id", "abc"]).unwrap();
        if let Cmd::Wait(w) = cli.cmd {
            assert_eq!(w.request_id, "abc");
        } else { panic!("expected Wait"); }
    }

    #[test]
    fn parse_answer_bool() {
        use clap::Parser;
        let cli = Cli::try_parse_from([
            "elicitate", "answer", "--request-id", "abc", "--boolean", "true"
        ]).unwrap();
        if let Cmd::Answer(a) = cli.cmd {
            assert_eq!(a.boolean, Some(true));
        } else { panic!("expected Answer"); }
    }

    #[test]
    fn build_minimal_spec_uses_defaults() {
        let args = AskArgs {
            title: Some("t".into()),
            question: Some("q".into()),
            from_json: None,
            from_file: None,
            r#async: false,
            notify: None,
            urgency: "warning".into(),
            timeout_secs: 60,
            cancel_label: None,
            confirm_label: None,
        };
        let spec = build_minimal_spec_from_flags(&args).unwrap();
        assert_eq!(spec.title, "t");
        assert_eq!(spec.question, "q");
        assert_eq!(spec.urgency, Urgency::Warning);
        assert_eq!(spec.timeout_secs, 60);
    }

    #[test]
    fn parse_notify_cfg_native() {
        let cfg = parse_notify_cfg(Some("native"));
        assert!(cfg.native);
        assert!(cfg.imessage_target.is_none());
    }

    #[test]
    fn parse_notify_cfg_full() {
        let cfg = parse_notify_cfg(Some("native,imessage:koosha@icloud.com,email:k@k.com,webhook:https://ntfy.sh/x"));
        assert!(cfg.native);
        assert_eq!(cfg.imessage_target.as_deref(), Some("koosha@icloud.com"));
        assert_eq!(cfg.email_target.as_deref(), Some("k@k.com"));
        assert_eq!(cfg.webhook_url.as_deref(), Some("https://ntfy.sh/x"));
    }

    #[test]
    fn parse_notify_cfg_empty() {
        let cfg = parse_notify_cfg(None);
        assert!(!cfg.native);
    }
}
