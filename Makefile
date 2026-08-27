# phenotype-tooling Makefile
.PHONY: all build build-rust build-ts test test-rust test-ts lint lint-rust lint-ts format clean help

all: lint test

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: build-rust build-ts

build-rust:
	cargo build --workspace

build-ts:
	npm run build --workspaces 2>/dev/null || true

test: test-rust test-ts

test-rust:
	cargo test --workspace

test-ts:
	npm test --workspaces 2>/dev/null || true

lint: lint-rust lint-ts

lint-rust:
	cargo clippy --workspace --all-targets -- -D warnings

lint-ts:
	npm run lint --workspaces 2>/dev/null || true

format:
	cargo fmt --all
	npm run format --workspaces 2>/dev/null || true

clean:
	cargo clean
	rm -rf node_modules
