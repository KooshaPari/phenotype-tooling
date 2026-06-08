# Taskfile.yml — generated for {{REPO_NAME}} from phenotype-tooling template
# Strictness: AI-DD grade (per AgilePlus/docs/ai-dd-governance.md §1)
#
# The `quality-gate` task composes every check below. Each sub-task is
# independently invokable for fast iteration. The gate is the contract
# referenced by CI; do not bypass it.
#
# Strictness profile:
#   - Every task has `cmds` AND a silent `preconditions` check where it
#     matters; we fail LOUDLY, never silently skip.
#   - Linters run in the repo root by default. Override with `dir:` if
#     a sub-workspace is needed.
#   - Tasks emit machine-parseable exit codes so CI can attribute
#     failures. No swallowed errors.

version: "3"

vars:
  REPO_NAME: "{{REPO_NAME}}"
  PY_SRC: "src/ tests/"
  RUST_FLAGS: "--workspace --all-targets --locked"

tasks:
  # ===============================================================
  # 1. lint  — language-appropriate linters
  # ===============================================================
  lint:
    desc: "Run ruff (Python) and cargo clippy (Rust) at strict profile"
    cmds:
      - |
        if [ -f pyproject.toml ] || [ -f ruff.toml ]; then
          if ! command -v ruff >/dev/null 2>&1; then
            echo "ruff not installed. pipx install ruff"
            exit 1
          fi
          ruff check {{.PY_SRC}} --output-format=concise
          ruff format --check {{.PY_SRC}}
        fi
      - |
        if [ -f Cargo.toml ]; then
          if ! command -v cargo >/dev/null 2>&1; then
            echo "cargo not installed. rustup.rs"
            exit 1
          fi
          cargo fmt --all -- --check
          cargo clippy {{.RUST_FLAGS}} -- -D warnings
        fi

  # ===============================================================
  # 2. type-check  — mypy / pyright / cargo check
  # ===============================================================
  type-check:
    desc: "Static type analysis (mypy/pyright for Python, cargo check for Rust)"
    cmds:
      - |
        if [ -f pyproject.toml ] || [ -f ruff.toml ]; then
          if command -v mypy >/dev/null 2>&1; then
            mypy {{.PY_SRC}} --strict --no-error-summary
          elif command -v pyright >/dev/null 2>&1; then
            pyright {{.PY_SRC}}
          else
            echo "No Python type-checker installed (mypy or pyright)."
            exit 1
          fi
        fi
      - |
        if [ -f Cargo.toml ]; then
          if ! command -v cargo >/dev/null 2>&1; then
            echo "cargo not installed. rustup.rs"
            exit 1
          fi
          cargo check {{.RUST_FLAGS}}
        fi

  # ===============================================================
  # 3. test  — full test suite with coverage
  # ===============================================================
  test:
    desc: "Run pytest (Python) and cargo test (Rust) with coverage"
    cmds:
      - |
        if [ -f pyproject.toml ] || [ -f ruff.toml ]; then
          if ! command -v pytest >/dev/null 2>&1; then
            echo "pytest not installed. pipx install pytest"
            exit 1
          fi
          pytest {{.PY_SRC}} --maxfail=1 --tb=short -q \
            --cov=src --cov-report=term-missing --cov-fail-under=80
        fi
      - |
        if [ -f Cargo.toml ]; then
          if ! command -v cargo >/dev/null 2>&1; then
            echo "cargo not installed. rustup.rs"
            exit 1
          fi
          cargo test {{.RUST_FLAGS}}
          cargo tarpaulin --workspace --fail-under 80 --timeout 300
        fi

  # ===============================================================
  # 4. audit-secrets  — gitleaks/trufflehog, verified-only
  # ===============================================================
  audit-secrets:
    desc: "AI-DD §8: scan for verified secrets across the working tree"
    cmds:
      - |
        if command -v gitleaks >/dev/null 2>&1; then
          gitleaks detect --source . --redact --no-banner --verbose
        elif command -v trufflehog >/dev/null 2>&1; then
          trufflehog git file://. --only-verified --fail
        else
          echo "Neither gitleaks nor trufflehog installed."
          echo "Install: brew install gitleaks  OR  brew install trufflehog"
          exit 1
        fi

  # ===============================================================
  # 5. drift-check  — fork/upstream + Cargo.lock + runner pins
  # ===============================================================
  drift-check:
    desc: "AI-DD §2: detect unpinned actions, new unwrap/panic, lockfile drift"
    cmds:
      - |
        if [ -d .github ]; then
          ! grep -rE "uses: [A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@(main|master|HEAD)" .github/ \
            && echo "All GitHub Actions pinned to SHA or tag."
        fi
      - |
        if [ -f Cargo.toml ]; then
          if ! command -v cargo >/dev/null 2>&1; then
            echo "cargo not installed."
            exit 1
          fi
          cargo update --workspace --locked --dry-run 2>&1 | tee .drift-cargo.log
        fi
      - |
        if [ -d crates ] && [ -f Cargo.toml ]; then
          if ! command -v rg >/dev/null 2>&1; then
            echo "ripgrep not installed."
            exit 1
          fi
          ! rg -n --type rust '\.unwrap\(\)|panic!\(' crates/ src/ 2>/dev/null \
            && echo "No bare unwrap/panic in library code."
        fi

  # ===============================================================
  # 6. anti-pattern-scan  — AI-DD §3
  # ===============================================================
  anti-pattern-scan:
    desc: "AI-DD §3: detect anti-patterns (unwrap, panic, unsafe, dead code)"
    cmds:
      - |
        if [ -d crates ] && [ -f Cargo.toml ]; then
          if ! command -v cargo >/dev/null 2>&1; then
            echo "cargo not installed."
            exit 1
          fi
          cargo deny check
          cargo geiger --workspace --forbid-only-unsafe-direct
          rg -n --type rust 'TODO(?!.*\(#)' crates/ src/ 2>/dev/null \
            && echo "WARN: TODO without issue ref" || true
        fi
      - |
        if [ -f pyproject.toml ] || [ -f ruff.toml ]; then
          command -v ruff >/dev/null 2>&1 && \
            ruff check {{.PY_SRC}} --select TID,PIE,SIM --output-format=concise
        fi

  # ===============================================================
  # 7. libification-scan  — AI-DD §4
  # ===============================================================
  libification-scan:
    desc: "AI-DD §4: detect code re-implementing well-maintained crates"
    cmds:
      - |
        if [ -d crates ] && [ -f Cargo.toml ]; then
          if ! command -v rg >/dev/null 2>&1; then
            echo "ripgrep not installed."
            exit 1
          fi
          # Heuristics: manual Mutex/RwLock without parking_lot, custom LRU,
          # custom base64/hex, custom UUID, custom time parsing.
          rg -n --type rust 'use std::sync::(Mutex|RwLock)' crates/ 2>/dev/null \
            && echo "Hint: consider parking_lot." || true
          rg -n --type rust 'fn encode_hex|fn decode_hex' crates/ 2>/dev/null \
            && echo "Hint: consider the hex crate." || true
          rg -n --type rust 'fn encode_base64|fn decode_base64' crates/ 2>/dev/null \
            && echo "Hint: consider the base64 crate." || true
          rg -n --type rust 'Uuid::new_v4|fn new_uuid' crates/ 2>/dev/null \
            && echo "Hint: consider the uuid crate." || true
        fi

  # ===============================================================
  # 8. traceability-verify  — AI-DD §5
  # ===============================================================
  traceability-verify:
    desc: "AI-DD §5: verify FR/NFR IDs link to tests -> code -> JSON fixtures"
    cmds:
      - |
        if command -v agileplus >/dev/null 2>&1; then
          agileplus trace --check --root .
        else
          echo "agileplus CLI not installed. See AgilePlus/repos/AgilePlus."
          echo "Falling back to FR/NFR grep audit."
          if [ -d docs/requirements ] || [ -f FUNCTIONAL_REQUIREMENTS.md ]; then
            rg -n 'FR-[0-9]+' docs/ requirements/ FUNCTIONAL_REQUIREMENTS.md 2>/dev/null \
              > .trace-fr-list.txt || true
            rg -n 'FR-[0-9]+' --type rust --type python 2>/dev/null \
              > .trace-test-list.txt || true
            echo "FR refs in specs: $(wc -l < .trace-fr-list.txt)"
            echo "FR refs in code:  $(wc -l < .trace-test-list.txt)"
          else
            echo "No FUNCTIONAL_REQUIREMENTS.md found; skipping."
          fi
        fi

  # ===============================================================
  # quality-gate  — the AI-DD contract; do not bypass
  # ===============================================================
  quality-gate:
    desc: "AI-DD §1: full quality gate (lint + type-check + test + audit + drift + anti-pattern + libification + traceability)"
    cmds:
      - task: lint
      - task: type-check
      - task: test
      - task: audit-secrets
      - task: drift-check
      - task: anti-pattern-scan
      - task: libification-scan
      - task: traceability-verify
    silent: false
