# Integrações

| Sistema | Função | Credencial | Status |
|---|---|---|---|
| Evolution API (self-hosted) | Canal WhatsApp principal | API Key (Header Auth) | A configurar |
| Google Calendar | Agendamentos | OAuth2 | A configurar |
| Google Sheets | CRM e métricas | Service Account | A configurar |
| Anthropic API (Claude) | LLM dos agentes | API Key | A configurar |
| Pinecone / Qdrant | Base vetorial | API Key | A definir |
| Instagram Graph API | DMs Instagram | OAuth Meta | Fase 2 |
| Asaas / Mercado Pago | Cobrança | API Key | Fase 2 |

## Endpoints n8n

| Webhook | Origem | Workflow |
|---|---|---|
| `/webhook/whatsapp` | WhatsApp Cloud API | `01-orquestrador-whatsapp` |
| `/webhook/instagram` | Meta | `02-orquestrador-instagram` |
| `/webhook/site-form` | Site / Tally | `03-captacao-leads` |
| `/webhook/calendar-event` | Google Calendar | `04-confirmacao-agendamento` |

## Variáveis de ambiente

```bash
# n8n
N8N_HOST=automacao.clinicacliente.com.br
N8N_PROTOCOL=https

# Evolution API
EVO_BASE_URL=https://evo.clinicacliente.com.br
EVO_API_KEY=
EVO_INSTANCE=clinica

# Anthropic
ANTHROPIC_API_KEY=

# Vector DB
PINECONE_API_KEY=
PINECONE_INDEX=clinica-kb

# Google
GOOGLE_SERVICE_ACCOUNT_JSON=
GOOGLE_CALENDAR_ID=
GOOGLE_SHEETS_CRM_ID=
```

> ⚠️ **Nunca commite credenciais.** Use o gerenciador de credenciais nativo do n8n.
