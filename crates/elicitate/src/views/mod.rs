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
    let mut rows = String::with_capacity(count * 128);
    for req in requests {
        let urg = match req.spec.urgency {
            crate::spec::Urgency::Warning => " warn",
            crate::spec::Urgency::Error => " urgent",
            _ => "",
        };
        rows.push_str(&format!(
            "<a href=/inbox/{rid} class=card{urg}><div class=row>\
             <div class=row-main><strong>{title}</strong>\
             <span class=ago>{ago}</span></div>\
             <div class=row-sub><span>{question}</span>\
             <span>{field_kind}</span></div></div></a>",
            rid = html_attr(&req.request_id),
            urg = urg,
            title = html_escape(req.spec.title.as_str()),
            ago = format_age(unix_now_ms_diff(req.queued_at_ms)),
            question = truncate(&html_escape(&req.spec.question), 80),
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

/// Render a form detail page for one pending request.
#[must_use]
pub fn render_form_html(req: &PendingRequest) -> String {
    let field_kind = field_kind_label(&req.spec.field);
    let urgency_badge = match req.spec.urgency {
        crate::spec::Urgency::Warning => " warn",
        crate::spec::Urgency::Error => " urgent",
        _ => "",
    };
    let ago = format_age(unix_now_ms_diff(req.queued_at_ms));
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
         <p>{notes}</p>\
         <pre>{spec_preview}</pre>\
         <a href=/inbox/{rid}/answer class=ok>Answer this request</a></main>\
         </body></html>",
        title = html_escape(req.spec.title.as_str()),
        css = full_html_css(),
        nav = NAV_HTML,
        urg = urgency_badge,
        rid = html_attr(&req.request_id),
        ago = ago,
        field_kind = field_kind,
        question = html_escape(&req.spec.question),
        notes = req.spec.notes.as_ref().map(|n| html_escape(&n.label)).unwrap_or_default(),
        spec_preview = html_escape(&serde_json::to_string_pretty(&req.spec).unwrap_or_default()),
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

// ---- helpers ----

fn field_kind_label(field: &FieldSpec) -> &'static str {
    match field {
        FieldSpec::Text { .. } => "Text",
        FieldSpec::LongText { .. } => "Long text",
        FieldSpec::Integer { .. } => "Integer",
        FieldSpec::Choice { .. } => "Choice",
        FieldSpec::Boolean { .. } => "Yes/No",
        FieldSpec::DateTime { .. } => "Date/time",
    }
}

fn unix_now_ms_diff(queued: u64) -> u64 {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_millis() as u64);
    now.saturating_sub(queued)
}

fn format_age(ms: u64) -> String {
    let secs = ms / 1000;
    if secs < 60 {
        format!("{}s", secs)
    } else if secs < 3600 {
        format!("{}m", secs / 60)
    } else if secs < 86400 {
        format!("{}h", secs / 3600)
    } else {
        format!("{}d", secs / 86400)
    }
}

fn truncate(s: &str, max: usize) -> String {
    if s.len() <= max {
        s.to_string()
    } else {
        format!("{}…", &s[..max.saturating_sub(1)])
    }
}

/// Alias for backwards compatibility — use [`full_html_css`] instead.
#[must_use]
pub fn render_inbox_css() -> &'static str {
    full_html_css()
}

/// Alias for backwards compatibility.
#[must_use]
pub fn render_printable_html(title: &str, content: &str) -> String {
    render_full_html(title, content)
}

// ---- snapshot tests ----

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inbox::PendingRequest;
    use crate::spec::{NotesSpec, ButtonSpec, PromptSpec, Urgency};

    fn sample_pending(id: &str, urgent: Urgency) -> PendingRequest {
        PendingRequest {
            request_id: id.into(),
            queued_at_ms: 1700000000000,
            expires_at_ms: 1700086400000,
            origin: crate::inbox::RequestOrigin {
                hostname: "test.local".into(),
                process: "elicitate".into(),
                pid: 42,
                callback: None,
            },
            spec: PromptSpec {
                title: "What is your favorite color?".into(),
                field: FieldSpec::Text {
                    label: "Color".into(),
                    secret: false,
                },
                description: Some("Please answer honestly.".into()),
                notes: Some(crate::spec::NotesSpec {
                    label: "Work notes".into(),
                    default: Some("Use blue.".into()),
                    max_length: Some(500),
                    required: true,
                }),
                buttons: Some(crate::spec::ButtonSpec {
                    cancel: "Skip".into(),
                    confirm: "Next".into(),
                    default_is_cancel: false,
                }),
                urgency: urgent,
                ..Default::default()
            },
            ..Default::default()
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
            "Test Request",
            "What is your favorite color?",
            "Text",
        ]));
        assert!(html.contains("2m ago") || html.contains("120s ago"));
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
        assert!(html.contains("Return to inbox"));
        assert!(html.contains("What is your favorite color?"));
        assert!(html.contains("Please answer honestly."));
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
}
