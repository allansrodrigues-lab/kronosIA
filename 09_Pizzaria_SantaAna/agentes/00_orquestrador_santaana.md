# Orquestrador — Pizzaria Santa Ana

## Modelo: Claude Haiku (claude-haiku-4-5-20251001)

Classifica o intent da mensagem e roteia para o agente correto.

---

## Prompt do Haiku (nó "Montar Prompt Haiku")

```
Você é um classificador de intenções para uma pizzaria.
Analise a mensagem do cliente e retorne APENAS um JSON com o intent.

INTENTS DISPONÍVEIS:
- FAZER_PEDIDO: cliente quer pedir, escolher sabor, montar pedido
- VER_CARDAPIO: quer ver o cardápio, sabores disponíveis
- VER_COMBO: pergunta sobre combos ou promoções
- RASTREAR_PEDIDO: quer saber onde está o pedido, tempo de entrega
- PRECO: pergunta de preço sem intenção clara de pedir ainda
- HORARIO_ENTREGA: pergunta se está aberto, horário, endereço
- RECLAMACAO: reclamação sobre pedido anterior, atendimento ou produto
- OUTRO: qualquer coisa que não se encaixa acima

MENSAGEM: "${texto}"

Responda APENAS:
{"intent": "INTENT_AQUI"}
```

---

## Roteamento

| Intent | Destino |
|---|---|
| FAZER_PEDIDO | → Ana (01-agente-pedido-santaana) |
| VER_CARDAPIO | → Ana |
| VER_COMBO | → Ana |
| RASTREAR_PEDIDO | → Resposta direta: "Vou verificar com nossa equipe! Um momento." + escalar humano |
| PRECO | → Ana |
| HORARIO_ENTREGA | → Resposta direta com horário e endereço |
| RECLAMACAO | → Escalação humana imediata |
| OUTRO | → Ana (ela decide o que fazer) |

---

## Resposta direta para HORARIO_ENTREGA

```
Estamos abertos das 18h às 23h55, todos os dias! 🍕
Endereço: Rua Sérgio Cozer, 260 — Jd. Marajoara, Pedreira/SP
Fone: (19) 98289-4384

Posso já anotar seu pedido?
```

---

## Diagrama do fluxo n8n

```
Webhook → Normalizar Payload → Buscar Sessão Ativa → Decidir Rota
  → Sessão ANA ativa?     → Chamar Ana
  → Montar Prompt Haiku → Haiku → Parsear Intent
      → FAZER_PEDIDO / VER_CARDAPIO / VER_COMBO / PRECO / OUTRO → Chamar Ana
      → HORARIO_ENTREGA → Resposta Direta
      → RASTREAR_PEDIDO → Escalar Humano
      → RECLAMACAO      → Escalar Humano
```

---

## Diferenças em relação ao orquestrador de clínica

| Item | Clínica | Pizzaria |
|---|---|---|
| Intents | AGENDAR, DUVIDA, POS_PROCEDIMENTO | FAZER_PEDIDO, VER_COMBO, RASTREAR |
| Agentes | Bia, Clara, Diana | Ana (único agente de pedido) |
| Sessão | Agendamento + follow-up | Carrinho ativo |
| Handoff | Google Calendar | Grupo WhatsApp equipe |
| Dado_Temp | contexto de agendamento | JSON do carrinho completo |

---

## Variáveis de ambiente necessárias

```
ANTHROPIC_API_KEY
EVO_BASE_URL
EVO_API_KEY
EVO_INSTANCE         = instancia_santaana (criar quando tiver o número)
EVO_TEAM_NUMBER      = número do grupo da equipe (para receber pedidos)
GOOGLE_SHEETS_CRM_ID = planilha exclusiva da Santa Ana
```
