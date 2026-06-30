// @trace QG-CHK-001: all-check-types orchestration + per-category thresholds
//
// Defines the check-type matrix and per-category result aggregation.
// The orchestration of running actual tools happens in `src/runner/`.

use serde::{Deserialize, Serialize};

/// All supported check categories. New entries here automatically appear
/// in the default matrix and the JSON report.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Hash)]
#[serde(rename_all = "snake_case")]
pub enum CheckCategory {
    Unit,
    Integration,
    E2e,
    Chaos,
    Perf,
    Property,
    Mutation,
    StaticAnalysis,
    Security,
    A11y,
}

impl CheckCategory {
    pub fn name(&self) -> &'static str {
        match self {
            Self::Unit => "unit",
            Self::Integration => "integration",
            Self::E2e => "e2e",
            Self::Chaos => "chaos",
            Self::Perf => "perf",
            Self::Property => "property",
            Self::Mutation => "mutation",
            Self::StaticAnalysis => "static_analysis",
            Self::Security => "security",
            Self::A11y => "a11y",
        }
    }

    /// All categories in display order.
    pub fn all() -> &'static [CheckCategory] {
        &[
            Self::Unit,
            Self::Integration,
            Self::E2e,
            Self::Chaos,
            Self::Perf,
            Self::Property,
            Self::Mutation,
            Self::StaticAnalysis,
            Self::Security,
            Self::A11y,
        ]
    }
}

/// Per-category result status.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CheckStatus {
    Passed,
    Failed,
    /// Category is explicitly not applicable to this repo (not silently skipped).
    NotApplicable,
    /// Category was configured but runner was not available; treated as warning not fail.
    Skipped,
}

/// Result for one check category.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CheckResult {
    pub category: CheckCategory,
    pub status: CheckStatus,
    /// Numeric score where applicable (e.g., mutation score %, init time ms).
    pub score: Option<f64>,
    /// Pass threshold for numeric score; `None` = pass/fail only.
    pub threshold: Option<f64>,
    pub details: String,
}

impl CheckResult {
    /// True when this result constitutes a gate failure.
    pub fn is_failure(&self) -> bool {
        self.status == CheckStatus::Failed
    }

    pub fn is_applicable(&self) -> bool {
        self.status != CheckStatus::NotApplicable
    }
}

/// The full check matrix: a collection of results, one per applicable category.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CheckMatrix {
    pub results: Vec<CheckResult>,
}

impl CheckMatrix {
    pub fn from_results(results: Vec<CheckResult>) -> Self {
        Self { results }
    }

    /// Iterate all categories represented in this matrix.
    pub fn categories(&self) -> impl Iterator<Item = &CheckResult> {
        self.results.iter()
    }

    /// True when no applicable result is a failure.
    pub fn all_pass(&self) -> bool {
        self.results.iter().all(|r| !r.is_failure())
    }

    /// Return failing results.
    pub fn failures(&self) -> Vec<&CheckResult> {
        self.results.iter().filter(|r| r.is_failure()).collect()
    }
}

impl Default for CheckMatrix {
    /// Default matrix: all categories with NotApplicable status (populated by runner).
    fn default() -> Self {
        let results = CheckCategory::all()
            .iter()
            .map(|&cat| CheckResult {
                category: cat,
                status: CheckStatus::NotApplicable,
                score: None,
                threshold: None,
                details: "not yet evaluated".into(),
            })
            .collect();
        Self { results }
    }
}

// ─── Per-category default thresholds ──────────────────────────────────────

/// Default pass thresholds. All are configurable via `.qgate.toml`.
pub struct Thresholds;

impl Thresholds {
    /// 100% pass rate: all unit tests must pass.
    pub const UNIT_PASS_RATE: f64 = 100.0;
    /// 100% pass rate: all integration tests must pass.
    pub const INTEGRATION_PASS_RATE: f64 = 100.0;
    /// 100% pass rate: all e2e tests must pass.
    pub const E2E_PASS_RATE: f64 = 100.0;
    /// Chaos resiliency score ≥ 80%.
    pub const CHAOS_RESILIENCE: f64 = 80.0;
    /// Init time ≤ 15 000 ms, edit latency ≤ 5 000 ms (MelosViz targets).
    pub const PERF_INIT_MS: f64 = 15_000.0;
    pub const PERF_EDIT_MS: f64 = 5_000.0;
    /// Property / fuzz: 0 counterexamples found.
    pub const PROPERTY_COUNTEREXAMPLES: f64 = 0.0;
    /// Mutation score ≥ 75%.
    pub const MUTATION_SCORE: f64 = 75.0;
    /// Static analysis: 0 errors (warnings may be configurable).
    pub const STATIC_ANALYSIS_ERRORS: f64 = 0.0;
    /// Security: 0 high/critical findings.
    pub const SECURITY_HIGH_FINDINGS: f64 = 0.0;
    /// A11y: 0 violations (only when UI detected).
    pub const A11Y_VIOLATIONS: f64 = 0.0;
}

#[cfg(test)]
mod tests {
    use super::*;

    // @trace QG-CHK-001
    #[test]
    fn all_categories_reachable() {
        let matrix = CheckMatrix::default();
        assert_eq!(matrix.results.len(), CheckCategory::all().len());
    }

    // @trace QG-CHK-002
    #[test]
    fn na_is_not_failure() {
        let r = CheckResult {
            category: CheckCategory::A11y,
            status: CheckStatus::NotApplicable,
            score: None,
            threshold: None,
            details: String::new(),
        };
        assert!(!r.is_failure());
    }

    // @trace QG-CHK-003
    #[test]
    fn failed_is_failure() {
        let r = CheckResult {
            category: CheckCategory::Unit,
            status: CheckStatus::Failed,
            score: Some(90.0),
            threshold: Some(100.0),
            details: "1 test failed".into(),
        };
        assert!(r.is_failure());
    }
}
