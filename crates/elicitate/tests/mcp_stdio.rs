//! Integration test that spawns the MCP server and exercises the
//! JSON-RPC protocol via stdin/stdout.

use std::io::Write;
use std::process::{Command, Stdio};

use elicitate::spec::PromptSpec;

fn mcp_bin() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_BIN_EXE_elicitate-mcp"))
}

#[test]
fn mcp_server_lists_tools() {
    // Spawn the MCP server and send a tools/list request.
    let mut child = Command::new(mcp_bin())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn elicitate-mcp");

    let request = serde_json::json!({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    });
    let mut stdin = child.stdin.take().expect("stdin");
    let req_str = serde_json::to_string(&request).unwrap();
    writeln!(stdin, "{req_str}").expect("write request");
    drop(stdin); // close stdin so the server sees EOF after the request

    let out = child.wait_with_output().expect("wait");
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(
        stdout.contains("elicitate_mcp"),
        "tools/list response must include elicitate_mcp. stdout: {stdout}"
    );
    // Validate JSON shape
    let parsed: serde_json::Value =
        serde_json::from_str(stdout.trim()).expect("response is not valid JSON");
    assert_eq!(parsed["jsonrpc"], "2.0");
    assert_eq!(parsed["id"], 1);
}

#[test]
fn mcp_server_rejects_unknown_tool() {
    let mut child = Command::new(mcp_bin())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn elicitate-mcp");

    let request = serde_json::json!({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "no_such_tool",
            "arguments": {}
        }
    });
    let mut stdin = child.stdin.take().expect("stdin");
    writeln!(stdin, "{}", serde_json::to_string(&request).unwrap()).expect("write");
    drop(stdin);

    let out = child.wait_with_output().expect("wait");
    let stdout = String::from_utf8_lossy(&out.stdout);
    let parsed: serde_json::Value = serde_json::from_str(stdout.trim()).unwrap_or_else(|_| {
        panic!("not valid JSON: {stdout}");
    });
    // rmcp returns an error response (not a result)
    assert!(parsed.get("error").is_some());
}

#[test]
fn mcp_server_validates_prompt_spec() {
    let mut child = Command::new(mcp_bin())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn elicitate-mcp");

    // Invalid spec — empty title
    let request = serde_json::json!({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "elicitate_mcp",
            "arguments": {
                "title": "",
                "question": "q",
                "field": { "kind": "boolean", "label": "?" }
            }
        }
    });
    let mut stdin = child.stdin.take().expect("stdin");
    writeln!(stdin, "{}", serde_json::to_string(&request).unwrap()).expect("write");
    drop(stdin);

    let out = child.wait_with_output().expect("wait");
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(
        stdout.contains("error") || stdout.contains("invalid"),
        "expected error response for invalid spec. stdout: {stdout}"
    );
}

#[test]
fn mcp_server_schema_export_is_loadable() {
    // This validates that the JSON Schema we publish via the library
    // matches the schema we'd hand to an MCP client. Drift here would
    // be a contract break.
    let schema = elicitate::schema_json();
    let prompt_spec_schema = schemars::schema_for!(PromptSpec);
    let published = serde_json::to_value(prompt_spec_schema).unwrap();
    assert_eq!(schema, published);
}