<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/PhenoDevOps/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/PhenoDevOps?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/PhenoDevOps?style=flat-square)
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
# repos — CodeProjects/Phenotype organizational shelf

This is the **repos shelf**: a polyrepo containing ~30 independent projects
organized under `CodeProjects/Phenotype/organizational-shelf/repos`.

## What is a shelf?

A shelf is an organizational layer above individual projects. Think of it like
`~/code/` or `/opt/` — a directory containing related but independent repositories.
Each project is a standalone git repo; the shelf is their shared home.

## Quick Start

### Finding a project
```bash
ls projects/INDEX.md   # Master project list with descriptions
cat projects/INDEX.md   # Find your project
```

### Working on a project
```bash
cd <project-name>      # e.g., cd heliosCLI
git status             # Verify you're in the right place
```

### Creating a worktree
```bash
git worktree add .worktrees/my-feature -b my-feature
cd .worktrees/my-feature
```

## Project Categories

Projects are organized into functional categories at the top level:

| Category | Contents |
|----------|----------|
| `apps/` | User-facing applications |
| `tooling/` | Developer tools, CLIs, scripts |
| `infra/` | Infrastructure, deployment, devops |
| `libs/` | Shared libraries and packages |
| `platforms/` | Platform-as-product projects |

Note: Not all projects are yet in these categories — the reorganization is ongoing.
Use `projects/INDEX.md` for the authoritative list.

## Key Files

| File | Purpose |
|------|---------|
| `projects/INDEX.md` | Master project catalog |
| `AGENTS.md` | Agent interaction rules |
| `GOVERNANCE.md` | Shelf governance |
| `CLAUDE.md` | Claude Code settings |
| `WORKSTORES.md` | Worktree management guide |
| `REPOS_INDEX.md` | Detailed shelf index |

## Architecture

```
repos/                          # ← Shelf root (YOU ARE HERE)
├── .worktrees/                 # Worktree staging area
├── .archive/                    # Archived projects
├── .claude/                     # Shelf-level Claude settings
├── .cursor/                     # Shelf-level Cursor settings
├── projects/                    # Project metadata & catalog
├── docs/                        # Cross-project documentation
│   ├── adr/                   # Architecture Decision Records
│   └── guides/                # How-to guides
├── scripts/                     # Cross-project scripts
├── governance/                  # Governance tooling
├── plans/                       # Work plans
└── [projects]                   # ~30 independent git repos
```

## Agent Workflow

1. **Identify the project** — Check `projects/INDEX.md` or ask the user
2. **Navigate to project** — `cd <project-name>`
3. **Read project rules** — Check for `CLAUDE.md` or `AGENTS.md` in project
4. **Do the work** — Follow shelf rules in `AGENTS.md`
5. **Commit & push** — Use conventional commits, open PR if needed

## NOT AgilePlus

This shelf contains **many projects**, of which AgilePlus is one.
AgilePlus-specific documentation lives inside the `AgilePlus/` project directory,
not at shelf level.

The files that were previously here describing AgilePlus have been moved to
their correct locations:
- AgilePlus governance → `AgilePlus/GOVERNANCE.md`
- AgilePlus agent rules → `AgilePlus/AGENTS.md`
- AgilePlus README → `AgilePlus/README.md`

## Getting Help

- Shelf-level issues: Ask here
- Project-specific issues: `cd <project>` and check that project's docs
- Architecture decisions: `cat docs/adr/INDEX.md`
- General questions: Check `projects/INDEX.md` first
