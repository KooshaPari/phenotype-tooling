//! macOS popup renderer via `osascript`'s `display dialog` command.
//!
//! AppleScript's `display dialog` is a thin wrapper over AppKit's NSAlert,
//! which is the canonical modal native popup on macOS. We shell out to
//! `osascript` rather than linking AppKit because:
//!
//! 1. `osascript` is a system component on every macOS install (since OS 8).
//! 2. Linking AppKit requires Xcode SDK + a Cocoa build script.
//! 3. The popup is rendered out-of-process, so the MCP server is never
//!    blocked on the AppKit main thread.
//!
//! Wire format: we emit a single `display dialog` call with custom
//! properties (title, default answer, icon, timeout). The user-entered
//! text and button name are returned on stdout as
//! `STATUS|BUTTON|TEXT|NOTES` for easy parsing.

use std::os::unix::process::CommandExt;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

use crate::error::ElicitError;
use crate::escape::applescript_escape;
use crate::options::ElicitOptions;
use crate::spec::{
    DateTimeKind, ElicitResponse, FieldSpec, FieldValue, PromptSpec, Urgency,
};

/// Render the popup on macOS.
pub fn render(spec: &PromptSpec, opts: &ElicitOptions) -> Result<ElicitResponse, ElicitError> {
    spec.validate().map_err(ElicitError::InvalidSpec)?;

    let script = build_script(spec)?;
    let timeout = opts.timeout.unwrap_or(Duration::from_secs(spec.timeout_secs as u64));

    let start = Instant::now();
    let mut child = Command::new("osascript")
        .arg("-e")
        .arg(&script)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .process_group(0) // detach so SIGTERM to MCP server doesn't kill popup
        .spawn()
        .map_err(|e| ElicitError::RendererFailed(format!("spawn osascript: {e}")))?;

    // Wait with timeout
    let output = loop {
        match child.try_wait() {
            Ok(Some(_status)) => {
                // Reap and collect stdout/stderr
                let out = child
                    .wait_with_output()
                    .map_err(ElicitError::Io)?;
                break out;
            }
            Ok(None) => {
                if start.elapsed() >= timeout {
                    let _ = child.kill();
                    let _ = child.wait();
                    return Ok(ElicitResponse::TimedOut {
                        elapsed_secs: start.elapsed().as_secs_f64(),
                    });
                }
                std::thread::sleep(Duration::from_millis(100));
            }
            Err(e) => return Err(ElicitError::Io(e)),
        }
    };

    parse_output(&output.stdout, &output.stderr, start.elapsed())
}

/// Build the AppleScript source.
fn build_script(spec: &PromptSpec) -> Result<String, ElicitError> {
    // Compose the body string (question + default + placeholder context).
    let body = applescript_escape(&spec.question)?;

    // Title (escape any embedded " or \).
    let title = applescript_escape(&format!("elicitate · {}", spec.title))?;

    // Default answer (for text fields) or empty (for other kinds).
    let default = match &spec.field {
        FieldSpec::Text { default, .. } => default.clone().unwrap_or_default(),
        FieldSpec::LongText { default, .. } => default.clone().unwrap_or_default(),
        FieldSpec::Integer { default, .. } => default.map(|v| v.to_string()).unwrap_or_default(),
        _ => String::new(),
    };
    let default_arg = if default.is_empty() {
        String::new()
    } else {
        format!(" default answer {}", applescript_escape(&default)?)
    };

    // Icon hint
    let icon = match spec.urgency {
        Urgency::Info => "note",
        Urgency::Warning => "caution",
        Urgency::Error => "stop",
        Urgency::Secret => "caution",
    };

    // Buttons
    let (cancel_label, confirm_label) = spec
        .buttons
        .as_ref()
        .map(|b| (b.cancel.clone(), b.confirm.clone()))
        .unwrap_or_else(|| ("Cancel".to_string(), "OK".to_string()));

    // Timeout: 0 means no timeout in AppleScript.
    let timeout_clause = if spec.timeout_secs == 0 {
        String::new()
    } else {
        format!(" giving up after {}", spec.timeout_secs)
    };

    // We use a single `display dialog` with `with hidden answer` for secret
    // fields; otherwise the default behavior echoes.
    let hidden_clause = match &spec.field {
        FieldSpec::Text { secret: true, .. } => " with hidden answer",
        _ => "",
    };

    // The script returns: STATUS|BUTTON|TEXT|NOTES
    // STATUS: "answered" | "cancelled" | "timed_out"
    // We populate this in a follow-up `if` block after the dialog.
    let script = format!(
        r#"
try
    set theResponse to display dialog {body} with title {title}{default_arg} with icon {icon}{hidden_clause} buttons {{{cancel_q}, {confirm_q}}} default button {default_btn}{timeout_clause}
    set theButton to button returned of theResponse
    set theText to text returned of theResponse
    if theButton is {confirm_q} then
        return "answered|" & theButton & "|" & theText & "|"
    else
        return "cancelled|" & theButton & "|" & theText & "|"
    end if
on error errMsg number errNum
    -- errNum -128 = user cancelled (Cmd+.)
    if errNum is -128 then
        return "cancelled|Cancel|||"
    else
        return "failed|Error|" & errMsg & "|"
    end if
end try
"#,
        body = body,
        title = title,
        default_arg = default_arg,
        icon = icon,
        hidden_clause = hidden_clause,
        cancel_q = applescript_escape(&cancel_label)?,
        confirm_q = applescript_escape(&confirm_label)?,
        default_btn = if spec
            .buttons
            .as_ref()
            .is_some_and(|b| b.default_is_cancel)
        {
            applescript_escape(&cancel_label)?
        } else {
            applescript_escape(&confirm_label)?
        },
        timeout_clause = timeout_clause,
    );

    Ok(script)
}

/// Parse `osascript`'s stdout/stderr into an [`ElicitResponse`].
fn parse_output(
    stdout: &[u8],
    stderr: &[u8],
    elapsed: Duration,
) -> Result<ElicitResponse, ElicitError> {
    let text = std::str::from_utf8(stdout)
        .map_err(|e| ElicitError::RendererFailed(format!("non-utf8 stdout: {e}")))?
        .trim();

    if text.is_empty() {
        let err = std::str::from_utf8(stderr).unwrap_or("(non-utf8 stderr)");
        return Ok(ElicitResponse::Failed {
            reason: format!("osascript produced no stdout; stderr: {err}"),
        });
    }

    // Format: STATUS|BUTTON|TEXT|NOTES (NOTES may be empty)
    let parts: Vec<&str> = text.splitn(4, '|').collect();
    if parts.len() < 3 {
        return Ok(ElicitResponse::Failed {
            reason: format!("unexpected osascript output: {text:?}"),
        });
    }

    let status = parts[0];
    let entered = parts[2];
    let notes_raw = parts.get(3).map(|s| s.to_string());

    match status {
        "answered" => {
            // Convert raw text to FieldValue based on the FieldSpec kind.
            // We don't have the spec here — caller does. For now return
            // Text and let the caller convert. This is a simplification
            // noted in the plan as v0.2 work.
            let value = FieldValue::Text(entered.to_string());
            Ok(ElicitResponse::Answered {
                value,
                notes: notes_raw.filter(|s| !s.is_empty()),
            })
        }
        "cancelled" => Ok(ElicitResponse::Cancelled {
            notes: notes_raw.filter(|s| !s.is_empty()),
        }),
        "timed_out" => Ok(ElicitResponse::TimedOut {
            elapsed_secs: elapsed.as_secs_f64(),
        }),
        "failed" => Ok(ElicitResponse::Failed {
            reason: entered.to_string(),
        }),
        other => Ok(ElicitResponse::Failed {
            reason: format!("unknown status '{other}' in osascript output"),
        }),
    }
}

/// Parse the user's raw text into the correct `FieldValue` variant.
///
/// The macOS renderer returns a `FieldValue::Text` for every input kind
/// (because `display dialog` doesn't preserve types). The dispatcher uses
/// this helper to coerce the string into the requested `FieldSpec` kind.
#[allow(dead_code)]
pub fn coerce_value(spec: &FieldSpec, raw: &str) -> Result<FieldValue, ElicitError> {
    match spec {
        FieldSpec::Text { .. } => Ok(FieldValue::Text(raw.to_string())),
        FieldSpec::LongText { .. } => Ok(FieldValue::LongText(raw.to_string())),
        FieldSpec::Integer { min, max, .. } => {
            let v: i64 = raw.trim().parse().map_err(|_| {
                ElicitError::RendererFailed(format!("not an integer: {raw:?}"))
            })?;
            if let Some(min) = min {
                if v < *min {
                    return Err(ElicitError::RendererFailed(format!(
                        "value {v} < min {min}"
                    )));
                }
            }
            if let Some(max) = max {
                if v > *max {
                    return Err(ElicitError::RendererFailed(format!(
                        "value {v} > max {max}"
                    )));
                }
            }
            Ok(FieldValue::Integer(v))
        }
        FieldSpec::Choice { options, .. } => {
            // Match by label (case-insensitive) first, then by value.
            let lower = raw.to_lowercase();
            for (i, o) in options.iter().enumerate() {
                if o.label.to_lowercase() == lower || o.value.to_lowercase() == lower {
                    return Ok(FieldValue::Choice {
                        value: o.value.clone(),
                        index: i,
                    });
                }
            }
            Err(ElicitError::RendererFailed(format!(
                "value {raw:?} not in choice options"
            )))
        }
        FieldSpec::Boolean { .. } => match raw.to_lowercase().as_str() {
            "yes" | "true" | "ok" | "1" => Ok(FieldValue::Boolean(true)),
            "no" | "false" | "cancel" | "0" => Ok(FieldValue::Boolean(false)),
            _ => Err(ElicitError::RendererFailed(format!(
                "not a boolean: {raw:?}"
            ))),
        },
        FieldSpec::DateTime { picker_kind, .. } => {
            // Validate basic shape; full validation is up to the agent.
            let s = raw.to_string();
            match picker_kind {
                DateTimeKind::Date => {
                    if s.len() != 10 {
                        return Err(ElicitError::RendererFailed(format!(
                            "date must be YYYY-MM-DD, got {s:?}"
                        )));
                    }
                }
                DateTimeKind::Time => {
                    if s.len() != 5 {
                        return Err(ElicitError::RendererFailed(format!(
                            "time must be HH:MM, got {s:?}"
                        )));
                    }
                }
                DateTimeKind::DateTime => {
                    // Trust RFC3339 shape — agent validates if needed.
                }
            }
            Ok(FieldValue::DateTime(s))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn script_includes_title_and_question() {
        let spec = PromptSpec {
            title: "Test".into(),
            question: "What?".into(),
            field: FieldSpec::Boolean {
                label: "yes?".into(),
                default: Some(true),
            },
            notes: None,
            buttons: None,
            urgency: Urgency::Warning,
            timeout_secs: 60,
            request_id: None,
        };
        let s = build_script(&spec).unwrap();
        assert!(s.contains("display dialog"));
        assert!(s.contains("Test"));
        assert!(s.contains("What?"));
        assert!(s.contains("caution")); // warning icon
    }

    #[test]
    fn script_uses_hidden_answer_for_secret() {
        let spec = PromptSpec {
            title: "Token".into(),
            question: "Enter token".into(),
            field: FieldSpec::Text {
                label: "token".into(),
                default: None,
                placeholder: None,
                max_length: None,
                secret: true,
                pattern: None,
            },
            notes: None,
            buttons: None,
            urgency: Urgency::Secret,
            timeout_secs: 60,
            request_id: None,
        };
        let s = build_script(&spec).unwrap();
        assert!(s.contains("with hidden answer"));
    }

    #[test]
    fn script_includes_timeout_clause() {
        let spec = PromptSpec {
            title: "t".into(),
            question: "q".into(),
            field: FieldSpec::Text {
                label: "l".into(),
                default: None,
                placeholder: None,
                max_length: None,
                secret: false,
                pattern: None,
            },
            notes: None,
            buttons: None,
            urgency: Urgency::Info,
            timeout_secs: 30,
            request_id: None,
        };
        let s = build_script(&spec).unwrap();
        assert!(s.contains("giving up after 30"));
    }

    #[test]
    fn coerce_value_integer() {
        let spec = FieldSpec::Integer {
            label: "n".into(),
            min: Some(0),
            max: Some(10),
            default: None,
        };
        let v = coerce_value(&spec, "5").unwrap();
        assert!(matches!(v, FieldValue::Integer(5)));
    }

    #[test]
    fn coerce_value_boolean() {
        let spec = FieldSpec::Boolean {
            label: "?".into(),
            default: None,
        };
        assert!(matches!(
            coerce_value(&spec, "yes").unwrap(),
            FieldValue::Boolean(true)
        ));
        assert!(matches!(
            coerce_value(&spec, "no").unwrap(),
            FieldValue::Boolean(false)
        ));
    }

    #[test]
    fn parse_output_answered() {
        let r = parse_output(b"answered|OK|hello|", b"", Duration::from_secs(1)).unwrap();
        assert!(r.is_answered());
    }

    #[test]
    fn parse_output_cancelled() {
        let r = parse_output(b"cancelled|Cancel|||", b"", Duration::from_secs(1)).unwrap();
        assert!(r.is_cancelled());
    }

    #[test]
    fn parse_output_failed() {
        let r = parse_output(b"failed|Error|something bad|", b"", Duration::from_secs(1)).unwrap();
        assert!(r.is_failed());
    }
}