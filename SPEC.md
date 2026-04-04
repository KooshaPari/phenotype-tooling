# SPEC.md - KlipDot

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    KlipDot Architecture                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     CLI Layer (clap)                       ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       ││
│  │  │  start   │ │  status  │ │   list   │ │  config  │       ││
│  │  │  daemon  │ │  health  │ │  cleanup │ │   set    │       ││
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       ││
│  │       └─────────────┴─────────────┴─────────────┘            ││
│  │                         │                                    ││
│  │              ┌──────────┴──────────┐                        ││
│  │              │    Service Mode     │ ← Background daemon   ││
│  │              │    (optional)       │                        ││
│  │              └──────────┬──────────┘                        ││
│  └──────────────────────────┼───────────────────────────────────┘│
│                             │                                  │
│  ┌──────────────────────────┼───────────────────────────────────┐│
│  │              Core Engine (tokio async)                        ││
│  │                                                              ││
│  │  ┌────────────────────────┴────────────────────────┐       ││
│  │  │              Interceptor Core                     │       ││
│  │  │  ┌──────────────┐ ┌──────────────┐              │       ││
│  │  │  │  Clipboard   │ │   File Ops   │              │       ││
│  │  │  │   Monitor    │ │   Monitor    │              │       ││
│  │  │  │              │ │              │              │       ││
│  │  │  │ • Platform   │ │ • Drag-drop  │              │       ││
│  │  │  │   specific   │ │ • File paste │              │       ││
│  │  │  │ • Image      │ │ • Stdin      │              │       ││
│  │  │  │   detection  │ │   detection  │              │       ││
│  │  │  └──────┬───────┘ └──────┬───────┘              │       ││
│  │  │         └─────────────────┘                      │       ││
│  │  │                   │                            │       ││
│  │  │  ┌────────────────┴────────────────┐           │       ││
│  │  │  │      Interceptor Logic            │           │       ││
│  │  │  │  • Image validation               │           │       ││
│  │  │  │  • Path replacement               │           │       ││
│  │  │  │  • Format conversion              │           │       ││
│  │  │  │  • Metadata extraction            │           │       │
│  │  │  └─────────────────────────────────┘           │       ││
│  │  └─────────────────────────────────────────────────┘       ││
│  │                                                              ││
│  │  ┌─────────────────────────────────────────────────────┐    ││
│  │  │              Image Processor                        │    ││
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│    ││
│  │  │  │  Format      │ │  Compress    │ │   Hash       ││    ││
│  │  │  │  Convert     │ │  (quality)   │ │  (dedup)     ││    ││
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘│    ││
│  │  │  ┌──────────────┐ ┌──────────────┐                │    ││
│  │  │  │   Resize     │ │  Metadata    │                │    ││
│  │  │  │  (optional)  │ │  Extraction  │                │    ││
│  │  │  └──────────────┘ └──────────────┘                │    ││
│  │  └─────────────────────────────────────────────────────┘    ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │              Shell Integration Layer                         ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        ││
│  │  │     ZSH      │ │     Bash     │ │     Fish     │        ││
│  │  │              │ │              │ │              │        ││
│  │  │ • Preexec    │ │ • Preexec    │ │ • Events     │        ││
│  │  │ • Precmd     │ │ • Precmd     │ │ • Handlers   │        ││
│  │  │ • Aliases    │ │ • Aliases    │ │ • Wrappers   │        ││
│  │  └──────────────┘ └──────────────┘ └──────────────┘        ││
│  │                                                              ││
│  │  ┌───────────────────────────────────────────────────────┐  ││
│  │  │              Hook Functions                           │  ││
│  │  │  klipdot_handle_image() • klipdot_check_paste()       │  ││
│  │  │  klipdot_cp • klipdot_mv • klipdot_scp                │  ││
│  │  └───────────────────────────────────────────────────────┘  ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │              Terminal Preview Layer                          ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          ││
│  │  │    chafa     │ │    timg      │ │   qlmanage   │          ││
│  │  │   (ASCII)    │ │  (Sixel)     │ │  (macOS)     │          ││
│  │  │              │ │              │ │              │          ││
│  │  │ • Terminal   │ │ • Kitty,     │ │ • QuickLook  │          ││
│  │  │   art       │ │   iTerm2     │ │   popup      │          ││
│  │  └──────────────┘ └──────────────┘ └──────────────┘          ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │              Storage Layer                                     ││
│  │  ┌───────────────────────────────────────────────────────┐  ││
│  │  │           ~/.klipdot/ Directory                         │  ││
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  ││
│  │  │  │screenshots│ │  hooks/  │ │  temp/   │ │  logs/   │   │  ││
│  │  │  │  *.png   │ │ *.zsh    │ │          │ │ *.log    │   │  ││
│  │  │  │  *.jpg   │ │ *.bash   │ │          │ │          │   │  ││
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  ││
│  │  │  ┌─────────────────────────────────────────────────┐   │  ││
│  │  │  │            config.json                          │   │  ││
│  │  │  │  • Interception settings                        │   │  ││
│  │  │  │  • Storage configuration                        │   │  ││
│  │  │  │  • Performance tuning                           │   │  ││
│  │  │  │  • Security options                             │   │  ││
│  │  │  └─────────────────────────────────────────────────┘   │  ││
│  │  └───────────────────────────────────────────────────────┘  ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │              AI Agent API (HTTP)                               ││
│  │  ┌───────────────────────────────────────────────────────┐  ││
│  │  │  GET  /api/status      → System status (JSON)         │  ││
│  │  │  GET  /api/images      → List recent images           │  ││
│  │  │  POST /api/process     → Process image batch          │  ││
│  │  │  GET  /api/monitor     → SSE stream                    │  ││
│  │  └───────────────────────────────────────────────────────┘  ││
│  │                                                              ││
│  │  Performance: <100ms API response, 1000+ images/min         ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Core Engine
**Interceptor** (`src/interceptor.rs`)
- Clipboard monitoring (platform-specific)
- File operation interception (drag-drop, paste)
- Standard input detection
- Process stdout/stderr monitoring
- Event-driven async architecture (Tokio)

**Image Processor** (`src/image_processor.rs`)
- Format detection and validation
- Format conversion (PNG, JPG, WebP)
- Quality compression
- Resize/thumbnail generation
- Perceptual hashing for deduplication
- Metadata extraction (EXIF)

**Configuration** (`src/config.rs`)
- JSON-based configuration
- Hot-reload support
- Platform-specific defaults
- Validation and migration

### 2. Shell Integration
**Shell Hooks** (`src/shell_hooks.rs`)
- ZSH: `preexec` and `precmd` hooks
- Bash: PROMPT_COMMAND integration
- Fish: Event handlers
- Wrapper functions: `klipdot_cp`, `klipdot_mv`, `klipdot_scp`

**Platform Support**
- **macOS**: `pbpaste`/`pbcopy` integration, `fswatch` for file monitoring
- **Linux**: `xclip`/`wl-clipboard`, `inotify` for file events
- **Windows**: Native clipboard API, file system watchers

### 3. Terminal Preview
**Image Preview** (`src/image_preview.rs`)
- **chafa**: ASCII art conversion (universal)
- **timg**: Sixel graphics (Kitty, iTerm2)
- **qlmanage**: macOS QuickLook (GUI fallback)
- Metadata display (dimensions, file size)

### 4. Service Mode
**Daemon** (`src/service.rs`)
- Background process management
- PID file handling
- Log rotation
- Signal handling (SIGTERM, SIGHUP)
- Auto-start on login (systemd, launchd)

### 5. Storage
**Local Storage**
- Directory: `~/.klipdot/`
- Screenshots: timestamped and UUID-named
- Hooks: Shell integration scripts
- Config: `config.json` with JSON Schema
- Logs: Rotated application logs

## Data Models

### Config
```rust
pub struct Config {
    pub enabled: bool,
    pub auto_start: bool,
    pub interception: InterceptionConfig,
    pub storage: StorageConfig,
    pub performance: PerformanceConfig,
    pub security: SecurityConfig,
    pub image_formats: Vec<String>,
}

pub struct InterceptionConfig {
    pub clipboard: bool,
    pub file_operations: bool,
    pub drag_drop: bool,
    pub stdin: bool,
    pub process_monitoring: bool,
}

pub struct StorageConfig {
    pub directory: PathBuf,
    pub max_file_size: usize,       // bytes
    pub compression_quality: u8,    // 0-100
    pub retention_days: u32,
    pub auto_cleanup: bool,
}

pub struct PerformanceConfig {
    pub clipboard_poll_interval_ms: u64,
    pub file_watch_interval_ms: u64,
    pub max_concurrent_processing: usize,
}

pub struct SecurityConfig {
    pub allow_external_access: bool,
    pub restricted_paths: Vec<PathBuf>,
    pub max_image_size: usize,
}
```

### ProcessedImage
```rust
pub struct ProcessedImage {
    pub id: Uuid,
    pub original_path: Option<PathBuf>,
    pub stored_path: PathBuf,
    pub filename: String,
    pub format: ImageFormat,
    pub dimensions: (u32, u32),
    pub file_size_bytes: u64,
    pub perceptual_hash: String,
    pub metadata: ImageMetadata,
    pub source: ImageSource,
    pub created_at: DateTime<Utc>,
}

pub enum ImageFormat {
    Png,
    Jpeg,
    Gif,
    Webp,
    Bmp,
}

pub enum ImageSource {
    Clipboard,
    FileDragDrop,
    Stdin,
    FileCopy { source_path: PathBuf },
}

pub struct ImageMetadata {
    pub exif: Option<ExifData>,
    pub color_space: Option<String>,
    pub bit_depth: Option<u8>,
}
```

### API Response
```typescript
interface StatusResponse {
    status: 'running' | 'stopped' | 'error';
    version: string;
    uptime_seconds: number;
    images_processed: number;
    storage_used_bytes: number;
    config: Config;
}

interface ImagesResponse {
    images: ProcessedImage[];
    total: number;
    page: number;
    per_page: number;
}
```

## Performance Specifications

### Interception
- **Clipboard Polling**: 1000ms (configurable)
- **File Watch**: Event-driven (no polling)
- **Process Monitoring**: 5000ms intervals
- **Image Processing**: ~50ms per image (typical)

### Resource Usage
- **Memory**: <50MB steady state
- **CPU**: <1% during idle monitoring
- **Disk**: Depends on screenshot volume
- **API Response**: <100ms guaranteed

### Throughput
- **Clipboard**: 1000+ operations/minute
- **File Operations**: 100+ concurrent
- **Batch Processing**: 100 images per batch

## Integration Points

### AI Agent Integration
```bash
# Start with API
klipdot start --daemon --api-port 8080

# Query from AI agent
curl http://localhost:8080/api/status
curl http://localhost:8080/api/images/recent
```

### Shell Configuration
```bash
# ~/.zshrc or ~/.bashrc
source ~/.klipdot/hooks/zsh-integration.zsh

# Quick preview function
klipdot_quick_preview() { ... }
```

### Vim/Neovim
```vim
" Paste images in markdown
autocmd InsertLeave * call klipdot#check_clipboard()
```

## Security Model

### Data Privacy
- **Local Only**: No network calls
- **User Permissions**: Files owned by user
- **Restricted Paths**: Configurable path restrictions
- **No External Storage**: Local filesystem only

### File Permissions
```bash
chmod 700 ~/.klipdot/
chmod 600 ~/.klipdot/config.json
chmod 644 ~/.klipdot/screenshots/*.png
```

### Access Control
- API access configurable (default: localhost only)
- Path restrictions for sensitive directories
- Max file size limits prevent DoS

## Extensibility

### Custom Hooks
```bash
# Add custom pre-processing
klipdot hooks add pre-process ~/.klipdot/hooks/optimize.sh

# Add custom post-processing
klipdot hooks add post-process ~/.klipdot/hooks/upload.sh
```

### Plugin System (Future)
```rust
pub trait Plugin {
    fn name(&self) -> &str;
    fn on_image_processed(&self, image: &ProcessedImage) -> Result<()>;
}
```

### Cloud Sync (User-implemented)
```bash
# In post-process hook
rsync ~/.klipdot/screenshots/ user@server:/backup/
```
