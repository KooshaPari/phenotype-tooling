# ESLint → Oxlint Migration Guide: 5-50x Linting Speedup

**Status:** Research & Implementation Guide
**Date:** 2026-02-15
**Speedup Target:** 5-50x faster JS/TS linting
**Timeline:** Phase 4 (4-6 hours)
**Risk Level:** MEDIUM (config migration required, but fallback available)

---

## 📚 Executive Summary

**Oxlint** is a Rust-based JavaScript linter built for speed:
- Written in Rust (not JavaScript)
- **5-50x faster** than ESLint (depending on rule set)
- Parallel file processing by default
- Compatible with 95%+ of ESLint configs
- Drop-in replacement for most projects

**Why oxlint specifically:**
- Aligns with "GO/RUST ONLY" modernization constraint
- No NodeJS overhead (pure Rust binary)
- Modern performance design (SIMD, parallelization)
- Active development (OXC initiative)
- Already used by Alibaba, Cloudflare internally

---

## 🎯 Phase 4 Implementation Plan

### Timeline
- **Week 4, Day 1:** Research & config migration (2-3 hours)
- **Week 4, Day 2:** Side-by-side testing (1-2 hours)
- **Week 4, Day 3:** Full rollout & cleanup (1 hour)

### Scope
- Replace ESLint with Oxlint in hooks system
- Migrate .eslintrc config to oxlint.json
- Update CI/CD to use oxlint
- Maintain ESLint fallback for compatibility

### Success Criteria
- Oxlint running successfully
- Linting 5-50x faster
- Zero new rule violations (vs ESLint baseline)
- All existing tests passing
- Clean fallback to ESLint if needed

---

## 📋 Oxlint Basics

### What is Oxlint?

**Oxlint** (part of the OXC project) is a next-generation JavaScript linter:
- **Core:** Written in Rust (oxc parser)
- **Engine:** Parallel linting with SIMD optimizations
- **Rules:** Subset of ESLint (but covers 95% of real usage)
- **Config:** ESLint-compatible JSON format
- **Performance:** 10-50x faster than ESLint depending on codebase

### Performance Comparison

```
ESLint (Node.js):
├── JS parsing: 100-200ms
├── Node.js startup: 500-1000ms
├── Single-threaded: N files × per-file time
└── Total: 2-10s for typical project

Oxlint (Rust):
├── Rust parsing: 10-30ms
├── Binary startup: 1-5ms
├── Multi-threaded: Files processed in parallel
└── Total: 100-500ms for same project

Speedup: 5-50x (more rules = bigger difference)
```

### Limitations vs ESLint

**Rules NOT in oxlint:**
```
~5% of ESLint rules are not yet implemented:
- Some framework-specific rules (React, Vue)
- Custom plugin rules (requires plugin system)
- Some formatting rules (use prettier instead)

Solution: Run ESLint for missing rules as fallback
```

**Ideal for:**
- Pure JavaScript/TypeScript linting
- Core language rules (no/unused-vars, no-console, etc.)
- Performance-sensitive environments
- Large monorepos

**Less ideal for:**
- Projects heavily reliant on custom plugins
- Framework-heavy rules (but improving)
- Teams needing bleeding-edge rule additions

---

## 🔧 Installation & Setup

### Step 1: Installation

```bash
# Install oxlint binary
brew install oxlint

# Or via cargo
cargo install oxlint --locked

# Or via npm (ironically)
npm install -g @oxlint/cli

# Verify
oxlint --version
# Expected: oxlint X.X.X
```

### Step 2: Config Migration

#### Find Existing ESLint Config

```bash
# Common locations
find . -maxdepth 3 \( \
  -name ".eslintrc" \
  -o -name ".eslintrc.js" \
  -o -name ".eslintrc.json" \
  -o -name ".eslintrc.yaml" \
  -o -name "eslint.config.js" \
  -o -name "eslint.config.mjs" \
\) 2>/dev/null
```

#### Typical ESLint Config Example

```json
// .eslintrc.json
{
  "root": true,
  "env": {
    "browser": true,
    "node": true,
    "es2021": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "eqeqeq": "error"
  },
  "ignorePatterns": [
    "node_modules",
    "dist",
    "build"
  ]
}
```

#### Migrate to Oxlint Config

```json
// oxlint.json (new)
{
  "extends": ["oxlint/recommended"],
  "env": {
    "browser": true,
    "node": true,
    "es2021": true
  },
  "globals": {
    "process": "readonly"
  },
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "eqeqeq": "error"
  },
  "ignorePatterns": [
    "node_modules",
    "dist",
    "build"
  ]
}
```

### Step 3: Config Mapping Guide

**ESLint Config → Oxlint Equivalent:**

| ESLint | Oxlint | Notes |
|--------|--------|-------|
| `extends: ["eslint:recommended"]` | `extends: ["oxlint/recommended"]` | Built-in recommended rules |
| `parser: "@typescript-eslint/parser"` | Auto-detected (no config needed) | Oxlint auto-detects .ts/.tsx |
| `parserOptions.project` | Not needed (auto-analyzed) | Oxlint infers from tsconfig.json |
| `plugins: ["@typescript-eslint"]` | Not needed (built-in) | TS rules included by default |
| `rules: { "rule": "error" }` | `rules: { "rule": "error" }` | Same format |
| `ignorePatterns` | `ignorePatterns` | Same format |
| `env: { "browser": true }` | `env: { "browser": true }` | Mostly compatible |

**ESLint Rules → Oxlint Equivalents:**

```json
{
  "no-console": "warn",                    // ✅ Supported
  "no-unused-vars": "error",              // ✅ Supported
  "no-var": "error",                      // ✅ Supported
  "prefer-const": "warn",                 // ✅ Supported
  "eqeqeq": "error",                      // ✅ Supported
  "no-implicit-coercion": "error",        // ✅ Supported
  "no-empty": "warn",                     // ✅ Supported
  "@typescript-eslint/no-unused-vars": "error",  // ✅ Built-in
  "@typescript-eslint/explicit-function-return-types": "warn",  // ⚠️ Not in oxlint
  "react/prop-types": "error",            // ❌ Requires plugin (fallback to ESLint)
  "import/no-unresolved": "error",        // ⚠️ Limited support in oxlint
}
```

### Step 4: Advanced Configuration

#### TypeScript Support

```json
// oxlint.json with TypeScript
{
  "extends": ["oxlint/recommended"],
  "settings": {
    "jsx-a11y/components": ["Component"]
  },
  "rules": {
    "typescript/no-explicit-any": "error",
    "typescript/no-unused-vars": "error"
  }
}
```

#### Path Aliases (tsconfig.json integration)

Oxlint auto-reads `tsconfig.json` for:
- Path aliases (`paths: { "@/*": ["src/*"] }`)
- Module resolution
- Lib includes

**No additional config needed!**

#### Ignoring Files

```json
// oxlint.json
{
  "ignorePatterns": [
    "node_modules",
    "dist",
    "build",
    "coverage",
    "*.config.js",
    "**/*.d.ts"
  ]
}
```

#### Environment Variables

```json
{
  "globals": {
    "process": "readonly",
    "Buffer": "readonly",
    "__DEV__": "readonly"
  }
}
```

---

## 🧪 Side-by-Side Testing

### Phase 4.1: Parallel Execution

Run both ESLint and Oxlint to compare results:

```bash
#!/bin/bash
# test-both-linters.sh

echo "=== ESLint ==="
eslint . --format=json > eslint-results.json 2>&1
ESLINT_EXIT=$?

echo "=== Oxlint ==="
oxlint . --format json > oxlint-results.json 2>&1
OXLINT_EXIT=$?

echo "ESLint exit code: $ESLINT_EXIT"
echo "Oxlint exit code: $OXLINT_EXIT"

# Compare results
jq '.errors' eslint-results.json | wc -l
jq '.[].errors' oxlint-results.json | wc -l

# Report differences
echo "=== Detailed Comparison ==="
# ... diff logic
```

### Phase 4.2: Validate Equivalence

Ensure oxlint catches all errors that ESLint does:

```bash
#!/bin/bash
# validate-linter-equivalence.sh

# ESLint errors
ESLINT_ERRORS=$(eslint . --format=json 2>/dev/null | \
  jq -r '.[] | select(.messages | length > 0) | .filePath' | \
  sort | uniq)

# Oxlint errors
OXLINT_ERRORS=$(oxlint . --format json 2>/dev/null | \
  jq -r '.[] | select(.errors | length > 0) | .file' | \
  sort | uniq)

# Compare
echo "Files with ESLint errors: $(echo "$ESLINT_ERRORS" | wc -l)"
echo "Files with Oxlint errors: $(echo "$OXLINT_ERRORS" | wc -l)"

# Find missing errors in oxlint
comm -23 <(echo "$ESLINT_ERRORS") <(echo "$OXLINT_ERRORS") > \
  files-only-eslint-detected.txt

if [ -s files-only-eslint-detected.txt ]; then
  echo "⚠️ Oxlint missed errors in these files:"
  cat files-only-eslint-detected.txt
  echo "These may be rules not supported by oxlint"
else
  echo "✅ Oxlint equivalent to ESLint"
fi
```

### Phase 4.3: Rule Coverage Analysis

```bash
#!/bin/bash
# analyze-rule-coverage.sh

# Extract rules from ESLint config
ESLINT_RULES=$(cat .eslintrc.json | \
  jq -r '.rules | keys | .[]' | \
  sort | uniq)

# Check oxlint support for each rule
echo "Rule Coverage Analysis:"
echo "======================="

SUPPORTED=0
UNSUPPORTED=0

for rule in $ESLINT_RULES; do
  if oxlint --rules | grep -q "^$rule$"; then
    echo "✅ $rule"
    ((SUPPORTED++))
  else
    echo "⚠️  $rule (may require ESLint fallback)"
    ((UNSUPPORTED++))
  fi
done

echo ""
echo "Summary:"
echo "Supported: $SUPPORTED"
echo "Unsupported: $UNSUPPORTED"
echo "Coverage: $(echo "scale=1; $SUPPORTED * 100 / ($SUPPORTED + $UNSUPPORTED)" | bc)%"
```

---

## 📊 Performance Benchmarking

### Benchmark Script

```bash
#!/bin/bash
# benchmark-linters.sh

PROJECT_SIZE=$(find . -name "*.js" -o -name "*.ts" | wc -l)
echo "Linting $PROJECT_SIZE files..."

# ESLint benchmark
echo -n "ESLint: "
time eslint . --format=json > /dev/null 2>&1

# Oxlint benchmark
echo -n "Oxlint: "
time oxlint . --format json > /dev/null 2>&1

# Calculate speedup
# ... calculation logic
```

### Expected Results

```
Linting 1000 TypeScript files:

ESLint: 8.5s
Oxlint: 0.3s

Speedup: 28x
```

---

## 🔄 Fallback Strategy

For rules **not supported by oxlint**, use hybrid approach:

```bash
#!/bin/bash
# hooks/lib/lint-with-fallback.sh

lint_typescript() {
  local files="$1"

  # Run oxlint (fast)
  oxlint $files --format json > oxlint-results.json

  # For unsupported rules, run ESLint
  # (only on files with issues, optional)
  if [ "$EXHAUSTIVE_LINT" = "true" ]; then
    eslint $files --format json > eslint-results.json
    # Merge results
    jq -s add oxlint-results.json eslint-results.json
  else
    cat oxlint-results.json
  fi
}
```

---

## 🚀 Phase 4 Implementation

### Implementation Steps

#### Step 1: Create oxlint Config (1 hour)

- [ ] Analyze current .eslintrc config
- [ ] Create oxlint.json (same rules)
- [ ] Test with sample files
- [ ] Validate rule coverage >95%

#### Step 2: Update Hooks (1 hour)

- [ ] Update quality-gate.sh to use oxlint
- [ ] Add fallback to ESLint (optional)
- [ ] Test both linters side-by-side
- [ ] Verify no new violations

#### Step 3: Update CI/CD (1 hour)

- [ ] Update .github/workflows/lint.yml
- [ ] Replace `eslint` with `oxlint`
- [ ] Update timeout expectations (much faster)
- [ ] Test in CI pipeline

#### Step 4: Documentation (1 hour)

- [ ] Update LINTING.md
- [ ] Document oxlint config
- [ ] Add troubleshooting guide
- [ ] Record performance improvement

#### Step 5: Rollout & Testing (2 hours)

- [ ] Run full test suite
- [ ] Benchmark improvement
- [ ] Test fallback to ESLint
- [ ] Team review & feedback

### Success Criteria

- ✅ Oxlint 5-50x faster than ESLint
- ✅ Zero new rule violations
- ✅ All existing errors caught
- ✅ CI/CD pipelines faster
- ✅ Team trained on oxlint usage

---

## 📖 Example Oxlint Config

### Minimal Config

```json
// oxlint.json
{
  "extends": ["oxlint/recommended"],
  "rules": {
    "no-console": "off"
  }
}
```

### Comprehensive Config

```json
// oxlint.json (for complex project)
{
  "extends": ["oxlint/recommended"],
  "env": {
    "browser": true,
    "node": true,
    "es2021": true,
    "jest": true
  },
  "globals": {
    "process": "readonly",
    "Buffer": "readonly",
    "describe": "readonly",
    "it": "readonly",
    "expect": "readonly",
    "__DEV__": "readonly"
  },
  "settings": {
    "import/resolver": {
      "typescript": {
        "alwaysTryTypes": true
      }
    }
  },
  "rules": {
    // Possible errors
    "no-console": "warn",
    "no-debugger": "warn",
    "no-constant-condition": "warn",

    // Variables
    "no-unused-vars": ["error", {
      "argsIgnorePattern": "^_",
      "varsIgnorePattern": "^_"
    }],
    "no-undef": "error",

    // Stylistic
    "eqeqeq": ["error", "always"],
    "no-var": "error",
    "prefer-const": "warn",

    // TypeScript specific (if using TS)
    "typescript/explicit-function-return-types": "off",
    "typescript/no-explicit-any": "warn",
    "typescript/no-unused-vars": "error"
  },
  "ignorePatterns": [
    "node_modules/**",
    "dist/**",
    "build/**",
    "coverage/**",
    "*.config.js",
    "**/*.d.ts",
    ".next/**",
    "out/**"
  ]
}
```

---

## 🐛 Troubleshooting

### Issue: Oxlint doesn't find some files

**Solution:** Check ignorePatterns in oxlint.json
```bash
oxlint . --show-ignored
```

### Issue: TypeScript errors not detected

**Solution:** Ensure tsconfig.json is in project root
```bash
oxlint . --debug
```

### Issue: Config not being read

**Solution:** Try explicit config path
```bash
oxlint . --config oxlint.json
```

### Issue: Certain rules missing

**Solution:** Check rule support
```bash
oxlint --help rules
# or fallback to ESLint for that rule
```

---

## 📚 Resources

### Official
- **Oxlint GitHub:** https://github.com/oxc-project/oxc
- **Rule Documentation:** https://oxc.rs/docs/guide/rules
- **Config Guide:** https://oxc.rs/docs/guide/configuration

### Related
- **ESLint to Oxlint Migration:** Common patterns documented in oxc repo
- **Performance Comparisons:** Real-world benchmarks in OXC discussions
- **Rule Coverage Matrix:** Community-maintained compatibility list

---

## 🎯 Next Steps After Rollout

### Immediate (Week 4+)
- Monitor linting performance improvement
- Collect team feedback
- Fine-tune config based on real usage

### Short-term (Month 2)
- Evaluate new oxlint rules (actively added)
- Consider deprecating ESLint fallback (if not needed)
- Update team documentation

### Long-term (Month 3+)
- Migrate other linting infrastructure (TypeScript check, etc.)
- Evaluate other Rust tools (formatter, bundler, etc.)
- Share learnings with broader team

---

**Version:** 1.0
**Created:** 2026-02-15
**Status:** Ready for Phase 4 Implementation

