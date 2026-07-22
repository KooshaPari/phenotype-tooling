//! Signal handling for graceful MCP server shutdown.
//!
//! On SIGTERM/SIGINT we cancel all in-flight popups gracefully and
//! let the server exit cleanly. Because each popup is spawned in its
//! own process group (POSIX `setsid` / Windows
//! `CREATE_NEW_PROCESS_GROUP`), SIGTERM to the server does not
//! propagate to the popups — they persist until the user closes them
//! or their timeout fires. This is the desired behavior: closing the
//! terminal should not lose the user's in-progress answer.

use std::collections::HashMap;
use std::sync::Arc;

use tokio::sync::{oneshot, Mutex};

#[derive(Debug, Default)]
pub struct ShutdownCoordinator {
    inflight: Arc<Mutex<HashMap<String, oneshot::Sender<()>>>>,
}

impl ShutdownCoordinator {
    /// Install SIGINT/SIGTERM handlers. Returns immediately; the
    /// returned `oneshot` resolves when a shutdown signal is received.
    #[cfg(unix)]
    pub fn install() -> tokio::sync::oneshot::Receiver<()> {
        let (tx, rx) = tokio::sync::oneshot::channel();
        tokio::spawn(async move {
            use tokio::signal::unix::{signal, SignalKind};
            let mut sigterm = signal(SignalKind::terminate()).expect("install SIGTERM handler");
            let mut sigint = signal(SignalKind::interrupt()).expect("install SIGINT handler");
            tokio::select! {
                _ = sigterm.recv() => {},
                _ = sigint.recv() => {},
            }
            let _ = tx.send(());
        });
        rx
    }

    #[cfg(not(unix))]
    pub fn install() -> tokio::sync::oneshot::Receiver<()> {
        let (tx, rx) = tokio::sync::oneshot::channel();
        tokio::spawn(async move {
            let _ = tokio::signal::ctrl_c().await;
            let _ = tx.send(());
        });
        rx
    }
}