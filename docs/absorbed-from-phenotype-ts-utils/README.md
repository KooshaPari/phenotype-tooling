# phenotype-ts-utils

Shared TypeScript utility library for the Phenotype org.
Consolidates 14 commonly-copied helpers across 25+ TypeScript repos.

## Install

```bash
npm install "phenotype-ts-utils @ github:KooshaPari/phenotype-ts-utils#v0.1.0"
```

Or with `pnpm` / `yarn`, the equivalent syntax.

> **Note**: v0.1.0 is published via Git-tag only (not on the npm registry).
> Once a 0.1.x patch is cut with publish config, consumers can swap to
> `npm install phenotype-ts-utils`.

## API

### `string`

| Function | Signature | Notes |
| -------- | --------- | ----- |
| `cn`     | `(...classes: Array<string \| undefined \| null \| false>) => string` | clsx-like className joiner |
| `truncate` | `(s: string, maxLen = 80, suffix = '...') => string` | Truncates, throws if `maxLen < len(suffix)` |
| `slugify` | `(s: string) => string` | URL-safe slug; returns `'untitled'` for empty input |

### `date`

| Function | Signature | Notes |
| -------- | --------- | ----- |
| `formatDate` | `(d: Date \| string, format: 'iso' \| 'us' \| 'eu' = 'iso') => string` | UTC-based, no locale surprises |
| `parseDate` | `(s: string) => Date \| null` | Returns `null` on invalid ISO 8601 |
| `addDays` | `(d: Date, days: number) => Date` | Returns a new Date |

### `function`

| Function | Signature | Notes |
| -------- | --------- | ----- |
| `debounce` | `<T>(fn: T, wait: number) => (...args: Parameters<T>) => void` | Standard trailing-edge debounce |
| `throttle` | `<T>(fn: T, wait: number) => (...args: Parameters<T>) => void` | Leading-edge throttle |

### `object`

| Function | Signature | Notes |
| -------- | --------- | ----- |
| `deepMerge` | `<T extends Record<string, any>>(target: T, source: Partial<T>) => T` | Arrays are replaced, not concatenated |
| `deepClone` | `<T>(v: T) => T` | JSON-roundtrip clone (suitable for JSON-serializable values) |

### `async`

| Function | Signature | Notes |
| -------- | --------- | ----- |
| `sleep` | `(ms: number) => Promise<void>` | Promise-based setTimeout |
| `retry` | `<T>(fn: () => Promise<T>, opts?: { attempts?: number; baseDelayMs?: number }) => Promise<T>` | Exponential backoff: `baseDelayMs * 2^i` |

### `array`

| Function | Signature | Notes |
| -------- | --------- | ----- |
| `uniqueBy` | `<T>(arr: T[], keyFn: (item: T) => unknown) => T[]` | Preserves first-seen order |
| `groupBy` | `<T, K extends string \| number>(arr: T[], keyFn: (item: T) => K) => Record<K, T[]>` | Empty input → `{}` |

## Usage

```typescript
import { cn, truncate, formatDate, debounce, deepMerge } from 'phenotype-ts-utils';

cn('btn', isPrimary && 'btn-primary', isDisabled && 'is-disabled');
// => 'btn btn-primary'

truncate('A long document title', 16);
// => 'A long docume...'

formatDate(new Date(), 'us');
// => '06/12/2026'

const onResize = debounce(() => layout(), 200);
window.addEventListener('resize', onResize);

deepMerge({ a: { x: 1 } }, { a: { y: 2 } });
// => { a: { x: 1, y: 2 } }
```

## Development

```bash
npm install
npm run typecheck   # tsc --noEmit
npm run test        # vitest run (28 tests)
npm run test:coverage
npm run lint        # eslint
npm run build       # tsc -> dist/
```

## License

MIT — see [LICENSE](./LICENSE).
