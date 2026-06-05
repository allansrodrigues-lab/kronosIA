# Fluxo 04 — Captação e Qualificação de Leads

## Objetivo
Capturar leads de múltiplos canais, qualificar rapidamente e direcionar os "quentes" para agendamento.

## Gatilhos
- Form do site preenchido
- DM no Instagram com palavra-chave (ex.: "tabela", "preço", "info")
- Anúncio de Lead Ads do Meta
- Mensagem WhatsApp de número novo

## Fluxo de qualificação (3 perguntas SPIN simplificado)

```
1. Lead entra → salva em "Leads brutos" no Sheets
2. Agente Marketing inicia conversa:
     P1: "Qual procedimento te interessa?"  (descobre intenção)
     P2: "É a primeira vez ou já fez antes?" (descobre maturidade)
     P3: "Tem alguma data em mente para começar?" (descobre urgência)
3. Score automático (0-100):
     - Procedimento com ticket alto → +30
     - Já fez antes (não é dor da primeira vez) → +20
     - Tem urgência (até 30 dias) → +30
     - Bairro próximo à clínica → +20
4. Switch por score:
     - Quente (≥70) → encaminha para fluxo de agendamento
     - Morno (40-69) → entra em nutrição (sequência de 5 mensagens em 14 dias)
     - Frio (<40) → mensagem educativa única + tag no CRM
```

## Sequência de nutrição (lead morno)

| Dia | Conteúdo |
|---|---|
| D+0 | Material educativo sobre o procedimento de interesse |
| D+3 | Depoimento real + foto antes/depois (com autorização) |
| D+7 | FAQ sobre cuidados e segurança |
| D+10 | Promoção limitada (ex.: avaliação gratuita) |
| D+14 | "Posso te chamar para uma avaliação sem compromisso?" |

## Integrações usadas
- Meta Lead Ads API (Fase 2)
- Tally / Typeform (formulário do site)
- Instagram Graph API (Fase 2)
- WhatsApp Cloud API
- Google Sheets (CRM)
- Anthropic Claude (conversa e classificação)

## Tratamento de erros
- Lead duplicado (mesmo número entrou por 2 canais) → mescla automaticamente
- Lead spam (mensagens genéricas/links) → marca e bloqueia

## Métricas geradas
- `leads_capturados_dia` (por canal)
- `score_medio_leads`
- `taxa_qualificacao` (% que respondeu as 3 perguntas)
- `taxa_conversao_lead_agendamento`
- `cac` (custo de aquisição, se houver dados de mídia paga)
