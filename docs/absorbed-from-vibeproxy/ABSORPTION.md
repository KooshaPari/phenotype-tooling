# Absorbed from vibeproxy

**Source:** `KooshaPari/vibeproxy` (archived and deleted from GitHub 2026-06-21)
**Target:** `phenotype-tooling/docs/absorbed-from-vibeproxy/`
**Tracked file count:** 207

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .agileplus/worklog.md
    .editorconfig
    .github/CODEOWNERS
    .github/FUNDING.yml
    .github/dependabot.yml
    .github/pull_request_template.md
    .github/release-drafter.yml
    .github/workflows/auto-release.yml
    .github/workflows/ci.yml
    .github/workflows/codeql.yml
    .github/workflows/cross-platform-test.yml
    .github/workflows/linux-build.yml
    .github/workflows/release-drafter.yml
    .github/workflows/release.yml
    .github/workflows/scorecard.yml
    .github/workflows/secrets-scan.yml
    .github/workflows/security-deep-scan.yml
    .github/workflows/trufflehog.yml
    .github/workflows/update-cliproxyapi.yml
    .gitignore
    .pre-commit-config.yaml
    AGENTS.md
    AMPCODE_SETUP.md
    CHANGELOG.md
    CLAUDE.md
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    FUNCTIONAL_REQUIREMENTS.md
    FUNDING.yml
    LICENSE
    Makefile
    PLAN.md
    PRD.md
    README.md
    SECURITY.md
    SPEC.md
    TEST_COVERAGE_MATRIX.md
    WARP.md
    appcast-x86_64.xml
    appcast.xml
    apps/linux/Cargo.toml
    apps/linux/README.md
    apps/linux/src/app.rs
    apps/linux/src/config_manager.rs
    apps/linux/src/keyring.rs
    apps/linux/src/main.rs
    apps/linux/src/server_manager.rs
    apps/linux/src/system_tray.rs
    apps/linux/src/ui.rs
    apps/macos/Info.plist
    apps/macos/NOTIFICATION_FIX.md
    apps/macos/Package.swift
    apps/macos/Sources/AppDelegate.swift
    apps/macos/Sources/AuthStatus.swift
    apps/macos/Sources/BackendClient.swift
    apps/macos/Sources/CLIProxyAPI.swift
    apps/macos/Sources/ConfigManager.swift
    apps/macos/Sources/GatewayProvider.swift
    apps/macos/Sources/GatewaySettingsView.swift
    apps/macos/Sources/IconCatalog.swift
    apps/macos/Sources/NodeConfigPanel.swift
    apps/macos/Sources/NodeGraphModels.swift
    apps/macos/Sources/RemoteProfileManager.swift
    apps/macos/Sources/RemoteProfileView.swift
    apps/macos/Sources/Resources/AppIcon.icns
    apps/macos/Sources/Resources/glyph.png
    apps/macos/Sources/Resources/icon-active.png
    apps/macos/Sources/Resources/icon-auggie.png
    apps/macos/Sources/Resources/icon-claude.png
    apps/macos/Sources/Resources/icon-codex.png
    apps/macos/Sources/Resources/icon-cursor.png
    apps/macos/Sources/Resources/icon-gemini.png
    apps/macos/Sources/Resources/icon-inactive.png
    apps/macos/Sources/Resources/icon-qwen.png
    apps/macos/Sources/RuleCanvas.swift
    apps/macos/Sources/RuleModels.swift
    apps/macos/Sources/RuleNodeView.swift
    apps/macos/Sources/RulePalette.swift
    apps/macos/Sources/RustCoreManager.swift
    apps/macos/Sources/SLMClient.swift
    apps/macos/Sources/SLMManager.swift
    apps/macos/Sources/SLMSettingsView.swift
    apps/macos/Sources/ServerManager.swift
    apps/macos/Sources/ServiceDiscoveryManager.swift
    apps/macos/Sources/ServiceItemView.swift
    apps/macos/Sources/SettingsView.swift
    apps/macos/Sources/SimpleVisualRulesEditor.swift
    apps/macos/Sources/ThinkingProxy.swift
    apps/macos/Sources/TunnelManager.swift
    apps/macos/Sources/VibeProxyCore/Models.swift
    apps/macos/Sources/VibeProxyCore/VibeProxyCore.swift
    apps/macos/Sources/VisualNodeProgrammer.swift
    apps/macos/Sources/VisualRulesEditor.swift
    apps/macos/Sources/main.swift
    apps/windows/VibeProxy.sln
    apps/windows/VibeProxy/App.xaml
    apps/windows/VibeProxy/App.xaml.cs
    apps/windows/VibeProxy/BackendClient.cs
    apps/windows/VibeProxy/ConfigManager.cs
    apps/windows/VibeProxy/CredentialManager.cs
    apps/windows/VibeProxy/MainWindow.xaml
    apps/windows/VibeProxy/MainWindow.xaml.cs
    apps/windows/VibeProxy/ServerManager.cs
    apps/windows/VibeProxy/SettingsWindow.xaml
    apps/windows/VibeProxy/SettingsWindow.xaml.cs
    apps/windows/VibeProxy/TrayIcon.cs
    apps/windows/VibeProxy/VibeProxy.csproj
    apps/windows/VibeProxy/VisualRulesEditor.xaml
    apps/windows/VibeProxy/VisualRulesEditor.xaml.cs
    apps/windows/VibeProxy/app.manifest
    apps/windows/WINDOWS_TESTING_GUIDE.md
    audit_scorecard.json
    cliff.toml
    create-app-bundle.sh
    deny.toml
    dev-live-reload.sh
    docs/.vitepress/config.mts
    docs/README.md
    docs/architecture/MONOREPO_MIGRATION.md
    docs/architecture/SERVICES_CONFIG.md
    docs/boundary/vibeproxy.md
    docs/guides/DUAL_ROUTER.md
    docs/guides/WINDOWS_UI.md
    docs/index.md
    docs/intent/vibeproxy.md
    docs/journeys/index.md
    docs/journeys/manifests/README.md
    docs/journeys/quick-start.md
    docs/operations/iconography/SPEC.md
    docs/operations/journey-traceability.md
    docs/reference/CHANGELOG.md
    docs/reference/COMPLETION_SUMMARY.md
    docs/reference/FORK_ATTRIBUTION.md
    docs/reference/MIGRATION_COMPLETE.md
    docs/setup/DEV_SETUP.md
    docs/setup/FACTORY_SETUP.md
    docs/setup/INJECT_SETUP.md
    docs/setup/INSTALLATION.md
    docs/stories/hello-world.md
    docs/stories/index.md
    docs/traceability/index.md
    entitlements.plist
    icon.png
    mise.toml
    proto/config.proto
    scripts/build-all.sh
    scripts/build-core.sh
    scripts/build-linux.sh
    scripts/build-macos.sh
    scripts/build-windows.ps1
    scripts/create-release.sh
    shared/bindings/csharp/Models.cs
    shared/bindings/csharp/VibeProxyCore.cs
    shared/bindings/csharp/VibeProxyCore.csproj
    shared/bindings/swift/Models.swift
    shared/bindings/swift/VibeProxyCore.swift
    simple-live-reload.sh
    sparkle-entitlements.plist
    src/Info.plist
    src/Package.resolved
    src/Package.swift
    src/Sources/AppDelegate.swift
    src/Sources/AuthStatus.swift
    src/Sources/CLIProxyAPI.swift
    src/Sources/GatewayProvider.swift
    src/Sources/GatewaySettingsView.swift
    src/Sources/IconCatalog.swift
    src/Sources/NodeConfigPanel.swift
    src/Sources/NodeGraphModels.swift
    src/Sources/NotificationNames.swift
    src/Sources/RemoteProfileManager.swift
    src/Sources/RemoteProfileView.swift
    src/Sources/Resources/AppIcon.icns
    src/Sources/Resources/cli-proxy-api-plus
    src/Sources/Resources/config.yaml
    src/Sources/Resources/glyph.png
    src/Sources/Resources/icon-active.png
    src/Sources/Resources/icon-antigravity.png
    src/Sources/Resources/icon-auggie.png
    src/Sources/Resources/icon-claude.png
    src/Sources/Resources/icon-codex.png
    src/Sources/Resources/icon-copilot.png
    src/Sources/Resources/icon-cursor.png
    src/Sources/Resources/icon-gemini.png
    src/Sources/Resources/icon-inactive.png
    src/Sources/Resources/icon-qwen.png
    src/Sources/Resources/icon-zai.png
    src/Sources/RuleCanvas.swift
    src/Sources/RuleModels.swift
    src/Sources/RuleNodeView.swift
    src/Sources/RulePalette.swift
    src/Sources/SLMManager.swift
    src/Sources/SLMSettingsView.swift
    src/Sources/ServerManager.swift
    src/Sources/ServiceDiscoveryManager.swift
    src/Sources/ServiceItemView.swift
    src/Sources/SettingsView.swift
    src/Sources/SimpleVisualRulesEditor.swift
    src/Sources/ThinkingProxy.swift
    src/Sources/TunnelManager.swift
    src/Sources/VisualNodeProgrammer.swift
    src/Sources/VisualRulesEditor.swift
    src/Sources/main.swift
    trufflehog.yml
    update-cli-proxy.sh
    vibeproxy-factory-video.webp
    vibeproxy.webp
```

## Intentional exclusions

The following generated/runtime artifacts exist in the source working tree but are intentionally not mirrored because they are not tracked source files:

- `__pycache__/`
- `*.egg-info/`
- `target/`
- `.benchmarks/`
- `.pytest_cache/`
- `node_modules/`
- `build/`
- `dist/`

## Verification note

Coverage is intended to match the source repository tracked inventory exactly; any extra files in this directory are limited to this manifest and may be used for archival context.
