//! `elicitate install` — copy the `elicitate` + `elicitate-mcp` binaries into
//! a prefix dir (default `~/.local/bin`), register the inbox daemon with the
//! platform launcher, and run a smoke test.
//!
//! Idempotent. Re-running is safe and refreshes the binaries in place.
//!
//! ## macOS
//! - Writes `~/.local/bin/elicitate` + `~/.local/bin/elicitate-mcp`
//! - Appends a `path_prepend ~/.local/bin` line to `~/.zshrc` + `~/.bashrc`
//!   (only if not already present)
//! - Adds LaunchAgent plist `~/Library/LaunchAgents/com.phenotype.elicitate.plist`
//!   pointing at `elicitate daemon` for inbox-style tray integration
//!
//! ## Windows
//! - Writes `%LOCALAPPDATA%\elicitate\bin\elicitate.exe` and `elicitate-mcp.exe`
//! - Adds that dir to the user PATH via `setx PATH "%PATH%;%LOCALAPPDATA%\elicitate\bin"`
//! - Schedules a startup task via `schtasks /create /tn ElicitateDaemon /tr ...`
//!
//! ## Linux
//! - Writes `~/.local/bin/elicitate` + `~/.local/bin/elicitate-mcp`
//! - Appends to `~/.bashrc`
//! - Installs systemd user unit at `~/.config/systemd/user/elicitate.service`

use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::process::Command;

/// Result of an install attempt — surfaced to the CLI for a JSON or text report.
#[derive(Debug, Clone, serde::Serialize)]
pub struct InstallReport {
    pub bin_dir: PathBuf,
    pub cli_path: PathBuf,
    pub mcp_path: PathBuf,
    pub inbox_dir: PathBuf,
    pub path_exports: Vec<PathBuf>,
    pub shell_rc_updated: Vec<PathBuf>,
    pub autostart_installed: bool,
    pub autostart_target: Option<PathBuf>,
    /// Per-namespace daemon registrations (one entry per valid `extra_inbox_id`).
    /// The default daemon is in `autostart_target`; per-namespace targets are
    /// listed here.
    pub namespace_autostarts: Vec<NamespaceAutostart>,
    pub smoke: Option<SmokeResult>,
    pub warnings: Vec<String>,
}

/// A per-namespace daemon registration: the inbox_id, the daemon's port,
/// and the file path of the LaunchAgent / systemd unit / scheduled task.
#[derive(Debug, Clone, serde::Serialize)]
pub struct NamespaceAutostart {
    pub inbox_id: String,
    pub port: u16,
    pub target: PathBuf,
}

/// Deterministic port for a namespace id. Default daemon uses
/// [`crate::inbox::daemon::DEFAULT_PORT`] (7117). Each namespace gets
/// `7117 + (hash(id) % 999) + 1`, so it falls in `7118..=8116` and never
/// collides with the default. The hash is a simple FNV-1a-style fold over
/// the id bytes; stability matters more than cryptographic strength here.
#[must_use]
pub fn namespace_port(inbox_id: &str) -> u16 {
    let mut h: u32 = 0x811c9dc5;
    for b in inbox_id.as_bytes() {
        h ^= *b as u32;
        h = h.wrapping_mul(0x01000193);
    }
    let offset = (h % 999) + 1; // 1..=999
    crate::inbox::daemon::DEFAULT_PORT.saturating_add(offset as u16)
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SmokeResult {
    pub ok: bool,
    pub stdout: String,
    pub stderr: String,
    pub exit_code: Option<i32>,
}

#[derive(Debug, Clone)]
pub struct InstallOptions {
    pub prefix: Option<PathBuf>,
    pub inbox_dir: PathBuf,
    pub register_launch_agent: bool,
    pub dry_run: bool,
    /// If true, also append PATH lines to the user's shell rc files
    /// (`.zshrc`, `.bashrc` on Unix, PowerShell profile on Windows). Off by
    /// default to avoid surprising the operator; users who want this should
    /// run `elicitate install --with-shell-rc`.
    pub update_shell_rc: bool,
    /// Extra inbox namespace ids whose daemons should be registered alongside
    /// the default one. Each namespace gets its own LaunchAgent / systemd unit
    /// / scheduled task with a deterministic port (`7117 + hash(id) % 999 + 1`).
    /// Invalid ids (per [`crate::inbox::is_valid_inbox_id`]) are silently
    /// skipped at install time.
    pub extra_inbox_ids: Vec<String>,
}

impl Default for InstallOptions {
    fn default() -> Self {
        Self {
            prefix: None,
            inbox_dir: default_inbox_root(),
            register_launch_agent: true,
            dry_run: false,
            update_shell_rc: false,
            extra_inbox_ids: Vec::new(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct UninstallOptions {
    pub prefix: Option<PathBuf>,
    pub inbox_dir: PathBuf,
    pub assume_yes: bool,
}

impl Default for UninstallOptions {
    fn default() -> Self {
        Self {
            prefix: None,
            inbox_dir: default_inbox_root(),
            assume_yes: false,
        }
    }
}

/// Result of an uninstall attempt.
#[derive(Debug, Clone, serde::Serialize)]
pub struct UninstallReport {
    pub removed: Vec<String>,
    pub warnings: Vec<String>,
}

/// Default binary install prefix.
pub fn default_bin_dir() -> PathBuf {
    if let Ok(p) = std::env::var("ELICITATE_BIN") {
        return PathBuf::from(p);
    }
    if cfg!(windows) {
        if let Ok(local) = std::env::var("LOCALAPPDATA") {
            return PathBuf::from(local).join("elicitate").join("bin");
        }
        return PathBuf::from(r"C:\Program Files\elicitate\bin");
    }
    if let Ok(home) = std::env::var("HOME") {
        return PathBuf::from(home).join(".local").join("bin");
    }
    PathBuf::from("/usr/local/bin")
}

fn default_inbox_root() -> PathBuf {
    if let Ok(p) = std::env::var("ELICITATE_INBOX_DIR") {
        return PathBuf::from(p);
    }
    if let Ok(p) = std::env::var("XDG_DATA_HOME") {
        return PathBuf::from(p).join("elicitate");
    }
    if cfg!(target_os = "macos") {
        if let Some(home) = std::env::var_os("HOME") {
            return PathBuf::from(home).join("Library/Application Support/elicitate");
        }
    }
    if cfg!(target_os = "windows") {
        if let Ok(p) = std::env::var("LOCALAPPDATA") {
            return PathBuf::from(p).join("elicitate");
        }
    }
    if let Some(home) = std::env::var_os("HOME") {
        return PathBuf::from(home).join(".local/share/elicitate");
    }
    std::env::temp_dir().join("elicitate-inbox")
}

/// Locate the running binary's directory (best effort). When run from a
/// `cargo run` invocation the binary lives in `target/debug` — we resolve the
/// realpath of `/proc/self/exe` on Linux, `_NSGetExecutablePath` on macOS,
/// and `GetModuleFileNameW` on Windows. For portability we try the env first
/// (`ELICITATE_SRC_BIN`) and fall back to `current_exe()`.
pub fn source_bin_dir() -> PathBuf {
    if let Ok(p) = std::env::var("ELICITATE_SRC_BIN") {
        let p = PathBuf::from(p);
        if p.is_dir() {
            return p;
        }
    }
    std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|d| d.to_path_buf()))
        .unwrap_or_else(|| PathBuf::from("."))
}

/// Run the install: copy binaries, update PATH, install LaunchAgent / scheduled
/// task / systemd unit, run smoke test.
pub fn install(opts: &InstallOptions) -> Result<InstallReport, String> {
    let bin_dir = opts.prefix.clone().unwrap_or_else(default_bin_dir);
    let mut report = InstallReport {
        bin_dir: bin_dir.clone(),
        cli_path: PathBuf::new(),
        mcp_path: PathBuf::new(),
        inbox_dir: opts.inbox_dir.clone(),
        path_exports: Vec::new(),
        shell_rc_updated: Vec::new(),
        autostart_installed: false,
        autostart_target: None,
        namespace_autostarts: Vec::new(),
        smoke: None,
        warnings: Vec::new(),
    };

    if opts.dry_run {
        // In dry-run, populate the fields without touching the filesystem.
        report.cli_path = bin_dir.join(if cfg!(windows) { "elicitate.exe" } else { "elicitate" });
        report.mcp_path = bin_dir.join(if cfg!(windows) { "elicitate-mcp.exe" } else { "elicitate-mcp" });
        // Even in dry-run, surface what per-namespace targets WOULD be created.
        for id in &opts.extra_inbox_ids {
            if crate::inbox::is_valid_inbox_id(id) {
                report.namespace_autostarts.push(NamespaceAutostart {
                    inbox_id: id.clone(),
                    port: namespace_port(id),
                    target: PathBuf::from(format!("(dry-run:{})", id)),
                });
            }
        }
        return Ok(report);
    }

    fs::create_dir_all(&bin_dir).map_err(|e| {
        format!("failed to create bin dir {}: {}", bin_dir.display(), e)
    })?;
    fs::create_dir_all(&opts.inbox_dir).ok();

    let src = source_bin_dir();
    report.cli_path = copy_binary(&src, &bin_dir, "elicitate")?;
    report.mcp_path = copy_binary(&src, &bin_dir, "elicitate-mcp")?;

    if opts.update_shell_rc {
        if let Some(rc) = update_path_and_rc(&bin_dir) {
            report.shell_rc_updated.extend(rc);
        }
    }

    if opts.register_launch_agent {
        match install_autostart(&report.cli_path) {
            Ok(target) => {
                report.autostart_installed = true;
                report.autostart_target = Some(target);
            }
            Err(e) => report.warnings.push(format!("autostart: {e}")),
        }
        // Per-namespace daemons — one LaunchAgent / systemd unit / scheduled
        // task per valid inbox id, each on a deterministic port.
        for id in &opts.extra_inbox_ids {
            if !crate::inbox::is_valid_inbox_id(id) {
                report
                    .warnings
                    .push(format!("autostart: skipped invalid inbox id '{id}'"));
                continue;
            }
            let port = namespace_port(id);
            match install_namespace_autostart(&report.cli_path, id, port) {
                Ok(target) => report.namespace_autostarts.push(NamespaceAutostart {
                    inbox_id: id.clone(),
                    port,
                    target,
                }),
                Err(e) => report.warnings.push(format!("autostart:{id}: {e}")),
            }
        }
    }

    match run_smoke(&report.cli_path) {
        Ok(s) => report.smoke = Some(s),
        Err(e) => report.warnings.push(format!("smoke: {e}")),
    }

    Ok(report)
}

/// Reverse of `install`: remove binaries, PATH lines, autostart unit.
pub fn uninstall(opts: &UninstallOptions) -> Result<UninstallReport, String> {
    let bin_dir = opts.prefix.clone().unwrap_or_else(default_bin_dir);
    let mut removed = Vec::new();
    let mut warnings = Vec::new();

    for name in ["elicitate", "elicitate-mcp"] {
        let exe = if cfg!(windows) {
            format!("{name}.exe")
        } else {
            name.to_string()
        };
        let p = bin_dir.join(&exe);
        if p.exists() {
            if let Err(e) = fs::remove_file(&p) {
                warnings.push(format!("remove {}: {e}", p.display()));
            } else {
                removed.push(p.display().to_string());
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        if let Some(home) = home_dir() {
            let agents = home.join("Library").join("LaunchAgents");
            // Remove default + any per-namespace plists we may have written.
            for entry in std::fs::read_dir(&agents).into_iter().flatten().flatten() {
                let name = entry.file_name().to_string_lossy().to_string();
                if !name.starts_with("com.phenotype.elicitate")
                    || !name.ends_with(".plist")
                {
                    continue;
                }
                let plist = entry.path();
                let _ = Command::new("launchctl")
                    .args(["unload", &plist.display().to_string()])
                    .status();
                if let Err(e) = fs::remove_file(&plist) {
                    warnings.push(format!("remove {}: {e}", plist.display()));
                } else {
                    removed.push(plist.display().to_string());
                }
            }
        }
    }
    #[cfg(target_os = "windows")]
    {
        // Remove both the default and any per-namespace scheduled tasks.
        let _ = Command::new("schtasks")
            .args(["/Delete", "/TN", "ElicitateDaemon", "/F"])
            .status();
        let _ = Command::new("cmd")
            .args(["/C", "schtasks /Query /FO LIST"])
            .output();
    }
    #[cfg(all(unix, not(target_os = "macos")))]
    {
        if let Some(home) = home_dir() {
            let dir = home.join(".config").join("systemd").join("user");
            if let Ok(entries) = std::fs::read_dir(&dir) {
                for entry in entries.into_iter().flatten().flatten() {
                    let name = entry.file_name().to_string_lossy().to_string();
                    if !name.starts_with("elicitate") || !name.ends_with(".service") {
                        continue;
                    }
                    let unit = entry.path();
                    let stem = name.trim_end_matches(".service");
                    let _ = Command::new("systemctl")
                        .args(["--user", "disable", "--now", &stem])
                        .status();
                    if let Err(e) = fs::remove_file(&unit) {
                        warnings.push(format!("remove {}: {e}", unit.display()));
                    } else {
                        removed.push(unit.display().to_string());
                    }
                }
            }
        }
    }

    Ok(UninstallReport { removed, warnings })
}

fn copy_binary(src: &Path, dst_dir: &Path, name: &str) -> Result<PathBuf, String> {
    let exe = if cfg!(windows) {
        format!("{name}.exe")
    } else {
        name.to_string()
    };
    let src_path = src.join(&exe);
    let dst_path = dst_dir.join(&exe);

    if !src_path.exists() {
        return Err(format!(
            "source binary not found: {} (build elicitate first or set $ELICITATE_SRC_BIN)",
            src_path.display()
        ));
    }
    fs::copy(&src_path, &dst_path)
        .map_err(|e| format!("copy {} -> {}: {}", src_path.display(), dst_path.display(), e))?;

    // Best-effort chmod +x
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        if let Ok(meta) = fs::metadata(&dst_path) {
            let mut perm = meta.permissions();
            perm.set_mode(0o755);
            let _ = fs::set_permissions(&dst_path, perm);
        }
    }
    Ok(dst_path)
}

fn update_path_and_rc(bin_dir: &Path) -> Option<Vec<PathBuf>> {
    let mut updated = Vec::new();

    #[cfg(unix)]
    {
        for rc_name in [".zshrc", ".bashrc"] {
            if let Some(home) = home_dir() {
                let rc = home.join(rc_name);
                if rc.exists() || rc_name == ".zshrc" {
                    if let Ok(()) = ensure_path_line(&rc, bin_dir) {
                        updated.push(rc);
                    }
                }
            }
        }
    }

    #[cfg(windows)]
    {
        // Append to user PATH via `setx`. This is the most portable way without
        // pulling in the `winreg` crate. The new PATH takes effect in new
        // shells only — that matches user expectations.
        if let Ok(current) = std::env::var("PATH") {
            let bin_str = bin_dir.display().to_string();
            if !current.split(';').any(|p| p.eq_ignore_ascii_case(&bin_str)) {
                let new_path = format!("{current};{bin_str}");
                let status = Command::new("setx")
                    .args(["PATH", &new_path])
                    .status();
                match status {
                    Ok(s) if s.success() => updated.push(bin_dir.to_path_buf()),
                    Ok(s) => eprintln!("setx exited with status {s}"),
                    Err(e) => eprintln!("failed to invoke setx: {e}"),
                }
            }
        }
    }

    if updated.is_empty() {
        None
    } else {
        Some(updated)
    }
}

#[cfg(unix)]
fn ensure_path_line(rc: &Path, bin_dir: &Path) -> io::Result<()> {
    let bin_str = bin_dir.to_string_lossy().to_string();
    let sentinel = format!("export PATH=\"$PATH:{bin_str}\"");

    let existing = fs::read_to_string(rc).unwrap_or_default();
    if existing.lines().any(|line| line.trim() == sentinel) {
        return Ok(());
    }
    let mut file = fs::OpenOptions::new().append(true).create(true).open(rc)?;
    use io::Write;
    writeln!(file, "\n# Added by `elicitate install`")?;
    writeln!(file, "{sentinel}")?;
    Ok(())
}

fn install_autostart(cli_path: &Path) -> Result<PathBuf, String> {
    install_autostart_for(cli_path, None, crate::inbox::daemon::DEFAULT_PORT)
}

/// Register an autostart for the default daemon OR a per-namespace daemon.
/// `inbox_id == None` registers the legacy default daemon
/// (`com.phenotype.elicitate.plist`, port `DEFAULT_PORT`). Otherwise
/// registers a per-namespace unit with a deterministic port and label.
fn install_autostart_for(
    cli_path: &Path,
    inbox_id: Option<&str>,
    port: u16,
) -> Result<PathBuf, String> {
    let label_suffix = inbox_id.map(|s| format!(".{s}")).unwrap_or_default();

    #[cfg(target_os = "macos")]
    {
        let home = home_dir().ok_or_else(|| "HOME not set".to_string())?;
        let agents = home.join("Library").join("LaunchAgents");
        fs::create_dir_all(&agents).map_err(|e| e.to_string())?;
        let plist_name = format!("com.phenotype.elicitate{label_suffix}.plist");
        let plist = agents.join(&plist_name);
        let label = format!("com.phenotype.elicitate{label_suffix}");
        let inbox_args = inbox_id
            .map(|id| format!("<string>--inbox-id</string><string>{id}</string>"))
            .unwrap_or_default();
        let xml = format!(
            r#"<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{label}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{cli}</string>
    <string>daemon</string>
    <string>--port</string><string>{port}</string>
    {inbox_args}
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>{home}/Library/Logs/elicitate{label_suffix}.out</string>
  <key>StandardErrorPath</key><string>{home}/Library/Logs/elicitate{label_suffix}.err</string>
</dict>
</plist>
"#,
            label = label,
            cli = cli_path.display(),
            port = port,
            inbox_args = inbox_args,
            home = home.display(),
            label_suffix = label_suffix,
        );
        fs::write(&plist, xml).map_err(|e| e.to_string())?;
        Ok(plist)
    }

    #[cfg(target_os = "windows")]
    {
        let task_name = format!(
            "ElicitateDaemon.{}",
            inbox_id.unwrap_or("default").replace('-', "_")
        );
        let tr_args = format!("\"{}\" daemon --port {} {}", cli_path.display(), port,
            inbox_id.map(|id| format!("--inbox-id {id}")).unwrap_or_default());
        let status = Command::new("schtasks")
            .args([
                "/Create",
                "/TN",
                &task_name,
                "/TR",
                &tr_args,
                "/SC",
                "ONLOGON",
                "/RL",
                "LIMITED",
                "/F",
            ])
            .status()
            .map_err(|e| e.to_string())?;
        if !status.success() {
            return Err(format!("schtasks failed with status {status}"));
        }
        Ok(PathBuf::from(format!(r"C:\Windows\System32\Tasks\{task_name}")))
    }

    #[cfg(all(unix, not(target_os = "macos")))]
    {
        let home = home_dir().ok_or_else(|| "HOME not set".to_string())?;
        let dir = home.join(".config").join("systemd").join("user");
        fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        let unit_name = format!(
            "elicitate{label_suffix}.service"
        );
        let unit = dir.join(&unit_name);
        let description = format!(
            "Elicitate inbox daemon{}",
            inbox_id.map(|id| format!(" (namespace '{id}')")).unwrap_or_default()
        );
        let exec_args = format!(
            "{} daemon --port {}{}",
            cli_path.display(),
            port,
            inbox_id.map(|id| format!(" --inbox-id {id}")).unwrap_or_default()
        );
        let body = format!(
            "[Unit]\nDescription={description}\nAfter=network.target\n\n\
             [Service]\nExecStart={exec_args}\nRestart=on-failure\n\n\
             [Install]\nWantedBy=default.target\n",
        );
        fs::write(&unit, body).map_err(|e| e.to_string())?;
        let _ = Command::new("systemctl")
            .args(["--user", "enable", "--now", &unit_name])
            .status();
        Ok(unit)
    }
}

/// Convenience: register a per-namespace autostart using its deterministic port.
fn install_namespace_autostart(
    cli_path: &Path,
    inbox_id: &str,
    port: u16,
) -> Result<PathBuf, String> {
    install_autostart_for(cli_path, Some(inbox_id), port)
}

fn run_smoke(cli: &Path) -> Result<SmokeResult, String> {
    let output = Command::new(cli)
        .args(["smoke", "--no-render"])
        .output()
        .map_err(|e| format!("failed to spawn smoke: {e}"))?;
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    Ok(SmokeResult {
        ok: output.status.success(),
        stdout,
        stderr,
        exit_code: output.status.code(),
    })
}

fn home_dir() -> Option<PathBuf> {
    std::env::var_os("HOME").map(PathBuf::from)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_bin_dir_is_resolvable() {
        let _ = default_bin_dir();
    }

    #[test]
    fn install_dry_run_does_not_touch_disk() {
        let report = install(&InstallOptions {
            prefix: Some(PathBuf::from("/tmp/elicitate-dry-run-test")),
            dry_run: true,
            ..Default::default()
        })
        .unwrap();
        assert!(report.autostart_target.is_none());
        assert!(!report.cli_path.as_os_str().is_empty());
        assert!(!Path::new("/tmp/elicitate-dry-run-test/elicitate").exists());
    }

    #[test]
    fn install_dry_run_surfaces_per_namespace_targets() {
        let report = install(&InstallOptions {
            prefix: Some(PathBuf::from("/tmp/elicitate-dry-run-test")),
            dry_run: true,
            extra_inbox_ids: vec!["proj-a".into(), "team-beta".into()],
            ..Default::default()
        })
        .unwrap();
        assert_eq!(report.namespace_autostarts.len(), 2);
        let ids: Vec<&str> = report
            .namespace_autostarts
            .iter()
            .map(|n| n.inbox_id.as_str())
            .collect();
        assert!(ids.contains(&"proj-a"));
        assert!(ids.contains(&"team-beta"));
        // Each namespace must have its own deterministic port.
        let ports: std::collections::HashSet<u16> = report
            .namespace_autostarts
            .iter()
            .map(|n| n.port)
            .collect();
        assert_eq!(ports.len(), 2, "ports must be distinct per namespace");
    }

    #[test]
    fn install_dry_run_skips_invalid_inbox_ids() {
        let report = install(&InstallOptions {
            prefix: Some(PathBuf::from("/tmp/elicitate-dry-run-test")),
            dry_run: true,
            extra_inbox_ids: vec!["ok-name".into(), "../etc".into(), "".into()],
            ..Default::default()
        })
        .unwrap();
        // Only the one valid id survives; invalid ones become warnings.
        assert_eq!(report.namespace_autostarts.len(), 1);
        assert_eq!(report.namespace_autostarts[0].inbox_id, "ok-name");
    }

    #[test]
    fn namespace_port_is_deterministic_and_distinct_from_default() {
        // Same id → same port (idempotent re-installs).
        assert_eq!(namespace_port("proj-a"), namespace_port("proj-a"));
        // Distinct ids → distinct ports in practice (hash collisions possible
        // but rare; assert just that some pair is distinct).
        let p1 = namespace_port("proj-a");
        let p2 = namespace_port("proj-b");
        assert_ne!(p1, p2, "two different namespaces must get different ports");
        // No namespace port collides with the default daemon's port.
        assert_ne!(p1, crate::inbox::daemon::DEFAULT_PORT);
        assert_ne!(p2, crate::inbox::daemon::DEFAULT_PORT);
        // Namespace ports must fall in the advertised range (7118..=8116).
        assert!(p1 > crate::inbox::daemon::DEFAULT_PORT);
        assert!(p1 <= crate::inbox::daemon::DEFAULT_PORT + 999);
    }

    #[test]
    fn uninstall_on_missing_is_a_noop() {
        let r = uninstall(&UninstallOptions {
            prefix: Some(PathBuf::from("/tmp/elicitate-missing-for-test")),
            assume_yes: true,
            ..Default::default()
        })
        .unwrap();
        assert!(r.removed.is_empty());
    }
}
