//! The agent-authored prompt spec and the human-returned response.
//!
//! These types are the **contract** between the agent and the popup.
//! Both surfaces serialize via serde; the JSON Schema is exported by
//! [`crate::schema`] for the MCP server's `inputSchema` / `outputSchema`.

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// The agent's authored prompt for a single popup.
///
/// The schema is designed so the agent can compose any UI surface from
/// primitive building blocks (text field, choice, boolean, etc.) without
/// the MCP surface needing to grow.
///
/// # Example (serde JSON)
///
/// ```json
/// {
///   "title": "Approve deployment?",
///   "question": "The diff touches 14 files. Continue with rollout?",
///   "field": {
///     "kind": "boolean",
///     "label": "Proceed?",
///     "default": true
///   },
///   "notes": {
///     "label": "Why? (optional)",
///     "required": false
///   },
///   "urgency": "warning",
///   "timeout_secs": 60
/// }
/// ```
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PromptSpec {
    /// One-line title shown in the popup window title bar.
    /// Max 80 chars.
    pub title: String,

    /// Multi-line body explaining context. Plain text only (no markdown —
    /// native chrome has no renderer). Max 2000 chars.
    pub question: String,

    /// The input field configuration.
    pub field: FieldSpec,

    /// Optional notes / free-text box shown below the field.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub notes: Option<NotesSpec>,

    /// Button labels. Default: `{"cancel": "Cancel", "confirm": "OK"}`.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub buttons: Option<ButtonSpec>,

    /// Urgency hint — affects icon + sound.
    #[serde(default)]
    pub urgency: Urgency,

    /// Timeout in seconds. After this, the response is `TimedOut`.
    /// Default: 600 (10 min). Set to 0 for no timeout (CI only).
    #[serde(default = "default_timeout_secs")]
    pub timeout_secs: u32,

    /// Request ID for correlation when multiple prompts are queued.
    /// If omitted, the library auto-generates a UUIDv4.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub request_id: Option<String>,
}

const fn default_timeout_secs() -> u32 {
    600
}

/// The input field configuration.
///
/// Tagged enum over six primitive kinds. Each kind carries only the
/// fields relevant to it; serde's `tag = "kind"` gives clean JSON,
/// and schemars' matching `tag = "kind"` produces a discriminated
/// schema in JSON Schema 2020-12 style.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[schemars(tag = "kind", rename_all = "snake_case")]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum FieldSpec {
    /// Single-line text input.
    Text {
        /// Label shown above the input.
        label: String,
        /// Default value (pre-filled).
        #[serde(default, skip_serializing_if = "Option::is_none")]
        default: Option<String>,
        /// Placeholder text (shown when empty).
        #[serde(default, skip_serializing_if = "Option::is_none")]
        placeholder: Option<String>,
        /// Maximum input length.
        #[serde(default, skip_serializing_if = "Option::is_none")]
        max_length: Option<u32>,
        /// If true, render as password field (• mask).
        #[serde(default)]
        secret: bool,
        /// Regex the value must match before OK is enabled.
        #[serde(default, skip_serializing_if = "Option::is_none")]
        pattern: Option<String>,
    },

    /// Long-form multi-line text.
    LongText {
        label: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        default: Option<String>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        max_length: Option<u32>,
    },

    /// Integer in `[min, max]`.
    Integer {
        label: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        min: Option<i64>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        max: Option<i64>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        default: Option<i64>,
    },

    /// Choice from a fixed list (radio buttons on GUI, select prompt on TUI).
    Choice {
        label: String,
        options: Vec<ChoiceOption>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        default_index: Option<usize>,
    },

    /// Boolean yes/no. Renders as 2 buttons.
    Boolean {
        label: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        default: Option<bool>,
    },

    /// Date / time picker.
    DateTime {
        label: String,
        /// RFC3339 default.
        #[serde(default, skip_serializing_if = "Option::is_none")]
        default: Option<String>,
        /// Which picker to render — date, time, or both.
        #[serde(default = "default_datetime_kind")]
        picker_kind: DateTimeKind,
    },
}

const fn default_datetime_kind() -> DateTimeKind {
    DateTimeKind::DateTime
}

/// A single option in a [`FieldSpec::Choice`].
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ChoiceOption {
    /// Machine-readable value returned in the response.
    pub value: String,
    /// Human-readable label shown in the popup.
    pub label: String,
    /// Optional longer description (shown as help text on GUI).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
}

/// The optional notes / free-text box.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct NotesSpec {
    /// Label shown above the notes box.
    pub label: String,
    /// Pre-filled notes.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub default: Option<String>,
    /// Maximum notes length.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub max_length: Option<u32>,
    /// If true, the OK button is disabled until notes are non-empty.
    #[serde(default)]
    pub required: bool,
}

/// Custom button labels.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ButtonSpec {
    /// Cancel button label. Default: "Cancel".
    pub cancel: String,
    /// Confirm button label. Default: "OK".
    pub confirm: String,
    /// If true, swap which button is the default (Enter-key target).
    #[serde(default)]
    pub default_is_cancel: bool,
}

impl Default for ButtonSpec {
    fn default() -> Self {
        Self {
            cancel: "Cancel".to_string(),
            confirm: "OK".to_string(),
            default_is_cancel: false,
        }
    }
}

/// Urgency hint — affects icon and sound on GUI popups.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[schemars(rename_all = "lowercase")]
#[serde(rename_all = "lowercase")]
pub enum Urgency {
    /// Informational (no sound, blue icon).
    #[default]
    Info,
    /// Warning (system sound, yellow icon).
    Warning,
    /// Error / critical (alert sound, red icon).
    Error,
    /// Treat as secret input (mask field, no logging).
    Secret,
}

/// What kind of date/time picker to render.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[schemars(rename_all = "lowercase")]
#[serde(rename_all = "lowercase")]
pub enum DateTimeKind {
    /// Date only (YYYY-MM-DD).
    Date,
    /// Time only (HH:MM).
    Time,
    /// Both (RFC3339).
    DateTime,
}

/// The value the human entered. Tagged enum mirrors [`FieldSpec`]'s kinds.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[schemars(tag = "kind", content = "value", rename_all = "snake_case")]
#[serde(tag = "kind", content = "value", rename_all = "snake_case")]
pub enum FieldValue {
    /// Text field value.
    Text(String),
    /// Long-text field value.
    LongText(String),
    /// Integer field value.
    Integer(i64),
    /// Choice field value (returns both the value and the index).
    Choice { value: String, index: usize },
    /// Boolean field value.
    Boolean(bool),
    /// Date/time field value (RFC3339).
    DateTime(String),
}

/// The popup's response — either an answer, a cancel, a timeout, or a failure.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[schemars(tag = "status", rename_all = "snake_case")]
#[serde(tag = "status", rename_all = "snake_case")]
pub enum ElicitResponse {
    /// User clicked OK and entered a value.
    Answered {
        value: FieldValue,
        /// Notes if a notes box was rendered and filled.
        #[serde(default, skip_serializing_if = "Option::is_none")]
        notes: Option<String>,
    },
    /// User clicked Cancel. Notes may be populated if they typed some.
    Cancelled {
        #[serde(default, skip_serializing_if = "Option::is_none")]
        notes: Option<String>,
    },
    /// Popup timed out without a response.
    TimedOut {
        /// Seconds elapsed before the timeout fired.
        elapsed_secs: f64,
    },
    /// Popup failed to render. The agent should fall back to a different
    /// strategy (e.g., inline question, or retry with `--renderer=force-tty`).
    Failed {
        /// Human-readable failure reason.
        reason: String,
    },
}

impl PromptSpec {
    /// Validate the spec. Returns an error message on the first violation.
    pub fn validate(&self) -> Result<(), String> {
        if self.title.is_empty() {
            return Err("title must not be empty".into());
        }
        if self.title.chars().count() > 80 {
            return Err(format!(
                "title exceeds 80 chars (got {})",
                self.title.chars().count()
            ));
        }
        if self.question.chars().count() > 2000 {
            return Err(format!(
                "question exceeds 2000 chars (got {})",
                self.question.chars().count()
            ));
        }
        if let FieldSpec::Choice { options, default_index, .. } = &self.field {
            if options.is_empty() {
                return Err("choice field must have at least one option".into());
            }
            if let Some(idx) = default_index {
                if *idx >= options.len() {
                    return Err(format!(
                        "default_index {idx} out of range ({} options)",
                        options.len()
                    ));
                }
            }
        }
        if let FieldSpec::Text { pattern: Some(p), .. } = &self.field {
            regex::Regex::new(p).map_err(|e| format!("invalid pattern regex: {e}"))?;
        }
        Ok(())
    }
}

impl ElicitResponse {
    /// Returns `true` if the user provided an answer (vs cancelling, timing
    /// out, or the popup failing).
    #[must_use]
    pub fn is_answered(&self) -> bool {
        matches!(self, Self::Answered { .. })
    }

    /// Returns `true` if the user cancelled.
    #[must_use]
    pub fn is_cancelled(&self) -> bool {
        matches!(self, Self::Cancelled { .. })
    }

    /// Returns `true` if the popup timed out.
    #[must_use]
    pub fn is_timed_out(&self) -> bool {
        matches!(self, Self::TimedOut { .. })
    }

    /// Returns `true` if the popup failed to render.
    #[must_use]
    pub fn is_failed(&self) -> bool {
        matches!(self, Self::Failed { .. })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn minimal_text() -> PromptSpec {
        PromptSpec {
            title: "Test".into(),
            question: "?".into(),
            field: FieldSpec::Text {
                label: "name".into(),
                default: None,
                placeholder: None,
                max_length: None,
                secret: false,
                pattern: None,
            },
            notes: None,
            buttons: None,
            urgency: Urgency::default(),
            timeout_secs: default_timeout_secs(),
            request_id: None,
        }
    }

    #[test]
    fn validate_accepts_minimal() {
        assert!(minimal_text().validate().is_ok());
    }

    #[test]
    fn validate_rejects_empty_title() {
        let mut s = minimal_text();
        s.title = "".into();
        assert!(s.validate().is_err());
    }

    #[test]
    fn validate_rejects_long_title() {
        let mut s = minimal_text();
        s.title = "x".repeat(81);
        assert!(s.validate().is_err());
    }

    #[test]
    fn validate_rejects_empty_choice() {
        let mut s = minimal_text();
        s.field = FieldSpec::Choice {
            label: "pick".into(),
            options: vec![],
            default_index: None,
        };
        assert!(s.validate().is_err());
    }

    #[test]
    fn validate_rejects_bad_default_index() {
        let mut s = minimal_text();
        s.field = FieldSpec::Choice {
            label: "pick".into(),
            options: vec![ChoiceOption {
                value: "a".into(),
                label: "A".into(),
                description: None,
            }],
            default_index: Some(5),
        };
        assert!(s.validate().is_err());
    }

    #[test]
    fn validate_rejects_bad_regex() {
        let mut s = minimal_text();
        s.field = FieldSpec::Text {
            label: "x".into(),
            default: None,
            placeholder: None,
            max_length: None,
            secret: false,
            pattern: Some("[unclosed".into()),
        };
        assert!(s.validate().is_err());
    }

    #[test]
    fn response_predicates() {
        let ans = ElicitResponse::Answered {
            value: FieldValue::Text("hi".into()),
            notes: None,
        };
        assert!(ans.is_answered());
        assert!(!ans.is_cancelled());

        let can = ElicitResponse::Cancelled { notes: None };
        assert!(can.is_cancelled());
        assert!(!can.is_answered());

        let to = ElicitResponse::TimedOut { elapsed_secs: 1.0 };
        assert!(to.is_timed_out());

        let f = ElicitResponse::Failed { reason: "x".into() };
        assert!(f.is_failed());
    }

    #[test]
    fn serde_roundtrip_text() {
        let s = minimal_text();
        let json = serde_json::to_string(&s).unwrap();
        let back: PromptSpec = serde_json::from_str(&json).unwrap();
        assert_eq!(back.title, s.title);
    }

    #[test]
    fn serde_roundtrip_choice() {
        let s = PromptSpec {
            field: FieldSpec::Choice {
                label: "target".into(),
                options: vec![
                    ChoiceOption {
                        value: "staging".into(),
                        label: "Staging".into(),
                        description: Some("preprod".into()),
                    },
                    ChoiceOption {
                        value: "prod".into(),
                        label: "Production".into(),
                        description: None,
                    },
                ],
                default_index: Some(0),
            },
            ..minimal_text()
        };
        let json = serde_json::to_string(&s).unwrap();
        let back: PromptSpec = serde_json::from_str(&json).unwrap();
        if let FieldSpec::Choice { options, .. } = &back.field {
            assert_eq!(options.len(), 2);
            assert_eq!(options[0].value, "staging");
        } else {
            panic!("round-trip lost choice variant");
        }
    }
}
