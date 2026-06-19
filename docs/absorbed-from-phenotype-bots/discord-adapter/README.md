# @phenotype/discord-adapter

Discord adapter for the Phenotype bot framework.

**Absorbed from:** `KooshaPari/AtomsBot` (decomposed 2026-06-18)

## What's Here

- `src/index.ts` — `DiscordAdapter` class implementing `@phenotype/sdk` `Adapter` contract
- `src/adapter.test.ts` — Vitest tests for adapter behavior

## Usage

```typescript
import { DiscordAdapter } from '@phenotype/discord-adapter';
import { PhenotypeBot } from '@phenotype/bot-framework';

const adapter = new DiscordAdapter();
await adapter.init({ token: process.env.DISCORD_TOKEN! });

const bot = new PhenotypeBot({ id: 'discord-bot', name: 'DiscordBot' });
bot.registerAdapter(adapter);
bot.registerHandler('!ping', async (msg) => {
  console.log('ping from', msg.author);
});

await bot.start();
```

## Adapter Contract

Implements `Adapter<TConfig, TState>` from `@phenotype/sdk`:
- `name: 'discord'`
- `version: '0.1.0'`
- `init(config: DiscordConfig): Promise<void>`
- `getState(): { ready, config }`
- `shutdown(): Promise<void>`

## License

MIT (inherited from AtomsBot)
