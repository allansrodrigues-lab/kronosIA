---
name: kronos-mcp
description: Operar o n8n e o CRM (Google Sheets) do Kronos direto pelos MCPs locais (mcp__n8n__* e mcp__google-sheets__*), sem SSH/SQLite nem UI. Use para ler/listar/criar/editar/validar workflows do n8n, checar saúde da instância, ver execuções, e para ler/escrever a planilha Kronos CRM (leads, sessões ativas, agendamentos, clientes). Também quando o usuário disser "lista os workflows", "valida o workflow", "lê os leads", "adiciona lead", "vê as sessões da Clara", "ver execução", "health do n8n".
---

# Kronos via MCP — operar n8n + CRM direto do chat

Os MCPs `n8n` e `google-sheets` estão configurados localmente (ver memória [[mcp-n8n-sheets-setup]]). Preferir SEMPRE estas ferramentas a SSH/SQLite (skills `n8n-edit`/`n8n-debug`) e ao conector do Drive — são mais rápidas e diretas. SSH/SQLite só quando precisar mexer na **versão publicada** que roda (ver gotcha abaixo).

## n8n (mcp__n8n__*)

Ferramentas principais:
- `n8n_health_check` — status da instância (`mode:"diagnostic"` pra debug de env/API).
- `n8n_list_workflows` — metadados (id/nome/active/tags/nodeCount). Paginação via `cursor`.
- `n8n_get_workflow` — JSON completo de um workflow (passar o `id`).
- `n8n_validate_workflow` / `validate_node` — validar antes de ativar.
- `n8n_create_workflow`, `n8n_update_partial_workflow`, `n8n_update_full_workflow`, `n8n_delete_workflow`.
- `n8n_executions` — inspecionar execuções (debug de bot).
- `search_nodes`, `get_node`, `search_templates`, `tools_documentation` — referência de nós/templates.

IDs reais dos workflows ativos (14/06/2026):
`Orq01RouterV2aa1`=01-orquestrador-v2 (Aurora) · `01-orquestrador-odonto` · `02-agendamento-bia` · `02-agendamento-odonto` · `TDJQkNQDJh9PnmSh`=03-atendimento-clara · `03-atendimento-odonto` · `vGfBm7cdjsESJtIH`=04-lembrete-24h · `wItuI9j8dVSbq0F0`=05-pos-venda-diana · `UrHGeigVUnisIMg1`=06-lead-landing.

### ⚠️ Gotcha: editar via MCP mexe no rascunho/entidade
A API do n8n edita a workflow, mas reativar exige publicar + reiniciar container (regra de ouro da skill `n8n-edit`: o que roda é a versão publicada em `workflow_history`). Se um fix via MCP "não pegar" no bot, cair pra `n8n-edit` (DB + `docker restart n8n-xve0-n8n-1`). Sempre confirmar se a execução vista é real ou test/mock antes de diagnosticar.

## CRM — Google Sheets (mcp__google-sheets__*)

Planilha **Kronos CRM**: `spreadsheet_id = 1ZlDFYkgx6aXUM0ayj1e1_K6uX0cruo7VuCcmg1_w5ps`.
Abas: `Leads, Sessoes_Ativas, Agendamentos, Log_Agendamentos, Feedback_PosVenda, Log_Interacoes, Slots_Disponiveis, Log_Lembretes, Clientes, Config`.

Ferramentas:
- `list_sheets`, `get_sheet_data` (range A1 opcional; `include_grid_data:false` por padrão = mais barato), `get_multiple_sheet_data`.
- `find_in_spreadsheet` — achar célula por valor (ótimo pra localizar uma sessão/lead por telefone).
- `update_cells` (range + matriz 2D), `batch_update_cells`, `add_rows`, `add_columns`.
- `batch_update` — operações estruturais (criar aba, inserir/deletar linhas, formatação).

Colunas de `Leads`: `Data_Hora, Nome, Contato, Segmento, Mensagem, Origem, Status`.

### ⚠️ Regras Kronos
- **Blindar base por cliente** ([[feedback-blindar-base-por-cliente]]): cada cliente tem planilha própria. NUNCA escrever dados de um cliente na planilha de outro. Confirmar o `spreadsheet_id` certo antes de escrever.
- Escrita em planilha modifica dado de produção — confirmar com o Allan antes de `update_cells`/`add_rows`/`batch_update` quando não for trivial/reversível.
- Não logar segredos (chaves de API) em células — já houve vazamento de `sk-ant-...` no `Log_Interacoes`.

## Se os MCPs não aparecerem
Usar a skill `mcp-reload`.
