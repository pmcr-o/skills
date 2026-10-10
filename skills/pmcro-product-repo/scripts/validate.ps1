param()

$ErrorActionPreference = "Stop"
$skillRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
foreach ($relative in @("SKILL.md", "agents\openai.yaml", "references\sample-prompts.md", "assets\README.md", "tests\README.md")) {
    if (-not (Test-Path -LiteralPath (Join-Path $skillRoot $relative) -PathType Leaf)) { throw "missing $relative" }
}
$jsonFiles = @(Get-ChildItem (Join-Path $skillRoot "agents") -Filter *.json -File)
if ($jsonFiles.Count -ne 1) { throw "expected one agent manifest" }
$surface = Get-Content $jsonFiles[0].FullName -Raw | ConvertFrom-Json
if ($surface.independentSurface -ne $true) { throw "agent surface must be independently addressable" }
if ($surface.samplePromptsRef -ne "references/sample-prompts.md") { throw "sample prompt reference missing" }
$prompts = Get-Content (Join-Path $skillRoot "references\sample-prompts.md") -Raw
if (([regex]::Matches($prompts, "(?m)^## Prompt ")).Count -lt 1) { throw "sample prompts missing" }
if ((Get-Content (Join-Path $skillRoot "SKILL.md")).Count -gt 150) { throw "SKILL.md exceeds 150 lines" }
Write-Output "PASS: pmcro-product-repo"
