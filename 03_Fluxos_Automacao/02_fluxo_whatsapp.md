# Fluxo 02 — Atendimento WhatsApp (Orquestrador)

## Objetivo
Receber toda mensagem do WhatsApp, classificar a intenção, e rotear para o agente especialista correto. É o "cérebro" do sistema.

## Gatilho
- Webhook do WhatsApp Cloud API: cada mensagem recebida.

## Passos (workflow n8n)

```
1. Webhook WhatsApp
2. Normaliza payload (extrai número, nome, mensagem, mídia)
3. Busca/cria contato no Sheets (CRM)
4. Busca histórico de conversa no Redis (últimas 10 mensagens)
5. Agente Classificador (Haiku) → retorna intent:
     - AGENDAR
     - DUVIDA_PROCEDIMENTO
     - DUVIDA_PRECO
     - POS_PROCEDIMENTO
     - RECLAMACAO
     - OUTRO
6. Switch por intenção → chama workflow especialista
7. Recebe resposta do especialista
8. Aplica guardrails (filtros de conteúdo proibido)
9. Envia resposta via WhatsApp
10. Salva interação no Redis + log no Sheets
```

## Regras de escalonamento humano (handoff)

O fluxo escala para um humano quando:
- Cliente digitar "humano", "atendente" ou "pessoa"
- Intent classificada como `RECLAMACAO`
- Agente respondeu 3x e cliente continua confuso
- Pergunta envolve diagnóstico médico
- Cliente solicita orçamento personalizado fora do padrão

Escalonamento = enviar resumo da conversa para um grupo WhatsApp da equipe + parar respostas automáticas por 4h.

## Integrações usadas
- WhatsApp Cloud API
- Anthropic Claude (Haiku para classificar, Sonnet para responder)
- Redis (memória curta)
- Google Sheets (histórico e CRM)

## Tratamento de erros
- LLM offline → resposta de "estou processando, retorno em instantes" + escalonamento
- Mensagem com mídia não suportada (áudio longo > 2min) → pede para escrever
- Spam (>20 msgs/min do mesmo número) → bloqueia temporariamente

## Métricas geradas
- `mensagens_recebidas_dia`
- `tempo_medio_resposta` (segundos)
- `taxa_resolucao_sem_humano`
- `intents_mais_comuns`
- `handoffs_dia`
