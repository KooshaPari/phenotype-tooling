# Known Issues

- `bun run build` currently fails because `turbo.json` still uses the deprecated `pipeline` field while Turbo 2.9.6 expects `tasks`.
- That failure is unrelated to the dependency bump and was left untouched in this change.
