# 🎨 Ultra-Parity 2026: Customization & Extension Guide

This guide explains how to add new features, aliases, and plugins to your environment without sacrificing the **<40ms startup** performance target.

---

## 1. Adding Aliases and Abbreviations

We use a hybrid approach: standard aliases for simple replacements and **Abbreviations** for Fish-like expanding shortcuts.

### Standard Aliases
Add these to the "Modern Rust CLI Aliases" section in `~/.zshrc`.
```zsh
alias mycmd='command --flags'
```

### Expanding Abbreviations (Fish-style)
Abbreviations expand instantly when you press **Space**. These are defined in the `abbreviations` associative array in `~/.zshrc`.
```zsh
# Example: Adding a new abbreviation
abbreviations+=(
  "k"   "kubectl"
  "tf"  "terraform"
)
```

---

## 2. Adding New Plugins

Always use **Znap** to ensure your plugins are compiled and loaded efficiently.

### Step-by-Step:
1.  Add the plugin to `~/.zshrc`:
    ```zsh
    znap source author/repo-name
    ```
2.  Run `refresh_zsh_cache` to pull the plugin and compile it.
3.  **Audit**: Check your startup time with `time zsh -i -c exit`. If it increases by more than 10ms, consider if the plugin is truly necessary.

---

## 3. Managing Tool Versions (`mise`)

**Mise** is your primary tool manager. It is significantly faster than `nvm` or `asdf`.

*   **Project-specific tools**: Create a `.mise.toml` in your project root.
*   **Global tools**: Run `mise global node@latest`.
*   **Zero-fork loading**: Mise initializations are cached via `znap eval`, so adding new tools to Mise does **not** slow down your shell startup.

---

## 4. UI & Theme Customization

### Prompt (Powerlevel10k / Starship)
*   To reconfigure your prompt visually: `p10k configure`.
*   To edit the raw configuration: Open `~/.p10k.zsh`.
*   **Performance Tip**: Stick to the "Instant Prompt" mode in P10k to keep the cursor appearing in <10ms.

### Syntax Highlighting Colors
Custom colors for `zsh-syntax-highlighting` can be added at the very end of `~/.zshrc`.
```zsh
ZSH_HIGHLIGHT_STYLES[command]='fg=magenta,bold'
```

---

## 5. ShareCLI Strategy Updates

If you need to change how an AI agent handles a specific command (e.g., you want `npm install` to always be queued), edit:
`~/temp-PRODVERCEL/485/kush/sharecli/etc/rules.conf`

Common strategies:
*   `coalesce`: Run once, share result with all waiting agents.
*   `queue`: Run one-by-one to prevent CPU spikes.
*   `passthrough`: Human-like immediate execution.

---
*Generated for Ultra-Parity 2026 Environment*
