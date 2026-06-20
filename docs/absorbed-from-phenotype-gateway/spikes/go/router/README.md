# Go spike — gateway router integration

Delegates OpenAI-compatible `/v1/*` to `third_party/cliproxyapi-plusplus`; combo policy defers to Rust spike.

## Integration sketch

- HTTP shim in phenotype-gateway (future `packages/router`)
- cliproxy++ as provider proxy plane
- OmniRoute interim features: see `docs/router/COMBO_ROUTING.md`
