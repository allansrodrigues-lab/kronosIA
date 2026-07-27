#!/usr/bin/env python3
"""Hook PostToolUse (Write|Edit): normaliza CRLF -> LF em scripts shell.

Por que existe: o ambiente local é Windows, mas os .sh rodam no VPS (bash).
Script salvo com CRLF falha em silêncio no Linux com erro enigmático
("bad interpreter: /bin/bash^M"). Este hook corta o problema na origem.

Mira SÓ o arquivo que acabou de ser editado (lido do JSON no stdin) — varrer
o projeto inteiro a cada Edit seria lento numa pasta OneDrive grande.
"""
import json
import sys

# Extensões que precisam de LF por rodarem no Linux/VPS.
ALVOS = (".sh", ".bash")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # stdin vazio ou malformado: não é motivo para travar o turno

    caminho = payload.get("tool_response", {}).get("filePath") or payload.get(
        "tool_input", {}
    ).get("file_path")

    if not caminho or not caminho.lower().endswith(ALVOS):
        return 0

    try:
        with open(caminho, "rb") as f:
            bruto = f.read()
    except OSError:
        return 0

    normalizado = bruto.replace(b"\r\n", b"\n")
    if normalizado == bruto:
        return 0

    try:
        with open(caminho, "wb") as f:
            f.write(normalizado)
    except OSError:
        return 0

    print(json.dumps({"systemMessage": f"CRLF -> LF normalizado em {caminho}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
