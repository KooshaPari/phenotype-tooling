# Research Report: Pareto Routing & Hysteresis

> **WORK_STREAM ID**: research-pareto-routing
> **Status**: ✅ Research Phase Complete
> **Date**: 2026-02-19

## Executive Summary

The research for Pareto Routing and Hysteresis (WP-1004) is complete. The strategy optimizes system efficiency by routing 80% of tasks to a lightweight Lifecycle loop while reserved 20% high-risk tasks for the full Gent orchestration (Plan/Operator/Reviewer).

## Key Findings

1. **Strategy**: 
   - Low Risk (80%): Routed to **Lifecycle Loop** (Fast, automated).
   - High Risk (20%): Routed to **The Gent Loop** (Comprehensive, human-like reasoning).
2. **Hysteresis**: Implemented via a damping band and dwell time to prevent "routing thrash" when risk scores fluctuate near the threshold.
3. **Risk Calculation**: Based on complexity, ambiguity, external dependencies, cost impact, and security sensitivity.
4. **Performance Targets**: <1ms routing latency, 5-minute default dwell time.

## Implementation Status

- **Algorithm**: `ParetoRouter` design complete (Rust-based).
- **Strategy**: Risk factors defined and weighted.
- **Failover**: Default to safe route (The Gent loop) on calculation failure.

## Next Steps

1. Implement `ParetoRouter` in `thegent-router` crate.
2. Integrate routing logic into the task intake API.
3. Develop monitoring for 80/20 split efficiency.

## Reference

Detailed research available in [SESSION_RESEARCH_FRAGMENTS_EXPANDED.md](./SESSION_RESEARCH_FRAGMENTS_EXPANDED.md).
