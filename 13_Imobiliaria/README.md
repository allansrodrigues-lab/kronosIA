# 13_Imobiliaria — Schalletti Imóveis (Demo Kronos)

Nicho **Imobiliária** da Kronos Intelligence — 1º da fila de ticket alto (comissão de venda paga a automação).
Marca 100% fictícia (padrão Bella Massa / Ferraz & Nogueira): **Schalletti Imóveis**, Campinas/SP.
Assistente: **Sofia** (qualificação + matching + visitas + ⭐ simulação de financiamento).

## Por que este nicho vende (pesquisa 03/07/2026)

- Só **19% das imobiliárias** no Brasil usam IA — oceano aberto
- **78% dos compradores fecham com o primeiro corretor que responde**; tempo médio de resposta do setor: 15h+. O bot responde em segundos
- Case do setor: conversão lead→visita de 3% para 8% com qualificação automática
- Posicionamento anti-objeção: "IA no operacional, humano no relacional" — o bot qualifica e agenda, o corretor fecha

## Estrutura

```
base_conhecimento/
  00_imobiliaria.md         — perfil da Schalletti (identidade, equipe, endereço fictícios)
  01_carteira_imoveis.md    — 12 imóveis fake (8 venda + 4 locação) + regras de matching
  02_politicas.md           — visitas, financiamento, locação, captação, LGPD, escalação
  03_tom_de_voz_sofia.md    — persona Sofia (calorosa, consultiva, nunca vendedora agressiva)
agentes/
  00_orquestrador_imobiliaria.md        — 9 intents (Haiku) + sessão + regras de desempate
  01_agente_atendimento_sofia.md        — prompt LIVE da Sofia (Sonnet 5): qualificação → matching 2-3 → visita
  02_agente_calculadora_financiamento.md — ⭐ Code node Price/SAC + formatação Sofia
workflows/
  workflow_orquestrador_imobiliaria_montagem.md — montagem n8n (reuso ~80% da Advocacia)
  workflow_crm_adapter_montagem.md              — 🔌 camada adaptadora de CRM (decisão-chave)
```

## 🔌 Arquitetura CRM Adapter (diferencial SaaS)

O bot nunca fala direto com Sheets/CRM — fala com o sub-workflow `[Imobiliária] - CRM Adapter`.
Trocar de CRM = trocar a env var `CRM_PROVIDER`. Conectores **pré-montados**: Google Sheets (ativo no
protótipo) + Vista CRM (sandbox grátis!) + Jetimob + Kenlo (desativados, prontos pra ligar no cliente real).
O cliente já paga o CRM dele — a chave de API é dele, a Kronos não paga nada.

## Status (03/07/2026)

- [x] Pesquisa de mercado do nicho
- [x] Nome cravado pelo Allan: Schalletti Imóveis
- [x] Peça 1 — Persona + agentes (Sofia, orquestrador, calculadora)
- [x] Peça 2 — Fluxo de atendimento (qualificação → matching → visita) documentado
- [x] Peça 3 — Base de conhecimento (4 arquivos)
- [x] Peça 4 — Carteira de imóveis fake
- [x] Spec do CRM Adapter com 3 conectores
- [x] Planilha CRM própria do nicho (abas conforme adapter) — `1bXnGkPZBNeDm_Uicr-sAVPY5ZMw1eHiM6h2ziaPwTWM`
- [x] Workflows no n8n — criados, validados, ATIVOS e testados fim-a-fim (03/07):
  - `YA2jMHR27ez9duUx` — DEMO-IMOB-01-orquestrador-schalletti (23 nodes)
  - `M7t1p5QYCNB8pE0q` — DEMO-IMOB-02-agente-sofia (25 nodes)
  - `Gd9NAe8SXPkXBGuT` — DEMO-IMOB-03-calculadora-financiamento (7 nodes)
  - `3YxOD6Qs1bpfSxRY` — DEMO-IMOB-04-crm-adapter (21 nodes, conectores Vista/Jetimob/Kenlo desativados)
- [x] Chavinha `/imobiliaria` na Central de Demos (roteador republicado, `/status` confirma)
- [x] Skill `kronos-imobiliaria`
- [ ] Logo + fachada via Canva IA (nunca à mão)
- [ ] Casos no test harness (`5500TEST*`) — smoke test manual passou (COMPRAR + continuação + financiamento); falta registrar a suíte no VPS
- [x] **Teste ao vivo do Allan — APROVADO 03/07 ~18h45** ("perfeita, sem erro"; conversa real completa, 10+ execuções todas verdes no n8n)

### Testes fim-a-fim executados (03/07, execuções n8n 10777–10788)

1. "quero comprar apartamento 2 quartos no Cambuí até 800 mil" → Haiku `COMPRAR` → Sofia ofereceu *SCH-001* (real da carteira), salvou perfil na sessão ✅
2. Continuação "quanto fica a parcela do SCH-001, entrada 20%, 30 anos" → rota de sessão direta (sem Haiku) + calculadora disparou sozinha: Price R$ 4.851, SAC 6.141→1.546, 3 disclaimers ✅
3. `/status` da chavinha lista `/imobiliaria` ✅ (linhas de teste da planilha já limpas)
