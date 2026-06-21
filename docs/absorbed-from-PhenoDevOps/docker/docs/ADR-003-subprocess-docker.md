# ADR-003: Subprocess-Based Docker Operations

## Status
**Accepted**

## Context

The Phenotype Docker utilities need to interact with Docker for building images, running containers, and managing compose stacks. We must decide on the integration approach.

### Requirements

1. **Simplicity:** Easy to implement and maintain
2. **Compatibility:** Works with all Docker versions
3. **Feature Complete:** Access to all Docker features
4. **Error Handling:** Clear error messages and status codes
5. **Testing:** Testable without Docker daemon

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Docker CLI (subprocess)** | Simple, feature-complete, well-documented | Process overhead |
| **Docker API (HTTP)** | Direct, efficient | Complex auth, version management |
| **Docker SDK (Go client)** | Native Go, type-safe | Dependency, version coupling |
| **Containerd API** | Modern, standard | Lower-level, more complex |

## Decision

**We will use Docker CLI subprocess execution** for initial implementation, with design for future API integration.

### Rationale

1. **Simplicity:** Subprocess calls are straightforward
2. **Compatibility:** Docker CLI handles API versioning
3. **Feature Complete:** Access to all Docker features immediately
4. **Debugging:** Easy to reproduce commands manually

### Consequences

**Positive:**
- Fast implementation
- No SDK dependencies
- Automatic authentication handling
- Easy debugging

**Negative:**
- Process spawning overhead
- Output parsing required
- Harder to unit test

## Implementation

### Docker Command Runner

```go
// Docker provides Docker CLI operations
type Docker struct {
    command string // "docker" or full path
    logger  *slog.Logger
}

// NewDocker creates a new Docker client
func NewDocker() *Docker {
    return &Docker{
        command: "docker",
        logger:  slog.Default(),
    }
}

// Build builds a Docker image
func (d *Docker) Build(ctx context.Context, opts BuildOptions) (string, error) {
    args := []string{"build"}
    
    if opts.Dockerfile != "" {
        args = append(args, "-f", opts.Dockerfile)
    }
    
    if opts.Tag != "" {
        args = append(args, "-t", opts.Tag)
    }
    
    for key, value := range opts.BuildArgs {
        args = append(args, "--build-arg", fmt.Sprintf("%s=%s", key, value))
    }
    
    args = append(args, opts.Context)
    
    cmd := exec.CommandContext(ctx, d.command, args...)
    
    output, err := cmd.CombinedOutput()
    if err != nil {
        return "", fmt.Errorf("docker build failed: %w\n%s", err, output)
    }
    
    // Parse image ID from output
    imageID := parseImageID(string(output))
    
    d.logger.Info("image built", "tag", opts.Tag, "id", imageID)
    return imageID, nil
}

// ComposeUp starts docker-compose services
func (d *Docker) ComposeUp(ctx context.Context, file string, detach bool) error {
    args := []string{"compose", "-f", file, "up"}
    
    if detach {
        args = append(args, "-d")
    }
    
    cmd := exec.CommandContext(ctx, d.command, args...)
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr
    
    return cmd.Run()
}

// ComposeDown stops and removes docker-compose services
func (d *Docker) ComposeDown(ctx context.Context, file string) error {
    cmd := exec.CommandContext(ctx, d.command, "compose", "-f", file, "down")
    return cmd.Run()
}

// Push pushes an image to registry
func (d *Docker) Push(ctx context.Context, image string) error {
    cmd := exec.CommandContext(ctx, d.command, "push", image)
    output, err := cmd.CombinedOutput()
    if err != nil {
        return fmt.Errorf("docker push failed: %w\n%s", err, output)
    }
    return nil
}

// Pull pulls an image from registry
func (d *Docker) Pull(ctx context.Context, image string) error {
    cmd := exec.CommandContext(ctx, d.command, "pull", image)
    output, err := cmd.CombinedOutput()
    if err != nil {
        return fmt.Errorf("docker pull failed: %w\n%s", err, output)
    }
    return nil
}

// BuildOptions contains build parameters
type BuildOptions struct {
    Context     string
    Dockerfile  string
    Tag         string
    BuildArgs   map[string]string
    NoCache     bool
    Target      string
}
```

### Command Output Parsing

```go
// Parse image ID from docker build output
func parseImageID(output string) string {
    // Look for "Successfully built <id>" or sha256:<id>
    lines := strings.Split(output, "\n")
    for _, line := range lines {
        if strings.Contains(line, "Successfully built") {
            parts := strings.Fields(line)
            if len(parts) >= 3 {
                return parts[2]
            }
        }
        if strings.Contains(line, "writing image sha256:") {
            // Extract from "writing image sha256:abc123..."
            start := strings.Index(line, "sha256:")
            if start != -1 {
                return line[start : start+19] // sha256: + 12 chars
            }
        }
    }
    return ""
}

// ParseError extracts meaningful error from Docker output
func ParseError(output string) error {
    // Common error patterns
    if strings.Contains(output, "Cannot connect to the Docker daemon") {
        return fmt.Errorf("docker daemon not running")
    }
    if strings.Contains(output, "unauthorized") {
        return fmt.Errorf("authentication failed: check registry credentials")
    }
    if strings.Contains(output, "manifest unknown") {
        return fmt.Errorf("image not found in registry")
    }
    if strings.Contains(output, "no such file or directory") {
        return fmt.Errorf("build context not found")
    }
    
    return fmt.Errorf("docker error: %s", output)
}
```

## Testing Strategy

```go
// MockDocker for testing
type MockDocker struct {
    BuildFunc func(ctx context.Context, opts BuildOptions) (string, error)
    PushFunc  func(ctx context.Context, image string) error
    PullFunc  func(ctx context.Context, image string) error
}

func (m *MockDocker) Build(ctx context.Context, opts BuildOptions) (string, error) {
    if m.BuildFunc != nil {
        return m.BuildFunc(ctx, opts)
    }
    return "sha256:mock", nil
}

func (m *MockDocker) Push(ctx context.Context, image string) error {
    if m.PushFunc != nil {
        return m.PushFunc(ctx, image)
    }
    return nil
}
```

## Related Decisions

- ADR-001: Docker Compose as Configuration Format
- ADR-002: OCI Image Format Support

---

*Last Updated: 2026-04-05*
