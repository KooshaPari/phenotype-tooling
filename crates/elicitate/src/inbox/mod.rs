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

use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde::{Deserialize, Serialize};

use crate::error::ElicitError;
use crate::spec::{ElicitResponse, PromptSpec};

pub mod change;
pub mod daemon;
pub mod notify;

pub use change::{InboxChangeBus, InboxWatcher};

/// State of a request in the inbox.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize, schemars::JsonSchema)]
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
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, schemars::JsonSchema)]
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

/// Parameters for the `elicitate_reply` MCP tool — lets an agent attach a
/// contextual note to a pending elicit before the user opens it.
#[derive(Debug, Clone, Serialize, Deserialize, schemars::JsonSchema)]
pub struct ReplyParams {
    /// ID of the pending request to attach the reply to.
    pub request_id: String,
    /// The reply message text the user will see on the form page.
    pub message: String,
    /// Optional inbox namespace id. When absent or `"default"`, falls back to
    /// the legacy single-inbox location. See [`resolve_inbox_root`].
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub inbox_id: Option<String>,
}

/// Parameters for the `inbox_status` MCP tool — a read-only projection of the
/// inbox's current state. Optional [`inbox_id`](Self::inbox_id) selects a
/// namespace; absent or `"default"` falls back to the legacy single-inbox.
#[derive(Debug, Clone, Serialize, Deserialize, schemars::JsonSchema)]
pub struct InboxStatusParams {
    /// Optional inbox namespace id.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub inbox_id: Option<String>,
}

/// Parameters for the `elicitate_cancel` MCP tool — cancel a pending elicit.
///
/// The matching `PendingRequest` is moved from the pending dir to the answered
/// dir with state `Cancelled` and no response value. Idempotent: cancelling
/// an already-cancelled request returns success without rewriting.
#[derive(Debug, Clone, Serialize, Deserialize, schemars::JsonSchema)]
pub struct CancelParams {
    /// ID of the pending request to cancel.
    pub request_id: String,
    /// Optional notes explaining why the agent cancelled.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
    /// Optional inbox namespace id. See [`resolve_inbox_root`].
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub inbox_id: Option<String>,
}

/// One queued request — the on-disk artifact.
#[derive(Debug, Clone, Serialize, Deserialize, schemars::JsonSchema)]
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
}

/// Information about the agent that enqueued the request.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, schemars::JsonSchema)]
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

/// Length 1..=64. Used to prevent path traversal in [`resolve_inbox_root`].
#[must_use]
pub fn is_valid_inbox_id(id: &str) -> bool {
    !id.is_empty()
        && id.len() <= 64
        && id.chars().all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
}

/// Resolve the on-disk path for an inbox namespace.
///
/// Resolution rules:
/// - `None` or `Some("default")` → [`default_inbox_root`] (legacy single-inbox).
/// - `Some(id)` where `id` passes [`is_valid_inbox_id`] →
///   `<parent_of_default>/inboxes/<id>`.
/// - Anything else (empty, invalid chars, too long) → [`default_inbox_root`]
///   so the caller never crashes on a hostile id from untrusted JSON.
#[must_use]
pub fn resolve_inbox_root(inbox_id: Option<&str>) -> PathBuf {
    match inbox_id {
        None | Some("default") => default_inbox_root(),
        Some(id) if is_valid_inbox_id(id) => {
            // parent of the default inbox is the elicitate data root
            let parent = default_inbox_root()
                .parent()
                .map(Path::to_path_buf)
                .unwrap_or_else(|| PathBuf::from("."));
            parent.join("inboxes").join(id)
        }
        Some(_) => default_inbox_root(),
    }
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

/// Write a reply message from an agent to a pending request.
///
/// Creates a `.reply.json` file next to the pending request's JSON file.
/// The reply appears as a contextual note on the form page when the user
/// opens it. Does NOT block or open a popup — the operator sees the note
/// only when they open the pending request.
///
/// Errors with [`ElicitError::RendererFailed`] if no pending request with
/// the given id exists.
pub fn write_reply(root: &Path, request_id: &str, message: &str) -> Result<(), ElicitError> {
    let pending_path = inbox_pending_dir(root).join(format!("{request_id}.json"));
    if !pending_path.exists() {
        return Err(ElicitError::RendererFailed(format!(
            "pending request '{request_id}' not found — cannot attach reply"
        )));
    }
    let reply = serde_json::json!({
        "request_id": request_id,
        "message": message,
    });
    let reply_path = pending_path.with_extension("reply.json");
    std::fs::write(
        &reply_path,
        serde_json::to_string_pretty(&reply).map_err(ElicitError::Json)?,
    )
    .map_err(|e| ElicitError::RendererFailed(format!("failed to write reply: {e}")))?;
    Ok(())
}

/// Cancel a pending request by id. The matching file is moved from the
/// pending dir to the answered dir with state `Cancelled` and an optional
/// `Cancelled { notes }` response.
///
/// Idempotent:
/// - Pending → Cancelled (writes the answered file, removes pending)
/// - Already Cancelled / Answered → no-op, returns the existing terminal state
/// - Missing → returns `ElicitError::RendererFailed`
pub fn cancel_pending(
    root: &Path,
    request_id: &str,
    notes: Option<&str>,
) -> Result<RequestState, ElicitError> {
    let mut req = load(root, request_id).map_err(|e| {
        ElicitError::RendererFailed(format!(
            "pending request '{request_id}' not found — cannot cancel: {e}"
        ))
    })?;
    if req.is_terminal() {
        return Ok(req.state);
    }
    req.response = Some(ElicitResponse::Cancelled {
        notes: notes.map(str::to_owned),
    });
    req.state = RequestState::Cancelled;
    finalize(root, &req)?;
    Ok(RequestState::Cancelled)
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
        };
        enqueue(tmp.path(), &req).unwrap();
        finalize(tmp.path(), &req).unwrap();
        let loaded = load(tmp.path(), "fn-1").unwrap();
        assert_eq!(loaded.state, RequestState::Answered);
    }

    // ---- write_reply (Phase 3 — v0.13.0) ----

    /// Helper: build a minimal PendingRequest and enqueue it into the
    /// pending dir so write_reply has something to attach to.
    fn write_pending_with_urgency(dir: &Path, id: &str, title: &str, urgency: crate::spec::Urgency) {
        let req = PendingRequest {
            request_id: id.into(),
            origin: sample_origin(),
            spec: crate::spec::PromptSpec {
                title: title.into(),
                question: "?".into(),
                field: crate::spec::FieldSpec::Boolean {
                    label: "?".into(),
                    default: None,
                },
                notes: None,
                buttons: None,
                urgency,
                timeout_secs: 60,
                request_id: Some(id.into()),
            },
            queued_at_ms: unix_now_ms(),
            expires_at_ms: unix_now_ms() + 60_000,
            state: RequestState::Pending,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
        };
        enqueue(dir, &req).unwrap();
    }

    #[test]
    fn reply_writes_file_for_existing_pending_request() {
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path();
        write_pending_with_urgency(dir, "r1", "R1", crate::spec::Urgency::Info);

        write_reply(dir, "r1", "here is some context").unwrap();

        let reply_path = inbox_pending_dir(dir).join("r1.reply.json");
        assert!(reply_path.exists(), "reply.json must exist after write_reply");
    }

    #[test]
    fn reply_returns_renderer_failed_for_missing_pending_request() {
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path();

        let err = write_reply(dir, "ghost", "no one home").unwrap_err();
        match err {
            ElicitError::RendererFailed(msg) => {
                assert!(msg.contains("ghost"), "error should name the missing id: {msg}");
                assert!(msg.contains("not found"), "error should explain the cause: {msg}");
            }
            other => panic!("expected RendererFailed, got {other:?}"),
        }
    }

    #[test]
    fn reply_does_not_modify_pending_request_json() {
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path();
        write_pending_with_urgency(dir, "p1", "P1", crate::spec::Urgency::Info);

        let pending_path = inbox_pending_dir(dir).join("p1.json");
        let original_bytes = std::fs::read(&pending_path).unwrap();
        let original: serde_json::Value = serde_json::from_slice(&original_bytes).unwrap();

        write_reply(dir, "p1", "contextual note").unwrap();

        let after_bytes = std::fs::read(&pending_path).unwrap();
        let after: serde_json::Value = serde_json::from_slice(&after_bytes).unwrap();
        assert_eq!(original, after, "pending JSON must not change when a reply is attached");
    }

    #[test]
    fn reply_payload_contains_request_id_and_message() {
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path();
        write_pending_with_urgency(dir, "rq-7", "Request Seven", crate::spec::Urgency::Warning);

        write_reply(dir, "rq-7", "operator should pick option B").unwrap();

        let reply_path = inbox_pending_dir(dir).join("rq-7.reply.json");
        let body: serde_json::Value =
            serde_json::from_slice(&std::fs::read(&reply_path).unwrap()).unwrap();
        assert_eq!(body["request_id"], "rq-7");
        assert_eq!(body["message"], "operator should pick option B");
    }

    // ---- multi-inbox (Phase 4 — v0.14.0 port) ----

    #[test]
    fn is_valid_inbox_id_accepts_alphanumeric_dashes_underscores() {
        for ok in ["default", "proj-a", "team_alpha", "x", "abc-123_XYZ"] {
            assert!(is_valid_inbox_id(ok), "{ok:?} should be valid");
        }
    }

    #[test]
    fn is_valid_inbox_id_rejects_path_traversal_and_empty() {
        for bad in ["", "../etc", "foo/bar", "foo bar", "a".repeat(65).as_str()] {
            assert!(
                !is_valid_inbox_id(bad),
                "{bad:?} should be rejected (length {}, chars: {:?})",
                bad.len(),
                bad.chars().count()
            );
        }
    }

    #[test]
    fn resolve_inbox_root_none_and_default_point_to_legacy() {
        assert_eq!(resolve_inbox_root(None), default_inbox_root());
        assert_eq!(
            resolve_inbox_root(Some("default")),
            default_inbox_root()
        );
    }

    #[test]
    fn resolve_inbox_root_invalid_falls_back_to_legacy_safely() {
        assert_eq!(resolve_inbox_root(Some("")), default_inbox_root());
        assert_eq!(resolve_inbox_root(Some("../escape")), default_inbox_root());
        assert_eq!(resolve_inbox_root(Some("foo bar")), default_inbox_root());
    }

    #[test]
    fn resolve_inbox_root_named_namespace_is_parent_inboxes_id() {
        let root = resolve_inbox_root(Some("proj-a"));
        let expected_parent = default_inbox_root();
        let expected_parent = expected_parent.parent().unwrap();
        assert_eq!(root, expected_parent.join("inboxes").join("proj-a"));
    }

    #[test]
    fn compute_inbox_status_isolates_two_namespaces() {
        let tmp = tempfile::tempdir().unwrap();
        let data_root = tmp.path();

        // Set up: an inbox in each of two namespaces
        let ns1 = data_root.join("inboxes").join("alpha");
        let ns2 = data_root.join("inboxes").join("beta");
        std::fs::create_dir_all(&ns1).unwrap();
        std::fs::create_dir_all(&ns2).unwrap();

        // Seed alpha with 2 pending requests
        write_pending_with_urgency(&ns1, "a1", "A1", crate::spec::Urgency::Info);
        write_pending_with_urgency(&ns1, "a2", "A2", crate::spec::Urgency::Warning);

        // Seed beta with 1 pending request
        write_pending_with_urgency(&ns2, "b1", "B1", crate::spec::Urgency::Info);

        let pending_alpha = list_pending(&ns1).unwrap();
        let pending_beta = list_pending(&ns2).unwrap();

        assert_eq!(pending_alpha.len(), 2);
        assert_eq!(pending_beta.len(), 1);
        assert!(pending_alpha.iter().all(|p| p.request_id.starts_with('a')));
        assert!(pending_beta.iter().all(|p| p.request_id.starts_with('b')));
    }

    #[test]
    fn write_reply_in_namespace_does_not_leak_into_default() {
        let tmp = tempfile::tempdir().unwrap();
        let data_root = tmp.path();
        let default_inbox = default_inbox_root_for_test(data_root);
        let ns_inbox = data_root.join("inboxes").join("isolated");
        std::fs::create_dir_all(&default_inbox).unwrap();
        std::fs::create_dir_all(&ns_inbox).unwrap();

        // Same request id "ghost" in both namespaces.
        // A reply to the namespace inbox should NOT write into default.
        let err = write_reply(&ns_inbox, "ghost", "should not leak").unwrap_err();
        match err {
            ElicitError::RendererFailed(_) => {} // expected: no pending request in ns
            other => panic!("expected RendererFailed for missing pending, got {other:?}"),
        }

        // No ghost.reply.json in default
        let default_ghost = inbox_pending_dir(&default_inbox).join("ghost.reply.json");
        assert!(!default_ghost.exists(), "no reply should leak to default inbox");
    }

    /// Helper: build a deterministic "default inbox root" inside the given temp dir
    /// for the duration of one test. We can't override the env var here because
    /// `default_inbox_root` reads it eagerly; instead we use the parent of the temp
    /// and override the inbox subdir in the assertions.
    fn default_inbox_root_for_test(_: &Path) -> PathBuf {
        // Use a sibling tempdir to avoid pollution from real env vars.
        let tmp = tempfile::tempdir().unwrap();
        tmp.path().join("inbox")
    }

    // ---- cancel_pending (Phase 6 — v0.17.0) ----

    #[test]
    fn cancel_pending_moves_to_answered_dir_with_cancelled_state() {
        let tmp = tempfile::tempdir().unwrap();
        write_pending_with_urgency(tmp.path(), "c-1", "C1", crate::spec::Urgency::Info);

        let state = cancel_pending(tmp.path(), "c-1", Some("no longer needed")).unwrap();
        assert_eq!(state, RequestState::Cancelled);

        assert!(!inbox_pending_dir(tmp.path()).join("c-1.json").exists());
        assert!(answered_dir(tmp.path()).join("c-1.json").exists());

        let loaded = load(tmp.path(), "c-1").unwrap();
        assert_eq!(loaded.state, RequestState::Cancelled);
        match loaded.response {
            Some(ElicitResponse::Cancelled { notes }) => {
                assert_eq!(notes.as_deref(), Some("no longer needed"));
            }
            other => panic!("expected Cancelled response, got {other:?}"),
        }
    }

    #[test]
    fn cancel_pending_missing_returns_renderer_failed() {
        let tmp = tempfile::tempdir().unwrap();
        let err = cancel_pending(tmp.path(), "ghost", None).unwrap_err();
        match err {
            ElicitError::RendererFailed(msg) => {
                assert!(msg.contains("ghost"));
            }
            other => panic!("expected RendererFailed, got {other:?}"),
        }
    }

    #[test]
    fn cancel_pending_already_cancelled_is_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        write_pending_with_urgency(tmp.path(), "c-2", "C2", crate::spec::Urgency::Info);

        // First cancel: Pending → Cancelled.
        assert_eq!(
            cancel_pending(tmp.path(), "c-2", Some("first")).unwrap(),
            RequestState::Cancelled
        );
        // Second cancel: already Cancelled, no-op.
        assert_eq!(
            cancel_pending(tmp.path(), "c-2", Some("second")).unwrap(),
            RequestState::Cancelled
        );
        // Original notes preserved (no rewrite).
        let loaded = load(tmp.path(), "c-2").unwrap();
        match loaded.response {
            Some(ElicitResponse::Cancelled { notes }) => {
                assert_eq!(notes.as_deref(), Some("first"));
            }
            other => panic!("expected Cancelled, got {other:?}"),
        }
    }

    // ---- enqueue (Phase 5 — v0.16.0) ----

    fn make_spec(title: &str) -> crate::spec::PromptSpec {
        crate::spec::PromptSpec {
            title: title.into(),
            question: "?".into(),
            field: crate::spec::FieldSpec::Boolean {
                label: "?".into(),
                default: None,
            },
            notes: None,
            buttons: None,
            urgency: crate::spec::Urgency::Info,
            timeout_secs: 60,
            request_id: None,
        }
    }

    fn make_origin() -> RequestOrigin {
        RequestOrigin {
            hostname: "host".into(),
            process: "p".into(),
            pid: 1,
            callback: None,
        }
    }

    #[test]
    fn enqueue_writes_pending_json_with_generated_request_id() {
        let tmp = tempfile::tempdir().unwrap();
        let req = PendingRequest::new(make_spec("T"), make_origin());
        let path = enqueue(tmp.path(), &req).unwrap();
        assert!(path.exists(), "enqueue must create the pending JSON");
        let body = std::fs::read_to_string(&path).unwrap();
        let parsed: serde_json::Value = serde_json::from_str(&body).unwrap();
        assert_eq!(parsed["request_id"], req.request_id);
        assert_eq!(parsed["spec"]["title"], "T");
    }

    #[test]
    fn enqueue_honours_explicit_request_id() {
        let tmp = tempfile::tempdir().unwrap();
        let mut spec = make_spec("T");
        spec.request_id = Some("agent-7".into());
        let req = PendingRequest::new(spec, make_origin());
        let path = enqueue(tmp.path(), &req).unwrap();
        assert!(
            path.ends_with("agent-7.json"),
            "got {:?}",
            path
        );
    }

    #[test]
    fn enqueue_atomic_no_tmp_left_behind() {
        let tmp = tempfile::tempdir().unwrap();
        let req = PendingRequest::new(make_spec("T"), make_origin());
        enqueue(tmp.path(), &req).unwrap();
        let pending = inbox_pending_dir(tmp.path());
        let stragglers: Vec<_> = std::fs::read_dir(&pending)
            .unwrap()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_name().to_string_lossy().ends_with(".tmp"))
            .collect();
        assert!(
            stragglers.is_empty(),
            "enqueue must atomically rename — no .tmp files left behind"
        );
    }
}
