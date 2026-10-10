param(
  [Parameter(Mandatory=$true)][string]$Root,
  [Parameter(Mandatory=$true)][string]$Skill,
  [Parameter(Mandatory=$true)][string]$Plugin,
  [switch]$Apply,
  [switch]$CleanManaged
)

$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "bootstrap_workspace.py"
$args = @($script, "--root", $Root, "--skill", $Skill, "--plugin", $Plugin)
if ($Apply) { $args += "--apply" }
if ($CleanManaged) { $args += "--clean-managed" }
python @args
exit $LASTEXITCODE
