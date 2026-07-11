---
name: kronos-prospeccao-robo
description: Operar a máquina de prospecção da Kronos — robô de disparo ativo (chip cobaia prospeccao01) + funil inbound da Eva (wa.me). Use para ligar/desligar o disparador, abastecer a fila, gerar código de pareamento, testar a Eva, ajustar templates de abordagem, ou diagnosticar "robô não disparou"/"alerta não chegou"/"chip caiu". Gatilhos, "bora ligar o robô", "abastece a fila", "pareia o chip", "testa a Eva", "prospecção automática", "chip cobaia".
---

# Máquina de Prospecção Kronos — robô outbound + Eva inbound

Duas frentes complementares (construídas 10/07/2026):
- **Outbound (robô)**: dispara 1ª abordagem padronizada pra fila do CRM pelo chip cobaia. SEM IA (custo zero).
- **Inbound (Eva)**: lead clica no link `wa.me`, manda a 1ª mensagem, Eva (Sonnet 5) qualifica, grava CRM e alerta o Allan. ~R$0,30-0,50/conversa.

## Mapa de peças

| Peça | ID / local |
|---|---|
| Disparador (cron 9h/14h/19h) | n8n `qVgwvD3ZW9COqdMA` — ⚠️ só ativar após aquecimento |
| Respostas (webhook + filtro É Prospect?) | n8n `RCg1zCr7RcSz1zmC` (ativo) |
| Eva prospecção | n8n `bnwAPhtE8CSEJS9d` (ativo), webhook `/webhook/eva-prospeccao` |
| Desvio da Eva no roteador | n8n `2hYQv4sOQq5AOXmt` (gatilho: texto com "agente"+"kronos") |
| Fila outbound | aba `Prospeccao` do Kronos CRM Interno `1tOXVM8frTwxbhCR1Gmb2dyPFNks8INCNSKWeg9t1UK4` |
| Leads da Eva | aba `Leads` da mesma planilha (Origem `prospeccao-<canal>`) |
| Chip cobaia | `5519997237404`, instância Evolution `prospeccao01` (descartável) |
| Links wa.me por canal | `07_Recursos/prospeccao_eva_links.md` |
| Doc do robô + templates | `07_Recursos/prospeccao_robo_disparador.md` |

**Números intocáveis (NUNCA viram cobaia nem recebem abordagem):** `5519971266736` (Kronos) e `5519971514971` (todos os protótipos).

## Operações comuns (tudo via MCP — mcp__n8n__* e mcp__google-sheets__*)

### Abastecer a fila
1. `get_sheet_data` na aba `Prospeccao` — candidato precisa de WhatsApp preenchido.
2. Normalizar WhatsApp pra **só dígitos** (`5519...`, 12-13 dígitos) e `Status = Fila` via `batch_update_cells`.
3. O robô ignora tudo que não for `Fila`/`Abordado_1`; ciclo: `Fila → Abordado_1 → (4d) → Abordado_2 → fim`, desvios `Respondeu`/`Nao_Perturbe`.

### Ligar / desligar o robô
- Ligar: `n8n_update_partial_workflow` no `qVgwvD3ZW9COqdMA` com `[{"type":"activateWorkflow"}]` → **restart do n8n** (skill `restart-n8n`). Desligar: `deactivateWorkflow` (efeito imediato no cron após restart).
- Regras fixas no nó `Preparar Rodada`: 2/rodada, 6/dia, esperas aleatórias, blocklist, follow-up 4d. Mudar limites = editar o jsCode desse nó (e re-publicar + restart).

### Parear / re-parear o chip (se cair ou banir)
No VPS (key nunca no chat — usar `\$KEY` dentro do SSH):
```bash
KEY=$(docker exec evolution-api printenv AUTHENTICATION_API_KEY)
curl -s "http://127.0.0.1:8080/instance/connect/prospeccao01?number=<NUMERO>" -H "apikey: $KEY"
```
→ devolve `pairingCode` (dar pro Allan digitar em Aparelhos conectados → Conectar com número). ⚡ **Pairing code funcionou direto do IP Hostinger em 10/07 — não precisou de proxy** (proxy segue como fallback se recusar repetidamente). Estado: `GET /instance/connectionState/prospeccao01` deve dar `open`.

### Testar a Eva (ponta a ponta, sem WhatsApp)
`curl -X POST https://n8n.kronosintelligence.com.br/webhook/whatsapp-demo` com payload Evolution (remoteJid `5500TEST*@s.whatsapp.net`) e `conversation` contendo "agente" + "Kronos". Conferir execução em `bnwAPhtE8CSEJS9d`, linha na aba `Leads` e (se quente) alerta no WhatsApp Kronos. Sessões Eva expiram em 24h; comando `/` do dono no roteador encerra a dele.

### Diagnóstico rápido
- **Robô não disparou**: workflow ativo? chip `open`? fila tem `Status=Fila` com WhatsApp válido? já bateu 6/dia? Ver execução do cron no `qVgwvD3ZW9COqdMA`.
- **Alerta não chegou**: resposta veio de número que está na aba `Prospeccao` com status ativo? (filtro "É Prospect?" derruba conversa pessoal de propósito — é o comportamento do aquecimento, não bug).
- **Eva muda**: quase sempre crédito Anthropic (`400 credit balance too low`) — checar antes de mexer no workflow (lição 10/07).
- Edição via MCP não "pegou" → versão publicada + restart (skills `n8n-edit`/`restart-n8n`).

## Guardrails (não negociar)
- Disparador NUNCA aponta pra outra instância que não `prospeccao01`.
- Não subir os limites (6/dia) sem semanas de chip saudável.
- Chip novo: **aquecer 7-10 dias** (uso humano normal) antes de ativar o robô.
- Sem link na 1ª mensagem fria. Robô nunca responde sozinho (anti-loop).
- Se o chip banir: perda aceita — novo chip pré-pago, re-parear, seguir. Nunca "dar um jeito" de burlar.
