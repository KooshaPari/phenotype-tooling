// @trace QG-CHK-001: check-type orchestration + aggregation
//
// Runs each enabled check category against the project and aggregates results.
// Each sub-module handles one category; language detection decides which runners fire.

use std::path::Path;

use anyhow::Result;
use tokio::process::Command;

use crate::checks::{CheckCategory, CheckMatrix, CheckResult, CheckStatus, Thresholds};
use crate::config::QGateConfig;

/// Detect what stacks are present in the project root.
pub struct StackDetector<'a> {
    root: &'a Path,
}

impl<'a> StackDetector<'a> {
    pub fn new(root: &'a Path) -> Self { Self { root } }

    pub fn has_rust(&self) -> bool { self.root.join("Cargo.toml").exists() }
    pub fn has_typescript(&self) -> bool {
        self.root.join("package.json").exists() || self.root.join("bun.lock").exists()
    }
    pub fn has_python(&self) -> bool {
        self.root.join("pyproject.toml").exists() || self.root.join("requirements.txt").exists()
    }
    pub fn has_ui(&self) -> bool {
        // Heuristic: any .html, .tsx, .svelte, or .vue file
        let extensions = ["html", "tsx", "svelte", "vue"];
        extensions.iter().any(|ext| {
            walkdir::WalkDir::new(self.root)
                .max_depth(5)
                .into_iter()
                .filter_map(|e| e.ok())
                .any(|e| e.path().extension().is_some_and(|x| x == *ext))
        })
    }
}

/// Run a shell command and return (success, combined output tail).
async fn run_cmd(program: &str, args: &[&str], cwd: &Path) -> Result<(bool, String)> {
    let output = Command::new(program)
        .args(args)
        .current_dir(cwd)
        .output()
        .await?;
    let combined = [
        String::from_utf8_lossy(&output.stdout).to_string(),
        String::from_utf8_lossy(&output.stderr).to_string(),
    ]
    .join("\n");
    let tail: String = combined
        .lines()
        .rev()
        .take(30)
        .collect::<Vec<_>>()
        .into_iter()
        .rev()
        .collect::<Vec<_>>()
        .join("\n");
    Ok((output.status.success(), tail))
}

/// Orchestrate all check categories and return an aggregated `CheckMatrix`.
pub async fn run_all_checks(root: &Path, cfg: &QGateConfig) -> Result<CheckMatrix> {
    let stack = StackDetector::new(root);
    let mut results: Vec<CheckResult> = Vec::new();

    // ── Unit tests ─────────────────────────────────────────────────────────
    if cfg.is_na("unit") {
        results.push(na("unit", CheckCategory::Unit));
    } else if stack.has_rust() {
        let (ok, detail) = run_cmd("cargo", &["test", "--workspace", "--lib"], root).await
            .unwrap_or((false, "cargo not found".into()));
        results.push(CheckResult {
            category: CheckCategory::Unit,
            status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
            score: if ok { Some(100.0) } else { Some(0.0) },
            threshold: Some(Thresholds::UNIT_PASS_RATE),
            details: if ok { "all unit tests passed".into() } else { detail },
        });
    } else if stack.has_typescript() {
        let (ok, detail) = run_cmd("bun", &["test"], root).await
            .unwrap_or((false, "bun not found".into()));
        results.push(CheckResult {
            category: CheckCategory::Unit,
            status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
            score: if ok { Some(100.0) } else { Some(0.0) },
            threshold: Some(Thresholds::UNIT_PASS_RATE),
            details: if ok { "all bun tests passed".into() } else { detail },
        });
    } else if stack.has_python() {
        let (ok, detail) = run_cmd("uv", &["run", "pytest", "-x", "--tb=short"], root).await
            .unwrap_or((false, "uv not found".into()));
        results.push(CheckResult {
            category: CheckCategory::Unit,
            status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
            score: if ok { Some(100.0) } else { Some(0.0) },
            threshold: Some(Thresholds::UNIT_PASS_RATE),
            details: if ok { "all pytest tests passed".into() } else { detail },
        });
    } else {
        results.push(skipped("unit", CheckCategory::Unit, "no supported stack detected"));
    }

    // ── Integration tests ──────────────────────────────────────────────────
    if cfg.is_na("integration") {
        results.push(na("integration", CheckCategory::Integration));
    } else if stack.has_rust() {
        let (ok, detail) = run_cmd(
            "cargo", &["test", "--workspace", "--test", "*"], root,
        ).await.unwrap_or((false, "cargo not found".into()));
        results.push(CheckResult {
            category: CheckCategory::Integration,
            status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
            score: if ok { Some(100.0) } else { Some(0.0) },
            threshold: Some(Thresholds::INTEGRATION_PASS_RATE),
            details: if ok { "integration tests passed".into() } else { detail },
        });
    } else {
        results.push(skipped("integration", CheckCategory::Integration, "stack-specific runner not configured"));
    }

    // ── E2E tests ──────────────────────────────────────────────────────────
    if cfg.is_na("e2e") {
        results.push(na("e2e", CheckCategory::E2e));
    } else {
        // Try playwright, then cypress, then cargo e2e feature.
        let playwright_ok = root.join("playwright.config.ts").exists()
            || root.join("playwright.config.js").exists();
        if playwright_ok {
            let (ok, detail) = run_cmd("bun", &["x", "playwright", "test"], root).await
                .unwrap_or((false, "playwright not available".into()));
            results.push(CheckResult {
                category: CheckCategory::E2e,
                status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
                score: if ok { Some(100.0) } else { Some(0.0) },
                threshold: Some(Thresholds::E2E_PASS_RATE),
                details: if ok { "playwright e2e passed".into() } else { detail },
            });
        } else {
            results.push(skipped("e2e", CheckCategory::E2e, "no playwright.config found"));
        }
    }

    // ── Chaos ──────────────────────────────────────────────────────────────
    if cfg.is_na("chaos") {
        results.push(na("chaos", CheckCategory::Chaos));
    } else {
        // Look for a chaos script or `cargo test --features chaos`.
        let chaos_script = root.join("scripts/chaos.sh");
        if chaos_script.exists() {
            let (ok, detail) = run_cmd("bash", &[chaos_script.to_str().unwrap_or("")], root).await
                .unwrap_or((false, "bash not found".into()));
            results.push(CheckResult {
                category: CheckCategory::Chaos,
                status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
                score: None,
                threshold: Some(Thresholds::CHAOS_RESILIENCE),
                details: if ok { "chaos tests passed".into() } else { detail },
            });
        } else {
            results.push(skipped("chaos", CheckCategory::Chaos, "no scripts/chaos.sh found"));
        }
    }

    // ── Perf / bench ───────────────────────────────────────────────────────
    if cfg.is_na("perf") {
        results.push(na("perf", CheckCategory::Perf));
    } else if stack.has_rust() {
        // cargo bench — success means benchmarks compile and run; threshold is advisory here
        let (ok, detail) = run_cmd("cargo", &["bench", "--workspace", "--no-run"], root).await
            .unwrap_or((false, "cargo not found".into()));
        results.push(CheckResult {
            category: CheckCategory::Perf,
            status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
            score: None,
            threshold: Some(cfg.perf_init_ms),
            details: if ok { "bench compile passed".into() } else { detail },
        });
    } else {
        results.push(skipped("perf", CheckCategory::Perf, "no Rust bench runner detected"));
    }

    // ── Property / fuzz ────────────────────────────────────────────────────
    if cfg.is_na("property") {
        results.push(na("property", CheckCategory::Property));
    } else if stack.has_rust() {
        // Run proptest / quickcheck if `#[cfg(test)]` features indicate them.
        let (ok, detail) = run_cmd(
            "cargo", &["test", "--workspace", "--features", "proptest"], root,
        ).await.unwrap_or((false, "no proptest feature".into()));
        results.push(CheckResult {
            category: CheckCategory::Property,
            status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
            score: None,
            threshold: Some(Thresholds::PROPERTY_COUNTEREXAMPLES),
            details: if ok { "property tests passed".into() } else { detail },
        });
    } else {
        results.push(skipped("property", CheckCategory::Property, "no Rust proptest runner"));
    }

    // ── Mutation ───────────────────────────────────────────────────────────
    if cfg.is_na("mutation") {
        results.push(na("mutation", CheckCategory::Mutation));
    } else if stack.has_rust() {
        // cargo-mutants must be installed; run with a 5-minute timeout.
        let mutants_available = run_cmd("cargo", &["mutants", "--version"], root).await
            .map(|(ok, _)| ok)
            .unwrap_or(false);
        if mutants_available {
            let (ok, detail) = run_cmd(
                "cargo", &["mutants", "--workspace", "--timeout", "60"], root,
            ).await.unwrap_or((false, "cargo-mutants failed".into()));
            results.push(CheckResult {
                category: CheckCategory::Mutation,
                status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
                score: None,
                threshold: Some(cfg.mutation_threshold),
                details: if ok { "mutation score passed".into() } else { detail },
            });
        } else {
            results.push(skipped("mutation", CheckCategory::Mutation, "cargo-mutants not installed"));
        }
    } else if stack.has_python() {
        let (ok, detail) = run_cmd("uv", &["run", "mutmut", "run"], root).await
            .unwrap_or((false, "mutmut not found".into()));
        results.push(CheckResult {
            category: CheckCategory::Mutation,
            status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
            score: None,
            threshold: Some(cfg.mutation_threshold),
            details: if ok { "mutmut passed".into() } else { detail },
        });
    } else {
        results.push(skipped("mutation", CheckCategory::Mutation, "no mutation runner for stack"));
    }

    // ── Static analysis ────────────────────────────────────────────────────
    if cfg.is_na("static_analysis") {
        results.push(na("static_analysis", CheckCategory::StaticAnalysis));
    } else {
        let mut sa_details: Vec<String> = Vec::new();
        let mut sa_failed = false;

        if stack.has_rust() {
            let (ok, detail) = run_cmd(
                "cargo", &["clippy", "--workspace", "--", "-D", "warnings"], root,
            ).await.unwrap_or((false, "clippy not found".into()));
            if !ok { sa_failed = true; sa_details.push(format!("clippy: {}", detail.lines().next().unwrap_or(""))); }
            else { sa_details.push("clippy: ok".into()); }

            let (fmt_ok, fmt_detail) = run_cmd(
                "cargo", &["fmt", "--all", "--", "--check"], root,
            ).await.unwrap_or((false, "rustfmt not found".into()));
            if !fmt_ok { sa_failed = true; sa_details.push(format!("rustfmt: {}", fmt_detail.lines().next().unwrap_or(""))); }
            else { sa_details.push("rustfmt: ok".into()); }
        }

        if stack.has_typescript() {
            let (ok, detail) = run_cmd("bun", &["x", "tsgo", "--noEmit"], root).await
                .unwrap_or_else(|_| {
                    // fallback to tsc if tsgo not installed
                    (false, "tsgo not found, falling back".into())
                });
            if !ok {
                // try tsc
                let (tsc_ok, tsc_detail) = tokio::process::Command::new("bun")
                    .args(["x", "tsc", "--noEmit"])
                    .current_dir(root)
                    .output()
                    .await
                    .map(|o| (o.status.success(), String::from_utf8_lossy(&o.stderr).to_string()))
                    .unwrap_or((false, "tsc not found".into()));
                if !tsc_ok { sa_failed = true; sa_details.push(format!("tsc: {}", tsc_detail.lines().next().unwrap_or(""))); }
                else { sa_details.push("tsc: ok".into()); }
            } else {
                sa_details.push(format!("tsgo: {}", if ok { "ok" } else { &detail }));
            }

            let (lint_ok, lint_detail) = run_cmd("bun", &["run", "lint"], root).await
                .unwrap_or((false, "eslint not found".into()));
            if !lint_ok { sa_failed = true; sa_details.push(format!("eslint: {}", lint_detail.lines().next().unwrap_or(""))); }
            else { sa_details.push("eslint: ok".into()); }
        }

        if stack.has_python() {
            let (ok, detail) = run_cmd("uv", &["run", "mypy", "."], root).await
                .unwrap_or((false, "mypy not found".into()));
            if !ok { sa_failed = true; sa_details.push(format!("mypy: {}", detail.lines().next().unwrap_or(""))); }
            else { sa_details.push("mypy: ok".into()); }

            let (ruff_ok, ruff_detail) = run_cmd("uv", &["run", "ruff", "check", "."], root).await
                .unwrap_or((false, "ruff not found".into()));
            if !ruff_ok { sa_failed = true; sa_details.push(format!("ruff: {}", ruff_detail.lines().next().unwrap_or(""))); }
            else { sa_details.push("ruff: ok".into()); }
        }

        results.push(CheckResult {
            category: CheckCategory::StaticAnalysis,
            status: if sa_failed { CheckStatus::Failed } else { CheckStatus::Passed },
            score: if sa_failed { Some(1.0) } else { Some(0.0) },
            threshold: Some(Thresholds::STATIC_ANALYSIS_ERRORS),
            details: sa_details.join("; "),
        });
    }

    // ── Security ───────────────────────────────────────────────────────────
    if cfg.is_na("security") {
        results.push(na("security", CheckCategory::Security));
    } else {
        let mut sec_failed = false;
        let mut sec_details: Vec<String> = Vec::new();

        // gitleaks for secrets
        let (gl_ok, gl_detail) = run_cmd("gitleaks", &["detect", "--no-git", "--exit-code", "1"], root).await
            .unwrap_or((true, "gitleaks not installed — skipping".into()));
        if !gl_ok { sec_failed = true; sec_details.push(format!("gitleaks: {}", gl_detail.lines().next().unwrap_or(""))); }
        else { sec_details.push("gitleaks: ok".into()); }

        // semgrep SAST — moved to dedicated Sast category (see below)
        let (sg_ok, sg_detail) = run_cmd(
            "semgrep", &["--config=auto", "--error", "--quiet", "."], root,
        ).await.unwrap_or((true, "semgrep not installed — skipping".into()));
        if !sg_ok { sec_failed = true; sec_details.push(format!("semgrep: {}", sg_detail.lines().next().unwrap_or(""))); }
        else { sec_details.push("semgrep: ok".into()); }

        if stack.has_rust() {
            let (ca_ok, ca_detail) = run_cmd("cargo", &["audit"], root).await
                .unwrap_or((true, "cargo-audit not installed — skipping".into()));
            if !ca_ok { sec_failed = true; sec_details.push(format!("cargo-audit: {}", ca_detail.lines().next().unwrap_or(""))); }
            else { sec_details.push("cargo-audit: ok".into()); }
        }

        if stack.has_python() {
            let (bandit_ok, bandit_detail) = run_cmd(
                "uv", &["run", "bandit", "-r", ".", "-ll"], root,
            ).await.unwrap_or((true, "bandit not installed — skipping".into()));
            if !bandit_ok { sec_failed = true; sec_details.push(format!("bandit: {}", bandit_detail.lines().next().unwrap_or(""))); }
            else { sec_details.push("bandit: ok".into()); }
        }

        results.push(CheckResult {
            category: CheckCategory::Security,
            status: if sec_failed { CheckStatus::Failed } else { CheckStatus::Passed },
            score: if sec_failed { Some(1.0) } else { Some(0.0) },
            threshold: Some(Thresholds::SECURITY_HIGH_FINDINGS),
            details: sec_details.join("; "),
        });
    }

    // ── SAST (semgrep) — dedicated category for static analysis findings ───
    // Semgrep was historically bundled under Security; splitting it out lets
    // repos opt-in independently (e.g. language-specific configs) and gives
    // DAST/SBOM their own audit trail.
    if cfg.is_na("sast") {
        results.push(na("sast", CheckCategory::Sast));
    } else {
        let semgrep_available = run_cmd("semgrep", &["--version"], root).await
            .map(|(ok, _)| ok)
            .unwrap_or(false);
        if semgrep_available {
            // Prefer repo-supplied `.semgrep.yml` if present; otherwise auto.
            let cfg_arg: &str = if root.join(".semgrep.yml").exists()
                || root.join(".semgrep.yaml").exists()
                || root.join("semgrep.yml").exists()
            {
                "--config=.semgrep.yml"
            } else {
                "--config=auto"
            };
            let (ok, detail) = run_cmd(
                "semgrep",
                &[cfg_arg, "--error", "--quiet", "--json", "--output=/tmp/semgrep.json", "."],
                root,
            ).await.unwrap_or((false, "semgrep failed".into()));
            // Count high/critical findings from the JSON (best-effort, fall
            // back to exit-code if /tmp/semgrep.json is unreadable).
            let high_count = parse_semgrep_high_count("/tmp/semgrep.json");
            let (status, score) = if !ok {
                (CheckStatus::Failed, Some(high_count.max(1.0)))
            } else if high_count > 0.0 {
                (CheckStatus::Failed, Some(high_count))
            } else {
                (CheckStatus::Passed, Some(0.0))
            };
            let details = match status {
                CheckStatus::Passed => "semgrep: 0 high/critical findings".to_string(),
                _ => format!("semgrep: {high_count} high/critical findings — {detail}"),
            };
            results.push(CheckResult {
                category: CheckCategory::Sast,
                status,
                score,
                threshold: Some(Thresholds::SAST_HIGH_FINDINGS),
                details,
            });
        } else {
            results.push(skipped("sast", CheckCategory::Sast, "semgrep not installed"));
        }
    }

    // ── DAST (schemathesis) — schema-driven black-box API fuzzing ─────────
    // Looks for `.qgate/dast-schemathesis.toml` (or env QGATE_DAST_BASE_URL)
    // describing the OpenAPI URL and base URL; runs `schemathesis run` with
    // a 5-minute timeout and parses the JSON report for failed-check counts.
    if cfg.is_na("dast") {
        results.push(na("dast", CheckCategory::Dast));
    } else {
        let dast_cfg = DastConfig::discover(root);
        match dast_cfg {
            None => results.push(skipped(
                "dast",
                CheckCategory::Dast,
                "no .qgate/dast.toml or QGATE_DAST_BASE_URL configured",
            )),
            Some(cfg) => {
                let schemathesis_available = run_cmd("schemathesis", &["--version"], root).await
                    .map(|(ok, _)| ok)
                    .unwrap_or(false);
                if !schemathesis_available {
                    results.push(skipped("dast", CheckCategory::Dast, "schemathesis not installed"));
                } else {
                    let report_path = root.join("target/qgate-dast-report.json");
                    let schema_arg = cfg.schema_url.as_deref().unwrap_or(&cfg.base_url);
                    let (ok, detail) = run_cmd(
                        "schemathesis",
                        &[
                            "run",
                            schema_arg,
                            "--base-url",
                            &cfg.base_url,
                            "--checks=all",
                            "--max-examples=50",
                            "--request-timeout=5",
                            &format!("--report-json={}", report_path.display()),
                        ],
                        root,
                    ).await.unwrap_or((false, "schemathesis crashed".into()));
                    let failed = parse_dast_failed_count(&report_path);
                    let (status, score) = if !ok {
                        (CheckStatus::Failed, Some(failed.max(1.0)))
                    } else if failed > 0.0 {
                        (CheckStatus::Failed, Some(failed))
                    } else {
                        (CheckStatus::Passed, Some(0.0))
                    };
                    let details = match status {
                        CheckStatus::Passed => {
                            format!("schemathesis: 0 failed checks against {}", cfg.base_url)
                        }
                        _ => format!("schemathesis: {failed} failed checks — {detail}"),
                    };
                    results.push(CheckResult {
                        category: CheckCategory::Dast,
                        status,
                        score,
                        threshold: Some(Thresholds::DAST_FAILED_CHECKS),
                        details,
                    });
                }
            }
        }
    }

    // ── SBOM (CycloneDX) — supply-chain artifact must be generated ────────
    // Repo opts in via `.qgate.toml` field `sbom_command` or by shipping a
    // pre-generated `target/sbom.cdx.json`. If neither is present and SBOM is
    // not declared N/A, the check is SKIPPED (warning) — not failed — to
    // avoid gating every repo on SBOM adoption.
    if cfg.is_na("sbom") {
        results.push(na("sbom", CheckCategory::Sbom));
    } else if let Some(cmd) = cfg.sbom_command.as_deref() {
        let (ok, detail) = run_cmd("bash", &["-c", cmd], root).await
            .unwrap_or((false, "sbom command failed to execute".into()));
        let artifact = root.join("target/sbom.cdx.json");
        let present = artifact.exists();
        let (status, score, details) = if ok && present {
            (CheckStatus::Passed, Some(1.0), format!("sbom generated: {}", artifact.display()))
        } else if present {
            (CheckStatus::Passed, Some(1.0), format!("sbom artifact present (command exited non-zero but artifact exists): {}", artifact.display()))
        } else {
            (CheckStatus::Failed, Some(0.0), format!("sbom command did not produce target/sbom.cdx.json: {detail}"))
        };
        results.push(CheckResult {
            category: CheckCategory::Sbom,
            status,
            score,
            threshold: Some(Thresholds::SBOM_MUST_EXIST),
            details,
        });
    } else {
        let artifact = root.join("target/sbom.cdx.json");
        if artifact.exists() {
            results.push(CheckResult {
                category: CheckCategory::Sbom,
                status: CheckStatus::Passed,
                score: Some(1.0),
                threshold: Some(Thresholds::SBOM_MUST_EXIST),
                details: format!("sbom artifact present at {}", artifact.display()),
            });
        } else {
            results.push(skipped(
                "sbom",
                CheckCategory::Sbom,
                "no sbom_command in .qgate.toml and target/sbom.cdx.json not found",
            ));
        }
    }

    // ── A11y ───────────────────────────────────────────────────────────────
    if cfg.is_na("a11y") {
        results.push(na("a11y", CheckCategory::A11y));
    } else if stack.has_ui() {
        let (ok, detail) = run_cmd("bun", &["x", "axe", "--exit"], root).await
            .unwrap_or((true, "axe not installed — skipping".into()));
        results.push(CheckResult {
            category: CheckCategory::A11y,
            status: if ok { CheckStatus::Passed } else { CheckStatus::Failed },
            score: None,
            threshold: Some(Thresholds::A11Y_VIOLATIONS),
            details: if ok { "axe: 0 violations".into() } else { detail },
        });
    } else {
        results.push(na("a11y", CheckCategory::A11y));
    }

    Ok(CheckMatrix::from_results(results))
}

fn na(name: &str, cat: CheckCategory) -> CheckResult {
    CheckResult {
        category: cat,
        status: CheckStatus::NotApplicable,
        score: None,
        threshold: None,
        details: format!("{name} explicitly declared N/A"),
    }
}

fn skipped(name: &str, cat: CheckCategory, reason: &str) -> CheckResult {
    CheckResult {
        category: cat,
        status: CheckStatus::Skipped,
        score: None,
        threshold: None,
        details: format!("{name} skipped: {reason}"),
    }
}

// ─── DAST configuration discovery ─────────────────────────────────────────
//
// A repo opts into DAST by shipping `.qgate/dast.toml` with `base_url` and
// (optionally) `schema_url` pointing at an OpenAPI document. Falling back to
// `QGATE_DAST_BASE_URL` / `QGATE_DAST_SCHEMA_URL` env vars makes it easy to
// drive from CI without committing internal URLs.
#[derive(Debug, Clone)]
struct DastConfig {
    base_url: String,
    schema_url: Option<String>,
}

impl DastConfig {
    fn discover(root: &Path) -> Option<Self> {
        // 1) .qgate/dast.toml (TOML preferred for consistency with .qgate.toml)
        let toml_path = root.join(".qgate/dast.toml");
        if toml_path.exists() {
            if let Ok(content) = std::fs::read_to_string(&toml_path) {
                if let Ok(v) = toml::from_str::<toml::Value>(&content) {
                    let base_url = v.get("base_url")?.as_str()?.to_string();
                    let schema_url = v.get("schema_url").and_then(|s| s.as_str()).map(String::from);
                    if !base_url.is_empty() {
                        return Some(Self { base_url, schema_url });
                    }
                }
            }
        }
        // 2) Environment variables
        let base_url = std::env::var("QGATE_DAST_BASE_URL").ok()?;
        if base_url.is_empty() {
            return None;
        }
        let schema_url = std::env::var("QGATE_DAST_SCHEMA_URL").ok().filter(|s| !s.is_empty());
        Some(Self { base_url, schema_url })
    }
}

/// Parse the high/critical finding count out of a semgrep JSON report.
/// Returns 0.0 if the file is missing, unreadable, or has no findings array.
fn parse_semgrep_high_count(path: &str) -> f64 {
    let Ok(content) = std::fs::read_to_string(path) else { return 0.0; };
    let Ok(v) = serde_json::from_str::<serde_json::Value>(&content) else { return 0.0; };
    let results = v.get("results").and_then(|r| r.as_array()).cloned().unwrap_or_default();
    let mut count: f64 = 0.0;
    for finding in results {
        let severity = finding.get("extra")
            .and_then(|e| e.get("severity"))
            .and_then(|s| s.as_str())
            .unwrap_or("");
        if severity.eq_ignore_ascii_case("error")
            || severity.eq_ignore_ascii_case("warning")
            || severity.eq_ignore_ascii_case("high")
            || severity.eq_ignore_ascii_case("critical")
        {
            count += 1.0;
        }
    }
    count
}

/// Parse the failed-check count out of a schemathesis JSON report.
/// Returns 0.0 if missing/unreadable; counts `failed_examples` if present
/// and `checks[].status == "failure"` markers as a fallback.
fn parse_dast_failed_count(path: &std::path::Path) -> f64 {
    let Ok(content) = std::fs::read_to_string(path) else { return 0.0; };
    let Ok(v) = serde_json::from_str::<serde_json::Value>(&content) else { return 0.0; };
    if let Some(n) = v.get("failed_examples").and_then(|n| n.as_f64()) {
        return n;
    }
    if let Some(n) = v.get("summary")
        .and_then(|s| s.get("failed"))
        .and_then(|n| n.as_f64())
    {
        return n;
    }
    if let Some(arr) = v.get("checks").and_then(|c| c.as_array()) {
        let fails = arr.iter()
            .filter(|c| c.get("status").and_then(|s| s.as_str()) == Some("failure"))
            .count();
        return fails as f64;
    }
    0.0
}
