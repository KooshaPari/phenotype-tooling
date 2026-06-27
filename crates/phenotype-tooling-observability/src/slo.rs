//! Service Level Objectives (SLOs) for the phenotype-tooling ecosystem.
//!
//! SLOs are declarative: a `name`, `target` (success rate or latency
//! p95), and a `window_s`. [`default_slos`] returns the two SLOs that
//! all `phenotype-tooling` deployments should track.

/// SLO definition.
///
/// `target` semantics depend on `kind`:
/// - [`SloKind::StartupLatencyP95`]: `target` is the p95 budget in **milliseconds**.
/// - [`SloKind::SuccessRate`]: `target` is the success rate as a **fraction** in `[0.0, 1.0]`.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize, PartialEq)]
pub struct Slo {
    pub name: String,
    pub kind: SloKind,
    pub target: f64,
    pub window_s: u64,
    pub burn_rate_alert: f64,
}

/// Discriminator for the SLO target's unit.
#[derive(Debug, Clone, Copy, serde::Serialize, serde::Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum SloKind {
    /// Latency budget in milliseconds, measured at p95.
    StartupLatencyP95,
    /// Success rate fraction (e.g. `0.999` for 99.9%).
    SuccessRate,
}

impl Slo {
    /// Construct a startup-latency SLO (ms p95).
    pub fn startup_latency(name: impl Into<String>, target_ms: f64, window_s: u64) -> Self {
        Self {
            name: name.into(),
            kind: SloKind::StartupLatencyP95,
            target: target_ms,
            window_s,
            burn_rate_alert: 2.0,
        }
    }

    /// Construct a success-rate SLO (fraction).
    pub fn success_rate(name: impl Into<String>, target: f64, window_s: u64) -> Self {
        Self {
            name: name.into(),
            kind: SloKind::SuccessRate,
            target,
            window_s,
            burn_rate_alert: 2.0,
        }
    }
}

/// Canonical SLOs for every phenotype-tooling deployment.
pub fn default_slos() -> Vec<Slo> {
    vec![
        Slo::startup_latency("cli_startup_p95", 200.0, 3600),
        Slo::success_rate("cli_success_rate", 0.999, 86_400),
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_slos_returns_two() {
        let slos = default_slos();
        assert_eq!(slos.len(), 2);
    }

    #[test]
    fn cli_startup_target_is_200ms() {
        let slos = default_slos();
        let startup = slos
            .iter()
            .find(|s| matches!(s.kind, SloKind::StartupLatencyP95))
            .expect("startup slo");
        assert_eq!(startup.target, 200.0);
        assert_eq!(startup.window_s, 3600);
    }

    #[test]
    fn cli_success_rate_is_999() {
        let slos = default_slos();
        let sr = slos
            .iter()
            .find(|s| matches!(s.kind, SloKind::SuccessRate))
            .expect("success-rate slo");
        assert!((sr.target - 0.999).abs() < 1e-9);
        assert_eq!(sr.window_s, 86_400);
    }

    #[test]
    fn slo_roundtrips_via_serde_json() {
        let s = Slo::startup_latency("test", 100.0, 600);
        let json = serde_json::to_string(&s).unwrap();
        let back: Slo = serde_json::from_str(&json).unwrap();
        assert_eq!(back, s);
    }
}