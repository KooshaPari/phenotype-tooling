# @phenotype/bot-framework

Bot orchestration framework for the Phenotype fleet.

**Absorbed from:** `KooshaPari/AtomsBot` (decomposed 2026-06-18)

## What's Here

- `src/index.ts` — `PhenotypeBot` class, `SimpleRouter`, message routing
- `src/bot.test.ts` — Vitest tests for bot lifecycle and routing

## Architecture

```
PhenotypeBot
  ├── registerAdapter(adapter)  // Discord, GitHub, Slack, custom
  ├── registerHandler(pattern, fn)  // Message routing
  ├── start() / stop()  // Lifecycle
  └── handleMessage(msg)  // Dispatch
```

## Usage

```typescript
import { PhenotypeBot } from '@phenotype/bot-framework';
import { DiscordAdapter } from '@phenotype/discord-adapter';

const bot = new PhenotypeBot({
  id: 'my-bot',
  name: 'MyBot',
});

bot.registerAdapter(new DiscordAdapter({ token: '...' }));
bot.registerHandler('!ping', async (msg) => {
  console.log('ping from', msg.author);
});

await bot.start();
```

## Related

- [`@phenotype/sdk`](../phenotype-sdk) — Core types
- [`@phenotype/discord-adapter`](../phenotype-discord-adapter) — Discord
- [`@phenotype/github-adapter`](../phenotype-github-adapter) — GitHub

## License

MIT (inherited from AtomsBot)
