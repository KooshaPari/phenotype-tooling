//! Render the inbox UI — both the form fragment embedded into the
//! daemon's HTML response and a self-contained printable plain-text
//! version that ships via iMessage / email.
//!
//! The HTML renderer returns the inner form fragment so the HTTP
//! server can wrap it in its global stylesheet. The plain-text
//! renderer is what gets pasted into a `mailto:` body.

use crate::inbox::PendingRequest;
use crate::spec::{FieldSpec, FieldValue};

/// Render the form fragment for a request — input(s), notes box, OK +
/// Cancel buttons. This is the body the daemon splices into its full
/// HTML page; calling it directly is useful when embedding the inbox
/// inside another UI.
#[must_use]
pub fn render_form_html(req: &PendingRequest) -> String {
    let field = field_to_html(&req.spec.field, &req.request_id);
    let notes = notes_to_html(&req.spec.notes);
    let id = html_attr(&req.request_id);
    format!(
        "<form method=\"POST\" action=\"/answer/{id}\" id=form-{id}>\
           {field}\
           {notes}\
           <div class=actions>\
             <button type=\"submit\" name=\"cancel\" value=\"1\" class=cancel>Cancel</button>\
             <button type=\"submit\" class=ok>Submit</button>\
           </div>\
         </form>",
        id = id,
        field = field,
        notes = notes,
    )
}

/// Render a complete HTML page (title bar, body, fields, buttons)
/// suitable for printing or for embedding inside an iframe.
#[must_use]
pub fn render_full_html(req: &PendingRequest) -> String {
    let body = render_form_html(req);
    let title = html_escape(&req.spec.title);
    let question = html_escape(&req.spec.question);
    format!(
        "<!doctype html><meta charset=utf-8><title>{title}</title>\
         <style>{css}</style><body>\
         <main class=card>\
           <h1>{title}</h1><p class=q>{question}</p>\
           {body}\
         </main>",
        title = title,
        css = DEFAULT_CSS,
        question = question,
        body = body,
    )
}

const DEFAULT_CSS: &str = "body{margin:0;background:#0f172a;color:#f8fafc;font-family:system-ui,-apple-system,sans-serif}\
.card{max-width:640px;margin:2rem auto;background:#1e293b;padding:2rem;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.35)}\
h1{margin:0 0 .5rem;font-size:1.4rem}\
p.q{white-space:pre-wrap;color:#cbd5e1}\
label{display:block;margin:1rem 0 .25rem;font-weight:600}\
input[type=text],input[type=number],textarea,select{width:100%;padding:.65rem .75rem;border-radius:8px;background:#0f172a;color:#f8fafc;border:1px solid #334155;font-size:1rem}\
textarea{min-height:6rem}\
button{padding:.7rem 1.4rem;border-radius:8px;border:none;font-weight:600;cursor:pointer;margin-right:.5rem}\
.ok{background:#22c55e;color:#052e16}\
.cancel{background:#ef4444;color:#fff}\
.secret{background:#facc15;color:#1c1917}\
.actions{margin-top:1.5rem;text-align:right}";

fn field_to_html(field: &FieldSpec, request_id: &str) -> String {
    let label = field_label(field);
    let placeholder = field_placeholder(field).unwrap_or_default();
    match field {
        FieldSpec::Text { default, secret, max_length, .. } => {
            let kind = if *secret { "password" } else { "text" };
            let default = default.as_deref().unwrap_or_default();
            let max = max_length
                .map(|m| format!(" maxlength=\"{m}\""))
                .unwrap_or_default();
            format!(
                "<label for=field-{rid}>{label}</label>\
                 <input id=field-{rid} type=\"{kind}\" name=value value=\"{default}\" placeholder=\"{ph}\"{max} required>",
                rid = request_id,
                kind = kind,
                label = html_escape(&label),
                default = html_attr(default),
                ph = html_attr(&placeholder),
                max = max,
            )
        }
        FieldSpec::LongText { default, max_length, .. } => {
            let default = default.as_deref().unwrap_or_default();
            let max = max_length
                .map(|m| format!(" maxlength=\"{m}\""))
                .unwrap_or_default();
            format!(
                "<label for=field-{rid}>{label}</label>\
                 <textarea id=field-{rid} name=value placeholder=\"{ph}\"{max}>{default}</textarea>",
                rid = request_id,
                label = html_escape(&label),
                ph = html_attr(&placeholder),
                max = max,
                default = html_escape(default),
            )
        }
        FieldSpec::Choice {
            options, default_index, ..
        } => {
            let opts = options
                .iter()
                .enumerate()
                .map(|(i, o)| {
                    let selected = matches!(default_index, Some(idx) if *idx == i);
                    format!(
                        "<option value=\"{val}\"{sel}>{label}</option>",
                        val = html_attr(&o.value),
                        sel = if selected { " selected" } else { "" },
                        label = html_escape(&o.label),
                    )
                })
                .collect::<String>();
            format!(
                "<label for=field-{rid}>{label}</label>\
                 <select id=field-{rid} name=value>{opts}</select>",
                rid = request_id,
                label = html_escape(&label),
                opts = opts,
            )
        }
        FieldSpec::Boolean { default, .. } => {
            let checked = matches!(default, Some(true));
            format!(
                "<label class=bool><input type=checkbox name=boolean value=true{checked}> {label}</label>",
                checked = if checked { " checked" } else { "" },
                label = html_escape(&label),
            )
        }
        FieldSpec::Integer { default, min, max, .. } => {
            let default = default.map(|d| d.to_string()).unwrap_or_default();
            let range = match (min, max) {
                (Some(lo), Some(hi)) => format!(" min=\"{lo}\" max=\"{hi}\""),
                (Some(lo), None) => format!(" min=\"{lo}\""),
                (None, Some(hi)) => format!(" max=\"{hi}\""),
                _ => String::new(),
            };
            format!(
                "<label for=field-{rid}>{label}</label>\
                 <input id=field-{rid} type=number name=integer value=\"{default}\"{range}>",
                rid = request_id,
                label = html_escape(&label),
                default = html_attr(&default),
                range = range,
            )
        }
        FieldSpec::DateTime { default, .. } => {
            let default = default.as_deref().unwrap_or_default();
            format!(
                "<label for=field-{rid}>{label}</label>\
                 <input id=field-{rid} type=datetime-local name=value value=\"{default}\">",
                rid = request_id,
                label = html_escape(&label),
                default = html_attr(default),
            )
        }
    }
}

fn field_label(field: &FieldSpec) -> String {
    match field {
        FieldSpec::Text { label, .. }
        | FieldSpec::LongText { label, .. }
        | FieldSpec::Choice { label, .. }
        | FieldSpec::Boolean { label, .. }
        | FieldSpec::Integer { label, .. }
        | FieldSpec::DateTime { label, .. } => label.clone(),
    }
}

fn field_placeholder(field: &FieldSpec) -> Option<String> {
    match field {
        FieldSpec::Text { placeholder, .. } => placeholder.clone(),
        _ => None,
    }
}

fn notes_to_html(notes: &Option<crate::spec::NotesSpec>) -> String {
    let Some(n) = notes else { return String::new() };
    let default = n.default.as_deref().unwrap_or_default();
    let req = if n.required { " required" } else { "" };
    let max = n
        .max_length
        .map(|m| format!(" maxlength=\"{m}\""))
        .unwrap_or_default();
    format!(
        "<label for=notes>{label}</label>\
         <textarea id=notes name=notes{req}{max}>{default}</textarea>",
        label = html_escape(&n.label),
        req = req,
        max = max,
        default = html_escape(default),
    )
}

/// Sanitize a string for an HTML attribute value.
fn html_attr(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

/// Sanitize a string for HTML body content.
fn html_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
}

/// Plain-text rendering for `mailto:` and iMessage bodies.
#[must_use]
pub fn render_plain_text(req: &PendingRequest) -> String {
    use crate::inbox::notify::render_prompt_as_text;
    let body = render_prompt_as_text(&req.spec, &req.request_id);
    let answer_hint = match &req.spec.field {
        FieldSpec::Boolean { .. } => {
            "Reply with: elicitate answer --request-id <id> --value true|false".to_string()
        }
        FieldSpec::Integer { .. } => {
            "Reply with: elicitate answer --request-id <id> --integer <n>".to_string()
        }
        _ => format!(
            "Reply with: elicitate answer --request-id {} --value <your-answer>",
            req.request_id
        ),
    };
    format!("{body}\n{answer_hint}\n")
}

/// HTML page wrapping a single request that prints cleanly on letter / A4.
#[must_use]
pub fn render_printable_html(req: &PendingRequest) -> String {
    let body = render_form_html(req);
    let title = html_escape(&req.spec.title);
    let question = html_escape(&req.spec.question);
    format!(
        "<!doctype html><meta charset=utf-8>\
         <style>@media print {{ body {{ background:#fff;color:#000 }} .card {{ box-shadow:none;border:1px solid #999 }} }}</style>\
         <body><div class=card><h1>{title}</h1><p>{question}</p>{body}</div>",
        title = title,
        question = question,
        body = body,
    )
}

/// Render a one-line summary used by `elicitate inbox --list`.
#[must_use]
pub fn render_summary(req: &PendingRequest) -> String {
    let origin = format!("{}@{}", req.origin.process, req.origin.hostname);
    let value = match req.response.as_ref() {
        Some(ElicitResponse::Answered { value, .. }) => format_value(value),
        Some(ElicitResponse::Cancelled { .. }) => "cancelled".into(),
        Some(ElicitResponse::TimedOut { .. }) => "timed_out".into(),
        Some(ElicitResponse::Failed { .. }) => "failed".into(),
        None => "<pending>".into(),
    };
    format!(
        "{rid:30}  {title:50}  from={origin:24}  state={state:?}  value={value}",
        rid = req.request_id,
        title = truncate(&req.spec.title, 50),
        origin = truncate(&origin, 24),
        state = req.state,
        value = value,
    )
}

/// JSON-shaped summary for `elicitate inbox --list` (machine readable).
pub fn render_summary_json(req: &PendingRequest) -> serde_json::Value {
    serde_json::json!({
        "request_id": req.request_id,
        "title": req.spec.title,
        "state": format!("{:?}", req.state),
        "origin": {
            "process": req.origin.process,
            "hostname": req.origin.hostname,
            "pid": req.origin.pid,
        },
        "queued_at_ms": req.queued_at_ms,
        "expires_at_ms": req.expires_at_ms,
        "value": match req.response.as_ref() {
            Some(ElicitResponse::Answered { value, .. }) => {
                serde_json::to_value(value).ok()
            }
            Some(ElicitResponse::Cancelled { .. }) => {
                Some(serde_json::json!("cancelled"))
            }
            Some(ElicitResponse::TimedOut { .. }) => {
                Some(serde_json::json!("timed_out"))
            }
            Some(ElicitResponse::Failed { reason }) => {
                Some(serde_json::json!({"failed": reason}))
            }
            None => None,
        },
    })
}

fn format_value(v: &FieldValue) -> String {
    match v {
        FieldValue::Text(s) | FieldValue::LongText(s) | FieldValue::DateTime(s) => s.clone(),
        FieldValue::Integer(n) => n.to_string(),
        FieldValue::Boolean(b) => b.to_string(),
        FieldValue::Choice { value, .. } => value.clone(),
    }
}

fn truncate(s: &str, max: usize) -> String {
    if s.chars().count() <= max {
        return s.to_string();
    }
    let mut out: String = s.chars().take(max).collect();
    out.push('…');
    out
}

use crate::spec::ElicitResponse;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inbox::{PendingRequest, RequestOrigin, RequestState, unix_now_ms};
    use crate::spec::{NotesSpec, PromptSpec, Urgency};

    fn sample() -> PendingRequest {
        PendingRequest {
            request_id: "abc".into(),
            origin: RequestOrigin {
                hostname: "host".into(),
                process: "p".into(),
                pid: 1,
                callback: None,
            },
            spec: PromptSpec {
                title: "Approve deployment?".into(),
                question: "14 files changed. Proceed?".into(),
                field: FieldSpec::Boolean {
                    label: "Proceed?".into(),
                    default: Some(true),
                },
                notes: Some(NotesSpec {
                    label: "Notes".into(),
                    default: None,
                    max_length: None,
                    required: false,
                }),
                buttons: None,
                urgency: Urgency::Warning,
                timeout_secs: 60,
                request_id: Some("abc".into()),
            },
            queued_at_ms: unix_now_ms(),
            expires_at_ms: unix_now_ms() + 60_000,
            state: RequestState::Pending,
            response: None,
            notified_via: vec![],
            metadata: serde_json::Map::new(),
        }
    }

    #[test]
    fn form_html_contains_field_and_notes() {
        let html = render_form_html(&sample());
        assert!(html.contains("action=\"/answer/abc\""));
        assert!(html.contains("name=boolean"));
        assert!(html.contains("name=notes"));
    }

    #[test]
    fn full_html_is_complete_document() {
        let html = render_full_html(&sample());
        assert!(html.starts_with("<!doctype html>"));
        assert!(html.contains("<h1>Approve deployment?</h1>"));
    }

    #[test]
    fn plain_text_has_answer_hint() {
        let s = render_plain_text(&sample());
        assert!(s.contains("open: "));
        assert!(s.contains("true|false"));
    }

    #[test]
    fn summary_contains_id_and_title() {
        let s = render_summary(&sample());
        assert!(s.contains("abc"));
        assert!(s.contains("Approve deployment?"));
        assert!(s.contains("<pending>"));
    }

    #[test]
    fn summary_shows_answered_value() {
        let mut r = sample();
        r.response = Some(ElicitResponse::Answered {
            value: FieldValue::Boolean(true),
            notes: None,
        });
        r.state = RequestState::Answered;
        let s = render_summary(&r);
        assert!(s.contains("true"));
    }
}
