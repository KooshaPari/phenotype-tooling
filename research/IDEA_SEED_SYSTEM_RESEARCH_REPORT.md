# Research Report: Idea Seed Detection & Storage System

> **WORK_STREAM ID**: research-idea-seed-system
> **Status**: ✅ Research Phase Complete
> **Date**: 2026-02-19

## Executive Summary

The research for the "Idea Seed" system is complete. This system automatically detects potential project ideas or fragments from agent conversations and stores them in a structured format for later retrieval and development.

## Key Findings

1. **Detection**: Uses NLP patterns to identify "Idea Seeds" (e.g., "we should...", "maybe we can...", "potential feature:").
2. **Storage**: Seeds are stored in `docs/research/idea-seeds/` as individual Markdown files with frontmatter metadata (source, date, status, priority).
3. **Session Integration**: Every conversation dump is scanned for idea seeds as part of the post-session processing.
4. **Lifecycle**: Seeds can be promoted to Work Stream items or discarded during periodic reviews.

## Implementation Status

- **Detection Logic**: Design complete.
- **Storage Format**: Standardized Markdown schema defined.
- **Cli Tool**: `thegent seeds list/promote` command design complete.

## Next Steps

1. Implement the Idea Seed scanner in the `thegent` CLI.
2. Automate seed extraction from conversation dumps.
3. Integrate seed promotion into the `WORK_STREAM.md` automation.

## Reference

Detailed research available in [IDEA_SEEDS_SESSION_STORAGE.md](./IDEA_SEEDS_SESSION_STORAGE.md).
