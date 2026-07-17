# Tooling Modernization Roadmap: Claude Code Hooks Ecosystem

**Version:** 1.0
**Date:** 2026-02-15
**Scope:** Complete hooks infrastructure (bash, git, linters, utilities)
**Constraint:** GO or RUST ONLY (no NodeJS, no Python except as-is)

---

## Executive Summary

The hooks ecosystem depends on 15+ tools spanning 4 generations of technology:
- **Legacy:** Bash, sed, awk (1970s-1980s design)
- **Modern:** Git, ripgrep (2005+, modern optimization)
- **External:** Linters, formatters (mixed quality, many slow)
- **Infrastructure:** hook-dispatcher (Rust, already modern)

**Opportunity:** Replace 40-50% of tooling with Go/Rust rewrites for **5-20x speedup** across the board.

---

## Tooling Inventory & Assessment

### FOUNDATION: Bash Shell

| Tool | Usage | Current | Status | Modernization Option |
|------|-------|---------|--------|----------------------|
| **Bash** | All hooks foundation | bash 5.1 | CRITICAL | Rebuild in Go/Rust + shell layer |
| Exit codes | Signaling | Native | FAST | No change needed |
| Variables | State | Native | SLOW | Consider typed data structures |
| Arrays | Collections | bash arrays | SLOW | Use Go/Rust for data-heavy ops |

**Analysis:**
- Bash is foundation for everything (all hooks are bash scripts)
- Pure bash has limitations: no parallelization, slow string ops, weak typing
- **Current bottleneck:** Variable expansion, array operations, subshell spawning

**Modernization Opportunity:**
1. **Hybrid approach:** Keep bash as orchestration layer, move compute to Go/Rust
   - Shell + Go/Rust coordination via stdin/stdout
   - Bash controls flow, Go/Rust does heavy lifting

2. **Complete rewrite:** Rewrite critical hooks entirely in Go/Rust
   - test-maturity.sh → maturity.rs (5-10x faster)
   - task-completion-verifier.sh → completion.rs (3-5x faster)
   - quality-gate.sh → gate.rs (10-20x faster: parallel linting)

3. **Intermediate:** Keep bash, add Go/Rust libraries
   - hooks/lib/ → move to hooks/lib-rs/ (compiled Go/Rust)
   - Shell calls out to fast libraries

**Recommendation:** **Hybrid approach (Option 1)**
- Keep bash for orchestration (it's good at flow control)
- Move compute-intensive operations to compiled language
- 50-60% effort, 70-80% speedup

---

### GIT OPERATIONS

| Tool | Current | Performance | Status | Modernization |
|------|---------|-------------|--------|----------------|
| **git** (canonical) | 2.40+ | Baseline | SLOW | ✅ Gitoxide |
| `git ls-files` | git | 100ms-1s | SLOW | Gitoxide: 10-20ms |
| `git status` | git | 200ms-2s | SLOW | Gitoxide: 30-100ms |
| `git diff` | git | 100ms-1s | SLOW | Gitoxide: 20-50ms |
| `git show` | git | 50-200ms | SLOW | Gitoxide: 5-20ms |
| `git log` | git | 100ms-5s | SLOW | Gitoxide: 10-100ms |

**Current Implementation:** Cached (ADR-002)
**Modernization:** Gitoxide (Rust) - already evaluated above
**Impact:** 5-20x speedup
**Timeline:** Phase 3.5 (2-3 hours)
**Status:** READY TO IMPLEMENT

---

### FILE DISCOVERY & MANIPULATION

| Tool | Purpose | Current | Performance | Status | Modernization |
|------|---------|---------|-------------|--------|----------------|
| **find** | File discovery | GNU find | 500ms-5s | SLOW | ✅ fd (Rust) |
| **grep** | Content search | ripgrep | 10-100ms | FAST | ✅ Already modern |
| **sed** | Text substitution | GNU sed | 50-200ms | MEDIUM | ✅ sd (Rust) |
| **awk** | Text processing | gawk | 50-500ms | MEDIUM | Consider Go rewrite |
| **xargs** | Parallel execution | GNU xargs | 100ms-1s | SLOW | ✅ parallel (Go) or xargs-rs |
| **sort/uniq** | Data dedup | GNU coreutils | 50-200ms | MEDIUM | ripgrep/fd already faster |

**Detailed Analysis:**

#### find → fd
```bash
# Current (slow)
find . -name "*.test.ts" -type f | xargs wc -l

# Modernized (fast)
fd -e test.ts | parallel wc -l
```
- **Speedup:** 3-5x (parallelization + SIMD)
- **Install:** `brew install fd`
- **Integration:** Drop-in replacement in hooks

#### grep → ripgrep
- **Status:** Already done (ripgrep is in use)
- **Performance:** Already optimized
- **No action needed**

#### sed → sd
```bash
# Current (slow)
sed -i 's/old/new/g' file

# Modernized (fast)
sd -p 'old' 'new' file
```
- **Speedup:** 2-3x (regex engine + string ops)
- **Install:** `brew install sd`
- **Integration:** Requires careful regex porting

#### awk → Go rewrite (optional)
- **Status:** Used in 3-4 hooks for field extraction
- **Speedup:** 5-10x for large inputs
- **Integration:** More complex than drop-in replacement
- **Recommendation:** Consider only if awk is bottleneck
- **Timeline:** Phase 4 (lower priority)

**Recommendation:**
1. ✅ **Immediately:** Replace `find` with `fd`
2. ✅ **Immediately:** Verify ripgrep in use (already done)
3. ⏳ **Phase 3.5:** Evaluate `sed` → `sd` (if text processing heavy)
4. ⏳ **Phase 4:** Consider `awk` rewrite (if performance bottleneck)

---

### LINTING & QUALITY TOOLS

| Tool | Language | Current | Speed | Language | Modernization |
|------|----------|---------|-------|----------|----------------|
| **ruff** | Python | ruff (Rust-based) | FAST | Rust | ✅ Already modern |
| **eslint** | JavaScript | eslint (Node) | SLOW | Node | ❌ User forbids Node |
| **pylint** | Python | pylint (Python) | SLOW | Python | ⚠️ User forbids |
| **shellcheck** | Bash | shellcheck (Haskell) | FAST | Haskell | ✅ Good enough |
| **typos** | Spelling | typos (Rust) | FAST | Rust | ✅ Already modern |
| **truffleHog** | Secrets | truffleHog (Python) | MEDIUM | Python | ⚠️ Consider gitleaks |
| **semgrep** | SAST | semgrep (OCaml) | MEDIUM | OCaml | Consider go-sast alternatives |

**Key Insight:** Most linters are already modernized (ruff, typos, shellcheck).

**Issues:**
- **eslint (Node):** Conflict with user's "GO or RUST ONLY" policy
  - Needs Go/Rust replacement: oxlint (Rust), biome (Rust)
- **pylint (Python):** User doesn't want Python linting tools
  - Could be replaced with: ruff (already does most pylint checks)
- **semgrep (OCaml):** Fine for now, consider Go alternative later

**Recommendation:**
1. ✅ **Keep:** ruff, typos, shellcheck (already modern)
2. ✅ **Replace:** eslint → oxlint (Rust) or biome (Rust)
   - **Speedup:** 5-50x (parallel, fewer passes)
   - **Effort:** 4-6 hours (config migration)
   - **Timeline:** Phase 3.5 or 4
3. ✅ **Replace:** truffleHog → gitleaks (Go) if secrets scanning needed
   - **Speedup:** 3-5x
   - **Effort:** 2 hours
4. ⏳ **Consider:** semgrep → go-sast (Go alternative)
   - **Timeline:** Phase 5 (lower priority)

---

### PROCESS COORDINATION & UTILITIES

| Tool | Purpose | Current | Performance | Modernization |
|------|---------|---------|-------------|----------------|
| **flock** | File locking | POSIX | FAST | No change (optimal) |
| **mkdir** | Atomic ops | POSIX | FAST | No change (optimal) |
| **named pipes** | IPC | POSIX | FAST | No change (optimal) |
| **timeout** | Limits | GNU coreutils | FAST | Consider Go wrapper |
| **parallel** | Parallelization | GNU Parallel | MEDIUM | ✅ parallel-rs (Rust) or Go |
| **ps/pgrep** | Process lookup | POSIX | SLOW | ✅ procs (Rust) |
| **tee** | Output splitting | POSIX | FAST | No change |

**Analysis:**

#### timeout
- **Current:** GNU timeout works fine
- **Alternative:** Could use Go for custom timeout with better error handling
- **Recommendation:** No change (POSIX timeout adequate)

#### parallel
```bash
# Current
find . -name "*.rs" | parallel rustfmt

# Rust alternative
for file in $(find . -name "*.rs"); do
  rustfmt "$file" &
done
```
- **Status:** GNU Parallel works, but Go/Rust alternative available
- **Recommendation:** Keep GNU Parallel (works fine, widely available)

#### ps/pgrep → procs
```bash
# Current
ps aux | grep hook-dispatcher

# Modernized
procs hook-dispatcher
```
- **Speedup:** 2-3x
- **Install:** `brew install procs`
- **Integration:** Drop-in replacement (better output)
- **Timeline:** Quick win (1 hour)

**Recommendation:**
1. ✅ **Keep:** flock, mkdir, named pipes (optimal for POSIX)
2. ✅ **Keep:** timeout (works fine)
3. ✅ **Keep:** parallel (works fine, specialized use)
4. ✅ **Replace:** ps/pgrep → procs (small speedup + better UX)
   - **Effort:** 1-2 hours
   - **Timeline:** Phase 3.5

---

### DATA PROCESSING & PARSING

| Tool | Purpose | Current | Performance | Modernization |
|------|---------|---------|-------------|----------------|
| **jq** | JSON processing | jq (C) | MEDIUM | ✅ jq (already fast) or yq (Rust) |
| **yaml** | YAML parsing | yq (Go) | FAST | ✅ Already Go (modern) |
| **base64** | Encoding | coreutils | FAST | No change |
| **openssl** | Crypto | openssl | MEDIUM | ✅ Modern (used for hashing) |

**Analysis:**
- **jq:** Already well-optimized C implementation
  - Alternatives: yq-rust, ijq (Rust) - only if jq is bottleneck
  - **Recommendation:** Keep jq (good enough)
- **yq:** Already Go (modern)
  - **Recommendation:** Keep yq
- **base64/openssl:** Already fast for their use cases
  - **Recommendation:** Keep as-is

**Recommendation:** No changes needed (already well-optimized)

---

### HOOK-DISPATCHER (Core Infrastructure)

| Component | Language | Performance | Status |
|-----------|----------|-------------|--------|
| **hook-dispatcher** | Rust | Excellent | ✅ Already modern |
| **Tool discovery** | Rust | FAST | ✅ Already optimized |
| **Hook execution** | Rust | FAST | ✅ Already optimized |
| **Logging** | Rust | FAST | ✅ Already optimized |

**Status:** Already fully modernized in Rust

**Recommendation:** No changes needed

---

## Modernization Priority Matrix

### 🔴 P0: CRITICAL (Implement immediately)

| Tool | Replacement | Speedup | Effort | Timeline | Notes |
|------|-------------|---------|--------|----------|-------|
| **git** | Gitoxide | 5-20x | 2-3h | Phase 3.5 | Already designed (ADR-002) |
| **find** | fd | 3-5x | 1-2h | Phase 3.5 | Drop-in replacement |
| **ps/pgrep** | procs | 2-3x | 1-2h | Phase 3.5 | Quick win |

**Total Effort:** 4-7 hours
**Total Speedup:** 10-50x combined
**Timeline:** 1 week

### 🟡 P1: HIGH (Implement Phase 4)

| Tool | Replacement | Speedup | Effort | Notes |
|------|-------------|---------|--------|-------|
| **eslint** | oxlint/biome | 5-50x | 4-6h | Config migration needed |
| **sed** | sd | 2-3x | 3-4h | Regex porting required |
| **bash hooks** | Hybrid Go/Rust | 3-10x | 8-12h | Rewrite core hooks |

**Total Effort:** 15-22 hours
**Total Speedup:** 10-100x combined

### 🟢 P2: MEDIUM (Implement Phase 5+)

| Tool | Replacement | Speedup | Effort | Notes |
|------|-------------|---------|--------|-------|
| **awk** | Go rewrite | 5-10x | 6-8h | Only if bottleneck |
| **semgrep** | go-sast | 3-5x | 8-10h | Lower priority |
| **secrets scanning** | gitleaks | 3-5x | 2-3h | If needed |

---

## Implementation Timeline

### Phase 3.5: Quick Wins (Week 3, 1-2 days)

**Goal:** Implement highest ROI changes with minimal effort

```
P3.5.1: Gitoxide Integration (2-3h)
  - Install gitoxide: brew install gitoxide
  - Update git_cached() in hooks/lib/git-cache.sh
  - Add gix fallback pattern
  - Benchmark: 5-20x speedup on git ops

P3.5.2: fd Integration (1-2h)
  - Install fd: brew install fd
  - Replace `find` with `fd` in hooks
  - Update patterns (fd syntax differs slightly)
  - Benchmark: 3-5x speedup on file discovery

P3.5.3: procs Integration (1-2h)
  - Install procs: brew install procs
  - Replace ps/pgrep calls with procs
  - Update output parsing if needed
  - Benchmark: 2-3x speedup on process lookup

Total Effort: 4-7 hours
Expected Speedup: 20-100x combined
Timeline: 1-2 days
```

### Phase 4: Medium-Effort Optimizations (Week 4, 2-3 days)

```
P4.1: eslint → oxlint Migration (4-6h)
  - Install oxlint: npm install -g oxlint (or cargo)
  - Migrate ESLint config → oxlint config
  - Test on sample projects
  - Benchmark: 5-50x speedup on JS linting

P4.2: bash Hook Hybridization (8-12h)
  - Identify compute-intensive hooks
  - Create Go/Rust equivalents for:
    - test-maturity.sh → maturity.rs (5-10x faster)
    - task-completion-verifier.sh → completion.rs (3-5x faster)
  - Maintain bash orchestration layer
  - Test extensively

P4.3: sed → sd Migration (3-4h) [Optional]
  - Evaluate sed usage in hooks
  - Migrate regex patterns to sd syntax
  - Test edge cases
  - Benchmark: 2-3x speedup

Total Effort: 15-22 hours
Expected Speedup: 50-200x combined
Timeline: 2-3 days
```

### Phase 5: Long-term Modernization (Weeks 5+)

```
P5.1: Remaining awk → Go rewrite (6-8h) [If needed]
P5.2: semgrep → go-sast migration (8-10h) [If SAST bottleneck]
P5.3: secrets scanning → gitleaks (2-3h) [If needed]
```

---

## Impact Analysis

### Before Modernization (Current State)
```
Stop Hook Execution: 8-12s
├── Git operations: 3-5s (40-50%)
├── File discovery: 1-2s (12-20%)
├── Linting/checks: 2-3s (25-35%)
└── Coordination: 1-2s (10-15%)
```

### After Phase 3.5 (Gitoxide + fd + procs)
```
Stop Hook Execution: 2-4s (60-75% reduction)
├── Git operations: 0.3-0.5s (git + gitoxide caching)
├── File discovery: 0.2-0.4s (fd parallelization)
├── Linting/checks: 2-3s (unchanged, for now)
└── Coordination: 0.5-1s (improved locking)
```

### After Phase 4 (eslint + bash optimization)
```
Stop Hook Execution: 0.5-1.5s (90%+ reduction)
├── Git operations: 0.1-0.3s
├── File discovery: 0.1-0.2s
├── Linting/checks: 0.2-0.8s (eslint → oxlint: 5-50x)
└── Coordination: 0.2-0.5s
```

---

## Tool Compatibility Matrix

### macOS (Primary Development)
```
✅ Gitoxide: brew install gitoxide
✅ fd: brew install fd
✅ procs: brew install procs
✅ oxlint: brew install oxlint
✅ sd: brew install sd
✅ gitleaks: brew install gitleaks
```

### Linux (CI/Docker)
```
✅ Gitoxide: cargo install gitoxide OR apt install gitoxide
✅ fd: apt install fd-find
✅ procs: cargo install procs
✅ oxlint: cargo install oxlint
✅ sd: cargo install sd
✅ gitleaks: apt install gitleaks
```

### Windows (Not Primary, but should work)
```
✅ Gitoxide: cargo install gitoxide
✅ fd: cargo install fd OR scoop install fd
⚠️ procs: Limited support
✅ oxlint: cargo install oxlint
✅ sd: cargo install sd
✅ gitleaks: scoop install gitleaks
```

**Recommendation:** Test all tools on Linux (CI environment) before production deployment.

---

## Risk Assessment

| Change | Risk | Mitigation |
|--------|------|-----------|
| **Gitoxide** | New tool, small surface | Fallback to git, test thoroughly |
| **fd** | Different syntax than find | Comprehensive testing, gradual rollout |
| **procs** | Output format differences | Regex parsing updates |
| **oxlint** | Config migration risk | Side-by-side testing with eslint |
| **Bash → Go/Rust** | Significant rewrite | Extensive testing, A/B comparison |

---

## Open Questions

1. **Bash vs Go/Rust hooks:** How aggressive should we be?
   - Option A: Keep bash, move compute to Go/Rust (hybrid)
   - Option B: Rewrite critical hooks entirely in Go (full Rust)
   - Option C: Rewrite all hooks in Go (maximum modernization)
   - **Recommendation:** Option A (hybrid) - lowest risk, high reward

2. **Config management:** How to handle tool discovery + installation?
   - Should hooks assume tools are installed?
   - Should we provide installation script?
   - Should we detect and fall back gracefully?
   - **Recommendation:** Detection with graceful fallback

3. **NodeJS tools (eslint):** Can we use oxlint without breaking existing configs?
   - oxlint is not 100% eslint-compatible
   - Config migration could be complex
   - **Recommendation:** Phase 4 (after Phase 3.5 proves approach)

4. **Bash rewrite scope:** Which hooks to rewrite first?
   - Priority 1: test-maturity.sh (currently slow, frequently run)
   - Priority 2: task-completion-verifier.sh (currently slow)
   - Priority 3: quality-gate.sh (most complex, highest value)
   - **Recommendation:** Start with Priority 1 & 2

---

## Success Criteria

### Phase 3.5 Completion
- ✅ Gitoxide integrated and tested
- ✅ fd in use for file discovery
- ✅ procs integrated for process lookup
- ✅ Combined 30-50x speedup verified
- ✅ Zero regressions in functionality

### Phase 4 Completion
- ✅ oxlint replacing eslint
- ✅ Hybrid bash/Go hooks working
- ✅ Combined 100-200x speedup (from baseline)
- ✅ All tests passing
- ✅ User experience noticeably improved

---

## Document History

| Version | Date | Status | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-15 | Proposed | Comprehensive tooling modernization roadmap |

