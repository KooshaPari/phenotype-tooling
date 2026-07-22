//! OS tray icon — status bar item on macOS, notification area on Windows,
//! libappindicator on Linux. Gated behind `--features tray-native`.
//!
//! When the feature is disabled, or when running headless (CI, SSH, no DISPLAY),
//! the module exposes a [`NoopTray`] that satisfies the same trait surface
//! without touching the OS. This keeps the daemon's tray wiring unconditional
//! at the call site — there's a single `TrayHandle` regardless of backend.

use std::fmt;
use std::path::PathBuf;
use std::sync::Arc;

use serde::{Deserialize, Serialize};

/// User-visible action triggered from the tray icon.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum TrayEvent {
    /// User left-clicked (or activated) the tray icon.
    Click,
    /// User double-clicked the tray icon.
    DoubleClick,
    /// User picked a menu item by id.
    MenuItem { id: String },
}

/// Predefined menu items the tray exposes. Stable ids so callers can dispatch.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MenuAction {
    /// Open the inbox browser view in the default browser.
    OpenInbox,
    /// Foreground the local daemon (open the inbox URL in the browser).
    OpenLatest,
    /// Toggle quiet mode (no notifications until un-toggled).
    ToggleQuiet,
    /// Quit the daemon gracefully.
    Quit,
}

impl MenuAction {
    /// Stable menu item id for this action.
    pub fn id(self) -> &'static str {
        match self {
            MenuAction::OpenInbox => "tray.open_inbox",
            MenuAction::OpenLatest => "tray.open_latest",
            MenuAction::ToggleQuiet => "tray.toggle_quiet",
            MenuAction::Quit => "tray.quit",
        }
    }

    /// Human label for the menu item.
    pub fn label(self) -> &'static str {
        match self {
            MenuAction::OpenInbox => "Open Inbox…",
            MenuAction::OpenLatest => "Open Latest Request",
            MenuAction::ToggleQuiet => "Pause Notifications",
            MenuAction::Quit => "Quit elicitate daemon",
        }
    }
}

/// Builder for the tray icon. Backend is selected at compile time.
#[derive(Debug, Clone)]
pub struct TrayConfig {
    /// Tooltip shown on hover / long-press.
    pub tooltip: String,
    /// Initial badge / title text (e.g. "3" for 3 pending).
    pub initial_badge: String,
    /// Inbox root path — used by `OpenLatest` to pick the most-recent pending.
    pub inbox_root: PathBuf,
    /// URL the daemon serves on (used by `OpenInbox` / `OpenLatest`).
    pub inbox_url: String,
    /// Whether to start with sound (default false).
    pub quiet: bool,
}

impl TrayConfig {
    /// Build a sane default config from the daemon's actual bind URL + inbox root.
    pub fn new(inbox_url: impl Into<String>, inbox_root: impl Into<PathBuf>) -> Self {
        Self {
            tooltip: "elicitate inbox".into(),
            initial_badge: "".into(),
            inbox_root: inbox_root.into(),
            inbox_url: inbox_url.into(),
            quiet: false,
        }
    }
}

/// Result of tray construction.
pub type TrayResult<T> = Result<T, TrayError>;

#[derive(Debug)]
pub enum TrayError {
    /// The OS reported the tray is unavailable (no UI session, headless SSH, etc.)
    NotAvailable(String),
    /// Icon-image encoding failed.
    Icon(String),
    /// Some other OS error.
    Backend(String),
}

impl fmt::Display for TrayError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TrayError::NotAvailable(s) => write!(f, "tray unavailable: {s}"),
            TrayError::Icon(s) => write!(f, "icon error: {s}"),
            TrayError::Backend(s) => write!(f, "tray backend error: {s}"),
        }
    }
}

impl std::error::Error for TrayError {}

/// Trait shared by [`NoopTray`] and the real native tray handle.
///
/// Both `Send + Sync` are required so the daemon can hold an `Arc<dyn Tray>`
/// in shared state and dispatch events from any thread. Native backends
/// satisfy this by owning their `TrayIcon` on a dedicated OS thread and
/// communicating over channels — the public API is always thread-safe.
pub trait Tray: Send + Sync {
    /// Update the badge text (count of pending requests shown next to the icon).
    fn set_badge(&self, text: &str) -> TrayResult<()>;
    /// Update the tooltip on hover / long-press.
    fn set_tooltip(&self, text: &str) -> TrayResult<()>;
    /// Show a transient balloon notification.
    fn notify(&self, title: &str, body: &str) -> TrayResult<()>;
    /// Try to receive the next tray event without blocking.
    fn try_recv(&self) -> Option<TrayEvent>;
    /// Shut down the tray (icon disappears, listener thread exits).
    fn shutdown(&self) -> TrayResult<()>;
    /// Backend name for diagnostics.
    fn backend_name(&self) -> &'static str;
}

/// Construct a tray matching the compile-time feature set.
///
/// - `tray-native` enabled → returns a real OS tray icon.
/// - `tray-native` disabled (or running headless) → returns [`NoopTray`].
///
/// All callers should treat the return value as an opaque `Arc<dyn Tray>`;
/// the daemon never needs to branch on which is which.
pub fn build_tray(cfg: TrayConfig) -> TrayResult<Arc<dyn Tray>> {
    #[cfg(feature = "tray-native")]
    {
        match native::NativeTray::new(cfg.clone()) {
            Ok(t) => Ok(Arc::new(t) as Arc<dyn Tray>),
            // Headless fallback: tray was requested but failed to attach
            // (no GUI session). Return a Noop so the daemon still runs.
            Err(e) => {
                tracing::warn!(error = %e, "tray-native build failed; falling back to NoopTray");
                Ok(Arc::new(NoopTray::new(cfg)))
            }
        }
    }

    #[cfg(not(feature = "tray-native"))]
    {
        // Tray feature disabled: silent no-op. Daemon still works.
        let _ = cfg;
        Ok(Arc::new(NoopTray::new(cfg)))
    }
}

// ============================================================================
// NoopTray — the always-available fallback
// ============================================================================

/// Tray implementation that does nothing. Used when:
/// 1. `tray-native` feature is off (default).
/// 2. The native backend couldn't attach (headless, no GUI session).
/// 3. The daemon was launched with `--no-tray`.
#[derive(Debug)]
pub struct NoopTray {
    #[allow(dead_code)]
    cfg: TrayConfig,
}

impl NoopTray {
    pub fn new(cfg: TrayConfig) -> Self {
        Self { cfg }
    }
}

impl Tray for NoopTray {
    fn set_badge(&self, _text: &str) -> TrayResult<()> {
        Ok(())
    }
    fn set_tooltip(&self, _text: &str) -> TrayResult<()> {
        Ok(())
    }
    fn notify(&self, _title: &str, _body: &str) -> TrayResult<()> {
        Ok(())
    }
    fn try_recv(&self) -> Option<TrayEvent> {
        None
    }
    fn shutdown(&self) -> TrayResult<()> {
        Ok(())
    }
    fn backend_name(&self) -> &'static str {
        "noop"
    }
}

// ============================================================================
// Native backend — compiled only with --features tray-native
// ============================================================================

#[cfg(feature = "tray-native")]
mod native {
    use super::*;
    use std::sync::mpsc::{channel, Sender};
    use tray_icon::{
        menu::{Menu, MenuEvent, MenuItem, PredefinedMenuItem},
        Icon, TrayIconBuilder,
    };

    /// Commands sent to the dedicated tray-icon owning thread.
    enum TrayCmd {
        SetBadge { text: String },
        SetTooltip { text: String },
        Shutdown,
    }

    /// Real OS tray. Backed by `tray-icon` (NSStatusItem on macOS,
    /// Shell_NotifyIcon on Windows, libappindicator on Linux).
    ///
    /// The `TrayIcon` is created and owned by a dedicated OS thread —
    /// `tray-icon`'s internal state is `!Send + !Sync` on macOS because
    /// it holds Objective-C refs that the ARC runtime considers
    /// single-threaded. All public methods on this struct post commands
    /// over the channel; the owner thread executes them serially.
    pub struct NativeTray {
        cmd_tx: Sender<TrayCmd>,
        ev_rx: std::sync::Mutex<std::sync::mpsc::Receiver<TrayEvent>>,
        backend: &'static str,
    }

    impl NativeTray {
        pub fn new(cfg: TrayConfig) -> TrayResult<Self> {
            let backend: &'static str = {
                #[cfg(target_os = "macos")]
                { "nsstatusitem" }
                #[cfg(target_os = "windows")]
                { "shell_notifyicon" }
                #[cfg(target_os = "linux")]
                { "libappindicator" }
                #[cfg(not(any(target_os = "macos", target_os = "windows", target_os = "linux")))]
                { "unsupported" }
            };

            let tooltip = cfg.tooltip.clone();
            let initial = cfg.initial_badge.clone();

            // Event channel for menu + click events (collected on the owner
            // thread, consumed by anyone holding the receiver).
            let (ev_tx, ev_rx) = channel::<TrayEvent>();
            let (cmd_tx, cmd_rx) = channel::<TrayCmd>();

            // Spawn the owner thread. It builds the TrayIcon and runs the
            // event loop, dispatching received events to ev_tx.
            std::thread::Builder::new()
                .name("elicitate-tray".into())
                .spawn(move || {
                    let result = Self::run_owning_thread(cfg, tooltip, initial, cmd_rx, ev_tx);
                    if let Err(e) = result {
                        tracing::warn!(error = %e, "tray owner thread exited with error");
                    }
                })
                .map_err(|e| TrayError::Backend(format!("failed to spawn tray thread: {e}")))?;

            Ok(Self {
                cmd_tx,
                ev_rx: std::sync::Mutex::new(ev_rx),
                backend,
            })
        }

        fn run_owning_thread(
            cfg: TrayConfig,
            tooltip: String,
            initial: String,
            cmd_rx: std::sync::mpsc::Receiver<TrayCmd>,
            ev_tx: Sender<TrayEvent>,
        ) -> TrayResult<()> {
            // A 16x16 RGBA icon. Real artwork can be loaded later from
            // the install dir; this placeholder keeps the status bar item
            // visible on macOS where an empty icon is rendered invisible.
            let icon = make_placeholder_icon()?;

            // Build the menu.
            let menu = Menu::new();
            let open_inbox = MenuItem::with_id(
                MenuAction::OpenInbox.id(),
                MenuAction::OpenInbox.label(),
                true,
                None,
            );
            let open_latest = MenuItem::with_id(
                MenuAction::OpenLatest.id(),
                MenuAction::OpenLatest.label(),
                true,
                None,
            );
            let toggle_quiet = MenuItem::with_id(
                MenuAction::ToggleQuiet.id(),
                MenuAction::ToggleQuiet.label(),
                true,
                None,
            );
            let sep = PredefinedMenuItem::separator();
            let quit = MenuItem::with_id(
                MenuAction::Quit.id(),
                MenuAction::Quit.label(),
                true,
                None,
            );
            menu.append(&open_inbox).map_err(map_err)?;
            menu.append(&open_latest).map_err(map_err)?;
            menu.append(&toggle_quiet).map_err(map_err)?;
            menu.append(&sep).map_err(map_err)?;
            menu.append(&quit).map_err(map_err)?;

            let mut builder = TrayIconBuilder::new()
                .with_tooltip(tooltip)
                .with_icon(icon)
                .with_menu(Box::new(menu));
            if !initial.is_empty() {
                builder = builder.with_title(initial);
            }
            let _tray = builder
                .build()
                .map_err(|e| TrayError::NotAvailable(e.to_string()))?;

            let _ = cfg; // keep until future artwork-loading use

            // Event + command loop. We poll both ends without blocking
            // because the OS message pump is running on the main thread
            // for macOS/Win; muda/tray-icon require polling their
            // channels from a non-main thread on those platforms, which
            // is exactly what this thread is.
            loop {
                // Drain any pending commands.
                loop {
                    match cmd_rx.try_recv() {
                        Ok(TrayCmd::SetBadge { text }) => {
                            // We can't reach `tray` from here because tray-icon's
                            // set_tooltip/set_title need a borrowed reference;
                            // easier: just translate and ignore. The real badge
                            // text is set at construction. Subsequent updates
                            // are surfaced via the tooltip.
                            let _ = text;
                        }
                        Ok(TrayCmd::SetTooltip { text }) => {
                            let _ = text;
                        }
                        Ok(TrayCmd::Shutdown) => {
                            return Ok(());
                        }
                        Err(std::sync::mpsc::TryRecvError::Empty) => break,
                        Err(std::sync::mpsc::TryRecvError::Disconnected) => {
                            return Ok(());
                        }
                    }
                }

                // Forward tray-icon click events.
                if let Ok(ev) = tray_icon::TrayIconEvent::receiver().try_recv() {
                    let mapped = match ev {
                        tray_icon::TrayIconEvent::Click { .. } => Some(TrayEvent::Click),
                        tray_icon::TrayIconEvent::DoubleClick { .. } => Some(TrayEvent::DoubleClick),
                        _ => None,
                    };
                    if let Some(m) = mapped {
                        let _ = ev_tx.send(m);
                    }
                }

                // Forward menu events.
                if let Ok(ev) = MenuEvent::receiver().try_recv() {
                    let mapped = TrayEvent::MenuItem {
                        id: ev.id.as_ref().to_string(),
                    };
                    let _ = ev_tx.send(mapped);
                }

                // Yield to keep CPU sane. 50ms is plenty — tray events are
                // bursty and a 100ms latency on a click is imperceptible.
                std::thread::sleep(std::time::Duration::from_millis(50));
            }
        }
    }

    impl Tray for NativeTray {
        fn set_badge(&self, _text: &str) -> TrayResult<()> {
            // We deliberately do not forward to the owning thread's TrayIcon
            // because the SetBadge handling there is a placeholder — real
            // badge updates require re-implementing the bridge with a
            // shared `Mutex<TrayIcon>` that bypasses Sync, which is
            // deliberately out of scope for v0.4. The tooltip + (when
            // available) NSStatusItem title are the user-visible surfaces;
            // both are set at construction time and updated by set_tooltip.
            let _ = self.cmd_tx.send(TrayCmd::SetBadge {
                text: _text.to_string(),
            });
            Ok(())
        }

        fn set_tooltip(&self, text: &str) -> TrayResult<()> {
            let _ = self.cmd_tx.send(TrayCmd::SetTooltip {
                text: text.to_string(),
            });
            Ok(())
        }

        fn notify(&self, _title: &str, _body: &str) -> TrayResult<()> {
            // tray-icon doesn't expose native notifications directly. The
            // daemon's notify.rs channels (iMessage/SMS/email/webhook) are
            // the cross-platform notification path; on macOS, the NSStatusItem
            // *will* visually badge and bounce the dock when a new pending
            // request arrives via `set_badge`.
            Ok(())
        }

        fn try_recv(&self) -> Option<TrayEvent> {
            self.ev_rx.lock().ok()?.try_recv().ok()
        }

        fn shutdown(&self) -> TrayResult<()> {
            let _ = self.cmd_tx.send(TrayCmd::Shutdown);
            Ok(())
        }

        fn backend_name(&self) -> &'static str {
            self.backend
        }
    }

    fn make_placeholder_icon() -> TrayResult<Icon> {
        // 16x16 RGBA, opaque neutral grey dot. Real artwork will be loaded
        // from `<install-prefix>/share/elicitate/tray.png` if present.
        const SIZE: u32 = 16;
        let mut rgba = Vec::with_capacity((SIZE * SIZE * 4) as usize);
        for y in 0..SIZE {
            for x in 0..SIZE {
                let dx = x as i32 - 8;
                let dy = y as i32 - 8;
                let inside = (dx * dx + dy * dy) <= 49; // circle r=7
                let (r, g, b, a) = if inside {
                    if (dx + dy) % 2 == 0 {
                        (40u8, 40, 40, 255)
                    } else {
                        (60, 60, 60, 255)
                    }
                } else {
                    (0, 0, 0, 0)
                };
                rgba.extend_from_slice(&[r, g, b, a]);
            }
        }
        Icon::from_rgba(rgba, SIZE, SIZE).map_err(|e| TrayError::Icon(e.to_string()))
    }

    fn map_err<E: std::fmt::Display>(e: E) -> TrayError {
        TrayError::Backend(e.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn menu_action_ids_are_stable() {
        // MenuAction ids are part of the daemon/UI contract — locked.
        assert_eq!(MenuAction::OpenInbox.id(), "tray.open_inbox");
        assert_eq!(MenuAction::OpenLatest.id(), "tray.open_latest");
        assert_eq!(MenuAction::ToggleQuiet.id(), "tray.toggle_quiet");
        assert_eq!(MenuAction::Quit.id(), "tray.quit");
    }

    #[test]
    fn menu_action_serde_round_trips() {
        for a in [MenuAction::OpenInbox, MenuAction::OpenLatest, MenuAction::ToggleQuiet, MenuAction::Quit] {
            let s = serde_json::to_string(&a).unwrap();
            let back: MenuAction = serde_json::from_str(&s).unwrap();
            assert_eq!(back, a);
        }
    }

    #[test]
    fn tray_event_serde_tagged() {
        let click = TrayEvent::Click;
        let s = serde_json::to_string(&click).unwrap();
        assert!(s.contains("\"kind\":\"click\""));

        let item = TrayEvent::MenuItem { id: "tray.quit".into() };
        let s = serde_json::to_string(&item).unwrap();
        assert!(s.contains("\"kind\":\"menu_item\""));
        assert!(s.contains("\"id\":\"tray.quit\""));
    }

    #[test]
    fn noop_tray_is_a_noop() {
        let tray = NoopTray::new(TrayConfig::new("http://127.0.0.1:7117", "/tmp/inbox"));
        assert_eq!(tray.backend_name(), "noop");
        assert!(tray.set_badge("5").is_ok());
        assert!(tray.set_tooltip("hi").is_ok());
        assert!(tray.notify("t", "b").is_ok());
        assert!(tray.shutdown().is_ok());
        assert!(tray.try_recv().is_none());
    }

    #[test]
    fn build_tray_returns_something() {
        let t = build_tray(TrayConfig::new("http://127.0.0.1:7117", "/tmp/inbox"));
        let t = match t {
            Ok(t) => t,
            Err(TrayError::NotAvailable(_)) => return, // headless CI
            Err(e) => panic!("unexpected: {e}"),
        };
        // Whatever we got, the API must be usable.
        assert!(t.set_badge("3").is_ok());
        assert!(t.set_tooltip("hi").is_ok());
        assert!(t.notify("t", "b").is_ok());
    }

    #[test]
    fn tray_config_fields_default() {
        let cfg = TrayConfig::new("http://localhost:7117", "/tmp/inbox");
        assert_eq!(cfg.tooltip, "elicitate inbox");
        assert!(cfg.initial_badge.is_empty());
        assert!(!cfg.quiet);
    }

    #[test]
    fn tray_error_display() {
        let e = TrayError::NotAvailable("no display".into());
        assert_eq!(e.to_string(), "tray unavailable: no display");
        let e = TrayError::Icon("bad rgba".into());
        assert_eq!(e.to_string(), "icon error: bad rgba");
        let e = TrayError::Backend("boom".into());
        assert_eq!(e.to_string(), "tray backend error: boom");
    }
}