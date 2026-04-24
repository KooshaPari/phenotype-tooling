# quality-gate

Rust CLI that runs `cargo fmt --check`, `cargo clippy -- -D warnings`, and
`cargo test --workspace` and emits a single JSON pass/fail report for CI
gating. Replaces 30+ duplicated `quality-gate.sh` files across the org.

**Replaces (representative set):**
- `repos/AgilePlus/scripts/quality-gate.sh`
- `repos/HexaKit/scripts/quality-gate.sh`
- `repos/heliosApp/scripts/quality-gate.sh`
- `repos/Civis/scripts/quality/quality-gate.sh`
- `repos/thegent/hooks/quality-gate.sh`
- `repos/PolicyStack/scripts/quality-gate.sh`

**Usage:** `quality-gate --path <dir> [--skip-clippy] [--skip-test] [--skip-fmt]`
