#!/usr/bin/env pwsh
# TDD verification for the kronos-plugin build.
# Asserts: plugin manifest valid, exact expected skill set present (no missing/extra),
# each SKILL.md has valid name+description frontmatter, and NO source files were
# silently dropped (full-tree comparison — guards the old "2 of 7 skills" path bug).
# Native PowerShell on purpose: no bash /tmp, no backslash-escaping pitfalls.

$ErrorActionPreference = 'Stop'
$repo    = Split-Path $PSScriptRoot -Parent
$srcRoot = Join-Path $repo '.claude\skills'
$plugin  = $PSScriptRoot
$pSkills = Join-Path $plugin 'skills'

$expected = @(
  'kronos-deploy','kronos-landing','kronos-workflow','kronos-agente',
  'n8n-edit','kronos-bot-patterns','n8n-debug','debug-pitfalls',
  'fix-n8n-auth','restart-n8n','kronos-mcp','mcp-reload'
)

$fail = 0
function Check($ok, $msg) {
  if ($ok) { Write-Host "  PASS  $msg" -ForegroundColor Green }
  else     { Write-Host "  FAIL  $msg" -ForegroundColor Red; $script:fail++ }
}

Write-Host "`n== Manifest ==" -ForegroundColor Cyan
$manifestPath = Join-Path $plugin '.claude-plugin\plugin.json'
Check (Test-Path $manifestPath) ".claude-plugin/plugin.json exists"
if (Test-Path $manifestPath) {
  try { $m = Get-Content $manifestPath -Raw | ConvertFrom-Json; Check $true "plugin.json is valid JSON (name=$($m.name) v$($m.version))" }
  catch { Check $false "plugin.json is valid JSON: $_" }
}

Write-Host "`n== Skill set (expect exactly $($expected.Count)) ==" -ForegroundColor Cyan
$built = @()
if (Test-Path $pSkills) { $built = Get-ChildItem $pSkills -Directory | Select-Object -ExpandProperty Name }
Check ($built.Count -eq $expected.Count) "built skill count = $($expected.Count) (got $($built.Count))"
foreach ($s in $expected) { Check ($built -contains $s) "present: $s" }
foreach ($b in $built) { if ($expected -notcontains $b) { Check $false "unexpected extra skill: $b" } }

Write-Host "`n== Each skill loads (frontmatter) + no dropped files ==" -ForegroundColor Cyan
foreach ($s in $expected) {
  $skillMd = Join-Path $pSkills "$s\SKILL.md"
  if (-not (Test-Path $skillMd)) { Check $false "$s : SKILL.md missing"; continue }
  $head = (Get-Content $skillMd -TotalCount 15) -join "`n"
  $hasName = $head -match '(?m)^name:\s*\S+'
  $hasDesc = $head -match '(?m)^description:\s*\S+'
  Check ($hasName -and $hasDesc) "$s : SKILL.md frontmatter has name + description"

  # full-tree: every source file must exist in the artifact
  $srcDir = Join-Path $srcRoot $s
  $srcFiles = Get-ChildItem $srcDir -Recurse -File | ForEach-Object { $_.FullName.Substring($srcDir.Length) }
  $missing = @()
  foreach ($rel in $srcFiles) {
    if (-not (Test-Path (Join-Path $pSkills "$s$rel"))) { $missing += $rel }
  }
  Check ($missing.Count -eq 0) "$s : all $($srcFiles.Count) source file(s) copied$(if($missing){' — MISSING: '+($missing -join ',')})"
}

Write-Host ""
if ($fail -eq 0) { Write-Host "ALL ASSERTIONS PASSED ($($expected.Count) skills verified)" -ForegroundColor Green; exit 0 }
else { Write-Host "$fail ASSERTION(S) FAILED" -ForegroundColor Red; exit 1 }
