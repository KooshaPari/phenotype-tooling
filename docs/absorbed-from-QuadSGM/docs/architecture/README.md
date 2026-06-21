# 4SGM Architecture Documentation

Welcome to the 4SGM Wholesale Chatbot architecture documentation. This directory contains comprehensive system design, architecture decisions, and implementation guidance.

## Quick Navigation

### System Overview
- **[system-design.md](./system-design.md)** - Complete system architecture, components, data flow, and deployment strategy
  - 7-layer architecture diagram
  - Technology stack details
  - Cost analysis and performance targets
  - Security and compliance

### Architecture Decision Records (ADRs)

ADRs document major technical decisions, their rationale, consequences, and tradeoffs. Read these to understand *why* we made specific choices.

#### Core Technology Decisions

1. **[ADR-001: FastMCP Selection](./adr/ADR-001-fastmcp-selection.md)**
   - Decision: Use FastMCP 2.13 for MCP server implementation
   - Rationale: 3-line tool registration vs. 20+ lines of boilerplate
   - Impact: ~80% faster tool development
   - Alternatives: Anthropic MCP SDK, custom implementation, HTTP-based tools

2. **[ADR-002: LangGraph Hybrid Pattern](./adr/ADR-002-langgraph-hybrid.md)**
   - Decision: Hybrid DeepAgents + Custom StateGraph for agent orchestration
   - Rationale: Balance between simple ReAct and sophisticated reasoning
   - Components: Router → ReAct (fast) / DeepAgents (accurate) → Tools → Escalation
   - Impact: 30% better recommendation quality, intelligent cost optimization

3. **[ADR-003: Langfuse for Observability](./adr/ADR-003-langfuse-observability.md)**
   - Decision: Open-source Langfuse vs. proprietary LangSmith
   - Rationale: 85-90% cost savings ($6k/year vs. $70-120k/year)
   - Components: Self-hosted on AWS EC2 or managed service option
   - Impact: Full data residency, cost control, no vendor lock-in

4. **[ADR-004: Repository Pattern](./adr/ADR-004-repository-pattern.md)**
   - Decision: Repository pattern for enterprise data abstraction
   - Rationale: Testable, flexible, scalable data access
   - Components: Repository interfaces → Service layer → MCP tools
   - Impact: Easy to swap databases, mock for tests, transparent caching

## Architecture Layers

The system is organized as a 7-layer architecture:

```
Layer 7: Presentation (Next.js Frontend)
         ↓ HTTP/SSE
Layer 6: API Orchestration (FastAPI)
         ↓ Python async
Layer 5: Agent Orchestration (LangGraph)
         ↓ MCP Protocol
Layer 4: Tool Execution (FastMCP Server)
         ↓ Function calls
Layer 3: Data Access (Repository Pattern)
         ↓ SQL/HTTP
Layer 2: Data Sources (SQL Server, Supabase, APIs)
         ↓
Layer 1: Observability & Monitoring (Langfuse)
```

Each layer has clear responsibilities and well-defined interfaces. See [system-design.md](./system-design.md) for detailed component descriptions.

## Key Design Principles

### 1. Enterprise-Grade Quality
- No MVP mindset - full-grade implementation from day one
- >90% test coverage on changed code
- Type-safe (TypeScript frontend, Python type hints)
- Comprehensive error handling and observability

### 2. MCP-First Architecture
- All integrations expose tools via MCP
- Easy to add new systems (SQL Server, ERP APIs, etc.)
- No tight coupling between systems
- Future-proof design

### 3. Cost Efficiency
- Target: <$1 per user conversation
- Strategic use of extended thinking (DeepAgents) only when needed
- Intelligent caching for hot queries
- Rightsize infrastructure (3 EC2 instances, not 10)

### 4. Observability-Driven
- Every agent decision traced in Langfuse
- Cost tracking at query level
- User journey replay capability
- A/B testing framework built-in

### 5. Testability
- Repository pattern enables mock data sources
- All business logic in testable service layer
- Comprehensive Playwright E2E tests
- >90% overall test coverage

## Common Workflows

### Understanding a Design Decision

1. Read the relevant ADR (e.g., ADR-001 for FastMCP)
2. Understand the **Context** (what problem are we solving?)
3. Review the **Decision** (what choice did we make?)
4. Consider the **Consequences** (positive and negative)
5. Check the **Tradeoffs** (what are we giving up?)

### Adding a New Business Tool

1. Define tool interface in `mcp_server/tools/`
2. Implement in FastMCP with 3-line registration (see ADR-001)
3. Write tests using mock repository
4. Update system-design.md tool list
5. Deploy and monitor with Langfuse (ADR-003)

### Optimizing a Slow Query

1. Identify slow query in Langfuse traces (ADR-003)
2. Locate repository method responsible (ADR-004)
3. Add database index or optimize SQL
4. Cache result using Redis decorator (ADR-004)
5. Benchmark improvement with load testing

### Debugging Agent Behavior

1. Replay session in Langfuse (ADR-003)
2. Check router classification (simple vs. complex)
3. Review tool selection by agent
4. Check tool outputs and latency
5. Adjust system prompt or routing logic if needed

## Performance Targets

| Metric | Target | P95 | Max |
|--------|--------|-----|-----|
| Simple Query | 2.0s | 3.0s | 5.0s |
| Complex Query | 10.0s | 12.0s | 15.0s |
| API Uptime | 99.5% | - | - |
| Tool Success | 95%+ | - | - |
| Cost/Query | $0.10-0.30 | - | - |

See system-design.md for detailed cost breakdown and optimization opportunities.

## Cost Overview

**Monthly: ~$1,937 (~$0.20 per query)**

- Compute: $600 (EC2)
- Databases: $625 (SQL Server + Supabase + Redis)
- LLM: $350 (Claude API)
- Observability: $150 (Langfuse self-hosted)
- Other: $112 (networking, storage, domain)

**Annual: ~$22,444**

Savings vs. LangSmith: ~$70-120k/year (ADR-003)

## Security Highlights

- TLS 1.3 encryption (in transit)
- AES-256 encryption (at rest)
- Row-level security (customer data isolation)
- WorkOS AuthKit (authentication)
- Secrets Manager (API key rotation)
- No service role keys in application code

## Development Environment

```bash
# Backend
cd 4sgm/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd 4sgm/frontend
npm install
npm run dev

# MCP Server
python cli.py mcp

# Run tests
pytest --cov=backend/
npm run test
```

## Deployment

Production deployment uses:
- Vercel (frontend CDN)
- AWS EC2 (FastAPI + FastMCP)
- AWS RDS (SQL Server)
- Supabase (PostgreSQL + pgvector)
- CloudFront (CDN)
- Langfuse (self-hosted observability)

See system-design.md for full deployment diagram and scaling strategy.

## Testing Strategy

- **Unit Tests**: Repository, service, utilities (Vitest/pytest)
- **Integration Tests**: API routes, tool execution
- **E2E Tests**: Full user workflows (Playwright)
- **Load Tests**: 100 concurrent users, 10k q/min peak
- **Target Coverage**: >90% overall, 100% on critical paths

## Troubleshooting

**Question: Where do I find tool implementation details?**
Answer: See ADR-002 (LangGraph integration) and system-design.md Layer 4 (Tool Execution)

**Question: How do I understand response latency?**
Answer: Check Langfuse traces (ADR-003). See system-design.md for latency targets.

**Question: What if a tool fails?**
Answer: MCP tools have timeout policy (5s per tool). See ADR-002 for escalation flow.

**Question: How is data protected?**
Answer: See system-design.md Security Architecture. Data encrypted in transit (TLS 1.3) and at rest (AES-256).

**Question: How do I add a new data source?**
Answer: Implement new repository (ADR-004). No changes needed to agent or tools.

## Document Structure

```
docs/architecture/
├── README.md (this file)
├── system-design.md (complete system overview)
└── adr/
    ├── ADR-001-fastmcp-selection.md
    ├── ADR-002-langgraph-hybrid.md
    ├── ADR-003-langfuse-observability.md
    └── ADR-004-repository-pattern.md
```

## Contributing

When updating architecture documentation:

1. Update relevant ADR if decision changes
2. Update system-design.md if implementation details change
3. Keep this README.md as central index
4. Link between documents using relative paths
5. Include version numbers and dates
6. Document tradeoffs, not just decisions

## Contact & Questions

- **Architecture**: See relevant ADR document
- **Implementation**: Check system-design.md components section
- **Performance**: Review Langfuse traces and metrics
- **Security**: See system-design.md Security Architecture

---

**Last Updated**: December 19, 2024
**Version**: 1.0
**Status**: Production Ready

For questions about specific decisions, read the relevant ADR. For implementation details, see system-design.md.
