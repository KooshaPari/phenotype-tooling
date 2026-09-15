# devenv-abstraction Specification

> **⚠️ DEPRECATED**: This project has been renamed to **[NanoVMS](https://github.com/KooshaPari/nanovms)**

Please refer to the [NanoVMS SPEC.md](https://github.com/KooshaPari/nanovms/blob/main/SPEC.md) for the current specification.

## Historical Overview

This was the original specification for the devenv-abstraction project, which has been superseded by NanoVMS with an improved two-level abstraction architecture:

1. **Infrastructure Layer** (CURRENT): VM runtimes (Native, Lima, WSL, MicroVM, WASM)
2. **Platform Layer** (PLANNED): Target platforms (iOS, Android, tvOS, etc.)

## Migration

All features and functionality have been migrated to NanoVMS. The devenv-abstraction repository is now read-only.

---

## Appendix: Historical Architecture Reference

### A.1 Original Hexagonal Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                         DEVENV-ABSTRACTION ARCHITECTURE                                    │
│                           (Hexagonal/Ports & Adapters)                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                              PRIMARY ADAPTERS (Driving)                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │  │
│  │  │   CLI       │  │   API       │  │   SDK       │  │   CI/CD Integration       │ │  │
│  │  │   Adapter   │  │   Adapter   │  │   Adapter   │  │   Adapters                │ │  │
│  │  │             │  │             │  │             │  │                             │ │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────────────┬───────────────┘ │  │
│  │         │                │                │                       │                 │  │
│  └─────────┼────────────────┼────────────────┼───────────────────────┼─────────────────┘  │
│            │                │                │                       │                    │
│  ┌─────────▼────────────────▼────────────────▼───────────────────────▼────────────────┐ │
│  │                              APPLICATION CORE                                       │ │
│  │                                                                                      │ │
│  │   ┌─────────────────────────────────────────────────────────────────────────────┐   │ │
│  │   │                         DEVENV DOMAIN SERVICES                               │   │ │
│  │   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │ │
│  │   │  │   Sandbox   │  │   Runtime   │  │   Image     │  │   Network   │    │   │ │
│  │   │  │   Service   │  │   Service   │  │   Service   │  │   Service   │    │   │ │
│  │   │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │ │
│  │   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │ │
│  │   │  │   Storage   │  │   Volume    │  │   Config    │  │   Security  │    │   │ │
│  │   │  │   Service   │  │   Service   │  │   Service   │  │   Service   │    │   │ │
│  │   │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │ │
│  │   └─────────────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                                      │ │
│  │   ┌─────────────────────────────────────────────────────────────────────────────┐   │ │
│  │   │                            DOMAIN MODELS                                     │   │ │
│  │   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │ │
│  │   │  │   Sandbox   │  │   Runtime   │  │    Image    │  │   Platform  │    │   │ │
│  │   │  │             │  │             │  │             │  │             │    │   │ │
│  │   │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │ │
│  │   └─────────────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────────────────────┘ │
│            │                │                │                       │                   │
│  ┌─────────┼────────────────┼────────────────┼───────────────────────┼────────────────┐  │
│  │         │                │                │                       │                │  │
│  │  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐  ┌───────────▼────────────┐  │  │
│  │  │   Sandbox   │  │   Runtime   │  │   Image     │  │   Platform            │  │  │
│  │  │   Port      │  │   Port      │  │   Port      │  │   Port                │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────────────────┘  │  │
│  │                                                                                    │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│            │                │                │                       │                   │
│  ┌─────────┼────────────────┼────────────────┼───────────────────────┼────────────────┐  │
│            │                │                │                       │                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                        SECONDARY ADAPTERS (Driven)                                 │ │
│  │                                                                                    │ │
│  │  Platform-Specific Implementations:                                                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │ │
│  │  │    macOS    │  │   Windows   │  │    Linux    │  │   WASM/WebAssembly          │ │ │
│  │  │   (Lima)    │  │   (WSL2)    │  │  (Native)   │  │   (Wasmtime)                │ │ │
│  │  │             │  │             │  │             │  │                             │ │ │
│  │  │ • Lima ctl  │  │ • WSL2 API  │  │ • Namespaces│  │ • Wasmtime API              │ │ │
│  │  │ • vz driver │  │ • gVisor    │  │ • cgroups   │  │ • WASI interface            │ │ │
│  │  │ • Rosetta   │  │ • Hyper-V   │  │ • seccomp   │  │ • Browser integration       │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │ │
│  │                                                                                    │ │
│  │  Container Runtimes:                                                              │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │ │
│  │  │   Docker    │  │   Podman    │  │  containerd │  │     gVisor                  │ │ │
│  │  │   API       │  │   API       │  │    API      │  │    Sandbox                  │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │ │
│  │                                                                                    │ │
│  └────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### A.2 Original Domain Models (Go)

```go
package domain

import (
	"context"
	"time"

	"github.com/google/uuid"
)

// SandboxID is a unique identifier for sandbox instances
type SandboxID uuid.UUID

// Sandbox represents an isolated development environment
type Sandbox struct {
	ID          SandboxID
	Name        string
	Description string
	Type        SandboxType
	Status      SandboxStatus
	
	// Configuration
	Runtime    RuntimeConfig
	Resources  ResourceConfig
	Network    NetworkConfig
	Storage    StorageConfig
	Security   SecurityConfig
	
	// State
	CreatedAt   time.Time
	StartedAt   *time.Time
	StoppedAt   *time.Time
	LastHealthCheck *time.Time
	
	// Relationships
	Images      []ImageReference
	Volumes     []VolumeMount
	OwnerID     string
	Labels      map[string]string
	
	// Platform-specific data
	PlatformData map[string]interface{}
}

// SandboxType defines the isolation mechanism
type SandboxType string

const (
	SandboxTypeNative   SandboxType = "native"   // Native process isolation
	SandboxTypeVM       SandboxType = "vm"       // Virtual machine
	SandboxTypeContainer SandboxType = "container" // OCI container
	SandboxTypeWASM     SandboxType = "wasm"     // WebAssembly
	SandboxTypeMicroVM  SandboxType = "microvm"  // Firecracker/gVisor
)

// SandboxStatus represents the lifecycle state
type SandboxStatus string

const (
	SandboxStatusCreating   SandboxStatus = "creating"
	SandboxStatusCreated    SandboxStatus = "created"
	SandboxStatusStarting   SandboxStatus = "starting"
	SandboxStatusRunning    SandboxStatus = "running"
	SandboxStatusStopping   SandboxStatus = "stopping"
	SandboxStatusStopped    SandboxStatus = "stopped"
	SandboxStatusPaused     SandboxStatus = "paused"
	SandboxStatusDestroying SandboxStatus = "destroying"
	SandboxStatusDestroyed  SandboxStatus = "destroyed"
	SandboxStatusError      SandboxStatus = "error"
)

// RuntimeConfig defines the runtime environment
type RuntimeConfig struct {
	Type           RuntimeType
	Version        string
	Environment    map[string]string
	WorkingDir     string
	Entrypoint     []string
	Command        []string
	Args           []string
}

// RuntimeType specifies the container/runtime technology
type RuntimeType string

const (
	RuntimeTypeDocker     RuntimeType = "docker"
	RuntimeTypePodman     RuntimeType = "podman"
	RuntimeTypeContainerd RuntimeType = "containerd"
	RuntimeTypeSystemdNspawn RuntimeType = "systemd-nspawn"
	RuntimeTypeChroot     RuntimeType = "chroot"
	RuntimeTypeNone       RuntimeType = "none"
)

// ResourceConfig defines resource constraints
type ResourceConfig struct {
	CPUs           float64           // Number of CPU cores
	MemoryMB       int64             // Memory limit in MB
	MemorySwapMB   int64             // Swap limit in MB
	DiskGB         int64             // Disk limit in GB
	DiskIOPs       int64             // I/O operations per second limit
	NetworkMbps    int64             // Network bandwidth limit
	PidsLimit      int64             // Maximum number of PIDs
	Ulimits        []UlimitConfig    // Resource limits
	CgroupParent   string            // Parent cgroup
}

// UlimitConfig represents a resource limit
type UlimitConfig struct {
	Name string
	Soft int64
	Hard int64
}

// NetworkConfig defines network settings
type NetworkConfig struct {
	Mode           NetworkMode
	Hostname       string
	Domainname     string
	DNS            []string
	DNSSearch      []string
	ExtraHosts     map[string]string
	PortBindings   map[string][]PortBinding
	MacAddress     string
	IPAddress      string
	Gateway        string
	NetworkID      string
	Bridge         string
}

// NetworkMode specifies network isolation level
type NetworkMode string

const (
	NetworkModeBridge   NetworkMode = "bridge"
	NetworkModeHost     NetworkMode = "host"
	NetworkModeNone     NetworkMode = "none"
	NetworkModeContainer NetworkMode = "container"
	NetworkModeCustom   NetworkMode = "custom"
)

// PortBinding represents a port mapping
type PortBinding struct {
	HostIP      string
	HostPort    string
	Protocol    string // tcp, udp, sctp
}

// StorageConfig defines storage settings
type StorageConfig struct {
	Driver         StorageDriver
	DriverOptions  map[string]string
	Rootfs         string
	Readonly       bool
	Volumes        []VolumeConfig
	Tmpfs          map[string]string
}

// StorageDriver specifies the storage backend
type StorageDriver string

const (
	StorageDriverOverlay2 StorageDriver = "overlay2"
	StorageDriverOverlay  StorageDriver = "overlay"
	StorageDriverAUFS     StorageDriver = "aufs"
	StorageDriverBtrfs    StorageDriver = "btrfs"
	StorageDriverZFS      StorageDriver = "zfs"
	StorageDriverVFS      StorageDriver = "vfs"
)

// VolumeConfig defines a volume mount
type VolumeConfig struct {
	Type        string // bind, volume, tmpfs
	Source      string
	Destination string
	Mode        string // ro, rw
	Propagation string // rprivate, private, rshared, shared, rslave, slave
}

// VolumeMount represents an active volume mount
type VolumeMount struct {
	VolumeConfig
	Name        string
	Driver      string
	Labels      map[string]string
}

// SecurityConfig defines security policies
type SecurityConfig struct {
	Privileged     bool
	User           string
	Group          string
	Groups         []string
	Capabilities   CapabilitiesConfig
	Seccomp        string  // Seccomp profile
	AppArmor       string  // AppArmor profile
	SELinux        string  // SELinux options
	ReadonlyRootfs bool
	NoNewPrivileges bool
}

// CapabilitiesConfig defines Linux capabilities
type CapabilitiesConfig struct {
	Add  []string
	Drop []string
}

// ImageReference represents a container image
type ImageReference struct {
	ID         string
	Name       string
	Tag        string
	Digest     string
	Registry   string
	Platform   Platform
	Size       int64
	CreatedAt  time.Time
	Labels     map[string]string
}

// Platform specifies the target architecture
type Platform struct {
	OS           string
	Architecture string
	Variant      string
}

// SandboxRepository defines the storage interface
type SandboxRepository interface {
	Create(ctx context.Context, sandbox *Sandbox) error
	Get(ctx context.Context, id SandboxID) (*Sandbox, error)
	Update(ctx context.Context, sandbox *Sandbox) error
	Delete(ctx context.Context, id SandboxID) error
	List(ctx context.Context, filter SandboxFilter) ([]*Sandbox, error)
	ListByStatus(ctx context.Context, status SandboxStatus) ([]*Sandbox, error)
}

// SandboxFilter provides query filtering
type SandboxFilter struct {
	Types      []SandboxType
	Statuses   []SandboxStatus
	Owners     []string
	Labels     map[string]string
	NamePrefix string
	CreatedAfter  *time.Time
	CreatedBefore *time.Time
}

// SandboxService defines the core domain service
type SandboxService interface {
	// Lifecycle operations
	Create(ctx context.Context, spec SandboxSpec) (*Sandbox, error)
	Start(ctx context.Context, id SandboxID) error
	Stop(ctx context.Context, id SandboxID, timeout time.Duration) error
	Pause(ctx context.Context, id SandboxID) error
	Resume(ctx context.Context, id SandboxID) error
	Restart(ctx context.Context, id SandboxID, timeout time.Duration) error
	Delete(ctx context.Context, id SandboxID, force bool) error
	
	// Query operations
	Get(ctx context.Context, id SandboxID) (*Sandbox, error)
	List(ctx context.Context, filter SandboxFilter) ([]*Sandbox, error)
	Logs(ctx context.Context, id SandboxID, options LogOptions) (LogStream, error)
	Exec(ctx context.Context, id SandboxID, command []string) (ExecResult, error)
	
	// Health and monitoring
	Health(ctx context.Context, id SandboxID) (*HealthStatus, error)
	Stats(ctx context.Context, id SandboxID) (*Stats, error)
}

// SandboxSpec defines the creation specification
type SandboxSpec struct {
	Name        string
	Description string
	Type        SandboxType
	Runtime     RuntimeConfig
	Resources   ResourceConfig
	Network     NetworkConfig
	Storage     StorageConfig
	Security    SecurityConfig
	Images      []ImageReference
	OwnerID     string
	Labels      map[string]string
}

// HealthStatus represents sandbox health
type HealthStatus struct {
	Status    string // healthy, unhealthy, starting
	FailingStreak int
	LastCheck time.Time
	Log       []HealthCheckResult
}

// HealthCheckResult represents a single check
type HealthCheckResult struct {
	Start    time.Time
	End      time.Time
	ExitCode int
	Output   string
}

// Stats represents resource usage statistics
type Stats struct {
	Read        time.Time
	Preread     time.Time
	
	CPUStats    CPUStats
	MemoryStats MemoryStats
	DiskStats   DiskStats
	NetworkStats map[string]NetworkStats
	PidsStats   PidsStats
}

// CPUStats represents CPU usage
type CPUStats struct {
	Usage           CPUUsage
	ThrottlingData  ThrottlingData
}

type CPUUsage struct {
	TotalUsage            uint64
	UsageInKernelmode     uint64
	UsageInUsermode       uint64
	PercpuUsage           []uint64
}

type ThrottlingData struct {
	Periods          uint64
	ThrottledPeriods uint64
	ThrottledTime    uint64
}

// MemoryStats represents memory usage
type MemoryStats struct {
	Usage             uint64
	MaxUsage          uint64
	Limit             uint64
	Stats             map[string]uint64
}

// DiskStats represents disk I/O
type DiskStats struct {
	ReadBytes  uint64
	WriteBytes uint64
	ReadIOps   uint64
	WriteIOps  uint64
}

// NetworkStats represents network usage
type NetworkStats struct {
	RxBytes      uint64
	RxPackets    uint64
	RxDropped    uint64
	RxErrors     uint64
	TxBytes      uint64
	TxPackets    uint64
	TxDropped    uint64
	TxErrors     uint64
}

// PidsStats represents process statistics
type PidsStats struct {
	Current uint64
	Limit   uint64
}

// LogOptions defines log streaming options
type LogOptions struct {
	Follow     bool
	Timestamps bool
	Since      time.Time
	Tail       int
}

// LogStream represents a log stream
type LogStream interface {
	Next() (*LogEntry, error)
	Close() error
}

// LogEntry represents a single log line
type LogEntry struct {
	Timestamp time.Time
	Source    string // stdout, stderr
	Message   string
}

// ExecResult represents command execution result
type ExecResult struct {
	ExitCode int
	Stdout   string
	Stderr   string
}
```

### A.3 Migration Path to NanoVMS

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                     MIGRATION: DEVENV-ABSTRACTION → NANOVMS                                │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  devenv-abstraction                              NanoVMS                                    │
│  ────────────────────                            ───────                                    │
│                                                                                             │
│  ┌─────────────┐                                 ┌─────────────┐                             │
│  │  Sandbox    │─────────────┬────────────────▶│  Runtime    │                             │
│  │  (generic)  │             │                 │  (Level 1)  │                             │
│  └─────────────┘             │                 └─────────────┘                             │
│                              │                       │                                     │
│  ┌─────────────┐             │                 ┌─────▼─────┐                               │
│  │  Runtime    │─────────────┘                 │  Platform │                               │
│  │  (mixed)    │                               │  (Level 2)│                               │
│  └─────────────┘                               └───────────┘                               │
│                                                                                             │
│  Key Changes:                                                                               │
│  ────────────                                                                               │
│  1. Clearer two-level abstraction:                                                          │
│     - Level 1: Infrastructure (VM/container runtime)                                        │
│     - Level 2: Platform (iOS, Android, etc.)                                              │
│                                                                                             │
│  2. Improved sandboxing model:                                                              │
│     - Hardware-level isolation (MicroVMs)                                                  │
│     - OS-level isolation (containers)                                                       │
│     - Process-level isolation (namespaces)                                                  │
│                                                                                             │
│  3. Unified OCI integration:                                                                │
│     - Standard container image format                                                       │
│     - Cross-platform image distribution                                                     │
│                                                                                             │
│  4. Enhanced developer experience:                                                          │
│     - Simpler CLI                                                                          │
│     - Better IDE integration                                                               │
│     - Improved performance                                                                 │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### A.4 Historical API Surface

```yaml
# Original REST API endpoints (for reference only)

# Sandbox Management
POST   /v1/sandboxes              # Create sandbox
GET    /v1/sandboxes              # List sandboxes
GET    /v1/sandboxes/{id}          # Get sandbox details
PUT    /v1/sandboxes/{id}          # Update sandbox
DELETE /v1/sandboxes/{id}          # Delete sandbox

# Lifecycle Operations
POST   /v1/sandboxes/{id}/start    # Start sandbox
POST   /v1/sandboxes/{id}/stop     # Stop sandbox
POST   /v1/sandboxes/{id}/pause    # Pause sandbox
POST   /v1/sandboxes/{id}/resume   # Resume sandbox
POST   /v1/sandboxes/{id}/restart  # Restart sandbox

# Operations
GET    /v1/sandboxes/{id}/logs     # Stream logs
POST   /v1/sandboxes/{id}/exec    # Execute command
GET    /v1/sandboxes/{id}/stats   # Get resource stats
GET    /v1/sandboxes/{id}/health   # Health check

# Images
GET    /v1/images                 # List images
POST   /v1/images/pull            # Pull image
DELETE /v1/images/{id}            # Delete image
```

### A.5 Historical Performance Targets

| Metric | Original Target | Achieved | Notes |
|--------|----------------|----------|-------|
| Sandbox creation | < 5 seconds | 3.2s avg | Lima-based on macOS |
| Sandbox startup | < 10 seconds | 7.8s avg | Including image pull |
| Memory overhead | < 256 MB | ~180 MB | Per sandbox |
| CPU overhead | < 5% | ~3% | Compared to native |
| Concurrent sandboxes | 50+ | 75 tested | On 16GB RAM |

---

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | SPEC-DEVENV-001 |
| **Version** | 0.9.9 (Final Archive) |
| **Status** | DEPRECATED / ARCHIVED |
| **Last Updated** | 2026-04-06 |
| **Superseded By** | [NanoVMS](https://github.com/KooshaPari/nanovms) |

---

*This document is preserved for historical reference. All active development has moved to NanoVMS.*
