# Dashboard de Métricas

## Stack recomendado (MVP barato)
- **Coleta:** workflows n8n exportam para Google Sheets
- **Visualização:** Looker Studio (gratuito) conectado ao Sheets
- **Alertas:** workflow n8n que checa Sheets diariamente e dispara Telegram/email

## Estrutura da planilha "Métricas"

### Aba `eventos`
Cada linha = 1 evento qualquer (msg recebida, agendamento criado, NPS coletado, etc.)

| timestamp | tipo_evento | origem | contato_id | dados_json |
|---|---|---|---|---|
| 2026-05-27 14:32 | mensagem_recebida | whatsapp | 5511... | {...} |
| 2026-05-27 14:32 | intent_classificada | aurora | 5511... | {"intent":"AGENDAR"} |
| 2026-05-27 14:33 | agendamento_criado | bia | 5511... | {"procedimento":"limpeza"} |

### Aba `kpis_diarios`
Agregado por dia (n8n calcula 1x/dia às 23h)

| data | msgs_recebidas | tempo_medio_resposta | agendamentos | no_show | nps_dia |
|---|---|---|---|---|---|
| 2026-05-27 | 47 | 38s | 12 | 1 | 9.2 |

### Aba `crm`
Cada cliente

| contato_id | nome | telefone | 1o_contato | ult_contato | total_atendimentos | ltv | tags |
|---|---|---|---|---|---|---|---|

## Layout do dashboard (Looker Studio)

### Página 1 — Visão Executiva
- Big numbers: receita do mês, agendamentos do mês, NPS médio, taxa no-show
- Gráfico linha: agendamentos por dia (últimos 30 dias)
- Gráfico pizza: distribuição de intents
- Tabela: top 5 procedimentos mais agendados

### Página 2 — Operação
- Tempo médio de resposta por hora do dia
- Taxa de handoff humano por dia
- Volume de mensagens por canal
- Erros do sistema (heatmap)

### Página 3 — Marketing
- Funil: leads → qualificados → agendados → compareceram → recompraram
- Performance por canal (WhatsApp orgânico, Instagram, Ads)
- Score médio dos leads
- CAC por canal

### Página 4 — Pós-venda
- NPS evolução (linha)
- Reviews gerados
- Taxa de recompra
- LTV médio por cohort de mês

## Atualização
- Dados brutos: tempo real (cada workflow grava)
- Dashboard: refresh a cada 1h
