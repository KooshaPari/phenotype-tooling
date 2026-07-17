# Data Engineering Best Practices Reference

## 1. ETL/ELT Pipeline Design Patterns

### ELT (Extract, Load, Transform) – Modern Approach

**Key Principle**: Push raw data to cloud warehouse, transform in-place using warehouse compute

| Stage | Pattern | Tool | Benefit |
|-------|---------|------|---------|
| Extract | Log-based CDC (Debezium) | Kafka Connect | Incremental loads, natural ordering |
| Load | Batch or streaming | Snowflake/BigQuery | Schema-less landing zone |
| Transform | SQL in warehouse | dbt | Scalable, version-controlled |

**Idempotency Requirement**: Running pipeline 10× must produce identical results
- Use merge statements with surrogate keys
- Deduplicate on natural keys
- Handle late-arriving facts and slowly changing dimensions

### Data Mesh Pattern (Federated Governance)

- **Domain ownership**: Each domain owns its data products
- **Contracts**: Service level agreements for freshness, quality
- **Governance as code**: Policies versioned and auto-enforced

---

## 2. Data Warehouse & Lake Architecture

### Medallion Architecture (Bronze-Silver-Gold)

```
Bronze Layer (Raw)          Silver Layer (Integrated)     Gold Layer (Business-Ready)
├─ Immutable data            ├─ Data Vault modeling       ├─ Star schema (fact + dims)
├─ No transformations        ├─ Type-2 SCDs              ├─ Dimensional models
├─ Compliance archiving      ├─ Deduplication            ├─ Analytics optimized
└─ Replayability             └─ Historization            └─ BI/ML ready
```

**Implementation**: dbt with layered models (stg_ → fct_/dim_ → marts)

### Data Vault 2.0 (Silver Layer)

- Hubs: Core business entities (unique keys)
- Links: Relationships between hubs (many-to-many)
- Satellites: Slowly changing dimensions (type-2 with validity dates)
- Benefits: Auditability, historization, independence of fact tables

---

## 3. Data Pipeline Orchestration

| Tool | Paradigm | Best For | Consideration |
|------|----------|----------|---|
| **Airflow** | DAG-based, schedule-centric | Enterprise, broad adoption | 10+ year battle-tested |
| **Dagster** | Software-defined assets (SDA) | Data product teams, lineage-critical | Modern observability, 3-5× cost |
| **Kestra** | YAML-first, simple UI | Mid-market | Emerging, limited ecosystem |

**2026 Recommendation**: Airflow for scale/adoption, Dagster for modern teams.

---

## 4. Stream Processing (Real-Time Data)

### Kafka + Spark Structured Streaming

- **Kafka**: Immutable event log with replay capability
- **Spark**: Real-time mode (p99 <10ms latency, new in 2026)
- **Use case**: AI agents need fresh context for decisions

```python
df = (spark
  .readStream
  .format("kafka")
  .option("subscribe", "transactions")
  .load())

enriched = df.join(dim_merchants, on="merchant_id")

(enriched.writeStream
  .format("bigquery")
  .option("checkpointLocation", "gs://checkpoints/transactions")
  .start())
```

---

## 5. Data Quality & Testing

### Multi-Layer Approach

| Layer | Tool | Coverage |
|-------|------|----------|
| Ingestion | Great Expectations | Raw data contracts |
| Transformation | dbt tests + dbt-expectations | Data model QA |
| Operations | Soda Core | Production monitoring |
| Analytics | Datadog/Metaplane | Anomaly detection, SLA tracking |

**Target**: 80%+ of critical data paths with automated tests

---

## 6. Data Lineage & Versioning

### OpenLineage (Vendor-Neutral Standard)

- Automatically captures lineage from Airflow, Spark, dbt
- Integrates with Marquez (visualization), Atlan (governance)
- Enables root-cause analysis and impact assessment

### DVC (Data Version Control)

```yaml
# dvc.yaml
stages:
  prepare:
    cmd: python src/prepare.py
    deps:
      - data/raw/transactions.csv
    outs:
      - data/prepared:
          cache: false
  featurize:
    cmd: python src/featurize.py
    deps:
      - data/prepared/
    outs:
      - data/features/
```

---

## 7. Common Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|---|---|---|
| **Data Silos** | Isolated datasets, no cross-org visibility | Data mesh with domain APIs + central catalog |
| **Pipeline Rigidity** | Complex DAGs requiring end-to-end runs | Asset-based orchestration, modular transforms |
| **Wrong Processing Model** | Batch for dashboards, streaming for reports | Blend models: batch aggregates + streaming metrics |
| **Role Silos** | Engineers don't understand full pipelines | Cross-functional pairing, code reviews, documented contracts |
| **AI Slop** | LLM-generated undebuggable code | Require explanation, favor simplicity, test rigorously |

---

## 8. Schema Evolution & CDC Best Practices

### Log-Based CDC with Debezium

```json
{
  "name": "postgres-cdc",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "plugin.name": "pgoutput",
    "key.converter": "io.confluent.kafka.schemaregistry.json.JsonSchemaConverter",
    "value.converter": "io.confluent.kafka.schemaregistry.json.JsonSchemaConverter",
    "snapshot.mode": "initial"
  }
}
```

**Schema Registry Integration**: Confluent Schema Registry auto-detects DDL changes, enforces compatibility

**Consumer Handling Evolution**:
```python
# Gracefully handle missing/new fields
order_id = payload.get("order_id")
new_field = payload.get("new_field", None)  # Default null
```

---

## 9. Enterprise Data Stack (2026 Baseline)

- **Orchestration**: Airflow (proven) or Dagster (modern)
- **Transformation**: dbt with dbt-expectations
- **Streaming**: Kafka + Spark Structured Streaming
- **Quality**: Great Expectations + dbt tests + Soda Core
- **Lineage**: OpenLineage + Marquez
- **Governance**: Data Mesh principles + federated RBAC
- **Versioning**: DVC for ML reproducibility, Git for code

---

## 10. Production Readiness Checklist

- [ ] Remote state backend (S3+DynamoDB, GCS, Snowflake)
- [ ] Idempotent pipelines (safe to replay)
- [ ] Data quality tests (80%+ coverage)
- [ ] Lineage tracking (OpenLineage or equivalent)
- [ ] Secrets in vault (never in code)
- [ ] Monitoring & alerting (Soda, Datadog, Metaplane)
- [ ] Disaster recovery (backup retention, cross-region replicas)
- [ ] Documentation (data contracts, schema evolution)
- [ ] Access control (RBAC per domain, row/column-level security)

---

## References

- dbt Labs: https://www.getdbt.com/blog/
- Dagster: https://dagster.io/learn/
- OpenLineage: https://openlineage.io/
- DataTalks.Club: https://datatalks.club/
- Great Expectations: https://greatexpectations.io/
- DVC: https://dvc.org/
