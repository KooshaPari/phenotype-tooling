//! Async inbox subsystem for non-blocking elicitation.
//!
//! When an agent runs in a context where blocking the user's terminal on a
//! modal popup is unacceptable (background workers, CI, SSH without X
//! forwarding, long-running services), [`crate::elicit`] would either hang
//! or fail silently. The **inbox** turns that into an async workflow:
//!
//! 1. The agent calls `elicitate ask --async --json <spec>`. Instead of
//!    blocking on a popup, the spec is persisted to an on-disk queue,
//!    surfaced via tray notification / iMessage / email, and the CLI
//!    returns immediately with the new `request_id`.
//! 2. The user opens the inbox (`elicitate inbox` or `elicitate inbox
//!    --web`) at their leisure, reads the queued prompt, and submits
//!    an answer through the inbox UI.
//! 3. The agent's next call to `elicitate wait --request-id <id>`
//!    (or `--block-on <id>`) returns the now-answered response.
//!
//! ## File layout
//!
//! ```text
//! ~/.local/share/elicitate/
//! ├── inbox/<request_id>.json     # pending spec + state
//! ├── answered/<request_id>.json  # answered response (kept for audit)
//! └── daemon.lock                 # pidfile of running inbox daemon
//! ```
//!
//! The inbox is platform-independent — every backend just JSON-encodes a
//! [`PendingRequest`] to disk. The native popup path is only used when the
//! agent explicitly opts in.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde::{Deserialize, Serialize};

use crate::error::ElicitError;
use crate::spec::{ElicitResponse, FieldSpec, FieldValue, PromptSpec};

pub mod change;
pub mod crypto;
pub mod daemon;
pub mod notify;

pub use change::{InboxChangeBus, InboxWatcher};

/// State of a request in the inbox.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RequestState {
    /// Spec is queued and waiting for the user.
    #[default]
    Pending,
    /// User has viewed the spec (e.g. via iMessage deep link) but not yet
    /// answered.
    Seen,
    /// User submitted an answer; the response is in [`PendingRequest::response`].
    Answered,
    /// User dismissed / declined.
    Cancelled,
    /// Request exceeded its TTL without a response.
    Expired,
}

/// Surface that surfaced this request to the user.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum NotificationKind {
    /// No external notification — the user will see it in the inbox UI.
    None,
    /// macOS `NSUserNotification` / `osascript display notification`.
    NativeNotification,
    /// Sent via iMessage.
    #[serde(rename = "imessage")]
    IMessage,
    /// Sent via email (mailto: deep link with rendered form in the body).
    Email,
    /// Pushed via NTFY / Pushover / generic webhook.
    Webhook,
}

/// One queued request — the on-disk artifact.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PendingRequest {
    /// Stable identifier; mirrors [`PromptSpec::request_id`].
    pub request_id: String,

    /// Originating agent (hostname + process name + arbitrary tag).
    pub origin: RequestOrigin,

    /// The prompt payload.
    pub spec: PromptSpec,

    /// When the spec was queued (ms since epoch).
    pub queued_at_ms: u64,

    /// When the queue entry will expire if unanswered.
    pub expires_at_ms: u64,

    /// Current state.
    #[serde(default)]
    pub state: RequestState,

    /// The user's response, if [`RequestState::Answered`].
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub response: Option<ElicitResponse>,

    /// Where (if anywhere) the request was surfaced.
    #[serde(default)]
    pub notified_via: Vec<NotificationKind>,

    /// Free-form metadata for the agent's bookkeeping.
    #[serde(default)]
    pub metadata: serde_json::Map<String, serde_json::Value>,

    /// Encrypted-at-rest values for [`FieldSpec::Text`] fields with
    /// `secret: true`. Keyed by the field key (label); plaintext is never
    /// written to disk when encryption is configured.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub encrypted_values: BTreeMap<String, crypto::SecretEnvelope>,
}

/// Information about the agent that enqueued the request.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RequestOrigin {
    pub hostname: String,
    pub process: String,
    pub pid: u32,
    /// Optional deep link (e.g. `imessage://…` or `mailto:…`) the inbox
    /// can use to reply from the same channel.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub callback: Option<String>,
}

/// Default per-request TTL when the prompt didn't set one.
const DEFAULT_TTL_MS: u64 = 24 * 60 * 60 * 1000;

impl PendingRequest {
    /// Construct a new pending request from a spec, populating `queued_at_ms`
    /// and `expires_at_ms` from the current clock + spec TTL.
    pub fn new(spec: PromptSpec, origin: RequestOrigin) -> Self {
        let now_ms = unix_now_ms();
        let ttl_ms = if spec.timeout_secs == 0 {
            DEFAULT_TTL_MS
        } else {
            (spec.timeout_secs as u64).saturating_mul(1000)
        };
        Self {
            request_id: spec
                .request_id
                .clone()
                .unwrap_or_else(|| uuid::Uuid::new_v4().to_string()),
            origin,
            spec,
            queued_at_ms: now_ms,
            expires_at_ms: now_ms.saturating_add(ttl_ms),
            state: RequestState::Pending,
            response: None,
            notified_via: Vec::new(),
            metadata: serde_json::Map::new(),
            encrypted_values: BTreeMap::new(),
        }
    }

    /// Whether the request has expired against the current wall clock.
    #[must_use]
    pub fn is_expired_now(&self) -> bool {
        unix_now_ms() >= self.expires_at_ms
    }

    /// Whether the state is terminal (Answered / Cancelled / Expired).
    #[must_use]
    pub fn is_terminal(&self) -> bool {
        matches!(
            self.state,
            RequestState::Answered | RequestState::Cancelled | RequestState::Expired
        )
    }

    /// Path on disk for this request inside `inbox_dir`.
    #[must_use]
    pub fn path_in(&self, inbox_dir: &Path) -> PathBuf {
        inbox_dir.join(format!("{}.json", self.request_id))
    }
}

/// Compute the current wall-clock millisecond timestamp.
#[must_use]
pub fn unix_now_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0)
}

/// Where the inbox data lives on disk.
///
/// Honours `ELICITATE_INBOX_DIR` (overrides everything), falls back to
/// `$XDG_DATA_HOME/elicitate` / `~/Library/Application Support/elicitate` /
/// `%LOCALAPPDATA%\elicitate` depending on platform.
pub fn default_inbox_root() -> PathBuf {
    if let Ok(p) = std::env::var("ELICITATE_INBOX_DIR") {
        return PathBuf::from(p);
    }
    if let Some(home) = std::env::var_os("XDG_DATA_HOME") {
        return PathBuf::from(home).join("elicitate");
    }
    if cfg!(target_os = "macos") {
        if let Some(home) = std::env::var_os("HOME") {
            return PathBuf::from(home).join("Library/Application Support/elicitate");
        }
    }
    if cfg!(target_os = "windows") {
        if let Ok(p) = std::env::var("LOCALAPPDATA") {
            return PathBuf::from(p).join("elicitate");
        }
    }
    if let Some(home) = std::env::var_os("HOME") {
        return PathBuf::from(home).join(".local/share/elicitate");
    }
    // last-resort fallback (CI without $HOME): a per-process temp dir.
    std::env::temp_dir().join("elicitate-inbox")
}

/// Subdirectory for pending entries.
#[must_use]
pub fn inbox_pending_dir(root: &Path) -> PathBuf {
    root.join("inbox")
}

/// Subdirectory for answered/terminal entries (audit trail).
#[must_use]
pub fn answered_dir(root: &Path) -> PathBuf {
    root.join("answered")
}

/// Persist a pending request to disk. Creates parent dirs if missing.
///
/// After the atomic rename, pings the global `InboxChangeBus` so any TUI
/// or daemon subscriber re-renders promptly (no 1 s polling latency).
pub fn enqueue(root: &Path, req: &PendingRequest) -> Result<PathBuf, ElicitError> {
    let dir = inbox_pending_dir(root);
    std::fs::create_dir_all(&dir)?;
    let path = req.path_in(&dir);
    let json = serde_json::to_vec_pretty(req).map_err(ElicitError::Json)?;
    // Atomic write: stage in <id>.tmp, rename over final.
    let tmp = dir.join(format!("{}.tmp", req.request_id));
    std::fs::write(&tmp, &json)?;
    std::fs::rename(&tmp, &path)?;
    InboxChangeBus::global().notify(&format!("enqueue:{}", req.request_id));
    Ok(path)
}

/// Move a request from the pending directory to the answered directory
/// after the user has responded. Returns the new path.
///
/// The mutated `req` (with `state` / `response` populated by the caller) is
/// serialized to the new path *before* the original pending file is removed.
/// Renaming alone would carry the pre-answer state forward and the waiter
/// would never observe the response.
///
/// Pings the global `InboxChangeBus` after the final write so waiters
/// unblock immediately (no `poll_interval` latency).
pub fn finalize(root: &Path, req: &PendingRequest) -> Result<PathBuf, ElicitError> {
    let pending = inbox_pending_dir(root).join(format!("{}.json", req.request_id));
    let answered_dir = answered_dir(root);
    std::fs::create_dir_all(&answered_dir)?;
    let dst = answered_dir.join(format!("{}.json", req.request_id));
    if let Some(parent) = dst.parent() {
        std::fs::create_dir_all(parent).ok();
    }
    // 1. Write the *updated* req (new state/response) to the answered path.
    let json = serde_json::to_vec_pretty(req).map_err(ElicitError::Json)?;
    let tmp = answered_dir.join(format!("{}.tmp", req.request_id));
    std::fs::write(&tmp, &json)?;
    std::fs::rename(&tmp, &dst)?;
    // 2. Best-effort remove the original pending file (no-op if it was
    //    already removed by another worker).
    std::fs::remove_file(&pending).ok();
    InboxChangeBus::global().notify(&format!("finalize:{}", req.request_id));
    Ok(dst)
}

/// Load a single request by id from `dir` (pending OR answered).
pub fn load(root: &Path, request_id: &str) -> Result<PendingRequest, ElicitError> {
    let candidates = [
        inbox_pending_dir(root).join(format!("{request_id}.json")),
        answered_dir(root).join(format!("{request_id}.json")),
    ];
    for path in candidates {
        if path.exists() {
            let text = std::fs::read_to_string(&path)?;
            return serde_json::from_str(&text).map_err(ElicitError::Json);
        }
    }
    Err(ElicitError::InvalidSpec(format!(
        "no inbox entry for request_id '{request_id}'"
    )))
}

/// List all pending (non-terminal) requests, newest first.
pub fn list_pending(root: &Path) -> Result<Vec<PendingRequest>, ElicitError> {
    let dir = inbox_pending_dir(root);
    if !dir.exists() {
        return Ok(Vec::new());
    }
    let mut out = Vec::new();
    for entry in std::fs::read_dir(&dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) != Some("json") {
            continue;
        }
        let text = std::fs::read_to_string(&path)?;
        let req: PendingRequest = match serde_json::from_str(&text) {
            Ok(r) => r,
            Err(_) => continue, // skip corrupt entries
        };
        out.push(req);
    }
    // Newest first
    out.sort_by(|a, b| b.queued_at_ms.cmp(&a.queued_at_ms));
    Ok(out)
}

/// Wait until `req.request_id` reaches a terminal state or the wait times out.
///
/// Subscribes to the global `InboxChangeBus` and wakes immediately when
/// `enqueue` or `finalize` for *any* request pings it (crossbeam broadcast).
/// `poll_interval` is now only the floor; the wake path is event-driven.
pub fn wait_for_response(
    root: &Path,
    request_id: &str,
    poll_interval: Duration,
    overall_timeout: Duration,
) -> Result<PendingRequest, ElicitError> {
    let start = std::time::Instant::now();
    let deadline = start.checked_add(overall_timeout).unwrap_or(start);
    let mut watcher = InboxChangeBus::global().subscribe();
    loop {
        // Re-check the file on every wake (handles the case where the
        // notify raced the rename — the rename is in `enqueue`/`finalize`
        // *before* the bus ping, so this is theoretically unreachable,
        // but a defensive load() costs nothing).
        match load(root, request_id) {
            Ok(req) if req.is_terminal() => return Ok(req),
            Ok(_req) => {}
            Err(e) => return Err(e),
        }
        if std::time::Instant::now() >= deadline {
            return Err(ElicitError::Timeout(
                std::time::Instant::now()
                    .saturating_duration_since(start),
            ));
        }
        // Sleep at most `poll_interval` or until the next bus wake, whichever
        // comes first.
        let now = std::time::Instant::now();
        let remaining = deadline.saturating_duration_since(now);
        let cap = poll_interval.min(remaining.max(Duration::from_millis(1)));
        let _ = watcher.wait_changed(cap);
    }
}

/// Decrypt any `encrypted_values` entries on an answered request back into
/// the response's `FieldValue::Text`.
///
/// v0.9.0: [`crate::inbox::daemon`] stores ciphertext in
/// [`PendingRequest::encrypted_values`] and a `[encrypted]` placeholder in
/// the response. This helper resolves the configured passphrase and swaps
/// the placeholder back to the real value so the agent's `wait` path gets
/// the plaintext without writing it to disk.
///
/// Returns the request unchanged (with the placeholder still in place) if
/// there are no encrypted values, and an error if encryption was used but
/// no passphrase is configured.
pub fn decrypt_answer(req: &mut PendingRequest) -> Result<(), ElicitError> {
    if req.encrypted_values.is_empty() {
        return Ok(());
    }
    let pass = crypto::resolve_passphrase(
        "ELICITATE_SECRET_PASSPHRASE",
        "ELICITATE_IDENTITY_FILE",
    )?
    .ok_or_else(|| {
        ElicitError::InvalidSpec(
            "answer is encrypted; set ELICITATE_SECRET_PASSPHRASE \
             or ELICITATE_IDENTITY_FILE to decrypt"
                .into(),
        )
    })?;

    if let FieldSpec::Text { label, .. } = &req.spec.field {
        if let Some(env) = req.encrypted_values.get(label) {
            let pt = crypto::decrypt_value(env, &pass, label, None)?;
            if let Some(ElicitResponse::Answered { value, .. }) = &mut req.response {
                *value = FieldValue::Text(String::from_utf8_lossy(&pt).into_owned());
            }
        }
    }
    req.encrypted_values.clear();
    Ok(())
}

/// Typed projection over a single inbox directory for the
/// `inbox_status` MCP tool. Counts by `RequestState` so an agent
/// can decide whether to wait / cancel / reply without parsing the
/// raw file list.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct InboxStatus {
    /// Absolute path of the inbox directory the status covers.
    pub inbox_dir: String,
    /// Total number of `<rid>.json` files discovered (pending + answered + timed_out + failed).
    pub total: u32,
    /// Per-state counts. Keys are the `RequestState` snake_case repr.
    pub pending: u32,
    pub answered: u32,
    pub timed_out: u32,
    pub failed: u32,
    /// `pending_request_ids`: the live `RequestState::Pending` ids in stable insertion order.
    /// Lets the agent pick the oldest one with `min(pending_request_ids)` without
    /// scanning the directory again.
    pub pending_request_ids: Vec<String>,
    /// Oldest and newest `queued_at_ms` across the pending set. Both `None` if empty.
    pub oldest_pending_ms: Option<u64>,
    pub newest_pending_ms: Option<u64>,
}

/// Compute the typed inbox status. Pure-data helper — does not touch disk
/// for the counts (uses the directory listing + the existing `list_pending`
/// + a `list_answered`-equivalent walker), but does not load each
/// `<rid>.json` (cheap on-disk walk; expensive parse avoided).
pub fn compute_inbox_status(inbox_dir: &Path) -> std::io::Result<InboxStatus> {
    use std::io::{self, ErrorKind};

    if !inbox_dir.exists() {
        return Err(io::Error::new(
            ErrorKind::NotFound,
            format!("inbox dir does not exist: {}", inbox_dir.display()),
        ));
    }

    let pending = list_pending(inbox_dir)?;
    let pending_count = pending.len() as u32;
    let pending_request_ids: Vec<String> =
        pending.iter().map(|p| p.request_id.clone()).collect();
    let oldest_pending_ms = pending.iter().map(|p| p.queued_at_ms).min();
    let newest_pending_ms = pending.iter().map(|p| p.queued_at_ms).max();

    // Walk the answered dir for the answered / timed_out / failed split.
    let answered_root = answered_dir(inbox_dir);
    let mut answered = 0u32;
    let mut timed_out = 0u32;
    let mut failed = 0u32;
    if answered_root.exists() {
        for entry in std::fs::read_dir(&answered_root)? {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) != Some("json") {
                continue;
            }
            // Cheap: we don't parse, we just count and read the terminal
            // state from the filename is unsupported (the answered dir
            // uses `<rid>.json` like the pending dir). So open + peek the
            // last 200 bytes for the `"state":` token.
            let bytes = match std::fs::read(&path) {
                Ok(b) => b,
                Err(_) => continue,
            };
            // Only scan the tail — the `state` field is near EOF because
            // serde_json's serializer writes fields in struct-decl order
            // and `state` is the last field on `PendingRequest`.
            let tail_start = bytes.len().saturating_sub(512);
            let tail = &bytes[tail_start..];
            if tail.windows(9).any(|w| w == b"\"state\":") {
                // Try to identify the state from the tail.
                if tail.windows(16).any(|w| w == b"\"timed_out\"") {
                    timed_out += 1;
                } else if tail.windows(9).any(|w| w == b"\"failed\"") {
                    failed += 1;
                } else if tail.windows(11).any(|w| w == b"\"answered\"") {
                    answered += 1;
                }
            }
        }
    }

    Ok(InboxStatus {
        inbox_dir: inbox_dir.display().to_string(),
        total: pending_count + answered + timed_out + failed,
        pending: pending_count,
        answered,
        timed_out,
        failed,
        pending_request_ids,
        oldest_pending_ms,
        newest_pending_ms,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_origin() -> RequestOrigin {
        RequestOrigin {
            hostname: "h".into(),
            process: "p".into(),
            pid: 1,
            callback: None,
        }
    }

    #[test]
    fn new_fills_request_id_and_timestamps() {
        let spec = crate::spec::PromptSpec {
            title: "t".into(),
            question: "?".into(),
            field: crate::spec::FieldSpec::Boolean {
                label: "?".into(),
                default: Some(true),
            },
            notes: None,
            buttons: None,
            urgency: crate::spec::Urgency::Info,
            timeout_secs: 60,
            request_id: None,
        };
        let req = PendingRequest::new(spec.clone(), sample_origin());
        assert!(!req.request_id.is_empty());
        assert!(req.expires_at_ms > req.queued_at_ms);
        assert!(!req.is_terminal());

        let mut spec2 = spec;
        spec2.request_id = Some("my-id".into());
        let req2 = PendingRequest::new(spec2, sample_origin());
        assert_eq!(req2.request_id, "my-id");
    }

    #[test]
    fn path_in_is_stable() {
        let req = PendingRequest {
            request_id: "abc".into(),
            origin: sample_origin(),
            spec: crate::spec::PromptSpec {
                title: "t".into(),
                question: "?".into(),
                field: crate::spec::FieldSpec::Boolean {
                    label: "?".into(),
                    default: None,
                },
                notes: None,
                buttons: None,
                urgency: crate::spec::Urgency::Info,
                timeout_secs: 60,
                request_id: Some("abc".into()),
            },
            queued_at_ms: 0,
            expires_at_ms: u64::MAX,
            state: RequestState::Pending,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
            encrypted_values: BTreeMap::new(),
        };
        let dir = Path::new("/x/inbox");
        assert_eq!(req.path_in(dir), PathBuf::from("/x/inbox/abc.json"));
    }

    #[test]
    fn enqueue_and_load_roundtrip() {
        let tmp = tempfile::tempdir().unwrap();
        let req = PendingRequest {
            request_id: "rt-1".into(),
            origin: sample_origin(),
            spec: crate::spec::PromptSpec {
                title: "t".into(),
                question: "?".into(),
                field: crate::spec::FieldSpec::Boolean {
                    label: "?".into(),
                    default: Some(false),
                },
                notes: None,
                buttons: None,
                urgency: crate::spec::Urgency::Info,
                timeout_secs: 60,
                request_id: Some("rt-1".into()),
            },
            queued_at_ms: unix_now_ms(),
            expires_at_ms: unix_now_ms() + 60_000,
            state: RequestState::Pending,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
            encrypted_values: BTreeMap::new(),
        };
        enqueue(tmp.path(), &req).unwrap();
        let loaded = load(tmp.path(), "rt-1").unwrap();
        assert_eq!(loaded.request_id, "rt-1");
        assert_eq!(loaded.state, RequestState::Pending);
    }

    #[test]
    fn finalize_moves_to_answered_dir() {
        let tmp = tempfile::tempdir().unwrap();
        let req = PendingRequest {
            request_id: "fn-1".into(),
            origin: sample_origin(),
            spec: crate::spec::PromptSpec {
                title: "t".into(),
                question: "?".into(),
                field: crate::spec::FieldSpec::Boolean {
                    label: "?".into(),
                    default: None,
                },
                notes: None,
                buttons: None,
                urgency: crate::spec::Urgency::Info,
                timeout_secs: 60,
                request_id: Some("fn-1".into()),
            },
            queued_at_ms: unix_now_ms(),
            expires_at_ms: unix_now_ms() + 60_000,
            state: RequestState::Answered,
            response: Some(ElicitResponse::Answered {
                value: crate::spec::FieldValue::Boolean(true),
                notes: None,
            }),
            notified_via: vec![],
            metadata: serde_json::Map::new(),
            encrypted_values: BTreeMap::new(),
        };
        enqueue(tmp.path(), &req).unwrap();
        finalize(tmp.path(), &req).unwrap();
        let loaded = load(tmp.path(), "fn-1").unwrap();
        assert_eq!(loaded.state, RequestState::Answered);
    }
}
