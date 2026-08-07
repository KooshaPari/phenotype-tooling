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
    // CRITICAL: flush after each writeln. The stdio pipe buffer may not
    // be flushed before the test calls drop(child.stdin.take()), causing
    // the server to only see 1-2 of the 3 messages — this is the source
    // of the well-known parallel-mode flake.
    stdin.flush().unwrap();

    // 2. initialized notification
    let notif = r#"{"jsonrpc":"2.0","method":"notifications/initialized"}"#;
    writeln!(stdin, "{}", notif).unwrap();
    stdin.flush().unwrap();

    // 3. tools/list
    let list = r#"{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}"#;
    writeln!(stdin, "{}", list).unwrap();
    stdin.flush().unwrap();

    // Give the server a brief moment to drain its read loop before we close
    // stdin. Without this, on slow / loaded runners, the server may EOF
    // before processing the third message.
    std::thread::sleep(std::time::Duration::from_millis(50));

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

/// Concurrent stdio smoke test — locks in the parallel-mode handshake fix.
/// Spawns N elicit-mcp children in parallel, runs the same 3-message
/// handshake against each, and asserts all of them return ≥2 lines.
/// This is the regression test for the well-known flake where `writeln!`
/// to a stdio pipe doesn't auto-flush before the test closes stdin.
#[test]
fn mcp_handshake_concurrent_parallel_children() {
    use std::io::Write;
    use std::process::{Command, Stdio};
    use std::sync::Arc;
    use std::thread;

    const N: usize = 6;

    let init = r#"{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke-test","version":"0.0.1"}}}"#;
    let notif = r#"{"jsonrpc":"2.0","method":"notifications/initialized"}"#;
    let list = r#"{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}"#;

    let results: Arc<std::sync::Mutex<Vec<(usize, Result<usize, String>)>>> =
        Arc::new(std::sync::Mutex::new(Vec::with_capacity(N)));

    let mut handles = Vec::with_capacity(N);
    for i in 0..N {
        let init = init.to_string();
        let notif = notif.to_string();
        let list = list.to_string();
        let results = Arc::clone(&results);

        let handle = thread::spawn(move || {
            let mut child = match Command::new("elicitate-mcp")
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
            {
                Ok(c) => c,
                Err(e) => {
                    results.lock().unwrap().push((i, Err(format!("spawn: {e}"))));
                    return;
                }
            };

            let stdin = child.stdin.as_mut().unwrap();
            // Write the handshake with explicit flushes between messages.
            // This is the fix for the parallel-mode flake.
            let mut write_all = |results: &mut Vec<(usize, Result<usize, String>)>| -> bool {
                if let Err(e) = writeln!(stdin, "{}", init).and_then(|()| stdin.flush()) {
                    results.push((i, Err(format!("write init: {e}"))));
                    return false;
                }
                if let Err(e) = writeln!(stdin, "{}", notif).and_then(|()| stdin.flush()) {
                    results.push((i, Err(format!("write notif: {e}"))));
                    return false;
                }
                if let Err(e) = writeln!(stdin, "{}", list).and_then(|()| stdin.flush()) {
                    results.push((i, Err(format!("write list: {e}"))));
                    return false;
                }
                true
            };
            if !write_all(&mut results.lock().unwrap()) {
                return;
            }
            // Brief settle to let the server drain its read loop.
            thread::sleep(std::time::Duration::from_millis(50));
            drop(child.stdin.take());

            let output = match child.wait_with_output() {
                Ok(o) => o,
                Err(e) => {
                    results.lock().unwrap().push((i, Err(format!("wait: {e}"))));
                    return;
                }
            };

            let lines = String::from_utf8_lossy(&output.stdout).lines().count();
            results.lock().unwrap().push((i, Ok(lines)));
        });
        handles.push(handle);
    }

    for h in handles {
        h.join().unwrap();
    }

    let results = results.lock().unwrap().clone();
    assert_eq!(results.len(), N, "all N children must complete");

    let mut failures: Vec<String> = Vec::new();
    for (i, r) in results {
        match r {
            Ok(lines) if lines >= 2 => {}
            Ok(lines) => failures.push(format!("child {i}: only {lines} lines")),
            Err(e) => failures.push(format!("child {i}: error: {e}")),
        }
    }
    assert!(
        failures.is_empty(),
        "concurrent handshake failed: {} (of {N} children)\n{}",
        failures.len(),
        failures.join("\n"),
    );
}

// ─── smoke: elicitate CLI ──────────────────────────────────────────

#[test]
fn elicitate_smoke_reports_ok() {
    // `elicitate smoke` tries to render a native popup, which requires a GUI
    // session. In headless contexts (CI, SSH without DISPLAY) the popup
    // can't render and the command exits non-zero. We treat that as OK as
    // long as the binary itself runs and reports a meaningful result.
    //
    // Two acceptable outcomes:
    //   (a) GUI session present  -> "smoke ok" / similar success message
    //   (b) GUI session absent   -> a non-zero exit mentioning popup/display
    //
    // Both prove the binary is wired up. Only a "command not found" or
    // "library not loaded" is a hard failure.
    let output = std::process::Command::new("elicitate")
        .arg("smoke")
        .output()
        .expect("failed to invoke elicitate binary");

    let stderr = String::from_utf8_lossy(&output.stderr);
    let stdout = String::from_utf8_lossy(&output.stdout);
    let combined = format!("{}{}", stdout, stderr);

    assert!(
        output.status.success()
            || combined.contains("popup")
            || combined.contains("display")
            || combined.contains("GTK")
            || combined.contains("not supported"),
        "elicitate smoke failed in an unexpected way. exit={:?}\nstdout: {}\nstderr: {}",
        output.status,
        stdout.chars().take(300).collect::<String>(),
        stderr.chars().take(300).collect::<String>(),
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
