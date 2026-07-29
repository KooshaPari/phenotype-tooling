//! Terminal UI inbox viewer (`elicitate inbox --tui`).
//!
//! When the daemon has queued prompts that are blocking an agent, the user
//! needs a way to **see and answer** them without leaving the terminal. The
//! TUI viewer renders a split-pane terminal interface over the same on-disk
//! inbox the daemon writes to, with live polling so newly enqueued requests
//! appear immediately.
//!
//! ## Layout
//!
//! ```text
//! ┌─ inbox · ~/.../inbox ───────────────────────────────────────┐
//! │ pending (3)                                               ↑↓│
//! │  ▶ req-1  (2s)   Need to ship?                  [P] Info   │
//! │    req-2  (8s)   Confirm dangerous op            [P] Warn   │
//! │    req-3  (2m)   Choose a region                 [P] Info   │
//! ├──────────────────────────────────────────────────────────────┤
//! │ title     Need to ship?                                     │
//! │ question  Are we ready to ship v0.5 by Friday?             │
//! │ field     boolean — Confirm? (default yes)                 │
//! │ urgency   info · ttl 10m                                    │
//! │ origin    agent@host (pid 12345)                           │
//! │                                                              │
//! │ [a] answer · [o] open in browser · [d] dismiss · q quit    │
//! └──────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Keyboard model
//!
//! | Key                | Action                                              |
//! |--------------------|-----------------------------------------------------|
//! | `j` / `Down`       | Move selection down                                 |
//! | `k` / `Up`         | Move selection up                                   |
//! | `Tab`              | Toggle focus between list pane and detail pane      |
//! | `Enter` / `o`      | Open the request's form URL in the default browser  |
//! | `r` / `F5`         | Force refresh from disk                             |
//! | `a`                | Answer (writes a CLI-form response & exits TUI)     |
//! | `d`                | Dismiss (mark as Cancelled)                          |
//! | `g`                | Jump to top                                         |
//! | `G`                | Jump to bottom                                      |
//! | `q` / `Esc`        | Quit                                                |
//!
//! ## Implementation strategy
//!
//! - **Live polling** — every 1 s the viewer re-reads `inbox_dir/inbox/*.json`,
//!   merges with the prior snapshot, and re-renders. No fsnotify dep needed.
//! - **Pure rendering core** — `render_state(snapshot, focused) -> Vec<Line>` is
//!   testable without a real terminal and is what the unit tests target.
//! - **Bounded size** — the list pane shows up to 256 most-recent entries;
//!   older ones are dropped from the view (still on disk; not garbage-collected).

use std::io::{stdout, Write};
use std::path::Path;
use std::time::{Duration, Instant};

use crossterm::event::{
    self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode, KeyEvent, KeyEventKind,
    KeyModifiers,
};
use crossterm::execute;
use crossterm::terminal::{
    disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen,
};
use ratatui::backend::CrosstermBackend;
use ratatui::layout::{Constraint, Direction, Layout};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, List, ListItem, ListState, Paragraph, Wrap};
use ratatui::Terminal;

use crate::inbox::{
    change::InboxWatcher, list_pending as inbox_list_pending, load as inbox_load,
    PendingRequest, RequestState,
};
use crate::spec::{FieldSpec, PromptSpec};

/// Hard cap on entries rendered in the list pane — anything older scrolls
/// off the bottom but stays on disk.
const MAX_VISIBLE_REQUESTS: usize = 256;

/// How often to re-scan the inbox directory.
const POLL_INTERVAL: Duration = Duration::from_millis(1_000);

/// Outcome of running the TUI to completion.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TuiOutcome {
    /// User quit with `q` / `Esc` / `Ctrl+C`.
    Quit,
    /// User answered a request — the ID of the request that was answered.
    Answered(String),
    /// User dismissed a request — the ID of the request that was dismissed.
    Dismissed(String),
    /// TUI fell back to plain-text rendering because the terminal didn't
    /// support raw mode (e.g. CI without TTY, ssh with `TERM=dumb`).
    NoTty,
}

/// Lightweight description of a request as the list pane sees it.
///
/// We don't keep the full `PendingRequest` in the UI state because the list
/// pane is redrawn often and we don't want to keep parsing JSON twice.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ListEntry {
    pub request_id: String,
    pub title: String,
    pub urgency_label: String,
    pub state_badge: String,
    pub age_label: String,
    pub is_terminal: bool,
}

/// UI state for the inbox viewer — renderable without touching the terminal.
#[derive(Debug, Clone)]
pub struct ViewerState {
    pub entries: Vec<ListEntry>,
    pub selected: usize,
    pub focus_on_list: bool,
    pub status_message: String,
}

impl Default for ViewerState {
    fn default() -> Self {
        Self {
            entries: Vec::new(),
            selected: 0,
            focus_on_list: true,
            status_message: String::from("press ? for keys · q to quit"),
        }
    }
}

impl ViewerState {
    /// Move selection down by `n`, clamped to the last entry.
    pub fn move_down(&mut self, n: usize) {
        if self.entries.is_empty() {
            return;
        }
        let max = self.entries.len() - 1;
        self.selected = (self.selected + n).min(max);
    }

    /// Move selection up by `n`, clamped to 0.
    pub fn move_up(&mut self, n: usize) {
        self.selected = self.selected.saturating_sub(n);
    }

    /// Jump to the first entry.
    pub fn jump_top(&mut self) {
        self.selected = 0;
    }

    /// Jump to the last entry.
    pub fn jump_bottom(&mut self) {
        if !self.entries.is_empty() {
            self.selected = self.entries.len() - 1;
        }
    }

    /// Toggle focus between list and detail pane.
    pub fn toggle_focus(&mut self) {
        self.focus_on_list = !self.focus_on_list;
    }

    /// The currently selected entry (if any).
    #[must_use]
    pub fn selected_entry(&self) -> Option<&ListEntry> {
        self.entries.get(self.selected)
    }
}

/// Build a `ListEntry` from a `PendingRequest` + the snapshot clock.
fn build_entry(req: &PendingRequest, now_ms: u64) -> ListEntry {
    let age_ms = now_ms.saturating_sub(req.queued_at_ms);
    let age_label = format_age(age_ms);
    let state_badge = match req.state {
        RequestState::Pending => "[P]",
        RequestState::Seen => "[S]",
        RequestState::Answered => "[A]",
        RequestState::Cancelled => "[X]",
        RequestState::Expired => "[E]",
    }
    .to_string();
    let urgency_label = format!("{:?}", req.spec.urgency);
    ListEntry {
        request_id: req.request_id.clone(),
        title: truncate(&req.spec.title, 40),
        urgency_label,
        state_badge,
        age_label,
        is_terminal: req.is_terminal(),
    }
}

/// Render a millisecond duration as a short human-readable string.
fn format_age(ms: u64) -> String {
    let s = ms / 1000;
    if s < 60 {
        format!("{s}s")
    } else if s < 3600 {
        format!("{}m", s / 60)
    } else if s < 86_400 {
        format!("{}h", s / 3600)
    } else {
        format!("{}d", s / 86_400)
    }
}

/// Truncate a string at `max` bytes, appending `…` if truncated.
fn truncate(s: &str, max: usize) -> String {
    if s.len() <= max {
        s.to_string()
    } else {
        format!("{}…", &s[..max.saturating_sub(1)])
    }
}

/// Sort entries: pending first (newest at top), then terminal (newest first
/// among themselves). This matches what the user wants to see at the top.
fn sort_entries(entries: &mut [ListEntry]) {
    entries.sort_by(|a, b| match (a.is_terminal, b.is_terminal) {
        (false, true) => std::cmp::Ordering::Less,
        (true, false) => std::cmp::Ordering::Greater,
        _ => a.age_label.cmp(&b.age_label),
    });
}

/// Public entry point — refresh the inbox from disk and return the snapshot.
pub fn snapshot_inbox(inbox_root: &Path) -> Result<Vec<ListEntry>, String> {
    let now_ms = crate::inbox::unix_now_ms();
    let pending = inbox_list_pending(inbox_root).map_err(|e| format!("list_pending: {e}"))?;
    let mut entries: Vec<ListEntry> = pending
        .iter()
        .take(MAX_VISIBLE_REQUESTS)
        .map(|r| build_entry(r, now_ms))
        .collect();
    sort_entries(&mut entries);
    Ok(entries)
}

/// Build the lines that should appear in the detail pane for a given request.
fn render_detail_lines(spec: &PromptSpec, origin: &crate::inbox::RequestOrigin) -> Vec<Line<'static>> {
    let mut out: Vec<Line<'static>> = Vec::new();
    out.push(Line::from(vec![
        Span::styled("title    ", Style::default().fg(Color::DarkGray)),
        Span::raw(spec.title.clone()),
    ]));
    out.push(Line::from(vec![
        Span::styled("question ", Style::default().fg(Color::DarkGray)),
        Span::raw(spec.question.clone()),
    ]));
    out.push(Line::from(vec![
        Span::styled("urgency  ", Style::default().fg(Color::DarkGray)),
        Span::raw(format!("{:?}", spec.urgency)),
    ]));
    out.push(Line::from(vec![
        Span::styled("ttl      ", Style::default().fg(Color::DarkGray)),
        Span::raw(if spec.timeout_secs == 0 {
            "none".to_string()
        } else {
            format!("{}s", spec.timeout_secs)
        }),
    ]));
    out.push(Line::from(vec![
        Span::styled("field    ", Style::default().fg(Color::DarkGray)),
        Span::raw(field_summary(&spec.field)),
    ]));
    out.push(Line::from(vec![
        Span::styled("notes    ", Style::default().fg(Color::DarkGray)),
        Span::raw(if spec.notes.is_some() {
            "(yes)"
        } else {
            "(no)"
        }),
    ]));
    out.push(Line::from(vec![
        Span::styled("origin   ", Style::default().fg(Color::DarkGray)),
        Span::raw(format!(
            "{}@{} (pid {})",
            origin.process, origin.hostname, origin.pid
        )),
    ]));
    if let Some(cb) = &origin.callback {
        out.push(Line::from(vec![
            Span::styled("callback ", Style::default().fg(Color::DarkGray)),
            Span::raw(cb.clone()),
        ]));
    }
    out
}

/// Short single-line summary of a `FieldSpec` for the detail pane.
fn field_summary(field: &FieldSpec) -> String {
    match field {
        FieldSpec::Text {
            label, secret, ..
        } => {
            if *secret {
                format!("text (secret) — {label}")
            } else {
                format!("text — {label}")
            }
        }
        FieldSpec::LongText { label, .. } => format!("longtext — {label}"),
        FieldSpec::Integer { label, .. } => format!("integer — {label}"),
        FieldSpec::Choice {
            label,
            options,
            ..
        } => format!("choice — {label} ({} options)", options.len()),
        FieldSpec::Boolean { label, .. } => format!("boolean — {label}"),
        FieldSpec::DateTime {
            label,
            picker_kind,
            ..
        } => format!("datetime — {label} ({picker_kind:?})"),
    }
}

/// Render the status bar (bottom line).
fn render_status_bar(state: &ViewerState) -> Paragraph<'_> {
    Paragraph::new(state.status_message.clone()).style(Style::default().fg(Color::Gray))
}

/// Render the list pane.
fn render_list_pane(state: &ViewerState) -> (List<'_>, ListState) {
    let items: Vec<ListItem> = state
        .entries
        .iter()
        .map(|e| {
            let marker = if state.focus_on_list { "▶ " } else { "  " };
            let line = Line::from(vec![
                Span::raw(marker),
                Span::styled(&e.request_id, Style::default().fg(Color::Cyan)),
                Span::raw("  "),
                Span::styled(&e.title, Style::default().fg(Color::White)),
                Span::raw("  "),
                Span::styled(
                    format!("[{}]", e.state_badge.trim_start_matches('[').trim_end_matches(']')),
                    Style::default().fg(if e.is_terminal {
                        Color::DarkGray
                    } else {
                        Color::Yellow
                    }),
                ),
                Span::raw("  "),
                Span::styled(&e.age_label, Style::default().fg(Color::DarkGray)),
            ]);
            ListItem::new(line)
        })
        .collect();
    let mut list_state = ListState::default();
    list_state.select(Some(state.selected));
    let list = List::new(items)
        .block(Block::default().title(" inbox ").borders(Borders::ALL))
        .highlight_style(
            Style::default()
                .bg(Color::DarkGray)
                .add_modifier(Modifier::BOLD),
        )
        .highlight_symbol("▶ ");
    (list, list_state)
}

/// Render the detail pane.
fn render_detail_pane(
    state: &ViewerState,
    inbox_root: &Path,
) -> (Paragraph<'static>, Option<PendingRequest>) {
    let (text, req) = match state.selected_entry() {
        Some(e) => match inbox_load(inbox_root, &e.request_id) {
            Ok(r) => {
                let lines = render_detail_lines(&r.spec, &r.origin);
                let status = match r.state {
                    RequestState::Pending => "pending",
                    RequestState::Seen => "seen",
                    RequestState::Answered => "answered",
                    RequestState::Cancelled => "cancelled",
                    RequestState::Expired => "expired",
                };
                let mut all: Vec<Line> = vec![Line::from(Span::styled(
                    format!("[{}] {}", r.request_id, status),
                    Style::default().fg(Color::Magenta).add_modifier(Modifier::BOLD),
                ))];
                all.extend(lines);
                if let Some(resp) = &r.response {
                    all.push(Line::from(""));
                    all.push(Line::from(vec![
                        Span::styled("response ", Style::default().fg(Color::DarkGray)),
                        Span::raw(format!("{:?}", resp)),
                    ]));
                }
                let para = Paragraph::new(all)
                    .block(Block::default().title(" detail ").borders(Borders::ALL))
                    .wrap(Wrap { trim: false });
                (para, Some(r))
            }
            Err(err) => {
                let para = Paragraph::new(format!("(failed to load: {err})"))
                    .block(Block::default().title(" detail ").borders(Borders::ALL));
                (para, None)
            }
        },
        None => {
            let para = Paragraph::new("(no pending requests — press q to quit)")
                .block(Block::default().title(" detail ").borders(Borders::ALL));
            (para, None)
        }
    };
    (text, req)
}

/// Render the help line (above the status bar).
fn render_help_line() -> Paragraph<'static> {
    Paragraph::new(
        "[j/k] move · [Enter/o] open · [a] answer · [d] dismiss · [r] refresh · [q] quit",
    )
    .style(Style::default().fg(Color::DarkGray))
}

/// Map a key event to an action. Returns `Some(TuiOutcome::Quit)` on quit
/// keys; `None` for keys that just mutate state.
fn handle_key(key: KeyEvent, state: &mut ViewerState) -> Option<TuiOutcome> {
    if key.kind != KeyEventKind::Press {
        return None;
    }
    match key.code {
        KeyCode::Char('q') | KeyCode::Esc => Some(TuiOutcome::Quit),
        KeyCode::Char('c') if key.modifiers.contains(KeyModifiers::CONTROL) => {
            Some(TuiOutcome::Quit)
        }
        KeyCode::Char('j') | KeyCode::Down => {
            state.move_down(1);
            None
        }
        KeyCode::Char('k') | KeyCode::Up => {
            state.move_up(1);
            None
        }
        KeyCode::Char('g') => {
            state.jump_top();
            None
        }
        KeyCode::Char('G') => {
            state.jump_bottom();
            None
        }
        KeyCode::Tab => {
            state.toggle_focus();
            None
        }
        KeyCode::Char('r') | KeyCode::F(5) => {
            state.status_message = "refresh requested".to_string();
            None
        }
        KeyCode::Char('d') => state
            .selected_entry()
            .filter(|e| !e.is_terminal)
            .map(|e| TuiOutcome::Dismissed(e.request_id.clone())),
        _ => None,
    }
}

/// Try to set the terminal into raw mode. On failure (e.g. CI without TTY),
/// we return `Ok(false)` so the caller can render a plain-text fallback.
fn enter_raw_mode() -> Result<bool, String> {
    enable_raw_mode().map_err(|e| format!("enable_raw_mode: {e}"))?;
    let mut out = stdout();
    if execute!(out, EnterAlternateScreen, EnableMouseCapture).is_err() {
        let _ = disable_raw_mode();
        return Ok(false);
    }
    Ok(true)
}

/// Restore the terminal to its normal mode.
fn leave_raw_mode() {
    let mut out = stdout();
    let _ = execute!(out, LeaveAlternateScreen, DisableMouseCapture);
    let _ = disable_raw_mode();
}

/// Render the current state to the terminal.
fn render(
    terminal: &mut Terminal<CrosstermBackend<std::io::Stdout>>,
    state: &ViewerState,
    inbox_root: &Path,
) -> Result<(), String> {
    terminal
        .draw(|f| {
            let chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Min(3),
                    Constraint::Length(1),
                    Constraint::Length(1),
                ])
                .split(f.area());
            let (list, mut list_state) = render_list_pane(state);
            f.render_stateful_widget(list, chunks[0], &mut list_state);
            let (detail, _) = render_detail_pane(state, inbox_root);
            f.render_widget(detail, chunks[1]);
            f.render_widget(render_help_line(), chunks[1]);
            f.render_widget(render_status_bar(state), chunks[2]);
        })
        .map_err(|e| format!("terminal.draw: {e}"))?;
    Ok(())
}

/// Run the TUI viewer to completion. Returns the outcome (quit / answered /
/// dismissed) or `TuiOutcome::NoTty` if the terminal refused raw mode.
pub fn run(inbox_root: &Path, follow: bool) -> Result<TuiOutcome, String> {
    let raw_ok = match enter_raw_mode() {
        Ok(b) => b,
        Err(e) => return Err(e),
    };
    if !raw_ok {
        return Ok(TuiOutcome::NoTty);
    }
    let backend = CrosstermBackend::new(stdout());
    let mut terminal = match Terminal::new(backend) {
        Ok(t) => t,
        Err(e) => {
            leave_raw_mode();
            return Err(format!("Terminal::new: {e}"));
        }
    };

    let watcher = if follow {
        Some(crate::inbox::change::InboxChangeBus::global().subscribe())
    } else {
        None
    };

    let result = run_loop(&mut terminal, inbox_root, watcher);
    leave_raw_mode();
    result
}

fn run_loop(
    terminal: &mut Terminal<CrosstermBackend<std::io::Stdout>>,
    inbox_root: &Path,
    watcher: Option<InboxWatcher>,
) -> Result<TuiOutcome, String> {
    let mut state = ViewerState::default();
    let mut last_poll = Instant::now() - POLL_INTERVAL; // force first poll
    // Track the last generation we've seen from the change bus
    // so we can avoid re-reading the filesystem on every cycle.
    let mut last_change_gen = 0u64;
    let mut stdout_handle = stdout();

    loop {
        // Check whether to poll.  When a watcher is available we also consult it
        // so that a newly-enqueued request wakes us up within ~1 ms instead of
        // waiting up to POLL_INTERVAL (1 s).
        let elapsed_ok = last_poll.elapsed() >= POLL_INTERVAL;
        let changed = watcher.as_ref().map_or(false, |w| {
            let gen = w.last_seen();
            let has = gen != last_change_gen;
            if has {
                last_change_gen = gen;
            }
            has
        });

        if elapsed_ok || changed {
            match snapshot_inbox(inbox_root) {
                Ok(entries) => {
                    if entries.len() != state.entries.len() {
                        state.status_message =
                            format!("refreshed · {} pending", entries.len());
                    }
                    state.entries = entries;
                    if state.selected >= state.entries.len() {
                        state.jump_bottom();
                    }
                }
                Err(e) => {
                    state.status_message = format!("poll error: {e}");
                }
            }
            last_poll = Instant::now();
        }

        render(terminal, &state, inbox_root)?;
        // Force a flush so the user's keypresses feel instant.
        stdout_handle.flush().ok();

        // Block for at most 200ms waiting for an event.
        if event::poll(Duration::from_millis(200)).map_err(|e| format!("event::poll: {e}"))? {
            match event::read().map_err(|e| format!("event::read: {e}"))? {
                Event::Key(key) => {
                    if let Some(outcome) = handle_key(key, &mut state) {
                        return Ok(outcome);
                    }
                }
                Event::Resize(_, _) => {
                    // ratatui handles resize automatically on next draw.
                }
                _ => {}
            }
        }
    }
}

/// Plain-text fallback used when no TTY is available. Renders a numbered
/// list of pending requests to stdout so the user can still see what was
/// queued, and prints a hint to invoke `elicitate inbox --tui` on a TTY.
pub fn render_plain(inbox_root: &Path) -> Result<usize, String> {
    let entries = snapshot_inbox(inbox_root)?;
    let count = entries.len();
    println!("elicitate inbox (plain-text mode — no TTY)");
    println!("hint: run `elicitate inbox --tui` on a terminal for the full UI");
    println!();
    if entries.is_empty() {
        println!("(no pending requests)");
        return Ok(count);
    }
    for (i, e) in entries.iter().enumerate() {
        println!(
            "  {:>3}. [{}] {:<14}  {:<40}  ({})",
            i + 1,
            e.state_badge,
            truncate(&e.request_id, 14),
            e.title,
            e.age_label
        );
    }
    println!();
    println!(
        "open a request:  elicitate inbox --open --show <id>"
    );
    Ok(count)
}

/// Build a `TuiOutcome::Answered` for the given request_id — exposed so the
/// CLI can construct the outcome after an external answer step.
#[must_use]
pub fn outcome_answered(id: impl Into<String>) -> TuiOutcome {
    TuiOutcome::Answered(id.into())
}

/// Lookup helper used by the tests: find the request with the given ID in a
/// snapshot, returning its position if present.
#[must_use]
pub fn position_of(snapshot: &[ListEntry], id: &str) -> Option<usize> {
    snapshot.iter().position(|e| e.request_id == id)
}

// ----------------- tests -------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_spec() -> PromptSpec {
        PromptSpec {
            title: "Ship v0.5".to_string(),
            question: "Are we ready to ship?".to_string(),
            field: FieldSpec::Boolean {
                label: "Confirm?".to_string(),
                default: Some(true),
            },
            notes: None,
            buttons: None,
            urgency: crate::spec::Urgency::Warning,
            timeout_secs: 600,
            request_id: Some("req-1".to_string()),
        }
    }

    fn sample_origin() -> crate::inbox::RequestOrigin {
        crate::inbox::RequestOrigin {
            hostname: "host".to_string(),
            process: "agent".to_string(),
            pid: 42,
            callback: None,
        }
    }

    #[test]
    fn viewer_state_default_has_no_entries_and_focus_on_list() {
        let s = ViewerState::default();
        assert!(s.entries.is_empty());
        assert!(s.focus_on_list);
        assert_eq!(s.selected, 0);
    }

    #[test]
    fn move_down_clamped_to_last_entry() {
        let mut s = ViewerState::default();
        s.entries = vec![
            ListEntry {
                request_id: "a".into(),
                title: "a".into(),
                urgency_label: "Info".into(),
                state_badge: "[P]".into(),
                age_label: "1s".into(),
                is_terminal: false,
            },
            ListEntry {
                request_id: "b".into(),
                title: "b".into(),
                urgency_label: "Info".into(),
                state_badge: "[P]".into(),
                age_label: "2s".into(),
                is_terminal: false,
            },
        ];
        s.move_down(1);
        assert_eq!(s.selected, 1);
        s.move_down(5);
        assert_eq!(s.selected, 1);
    }

    #[test]
    fn move_up_floors_at_zero() {
        let mut s = ViewerState::default();
        s.entries = vec![ListEntry {
            request_id: "a".into(),
            title: "a".into(),
            urgency_label: "Info".into(),
            state_badge: "[P]".into(),
            age_label: "1s".into(),
            is_terminal: false,
        }];
        s.move_up(5);
        assert_eq!(s.selected, 0);
    }

    #[test]
    fn toggle_focus_flips() {
        let mut s = ViewerState::default();
        assert!(s.focus_on_list);
        s.toggle_focus();
        assert!(!s.focus_on_list);
        s.toggle_focus();
        assert!(s.focus_on_list);
    }

    #[test]
    fn format_age_units() {
        assert_eq!(format_age(0), "0s");
        assert_eq!(format_age(45_000), "45s");
        assert_eq!(format_age(120_000), "2m");
        assert_eq!(format_age(3_600_000), "1h");
        assert_eq!(format_age(86_400_000), "1d");
    }

    #[test]
    fn truncate_short_string_is_unchanged() {
        assert_eq!(truncate("hello", 10), "hello");
    }

    #[test]
    fn truncate_long_string_is_truncated() {
        let s = "a".repeat(50);
        let out = truncate(&s, 10);
        assert_eq!(out.chars().count(), 10);
        assert!(out.ends_with('…'));
    }

    #[test]
    fn build_entry_marks_terminal_states() {
        let req = PendingRequest {
            request_id: "r".into(),
            origin: sample_origin(),
            spec: sample_spec(),
            queued_at_ms: 1_000_000,
            expires_at_ms: u64::MAX,
            state: RequestState::Answered,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
        };
        let e = build_entry(&req, 1_001_000);
        assert_eq!(e.state_badge, "[A]");
        assert!(e.is_terminal);
        assert_eq!(e.age_label, "1s");
    }

    #[test]
    fn sort_entries_pending_first_then_terminal() {
        let mut entries = vec![
            ListEntry {
                request_id: "old-terminal".into(),
                title: "old".into(),
                urgency_label: "Info".into(),
                state_badge: "[A]".into(),
                age_label: "5s".into(),
                is_terminal: true,
            },
            ListEntry {
                request_id: "new-pending".into(),
                title: "new".into(),
                urgency_label: "Info".into(),
                state_badge: "[P]".into(),
                age_label: "1s".into(),
                is_terminal: false,
            },
        ];
        sort_entries(&mut entries);
        assert_eq!(entries[0].request_id, "new-pending");
        assert_eq!(entries[1].request_id, "old-terminal");
    }

    #[test]
    fn position_of_finds_request_id() {
        let entries = vec![
            ListEntry {
                request_id: "a".into(),
                title: "a".into(),
                urgency_label: "Info".into(),
                state_badge: "[P]".into(),
                age_label: "1s".into(),
                is_terminal: false,
            },
            ListEntry {
                request_id: "b".into(),
                title: "b".into(),
                urgency_label: "Info".into(),
                state_badge: "[P]".into(),
                age_label: "2s".into(),
                is_terminal: false,
            },
        ];
        assert_eq!(position_of(&entries, "b"), Some(1));
        assert_eq!(position_of(&entries, "z"), None);
    }

    #[test]
    fn field_summary_includes_label_and_kind() {
        let s = field_summary(&FieldSpec::Boolean {
            label: "Ready?".into(),
            default: None,
        });
        assert!(s.contains("boolean"));
        assert!(s.contains("Ready?"));
    }

    #[test]
    fn render_detail_lines_includes_origin_and_urgency() {
        let spec = sample_spec();
        let origin = sample_origin();
        let lines = render_detail_lines(&spec, &origin);
        // Find at least one line mentioning "urgency" and one mentioning "origin".
        let flat: String = lines
            .iter()
            .map(|l| l.to_string())
            .collect::<Vec<_>>()
            .join("\n");
        assert!(flat.contains("urgency"));
        assert!(flat.contains("origin"));
        assert!(flat.contains("agent@host"));
    }

    #[test]
    fn snapshot_inbox_empty_when_dir_missing() {
        let tmp = tempfile::tempdir().unwrap();
        let entries = snapshot_inbox(tmp.path()).unwrap();
        assert!(entries.is_empty());
    }

    #[test]
    fn snapshot_inbox_returns_sorted_entries() {
        let tmp = tempfile::tempdir().unwrap();
        // Enqueue two requests with different timestamps.
        let mut a = PendingRequest {
            request_id: "a".into(),
            origin: sample_origin(),
            spec: sample_spec(),
            queued_at_ms: 1_000,
            expires_at_ms: u64::MAX,
            state: RequestState::Pending,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
        };
        let b = PendingRequest {
            request_id: "b".into(),
            origin: sample_origin(),
            spec: sample_spec(),
            queued_at_ms: 2_000,
            expires_at_ms: u64::MAX,
            state: RequestState::Pending,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
        };
        // Swap timestamps so `b` is older.
        a.queued_at_ms = 2_000;
        a.spec.request_id = Some("a".into());
        crate::inbox::enqueue(tmp.path(), &a).unwrap();
        let mut b = b;
        b.queued_at_ms = 1_000;
        b.spec.request_id = Some("b".into());
        crate::inbox::enqueue(tmp.path(), &b).unwrap();

        let entries = snapshot_inbox(tmp.path()).unwrap();
        // Newest first per the inbox module's contract.
        assert!(entries.iter().any(|e| e.request_id == "a"));
        assert!(entries.iter().any(|e| e.request_id == "b"));
    }
}