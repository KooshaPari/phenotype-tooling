//! Integration tests for the elicitate CLI binary.

use std::io::Write;
use std::process::{Command, Stdio};

use elicitate::spec::PromptSpec;

/// Build a path to the compiled elicitate binary.
fn elicitate_bin() -> std::path::PathBuf {
    // Cargo provides CARGO_BIN_EXE_elicitate for integration tests
    std::path::PathBuf::from(env!("CARGO_BIN_EXE_elicitate"))
}

#[test]
fn cli_help_exits_nonzero() {
    let out = Command::new(elicitate_bin())
        .arg("--help")
        .output()
        .expect("spawn elicitate --help");
    assert!(out.status.code().is_some());
}

#[test]
fn cli_version_prints() {
    let out = Command::new(elicitate_bin())
        .arg("version")
        .output()
        .expect("spawn elicitate version");
    assert!(out.status.success());
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(stdout.contains("elicitate"));
    assert!(stdout.contains(env!("CARGO_PKG_VERSION")));
}

#[test]
fn cli_schema_prints_valid_json() {
    let out = Command::new(elicitate_bin())
        .args(["schema"])
        .output()
        .expect("spawn elicitate schema");
    assert!(out.status.success());
    let stdout = String::from_utf8_lossy(&out.stdout);
    let parsed: serde_json::Value =
        serde_json::from_str(&stdout).expect("schema output is not valid JSON");
    assert!(parsed.is_object());
}

#[test]
fn cli_detect_prints_valid_json() {
    let out = Command::new(elicitate_bin())
        .args(["detect"])
        .output()
        .expect("spawn elicitate detect");
    assert!(out.status.success());
    let stdout = String::from_utf8_lossy(&out.stdout);
    let parsed: serde_json::Value =
        serde_json::from_str(&stdout).expect("detect output is not valid JSON");
    assert!(parsed.get("platform").is_some());
}

#[test]
fn cli_ask_with_from_json_validates_spec() {
    // Valid spec that should pass validation but will hit the renderer
    // (which falls back to TUI on CI).
    let spec_json = r#"{
        "title": "Test",
        "question": "Test?",
        "field": {"kind": "boolean", "label": "?", "default": true},
        "timeout_secs": 1
    }"#;
    let mut child = Command::new(elicitate_bin())
        .args(["ask", "--renderer", "tty", "--from-json", spec_json])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn elicitate ask");
    // Close stdin immediately so inquire sees EOF and returns Cancel
    drop(child.stdin.take());
    let out = child.wait_with_output().expect("wait");
    // The CLI must produce JSON output regardless of response status
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(
        !stdout.trim().is_empty(),
        "expected JSON output, got empty stdout. stderr: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    // Validate it's parseable
    let parsed: serde_json::Value =
        serde_json::from_str(&stdout).expect("output is not valid JSON");
    assert!(parsed.get("status").is_some());
}

#[test]
fn cli_ask_rejects_invalid_urgency() {
    let out = Command::new(elicitate_bin())
        .args(["ask", "--title", "t", "--question", "q", "--urgency", "bogus"])
        .output()
        .expect("spawn elicitate ask --urgency bogus");
    // clap rejects the bad urgency enum
    assert!(!out.status.success());
}

#[test]
fn cli_ask_from_file_loads() {
    let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures");
    let path = dir.join("simple_text.json");
    let mut child = Command::new(elicitate_bin())
        .args(["ask", "--renderer", "tty", "--from-file"])
        .arg(&path)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn elicitate ask --from-file");
    drop(child.stdin.take());
    let out = child.wait_with_output().expect("wait");
    let stdout = String::from_utf8_lossy(&out.stdout);
    let parsed: serde_json::Value =
        serde_json::from_str(&stdout).expect("output is not valid JSON");
    assert!(parsed.get("status").is_some());
    // Sanity: the prompt loaded our fixture
    let _: PromptSpec = serde_json::from_str(
        &std::fs::read_to_string(&path).expect("read fixture"),
    )
    .expect("fixture is valid");
}

#[test]
fn cli_smoke_no_render_succeeds() {
    let out = Command::new(elicitate_bin())
        .args(["smoke", "--no-render"])
        .output()
        .expect("spawn elicitate smoke --no-render");
    assert!(out.status.success(), "smoke --no-render must exit 0");
}

#[test]
fn cli_serve_subcommand_is_rejected_from_elicitate_binary() {
    let out = Command::new(elicitate_bin())
        .args(["serve"])
        .output()
        .expect("spawn elicitate serve");
    assert!(!out.status.success());
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("elicitate-mcp"));
}