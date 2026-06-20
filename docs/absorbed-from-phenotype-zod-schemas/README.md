<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/phenotype-zod-schemas/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/phenotype-zod-schemas?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/phenotype-zod-schemas?style=flat-square)
![AI-Slop](https://img.shields.io/badge/AI--DD-Slop%20Expected-orange?style=flat-square)
![AI-Only-Maintained](https://img.shields.io/badge/Planned%20%26%20Maintained%20by-AI%20Agents%20Only-red?style=flat-square)
![HITL-less](https://img.shields.io/badge/HITL--less%20AI--DD-metaproject-yellow?style=flat-square)

> ⚠️ **AI-Agent-Only Repository**
>
> This repo is **planned, maintained, and managed exclusively by AI Agents**.
> Slop issues, rough edges, and AI artifacts are **expected and intentionally
> present** as part of an **HITL-less / minimized AI-DD** metaproject focused
> on learning, refining, and brute-force training both the agents and the
> human operator. Bug reports and contributions are still welcome, but please
> expect AI-generated code, comments, and documentation throughout.
<!-- AI-DD-META:END -->
# @phenotype/zod-schemas

Shared [Zod](https://zod.dev) validation schemas for the Phenotype platform.
Provides five commonly reused schemas that every Phenotype service reaches
for: email, URL, UUID, ISO timestamp, and pagination query parameters.

## Install

```bash
npm install @phenotype/zod-schemas zod
```

`zod` is declared as a peer dependency; install the major version that matches
your application (^3.22).

## Schemas

| Name                   | Type                              | Purpose                                          |
| ---------------------- | --------------------------------- | ------------------------------------------------ |
| `emailSchema`          | `z.ZodString`                     | RFC 5322-friendly email string                   |
| `urlSchema`            | `z.ZodString`                     | HTTP/HTTPS URL string                            |
| `uuidSchema`           | `z.ZodString`                     | RFC 4122 UUID (v1–v5) string                     |
| `isoTimestampSchema`   | `z.ZodString`                     | ISO 8601 timestamp (e.g. `2026-06-08T12:00:00Z`) |
| `paginationQuerySchema`| `z.ZodObject<...>`                | `{ page, pageSize }` query (1-based, defaulted)  |

## Usage

```ts
import {
  emailSchema,
  uuidSchema,
  paginationQuerySchema,
} from "@phenotype/zod-schemas";

emailSchema.parse("alice@example.com");   // "alice@example.com"
uuidSchema.parse("550e8400-e29b-41d4-a716-446655440000"); // ok

const { page, pageSize } = paginationQuerySchema.parse({
  page: "2",
  pageSize: "50",
});
// page=2, pageSize=50
```

## Build & test

```bash
npm run build   # tsc -> dist/
npm test        # vitest run
```

## License

MIT © Phenotype
