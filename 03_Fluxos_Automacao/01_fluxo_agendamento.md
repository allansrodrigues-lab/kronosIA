# Fluxo 01 — Agendamento

## Objetivo
Permitir que o cliente agende, remarque ou cancele um procedimento via WhatsApp sem intervenção humana, mantendo a agenda do Google Calendar sincronizada e enviando lembretes automáticos.

## Gatilho
- Mensagem recebida no WhatsApp com intenção classificada como `AGENDAR`, `REMARCAR` ou `CANCELAR`.

## Passos (workflow n8n)

```
1. Webhook (recebe mensagem do orquestrador)
2. Switch (intenção: agendar / remarcar / cancelar)
   │
   ├── AGENDAR
   │    a. Agente IA pergunta: procedimento desejado
   │    b. Busca disponibilidade no Google Calendar (próximos 14 dias)
   │    c. Apresenta 3 opções de horário
   │    d. Confirma com o cliente
   │    e. Cria evento no Calendar (com nome, telefone, procedimento)
   │    f. Salva linha no Google Sheets (CRM)
   │    g. Envia mensagem de confirmação + instruções pré-procedimento
   │
   ├── REMARCAR
   │    a. Busca agendamento atual do cliente
   │    b. Apresenta novas opções
   │    c. Atualiza Calendar e Sheets
   │
   └── CANCELAR
        a. Confirma cancelamento com o cliente
        b. Remove evento do Calendar
        c. Marca linha no Sheets como "cancelado"
        d. Pergunta se quer reagendar
```

## Sub-fluxo: lembrete 24h antes
- **Cron:** roda a cada hora
- Busca eventos do Calendar nas próximas 24-25h
- Envia template WhatsApp: *"Olá [Nome]! Lembrando seu [procedimento] amanhã às [hora]. Responda 1 para CONFIRMAR ou 2 para REMARCAR."*
- Se confirmar: marca no Sheets
- Se remarcar: dispara fluxo de remarcação
- Se não responder em 4h: envia segundo lembrete

## Integrações usadas
- WhatsApp Cloud API (envio + recebimento)
- Google Calendar (CRUD de eventos)
- Google Sheets (registro de status)
- Anthropic Claude (interpretação e geração de mensagens)

## Tratamento de erros
- Sem horário disponível → oferece lista de espera
- Cliente não confirma em 24h → marca como "risco de no-show" e notifica recepção
- Erro de API do Calendar → fallback para criar tarefa manual no Sheets + alerta

## Métricas geradas
- `agendamentos_criados_dia`
- `taxa_confirmacao_24h`
- `taxa_no_show`
- `tempo_medio_agendamento` (segundos da primeira msg até confirmação)
