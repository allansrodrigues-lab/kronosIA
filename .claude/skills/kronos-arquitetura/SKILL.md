---
name: kronos-arquitetura
description: Operar e customizar o nicho Arquitetura da Kronos — Estúdio Traço (fictício) com a Marina (qualificação de projeto + ⭐ calculadora de estimativa por m² + ⭐ filtro determinístico de pedido técnico + briefing). Use para testar a demo, corrigir a Marina, ajustar faixas de honorário, adaptar para escritório real, ou diagnosticar falha nos workflows. Gatilhos: "arquitetura", "Estúdio Traço", "Traço", "Marina", "estimativa de projeto", "briefing", "bot de arquiteto", "demo arquitetura", "pedido técnico".
---

# Kronos — Nicho Arquitetura (Estúdio Traço / Marina)

## Mapa do nicho
| Peça | ID / caminho |
|---|---|
| Orquestrador | `tHFU2KbsogpVq3wE` — `DEMO-ARQ-01-orquestrador-traco` (webhook `/webhook/whatsapp-arquitetura-demo`) |
| Agente Marina | `NDwmJkELDwXMnOPx` — `DEMO-ARQ-02-agente-marina` (sub-workflow) |
| CRM | planilha `1rXds8GoSGT5zT4LHzn7atNSJObStcxsgq65pUHRWKTY` (abas Sessoes_Arquitetura, Briefings, Leads_Arquitetura, Log_Conversas) |
| Chavinha | `/arquitetura` no `kronos-roteador-demo` (`2hYQv4sOQq5AOXmt`) |
| Harness | cenários `ARQ01-ARQ08` em `/docker/test-harness/run_tests.py` no VPS |
| Base local | `17_Arquitetura/` (agentes + base_conhecimento) |

## ⭐ Diferenciais (não quebrar)
1. **Filtro de Pedido Técnico** — Code node `Filtro Pedido Técnico` no orquestrador, roda ANTES do Haiku. Pergunta técnica (tirar parede, cálculo estrutural, ART/RRT, laudo) = ato privativo de arquiteto (Lei 12.378/2010) → resposta padrão fixa + redireciona pro briefing. O harness valida com `expected: PEDIDO_TECNICO` (detectado pela presença do nó `Preparar Resposta Técnica` na execução).
2. **Calculadora de Estimativa** — Code node `Calculadora de Estimativa` DENTRO da Marina, roda ANTES do prompt. Extrai tipo+área do texto/sessão com **normalização BR** (`1.500 m²` = 1500; vírgula = decimal) e injeta a faixa no system prompt ("use EXATAMENTE estes números"). Faixas por m²: residencial 80-150 · comercial 90-160 · interiores 70-120 · reforma 60-110. Área < 30 m² → projeto por ambiente; > 1.500 m² → escala humano.
3. Marina **nunca** fecha valor exato, promete prazo de prefeitura, critica outro profissional, nem dá orientação técnica.

## Testar a demo
1. Chavinha: mandar `/arquitetura` pelo WhatsApp do dono (`5519971266736`) pro chip `clinica01`.
2. Sem WhatsApp (harness manual):
```bash
curl -X POST https://n8n.kronosintelligence.com.br/webhook/whatsapp-arquitetura-demo \
  -H "Content-Type: application/json" \
  -d '{"event":"messages.upsert","instance":"clinica01","data":{"key":{"remoteJid":"5500TEST90001@s.whatsapp.net","fromMe":false,"id":"TESTARQ"},"pushName":"Teste","message":{"conversation":"Quanto custa um projeto de casa de 150m2?"},"messageType":"conversation","messageTimestamp":1716825600}}'
```
3. Suite: `ssh vps 'cd /docker/test-harness && python3 run_tests.py'` — ARQ01-ARQ08 devem ficar verdes.

## Ajustar faixas de honorário
Editar em DOIS lugares (manter em sincronia): `17_Arquitetura/base_conhecimento/02_precos_honorarios.md` (documentação) e o objeto `FAIXAS` no Code node `Calculadora de Estimativa` da Marina (o que vale em produção).

## Adaptar pra escritório real
Regra-mãe: instância Evolution própria + planilha CRM própria. Trocar: nome/endereço/telefone no `Montar Prompt Marina`, faixas de honorário, `documentId` dos 6+ nós Sheets (Marina) e 2 nós (orquestrador), e o webhook path. Voice Agent e logo seguem o padrão das skills `kronos-voice` e Canva.

## Pegadinhas conhecidas
- Sheets "Forbidden" = planilha não compartilhada com `kronos-n8n@kronos-ia-498605.iam.gserviceaccount.com` (Editor).
- O buffer usa a data table compartilhada `demo_buffer_mensagens` (`nGMa7pY70kK6k8ZA`) — mesma dos outros nichos, chaveada por telefone.
- Voz: o nó `Responder em Voz` da Marina ainda usa o `voice_id` da Vera (`Xb7hH8MSUJpSbSDYk0k2`) — trocar quando o Voice Agent próprio da Marina for criado.
- Referências por nome de nó (`$('Calculadora de Estimativa')`) quebram se renomear nós.
