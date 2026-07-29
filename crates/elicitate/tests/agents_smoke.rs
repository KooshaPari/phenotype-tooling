//! Cross-client smoke tests — verify each installed agent has a valid
//! elicate MCP config entry, and the MCP server responds to the standard
//! handshake.

use std::fs;
use std::path::PathBuf;

// ─── helpers ────────────────────────────────────────────────────────
fn home() -> PathBuf {
    dirs::home_dir().expect("$HOME")
}

fn agent_config_exists(path: &str) -> bool {
    let p = home().join(path);
    p.exists()
}

fn config_contains(path: &str, needle: &str) -> bool {
    let p = home().join(path);
    match fs::read_to_string(&p) {
        Ok(content) => content.contains(needle),
        Err(_) => false,
    }
}

// ─── per-agent config presence tests ────────────────────────────────

#[test]
fn forgecode_plugin_toml_exists() {
    let p = home().join("CodeProjects/Phenotype/repos/phenotype-tooling")
        .join(".forgecode/plugins/elicitate/plugin.toml");
    assert!(p.exists(), "forgecode plugin.toml missing at {}", p.display());
    let content = fs::read_to_string(&p).unwrap();
    assert!(content.contains("elicitate-mcp"), "plugin.toml must reference elicitate-mcp");
}

#[test]
fn codex_mcp_toml_has_elicitate() {
    if !agent_config_exists(".codex/mcp.toml") {
        eprintln!("SKIP: ~/.codex/mcp.toml not found");
        return;
    }
    assert!(
        config_contains(".codex/mcp.toml", "elicitate"),
        "~/.codex/mcp.toml must register elicitate"
    );
}

#[test]
fn cursor_mcp_json_has_elicitate() {
    if !agent_config_exists(".cursor/mcp.json") {
        eprintln!("SKIP: ~/.cursor/mcp.json not found");
        return;
    }
    assert!(
        config_contains(".cursor/mcp.json", "elicitate"),
        "~/.cursor/mcp.json must register elicitate"
    );
}

#[test]
fn claude_json_has_elicitate() {
    if !agent_config_exists(".claude.json") {
        eprintln!("SKIP: ~/.claude.json not found");
        return;
    }
    assert!(
        config_contains(".claude.json", "elicitate"),
        "~/.claude.json must register elicitate in mcpServers"
    );
}

#[test]
fn kilo_jsonc_has_elicitate() {
    if !agent_config_exists(".config/kilo/kilo.jsonc") {
        eprintln!("SKIP: ~/.config/kilo/kilo.jsonc not found");
        return;
    }
    assert!(
        config_contains(".config/kilo/kilo.jsonc", "elicitate"),
        "~/.config/kilo/kilo.jsonc must register elicitate"
    );
}

#[test]
fn droid_mcp_json_has_elicitate() {
    if !agent_config_exists(".factory/mcp.json") {
        eprintln!("SKIP: ~/.factory/mcp.json not found");
        return;
    }
    assert!(
        config_contains(".factory/mcp.json", "elicitate"),
        "~/.factory/mcp.json must register elicitate"
    );
}

#[test]
fn elicitate_mcp_is_on_path() {
    assert!(
        which::which("elicitate-mcp").is_ok(),
        "elicitate-mcp must be on $PATH"
    );
}

// ─── MCP handshake smoke test ──────────────────────────────────────

#[test]
fn mcp_handshake_initialize_and_list_tools() {
    use std::io::Write;
    use std::process::{Command, Stdio};

    let mut child = Command::new("elicitate-mcp")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("failed to spawn elicitate-mcp");

    let stdin = child.stdin.as_mut().unwrap();

    // 1. initialize
    let init = r#"{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke-test","version":"0.0.1"}}}"#;
    writeln!(stdin, "{}", init).unwrap();

    // 2. initialized notification
    let notif = r#"{"jsonrpc":"2.0","method":"notifications/initialized"}"#;
    writeln!(stdin, "{}", notif).unwrap();

    // 3. tools/list
    let list = r#"{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}"#;
    writeln!(stdin, "{}", list).unwrap();

    // close stdin so the server sees EOF and exits after processing
    drop(child.stdin.take());

    let output = child
        .wait_with_output()
        .expect("failed to wait for elicitate-mcp");

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    // The server should emit at least 2 JSON responses (initialize + tools/list)
    let lines: Vec<&str> = stdout.lines().collect();
    assert!(
        lines.len() >= 2,
        "expected ≥2 JSON responses from elicitate-mcp, got {} (stdout: {}, stderr: {})",
        lines.len(),
        stdout.chars().take(500).collect::<String>(),
        stderr.chars().take(500).collect::<String>()
    );

    // Parse tools/list response — must contain "elicitate_mcp"
    let tools_resp = lines.last().expect("no last line");
    let parsed: serde_json::Value =
        serde_json::from_str(tools_resp).expect("tools/list response is not valid JSON");

    assert_eq!(
        parsed["id"], 2,
        "expected id:2 in tools/list response"
    );

    let tools = parsed["result"]["tools"]
        .as_array()
        .expect("tools/list result.tools is not an array");

    let names: Vec<&str> = tools
        .iter()
        .filter_map(|t| t["name"].as_str())
        .collect();

    assert!(
        names.contains(&"elicitate_mcp"),
        "tools/list must include 'elicitate_mcp', got: {:?}",
        names
    );
}

// ─── smoke: elicitate CLI ──────────────────────────────────────────

#[test]
fn elicitate_smoke_reports_ok() {
    let output = std::process::Command::new("elicitate")
        .arg("smoke")
        .output()
        .expect("failed to run elicitate smoke");

    let stderr = String::from_utf8_lossy(&output.stderr);
    // smoke should exit 0 even if the popup times out (it reports OK or popup timeout)
    assert!(
        output.status.success(),
        "elicitate smoke exited with {:?} — stderr: {}",
        output.status,
        stderr.chars().take(500).collect::<String>()
    );
}

#[test]
fn elicitate_version_reports_semver() {
    let output = std::process::Command::new("elicitate")
        .arg("--version")
        .output()
        .expect("failed to run elicitate --version");

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("elicitate"),
        "expected 'elicitate' in --version output, got: {}",
        stdout
    );
    assert!(
        output.status.success(),
        "elicitate --version failed"
    );
}

#[test]
fn elicitate_schema_exports_valid_json() {
    let output = std::process::Command::new("elicitate")
        .arg("schema")
        .output()
        .expect("failed to run elicitate schema");

    let stdout = String::from_utf8_lossy(&output.stdout);
    let parsed: serde_json::Value =
        serde_json::from_str(&stdout).expect("elicitate schema output is not valid JSON");

    assert!(
        parsed.get("properties").is_some(),
        "schema must have 'properties' key"
    );
    assert!(
        parsed.get("$schema").is_some(),
        "schema must have '$schema' key"
    );
}

#[test]
fn elicitate_detect_reports_platform() {
    let output = std::process::Command::new("elicitate")
        .arg("detect")
        .output()
        .expect("failed to run elicitate detect");

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("macos") || stdout.contains("linux") || stdout.contains("windows"),
        "detect must report a platform, got: {}",
        stdout
    );
    assert!(output.status.success());
}
