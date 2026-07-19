//! Benchora — eval/perf harness boundary crate.
//!
//! Suite-facing Harbor soft-eval lives under `harbor-soft/`.
//! Harbor fork/env provisioning lives in portage-temp.

/// Crate identity for absorb/registry probes.
pub fn crate_name() -> &'static str {
    "benchora"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn crate_name_is_benchora() {
        assert_eq!(crate_name(), "benchora");
    }
}
