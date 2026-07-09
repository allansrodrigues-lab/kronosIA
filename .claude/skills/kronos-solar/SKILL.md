---
name: kronos-solar
description: Operar e customizar o nicho Energia Solar da Kronos — Zênite Energia Solar (fictícia) com a Helena (qualificação + ⭐ calculadora de payback + visita técnica) e Voice Agent por ligação. Use para testar a demo, corrigir a Helena, ajustar a calculadora, adaptar para cliente real, plugar CONTA_LUZ/OCR de verdade, ou diagnosticar falha nos workflows. Gatilhos: "energia solar", "Zênite", "Helena", "calculadora de payback", "visita técnica", "bot solar", "demo solar".
---

# Kronos Energia Solar — Zênite Energia Solar

4º nicho "do A ao Z" (ticket alto, venda pontual — 09/07/2026). Marca 100% fictícia (padrão Bella
Massa / Ferraz & Nogueira / Schalletti). Assistente: **Helena** — consultiva, direta em número,
"quem responde primeiro com o número na mão leva o cliente".

## Onde está tudo (15_Solar/)

| Arquivo | Conteúdo |
|---|---|
| `README.md` | Visão geral + checklist de status (fonte da verdade do que falta) |
| `base_conhecimento/00_zenite_solar.md` | Perfil da Zênite (Campinas, equipe fictícia, garantias) |
| `base_conhecimento/01_produtos_precos.md` | Tipos de sistema, tabela R$/kWp, geração distribuída |
| `base_conhecimento/02_politicas.md` | Visita técnica, financiamento, manutenção, LGPD, escalação |
| `base_conhecimento/03_tom_de_voz_helena.md` | Persona + frases-padrão + o que Helena NUNCA faz |
| `agentes/00_orquestrador_solar.md` | 8 intents (Haiku) + prompt de classificação + sessão |
| `agentes/01_agente_atendimento_helena.md` | Prompt LIVE da Helena (Sonnet 5, SEM temperature) |
| `agentes/02_agente_calculadora_payback.md` | ⭐ Code node payback pronto (JS) + fórmula + parâmetros a revisar |
| `workflows/workflow_orquestrador_solar_montagem.md` | Guia de montagem n8n (decisões de arquitetura) |

## CRM (planilha própria do nicho — regra-mãe)

- **ID:** `120rfE1JNfh0H0slWXZlvf1GVvHxn8MRoB-0NTw1S4Tk` ("Kronos CRM — Zênite (Energia Solar)")
- Abas: `Leads_Solar` · `Sessoes_Solar` · `Simulacoes` (KPI simulação→visita) · `Visitas_Tecnicas` · `Log_Conversas`
- Dona = conta do Allan; robô `kronos-n8n@...iam.gserviceaccount.com` é Editor
- ⛔ Nunca criar planilha via `create_spreadsheet` do MCP (service account tem cota ZERO) — criar via conector Drive + Allan compartilha (ver memória `mcp-n8n-sheets-setup`)

## Workflows n8n — 3, não 4

Decisão tomada na montagem: a visita técnica ficou **embutida no workflow da Helena**, mesmo
padrão real da Sofia/Imobiliária (que também não tem workflow de agendamento separado — só a Bia,
que usa slots pré-cadastrados, precisa disso). Sem CRM Adapter — Sheets direto (instaladora
pequena não tem CRM próprio).

| Nome no n8n | ID | Papel |
|---|---|---|
| `DEMO-SOLAR-01-orquestrador-zenite` | `hbDX9SmUjturOrW7` | Buffer 2,5s, IF áudio/transcrição, Haiku 8 intents, escalação RECLAMACAO, detecta CONTA_LUZ (imagem/pdf) e pula o Haiku |
| `DEMO-SOLAR-02-agente-helena` | `B0ck0jtpAH0ZJs0I` | Qualificação, visita técnica, escalação, Sheets direto (Leads/Sessões/Log), aciona a calculadora sozinha quando `valor_conta`+`tipo_imovel`+`fase_rede` completam (IF estrutural, não decisão da LLM) |
| `DEMO-SOLAR-03-calculadora-payback` | `1CAQyhiSw2pKvdXK` | Webhook próprio `/webhook/payback-solar`, Code node determinístico + formatação Sonnet, grava `Simulacoes` + `simulacao` na sessão |

Chavinha `/solar` na Central de Demos (skill `kronos-central-demos`, patch no nó "Roteia" do
roteador `2hYQv4sOQq5AOXmt`).

## Voice Agent (ligação) — ElevenLabs

Agente `agent_1801kx3zb2wtem6v923vgy8mwy5f` (Helena - Zênite Solar): voz **Roberta**, LLM
**Claude Sonnet 4.6**, idioma pt-BR. 2 ferramentas webhook **síncronas** (`responseMode:
responseNode` — diferente dos webhooks assíncronos do WhatsApp, que respondem `onReceived` e
processam em segundo plano):

| Ferramenta | Workflow n8n | Webhook |
|---|---|---|
| `calcular_payback` | `5IrRDmb7ViJOyPhU` | `/webhook/helena-payback` — roda o mesmo cálculo determinístico, responde a mensagem já formatada pra IA falar |
| `agendar_visita_tecnica` | `l6mcqTExEPS9eZGJ` | `/webhook/helena-visita` — grava direto em `Visitas_Tecnicas` + confirma no WhatsApp |

Seguir skill `kronos-voice` (receita v2) pra clonar esse padrão em outro nicho.

## Pegadinhas (queimaram tempo nesta montagem)

- **`$json` muda de contexto a cada node.** No workflow 03, o node "Atualizar Sessão c/ Simulação"
  vinha depois de "Registrar Simulação" (Google Sheets) — `$json.numero`/`$json.resultado`
  apontavam pro **retorno do node anterior** (que não tem esses campos), não pro payload original.
  Fix: `$('Parsear Formatação').first().json...`. Lição: sempre nomear o node de origem explicitamente
  quando o valor precisa "atravessar" um node no meio do caminho.
- Ativar workflow novo **pega na hora** sem restart do n8n (testado 09/07) — restart só é
  obrigatório quando se **edita** um workflow que já estava publicado/ativo.
- Rodar vários testes do harness em rajada (< 10s entre disparos) pode estourar o rate limit de
  leitura do Google Sheets API (`Quota exceeded... Read requests per minute`) — não é bug do
  workflow, é só espaçar os disparos de teste.
- Parser Sonnet 5: `content.find(b => b.type === 'text')?.text` — NUNCA `content[0].text` (thinking vem primeiro)
- Sonnet 5 **sem `temperature`** (400)
- Error Trigger → Error Handler central `X29vC9p5WB38iZFI` em todos os workflows
- Helena nunca inventa placas/investimento/economia/payback (só a calculadora), nunca simula parcela de financiamento

## Limitação MVP conhecida — CONTA_LUZ sem OCR real

Quando o cliente manda foto/PDF da conta de luz, o orquestrador detecta o tipo de mídia e roteia
pra Helena **sem** extrair o valor automaticamente — ela pede o valor digitado (fallback gracioso,
documentado no prompt live e na base de conhecimento). Adicionar leitura real (vision/OCR) é
trabalho futuro; ver a seção "IMPORTANTE SOBRE IMAGENS" no prompt da Helena antes de prometer essa
capacidade numa demo ao vivo.

## Parâmetros da calculadora a revisar periodicamente

Tarifa R$1,05/kWh (CPFL Campinas), HSP 5,2, FATOR_FIO_B 0,92 (Lei 14.300, cai até 2028), tabela
R$/kWp por porte — todos hardcoded no Code node dos workflows 03 e na ferramenta de voz
`calcular_payback`. Editar os **dois lugares** se o parâmetro mudar (não há fonte única hoje).

## Material comercial

- Demo PNG de prospecção: `07_Recursos/demo_solar.png` (skill `kronos-demo-whatsapp`)
- Aba animada na landing: seção "Por segmento" → `#seg-solar` em `07_Recursos/index.html` (skill
  `kronos-nicho-landing-demo`), accent navy+âmbar (`#f5a623`)

## Depois do n8n (checklist README)

Proposta comercial + deploy da landing atualizada → teste ao vivo do Allan (só com tudo montado).
