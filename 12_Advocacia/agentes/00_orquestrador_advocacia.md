# Orquestrador — Escritório de Advocacia (Demo Kronos)

## Modelo: Claude Haiku (claude-haiku-4-5-20251001)

Classifica o intent da mensagem e roteia para o agente ou serviço correto.

---

## Prompt do Haiku (nó "Montar Prompt Haiku")

```
Você é um classificador de intenções para um escritório de advocacia.
Analise a mensagem do cliente e retorne APENAS um JSON com o intent.

INTENTS DISPONÍVEIS:
- TRIAGEM: cliente descreve um problema ou caso jurídico (trabalhista, civil, família, etc.)
- CONSULTA_AGENDAMENTO: quer agendar uma consulta ou reunião com advogado
- DUVIDA_AREA: pergunta sobre quais áreas o escritório atende, o que fazem
- DOCUMENTO: mensagem indica que enviou ou vai enviar um PDF/documento para análise
- ACOMPANHAMENTO: cliente existente quer saber do andamento do caso
- RECLAMACAO: reclamação sobre atendimento, prazo ou processo
- OUTRO: qualquer coisa que não se encaixa acima

MENSAGEM: "${texto}"

Responda APENAS:
{"intent": "INTENT_AQUI"}
```

---

## Roteamento

| Intent | Destino |
|---|---|
| TRIAGEM | → Léa (01_agente_triagem_lea) |
| CONSULTA_AGENDAMENTO | → Léa (fluxo agendamento) |
| DUVIDA_AREA | → Léa (explica áreas de atuação) |
| DOCUMENTO | → Serviço Análise PDF (kronos-analise-pdf) |
| ACOMPANHAMENTO | → Resposta direta: "Vou verificar com o responsável pelo seu caso. Qual seu nome completo?" + escalar humano |
| RECLAMACAO | → Escalação humana imediata |
| OUTRO | → Léa (ela decide o que fazer) |

---

## Diagrama do fluxo n8n

```
Webhook → Normalizar Payload → Buscar Sessão Ativa → Decidir Rota
  → Sessão LÉA ativa?     → Chamar Léa
  → É PDF? (docMessage)   → Análise PDF (sub-workflow)
  → Montar Prompt Haiku → Haiku → Parsear Intent
      → TRIAGEM / CONSULTA / DUVIDA / OUTRO → Chamar Léa
      → DOCUMENTO                            → Análise PDF
      → ACOMPANHAMENTO                       → Escalar Humano
      → RECLAMACAO                           → Escalar Humano
```

---

## Variáveis de ambiente necessárias

```
ANTHROPIC_API_KEY
EVO_BASE_URL
EVO_API_KEY
EVO_INSTANCE         = instancia_advocacia (criar quando tiver o número)
EVO_TEAM_NUMBER      = número ou JID do grupo da equipe jurídica
GOOGLE_SHEETS_CRM_ID = planilha exclusiva do escritório cliente
```
