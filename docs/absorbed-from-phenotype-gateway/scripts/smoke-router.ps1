# Smoke-test Rust router spike + packages/router promotion package.
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "==> smoke router spike"
Push-Location (Join-Path $Root "spikes/rust/router")
try {
    cargo test
    if ($LASTEXITCODE -ne 0) { exit 1 }
} finally {
    Pop-Location
}

Write-Host "==> smoke packages/router"
Push-Location (Join-Path $Root "packages/router")
try {
    cargo test
    if ($LASTEXITCODE -ne 0) { exit 1 }
} finally {
    Pop-Location
}

Write-Host "ROUTER SMOKE OK"
