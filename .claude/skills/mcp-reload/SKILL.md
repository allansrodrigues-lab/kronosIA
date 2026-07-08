---
name: mcp-reload
description: Diagnosticar e consertar os MCPs locais do Kronos (n8n e google-sheets) quando não expõem ferramentas, somem, ou dão timeout/erro de conexão. Use quando "o MCP não carregou", "mcp__n8n__* não aparece", "google-sheets sumiu", "connection timed out", "MODULE_NOT_FOUND", ou depois de mexer em ~/.claude.json. Cobre: pacote errado, chave de projeto errada (/ vs \), timeout de download, barras corrompidas e processo zumbi.
---

# MCP Reload — destravar n8n + google-sheets (validado 14/06/2026)

Config de referência e causa-raiz dos erros: memória [[mcp-n8n-sheets-setup]]. Os servers ficam em `~/.claude.json` → `projects[<chave>].mcpServers`.

## Diagnóstico rápido
1. `ToolSearch "n8n search_nodes"` e `ToolSearch "get_sheet_data update_cells"`. Se aparecem `mcp__n8n__*` / `mcp__google-sheets__*`, estão OK.
2. Se não, ler o log mais novo do cwd da sessão (o caminho usa `--` no lugar de `/` e `\`):
   `~/AppData/Local/claude-cli-nodejs/Cache/<cwd-sanitizado>/mcp-logs-n8n/` e `.../mcp-logs-google-sheets/` → `ls -t | head -1` e `tail` o `.jsonl`.

## As 4 causas e os fixes

1. **Pacote n8n errado** — `@n8n/mcp-server` dá 404. Correto: `n8n-mcp` (`npm i -g n8n-mcp`).
2. **Chave de projeto errada** — `.claude.json` tem chaves duplicadas misturando `/` e `\`, mais a subpasta `.github` (cwd real). A config tem que estar na chave que bate com o `cwd` do log. Replicar nas 3 variantes.
3. **Timeout de 30s** — `npx -y`/`uvx` baixam pacote no startup e estouram. Instalar local: `npm i -g n8n-mcp` e `uv tool install mcp-google-sheets`.
4. **Barras `\` corrompidas** — no Windows o `cmd.exe` come os `\` (caminho vira `C:UsersUsuario...`, dá `MODULE_NOT_FOUND` / "não reconhecido"). Usar **barras `/`** em todos os caminhos e comando que o PATH resolve.

## Config que funciona (forward slashes, comando via PATH)
```json
"n8n": {
  "type": "stdio", "command": "node",
  "args": ["C:/Users/Usuario/AppData/Roaming/npm/node_modules/n8n-mcp/dist/mcp/stdio-wrapper.js"],
  "env": { "MCP_MODE": "stdio", "N8N_API_URL": "https://n8n.kronosintelligence.com.br", "N8N_API_KEY": "<JWT>" }
},
"google-sheets": {
  "type": "stdio", "command": "mcp-google-sheets", "args": [],
  "env": { "SERVICE_ACCOUNT_PATH": "C:/Users/Usuario/.claude/kronos-service-account.json" }
}
```
Editar `.claude.json` com um **script node** (`fs.readFileSync`/`JSON.parse`/`writeFileSync`), nunca com `node -e` inline com `\` (o shell corrompe). Fazer backup antes (`cp .claude.json .claude.json.bak-<ts>`).

## Validar antes de pedir restart
Spawnar como o Claude faria e checar `serverInfo`:
- n8n: `echo '<init json>' | MCP_MODE=stdio N8N_API_URL=... N8N_API_KEY=x node "C:/.../stdio-wrapper.js"`
- sheets: `echo '<init json>' | SERVICE_ACCOUNT_PATH="C:/.../kronos-service-account.json" mcp-google-sheets`

## ⚠️ Aplicar a config nova = matar o processo
Mudança em `.claude.json` só vale quando o **processo do Claude morre e sobe de novo**. No desktop Windows, **fechar a janela NÃO mata** o processo (a sessão persiste com a config velha em memória), e `/mcp` reconnect não recarrega de forma confiável. Instruir o usuário: **Ctrl+Shift+Esc → finalizar TODOS os "Claude"/"node" → reabrir**. Confirmar sucesso vendo um **sessionId novo** no log.
