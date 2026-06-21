# Research

- Detected manifests in the repository:
  - `pyproject.toml` at the repo root
  - `4sgm/package.json`
  - `docs/package.json`
- Current task surface from the existing `Taskfile.yml` was repo-specific and hardcoded to `4sgm/*` paths.
- Command choices used:
  - Python: `uv build`, `uv run pytest`, `uv run ruff check .`
  - Node: `npm run build`, `npm test`, `npm run lint`, `npm run typecheck`
  - Go/Rust fallbacks were included because language detection is manifest-based.
