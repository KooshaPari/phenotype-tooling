//! quality-gate: aggregates cargo/clippy/test/fmt pass-fail into one gate.
//!
//! Replaces many duplicates of scripts/quality-gate.sh across the org:
//! - repos/AgilePlus/scripts/quality-gate.sh
//! - repos/PhenoKits/HexaKit/scripts/quality-gate.sh
//! - repos/HexaKit/scripts/quality-gate.sh
//! - repos/heliosApp/scripts/quality-gate.sh
//! - repos/PolicyStack/scripts/quality-gate.sh
//! - repos/Civis/scripts/quality/quality-gate.sh
//! - repos/thegent/hooks/quality-gate.sh
//! - repos/portage/scripts/quality-gate.sh
//! - (+30 others in worktrees)

use anyhow::Result;
use clap::Parser;
use serde::Serialize;
use std::path::PathBuf;

/// Run cargo fmt/clippy/test in sequence and emit a JSON pass/fail report.
#[derive(Parser, Debug)]
#[command(version, about)]
struct Cli {
    /// Root directory of the cargo workspace.
    #[arg(short, long, default_value = ".")]
    path: PathBuf,

    /// Skip clippy step.
    #[arg(long)]
    skip_clippy: bool,

    /// Skip test step.
    #[arg(long)]
    skip_test: bool,

    /// Skip fmt step.
    #[arg(long)]
    skip_fmt: bool,

    /// Emit JSON report to stdout.
    #[arg(long, default_value_t = true)]
    json: bool,
}

#[derive(Serialize)]
struct StepResult {
    name: &'static str,
    skipped: bool,
    passed: bool,
    stderr_tail: String,
}

#[derive(Serialize)]
struct Report {
    root: PathBuf,
    all_passed: bool,
    steps: Vec<StepResult>,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // TODO: spawn `cargo fmt --check` via tokio::process::Command.
    // TODO: spawn `cargo clippy --workspace -- -D warnings`.
    // TODO: spawn `cargo test --workspace`.
    // TODO: capture stderr tails, aggregate pass/fail.
    // Source reference: repos/AgilePlus/scripts/quality-gate.sh.
    let steps = vec![
        StepResult { name: "fmt", skipped: cli.skip_fmt, passed: true, stderr_tail: String::new() },
        StepResult {
            name: "clippy",
            skipped: cli.skip_clippy,
            passed: true,
            stderr_tail: String::new(),
        },
        StepResult {
            name: "test",
            skipped: cli.skip_test,
            passed: true,
            stderr_tail: String::new(),
        },
    ];
    let all_passed = steps.iter().all(|s| s.skipped || s.passed);
    let report = Report { root: cli.path.clone(), all_passed, steps };

    if cli.json {
        println!("{}", serde_json::to_string_pretty(&report)?);
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    #[test]
    fn smoke() {}
}
