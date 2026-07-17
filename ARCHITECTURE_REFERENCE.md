# 🧠 Ultra-Parity 2026: ShareCLI & Architecture Reference

This docset explains the advanced backend mechanisms and integration logic that power the "Ultra-Parity 2026" environment.

---

## 🔒 The ShareCLI Harness

Your environment is governed by the **ShareCLI Harness**, which provides a bridge between human intent and AI agent execution.

### 1. Harness Dispatcher (`sharecli/bin/harness`)
When you run commands like `git`, you are actually calling the harness.
*   **Context Detection**: The harness walks the process tree to determine if the caller is a human or an AI agent.
*   **Rule Enforcement**: It applies strategies defined in `etc/rules.conf` (e.g., `coalesce`, `queue`, `retry`).
*   **Output Transformation**: If requested, the harness can filter or re-render output into structured JSON or Markdown for better agent parsing.

### 2. Fork Prevention Logic
To maintain peak system responsiveness, the harness handles high-frequency calls:
*   **Coalescing**: Identical read-only commands (like `git branch`) triggered by multiple agents are coalesced into a single execution.
*   **Throttling**: Background forks are throttled to ensure the human terminal session remains interactive.

---

## ⚡ Zero-Fork Architecture

The shell is designed to boot without spawning any external processes.

### 1. C-Builtin Migration
We have replaced standard system calls with Zsh's internal C modules:
*   `zmodload zsh/datetime`: Replaces `/bin/date`. Use `$EPOCHSECONDS` or `$strftime`.
*   `zmodload zsh/stat`: Replaces `/usr/bin/stat`. Use `zstat` for metadata.
*   `zmodload zsh/parameter`: Allows access to shell internal tables without forking.

### 2. Znap Eval Caching
Most Zsh frameworks run `eval "$(tool init)"` on startup. 
*   **The Problem**: Each `eval` triggers a process fork (~30ms overhead).
*   **The Fix**: `znap eval` runs the init once, captures the output, and caches it. On subsequent boots, the shell performs a single sequential read of the cached Zsh code.

---

## 🛠️ Resilience and Maintenance

### 1. SIGWINCH (Resize) Throttling
Zsh is notoriously bad at handling terminal window resizing when using complex right-prompts (`RPROMPT`).
*   **The Fix**: We use `zle-line-finish` to clear the `RPROMPT` the moment a command is executed or the window is resized.
*   **The Result**: No "ghost text" remains when scrolling back through your terminal history.

### 2. Agent Fast-Path
AI Agents do not need syntax highlighting, autosuggestions, or complex prompts.
*   **Top-of-File Detect**: `.zshenv` checks for `AGENT_ID`.
*   **Bypass**: If an agent is detected, the shell `return`s immediately, skipping **100%** of the interactive configuration.
*   **Performance**: Raw shell access in **<2ms**.

### 3. Compiled Hyper-Shim (Universal Accelerator)
To supersede standard shell redirection and slow bash shims, we use a unified, compiled Go binary: **`ultra-shim`**.
*   **Location**: `~/.local/bin/ultra-shim`
*   **Logic**: Performs sub-millisecond agent detection, tool redirection (e.g., `ls` $\rightarrow$ `eza`), and flag safety (e.g., `grep -E` fix).
*   **Safety**: Recursive guards and timeouts are implemented in the Go binary, ensuring zero-fork overhead for protection.
*   **Agent Fast-Path**: Integrated directly into the shim to bypass heavy hooks for AI callers.

### 4. Parallel Maintenance Engine
The `shell_maintenance` system (aliased to `refresh_zsh_cache`) executes three critical tasks in parallel:
1.  **`znap pull`**: Updates all plugins asynchronously.
2.  **`rm -rf ~/.cache/zsh-snap/eval/*`**: Flushes cached initialization scripts for tools like `starship` and `mise`.
3.  **`rm -f ~/.zcompdump*`**: Rebuilds the completion cache.
By using Zsh backgrounding (`&`) and `wait`, this process is completed in a fraction of the time required for sequential execution. This architecture is inspired by **mac-ops** for modular system cleanup.

### 4. Safe Deletion (The `vouch` System)
To prevent accidental data loss during development, the `vouch` function replaces `rm -rf` for non-critical deletions. It moves files to `~/.zsh_trash/` with a timestamp, providing an easy recovery path.

---

## 🤖 Advanced Agent Workflow (YOLO Mode Safety)

The "Ultra-Parity 2026" environment provides a robust harness for running multiple parallel AI agents safely.

### 1. Parallel Worktrees (`worktrunk`)
When running multiple agents on the same project, file locks and branch conflicts can occur.
*   **Solution**: `worktrunk` (aliased to `wt`) automates Git worktrees.
*   **Parallelism**: Each agent operates in its own dedicated, persistent worktree, allowing them to run in parallel without stepping on each other's files.

### 2. Sandboxed Terminals (`sprites`)
For agents that operate in "YOLO mode" (executing commands without human intervention), a sandbox is critical.
*   **Mechanism**: `sprites` provides persistent, isolated terminals with their own storage and checkpoints.
*   **Safety**: If an agent executes a destructive command, only the sandbox is affected, and you can roll back to a previous checkpoint.

---
*Generated for Ultra-Parity 2026 Environment*
