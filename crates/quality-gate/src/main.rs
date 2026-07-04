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
use tokio::process::Command;

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

    /// Exit with non-zero status on any failure (default: true).
    #[arg(long, default_value_t = true)]
    fail_fast: bool,
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

/// Run a cargo sub-command and capture the last N lines of stderr.
/// Returns `(passed, stderr_tail)`.
async fn run_cargo(args: &[&str], cwd: &PathBuf) -> Result<(bool, String)> {
    let output = Command::new("cargo")
        .args(args)
        .current_dir(cwd)
        // Disable colour so output is clean in CI and respects NO_COLOR.
        .env(
            "CARGO_TERM_COLOR",
            if std::env::var_os("NO_COLOR").is_some() {
                "never"
            } else {
                "auto"
            },
        )
        .output()
        .await?;

    let stderr = String::from_utf8_lossy(&output.stderr);
    // Keep the last 20 lines for the report.
    let tail: String = stderr
        .lines()
        .rev()
        .take(20)
        .collect::<Vec<_>>()
        .into_iter()
        .rev()
        .collect::<Vec<_>>()
        .join("\n");

    Ok((output.status.success(), tail))
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    let root = cli.path.canonicalize().unwrap_or_else(|_| cli.path.clone());

    let mut steps: Vec<StepResult> = Vec::new();

    // --- fmt --check --------------------------------------------------------
    let fmt_result = if cli.skip_fmt {
        (true, String::new())
    } else {
        run_cargo(&["fmt", "--all", "--", "--check"], &root).await?
    };
    steps.push(StepResult {
        name: "fmt",
        skipped: cli.skip_fmt,
        passed: fmt_result.0,
        stderr_tail: fmt_result.1,
    });

    // --- clippy -------------------------------------------------------------
    let clippy_result = if cli.skip_clippy {
        (true, String::new())
    } else {
        run_cargo(&["clippy", "--workspace", "--", "-D", "warnings"], &root).await?
    };
    steps.push(StepResult {
        name: "clippy",
        skipped: cli.skip_clippy,
        passed: clippy_result.0,
        stderr_tail: clippy_result.1,
    });

    // --- test ---------------------------------------------------------------
    let test_result = if cli.skip_test {
        (true, String::new())
    } else {
        run_cargo(&["test", "--workspace"], &root).await?
    };
    steps.push(StepResult {
        name: "test",
        skipped: cli.skip_test,
        passed: test_result.0,
        stderr_tail: test_result.1,
    });

    let all_passed = steps.iter().all(|s| s.skipped || s.passed);
    let report = Report {
        root,
        all_passed,
        steps,
    };

    if cli.json {
        println!("{}", serde_json::to_string_pretty(&report)?);
    } else {
        // Human-readable summary.
        for s in &report.steps {
            let status = if s.skipped {
                "SKIP"
            } else if s.passed {
                "PASS"
            } else {
                "FAIL"
            };
            eprintln!("[quality-gate] {} {}", status, s.name);
        }
    }

    if cli.fail_fast && !all_passed {
        std::process::exit(1);
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn report_all_passed_when_all_skipped() {
        let steps = vec![
            StepResult {
                name: "fmt",
                skipped: true,
                passed: false,
                stderr_tail: String::new(),
            },
            StepResult {
                name: "clippy",
                skipped: true,
                passed: false,
                stderr_tail: String::new(),
            },
        ];
        let all_passed = steps.iter().all(|s| s.skipped || s.passed);
        assert!(all_passed);
    }

    #[test]
    fn report_fails_when_one_step_fails() {
        let steps = vec![
            StepResult {
                name: "fmt",
                skipped: false,
                passed: true,
                stderr_tail: String::new(),
            },
            StepResult {
                name: "clippy",
                skipped: false,
                passed: false,
                stderr_tail: "error: unused import".into(),
            },
        ];
        let all_passed = steps.iter().all(|s| s.skipped || s.passed);
        assert!(!all_passed);
    }

    #[test]
    fn report_serializes_to_json() {
        let report = Report {
            root: PathBuf::from("/tmp"),
            all_passed: true,
            steps: vec![StepResult {
                name: "fmt",
                skipped: true,
                passed: false,
                stderr_tail: String::new(),
            }],
        };
        let json = serde_json::to_string(&report).unwrap();
        assert!(json.contains("all_passed"));
        assert!(json.contains("steps"));
    }
}
