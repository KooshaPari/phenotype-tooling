# Smoke-build Go submodule planes under third_party/.
# Exit 0 only when every plane builds; see spikes/go/*/README.md for known failures.
param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"
$env:GOPROXY = if ($env:GOPROXY) { $env:GOPROXY } else { "https://proxy.golang.org,direct" }

$planes = @(
    @{ Name = "agentapi-plusplus"; Path = "third_party/agentapi-plusplus"; BuildPath = "." },
    @{ Name = "cliproxyapi-plusplus"; Path = "third_party/cliproxyapi-plusplus"; BuildPath = "." },
    @{ Name = "cliproxy-package"; Path = "packages/cliproxy"; BuildPath = "." },
    @{ Name = "agentapi-package"; Path = "packages/agentapi"; BuildPath = "." },
    @{ Name = "bifrost-package"; Path = "packages/bifrost"; BuildPath = "." },
    @{ Name = "argis-package"; Path = "packages/argis"; BuildPath = "." },
    @{ Name = "argis-extensions"; Path = "third_party/argis-extensions"; BuildPath = "." },
    @{ Name = "bifrost-transports"; Path = "third_party/bifrost"; BuildPath = "transports" }
)

function Ensure-BifrostTransportsReplaces {
    param([string]$BuildDir)
    $gomod = Join-Path $BuildDir "go.mod"
    if (-not (Test-Path $gomod)) { return }
    $content = Get-Content $gomod -Raw
    if ($content -match '(?m)^replace github\.com/maximhq/bifrost/core =>') { return }
    @"

replace github.com/maximhq/bifrost/core => ../core
replace github.com/maximhq/bifrost/framework => ../framework
replace github.com/maximhq/bifrost/plugins/governance => ../plugins/governance
replace github.com/maximhq/bifrost/plugins/compat => ../plugins/compat
replace github.com/maximhq/bifrost/plugins/logging => ../plugins/logging
replace github.com/maximhq/bifrost/plugins/maxim => ../plugins/maxim
replace github.com/maximhq/bifrost/plugins/otel => ../plugins/otel
replace github.com/maximhq/bifrost/plugins/semanticcache => ../plugins/semanticcache
replace github.com/maximhq/bifrost/plugins/telemetry => ../plugins/telemetry
"@ | Add-Content -Path $gomod
}

$failed = @()
foreach ($plane in $planes) {
    $dir = Join-Path $Root $plane.Path
    $buildDir = Join-Path $dir $plane.BuildPath
    if (-not (Test-Path $buildDir)) {
        Write-Host "SKIP $($plane.Name): missing $buildDir"
        $failed += $plane.Name
        continue
    }
    $gomod = Join-Path $buildDir "go.mod"
    if (-not (Test-Path $gomod)) {
        Write-Host "SKIP $($plane.Name): no go.mod in $($plane.BuildPath)"
        continue
    }
    if ($plane.Name -eq "bifrost-transports") {
        Ensure-BifrostTransportsReplaces -BuildDir $buildDir
    }
    Write-Host "==> smoke $($plane.Name) ($buildDir)"
    Push-Location $buildDir
    try {
        & go build ./...
        if ($LASTEXITCODE -ne 0) { $failed += $plane.Name }
    } finally {
        Pop-Location
    }
}

if ($failed.Count -gt 0) {
    Write-Host "SMOKE FAIL: $($failed -join ', ')"
    exit 1
}
Write-Host "SMOKE OK"
exit 0
