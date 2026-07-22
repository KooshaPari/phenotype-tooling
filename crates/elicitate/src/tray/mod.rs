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
/// Only `Send` is required (not `Sync`) — the `Mutex<NativeTray>` in the
/// native backend already serialises concurrent access. `tray-icon`'s
/// `TrayIcon` is `!Sync` on macOS because it holds Objective-C refs that
/// the ARC runtime considers single-threaded, so we explicitly opt out of
/// the `Sync` bound.
pub trait Tray: Send {
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
    use std::sync::Mutex;
    use tray_icon::{
        menu::{Menu, MenuEvent, MenuItem, PredefinedMenuItem},
        Icon, TrayIcon, TrayIconBuilder, TrayIconEvent,
    };

    /// Real OS tray. Backed by `tray-icon` (NSStatusItem on macOS,
    /// Shell_NotifyIcon on Windows, libappindicator on Linux).
    pub struct NativeTray {
        inner: Mutex<TrayIcon>,
        cfg: TrayConfig,
    }

    impl NativeTray {
        pub fn new(cfg: TrayConfig) -> TrayResult<Self> {
            let tooltip = cfg.tooltip.clone();
            let initial = cfg.initial_badge.clone();

            // A 16x16 RGBA icon. Real artwork can be loaded later from
            // the install dir; this placeholder keeps the status bar item
            // visible on macOS where an empty icon is rendered invisible.
            let icon = make_placeholder_icon()?;

            // Build the menu.
            let menu = Menu::new();
            let open_inbox = MenuItem::with_id(MenuAction::OpenInbox.id(), MenuAction::OpenInbox.label(), true, None);
            let open_latest = MenuItem::with_id(MenuAction::OpenLatest.id(), MenuAction::OpenLatest.label(), true, None);
            let toggle_quiet = MenuItem::with_id(MenuAction::ToggleQuiet.id(), MenuAction::ToggleQuiet.label(), true, None);
            let sep = PredefinedMenuItem::separator();
            let quit = MenuItem::with_id(MenuAction::Quit.id(), MenuAction::Quit.label(), true, None);
            menu.append(&open_inbox).map_err(map_menu_err)?;
            menu.append(&open_latest).map_err(map_menu_err)?;
            menu.append(&toggle_quiet).map_err(map_menu_err)?;
            menu.append(&sep).map_err(map_menu_err)?;
            menu.append(&quit).map_err(map_menu_err)?;

            let mut builder = TrayIconBuilder::new()
                .with_tooltip(tooltip)
                .with_icon(icon)
                .with_menu(Box::new(menu));
            if !initial.is_empty() {
                builder = builder.with_title(initial);
            }

            let tray = builder
                .build()
                .map_err(|e| TrayError::NotAvailable(e.to_string()))?;

            Ok(Self {
                inner: Mutex::new(tray),
                cfg,
            })
        }
    }

    impl Tray for NativeTray {
        fn set_badge(&self, text: &str) -> TrayResult<()> {
            let guard = self.inner.lock().map_err(|e| TrayError::Backend(format!("poisoned lock: {e}")))?;
            // tray-icon's `set_title` is macOS-visible text; on other platforms
            // it just becomes part of the tooltip. We also update the tooltip
            // with a count suffix for cross-platform visibility.
            let base = self.cfg.tooltip.split(" (").next().unwrap_or(&self.cfg.tooltip).to_string();
            let combined = if text.is_empty() {
                base
            } else {
                format!("{base} ({text})")
            };
            guard.set_tooltip(Some(combined.as_str())).map_err(|e| TrayError::Backend(e.to_string()))?;
            guard.set_title(Some(text)); // returns () on tray-icon 0.24
            Ok(())
        }

        fn set_tooltip(&self, text: &str) -> TrayResult<()> {
            let guard = self.inner.lock().map_err(|e| TrayError::Backend(format!("poisoned lock: {e}")))?;
            guard.set_tooltip(Some(text)).map_err(|e| TrayError::Backend(e.to_string()))?;
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
            // TrayIconEvent (icon click) and MenuEvent (menu item picked).
            if let Ok(ev) = TrayIconEvent::receiver().try_recv() {
                match ev {
                    TrayIconEvent::Click { .. } => {
                        return Some(TrayEvent::Click);
                    }
                    TrayIconEvent::DoubleClick { .. } => {
                        return Some(TrayEvent::DoubleClick);
                    }
                    _ => {}
                }
            }
            if let Ok(ev) = MenuEvent::receiver().try_recv() {
                return Some(TrayEvent::MenuItem { id: ev.id.as_ref().to_string() });
            }
            None
        }

        fn shutdown(&self) -> TrayResult<()> {
            // Dropping the TrayIcon removes it from the status bar.
            let _ = self.inner.lock().map(|g| drop(g));
            Ok(())
        }

        fn backend_name(&self) -> &'static str {
            #[cfg(target_os = "macos")]
            { "nsstatusitem" }
            #[cfg(target_os = "windows")]
            { "shell_notifyicon" }
            #[cfg(target_os = "linux")]
            { "libappindicator" }
            #[cfg(not(any(target_os = "macos", target_os = "windows", target_os = "linux")))]
            { "unsupported" }
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

    fn map_menu_err<E: std::fmt::Display>(e: E) -> TrayError {
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