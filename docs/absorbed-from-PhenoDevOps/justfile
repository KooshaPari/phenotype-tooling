# Standard justfile for PhenoDevOps

set shell := ["bash", "-cu"]

# List available recipes
default:
    @just --list

# Start the development server / watch mode
dev:
    task dev

# Produce release artifacts
build:
    task build:release

# Run the test suite
test:
    task test

# Run the linter
lint:
    task lint

# Apply formatter
fmt:
    task fmt

# Remove build artifacts
clean:
    task clean
