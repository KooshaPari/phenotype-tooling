# @phenotype/github-adapter

GitHub adapter for the Phenotype bot framework.

**Absorbed from:** `KooshaPari/AtomsBot` (decomposed 2026-06-18)

## What's Here

- `src/index.ts` — `GitHubAdapter` class implementing `@phenotype/sdk` `Adapter` contract
- `src/adapter.test.ts` — Vitest tests for adapter behavior

## Usage

```typescript
import { GitHubAdapter } from '@phenotype/github-adapter';
import { PhenotypeBot } from '@phenotype/bot-framework';

const adapter = new GitHubAdapter();
await adapter.init({ token: process.env.GITHUB_TOKEN! });

const bot = new PhenotypeBot({ id: 'gh-bot', name: 'GitHubBot' });
bot.registerAdapter(adapter);

await bot.start();
```

## Adapter Contract

Implements `Adapter<TConfig, TState>` from `@phenotype/sdk`:
- `name: 'github'`
- `version: '0.1.0'`
- `init(config: GitHubConfig): Promise<void>`
- `getState(): { ready, config }`
- `shutdown(): Promise<void>`

## License

MIT (inherited from AtomsBot)
