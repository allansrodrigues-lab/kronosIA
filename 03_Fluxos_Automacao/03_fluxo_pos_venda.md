# Fluxo 03 — Pós-venda e Fidelização

## Objetivo
Manter o relacionamento depois do procedimento, garantir cuidados pós, coletar feedback e estimular recompra.

## Gatilho
- **Cron diário às 9h** — busca eventos do Calendar com status "concluído" nos últimos 30 dias.

## Trilha de mensagens

| Quando | Mensagem | Objetivo |
|---|---|---|
| **D+1** (dia seguinte) | "Olá [Nome]! Como você está se sentindo após o [procedimento]? Lembre-se de [cuidado principal]." | Cuidado pós + abrir canal |
| **D+3** | Mini-pesquisa: "De 0 a 10, qual sua satisfação?" | NPS |
| **D+7** | Foto comparativa (se aplicável) + dica de manutenção | Engajamento |
| **D+15** | Conteúdo educativo (próximos passos da pele/corpo) | Autoridade |
| **D+30** | "Está na hora da sua manutenção! Posso reservar um horário?" | Recompra |

## Lógica de personalização

Cada mensagem usa dados do CRM:
- Nome do cliente
- Procedimento realizado
- Profissional que atendeu
- Histórico (primeiro atendimento? cliente recorrente?)

E ajusta tom:
- Cliente novo → mais educativo
- Cliente recorrente → mais próximo, oferece pacote/desconto fidelidade

## Tratamento de respostas
- Resposta positiva (NPS ≥ 9) → pede review no Google
- Resposta negativa (NPS ≤ 6) → handoff imediato para a gerente
- Resposta neutra → registra para análise

## Integrações usadas
- Google Calendar (gatilho)
- Google Sheets (CRM e tracking)
- WhatsApp Cloud API (envio)
- Anthropic Claude (personalização das mensagens)

## Tratamento de erros
- Cliente bloqueou WhatsApp → marca no CRM, para fluxo
- Cliente reclamou → handoff imediato, pausa próximas mensagens

## Métricas geradas
- `taxa_resposta_d1`
- `nps_medio`
- `reviews_google_gerados`
- `taxa_recompra_d30`
- `ltv_medio`
