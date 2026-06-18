# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Kronos Intelligence — automação de atendimento (n8n + WhatsApp)

Produto SaaS de bots WhatsApp para clínicas (agendamento + atendimento) via n8n, Evolution API e Google Sheets, rodando num VPS Hostinger. Landing page em `07_Recursos/index.html`. Protótipos ativos: **Aurora** (estética, `clinica01`) e **OdontoVita** (odonto, `kronosdemo`).

---

## Arquitetura geral

```
WhatsApp → Evolution API → n8n Webhook
                                └─ Orquestrador (Aurora) — Claude Haiku classifica intent
                                        ├─ AGENDAR       → Bia  (sub-workflow 02)
                                        ├─ DUVIDA_*      → Clara (sub-workflow 03)
                                        ├─ POS_PROCEDIMENTO → Diana (sub-workflow 05)
                                        ├─ RECLAMACAO    → escalação humana
                                        └─ demais         → resposta direta
                                                └─ Google Sheets (CRM / log)
```

**Intenções suportadas:** `AGENDAR`, `DUVIDA_PROCEDIMENTO`, `DUVIDA_PRECO`, `POS_PROCEDIMENTO`, `LEAD_NOVO`, `RECLAMACAO`, `OUTRO`.

### Agentes (04_Agentes_IA/)

| Arquivo | Nome | Papel |
|---|---|---|
| `00_agente_principal_orquestrador.md` | **Aurora** | Recepção, classificação de intent, roteamento |
| `01_agente_agendamento.md` | **Bia** | Agendar, remarcar, cancelar |
| `02_agente_atendimento.md` | **Clara** | Dúvidas sobre procedimentos e preços |
| `03_agente_pos_venda.md` | **Diana** | Pós-procedimento e recompra |
| `04_agente_marketing.md` | **Eva** | Captação e qualificação de leads |

Base de conhecimento compartilhada em `04_Agentes_IA/base_conhecimento/` — atualizar esses arquivos é suficiente para todos os agentes refletirem a mudança.

### Workflows (07_Recursos/)

| Arquivo JSON | Função |
|---|---|
| `workflow_01_orquestrador.json` | Orquestrador principal (Aurora + Haiku) |
| `workflow_02_agendamento.json` | Bia — agendamento via Google Calendar |
| `workflow_03_atendimento.json` | Clara — atendimento e dúvidas |
| `workflow_04_lembrete_24h.json` | Lembrete automático D-1 |
| `workflow_05_pos_venda.json` | Diana — follow-up pós-procedimento |

Cada workflow tem um `_guide.md` e um `_montagem_manual.md` correspondentes.

---

## Environment

- **Ambiente local é Windows** — evitar paths bash `/tmp`; cuidado com escape de barra invertida em `.claude.json` e arquivos de config (conferir backslashes escapados). Usar caminhos Windows-compatíveis ou `$env:TEMP` para operações locais.
- **IP de datacenter Hostinger é bloqueado pelo WhatsApp** — conexões da Evolution API exigem proxy residencial se a instância cair.
- **n8n roda em Docker atrás do Traefik** — antes de escrever qualquer `docker-compose`, confirmar o nome real da rede com `docker network ls` (nunca assumir `traefik` ou `web`).

## Environment & Stack

- **VPS Hostinger** — IP `2.24.101.180`, SSH root, chave `~/.ssh/kronos_vps` (sem senha).
- **Containers Docker:** `n8n-xve0-n8n-1`, `evolution-api`, `evolution-postgres`, `evolution-redis`, `kronos-site-*`, `traefik-*`.
- **n8n usa SQLite** (`/home/node/.n8n/database.sqlite`). Para consultar via script: rodar `node` de dentro de `/usr/local/lib/node_modules/n8n` com `require('sqlite3')`. Campo `execution_data.data` usa formato **flatted** (`require('flatted')` para decodificar).
- **Evolution API v2.3.7** — instâncias: `kronosdemo` (Odonto `5519997237404`, webhook `/webhook/whatsapp-odonto`) e `clinica01` (Aurora `5519971514971`, webhook `/webhook/whatsapp`).
- **LLM:** Claude Haiku (`claude-haiku-4-5-20251001`) para classificação de intent; Claude Sonnet para respostas dos agentes especialistas.
- **Regra-mãe:** cada cliente novo nasce isolado — instância Evolution própria + planilha CRM própria. Nunca compartilhar base entre clientes.

### Variáveis de ambiente no n8n (Settings → Variables)

```
ANTHROPIC_API_KEY
EVO_BASE_URL      = https://evo.clinicacliente.com.br
EVO_API_KEY
EVO_INSTANCE      = clinica01 | kronosdemo
EVO_TEAM_NUMBER   = número ou JID do grupo da equipe (escalações)
GOOGLE_SHEETS_CRM_ID
```

---

## n8n Workflows

- Sempre editar a versão **publicada/ativa** (`workflow_history`), não o rascunho (`workflow_entity`). Editar só o `workflow_entity` (draft) **não tem efeito**.
- Após editar, **reiniciar o n8n para aplicar** (deactivate/reactivate ou restart do container) — unpublish/publish via UI não aplica sem restart.
- **n8n auto-traduz o texto da UI** (especialmente via tradução do Chrome), o que corrompe nomes de variáveis e referências `$env`. Sempre desativar a tradução do navegador no n8n e conferir que nomes de variável/env não foram traduzidos **antes** de debugar falhas de auth da API.
- **Execute Workflow exige sub-workflow publicado** — ao reativar um orquestrador, publicar também os subs que ele chama.
- Referências a nodes pelo nome (`$('Montar Prompt Haiku')`) quebram se o node for renomeado.

## API Key Debugging (n8n)

Quando Claude Haiku/Anthropic retorna 401 no n8n, verificar nessa ordem:

1. A API key está válida e não revogada
2. `$env.ANTHROPIC_API_KEY` resolve corretamente dentro do nó (testar com nó Set antes)
3. **Auto-tradução do Chrome não corrompeu** nomes de variáveis ou chaves JSON — conferir a config crua (não a UI traduzida); desativar auto-translate no editor do n8n

### Convenção de nomes no n8n

```
[Categoria] - [Nome] (vX.Y)
Ex: [WhatsApp] - Orquestrador principal (v1.2)
    [Agendamento] - Criar evento (v1.0)
```

### Padrão de erro em todos os workflows

Todo workflow deve ter **Error Trigger** que: (1) loga na planilha de monitoramento, (2) envia alerta no Telegram do implementador, (3) em falha de IA → escala para humano no WhatsApp.

---

## WhatsApp / Evolution API

Para problemas de conexão WhatsApp/Evolution API, checar **antes** de resetar DB/Redis:

1. Compatibilidade de versão Evolution API / Baileys (versão obsoleta do Baileys empacotado é rejeitada pelo WhatsApp).
2. Se o IP de datacenter do VPS está bloqueado pelo WhatsApp — usar proxy residencial se for o caso.

Só depois disso tentar DB delete / Redis clear / downgrade.

## Debugging

- Confirmar se dado mostrado no n8n é **execução real ou test/mock** antes de diagnosticar.
- **Testar bot por número sem automação** (`5519971266736` — WhatsApp da Kronos). Número-com-bot contra número-com-bot → loop infinito.
- ⚠️ IP de datacenter pode ser bloqueado pelo WhatsApp — se conexão cair, considerar proxy residencial e/ou atualizar Evolution API.

### Checklist de erro de auth da API Anthropic (nessa ordem)

1. API key válida e não revogada
2. `$env.ANTHROPIC_API_KEY` resolve corretamente no nó
3. Headers: `x-api-key` (não `Authorization`) + `anthropic-version: 2023-06-01`
4. Nome da variável não corrompido pela **auto-tradução do Chrome** — conferir config crua, não a UI traduzida

### Testar webhook sem WhatsApp

```bash
curl -X POST https://SEU-N8N/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica01",
    "data": {
      "key": { "remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false, "id": "TEST001" },
      "pushName": "Maria Teste",
      "message": { "conversation": "Quero agendar uma limpeza de pele" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

---

## File Paths

Usar tratamento de caminhos cross-platform — não assumir que `/tmp` funciona igual em bash (VPS) vs PowerShell (Windows local). Operações no VPS: bash paths. Operações locais de empacotamento (plugins/skills): usar caminhos relativos ou `$env:TEMP`.

## Deploy / Infra

- Use **bash paths** (não PowerShell `/tmp`) para operações de arquivo no VPS.
- Site (`07_Recursos/index.html`) roda no VPS via container `kronos-site-*` + Traefik (não na shared hosting).
- Skills disponíveis: `/kronos-deploy` (infra VPS), `/kronos-workflow` (editar n8n), `/n8n-debug` (diagnóstico de bot), `/kronos-agente` (criar/adaptar agente para novo nicho).

## n8n Workflow Editing

- Sempre editar a versão **publicada/ativa** (`workflow_history`), não o rascunho (`workflow_entity`). Editar só o draft **não tem efeito**.
- Após atualizar, verificar se é a versão ativa e reiniciar o n8n se necessário (deactivate/reactivate ou restart do container).

## Environment & Variable Hygiene

Ao debugar auth da API Anthropic/Claude Haiku no n8n, checar nessa ordem:

1. API key válida e não revogada (401)
2. `$env.ANTHROPIC_API_KEY` resolve corretamente no nó
3. **Auto-tradução do Chrome não corrompeu** nomes de variáveis — sempre desativar tradução do navegador no editor do n8n e verificar o nome cru da variável antes de debugar

## VPS / WhatsApp Deployment Notes

- **IP de datacenter Hostinger é bloqueado pelo WhatsApp** — planejar proxy residencial para vincular chip de cliente novo.
- Verificar se a versão da Evolution API suporta o endpoint chamado (ex: `pairing-code`).
- Atenção a versões obsoletas do Baileys empacotado — causam crash loops rejeitados pelo WhatsApp.

## Path & Shell Conventions

- Ambiente local é **Windows** — evitar backslash escaping em `.claude.json` e arquivos de config.
- Cuidado com divergência de paths `/tmp` entre bash (VPS) e PowerShell (local) ao empacotar plugins ou copiar arquivos.
- Operações no VPS: bash paths. Operações locais: caminhos relativos ou `$env:TEMP`.
