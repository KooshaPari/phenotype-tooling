# @phenotype/sdk

Core types and interfaces for the Phenotype fleet.

**Absorbed from:** `KooshaPari/AtomsBot` (decomposed 2026-06-18)

## What's Here

- `src/types.ts` — Auto-extracted type/interface declarations from AtomsBot
- `src/index.ts` — Core abstractions: `Adapter`, `Bot`, `Message`, `AdapterType`

## Usage

```typescript
import type { Adapter, Bot, Message } from '@phenotype/sdk';

class MyAdapter implements Adapter {
  readonly name = 'my-adapter';
  readonly version = '0.1.0';
  async init(config) { /* ... */ }
  getState() { return {}; }
  async shutdown() { /* ... */ }
}
```

## Build

```bash
pnpm install
pnpm build
pnpm test
```

## Related

- [`@phenotype/bot-framework`](../phenotype-bot-framework) — Bot orchestration
- [`@phenotype/discord-adapter`](../phenotype-discord-adapter) — Discord adapter
- [`@phenotype/github-adapter`](../phenotype-github-adapter) — GitHub adapter

## License

MIT (inherited from AtomsBot)
