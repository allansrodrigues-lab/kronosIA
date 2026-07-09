# Montagem n8n — Nicho Solar (Zênite) — arquitetura definida na sessão Fable 09/07/2026

Espelho da arquitetura validada da Imobiliária (reuso ~85%). Este documento é o mapa
para a fase Sonnet montar sem re-decidir nada: clonar, repontar, publicar, testar.

---

## Workflows a criar (4)

| Nome no n8n | Clonar de | O que muda |
|---|---|---|
| `DEMO-SOLAR-01-orquestrador-zenite` | `DEMO-IMOB-01-orquestrador-schalletti` (`YA2jMHR27ez9duUx`) | Prompt Haiku (8 intents do solar), Switch de rotas, abas do Sheets |
| `DEMO-SOLAR-02-agente-helena` | `DEMO-IMOB-02-agente-sofia` (`M7t1p5QYCNB8pE0q`) | Prompt LIVE da Helena; sem matching de carteira — no lugar, injeta `${simulacao}` da sessão; handoff pra calculadora quando qualificação completa |
| `DEMO-SOLAR-03-calculadora-payback` | `DEMO-IMOB-03-calculadora-financiamento` (`Gd9NAe8SXPkXBGuT`) | Code node `calcular_payback_solar` (ver `02_agente_calculadora_payback.md`) + formatação Helena |
| `DEMO-SOLAR-04-visita-tecnica` | Motor de agendamento da Bia (workflow_02) | Evento "Visita técnica — {nome} ({bairro})", agenda do consultor, lembrete D-1 |

**Não criar CRM Adapter** — o nicho usa Sheets direto (adapter é diferencial da Imobiliária,
onde o cliente final tem CRM próprio; instaladora solar pequena não tem).

## Decisões de arquitetura (para não re-discutir na montagem)

1. **Rota `ORCAMENTO` é a espinha dorsal.** Helena qualifica → quando `valor_conta` + `tipo_imovel`
   + `fase_rede` estiverem na sessão, o workflow chama a calculadora **automaticamente** (IF no
   orquestrador checa a sessão, não depende de a Helena "decidir"). Lição Schalletti: fallback
   estrutural por código, nunca só prompt.
2. **`CONTA_LUZ` (foto/PDF da conta):** detectar por `messageType` (imagem/documento) ANTES do Haiku
   — mídia não passa pelo classificador. Rota: download → motor de leitura (Advocacia ♻️) → extrai
   valor médio → grava `valor_conta` na sessão → Helena confirma o valor com o cliente → calculadora.
   No MVP da demo, se o OCR falhar: Helena pede o valor digitado (fallback gracioso, sem erro).
3. **Simulação gravada na sessão como JSON** (campo `simulacao`) — a Helena referencia nas mensagens
   seguintes ("como te mostrei, o payback fica em...") sem recalcular.
4. **Fluxo pós-simulação:** calculadora responde → seta `status=simulacao` → próxima mensagem do
   cliente volta pra Helena com a simulação no contexto (rota de sessão direta, sem Haiku — padrão
   validado na Schalletti, execuções 10777–10788).
5. **Buffer/debounce 2,5s** (padrão dos bots), **IF voz** antes do classificador (transcrição ♻️ Aurora).
6. **Error Trigger** → Error Handler central `X29vC9p5WB38iZFI` em TODOS os 4 workflows + registrar
   no Self-Healing Monitor (`ADmfpDIilh48WwV3`).

## Planilha CRM própria (regra-mãe: isolada) — "Kronos CRM — Solar (Zênite)"

| Aba | Colunas |
|---|---|
| `Leads_Solar` | data, jid, nome, tipo_imovel, valor_conta, cidade, intent_inicial, status, origem |
| `Sessoes_Solar` | jid, nome, tipo_imovel, valor_conta, fase_rede, tipo_telhado, cidade, simulacao (JSON), status, historico, data_contato |
| `Simulacoes` | data, jid, nome, conta, kwp, placas, investimento, economia_mensal, payback, converteu_visita |
| `Visitas_Tecnicas` | data_agendada, periodo, jid, nome, endereco, status (agendada/realizada/proposta/fechou), obs |
| `Log_Conversas` | timestamp, jid, quem (cliente/helena), mensagem, intent |

A aba `Simulacoes` é ouro para a demo comercial: mostra ao dono da instaladora a taxa
simulação → visita (o KPI que vende o bot).

## Variáveis e integrações

- Mesma instância da Central de Demos (`clinica01`) — nova entrada `/solar` na chavinha
  (seguir `kronos-central-demos`; atualizar `/status`)
- `GOOGLE_SHEETS_SOLAR_ID` = ID da planilha nova (Settings → Variables no n8n)
- Modelos: Haiku classifica, Sonnet 5 responde (sem `temperature`), parser sempre
  `content.find(b => b.type === 'text')?.text`

## Test harness — 7 cenários a registrar (JIDs `5500TEST*` únicos por rodada)

| # | Mensagem | Intent esperado |
|---|---|---|
| S01 | "quanto custa colocar energia solar na minha casa?" | ORCAMENTO |
| S02 | "minha conta vem uns 900 reais" (sessão em qualificação) | ORCAMENTO (continuação) |
| S03 | "painel funciona em dia de chuva?" | DUVIDA_TECNICA |
| S04 | "dá pra parcelar o sistema?" | FINANCIAMENTO |
| S05 | "quero marcar a visita técnica pra sábado de manhã" | VISITA_TECNICA |
| S06 | "instalei com vocês e o app não mostra a geração" | POS_INSTALACAO |
| S07 | "tá atrasado 2 semanas e ninguém me responde" | RECLAMACAO |

Validação fim-a-fim extra (manual): S01→S02 completando qualificação deve disparar a calculadora
e gravar linha em `Simulacoes` (lição do test-harness: intent verde não garante escrita na planilha
— conferir a linha).

## Ordem de montagem (fase Sonnet)

1. Criar planilha CRM + abas → anotar ID
2. Clonar e adaptar os 4 workflows (nesta ordem: 03 calculadora → 02 Helena → 01 orquestrador → 04 visita)
3. Publicar os 4 (Execute Workflow exige sub publicado) + restart n8n
4. Registrar `/solar` na chavinha da Central de Demos
5. Rodar test harness (7 cenários) + validação fim-a-fim da calculadora
6. Só então: voz, demo visual, landing, skill, proposta
