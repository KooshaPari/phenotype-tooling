//! Signal handling for graceful MCP server shutdown.
//!
//! On SIGTERM/SIGINT we cancel all in-flight popups gracefully and
//! let the server exit cleanly. Because each popup is spawned in its
//! own process group (POSIX `setsid` / Windows
//! `CREATE_NEW_PROCESS_GROUP`), SIGTERM to the server does not
//! propagate to the popups — they persist until the user closes them
//! or their timeout fires. This is the desired behavior: closing the
//! terminal does not lose the user's in-progress answer.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::Duration;

use tokio::sync::oneshot;

/// Handle to orchestrate graceful MCP server shutdown.
///
/// On SIGTERM/SIGINT we wait for in-flight requests to drain up to the
/// configured timeout, then the server exits cleanly. Each popup is
/// spawned in its own process group (POSIX `setsid` / Windows
/// `CREATE_NEW_PROCESS_GROUP`), so SIGTERM to the server does not
/// propagate to the popups — they persist until the user closes them
/// or their timeout fires.
#[derive(Clone, Debug)]
pub struct ShutdownCoordinator {
    inflight: Arc<AtomicUsize>,
    shutdown_timeout: Duration,
}

impl Default for ShutdownCoordinator {
    fn default() -> Self {
        Self::new(Duration::from_secs(5))
    }
}

impl ShutdownCoordinator {
    /// Create a new coordinator with the given shutdown timeout.
    ///
    /// The timeout controls how long [`cancel_all`](Self::cancel_all)
    /// waits for in-flight requests to finish after the shutdown signal
    /// fires.
    pub fn new(shutdown_timeout: Duration) -> Self {
        Self {
            inflight: Arc::new(AtomicUsize::new(0)),
            shutdown_timeout,
        }
    }

    /// Register a new in-flight request. Returns a handle that should
    /// be dropped when the request completes.
    pub fn register(&self) -> InFlightGuard {
        self.inflight.fetch_add(1, Ordering::AcqRel);
        InFlightGuard {
            inflight: self.inflight.clone(),
        }
    }

    /// Return the current number of in-flight requests.
    pub fn inflight_count(&self) -> usize {
        self.inflight.load(Ordering::Acquire)
    }

    /// Wait for all in-flight requests to finish, up to the configured
    /// timeout. Returns the number of requests still tracked after the
    /// timeout expires (should be zero in the happy case).
    pub async fn cancel_all(&self) -> usize {
        let deadline = tokio::time::Instant::now() + self.shutdown_timeout;
        loop {
            let remaining = self.inflight.load(Ordering::Acquire);
            if remaining == 0 {
                return 0;
            }
            if tokio::time::Instant::now() >= deadline {
                return remaining;
            }
            tokio::time::sleep(Duration::from_millis(50)).await;
        }
    }

    /// Install SIGINT/SIGTERM handlers. Returns immediately; the
    /// returned `oneshot` resolves when a shutdown signal is received.
    /// When the signal fires, `cancel_all()` is called to drain in-flight
    /// requests before the receiver resolves.
    #[cfg(unix)]
    pub fn install(self: Arc<Self>) -> oneshot::Receiver<()> {
        let (tx, rx) = oneshot::channel();
        let this = self.clone();
        tokio::spawn(async move {
            use tokio::signal::unix::{signal, SignalKind};
            let mut sigterm =
                signal(SignalKind::terminate()).expect("install SIGTERM handler");
            let mut sigint =
                signal(SignalKind::interrupt()).expect("install SIGINT handler");
            tokio::select! {
                _ = sigterm.recv() => {},
                _ = sigint.recv() => {},
            }
            let remaining = this.cancel_all().await;
            tracing::info!(remaining, "graceful shutdown complete");
            let _ = tx.send(());
        });
        rx
    }

    /// Install CTRL_CLOSE handler (Windows). Returns immediately; the
    /// returned `oneshot` resolves when a shutdown signal is received.
    /// When the signal fires, `cancel_all()` is called to drain in-flight
    /// requests before the receiver resolves.
    #[cfg(not(unix))]
    pub fn install(self: Arc<Self>) -> oneshot::Receiver<()> {
        let (tx, rx) = oneshot::channel();
        let this = self.clone();
        tokio::spawn(async move {
            let _ = tokio::signal::ctrl_c().await;
            let remaining = this.cancel_all().await;
            tracing::info!(remaining, "graceful shutdown complete");
            let _ = tx.send(());
        });
        rx
    }
}

/// RAII guard that decrements the in-flight counter when dropped.
#[derive(Debug)]
pub struct InFlightGuard {
    inflight: Arc<AtomicUsize>,
}

impl Drop for InFlightGuard {
    fn drop(&mut self) {
        self.inflight.fetch_sub(1, Ordering::AcqRel);
    }
}
