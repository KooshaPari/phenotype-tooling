# Agent Rules - KlipDot

**This project is managed through AgilePlus.**

## Overview

KlipDot is a powerful clipboard management and snippet orchestration system designed for developers who value efficiency. It provides intelligent clipboard history, searchable snippet libraries, and cross-application text transformation workflows that integrate seamlessly with the Phenotype ecosystem.

### Purpose & Goals

- **Mission**: Transform clipboard from passive storage to active productivity tool
- **Primary Goal**: Provide instant access to clipboard history with intelligent search and categorization
- **Secondary Goals**:
  - Enable snippet sharing across team members
  - Support rich content (images, files, formatted text)
  - Integrate with IDE extensions and CLI workflows
  - Maintain privacy with local-first encryption

### Key Responsibilities

1. **Clipboard Monitoring**: Real-time capture of clipboard changes across applications
2. **History Management**: Persistent storage with compression and deduplication
3. **Search & Retrieval**: Fast fuzzy search with ranking algorithms
4. **Snippet Organization**: Hierarchical tagging and folder structures
5. **Transformation Pipeline**: Text transformations (case conversion, formatting, encoding)
6. **Sync Service**: Optional encrypted cloud sync for multi-device workflows

## Stack

### Primary Language & Runtime
- **Language**: Rust (Edition 2024, Nightly Compiler)
- **Runtime**: Native with tokio for async operations
- **GUI Framework**: Tauri (Rust backend + Web frontend)
- **Frontend**: SolidJS with TypeScript

### Core Dependencies
```toml
[dependencies]
# Async Runtime
tokio = { version = "1.35", features = ["full"] }
tokio-util = "0.7"

# GUI Framework
tauri = { version = "1.6", features = ["api-all"] }
tauri-plugin-clipboard = "0.1"
tauri-plugin-global-shortcut = "0.1"

# Storage
sled = "1.0"                  # Embedded database
rocksdb = "0.21"             # High-performance storage
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Search
tantivy = "0.21"             # Full-text search engine
fst = "0.4"                  # Finite state transducers

# Clipboard & System Integration
arboard = "3.3"              # Cross-platform clipboard
enigo = "0.1"                # Input simulation
active-win-pos-rs = "0.8"    # Active window detection

# Cryptography
ring = "0.17"                # Cryptographic primitives
argon2 = "0.5"               # Password hashing

# Utilities
chrono = { version = "0.4", features = ["serde"] }
uuid = { version = "1.6", features = ["v4", "serde"] }
regex = "1.10"
once_cell = "1.19"
```

### Frontend Stack
```json
{
  "dependencies": {
    "solid-js": "^1.8",
    "@solidjs/router": "^0.10",
    "@tanstack/solid-virtual": "^3.0",
    "fuse.js": "^7.0",
    "date-fns": "^3.0",
    "class-variance-authority": "^0.7"
  }
}
```

### Platform-Specific
- **macOS**: Cocoa APIs for window management, NSPasteboard
- **Linux**: X11/Wayland selection APIs, DBus for shortcuts
- **Windows**: Win32 clipboard APIs, global hotkeys

### Build & Development Tools
- **Task Runner**: Cargo xtask + npm scripts
- **Linting**: Clippy + ESLint + Prettier
- **Testing**: cargo-nextest + Vitest
- **Bundling**: Tauri CLI

## Quick Start

### Prerequisites

```bash
# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default nightly

# Node.js (via fnm or nvm)
fnm install 20
fnm use 20

# Tauri system dependencies
# macOS:
brew install cmake
# Linux:
# sudo apt install libwebkit2gtk-4.0-dev libappindicator3-dev
# Windows:
# Install WebView2 runtime
```

### Installation

```bash
# Clone the repository
cd /Users/kooshapari/CodeProjects/Phenotype/repos/KlipDot

# Install dependencies
npm install
cargo fetch

# Build native dependencies
npm run tauri:build

# Or development mode
npm run tauri:dev
```

### Development Environment Setup

```bash
# Copy environment configuration
cp .env.example .env

# Edit .env with your settings
# KLIPDOT_ENCRYPTION_KEY - Optional master encryption key
# KLIPDOT_SYNC_ENDPOINT - Optional sync server URL

# Initialize local database
cargo run --bin klipdot-init
```

### Running the Application

```bash
# Development mode (frontend + backend)
npm run dev

# Backend only
cargo run --bin klipdot-core

# Frontend only (Vite dev server)
npm run vite:dev

# Production build
npm run build:production
```

### Verification

```bash
# Run all tests
cargo nextest run
npm run test

# Run with coverage
cargo tarpaulin --out Html
npm run test:coverage

# Check code quality
cargo clippy --all-targets -- -D warnings
npm run lint

# Type checking
npm run typecheck
```

## Architecture

### System Design

KlipDot uses a layered architecture with platform abstraction:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   SolidJS    │  │  Tauri API   │  │   WebView    │     │
│  │   Frontend   │  │   Bridge     │  │   Window     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                     Application Core                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   UI State   │  │   Commands   │  │   Events     │     │
│  │   Manager    │  │   Handler    │  │   Router     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                     Service Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Clipboard  │  │   Search     │  │   Sync       │     │
│  │   Monitor    │  │   Engine     │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Storage    │  │   Security   │  │   Platform   │     │
│  │   (Sled)     │  │   (Ring)     │  │   Abstraction│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. Clipboard Monitor
- **Responsibility**: Watch system clipboard for changes
- **Implementation**: Platform-specific watchers (NSPasteboard, X11 selection, Win32)
- **Features**: Deduplication, content hashing, change detection
- **Performance**: Event-driven with debouncing

#### 2. Search Engine
- **Implementation**: Tantivy for full-text, FST for prefix matching
- **Index Fields**: Content (tokenized), Metadata (exact), Tags (filtered)
- **Ranking**: TF-IDF with recency boosting
- **Query Types**: Fuzzy, Regex, Tag-based, Time range

#### 3. Storage Layer
- **Primary**: Sled embedded database (LSM-tree)
- **Cache**: LRU cache for hot items
- **Compression**: Zstd for large content
- **Encryption**: AES-256-GCM for sensitive items

#### 4. Sync Service
- **Protocol**: WebSocket with automatic reconnection
- **Conflict Resolution**: Last-write-wins with vector clocks
- **Encryption**: End-to-end with user-managed keys
- **Bandwidth**: Delta sync with compression

### Data Models

```rust
// Core clipboard item
struct ClipboardItem {
    id: Uuid,
    content: ContentType,
    source: SourceInfo,
    timestamp: DateTime<Utc>,
    tags: Vec<String>,
    metadata: ItemMetadata,
}

enum ContentType {
    Text(String),
    RichText { html: String, text: String },
    Image(Vec<u8>, ImageFormat),
    FileList(Vec<PathBuf>),
}

struct SourceInfo {
    application: String,
    window_title: Option<String>,
    process_id: Option<u32>,
}
```

### Event Flow

```
System Clipboard → Platform Watcher → Content Filter → Deduplication → Storage
                                                             ↓
                                                    Search Index Update
                                                             ↓
                                                    UI Notification
```

### Security Model

1. **Local Encryption**: Optional per-item or global encryption
2. **Sync Encryption**: End-to-end, server cannot decrypt
3. **Key Management**: Master password with Argon2 derivation
4. **Access Control**: OS-level permissions for clipboard access

## Quality Standards

### Testing Requirements

#### Test Coverage
- **Minimum Coverage**: 75% Rust code, 80% TypeScript code
- **Critical Paths**: 95% coverage for clipboard handling and encryption
- **UI Tests**: E2E with Playwright

#### Test Categories
```bash
# Rust tests
cargo nextest run --lib           # Unit tests
cargo nextest run --test '*'      # Integration tests

# Frontend tests
npm run test:unit                 # Vitest unit tests
npm run test:e2e                  # Playwright E2E

# Platform-specific
cargo test --features macos
cargo test --features linux
cargo test --features windows
```

### Code Quality

#### Rust Standards
```bash
# Strict clippy
cargo clippy --all-targets -- -D warnings \
  -W clippy::pedantic \
  -W clippy::nursery

# Formatting
cargo fmt --check

# Security audit
cargo audit
```

#### TypeScript Standards
```bash
# ESLint
npm run lint

# Prettier
npm run format:check

# Type checking
npm run typecheck
```

### Performance Benchmarks

```bash
# Search performance
cargo bench -- search_throughput

# Storage benchmarks
cargo bench -- storage_operations

# Memory usage
cargo bench -- memory_footprint
```

### Accessibility Requirements

- WCAG 2.1 AA compliance for all UI elements
- Keyboard navigation for all features
- Screen reader support with ARIA labels
- High contrast mode support

## Git Workflow

### Branch Strategy

```
main
  │
  ├── feature/clipboard-rich-text
  │   └── PR #67 → squash merge ──┐
  │                               │
  ├── feature/search-fuzzy-match  │
  │   └── PR #68 → squash merge ──┤
  │                               │
  ├── fix/mac-pasteboard-leak     │
  │   └── PR #69 → squash merge ──┤
  │                               │
  └── hotfix/windows-crash ──────┘
      └── PR #70 → merge commit
```

### Branch Naming

```
feature/<platform>-<description>   # Platform-specific features
feature/core-<description>          # Core functionality
fix/<platform>-<issue>             # Platform-specific fixes
docs/<topic>
chore/<maintenance>
hotfix/<critical>
```

### Commit Conventions

```
feat(clipboard): add support for rich text content

Adds HTML parsing and storage for rich text clipboard content.
Includes sanitization to prevent XSS in preview.

fix(search): resolve fuzzy matching performance issue

Replaces naive Levenshtein with optimized bit-parallel algorithm.
Reduces search latency by 80% for large histories.

refactor(storage): migrate from SQLite to Sled

SQLite caused locking issues with high-frequency updates.
Sled provides better write performance and simpler deployment.
```

### Pull Request Process

1. **Pre-PR Checklist**:
   ```bash
   cargo fmt && cargo clippy -- -D warnings
   cargo nextest run
   npm run lint && npm run typecheck
   npm run test
   ```

2. **PR Requirements**:
   - Screenshots for UI changes
   - Performance impact assessment
   - Platform compatibility notes
   - Security considerations (if applicable)

3. **Review Requirements**:
   - 1 approval minimum
   - CI must pass on all platforms (macOS, Linux, Windows)
   - Manual testing for platform-specific changes

4. **Merge Strategy**:
   - Squash merge for features
   - Regular merge for hotfixes
   - Delete branch after merge

## File Structure

```
KlipDot/
├── src-tauri/                  # Rust backend
│   ├── src/
│   │   ├── main.rs            # Application entry
│   │   ├── lib.rs             # Library exports
│   │   ├── commands/          # Tauri command handlers
│   │   │   ├── clipboard.rs
│   │   │   ├── search.rs
│   │   │   ├── sync.rs
│   │   │   └── settings.rs
│   │   ├── services/          # Business logic
│   │   │   ├── clipboard_monitor.rs
│   │   │   ├── search_engine.rs
│   │   │   ├── sync_service.rs
│   │   │   └── storage.rs
│   │   ├── platform/          # Platform abstraction
│   │   │   ├── mod.rs
│   │   │   ├── macos.rs
│   │   │   ├── linux.rs
│   │   │   └── windows.rs
│   │   ├── models/            # Data structures
│   │   │   ├── item.rs
│   │   │   ├── content.rs
│   │   │   └── settings.rs
│   │   └── utils/             # Utilities
│   │       ├── crypto.rs
│   │       ├── compression.rs
│   │       └── time.rs
│   ├── Cargo.toml
│   └── tauri.conf.json
│
├── src/                        # SolidJS frontend
│   ├── components/            # UI components
│   │   ├── ClipboardItem.tsx
│   │   ├── SearchBar.tsx
│   │   ├── TagList.tsx
│   │   └── SettingsPanel.tsx
│   ├── stores/                # State management
│   │   ├── clipboardStore.ts
│   │   ├── searchStore.ts
│   │   └── settingsStore.ts
│   ├── utils/                 # Frontend utilities
│   │   ├── api.ts
│   │   ├── search.ts
│   │   └── formatting.ts
│   ├── App.tsx
│   └── index.tsx
│
├── tests/                      # E2E tests
│   └── e2e/
│       └── clipboard.spec.ts
│
├── docs/                       # Documentation
│   ├── architecture.md
│   └── api.md
│
├── .github/                    # CI/CD
│   └── workflows/
│       ├── test.yml
│       ├── build-macos.yml
│       ├── build-linux.yml
│       └── build-windows.yml
│
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── Cargo.toml (workspace)
├── CHANGELOG.md
├── cliff.toml
└── AGENTS.md                   # This file
```

## CLI

### Core Commands

```bash
# Application
klipdot                          # Launch GUI
klipdot --background             # Start in background (no window)
klipdot --toggle                 # Toggle window visibility

# Clipboard Operations
klipdot history                  # Show clipboard history
klipdot search <query>           # Search clipboard
klipdot copy <id>                # Copy item to clipboard
klipdot delete <id>              # Delete item
klipdot clear                    # Clear all history

# Snippet Management
klipdot snippet list             # List snippets
klipdot snippet add <name>       # Add current clipboard as snippet
klipdot snippet edit <name>      # Edit snippet
klipdot snippet delete <name>    # Delete snippet
klipdot snippet export <path>    # Export snippets

# Settings
klipdot config get <key>         # Get config value
klipdot config set <key> <val>   # Set config value
klipdot config reset             # Reset to defaults

# Sync
klipdot sync status              # Check sync status
klipdot sync enable              # Enable cloud sync
klipdot sync disable             # Disable cloud sync
klipdot sync force               # Force immediate sync

# Maintenance
klipdot doctor                   # Run diagnostics
klipdot optimize                 # Optimize database
klipdot backup <path>            # Create backup
klipdot restore <path>           # Restore from backup
```

### Global Shortcuts

Default shortcuts (customizable):
- `Cmd+Shift+V` - Open KlipDot window
- `Cmd+Shift+[` - Previous clipboard item
- `Cmd+Shift+]` - Next clipboard item
- `Cmd+Shift+C` - Copy without formatting

### npm Scripts

```bash
npm run dev                    # Development mode
npm run build                  # Production build
npm run test                   # Run all tests
npm run test:unit              # Unit tests only
npm run test:e2e               # E2E tests
npm run lint                   # ESLint
npm run format                 # Prettier
npm run typecheck              # TypeScript check
npm run tauri:dev              # Tauri dev mode
npm run tauri:build            # Build Tauri app
```

## Troubleshooting

### Common Issues

#### Issue: App doesn't detect clipboard changes on macOS

**Symptoms:**
- Clipboard history not updating
- No notifications on copy

**Diagnosis:**
```bash
# Check accessibility permissions
System Preferences > Security & Privacy > Accessibility
# KlipDot should be checked

# Check console logs
log stream --predicate 'process == "KlipDot"'
```

**Resolution:**
1. Grant Accessibility permissions in System Preferences
2. Restart KlipDot after permission changes
3. If using Secure Input, unlock keychain first

---

#### Issue: Search is slow with large history

**Symptoms:**
- Search takes > 500ms
- UI freezes during search

**Diagnosis:**
```bash
# Check index status
klipdot doctor

# Check database size
ls -lh ~/Library/Application\ Support/KlipDot/
```

**Resolution:**
```bash
# Rebuild search index
klipdot optimize --rebuild-index

# Reduce history size
klipdot config set max_history_items 10000
klipdot clear --older-than 30d
```

---

#### Issue: Sync fails with authentication error

**Symptoms:**
```
Error: Sync failed: authentication required
```

**Resolution:**
```bash
# Re-authenticate
klipdot sync disable
klipdot sync enable

# Check sync endpoint
klipdot config get sync.endpoint

# Reset sync state
rm -rf ~/Library/Application\ Support/KlipDot/sync/
klipdot sync force
```

---

#### Issue: High memory usage

**Symptoms:**
- Memory usage > 500MB
- System slowdown

**Resolution:**
```bash
# Check memory usage
klipdot doctor --memory

# Enable memory limits
klipdot config set memory_limit_mb 256

# Reduce cache size
klipdot config set cache_size_mb 64
```

---

#### Issue: Keyboard shortcuts not working

**Diagnosis:**
```bash
# List registered shortcuts
klipdot config get shortcuts

# Check for conflicts with other apps
```

**Resolution:**
1. Check for conflicting shortcuts in System Preferences
2. Reset shortcuts to defaults:
   ```bash
   klipdot config reset shortcuts
   ```
3. Re-register shortcuts:
   ```bash
   klipdot config set shortcuts.enabled false
   klipdot config set shortcuts.enabled true
   ```

---

#### Issue: Build fails on Linux with WebKit errors

**Symptoms:**
```
error: failed to run custom build command for `webkit2gtk-sys`
```

**Resolution:**
```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install libwebkit2gtk-4.0-dev \
  libappindicator3-dev \
  librsvg2-dev \
  patchelf

# Fedora
sudo dnf install webkit2gtk3-devel \
  libappindicator-gtk3-devel \
  librsvg2-devel
```

---

### Debug Mode

```bash
# Enable debug logging
export KLIPDOT_LOG_LEVEL=debug
export RUST_BACKTRACE=1

# Run with logging
klipdot 2>&1 | tee klipdot.log

# Tauri debug
npm run tauri:dev -- --features debug
```

### Data Recovery

```bash
# Backup before recovery
klipdot backup ~/klipdot-backup-$(date +%Y%m%d).db

# Database repair
klipdot doctor --repair

# Export to JSON
klipdot export --format json ~/klipdot-export.json
```

### Performance Profiling

```bash
# CPU profiling
cargo flamegraph --bin klipdot-core

# Memory profiling
cargo heaptrack --bin klipdot-core

# Search benchmarks
cargo bench search
```

---

## Agent Self-Correction & Verification Protocols

### Critical Rules

1. **Platform Testing Required**
   - All clipboard-related changes must be tested on target platform
   - Use VMs or CI for platforms you don't have access to

2. **Privacy First**
   - Never log clipboard content in plaintext
   - Encrypt sensitive data before any storage
   - Respect user privacy settings

3. **Test Cross-Platform**
   - Platform abstraction layer must have tests for each OS
   - Conditional compilation for platform-specific code

4. **AgilePlus Integration**
   - Reference related specs for all features
   - Update specs when requirements change

---

*This AGENTS.md is a living document. Update it as KlipDot evolves.*
