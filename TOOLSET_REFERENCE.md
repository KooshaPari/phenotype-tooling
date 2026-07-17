# 🛠️ Ultra-Parity 2026: Toolset and Plugin Reference

This docset provides detailed information on the specific tools and plugins configured in the "Ultra-Parity 2026" Zsh environment.

---

## 🌟 Core Zsh Plugins

We use **Znap** for plugin management, which ensures asynchronous compilation and caching of all shell extensions.

| Plugin | Source | Purpose | Key Feature |
| :--- | :--- | :--- | :--- |
| **zsh-autosuggestions** | `zsh-users` | Fish-like ghost text. | Asynchronous (0ms lag). |
| **zsh-syntax-highlighting** | `zsh-users` | Real-time command coloring. | Validates syntax as you type. |
| **zsh-history-search** | `zsh-users` | Substring history search. | Arrow keys filter by prefix. |
| **zsh-cheatsheet** | `Xav-Deb` | Interactive help menu. | Context-aware (`Ctrl+H`). |
| **zsh-nvm-x** | `seebeen` | Optimized NVM loader. | Zero-overhead lazy loading. |
| **zsh-ai-cmd** | `kylesnowschwartz` | AI command generation. | Ghost-text predictions. |
| **zsh-alias-hinter** | `mpartipilo` | Alias suggestions. | Learn aliases as you type. |
| **zsh-deja-vu** | `justyntemme` | Per-directory history. | Contextual command recall. |
| **zsh-vi-man** | `TunaCuma` | Detailed man help. | `Shift-K` for option info. |
| **fzf-tab** | `Aloxaf` | Fuzzy completion menu. | In-place completion previews. |

---

## 🚀 The Rust-Powered Tooling Suite

The following high-performance tools are installed and aliased for daily use.

### 📦 Navigation & File Management
*   **`zoxide` (aliased to `cd`)**: A smarter version of `cd`. It learns your most-visited directories.
*   **`yazi` (aliased to `ra`)**: A terminal file manager written in Rust. It provides image previews and ultra-fast navigation.
*   **`eza` (aliased to `ls` / `ll`)**: A modern replacement for `ls`. 

### 📝 Text & Search
*   **`bat` (aliased to `cat`)**: A `cat` clone with syntax highlighting and Git integration.
*   **`rg` (ripgrep, aliased to `grep`)**: The fastest search tool available.
*   **`fd` (aliased to `find`)**: A fast and user-friendly alternative to the `find` command.
*   **`sd` (aliased to `sed`)**: An intuitive find-and-replace CLI.

### 📊 System & Monitoring
*   **`btop` (aliased to `top`)**: A beautiful, interactive system monitor.
*   **`procs` (aliased to `ps`)**: A human-readable process viewer.
*   **`duf` (aliased to `df`)**: A color-coded disk usage tool.
*   **`dust` (aliased to `du`)**: A visual directory tree of space consumption.

### 🌐 Network & APIs
*   **`xh` (aliased to `curl`)**: A friendly and fast tool for sending HTTP requests.
*   **`doggo` (aliased to `dig`)**: A modern DNS client for humans with visual output.
*   **`gping` (aliased to `ping`)**: A ping tool with a real-time latency graph.
*   **`gh-f` (GitHub CLI Extension)**: Interactive fuzzy-finding for GitHub resources (repo, issue, pr).

---

## 🤖 AI & Documentation Integration

### `zsh-ai-cmd`
Provides LLM-powered command suggestions as you type.
*   *Keybindings*: Press **Right-Arrow** or **Tab** to accept an AI suggestion.

### `zsh-cheatsheet` + `tlrc`
Your shell is integrated with a multi-layered help system.
1.  **Local Cheats**: Hand-written Markdown files in `cheats/`.
2.  **`tldr` (tlrc)**: If a local sheet isn't found, it pulls from the community-driven `tldr` project.

---

## 🛠️ Specialized Maintenance & Ops

### 1. `mac-ops` (Modular CLI Cleanup)
A native Zsh system optimizer designed for zero-dependency parallel execution and safety. 
*   **Key Feature**: Moves items to a trash directory with a 72-hour recovery window.
*   **Repo**: [seunggabi/mac-ops](https://github.com/seunggabi/mac-ops)

### 2. CiderStack (macOS Virtualization)
A native macOS app built on Apple's Virtualization.framework, optimized for Apple Silicon VMs.
*   **Use Case**: Testing your shell environment on macOS 26 Tahoe or clean OS states.
*   **Site**: [ciderstack.com](https://ciderstack.com)

### 3. Debugging & Testing (Frontend)
For the "Ultra-Parity" developer, debugging should be as fast as the shell.
*   **Agent-Browser**: A fast, daemon-backed Playwright controller for frontend debugging.
*   **Browser-Debugger-CLI**: A simple CLI that opens a WebSocket connection directly to the Chrome DevTools Protocol (CDP) for real-time debugging.

---
*Generated for Ultra-Parity 2026 Environment*
