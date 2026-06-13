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

## n8n Workflow Editing

- Sempre editar a versão **publicada/ativa** (`workflow_history`), não o rascunho (`workflow_entity`).
- Após qualquer mudança de config/env, **reiniciar o container n8n** — unpublish/publish via UI não aplica sem restart.
- **Execute Workflow exige sub-workflow publicado** — ao reativar um orquestrador, publicar também os subs que ele chama.
- Referências a nodes pelo nome (`$('Montar Prompt Haiku')`) quebram se o node for renomeado.

### Convenção de nomes no n8n

```
[Categoria] - [Nome] (vX.Y)
Ex: [WhatsApp] - Orquestrador principal (v1.2)
    [Agendamento] - Criar evento (v1.0)
```

### Padrão de erro em todos os workflows

Todo workflow deve ter **Error Trigger** que: (1) loga na planilha de monitoramento, (2) envia alerta no Telegram do implementador, (3) em falha de IA → escala para humano no WhatsApp.

---

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

## Deploy / Infra

- Use **bash paths** (não PowerShell `/tmp`) para operações de arquivo no VPS.
- Site (`07_Recursos/index.html`) roda no VPS via container `kronos-site-*` + Traefik (não na shared hosting).
- Skills disponíveis: `/kronos-deploy` (infra VPS), `/kronos-workflow` (editar n8n), `/n8n-debug` (diagnóstico de bot), `/kronos-agente` (criar/adaptar agente para novo nicho).
