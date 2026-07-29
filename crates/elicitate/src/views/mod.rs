use crate::inbox::PendingRequest;
use crate::spec::FieldSpec;

pub const INBOX_SLUG: &str = "elicitate inbox";
const NAV_HTML: &str = "<p class=nav><a href=/inbox>&larr; Inbox</a></p>";

/// Escape text for safe HTML body content.
#[must_use]
pub fn html_escape(raw: &str) -> String {
    raw.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

/// Escape text for safe HTML attribute content.
#[must_use]
pub fn html_attr(raw: &str) -> String {
    raw.replace('&', "&amp;")
        .replace('"', "&quot;")
        .replace('<', "&lt;")
}

/// Compiled, minified CSS for the inbox web frontend.
#[must_use]
pub fn full_html_css() -> &'static str {
    concat!(
        "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}",
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:#f5f5f7;color:#1d1d1f;line-height:1.5;padding:1rem;max-width:720px;margin:0 auto}",
        "a{color:#0066cc;text-decoration:none;font-weight:500}",
        "a:hover{text-decoration:underline}",
        "header{display:flex;align-items:baseline;gap:.75rem;margin-bottom:1.5rem;padding-bottom:.75rem;border-bottom:1px solid #d2d2d7}",
        "header h1{font-size:1.5rem;font-weight:600}",
        ".badge{display:inline-block;background:#0066cc;color:#fff;font-size:.75rem;font-weight:600;padding:.125rem .5rem;border-radius:99px;line-height:1.4}",
        ".card{display:block;background:#fff;border-radius:10px;padding:.75rem 1rem;margin-bottom:.5rem;border:1px solid #e5e5ea;transition:box-shadow .15s}",
        ".card:hover{box-shadow:0 2px 8px rgba(0,0,0,.08)}",
        ".row{display:flex;flex-direction:column;gap:.25rem}",
        ".row-main{display:flex;justify-content:space-between;align-items:baseline;gap:.5rem}",
        ".row-main strong{font-size:1rem;font-weight:600}",
        ".row-main .ago{font-size:.8125rem;color:#86868b;white-space:nowrap}",
        ".row-sub{display:flex;justify-content:space-between;font-size:.8125rem;color:#6e6e73;gap:.5rem}",
        ".warn{border-left:4px solid #ff9f0a;padding-left:calc(1rem - 4px)}",
        ".urgent{border-left:4px solid #ff453a;padding-left:calc(1rem - 4px)}",
        "footer{margin-top:2rem;font-size:.8125rem;color:#86868b;text-align:center}",
        ".empty{text-align:center;padding:3rem 1rem;color:#86868b}",
        ".empty p{font-size:1.125rem;margin-bottom:.5rem}",
        "main.card{background:#fff;border-radius:10px;padding:1.5rem;border:1px solid #e5e5ea}",
        "main.card h2{font-size:1.25rem;font-weight:600;margin-bottom:.5rem}",
        "main.card p{color:#515154;margin-bottom:1rem;line-height:1.6}",
        "main.card .ok{display:inline-block;margin-top:.5rem;font-weight:500}",
        "pre{background:#f0f0f2;padding:.75rem;border-radius:8px;overflow-x:auto;font-size:.8125rem;margin:.5rem 0}",
        "@media(prefers-color-scheme:dark){body{background:#1c1c1e;color:#f5f5f7}a{color:#409cff}.card,.card.main{background:#2c2c2e;border-color:#38383a}.badge{background:#409cff}.row-sub,.ago,.empty,.footer{color:#98989d}header{border-color:#38383a}pre{background:#2c2c2e}}",
        "@media(max-width:480px){body{padding:.5rem}header h1{font-size:1.25rem}.card{padding:.5rem .75rem}}",
    )
}

/// Render an age string (e.g. "5s", "12m", "3h", "2d") from a duration in ms.
#[must_use]
pub fn format_age(ms: u64) -> String {
    let secs = ms / 1000;
    if secs < 60 {
        format!("{secs}s")
    } else if secs < 3_600 {
        format!("{}m", secs / 60)
    } else if secs < 86_400 {
        format!("{}h", secs / 3_600)
    } else {
        format!("{}d", secs / 86_400)
    }
}

/// Difference between `now_ms` and `past_ms`, clamped to 0.
#[must_use]
pub fn unix_now_ms_diff(past_ms: u64) -> u64 {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_millis() as u64);
    now.saturating_sub(past_ms)
}

/// Truncate a string to `max_chars`, appending an ellipsis if cut.
#[must_use]
pub fn truncate(s: &str, max_chars: usize) -> String {
    if s.chars().count() <= max_chars {
        return s.to_string();
    }
    let mut out: String = s.chars().take(max_chars.saturating_sub(1)).collect();
    out.push('…');
    out
}

/// Map `Urgency` to its CSS class for card styling.
#[must_use]
pub fn urgency_class(u: crate::spec::Urgency) -> &'static str {
    use crate::spec::Urgency::*;
    match u {
        Info => "info",
        Warning => "warn",
        Error => "urgent",
        Secret => "info",
    }
}

/// Map `Urgency` to a short human label.
#[must_use]
pub fn urgency_label(u: crate::spec::Urgency) -> &'static str {
    use crate::spec::Urgency::*;
    match u {
        Info => "Info",
        Warning => "Warning",
        Error => "Error",
        Secret => "Secret",
    }
}

/// Map `FieldSpec` to a short kind label (e.g. "text", "yes / no").
#[must_use]
pub fn field_kind_label(f: &FieldSpec) -> &'static str {
    match f {
        FieldSpec::Text { .. } => "text",
        FieldSpec::LongText { .. } => "long text",
        FieldSpec::Integer { .. } => "integer",
        FieldSpec::Choice { .. } => "choice",
        FieldSpec::Boolean { .. } => "yes / no",
        FieldSpec::DateTime { .. } => "date",
    }
}

// ---- inbox index page ----

/// Render a browsable inbox index page listing pending requests.
#[must_use]
pub fn render_inbox_index_html(requests: &[PendingRequest]) -> String {
    let count = requests.len();
    if count == 0 {
        return format!(
            "<!doctype html><html lang=en>\
             <meta charset=utf-8>\
             <meta name=viewport content='width=device-width,initial-scale=1'>\
             <title>{title}</title>\
             <style>{css}</style>\
             <body>\
             <header><h1>{title}</h1></header>\
             <main class=empty><p>No pending requests</p>\
             <p>Use <code>elicitate ask</code> from your agent.</p></main>\
             <footer><p>elicitate</p></footer>\
             </body></html>",
            title = INBOX_SLUG,
            css = full_html_css(),
        );
    }
    let mut rows = String::with_capacity(count * 160);
    for req in requests {
        let urg = urgency_class(req.spec.urgency);
        let urgency_label = urgency_label(req.spec.urgency);
        rows.push_str(&format!(
            "<a href=/inbox/{rid} class=card {urg}><div class=row>\
             <div class=row-main><strong>{title}</strong>\
             <span class=ago>{ago}</span></div>\
             <div class=row-sub><span>{question}</span>\
             <span class=badge>{urgency_label}</span>\
             <span>{field_kind}</span></div></div></a>",
            rid = html_attr(&req.request_id),
            urg = urg,
            title = html_escape(req.spec.title.as_str()),
            ago = format_age(unix_now_ms_diff(req.queued_at_ms)),
            question = truncate(&html_escape(&req.spec.question), 80),
            urgency_label = urgency_label,
            field_kind = field_kind_label(&req.spec.field),
        ));
    }
    format!(
        "<!doctype html><html lang=en>\
         <meta charset=utf-8>\
         <meta name=viewport content='width=device-width,initial-scale=1'>\
         <title>{title}</title>\
         <style>{css}</style>\
         <body>\
         <header><h1>{title}</h1><span class=badge>{count}</span></header>\
         <main>{rows}</main>\
         <footer><p>elicitate</p></footer>\
         </body></html>",
        title = INBOX_SLUG,
        css = full_html_css(),
        count = count,
        rows = rows,
    )
}

// ---- form detail page ----

/// Render the form-widget HTML for a single [`FieldSpec`] variant.
///
/// Each variant emits the appropriate HTML input element:
/// - `Text` → `<input type=text|name=value …>`
/// - `LongText` → `<textarea name=value …>`
/// - `Integer` → `<input type=number name=integer …>`
/// - `Choice` → `<select name=value><option …>…</option></select>`
/// - `Boolean` → `<input type=checkbox name=boolean value=on …>`
/// - `DateTime` → `<input type=date|time|datetime-local name=value …>`
///
/// All user-controlled values (label, placeholder, default, choice labels)
/// pass through [`html_attr`] / [`html_escape`] before insertion.
#[must_use]
pub fn render_field_widget(field: &FieldSpec) -> String {
    match field {
        FieldSpec::Text {
            label,
            default,
            placeholder,
            max_length,
            secret,
            ..
        } => {
            let label_html = html_escape(label);
            let placeholder_html = placeholder
                .as_deref()
                .map(|p| format!(r#" placeholder="{}""#, html_attr(p)))
                .unwrap_or_default();
            let default_html = default
                .as_deref()
                .map(|d| format!(r#" value="{}""#, html_attr(d)))
                .unwrap_or_default();
            let max_len_html = max_length
                .map(|m| format!(r#" maxlength="{}""#, m))
                .unwrap_or_default();
            let input_type = if *secret { "password" } else { "text" };
            format!(
                r"<label for=eli-field>{label}</label>\
                   <input id=eli-field type={input_type} name=value{placeholder}{default}{max_len} required>",
                label = label_html,
                input_type = input_type,
                placeholder = placeholder_html,
                default = default_html,
                max_len = max_len_html,
            )
        }
        FieldSpec::LongText {
            label,
            default,
            max_length,
        } => {
            let label_html = html_escape(label);
            let default_html = default
                .as_deref()
                .map(|d| html_escape(d))
                .unwrap_or_default();
            let max_len_html = max_length
                .map(|m| format!(r#" maxlength="{}""#, m))
                .unwrap_or_default();
            format!(
                r"<label for=eli-field>{label}</label>\
                   <textarea id=eli-field name=value{rows}{max_len}>{default}</textarea>",
                label = label_html,
                rows = r#" rows="4""#,
                max_len = max_len_html,
                default = default_html,
            )
        }
        FieldSpec::Integer {
            label,
            min,
            max,
            default,
        } => {
            let label_html = html_escape(label);
            let min_html = min.map(|m| format!(r#" min="{}""#, m)).unwrap_or_default();
            let max_html = max.map(|m| format!(r#" max="{}""#, m)).unwrap_or_default();
            let default_html = default
                .map(|d| format!(r#" value="{}""#, d))
                .unwrap_or_default();
            format!(
                r"<label for=eli-field>{label}</label>\
                   <input id=eli-field type=number name=integer{min}{max}{default} required>",
                label = label_html,
                min = min_html,
                max = max_html,
                default = default_html,
            )
        }
        FieldSpec::Choice {
            label,
            options,
            default_index,
        } => {
            let label_html = html_escape(label);
            let mut opts = String::with_capacity(options.len() * 64);
            for (i, opt) in options.iter().enumerate() {
                let value = html_attr(&opt.value);
                let label_text = html_escape(&opt.label);
                let selected = default_index
                    .map(|d| d == i)
                    .unwrap_or(false);
                let sel_attr = if selected { " selected" } else { "" };
                opts.push_str(&format!(
                    r#"<option value="{value}"{sel}>{label}</option>"#,
                    value = value,
                    sel = sel_attr,
                    label = label_text,
                ));
            }
            format!(
                r"<label for=eli-field>{label}</label>\
                   <select id=eli-field name=value required>{opts}</select>",
                label = label_html,
                opts = opts,
            )
        }
        FieldSpec::Boolean { label, default } => {
            let label_html = html_escape(label);
            let checked = default.unwrap_or(false);
            let checked_attr = if checked { " checked" } else { "" };
            format!(
                r"<label class=bool><input type=checkbox name=boolean value=on{checked}> \
                   <span>{label}</span></label>",
                checked = checked_attr,
                label = label_html,
            )
        }
        FieldSpec::DateTime {
            label,
            default,
            picker_kind,
        } => {
            use crate::spec::DateTimeKind;
            let input_type = match picker_kind {
                DateTimeKind::Date => "date",
                DateTimeKind::Time => "time",
                DateTimeKind::DateTime => "datetime-local",
            };
            let label_html = html_escape(label);
            let default_html = default
                .as_deref()
                .map(|d| format!(r#" value="{}""#, html_attr(d)))
                .unwrap_or_default();
            format!(
                r"<label for=eli-field>{label}</label>\
                   <input id=eli-field type={input_type} name=value{default} required>",
                label = label_html,
                input_type = input_type,
                default = default_html,
            )
        }
    }
}

/// Render a form detail page for one pending request.
///
/// The page emits a real `<form method=POST action=/inbox/{rid}/answer>`
/// with input/textarea/select/checkbox widgets per the [`FieldSpec`]
/// variant. Submitting POSTs the form back to the daemon's
/// `Route::Answer`, which validates, writes the JSON response file, and
/// redirects to `/inbox/{rid}/done`.
#[must_use]
pub fn render_form_html(req: &PendingRequest) -> String {
    let field_kind = field_kind_label(&req.spec.field);
    let urgency_badge = match req.spec.urgency {
        crate::spec::Urgency::Warning => " warn",
        crate::spec::Urgency::Error => " urgent",
        _ => "",
    };
    let ago = format_age(unix_now_ms_diff(req.queued_at_ms));
    let widget = render_field_widget(&req.spec.field);
    let notes_box = req
        .spec
        .notes
        .as_ref()
        .map(|n| {
            let req_attr = if n.required { " required" } else { "" };
            let max_len = n
                .max_length
                .map(|m| format!(r#" maxlength="{}""#, m))
                .unwrap_or_default();
            format!(
                r#"<label for=eli-notes>{nl}</label>\
                   <textarea id=eli-notes name=notes{req}{max_len}>{default}</textarea>"#,
                nl = html_escape(&n.label),
                req = req_attr,
                max_len = max_len,
                default = html_escape(n.default.as_deref().unwrap_or("")),
            )
        })
        .unwrap_or_default();
    format!(
        "<!doctype html><html lang=en>\
         <meta charset=utf-8>\
         <meta name=viewport content='width=device-width,initial-scale=1'>\
         <title>{title}</title>\
         <style>{css}</style>\
         <body>\
         {nav}\
         <div class=card{urg}><div class=row>\
         <div class=row-main><strong>{title}</strong>\
         <span class=ago>{ago}</span></div>\
         <div class=row-sub><span>{field_kind}</span></div></div></div>\
         <main class=card><h2>{question}</h2>\
         {widget}\
         {notes_box}\
         <form method=POST action=/inbox/{rid}/answer class=actions>\
         <button type=submit name=confirm value=ok class=ok>Submit</button>\
         <button type=submit name=cancel value=1 class=cancel>Cancel</button>\
         </form>\
         </main>\
         </body></html>",
        title = html_escape(req.spec.title.as_str()),
        css = full_html_css(),
        nav = NAV_HTML,
        urg = urgency_badge,
        rid = html_attr(&req.request_id),
        ago = ago,
        field_kind = field_kind,
        question = html_escape(&req.spec.question),
        widget = widget,
        notes_box = notes_box,
    )
}

// ---- answer confirmation page ----

/// Render a confirmation page after answering a request.
#[must_use]
pub fn render_answer_html(_request_id: &str, success: bool, message: &str) -> String {
    let icon = if success { "\u{2705}" } else { "\u{274C}" };
    let heading = if success {
        "Answer received"
    } else {
        "Failed to record answer"
    };
    format!(
        "<!doctype html><html lang=en>\
         <meta charset=utf-8>\
         <meta name=viewport content='width=device-width,initial-scale=1'>\
         <title>{icon} {heading}</title>\
         <style>{css}</style>\
         <body>\
         {nav}\
         <main class=card><h2>{icon} {heading}</h2>\
         <p>{message}</p>\
         <a href=/inbox class=ok>Return to inbox</a></main>\
         </body></html>",
        icon = icon,
        heading = heading,
        css = full_html_css(),
        nav = NAV_HTML,
        message = html_escape(message),
    )
}

// ---- generic helpers ----

/// Render a full-page HTML document around content.
#[must_use]
pub fn render_full_html(title: &str, content: &str) -> String {
    format!(
        "<!doctype html><html lang=en>\
         <meta charset=utf-8>\
         <meta name=viewport content='width=device-width,initial-scale=1'>\
         <title>{title}</title>\
         <style>{css}</style>\
         <body>{content}</body></html>",
        title = html_escape(title),
        css = full_html_css(),
        content = content,
    )
}

/// Render plain-text summary of a pending request.
#[must_use]
pub fn render_plain_text(req: &PendingRequest) -> String {
    let field_kind = field_kind_label(&req.spec.field);
    format!(
        "[{kind}] {title}: {question}",
        kind = field_kind,
        title = req.spec.title.as_str(),
        question = &req.spec.question,
    )
}

/// Render a one-line summary string for a pending request.
#[must_use]
pub fn render_summary(req: &PendingRequest) -> String {
    format!(
        "{} — {} ({})",
        &req.spec.title,
        req.spec.question,
        field_kind_label(&req.spec.field),
    )
}

/// Render a JSON summary for a pending request.
#[must_use]
pub fn render_summary_json(req: &PendingRequest) -> serde_json::Value {
    let field_kind = match &req.spec.field {
        FieldSpec::Text { .. } => "text",
        FieldSpec::LongText { .. } => "long_text",
        FieldSpec::Integer { .. } => "integer",
        FieldSpec::Choice { .. } => "choice",
        FieldSpec::Boolean { .. } => "boolean",
        FieldSpec::DateTime { .. } => "date_time",
    };
    serde_json::json!({
        "request_id": req.request_id,
        "title": &req.spec.title,
        "question": req.spec.question,
        "field_kind": field_kind,
        "queued_at_ms": req.queued_at_ms,
    })
}

// ---- end of file ----

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inbox::{PendingRequest, RequestOrigin};
    use crate::spec::{ButtonSpec, FieldSpec, NotesSpec, PromptSpec, Urgency};

    fn sample_pending(id: &str, urgent: Urgency) -> PendingRequest {
        PendingRequest {
            request_id: id.into(),
            queued_at_ms: 1_700_000_000_000,
            expires_at_ms: 1_700_000_060_000,
            origin: crate::inbox::RequestOrigin {
                hostname: "test-host".into(),
                process: "elicitate-test".into(),
                pid: 12345,
                callback: None,
            },
            spec: PromptSpec {
                title: "What is your favorite color?".into(),
                question: "Please answer honestly.".into(),
                field: crate::spec::FieldSpec::Text {
                    label: "Color".into(),
                    placeholder: None,
                    default: None,
                    secret: false,
                    pattern: None,
                    max_length: None,
                },
                notes: None,
                buttons: None,
                urgency: urgent,
                timeout_secs: 60,
                request_id: Some(id.into()),
            },
            response: None,
            state: crate::inbox::RequestState::Pending,
            notified_via: vec![],
            metadata: Default::default(),
        }
    }

    fn snapshot_contains(haystack: &str, needles: &[&str]) -> bool {
        needles.iter().all(|n| haystack.contains(n))
    }

    #[test]
    fn index_empty() {
        let html = render_inbox_index_html(&[]);
        assert!(snapshot_contains(&html, &[
            "No pending requests",
            "elicitate",
        ]));
        assert!(html.contains("</html>"));
    }

    #[test]
    fn index_with_pending() {
        let reqs = vec![sample_pending("r1", Urgency::Info)];
        let html = render_inbox_index_html(&reqs);
        assert!(snapshot_contains(&html, &[
            "r1",
            "What is your favorite color?",
            "Info",
        ]));
        assert!(html.contains("</html>"));
    }

    #[test]
    fn index_multiple_requests() {
        let reqs = vec![
            sample_pending("a", Urgency::Info),
            sample_pending("b", Urgency::Warning),
            sample_pending("c", Urgency::Error),
        ];
        let html = render_inbox_index_html(&reqs);
        assert!(html.matches("<a href=").count() >= 3);
        assert!(html.contains("class=card warn"));
        assert!(html.contains("urgent"));
    }

    #[test]
    fn form_detail_has_nav() {
        let req = sample_pending("det1", Urgency::Info);
        let html = render_form_html(&req);
        // nav emits: &larr; Inbox (HTML entity for ←)
        assert!(html.contains("&larr;"));
        assert!(html.contains("href=/inbox"));
        // sample_pending() sets title="What is your favorite color?"
        assert!(html.contains("What is your favorite color?"));
    }

    #[test]
    fn answer_success() {
        let html = render_answer_html("r99", true, "Your answer was recorded.");
        assert!(html.contains("Answer received"));
        assert!(html.contains("Your answer was recorded."));
        assert!(html.contains("Return to inbox"));
    }

    #[test]
    fn answer_failure() {
        let html = render_answer_html("r99", false, "Invalid value.");
        assert!(html.contains("Failed to record answer"));
        assert!(html.contains("\u{274C}"));
    }

    #[test]
    fn css_dark_mode_prefers() {
        let css = full_html_css();
        assert!(css.contains("prefers-color-scheme:dark"));
        assert!(css.contains("background:#1c1c1e"));
        assert!(css.contains("color:#f5f5f7"));
    }

    #[test]
    fn css_responsive() {
        let css = full_html_css();
        assert!(css.contains("max-width:720px"));
        assert!(css.contains("max-width:480px"));
    }

    // ---- v0.7.0: submit-form-from-browser ----

    /// The form page must emit a real `<form method=POST>` whose action
    /// points at the daemon's answer route. This is the v0.7.0 contract:
    /// the user fills the widget, presses Submit, and the browser POSTs
    /// the body to the daemon (which parses + validates + writes the
    /// response file).
    #[test]
    fn form_emits_post_action() {
        let req = sample_pending("rid-form-post", Urgency::Info);
        let html = render_form_html(&req);
        assert!(
            html.contains(r#"<form method=POST action=/inbox/rid-form-post/answer"#),
            "form must post to /inbox/{{rid}}/answer, got: {html}"
        );
        assert!(html.contains(r#"name=confirm value=ok"#));
        assert!(html.contains(r#"name=cancel value=1"#));
    }

    /// `FieldSpec::Text` renders as a single-line `<input type=text>`
    /// named `value`. Placeholders, max-length, and `secret=true` (which
    /// flips the input type to `password`) are all encoded in attributes.
    #[test]
    fn text_field_renders_input() {
        let mut req = sample_pending("rid-text", Urgency::Info);
        req.spec.field = FieldSpec::Text {
            label: "Color".into(),
            placeholder: Some("e.g. blue".into()),
            default: Some("blue".into()),
            max_length: Some(64),
            secret: false,
            pattern: None,
        };
        let html = render_form_html(&req);
        assert!(
            html.contains(r#"<input id=eli-field type=text name=value"#),
            "Text must emit <input type=text name=value …>: {html}"
        );
        assert!(html.contains(r#"placeholder="e.g. blue""#));
        assert!(html.contains(r#"value="blue""#));
        assert!(html.contains(r#"maxlength="64""#));
        // Secret flips the input type to password.
        req.spec.field = FieldSpec::Text {
            label: "PIN".into(),
            placeholder: None,
            default: None,
            max_length: None,
            secret: true,
            pattern: None,
        };
        let html_secret = render_form_html(&req);
        assert!(
            html_secret.contains(r#"type=password"#),
            "secret=true must emit type=password: {html_secret}"
        );
    }

    /// `FieldSpec::Choice` renders as a `<select name=value>` containing
    /// one `<option value="…">label</option>` per `ChoiceOption`. The
    /// `default_index` selects the right option via the `selected` attr.
    #[test]
    fn choice_field_renders_select() {
        let mut req = sample_pending("rid-choice", Urgency::Info);
        req.spec.field = FieldSpec::Choice {
            label: "Environment".into(),
            options: vec![
                crate::spec::ChoiceOption {
                    value: "staging".into(),
                    label: "Staging".into(),
                    description: None,
                },
                crate::spec::ChoiceOption {
                    value: "prod".into(),
                    label: "Production".into(),
                    description: None,
                },
            ],
            default_index: Some(1),
        };
        let html = render_form_html(&req);
        assert!(
            html.contains(r#"<select id=eli-field name=value required>"#),
            "Choice must emit <select name=value>: {html}"
        );
        assert!(html.contains(r#"<option value="staging""#));
        assert!(html.contains(r#"<option value="prod" selected"#));
        assert!(html.contains(r#"<option value="staging">Staging</option>"#));
        assert!(html.contains(r#"<option value="prod" selected>Production</option>"#));
    }

    /// `FieldSpec::Boolean` renders as `<input type=checkbox name=boolean
    /// value=on>`. The label is the visible label text. `default=true`
    /// adds `checked`.
    #[test]
    fn boolean_field_renders_checkbox() {
        let mut req = sample_pending("rid-bool", Urgency::Info);
        req.spec.field = FieldSpec::Boolean {
            label: "Proceed?".into(),
            default: Some(true),
        };
        let html = render_form_html(&req);
        assert!(
            html.contains(r#"<input type=checkbox name=boolean value=on checked>"#),
            "Boolean default=true must emit checked: {html}"
        );
        assert!(html.contains("Proceed?"));
        // Now flip default=false and re-check.
        req.spec.field = FieldSpec::Boolean {
            label: "Proceed?".into(),
            default: Some(false),
        };
        let html_false = render_form_html(&req);
        assert!(
            html_false.contains(r#"<input type=checkbox name=boolean value=on>"#),
            "Boolean default=false must not be checked: {html_false}"
        );
        assert!(!html_false.contains("checked"));
    }
}
