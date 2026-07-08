#!/usr/bin/env pwsh
# Build the kronos-plugin: copy every skill folder (whole tree) from .claude\skills
# into kronos-plugin\skills. Native Copy-Item -Recurse so supporting files (e.g.
# debug-pitfalls\session-end-hook.md) are never silently dropped. No bash /tmp.

$ErrorActionPreference = 'Stop'
$repo    = Split-Path $PSScriptRoot -Parent
$srcRoot = Join-Path $repo '.claude\skills'
$pSkills = Join-Path $PSScriptRoot 'skills'

if (Test-Path $pSkills) { Remove-Item $pSkills -Recurse -Force }
New-Item -ItemType Directory -Path $pSkills | Out-Null

$count = 0
Get-ChildItem $srcRoot -Directory | ForEach-Object {
  Copy-Item $_.FullName -Destination $pSkills -Recurse -Force
  $count++
  Write-Host "  copied $($_.Name)"
}
Write-Host "Built $count skill(s) into $pSkills" -ForegroundColor Green
