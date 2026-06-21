# apikit Specification

> HTTP toolkit specification (REST, GraphQL, WebSocket adapters)

## Overview

apikit provides a unified HTTP toolkit with adapters for REST,
GraphQL, and WebSocket protocols.

## Components

### REST Adapter

- Typed HTTP client (get, post, put, patch, delete)
- Async/await native
- JSON serialization via serde

### GraphQL Adapter

- Query execution via async-graphql
- Error-aware responses
- Schema generation and server

### WebSocket Adapter

- Full-duplex message send/receive
- tokio-tungstenite based
- Connection lifecycle management

## Architecture

The library is organized into four layers:

1. **Adapters** — Protocol-specific implementations (REST, GraphQL, WebSocket)
2. **Application** — Router, handler dispatch, request pipeline
3. **Domain** — Core domain types and middleware traits
4. **Infrastructure** — Logging, configuration, shared utilities

## References

- [Hyper](https://hyper.rs/) (HTTP server/client)
- [async-graphql](https://github.com/async-graphql/async-graphql)
- [tokio-tungstenite](https://github.com/snapview/tokio-tungstenite)
