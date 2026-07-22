//! `elicitate` CLI binary — `ask`, `schema`, `detect`, `smoke`, `serve`.

use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Args, Parser, Subcommand};
use serde_json::json;

use elicitate::options::RendererPreference;
use elicitate::spec::{
    ButtonSpec, ElicitResponse, FieldSpec, FieldValue, NotesSpec,
    PromptSpec, Urgency,
};

/// Native OS popup elicitation — render a modal dialog and read the user's
/// response as typed JSON.
#[derive(Debug, Parser)]
#[command(
    name = "elicitate",
    version,
    about = "Native OS popup elicitation for autonomous agents",
    long_about = "elicitate renders a native OS popup (NSAlert on macOS, Win32 form on Windows, \
                  zenity/kdialog/Tk/inquire on Linux) and returns the user's response as typed JSON. \
                  It is the elicitation primitive used by Forge, Codex, Cursor, and any MCP-compatible agent."
)]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,

    /// Increase verbosity (-v, -vv, -vvv).
    #[arg(short, long, action = clap::ArgAction::Count, global = true)]
    verbose: u8,

    /// Force a specific renderer.
    #[arg(long, global = true, value_enum)]
    renderer: Option<RendererArg>,
}

#[derive(Debug, Clone, Copy, clap::ValueEnum)]
enum RendererArg {
    Auto,
    Gui,
    Tty,
}

impl From<RendererArg> for RendererPreference {
    fn from(r: RendererArg) -> Self {
        match r {
            RendererArg::Auto => RendererPreference::AutoGui,
            RendererArg::Gui => RendererPreference::ForceGui,
            RendererArg::Tty => RendererPreference::ForceTty,
        }
    }
}

#[derive(Debug, Subcommand)]
enum Cmd {
    /// Render a popup from CLI flags, --from-json, or --from-file.
    Ask(AskArgs),
    /// Print the JSON Schema for PromptSpec (or FieldSpec / ElicitResponse).
    Schema(SchemaArgs),
    /// Detect platform + renderer kind.
    Detect,
    /// Render a built-in test popup (used for CI smoke).
    Smoke(SmokeArgs),
    /// Run the MCP server on stdio.
    Serve,
    /// Print version + license info.
    Version,
}

#[derive(Debug, Args)]
struct AskArgs {
    #[arg(long)]
    title: Option<String>,
    #[arg(long)]
    question: Option<String>,

    /// Render from an inline JSON spec. Conflicts with --title / --question.
    #[arg(long, conflicts_with_all = &["title", "question"])]
    from_json: Option<String>,

    /// Render from a JSON spec file. Conflicts with --title / --question.
    #[arg(long, conflicts_with_all = &["title", "question"])]
    from_file: Option<PathBuf>,

    /// Urgency: info | warning | error | secret.
    #[arg(long, default_value = "info")]
    urgency: String,

    /// Timeout in seconds. 0 = no timeout.
    #[arg(long, default_value = "600")]
    timeout_secs: u32,

    /// Cancel button label.
    #[arg(long, default_value = "Cancel")]
    cancel_label: Option<String>,

    /// Confirm button label.
    #[arg(long, default_value = "OK")]
    confirm_label: Option<String>,
}

#[derive(Debug, Args)]
struct SchemaArgs {
    /// Print the FieldSpec schema instead.
    #[arg(long)]
    field: bool,
    /// Print the ElicitResponse schema instead.
    #[arg(long)]
    response: bool,
}

#[derive(Debug, Args)]
struct SmokeArgs {
    /// Title to use for the smoke popup.
    #[arg(long, default_value = "elicitate smoke test")]
    title: String,

    /// Skip the popup entirely (just verify CLI parsing).
    #[arg(long)]
    no_render: bool,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    init_tracing(cli.verbose);

    let result = match cli.cmd {
        Cmd::Ask(args) => cmd_ask(args, cli.renderer.map(std::convert::Into::into)),
        Cmd::Schema(args) => Ok(cmd_schema(args)),
        Cmd::Detect => Ok(cmd_detect()),
        Cmd::Smoke(args) => cmd_smoke(args, cli.renderer.map(std::convert::Into::into)),
        Cmd::Serve => {
            eprintln!("error: 'serve' is provided by the `elicitate-mcp` binary, not `elicitate`. Run `elicitate-mcp` instead.");
            return ExitCode::from(2);
        }
        Cmd::Version => {
            println!("elicitate {}", env!("CARGO_PKG_VERSION"));
            println!("license: MIT");
            println!("repository: https://github.com/KooshaPari/phenotype-tooling");
            return ExitCode::SUCCESS;
        }
    };

    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::FAILURE
        }
    }
}

fn init_tracing(verbose: u8) {
    use tracing_subscriber::EnvFilter;
    let level = match verbose {
        0 => "warn",
        1 => "info",
        2 => "debug",
        _ => "trace",
    };
    let filter =
        EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new(level));
    let _ = tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_target(false)
        .try_init();
}

fn cmd_ask(args: AskArgs, renderer: Option<RendererPreference>) -> Result<(), String> {
    let spec = if let Some(json_str) = args.from_json {
        serde_json::from_str::<PromptSpec>(&json_str)
            .map_err(|e| format!("invalid --from-json: {e}"))?
    } else if let Some(path) = args.from_file {
        let text = std::fs::read_to_string(&path)
            .map_err(|e| format!("read {}: {e}", path.display()))?;
        serde_json::from_str::<PromptSpec>(&text)
            .map_err(|e| format!("parse {}: {e}", path.display()))?
    } else {
        build_minimal_spec_from_flags(&args)?
    };

    let mut opts = elicitate::ElicitOptions::default();
    if let Some(r) = renderer {
        opts.renderer = r;
    }

    let response = elicitate::elicit_with(&spec, &opts).map_err(|e| e.to_string())?;
    let out = serde_json::to_string_pretty(&response)
        .map_err(|e| format!("serialize response: {e}"))?;
    println!("{out}");
    Ok(())
}

/// Build a minimal text-field spec from CLI flags (used when neither
/// --from-json nor --from-file is provided).
fn build_minimal_spec_from_flags(args: &AskArgs) -> Result<PromptSpec, String> {
    let title = args
        .title
        .clone()
        .ok_or_else(|| "--title is required (or use --from-json / --from-file)".to_string())?;
    let question = args
        .question
        .clone()
        .ok_or_else(|| "--question is required (or use --from-json / --from-file)".to_string())?;

    let urgency = match args.urgency.as_str() {
        "info" => Urgency::Info,
        "warning" => Urgency::Warning,
        "error" => Urgency::Error,
        "secret" => Urgency::Secret,
        other => return Err(format!("invalid urgency '{other}'")),
    };

    let buttons = if args.cancel_label.is_some() || args.confirm_label.is_some() {
        Some(ButtonSpec {
            cancel: args.cancel_label.clone().unwrap_or_else(|| "Cancel".into()),
            confirm: args.confirm_label.clone().unwrap_or_else(|| "OK".into()),
            default_is_cancel: false,
        })
    } else {
        None
    };

    Ok(PromptSpec {
        title,
        question,
        field: FieldSpec::Text {
            label: "Enter value".into(),
            default: None,
            placeholder: None,
            max_length: None,
            secret: matches!(urgency, Urgency::Secret),
            pattern: None,
        },
        notes: Some(NotesSpec {
            label: "Notes (optional)".into(),
            default: None,
            max_length: None,
            required: false,
        }),
        buttons,
        urgency,
        timeout_secs: args.timeout_secs,
        request_id: None,
    })
}

fn cmd_schema(args: SchemaArgs) {
    let s = if args.field {
        serde_json::to_string_pretty(&schemars::schema_for!(FieldSpec)).unwrap()
    } else if args.response {
        elicitate::schema_response_json().to_string()
    } else {
        elicitate::schema_json().to_string()
    };
    println!("{s}");
}

fn cmd_detect() {
    let platform = elicitate::platform();
    let auto = elicitate::detect_renderer(RendererPreference::AutoGui);
    let forced_tty = elicitate::detect_renderer(RendererPreference::ForceTty);
    let forced_gui = elicitate::detect_renderer(RendererPreference::ForceGui);
    let result = json!({
        "platform": platform,
        "renderer_auto": auto,
        "renderer_force_tty": forced_tty,
        "renderer_force_gui": forced_gui,
    });
    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_smoke(args: SmokeArgs, renderer: Option<RendererPreference>) -> Result<(), String> {
    if args.no_render {
        println!("smoke: --no-render set, skipping popup");
        return Ok(());
    }
    let spec = PromptSpec {
        title: args.title,
        question: "This is the elicitate smoke test. Did it work?".into(),
        field: FieldSpec::Boolean {
            label: "Worked?".into(),
            default: Some(true),
        },
        notes: None,
        buttons: None,
        urgency: Urgency::Info,
        timeout_secs: 30,
        request_id: Some("smoke".into()),
    };
    let mut opts = elicitate::ElicitOptions::default();
    if let Some(r) = renderer {
        opts.renderer = r;
    }
    match elicitate::elicit_with(&spec, &opts) {
        Ok(ElicitResponse::Answered {
            value: FieldValue::Boolean(b),
            ..
        }) => {
            if b {
                println!("smoke: passed");
                Ok(())
            } else {
                println!("smoke: user said no");
                Err("user reported failure".into())
            }
        }
        Ok(ElicitResponse::Cancelled { .. }) => Err("user cancelled".into()),
        Ok(ElicitResponse::TimedOut { .. }) => Err("popup timed out".into()),
        Ok(ElicitResponse::Failed { reason }) => Err(format!("popup failed: {reason}")),
        Ok(other) => Err(format!("unexpected response variant: {other:?}")),
        Err(e) => Err(e.to_string()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_help() {
        use clap::Parser;
        assert!(Cli::try_parse_from(["elicitate", "--help"]).is_err());
    }

    #[test]
    fn parse_schema_subcommand() {
        use clap::Parser;
        let cli = Cli::try_parse_from(["elicitate", "schema"]).unwrap();
        assert!(matches!(cli.cmd, Cmd::Schema(_)));
    }

    #[test]
    fn parse_detect_subcommand() {
        use clap::Parser;
        let cli = Cli::try_parse_from(["elicitate", "detect"]).unwrap();
        assert!(matches!(cli.cmd, Cmd::Detect));
    }

    #[test]
    fn parse_ask_with_from_json() {
        use clap::Parser;
        let json = r#"{"title":"t","question":"q","field":{"kind":"boolean","label":"?","default":true}}"#;
        let cli = Cli::try_parse_from(["elicitate", "ask", "--from-json", json]).unwrap();
        assert!(matches!(cli.cmd, Cmd::Ask(_)));
    }

    #[test]
    fn parse_ask_requires_either_flags_or_json() {
        use clap::Parser;
        // No flags, no json, no file
        let cli = Cli::try_parse_from(["elicitate", "ask"]);
        // Should parse but fail at runtime in cmd_ask
        assert!(cli.is_ok());
    }

    #[test]
    fn build_minimal_spec_uses_defaults() {
        let args = AskArgs {
            title: Some("t".into()),
            question: Some("q".into()),
            from_json: None,
            from_file: None,
            urgency: "warning".into(),
            timeout_secs: 60,
            cancel_label: None,
            confirm_label: None,
        };
        let spec = build_minimal_spec_from_flags(&args).unwrap();
        assert_eq!(spec.title, "t");
        assert_eq!(spec.question, "q");
        assert_eq!(spec.urgency, Urgency::Warning);
        assert_eq!(spec.timeout_secs, 60);
    }
}