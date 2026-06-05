# Arquitetura Geral

## Diagrama de alto nível

```
┌─────────────────────────────────────────────────────────────┐
│                       CANAIS DE ENTRADA                      │
│   WhatsApp Business   │   Instagram DM   │   Site / Forms   │
└──────────┬──────────────────┬─────────────────────┬──────────┘
           │                  │                     │
           ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ORQUESTRADOR (n8n + Agente Principal)           │
│                                                              │
│   Identifica intenção → roteia para o agente especialista    │
└──┬──────────────┬──────────────┬──────────────┬─────────────┘
   │              │              │              │
   ▼              ▼              ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Agente   │ │ Agente   │ │ Agente   │ │ Agente       │
│Agendam.  │ │Atendim.  │ │Pós-venda │ │Marketing/Lead│
└────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
     │            │             │              │
     ▼            ▼             ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                       CAMADA DE DADOS                        │
│  Google Calendar │ Google Sheets/CRM │ Base Conhecimento    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │   DASHBOARD MÉTRICAS  │
                  └───────────────────────┘
```

## Componentes

### Camada de canais
- **WhatsApp Business API** (Cloud API oficial ou Z-API/Evolution)
- **Instagram DM** via Meta Graph API
- **Formulários web** (Tally, Typeform ou form nativo do site)

### Camada de orquestração — n8n
- Hospedagem: VPS própria (DigitalOcean/Hetzner) ou n8n Cloud
- Workflows separados por domínio (agendamento, atendimento, etc.)
- Webhook único de entrada → roteamento por intenção

### Camada de IA
- **LLM:** Claude Sonnet (resposta) + Haiku (classificação rápida)
- **Base de conhecimento:** vetorizada com embeddings (Pinecone, Qdrant ou Supabase pgvector)
- **Memória:** Redis para contexto de conversa de curto prazo

### Camada de dados
- **Google Calendar** — agendamentos
- **Google Sheets / Notion / Airtable** — CRM leve do MVP
- **Supabase / Postgres** — quando escalar
- **Drive** — anexos (fotos de procedimento, fichas)

### Camada de observabilidade
- Logs no próprio n8n
- Métricas exportadas para Google Sheets ou Looker Studio
- Alertas no Slack/Telegram do implementador
