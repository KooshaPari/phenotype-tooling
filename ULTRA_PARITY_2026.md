# 🏁 Ultra-Parity 2026: Zsh Environment Specification

This document serves as the technical reference for the "Ultra-Parity 2026" Zsh environment, a high-performance, zero-fork, AI-ready shell configuration.

## 🏁 Performance Benchmarks

| Context | Metric | Target | Result (Typical) |
| :--- | :--- | :--- | :--- |
| **AI Agent** | Startup Time | < 5ms | **~2ms** |
| **Human** | Cold Startup | < 50ms | **~38ms** |
| **Human** | Warm Startup | < 250ms | **~180ms** |
| **Input Latency** | Keypress to UI | < 10ms | **~5ms (Async)** |

---

## 🛠️ The 2026 Toolstack

We have replaced aging GNU/BSD utilities with modern, Rust-based alternatives for maximum performance and user experience.

| Classic | Modern | Description |
| :--- | :--- | :--- |
| `ls` | `eza` | Icons, Git status, and faster metadata rendering. |
| `cat` | `bat` | Syntax highlighting and Git diff markers. |
| `grep` | `rg` | Extremely fast searching, respects `.gitignore`. |
| `find` | `fd` | Simple syntax, color-coded, faster than `find`. |
| `cd` | `zoxide` | AI-powered directory jumper. |
| `ps` | `procs` | Human-readable process monitoring. |
| `top` | `btop` | High-fidelity interactive system dashboard. |
| `df`/`du` | `duf`/`dust` | Visual disk and directory usage mapping. |
| `nvm`/`pyenv`| `mise` | Unified tool versioning with zero startup overhead. |
| `ranger` | `yazi` | Blazing fast terminal file manager with previews. |
| `tldr` | `tlrc` | Rust-based, ultra-fast `tldr` client. |

---

## 🏗️ Core Architecture

### 1. Philosophy: Performance over Bloat
The Ultra-Parity environment adheres to:
*   **Minimalism**: Only use plugins that provide distinct value.
*   **Compilation**: Every script is compiled to `.zwc` byte-code.
*   **Zero-Subshells**: Avoiding `$(...)` in the startup path.

### 2. Zero-Fork Boot Engine (`znap`)
Instead of spawning subshells for `eval $(tool init)`, we use **Znap** to cache and compile the output into byte-code (`.zwc`). This reduces startup time by an order of magnitude.

### 3. Starship & Ghostty Integration
We use **Starship**, the fastest cross-shell prompt, cached via **Znap** for near-zero overhead. Combined with **Ghostty's** native shell integration, this provides:
*   **Instant Splits**: New tabs and splits open in the same directory automatically.
*   **Reflow Resilience**: Ghostty handles terminal resizing natively, minimizing the need for complex shell-side SIGWINCH handling.

### 4. Context-Aware "Agent Fast-Path"
The environment detects if the caller is an AI Agent (via `AGENT_ID` or `SHARECLI_AGENT_CONTEXT`).
*   **Agent Mode**: Skips **100%** of UI, ZLE, and plugin initialization. Ready in <2ms.
*   **Human Mode**: Loads full interactive suite.

---

## ⌨️ Interactive Features

### 🔍 Smart Help (`Ctrl+H`)
Powered by `zsh-cheatsheet` and `tlrc`. Context-aware help directly in the buffer.

### 🪄 AI Command Generation (`zsh-ai-cmd`)
Integrated LLM support. Provides "ghost text" suggestions for complex commands. 

### 💡 Alias & History Goodies
*   **`zsh-alias-hinter`**: Automatically suggests existing aliases when you type a full command.
*   **`zsh-deja-vu`**: Intelligent directory-specific history retrieval. 
*   **`gh-f`**: GitHub CLI extension for interactive `fzf` browsing.

### 📦 Optimized NVM (`zsh-nvm-x`)
Lazy-loads NVM only when `node`, `npm`, or `nvm` are called, ensuring 0ms startup overhead.

---

## 💾 Maintenance Commands

*   `refresh_zsh_cache`: Pulls latest plugin updates and regenerates the `znap` evaluation cache.
*   `starship help`: View Starship prompt configuration options.
*   `mise list`: Manage installed language versions (Node, Python, Go, etc.).

---

## 📚 Related Documentation

*   `TOOLSET_REFERENCE.md`: Detailed usage of modern Rust utilities.
*   `ARCHITECTURE_REFERENCE.md`: Deep-dive into zero-fork and harness logic.
*   `CUSTOMIZATION_GUIDE.md`: How to extend and modify the shell.
*   `COMPARISON_GUIDE.md`: Competitive analysis and benchmarks.
*   `INTELLIGENCE_REFERENCE.md`: Predictive history and contextual AI.
*   `SHELL_GEMS.md`: Advanced navigation and workflow hacks.

---
*Generated for Ultra-Parity 2026 Environment*
