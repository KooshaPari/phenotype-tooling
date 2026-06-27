use anyhow::Result;
use chrono::Utc;
use clap::Parser;
use futures::stream::{FuturesUnordered, StreamExt};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::time::Duration;
use tokio::time;

#[derive(Parser)]
#[command(
    name = "anthropic-usage-poll",
    about = "Poll Anthropic Admin API for token usage"
)]
struct Cli {
    /// Run once and exit
    #[arg(long)]
    once: bool,
    /// Polling interval in seconds
    #[arg(long, default_value = "600")]
    interval: u64,
    /// Output path (default: ~/.claude/usage.json)
    #[arg(long)]
    output: Option<PathBuf>,
    /// Number of concurrent polls to fan out per cycle (WP-02 T2)
    #[arg(long, default_value = "8")]
    concurrent: usize,
}

#[derive(Debug, Serialize, Deserialize, Default)]
struct UsageSnapshot {
    daily_remaining: Option<u64>,
    monthly_remaining: Option<u64>,
    per_model_tokens_last_24h: serde_json::Value,
    updated_at: String,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    let output = cli.output.unwrap_or_else(default_output_path);
    if cli.once {
        poll_and_write(&output, cli.concurrent).await?;
    } else {
        let mut ticker = time::interval(Duration::from_secs(cli.interval));
        loop {
            ticker.tick().await;
            if let Err(e) = poll_and_write(&output, cli.concurrent).await {
                eprintln!("poll error: {e}");
            }
        }
    }
    Ok(())
}

fn default_output_path() -> PathBuf {
    std::env::var("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("."))
        .join(".claude")
        .join("usage.json")
}

async fn poll_and_write(output: &Path, concurrent: usize) -> Result<()> {
    let snapshot = fetch_usage_concurrent(concurrent).await?;
    write_atomic(output, &snapshot)
}

/// Fan out `concurrent` parallel polls via `FuturesUnordered`, then
/// merge into a single snapshot. Used to amortize network latency on
/// large account-fleet polling cycles.
async fn fetch_usage_concurrent(concurrent: usize) -> Result<UsageSnapshot> {
    let n = concurrent.max(1);
    let mut futures = FuturesUnordered::new();
    for _ in 0..n {
        futures.push(fetch_usage());
    }
    while let Some(_res) = futures.next().await {
        // Discard per-request results; merge is identity for the stub
        // implementation but will sum `daily_remaining` once the real
        // Admin API is wired in.
    }
    Ok(UsageSnapshot {
        daily_remaining: None,
        monthly_remaining: None,
        per_model_tokens_last_24h: serde_json::json!({}),
        updated_at: Utc::now().to_rfc3339(),
    })
}

async fn fetch_usage() -> Result<UsageSnapshot> {
    // TODO: read ANTHROPIC_ADMIN_KEY from env; skip poll if unset
    let _api_key = std::env::var("ANTHROPIC_ADMIN_KEY").unwrap_or_default();
    // TODO: add If-None-Match / ETag header to avoid redundant writes
    // TODO: GET /v1/organizations/usage_report/messages with bearer auth
    // TODO: map response body fields into UsageSnapshot
    let _client = reqwest::Client::new();
    Ok(UsageSnapshot {
        daily_remaining: None,
        monthly_remaining: None,
        per_model_tokens_last_24h: serde_json::json!({}),
        updated_at: Utc::now().to_rfc3339(),
    })
}

fn write_atomic(path: &Path, snapshot: &UsageSnapshot) -> Result<()> {
    // TODO: write to a sibling temp file then fs::rename for atomicity
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(snapshot)?;
    std::fs::write(path, json)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_snapshot_serializes() {
        let s = UsageSnapshot::default();
        let json = serde_json::to_string(&s).expect("serialize");
        assert!(json.contains("updated_at"));
    }

    #[test]
    fn default_output_path_contains_claude() {
        let p = default_output_path();
        assert!(p.to_string_lossy().contains(".claude"));
    }

    #[test]
    fn concurrent_arg_parses() {
        let cli = Cli::try_parse_from(["anthropic-usage-poll", "--once", "--concurrent", "16"]).unwrap();
        assert_eq!(cli.concurrent, 16);
        assert!(cli.once);
    }
}
