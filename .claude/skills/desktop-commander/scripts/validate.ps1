param()
$ErrorActionPreference = "Stop"
$skillRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
foreach ($relative in @("SKILL.md", "agents\openai.yaml", "references\sample-prompts.md", "assets\README.md")) {
    if (-not (Test-Path -LiteralPath (Join-Path $skillRoot $relative) -PathType Leaf)) { throw "missing $relative" }
}
$surface = Get-Content (Get-ChildItem (Join-Path $skillRoot "agents") -Filter *.json | Select-Object -First 1).FullName -Raw | ConvertFrom-Json
if ($surface.independentSurface -ne $true) { throw "surface must be independently addressable" }
$promptText = Get-Content (Join-Path $skillRoot "references\sample-prompts.md") -Raw
if (([regex]::Matches($promptText, "(?m)^## Prompt ")).Count -lt 2) { throw "expected generic and specialized prompts" }
if ((Get-Content (Join-Path $skillRoot "SKILL.md") -Raw) -notmatch "PowerShell") { throw "PowerShell boundary missing" }
Write-Output "PASS: desktop-commander"
