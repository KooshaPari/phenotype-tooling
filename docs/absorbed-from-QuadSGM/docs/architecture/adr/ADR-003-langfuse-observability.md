# ADR-003: Langfuse for Observability vs. LangSmith Enterprise

## Status
Accepted

## Context

The 4SGM Wholesale Chatbot requires comprehensive observability to:
1. Debug agent decision-making in production
2. Identify bottlenecks in tool execution
3. Track LLM token usage and costs
4. Monitor escalation rates and failure patterns
5. Measure response latency and quality metrics
6. Conduct A/B testing on agent configurations
7. Provide audit trails for compliance

We evaluated two primary solutions:

### Option 1: LangSmith (Langchain/Anthropic Enterprise)
- Official LangChain observability platform
- Closed-source, proprietary
- **Pricing**: Enterprise plan required (~$5,000+/month minimum)
- Strong LangChain integration (out-of-the-box instrumentation)
- Hosted service, no self-hosting

### Option 2: Langfuse (Open Source)
- Open source, self-hosted alternative
- Active development by community
- **Pricing**: Self-hosted free, or managed service (~$99-500/month depending on volume)
- Community-driven, transparent development
- Self-hosted option allows data residency
- Growing LangChain/LangGraph integration

The decision directly impacts operational costs (~$60k/year for LangSmith vs. ~$1.5-6k/year for Langfuse) and operational complexity (managed service vs. self-hosted).

## Decision

We selected **Langfuse (Open Source)** for observability with self-hosted deployment on AWS.

### Rationale

**Cost Efficiency**:
- LangSmith Enterprise: $5,000-10,000/month (~$70-120k/year)
- Langfuse Managed: $500/month (~$6k/year) for equivalent features
- Langfuse Self-Hosted: Free (with EC2 infrastructure cost ~$300/month)
- **Savings**: 85-90% cost reduction vs. LangSmith

**Feature Parity**:
- Both track LLM calls, token usage, latency
- Both support distributed tracing across tool calls
- Both provide cost analytics and session replay
- Langfuse has improving agent observability features
- Langfuse has open development roadmap (transparent)

**Data Privacy**:
- LangSmith: Data sent to Langchain's servers
- Langfuse Self-Hosted: All data stays in our AWS account
- Langfuse Managed: Langfuse-hosted servers (privacy control option)
- Compliance advantage: Self-hosted meets stricter data residency requirements

**Flexibility**:
- Open source: Can fork/customize if needed
- Self-hosted: Full control over infrastructure
- Community: Growing integration library (LangChain, LangGraph, Anthropic)
- Vendor lock-in: Minimal (MCP-compliant, open data format)

### Implementation: Langfuse Self-Hosted

```yaml
# infrastructure/docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: langfuse
      POSTGRES_USER: langfuse_user
      POSTGRES_PASSWORD: ${LANGFUSE_DB_PASSWORD}
    volumes:
      - langfuse_db:/var/lib/postgresql/data

  langfuse:
    image: langfuse/langfuse:latest
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://langfuse_user:${LANGFUSE_DB_PASSWORD}@postgres:5432/langfuse
      NEXTAUTH_SECRET: ${LANGFUSE_AUTH_SECRET}
      NEXTAUTH_URL: https://langfuse.yourdomain.com
      SALT: ${LANGFUSE_SALT}
    ports:
      - "3000:3000"
    volumes:
      - langfuse_data:/app/data

volumes:
  langfuse_db:
  langfuse_data:
```

```python
# backend/observability.py - Langfuse Integration
from langfuse import Langfuse
from langgraph.prebuilt import create_langgraph_tracer

# Initialize Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
)

# Create LangGraph tracer for automatic instrumentation
tracer = create_langgraph_tracer(
    client=langfuse,
    root_trace_id="4sgm_agent"
)

# In FastAPI route:
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Chat endpoint with Langfuse observability"""

    # Start trace
    trace = langfuse.trace(
        name="wholesale_chat",
        user_id=request.user_id,
        session_id=request.session_id,
        metadata={
            "customer_type": request.customer_type,
            "integration": "fastapi"
        }
    )

    try:
        # Execute agent (automatic tracing via tracer)
        final_state = graph.invoke(
            {"messages": [...], "customer_id": request.customer_id},
            config={"callbacks": [tracer]}
        )

        # Add span for response generation
        with trace.span(name="response_formatting") as span:
            response_text = final_state["response"]
            span.event(name="tokens", input={"tokens": count_tokens(response_text)})

        yield format_sse_response(response_text)

        # Flush trace
        langfuse.flush()

    except Exception as e:
        trace.event(name="error", input={"error": str(e), "type": type(e).__name__})
        langfuse.flush()
        raise
```

### Langfuse Features Used

**Trace Visualization**:
- View full agent execution flow with tool calls, latency, tokens
- Identify bottleneck steps (which tools are slow?)
- See LLM model calls, input tokens, output tokens, cost

**Session Analysis**:
- Multi-turn conversation replay
- User journey analysis
- Escalation triggers and patterns

**Analytics Dashboard**:
- Token usage trends (cost tracking)
- Latency percentiles (p50, p95, p99)
- Error rate by tool/agent
- Query success rate by intent type

**Cost Analytics**:
- Per-query token breakdown
- Model usage (Claude 3.5 Sonnet vs. others)
- Tool execution cost attribution
- Budget alerts for cost anomalies

**Experimentation**:
- A/B test different prompts, models, tools
- Compare performance metrics (latency, cost, quality)
- Statistical significance testing

## Consequences

### Positive
1. **Cost Savings**: 85-90% reduction vs. LangSmith (~$70-120k/year saved)
2. **Data Privacy**: Self-hosted option keeps all traces in our infrastructure
3. **Open Source**: Community-driven development; can contribute improvements
4. **Flexibility**: Self-host or use managed service; switch easily
5. **Transparency**: Open roadmap visible; no proprietary black boxes
6. **Control**: Full access to trace data; export in standard formats
7. **Compliance**: Self-hosted meets data residency and privacy requirements
8. **No Vendor Lock-in**: Open data format; easily migrate if needed
9. **Growing Integration**: Improving LangChain, LangGraph, Anthropic support
10. **Production Ready**: Used in production by Langchain, Anthropic, and startups

### Negative
1. **Self-Hosting Complexity**: Need to maintain PostgreSQL, Docker, infrastructure updates
2. **Smaller Community**: Fewer integrations, fewer blog posts vs. LangSmith
3. **Immature Features**: Some features (agent tracing, cost analysis) still evolving
4. **Support**: Community-driven; no commercial support option (vs. LangSmith SLA)
5. **Documentation**: Fewer tutorials/examples than LangSmith
6. **Infrastructure Cost**: Self-hosted requires EC2 instance (~$200-300/month) vs. free managed service
7. **Scaling**: Self-hosted requires monitoring/optimization as scale grows
8. **Team Training**: Requires learning Langfuse UI vs. proprietary LangSmith interface

### Mitigation Strategies
1. **Self-Hosting**: Use Langfuse managed service (~$99-500/month) if infrastructure burden is too high
2. **Community Risk**: Monitor Langfuse GitHub; have fallback plan to LangSmith if needed
3. **Documentation**: Create internal guides for team; document common queries
4. **Support**: Use community Discord/GitHub for issues; hire contractor if critical
5. **Scaling**: Use managed Langfuse service instead of self-hosted at scale
6. **Training**: Record short video tutorials on Langfuse UI for team onboarding

## Tradeoffs Accepted

1. **Support for Cost**: Accept community-driven support for 85% cost savings
2. **Maturity for Savings**: Accept newer platform for significant operational cost reduction
3. **Infrastructure for Control**: Accept self-hosting overhead for data privacy and flexibility

## Managed Service Upgrade Path

If self-hosted becomes bottleneck, we can upgrade to Langfuse Managed (~$99-500/month) with minimal changes:

```python
# Change only connection string, code stays same
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host="https://cloud.langfuse.com"  # Just change host
)
```

## References
- [Langfuse Official Documentation](https://docs.langfuse.com/)
- [Langfuse Self-Hosted Setup](https://docs.langfuse.com/self-host)
- [LangGraph Integration](https://docs.langfuse.com/integrations/langgraph)
- [LangSmith Pricing](https://smith.langchain.com/pricing)
- [Langfuse GitHub Repository](https://github.com/langfuse/langfuse)
- [Agent Observability Best Practices](https://docs.langfuse.com/guides/tracing)

## Implementation Checklist
- [x] Langfuse deployed to AWS EC2
- [x] PostgreSQL database configured with backups
- [x] LangGraph tracer integrated with FastAPI routes
- [x] Cost analytics dashboard configured
- [x] Session replay and trace visualization tested
- [x] Alerts set up for anomalies (latency, cost, errors)
- [x] Team trained on Langfuse UI
- [x] Documentation created for common queries
- [x] Fallback plan to LangSmith documented
- [x] Monthly cost tracking started

## Cost Comparison Table

| Feature | LangSmith | Langfuse Self-Hosted | Langfuse Managed |
|---------|-----------|----------------------|------------------|
| Trace Storage | Unlimited | Unlimited | Limited by plan |
| Cost/Year | $70-120k | $3.6k (EC2) | $1.2-6k |
| Setup Complexity | Easy | Medium | Easy |
| Data Residency | Langsmith servers | Your AWS | Langfuse servers |
| Support | Commercial SLA | Community | Community |
| Self-hosting | No | Yes | No |
| Integration Cost | High | High | High |
| **Annual Savings** | **Baseline** | **$66-116k** | **$68-118k** |

## Questions & Decisions Log

**Q: Can we switch from Langfuse to LangSmith later?**
A: Yes. Traces are exportable in standard formats. Switching requires ~1 week of engineering, but data migration is straightforward.

**Q: What if Langfuse shuts down?**
A: Code is open source. Worst case: we fork and maintain internally. More likely: community adoption continues or acquires. Either way, self-hosted instance continues working.

**Q: Is self-hosted Langfuse production-ready?**
A: Yes. Used by multiple production systems at scale. We recommend: (1) Set up automated backups, (2) Monitor PostgreSQL health, (3) Use managed Langfuse if team size < 3.

**Q: How much does token cost tracking matter?**
A: Critical for cost control. We set alerts: warn if daily cost > $100, critical if > $500. Langfuse provides granular breakdown by model/tool/user.

**Q: Can we use Langfuse with other LLM providers?**
A: Yes. Langfuse is model-agnostic. Works with Claude, GPT-4, Cohere, open source models, etc. Our LangGraph agent can swap models without touching observability.
