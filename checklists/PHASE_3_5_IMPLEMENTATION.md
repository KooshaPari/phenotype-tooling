# Phase 3.5 Implementation Checklist: Quick Wins Modernization

**Timeline:** 1-2 days
**Effort:** 4-7 hours
**Expected Speedup:** 30-100x combined
**Risk Level:** LOW (fallback-friendly, no breaking changes)

---

## 🎯 Objective

Implement three high-ROI tool replacements with minimal code changes and maximum performance gain:
- **Gitoxide** (git 5-20x faster)
- **fd** (find 3-5x faster)
- **procs** (ps/pgrep 2-3x faster)

All changes are **backwards compatible** with graceful fallback to original tools.

---

## 📋 Pre-Implementation Checklist

### System Verification
- [ ] macOS or Linux system (Windows not tested)
- [ ] Homebrew installed (for tool installation)
- [ ] Cargo installed (fallback for installation)
- [ ] Test repository available (for git benchmarking)
- [ ] At least 500MB free disk space (for new tools)

### Baseline Measurement
- [ ] Record current hook execution time
  ```bash
  time make dev-hooks Stop
  # Expected: 8-12 seconds
  ```
- [ ] Profile git operations
  ```bash
  time git ls-files > /dev/null
  time git status --short > /dev/null
  time git diff --name-only HEAD > /dev/null
  # Expected: 100ms-1s each
  ```
- [ ] Check tool availability
  ```bash
  command -v git status find grep ps
  ```

### Code Review
- [ ] Read hooks/lib/common.sh (understand git usage)
- [ ] Identify all `git` calls in hooks/
- [ ] Identify all `find` calls in hooks/
- [ ] Identify all `ps`/`pgrep` calls in hooks/
- [ ] Document fallback strategy (graceful degradation required)

---

## 🚀 Task 1: Gitoxide Integration (2-3 hours)

### T1.1: Installation

- [ ] Install gitoxide
  ```bash
  # macOS
  brew install gitoxide

  # Linux (Ubuntu/Debian)
  sudo apt-get install -y gitoxide

  # Linux (other, via cargo)
  cargo install gitoxide --locked

  # Verify
  gix --version
  # Expected: gix version X.X.X
  ```

- [ ] Test gitoxide on test repo
  ```bash
  cd /path/to/test/repo
  time gix ls-files > /dev/null
  time gix status --short > /dev/null
  time gix diff --name-only HEAD > /dev/null
  # Expected: <100ms each (compare to git results)
  ```

- [ ] Compare performance
  ```bash
  echo "=== GIT ==="
  time git ls-files > /dev/null
  echo "=== GITOXIDE ==="
  time gix ls-files > /dev/null
  # Document speedup ratio
  ```

### T1.2: Create git_cached() Wrapper

- [ ] Create/update hooks/lib/git-cache.sh
  ```bash
  #!/bin/bash
  # Git operation wrapper with gitoxide fallback + caching

  # Cache directory
  GIT_CACHE_DIR="${CLAUDE_HOME:-.}/.git-cache"
  GIT_CACHE_TTL=60  # seconds

  git_cached() {
    local cmd="$1"
    local args=("${@:2}")
    local cache_key="git-${cmd}-${args[*]}"
    cache_key="${cache_key// /-}"  # Sanitize

    # Check cache
    if check_cache "$cache_key" "$GIT_CACHE_TTL"; then
      return
    fi

    # Try gitoxide
    if command -v gix >/dev/null 2>&1; then
      if timeout 3 gix "$cmd" "${args[@]}" 2>/dev/null; then
        cache_result "$cache_key"
        return
      fi
    fi

    # Fallback to git
    timeout 5 git "$cmd" "${args[@]}"
  }

  check_cache() { ... }  # See implementation
  cache_result() { ... } # See implementation
  ```

- [ ] Implement cache_check() function
  - Check ~/.claude/.git-cache/ for key
  - Check mtime (60s TTL)
  - Return cached output if valid
  - Remove stale cache

- [ ] Implement cache_result() function
  - Store command output to cache file
  - Set mtime to now
  - Clean old cache entries (>10 entries or >24h old)

- [ ] Create ~/.claude/.git-cache/ directory
  ```bash
  mkdir -p ~/.claude/.git-cache
  chmod 700 ~/.claude/.git-cache
  ```

### T1.3: Update hooks to use git_cached()

- [ ] Audit hooks/lib/common.sh for git calls
  ```bash
  grep -n "git " hooks/lib/common.sh | head -20
  ```

- [ ] Replace with git_cached() wrapper
  - `git diff --name-only HEAD` → `git_cached diff --name-only HEAD`
  - `git ls-files` → `git_cached ls-files`
  - `git status --short` → `git_cached status --short`
  - Document each change

- [ ] Update hook_should_run() function
  ```bash
  # Before
  changed_files="$(timeout 5 git diff --name-only HEAD 2>/dev/null || true)"

  # After
  changed_files="$(git_cached diff --name-only HEAD || true)"
  ```

- [ ] Update remaining hooks
  - [ ] test-maturity.sh
  - [ ] task-completion-verifier.sh
  - [ ] quality-gate.sh
  - [ ] spec-preflight.sh (if it calls git)
  - [ ] spec-verifier.sh (if it calls git)
  - [ ] other hooks with git calls

### T1.4: Testing & Validation

- [ ] Run test suite
  ```bash
  make test
  # Expect: All tests pass
  ```

- [ ] Test with slow repo
  ```bash
  # Create large test repo
  mkdir /tmp/large-repo && cd /tmp/large-repo
  git init
  touch $(seq 1 10000 | xargs -I {} echo "file-{}.txt")
  git add .
  git commit -m "Large repo"

  # Benchmark
  time hook_should_run test-maturity.sh
  # Expected: <100ms with cache hit
  ```

- [ ] Verify fallback works
  ```bash
  # Temporarily rename gitoxide
  mv $(which gix) /tmp/gix-backup

  # Run hooks - should use git
  make test

  # Restore gitoxide
  mv /tmp/gix-backup $(dirname $(which git))/gix
  ```

- [ ] Measure latency improvement
  ```bash
  time make dev-hooks Stop
  # Expected: 25-40% reduction from baseline
  ```

- [ ] Document baseline vs new performance
  - Git operations: XXms → XXms (YY% improvement)
  - Overall Stop hook: XXs → XXs (YY% improvement)

### T1.5: Commit & Document

- [ ] Create git commit
  ```bash
  git add hooks/lib/git-cache.sh hooks/lib/common.sh hooks/*.sh
  git commit -m "Phase 3.5: Integrate gitoxide for 5-20x git speedup

  - Add git_cached() wrapper with gitoxide support
  - Fallback to canonical git if gitoxide unavailable
  - Add file-based caching (60s TTL)
  - Measured 5-20x speedup on git operations
  - Zero breaking changes, fully backwards compatible"
  ```

- [ ] Update hooks/PERFORMANCE.md
  ```markdown
  ## Git Operations (Phase 3.5)

  | Operation | Before | After | Improvement |
  |-----------|--------|-------|-------------|
  | git ls-files | XXms | XXms | YY% |
  | git status | XXms | XXms | YY% |
  | git diff | XXms | XXms | YY% |

  Implementation: gitoxide + file-based caching
  ```

---

## 🔍 Task 2: fd Integration (1-2 hours)

### T2.1: Installation

- [ ] Install fd
  ```bash
  # macOS
  brew install fd

  # Linux
  sudo apt-get install fd-find

  # Verify
  fd --version
  # Expected: fd X.X.X
  ```

- [ ] Test fd on test repo
  ```bash
  time fd -e test.ts . > /dev/null
  time fd -e js . > /dev/null
  # Compare to find performance
  ```

### T2.2: Audit find Usage

- [ ] Find all find commands in hooks
  ```bash
  grep -rn "find " hooks/ --include="*.sh" | grep -v "# find" | head -20
  ```

- [ ] Document each find pattern
  - Pattern: `find . -name "*.ts" -type f`
  - Equivalent fd: `fd -e ts`
  - Usage: Used in quality-gate.sh for TypeScript discovery

### T2.3: Replace find with fd

- [ ] Create wrapper (optional, for gradual rollout)
  ```bash
  # hooks/lib/fd-wrapper.sh
  find_files() {
    local pattern="$1"
    if command -v fd >/dev/null 2>&1; then
      fd "$pattern"
    else
      find . -name "$pattern" -type f
    fi
  }
  ```

- [ ] Update hooks to use fd
  - [ ] quality-gate.sh (file discovery)
  - [ ] spec-preflight.sh (if used)
  - [ ] Other hooks with find

- [ ] Examples of find → fd migration
  ```bash
  # Before
  find . -name "*.ts" -type f | xargs tsc --noEmit

  # After
  fd -e ts | xargs tsc --noEmit

  # Or (if fd not available)
  find_files "*.ts" | xargs tsc --noEmit
  ```

### T2.4: Testing

- [ ] Run tests with fd
  ```bash
  make test
  # Expect: All pass
  ```

- [ ] Verify fallback works
  ```bash
  # Move fd temporarily
  mv $(which fd) /tmp/fd-backup
  make test  # Should use find
  mv /tmp/fd-backup $(which fd)
  ```

- [ ] Benchmark improvement
  ```bash
  # Before
  time find . -name "*.test.ts" -type f | wc -l

  # After
  time fd -e test.ts | wc -l
  # Expected: 3-5x faster
  ```

### T2.5: Commit

- [ ] Create commit
  ```bash
  git add hooks/lib/fd-wrapper.sh hooks/*.sh
  git commit -m "Phase 3.5: Integrate fd for 3-5x file discovery speedup

  - Add fd-wrapper.sh with graceful fallback to find
  - Replace find commands with fd equivalents
  - Measured 3-5x speedup on file discovery
  - Backwards compatible"
  ```

---

## 👁️ Task 3: procs Integration (1-2 hours)

### T3.1: Installation

- [ ] Install procs
  ```bash
  # macOS
  brew install procs

  # Linux
  cargo install procs

  # Verify
  procs --version
  ```

- [ ] Test procs vs ps
  ```bash
  time ps aux | grep hook-dispatcher > /dev/null
  time procs hook-dispatcher > /dev/null
  # Expected: faster with better output
  ```

### T3.2: Audit ps/pgrep Usage

- [ ] Find all ps/pgrep calls
  ```bash
  grep -rn "ps " hooks/ --include="*.sh" | head -10
  grep -rn "pgrep" hooks/ --include="*.sh" | head -10
  ```

- [ ] Document usage patterns
  - Pattern: `ps aux | grep hook-dispatcher`
  - Usage: Check if hook-dispatcher running

### T3.3: Replace with procs

- [ ] Update ps calls
  ```bash
  # Before
  ps aux | grep hook-dispatcher | grep -v grep

  # After
  procs hook-dispatcher
  ```

- [ ] Create wrapper (optional)
  ```bash
  procs_safe() {
    if command -v procs >/dev/null 2>&1; then
      procs "$@"
    else
      ps aux | grep "$@" | grep -v grep
    fi
  }
  ```

- [ ] Update all hooks using ps/pgrep
  - [ ] hook-dispatcher related code
  - [ ] Agent lifecycle checks
  - [ ] Process monitoring

### T3.4: Testing

- [ ] Run tests
  ```bash
  make test
  ```

- [ ] Test fallback
  ```bash
  # Temporarily remove procs
  mv $(which procs) /tmp/procs-backup
  make test
  mv /tmp/procs-backup $(which procs)
  ```

- [ ] Verify output format matches expectations
  - procs output should be parseable
  - Regex patterns unchanged
  - No breaking changes

### T3.5: Commit

- [ ] Create commit
  ```bash
  git add hooks/lib/procs-wrapper.sh hooks/*.sh
  git commit -m "Phase 3.5: Integrate procs for 2-3x process lookup speedup

  - Add procs-wrapper.sh with fallback to ps
  - Replace ps/pgrep calls with procs
  - Better output formatting
  - Backwards compatible"
  ```

---

## 📊 Final Validation (30 minutes)

### V1: Combined Performance Test

- [ ] Run complete Stop hook sequence
  ```bash
  time make dev-hooks Stop

  # Record results:
  # Before: XXs
  # After:  XXs
  # Improvement: YY%
  ```

- [ ] Profile each component
  ```bash
  # Git operations
  echo "=== GIT OPERATIONS ==="
  time {
    git_cached ls-files > /dev/null
    git_cached status > /dev/null
    git_cached diff --name-only HEAD > /dev/null
  }

  # File discovery
  echo "=== FILE DISCOVERY ==="
  time {
    fd -e ts . > /dev/null
    fd -e js . > /dev/null
  }

  # Process lookup
  echo "=== PROCESS LOOKUP ==="
  time {
    procs hook-dispatcher
  }
  ```

### V2: Fallback Verification

- [ ] All three tools removed simultaneously
  ```bash
  mkdir /tmp/tools-backup
  cp $(which gix fd procs) /tmp/tools-backup/
  rm $(which gix fd procs)

  # Run tests - should all pass with fallbacks
  make test

  # Restore
  cp /tmp/tools-backup/* /usr/local/bin/
  ```

- [ ] No broken functionality
  - [ ] Git operations work
  - [ ] File discovery works
  - [ ] Process lookup works
  - [ ] Cache invalidation works

### V3: Documentation

- [ ] Update hooks/README.md
  ```markdown
  ## Phase 3.5: Tool Modernization

  The following performance-optimized tools are now integrated:

  | Tool | Purpose | Status | Impact |
  |------|---------|--------|--------|
  | gitoxide | Git operations | Recommended | 5-20x faster |
  | fd | File discovery | Recommended | 3-5x faster |
  | procs | Process lookup | Optional | 2-3x faster |

  All have graceful fallback to original tools.

  Installation:
  ```bash
  brew install gitoxide fd procs  # macOS
  ```
  ```

- [ ] Create PHASE_3_5_SUMMARY.md
  - Baseline vs new performance
  - Tools installed and versions
  - Fallback strategy verified
  - Total speedup measured
  - Next steps (Phase 4)

### V4: Cleanup

- [ ] Remove temporary test directories
- [ ] Clean git cache (>1 day old entries)
- [ ] Archive baseline measurements
- [ ] Update CHANGELOG.md

---

## 🎯 Success Criteria

✅ **Phase 3.5 Complete when:**

- [ ] Gitoxide installed and fallback working
- [ ] fd installed and fallback working
- [ ] procs installed and fallback working
- [ ] Combined 30-100x speedup verified
- [ ] Zero test regressions
- [ ] All hooks output unchanged
- [ ] Documentation updated
- [ ] Three commits created (one per tool)
- [ ] Performance measurements documented

**Expected Result:** 8-12s Stop hook time → 2-4s (60-75% reduction)

---

## ⏭️ Next Steps

After Phase 3.5 completion:

1. **Immediately:** Proceed to Phase 2 (race condition elimination) in parallel
2. **Week 3/4:** Complete Phase 3 (caching) + Phase 4 (scaling)
3. **Phase 4+:** Additional tool modernization (oxlint, bash hybridization)

---

## 📞 Troubleshooting

### Tool Installation Issues

```bash
# If brew fails, try cargo
cargo install gitoxide --locked

# If cargo not available, build from source
git clone https://github.com/Byron/gitoxide
cd gitoxide && cargo build --release
cp target/release/gix /usr/local/bin/
```

### Performance Not Improving

- Verify tool versions are latest
- Check cache directory permissions
- Run with strace to see actual tool calls
- Confirm git repo isn't in remote mount (very slow)

### Fallback Not Working

```bash
# Test fallback explicitly
unset PATH  # Remove tools from path
# Should still work with default git/find/ps
```

---

**Version:** 1.0
**Created:** 2026-02-15
**Status:** Ready to implement

