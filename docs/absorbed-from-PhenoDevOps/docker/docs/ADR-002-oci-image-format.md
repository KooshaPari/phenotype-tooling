# ADR-002: OCI Image Format Support

## Status
**Accepted**

## Context

The Phenotype Docker utilities need to parse and work with container images. We must decide on the image format specification to support.

### Requirements

1. **Interoperability:** Work with all major registries
2. **Future-Proof:** Align with industry standards
3. **Simplicity:** Avoid complexity where possible
4. **Backward Compatible:** Support existing Docker images

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **OCI Image Spec** | Industry standard, interoperable | Slightly more complex |
| **Docker v2.2** | Widely supported, mature | Legacy, vendor-specific |
| **Docker v1** | Simple | Deprecated, insecure |
| **Both OCI + Docker** | Maximum compatibility | Implementation complexity |

## Decision

**We will implement OCI Image Specification v1** as the primary format, with transparent support for legacy Docker v2.2 manifests.

### Rationale

1. **Standardization:** OCI is the industry standard, Docker v2.2 is legacy
2. **Interoperability:** Works with all OCI-compliant registries (Docker Hub, ECR, GCR, ACR)
3. **Future-Proof:** New features will come to OCI first
4. **Simplicity:** Clean, well-documented specification

### Consequences

**Positive:**
- Full compatibility with modern registries
- Simpler, cleaner code
- Future-proof implementation

**Negative:**
- Need to handle legacy Docker v2.2 conversion
- Some older images may need translation

## Implementation

### OCI Image Format

```go
// Manifest represents an OCI image manifest
type Manifest struct {
    SchemaVersion int          `json:"schemaVersion"`
    MediaType     string       `json:"mediaType"`
    Config        Descriptor   `json:"config"`
    Layers        []Descriptor `json:"layers"`
    Annotations   map[string]string `json:"annotations,omitempty"`
}

// Descriptor describes a content-addressable object
type Descriptor struct {
    MediaType string `json:"mediaType"`
    Digest    string `json:"digest"`
    Size      int64  `json:"size"`
    URLs      []string `json:"urls,omitempty"`
    Annotations map[string]string `json:"annotations,omitempty"`
}

// ImageConfig represents the OCI image configuration
type ImageConfig struct {
    Created      time.Time         `json:"created,omitempty"`
    Author       string            `json:"author,omitempty"`
    Architecture string            `json:"architecture"`
    OS           string            `json:"os"`
    Config       ContainerConfig   `json:"config,omitempty"`
    RootFS       RootFS            `json:"rootfs"`
    History      []History         `json:"history,omitempty"`
}

// Image represents a parsed container image
type Image struct {
    Reference   string
    Registry    string
    Name        string
    Tag         string
    Digest      string
    Manifest    *Manifest
    Config      *ImageConfig
    Size        int64
}

// ParseImage parses an image reference
func ParseImage(ref string) (*Image, error) {
    // Parse reference components
    named, err := reference.ParseNormalizedNamed(ref)
    if err != nil {
        return nil, fmt.Errorf("parsing reference: %w", err)
    }
    
    // Extract components
    var tag, digest string
    if tagged, ok := named.(reference.Tagged); ok {
        tag = tagged.Tag()
    }
    if digested, ok := named.(reference.Digested); ok {
        digest = digested.Digest().String()
    }
    
    // Default to "latest" if no tag
    if tag == "" && digest == "" {
        named = reference.TagNameOnly(named)
        tag = "latest"
    }
    
    return &Image{
        Reference: ref,
        Registry:  reference.Domain(named),
        Name:      reference.Path(named),
        Tag:       tag,
        Digest:    digest,
    }, nil
}
```

### Media Types

```go
// OCI Media Types
const (
    // Descriptors
    MediaTypeDescriptor = "application/vnd.oci.descriptor.v1+json"
    
    // Manifests
    MediaTypeManifest        = "application/vnd.oci.image.manifest.v1+json"
    MediaTypeManifestList    = "application/vnd.oci.image.index.v1+json"
    
    // Legacy Docker Media Types
    MediaTypeDockerManifest      = "application/vnd.docker.distribution.manifest.v2+json"
    MediaTypeDockerManifestList  = "application/vnd.docker.distribution.manifest.list.v2+json"
    
    // Config
    MediaTypeImageConfig   = "application/vnd.oci.image.config.v1+json"
    MediaTypeDockerConfig    = "application/vnd.docker.container.image.v1+json"
    
    // Layers
    MediaTypeLayer         = "application/vnd.oci.image.layer.v1.tar"
    MediaTypeLayerGzip     = "application/vnd.oci.image.layer.v1.tar+gzip"
    MediaTypeLayerZstd     = "application/vnd.oci.image.layer.v1.tar+zstd"
)

// IsValidMediaType checks if media type is supported
func IsValidMediaType(mediaType string) bool {
    supported := []string{
        MediaTypeManifest, MediaTypeManifestList,
        MediaTypeDockerManifest, MediaTypeDockerManifestList,
    }
    
    for _, mt := range supported {
        if mediaType == mt {
            return true
        }
    }
    return false
}
```

## Related Decisions

- ADR-001: Docker Compose as Configuration Format
- ADR-003: Container Runtime Abstraction

---

*Last Updated: 2026-04-05*
