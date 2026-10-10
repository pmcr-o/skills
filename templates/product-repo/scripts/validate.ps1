param(
  [string]$Root = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
foreach ($relative in @("README.md", "product.manifest.json", "autonomy-grant.example.json", ".agents\agents\orchestrator.json", ".agents\agents\checker.json", ".agents\agents\reflector.json", ".pmcro\protocol\trail-event.schema.json", ".pmcro\trails\example.jsonl", "scripts\validate_trail.py", "tests\README.md")) {
  if (-not (Test-Path -LiteralPath (Join-Path $rootPath $relative) -PathType Leaf)) { throw "missing $relative" }
}
$manifest = Get-Content -LiteralPath (Join-Path $rootPath "product.manifest.json") -Raw | ConvertFrom-Json
if ($manifest.apiVersion -ne "pmcro.product-repo/v1") { throw "invalid product manifest" }
if ($manifest.promotion -ne "checker-verified-only") { throw "checker promotion policy missing" }
if (Get-Command python -ErrorAction SilentlyContinue) {
  & python (Join-Path $rootPath "scripts\validate_trail.py") --trail (Join-Path $rootPath ".pmcro\trails\example.jsonl")
  if ($LASTEXITCODE -ne 0) { throw "generic trail validator failed" }
}
Write-Output "PASS: PMCR-O product repository template"
