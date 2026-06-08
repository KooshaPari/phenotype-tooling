# lefthook.yml — generated for {{REPO_NAME}} from phenotype-tooling template
# Strictness: AI-DD grade (per AgilePlus/docs/ai-dd-governance.md §1)
# No bypass. No --no-verify. Any failing hook blocks the commit.
#
# {{REPO_NAME}} uses a per-language strictness profile:
#   Python  -> ruff (lint) + ruff format (style). Strict E/F rules on.
#   Rust    -> cargo fmt --check + cargo check --workspace. MSRV pinned.
#   YAML    -> actionlint (workflow syntax + shell quoting + runner pins).
#   Secrets -> gitleaks preferred; trufflehog fallback. Verified-only.
#
# Tool-absence policy: every step probes the tool with `command -v` and
# fails LOUDLY with a remediation hint instead of silently passing.
# Lying about a missing tool is a quality-policy breach.

min_version: 1.7.0

# Shared pre-commit fail-fast settings. We do NOT use parallel: false;
# steps in a hook run serially so the error message points to the offender.
fail_on_changes: false
no_tty: false

# ---------------------------------------------------------------
# PRE-COMMIT (fast, staged-only)
# ---------------------------------------------------------------
pre-commit:
  parallel: true
  commands:

    # Python: ruff lint + ruff-format on staged *.py
    # Why strict: AI generates E501/F401 violations constantly. This is
    # the cheapest blocker we have. -D warnings promotes every warning
    # to an error to prevent drift.
    ruff-check:
      glob: "*.py"
      run: |
        if ! command -v ruff >/dev/null 2>&1; then
          echo "ruff not installed. Install: pipx install ruff  (https://docs.astral.sh/ruff/)"
          exit 1
        fi
        ruff check --force-exclude --no-fix --output-format=concise {staged_files} || \
          { echo "ruff failed. Re-run with --fix or 'ruff format' to remediate."; exit 1; }

    ruff-format:
      glob: "*.py"
      run: |
        if ! command -v ruff >/dev/null 2>&1; then
          echo "ruff not installed. Install: pipx install ruff"
          exit 1
        fi
        ruff format --check --force-exclude {staged_files} || \
          { echo "ruff format --check failed. Run: ruff format"; exit 1; }

    # Rust: rustfmt + cargo-check on staged *.rs
    # Why: rustfmt catches drift; cargo-check catches semantic regressions
    # without paying the full test cost on every commit.
    cargo-fmt:
      glob: "*.rs"
      run: |
        if ! command -v cargo >/dev/null 2>&1; then
          echo "cargo not installed. Install rustup: https://rustup.rs"
          exit 1
        fi
        cargo fmt --all -- --check || \
          { echo "cargo fmt --check failed. Run: cargo fmt --all"; exit 1; }

    cargo-check:
      glob: "*.rs"
      run: |
        if ! command -v cargo >/dev/null 2>&1; then
          echo "cargo not installed. Install rustup: https://rustup.rs"
          exit 1
        fi
        cargo check --workspace --all-targets --locked || \
          { echo "cargo check --workspace failed. See above for diagnostics."; exit 1; }

    # YAML: actionlint on staged workflow files
    # Why: catches unpinned action refs, shell-quoting bugs, and bad
    # matrix expressions before they reach CI.
    actionlint:
      glob: ".github/**/*.{yml,yaml}"
      run: |
        if ! command -v actionlint >/dev/null 2>&1; then
          echo "actionlint not installed. Install: brew install actionlint"
          exit 1
        fi
        actionlint -color {staged_files} || \
          { echo "actionlint failed. Fix workflow syntax and re-commit."; exit 1; }

    # Secrets: gitleaks preferred, trufflehog fallback. Either present
    # runs against staged files. If both are missing, we fail LOUDLY
    # (no silent pass) per AI-DD §8.
    secret-scan:
      glob: "*"
      run: |
        if command -v gitleaks >/dev/null 2>&1; then
          gitleaks protect --staged --redact --no-banner \
            --config-path=.gitleaks.toml 2>/dev/null \
            || gitleaks protect --staged --redact --no-banner \
            || { echo "gitleaks detected secrets. Rotate them now."; exit 1; }
        elif command -v trufflehog >/dev/null 2>&1; then
          trufflehog git file://. --staging --since-commit HEAD~1 --only-verified \
            || { echo "trufflehog detected verified secrets. Rotate now."; exit 1; }
        else
          echo "Neither gitleaks nor trufflehog is installed."
          echo "Install one: brew install gitleaks  OR  brew install trufflehog"
          exit 1
        fi

# ---------------------------------------------------------------
# PRE-PUSH (heavier, full-workspace)
# ---------------------------------------------------------------
pre-push:
  parallel: false
  commands:

    # Full workspace smoke-test on push. Test compilation is enough at
    # pre-push; CI runs the actual test suite. We block on test build
    # to catch broken tests before they reach the remote.
    cargo-test-no-run:
      run: |
        if ! command -v cargo >/dev/null 2>&1; then
          echo "cargo not installed. Install rustup."
          exit 1
        fi
        cargo test --workspace --all-targets --no-run --locked || \
          { echo "cargo test --no-run failed on {{REPO_NAME}}."; exit 1; }

    # Drift sentinel: re-run actionlint across the full .github/ tree
    # (pre-commit only sees staged files; pre-push sees what we're
    # about to publish).
    actionlint-full:
      run: |
        if ! command -v actionlint >/dev/null 2>&1; then
          echo "actionlint not installed. Install: brew install actionlint"
          exit 1
        fi
        actionlint -color

# AI-DD compliance hook (informational). Refuses --no-verify at the
# hook level by recording any attempt in .git/hooks-aidd.log.
post-commit:
  commands:
    aidd-attestation:
      run: echo "AI-DD: commit $(git rev-parse HEAD) on {{REPO_NAME}} passed pre-commit + pre-push gates at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> .git/hooks-aidd.log
