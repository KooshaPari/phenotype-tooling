# Journey Manifests

A *manifest* is a JSON document that pairs a recorded journey (a `.tape` file)
with the spec sections, design references, and acceptance criteria it
demonstrates. The manifest is the **contract** between the spec author and the
journey-verification CI gate.

## Schema

The canonical schema is [`manifest.schema.json`](../../apps/journeys/src/content/schema/manifest.schema.json).
All manifests in this directory MUST validate against it.

## Authoring workflow

1. **Identify the spec section** the journey will demonstrate. Manifests live
   at `docs/journeys/manifests/<spec-id>/`, e.g. `docs/journeys/manifests/001-spec-driven-development-engine/`.

2. **Create a `manifest.json`** with the required top-level fields:

   ```json
   {
     "schemaVersion": "0.1.0",
     "id": "001-spec-driven-development-engine/WP02-governance",
     "spec": "apps/specs/src/content/specs/platform/001-spec-driven-development-engine/SPEC.md",
     "scenario": "Author runs the spec-governance task and the CLI re-emits the manifest within 1s",
     "tape": "./tapes/wp02-governance.tape",
     "assertions": [
       { "type": "exit-code", "expect": 0, "label": "phenotype-journey validate exits clean" },
       { "type": "ocr",       "expect": "PASS", "region": { "x": 12, "y": 240, "w": 480, "h": 32 } }
     ],
     "designRefs": [
       "apps/handbook/src/content/docs/design/tokens.md#status-pass"
     ],
     "acceptanceCriteria": [
       "AC-2.3: spec governance emits manifest in under 1s"
     ]
   }
   ```

3. **Record the tape**:

   ```bash
   phenotype-journey record \
     --tape  docs/journeys/manifests/001-spec-driven-development-engine/tapes/wp02-governance.tape \
     --manifest docs/journeys/manifests/001-spec-driven-development-engine/manifest.json
   ```

4. **Validate locally** (mock mode, no API key required):

   ```bash
   phenotype-journey validate docs/journeys/manifests/001-spec-driven-development-engine/
   ```

5. **Open a PR**. The CI workflow
   (`.github/workflows/journey-verify.yml`) runs `phenotype-journey verify`
   against every manifest under this directory. PRs fail if any manifest does
   not pass.

## Layout

Each manifest lives in its own directory:

```
docs/journeys/manifests/
├── README.md                        ← you are here
├── 001-spec-driven-development-engine/
│   ├── manifest.json
│   ├── manifest.verified.json       ← produced by `phenotype-journey verify`
│   └── tapes/
│       └── *.tape
└── <other-spec-id>/
    └── …
```

## Commands

| Command                                              | Purpose                                  |
|------------------------------------------------------|------------------------------------------|
| `phenotype-journey record --tape … --manifest …`     | Capture a new tape against the manifest  |
| `phenotype-journey validate <dir>/`                  | Mock-mode replay + assertion check       |
| `phenotype-journey verify --manifest <m>.json`       | CI gate; produces `*.verified.json`      |
| `phenotype-journey sync`                             | Refresh `designRefs` from `phenotype-infra` |
| `phenotype-journey assert --list <m>.json`           | Print human-readable assertion results   |

See [`../operations/journey-traceability.md`](../operations/journey-traceability.md)
for the bigger picture.

## Status

- [x] Schema defined (`manifest.schema.json` v0.1.0)
- [x] Layout convention (per-spec subdir + `tapes/`)
- [x] CLI subcommands (`record`, `validate`, `verify`, `sync`, `assert`)
- [ ] First 3 manifests authored for the spec-driven-development-engine spec
- [ ] `phenotype-infra` cross-link check running in CI
