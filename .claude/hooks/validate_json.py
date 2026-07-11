"""
Hook PostToolUse (Edit|Write): valida JSON só quando o arquivo editado termina em .json.
Le o payload do hook via stdin (formato do Claude Code), nao existe $CLAUDE_FILE_PATH.
Exit 2 + stderr = o Claude Code devolve o erro pro modelo corrigir na hora
(exit 0 com print no stdout era engolido como sucesso silencioso).
"""
import json
import sys

payload = json.load(sys.stdin)
file_path = payload.get("tool_input", {}).get("file_path", "")

if not file_path.endswith(".json"):
    sys.exit(0)

try:
    with open(file_path, encoding="utf-8") as f:
        json.load(f)
except (json.JSONDecodeError, OSError) as e:
    print(f"JSON invalido apos a edicao: {file_path} -> {e}", file=sys.stderr)
    sys.exit(2)
