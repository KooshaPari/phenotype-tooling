# AGENTS.md — jobs

## Project Overview

- **Name**: jobs (Job Board & Recruitment Platform)
- **Description**: Job posting and candidate matching platform with AI-powered recommendations
- **Location**: `/Users/kooshapari/CodeProjects/Phenotype/repos/jobs`
- **Language Stack**: TypeScript, Next.js, Node.js 20+, PostgreSQL
- **Published**: Private (Phenotype org)

## Quick Start

```bash
# Navigate to project
cd /Users/kooshapari/CodeProjects/Phenotype/repos/jobs

# Install dependencies
npm install

# Set up database
npm run db:migrate

# Start development
npm run dev
```

## Architecture

### Job Platform Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   Job Seeker    │  │   Employer      │  │   Admin         │   │
│  │   Portal        │  │   Dashboard     │  │   Panel         │   │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘   │
└───────────┼───────────────────┼───────────────────┼──────────────┘
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────┐
│                     API Layer                                    │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    tRPC / GraphQL                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │ Jobs     │  │ Users    │  │ Matching │  │ Analytics│  │ │
│  │  │ Router   │  │ Router   │  │ Engine   │  │ Router   │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────────────┐
│                     Services                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │   Search        │  │   Matching      │  │   Notification  ││
│  │   (Algolia/     │  │   (AI/ML)       │  │   (Email/Push)  ││
│  │   Elasticsearch)│  │                 │  │                 ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Quality Standards

### TypeScript Quality

- **Formatter**: Prettier
- **Linter**: ESLint with strict TypeScript
- **Tests**: Vitest >80% coverage
- **E2E**: Playwright

## Git Workflow

### Branch Naming

Format: `<type>/<feature>/<description>`

Examples:
- `feat/matching/add-ml-recommendations`
- `fix/search/handle-filters`
- `ui/job-cards/redesign`

### Commit Messages

Format: `<type>(<scope>): <description>`

Examples:
- `feat(jobs): add salary range filtering`
- `fix(matching): correct similarity scoring`
- `ui(forms): update application wizard`

## File Structure

```
jobs/
├── src/
│   ├── app/                   # Next.js app router
│   ├── components/            # React components
│   ├── server/                # tRPC routers
│   └── lib/                   # Utilities
├── prisma/                    # Database schema
├── tests/
└── AGENTS.md                  # This file
```

## CLI Commands

```bash
# Development
npm run dev
npm run build
npm start

# Database
npm run db:migrate
npm run db:studio

# Testing
npm test
npm run test:e2e
```

## Troubleshooting

### Search not working

```bash
# Reindex Algolia
npm run search:reindex

# Check configuration
npm run search:diagnostics
```

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [tRPC](https://trpc.io/)
- [Phenotype Registry](https://github.com/KooshaPari/phenotype-registry)

## Agent Notes

**Critical Details:**
- Index jobs on publish
- Matching happens asynchronously
- Resume parsing uses AI
- GDPR compliance required

**Known Gotchas:**
- PDF parsing varies by format
- Search relevance needs tuning
- Email deliverability issues
- Rate limit external APIs
