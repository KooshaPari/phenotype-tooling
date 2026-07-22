//! `elicitate-mcp` — MCP server entry point.
//!
//! Exposes a single tool, `elicitate_mcp`, over stdio JSON-RPC. Connects
//! to Forge, Codex, Cursor, Claude Code, or any MCP-compatible host.

use std::process::ExitCode;

use elicitate::mcp::ElicitateMcp;
use rmcp::ServiceExt;

#[tokio::main]
async fn main() -> ExitCode {
    init_tracing();

    let server = ElicitateMcp::new();
    let transport = rmcp::transport::io::stdio();

    let result: Result<(), Box<dyn std::error::Error>> = async {
        let server = server.serve(transport).await?;
        server.waiting().await?;
        Ok(())
    }
    .await;

    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::FAILURE
        }
    }
}

fn init_tracing() {
    use tracing_subscriber::EnvFilter;
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info"));
    let _ = tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_target(false)
        .with_writer(std::io::stderr) // never write to stdout — that's the JSON-RPC pipe
        .try_init();
}