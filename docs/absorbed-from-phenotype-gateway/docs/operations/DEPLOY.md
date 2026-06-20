# Deploy — interim stack map

Maps OmniRoute deploy stack to phenotype-gateway operations (absorb docs, not TS monolith).

| OmniRoute component | Interim | Gateway ops |
|---------------------|---------|-------------|
| Docker Compose | OmniRoute `docker-compose.yml` | Reference only — unified compose TBD in `packages/` |
| Caddy LB | OmniRoute edge | phenotype-gateway edge doc (future) |
| Redis | OmniRoute sessions/cache | Shared infra note — not duplicated per plane |
| cliproxy++ | `third_party/cliproxyapi-plusplus` | Primary `/v1` proxy |
| bifrost | `third_party/bifrost` | Enterprise MCP/guardrails |

## Submodule checkout

```bash
git submodule update --init --recursive
```

See [SUBMODULE_UPDATE.md](./SUBMODULE_UPDATE.md).
