# Kronos Intelligence — Status de Sessão
> Atualizado: 2026-06-14

## Estado atual do sistema

| Componente | Status |
|---|---|
| VPS Hostinger (2.24.101.180) | Online |
| n8n (n8n.kronosintelligence.com.br) | Online, porta 5678 |
| Evolution API | Online |
| Landing page (kronosintelligence.com.br) | Online com SSL |
| Aurora (clinica01) | Ativa |
| OdontoVita (kronosdemo) | Ativa |

## Workflows ativos e saúde dos nós Anthropic

| Workflow | Nó Claude | Modelo | API Key | Header | OK? |
|---|---|---|---|---|---|
| 01-orquestrador-v2 | Claude Haiku — Classificar | claude-haiku-4-5-20251001 | `$env` | `x-api-key` | ✓ |
| 01-orquestrador-odonto | Claude Haiku — Classificar | claude-haiku-4-5-20251001 | `$env` | `x-api-key` | ✓ |
| 02-agendamento-bia | Claude Sonnet — Bia | claude-sonnet-4-6 | `$env` | `x-api-key` | ✓ |
| 02-agendamento-odonto | Claude Sonnet — Bia | claude-sonnet-4-6 | `$env` | `x-api-key` | ✓ |
| 03-atendimento-clara | Claude Sonnet — Clara | claude-sonnet-4-6 | `$env` | `x-api-key` | ✓ |
| 03-atendimento-odonto | Claude Sonnet — Clara | claude-sonnet-4-6 | `$env` | `x-api-key` | ✓ |
| 05-pos-venda-diana | Claude Sonnet — Diana | claude-sonnet-4-6 | `$env` | `x-api-key` | ✓ |

Auditado em 2026-06-14 via SQLite direto no container. Nenhum nó com chave hardcoded.

## MCP n8n

Adicionado em 2026-06-14:
- **URL:** https://n8n.kronosintelligence.com.br
- **API key:** armazenada no docker-compose `/docker/n8n-xve0/docker-compose.yml` como `N8N_API_KEY`
- **Registrado como:** `n8n` via `claude mcp add`

## 3 causas mais prováveis de quebra (ranking)

### 1 — API key Anthropic revogada ou com saldo zerado (60%)
**Confirmar com:**
```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "docker exec n8n-xve0-n8n-1 printenv ANTHROPIC_API_KEY"
```
Testar a chave em console.anthropic.com → API Keys.

### 2 — Versão publicada do workflow desatualizada (25%)
Edições salvas no rascunho (`workflow_entity`) mas nunca publicadas sobrescritas pela versão ativa (`workflow_history`).

**Confirmar com:**
```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "docker exec n8n-xve0-n8n-1 node -e \"
  const sqlite3 = require('sqlite3');
  const db = new sqlite3.Database('/home/node/.n8n/database.sqlite');
  db.all('SELECT we.name, wh.createdAt as published FROM workflow_entity we JOIN workflow_history wh ON we.id=wh.workflowId ORDER BY wh.createdAt DESC LIMIT 10', (e,r) => { console.log(JSON.stringify(r,null,2)); db.close(); });
\""
```

### 3 — Auto-tradução do Chrome corrompeu nomes de variáveis (15%)
O Chrome traduz silenciosamente labels da UI do n8n, corrompendo nomes de headers e variáveis de ambiente.

**Confirmar com:** abrir o nó suspeito e conferir o JSON bruto no banco (ver skill `/fix-n8n-auth` passo 3).

## Pendências abertas

- [ ] Criar API key do n8n na UI (Settings → API) e atualizar MCP com a key real
- [ ] Separar CRM por cliente (Aurora e Odonto ainda compartilham planilha)
- [ ] Quiz dos números de venda com o Allan
- [ ] Links de pagamento Mercado Pago (Essencial R$397 / Profissional R$697 / Premium R$1.197)
- [ ] Abordar Pizzaria Santa Ana — workflows e proposta prontos, só falta o contato
- [ ] Solicitar revisão de segurança no Google Search Console (SEO)

## Pizzaria Santa Ana — pronto para deploy

Workflows criados em `09_Pizzaria_SantaAna/workflows/`. Para ativar quando fechar contrato:
1. Criar instância Evolution `santaana`
2. Criar planilha com abas: Sessoes_Ativas, Log_Pedidos, Pedidos
3. Configurar variáveis `EVO_INSTANCE_SANTAANA`, `EVO_TEAM_NUMBER_SANTAANA`, `GOOGLE_SHEETS_CRM_ID_SANTAANA` no n8n
4. `scp` dos JSONs pro VPS + import + activate + restart
5. Smoke test (ver `workflow_montagem_manual.md`)

## Como retomar

1. Ler este arquivo (`STATUS.md`) para contexto imediato
2. SSH rápido de verificação: `ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "docker ps --format 'table {{.Names}}\t{{.Status}}'"`
3. Disparar curl de teste (ver CLAUDE.md § Testar webhook sem WhatsApp)
4. Se bot com 401 → `/fix-n8n-auth`
5. Se bot parado/loop → `/n8n-debug`
