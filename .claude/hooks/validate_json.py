"""
Hook PostToolUse (Edit|Write): valida JSON só quando o arquivo editado termina em .json.
Le o payload do hook via stdin (formato do Claude Code), nao existe $CLAUDE_FILE_PATH.
"""
import json
import sys
import subprocess

payload = json.load(sys.stdin)
file_path = payload.get("tool_input", {}).get("file_path", "")

if not file_path.endswith(".json"):
    sys.exit(0)

result = subprocess.run(
    ["python", "-m", "json.tool", file_path],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

if result.returncode != 0:
    print(f"Invalid JSON: {file_path}")
