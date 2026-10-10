param()

$ErrorActionPreference = "Stop"
$skillRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$required = @(
    "SKILL.md",
    "agents\\openai.yaml",
    "references\\sample-prompts.md",
    "assets\\README.md",
    "tests\\README.md"
)
foreach ($relative in $required) {
    $path = Join-Path $skillRoot $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "missing required file: $relative"
    }
}
$jsonFiles = @(Get-ChildItem (Join-Path $skillRoot "agents") -Filter *.json -File)
if ($jsonFiles.Count -lt 1) {
    throw "expected at least one machine-readable agents/*.json manifest"
}
foreach ($jsonFile in $jsonFiles) {
    $surface = Get-Content -LiteralPath $jsonFile.FullName -Raw | ConvertFrom-Json
    if ($surface.independentSurface -ne $true) {
        throw "independentSurface must be true: $($jsonFile.Name)"
    }
    if ($surface.samplePromptsRef -ne "references/sample-prompts.md") {
        throw "samplePromptsRef must point to references/sample-prompts.md: $($jsonFile.Name)"
    }
}
$promptText = Get-Content -LiteralPath (Join-Path $skillRoot "references\\sample-prompts.md") -Raw
if ([regex]::Matches($promptText, "(?m)^## Prompt ").Count -lt 1) {
    throw "sample prompts are required"
}
if ((Get-Content -LiteralPath (Join-Path $skillRoot "SKILL.md")).Count -gt 150) {
    throw "SKILL.md exceeds the 150-line authoring limit"
}
Write-Output "PASS: pmcro-clean-architecture"
