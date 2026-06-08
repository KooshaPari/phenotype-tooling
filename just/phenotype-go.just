# phenotype-go.just — Phenotype-org shared Go recipe library.
# Import from a per-repo justfile via:
#   import? "path/to/phenotype-go.just"

# Show the available recipes
default:
  @just --list

# Build all packages in the module
build:
  go build ./...

# Run the full test suite
test:
  go test ./...

# Lint with golangci-lint if present, else go vet
lint:
  golangci-lint run ./... || go vet ./...

# Check formatting without modifying files
fmt:
  gofmt -l .

# Run go vet as a lightweight static check
vet:
  go vet ./...

# Full local CI sweep — runs every gate, stops on first failure
ci:
  @just fmt
  @just vet
  @just lint
  @just test

# Remove build artifacts and test caches
clean:
  go clean ./...
  rm -rf bin/
