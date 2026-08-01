//! Regression tests for the checked-in MCP client registrations.
//!
//! `elicitate-mcp` is itself the MCP server entrypoint.  It does not expose a
//! `serve` subcommand, so host configurations must launch it without args.

use std::fs;
use std::path::{Path, PathBuf};

use serde_json::Value;

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn assert_json_registration_has_no_args(path: &Path) {
    let content = fs::read_to_string(path).unwrap_or_else(|error| {
        panic!("failed to read MCP config {}: {error}", path.display())
    });
    let config: Value = serde_json::from_str(&content).unwrap_or_else(|error| {
        panic!("MCP config {} is not valid JSON: {error}", path.display())
    });
    let server = &config["mcpServers"]["elicitate_mcp"];
    assert_eq!(server["command"], "elicitate-mcp", "wrong command in {}", path.display());
    assert!(
        server.get("args").is_none(),
        "{} must launch elicitate-mcp without args; `serve` is not a valid subcommand",
        path.display()
    );
}

fn assert_toml_registration_has_no_args(path: &Path) {
    let content = fs::read_to_string(path).unwrap_or_else(|error| {
        panic!("failed to read MCP config {}: {error}", path.display())
    });
    assert!(
        content.lines().any(|line| line.trim() == "command = \"elicitate-mcp\""),
        "{} must register the elicitate-mcp command",
        path.display()
    );
    assert!(
        !content.lines().any(|line| line.trim_start().starts_with("args")),
        "{} must launch elicitate-mcp without args; `serve` is not a valid subcommand",
        path.display()
    );
}

#[test]
fn cursor_plugin_registration_has_no_args() {
    assert_json_registration_has_no_args(
        &repo_root().join("crates/elicitate/plugins/cursor/cursor-mcp.json"),
    );
}

#[test]
fn codex_plugin_registration_has_no_args() {
    assert_toml_registration_has_no_args(&repo_root().join("crates/elicitate/plugins/codex/codex.toml"));
}

#[test]
fn forgecode_plugin_registration_has_no_args() {
    assert_toml_registration_has_no_args(
        &repo_root().join("crates/elicitate/plugins/forgecode/plugin.toml"),
    );
}
