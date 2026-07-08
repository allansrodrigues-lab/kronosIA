---
name: kronos-imobiliaria
description: Operar e montar o nicho Imobiliária da Kronos — Schalletti Imóveis (fictícia) com a Sofia (qualificação + matching + visita + calculadora de financiamento) e CRM Adapter multi-CRM. Use para montar os workflows n8n do nicho, editar prompt da Sofia, mexer na carteira de imóveis, ativar conector de CRM real (Vista/Jetimob/Kenlo), ou diagnosticar a demo. Gatilhos: "imobiliária", "Schalletti", "Sofia", "bora n8n da Schalletti", "matching de imóvel", "calculadora de financiamento", "CRM adapter", "conector Vista".
---

# Kronos Imobiliária — Schalletti Imóveis

Nicho de ticket alto nº 1 (comissão de venda paga a automação). Marca 100% fictícia (padrão Bella Massa).
Assistente: **Sofia** — calorosa, consultiva, "a corretora de confiança no WhatsApp".

## Onde está tudo (13_Imobiliaria/)

| Arquivo | Conteúdo |
|---|---|
| `README.md` | Visão geral + checklist de status (fonte da verdade do que falta) |
| `base_conhecimento/00_imobiliaria.md` | Perfil Schalletti (Campinas, equipe fictícia, CRECI fake) |
| `base_conhecimento/01_carteira_imoveis.md` | 12 imóveis fake (SCH-001..008 venda, SCH-101..104 locação) + regras de matching |
| `base_conhecimento/02_politicas.md` | Visitas, financiamento (20% entrada, 10,49% a.a.), locação (renda 3x), captação, LGPD |
| `base_conhecimento/03_tom_de_voz_sofia.md` | Persona + frases-padrão + o que Sofia NUNCA faz |
| `agentes/00_orquestrador_imobiliaria.md` | 9 intents (Haiku) + prompt de classificação + sessão |
| `agentes/01_agente_atendimento_sofia.md` | Prompt LIVE da Sofia (Sonnet 5, SEM temperature) |
| `agentes/02_agente_calculadora_financiamento.md` | ⭐ Code node Price/SAC pronto (JS) + validações + template de resposta |
| `workflows/workflow_orquestrador_imobiliaria_montagem.md` | Guia de montagem n8n (fluxo + checklist de publicação) |
| `workflows/workflow_crm_adapter_montagem.md` | 🔌 CRM Adapter: contrato, formato canônico, 4 ramos |

## CRM (planilha própria do nicho — regra-mãe)

- **ID:** `1bXnGkPZBNeDm_Uicr-sAVPY5ZMw1eHiM6h2ziaPwTWM` ("Kronos CRM — Imobiliária Schalletti")
- Abas prontas: `Carteira_Imoveis` (12 imóveis seedados) · `Leads_Imobiliaria` · `Sessoes_Imobiliaria` · `Visitas` · `Log_Interacoes`
- Dona = conta do Allan; robô `kronos-n8n@...iam.gserviceaccount.com` é Editor
- ⛔ Nunca criar planilha via `create_spreadsheet` do MCP (service account tem cota ZERO) — criar via conector Drive + Allan compartilha (ver memória `mcp-n8n-sheets-setup`)

## Montagem n8n (ordem)

1. `[Imobiliária] - CRM Adapter (v1.0)` — Switch em `$env.CRM_PROVIDER` (padrão `sheets`); ramos vista/jetimob/kenlo PRÉ-MONTADOS e desativados; todo ramo termina em Code node → formato canônico; fallback p/ sheets
2. `[Imobiliária] - Calculadora Financiamento (v1.0)` — Code node `calcular_financiamento` (JS pronto no agente 02)
3. `[Imobiliária] - Sofia Atendimento (v1.0)` — Sonnet 5 `claude-sonnet-5`, carteira injetada via adapter `get_imoveis`
4. `[Imobiliária] - Orquestrador Schalletti (v1.0)` — clonar orquestrador da Advocacia (~80% reuso): buffer 2-3s → IF áudio/transcrição → Haiku classifica → Switch 9 intents
5. Env vars: `CRM_PROVIDER=sheets` + ID da planilha acima
6. Chavinha `/imobiliaria` na Central de Demos (skill kronos-central-demos)
7. Test harness: payloads `5500TEST*` cobrindo os 9 intents

## Pegadinhas (queimaram horas em outros nichos)

- Publicar **todos os sub-workflows** antes do orquestrador; editar sempre a versão publicada; **restart do n8n** após publicar (skill restart-n8n)
- Parser Sonnet 5: `content.find(b => b.type === 'text')?.text` — NUNCA `content[0].text` (thinking vem primeiro)
- Sonnet 5 **sem `temperature`** (400)
- Error Trigger → Error Handler central `X29vC9p5WB38iZFI` em TODOS os workflows
- Sofia nunca inventa imóvel (só carteira), máx 2-3 por mensagem, nunca negocia preço
- Calculadora: conta no Code node (determinística), IA só formata + 3 disclaimers obrigatórios

## Ativar CRM real (cliente fechou)

1. Preencher env var do conector (`VISTA_API_KEY`+`VISTA_BASE_URL` / `JETIMOB_TOKEN` / `KENLO_TOKEN`)
2. Habilitar os nodes do ramo no CRM Adapter → rodar test harness → trocar `CRM_PROVIDER`
3. Vista tem **sandbox grátis** (validar conector antes de cliente); Kenlo exige homologação de parceiro
4. A API é paga pela assinatura do CLIENTE — Kronos não paga CRM

## Depois do n8n (checklist README)

Logo + fachada via Canva IA (nunca à mão) → demo visual (skill kronos-demo-whatsapp) → roteiro de demo → teste ao vivo do Allan (só com tudo montado).
