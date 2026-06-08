# Como adicionar Clara ao Workflow 01 (roteamento completo)

> Este guia expande o Workflow 01 para rotear também para a Clara.
> Se você já fez o `workflow_01_conexao_bia.md`, esta é uma adição simples.

---

## O que mudar no Workflow 01

Você já tem (ou vai ter, pelo guia anterior) um node `É AGENDAR?` que desvia para a Bia.
Agora, após o `Parsear Intent`, você precisa de um roteamento completo por todos os intents.

**Recomendação:** substituir o IF `É AGENDAR?` por um **Switch** com todas as intents.

---

## Substituir "É AGENDAR?" por um Switch completo

### Passo 1 — Remover o node "É AGENDAR?" e "É Reclamação?"

> Se ainda não criou esses nodes, pule este passo — crie o Switch diretamente.

- Selecione e delete os nodes `É AGENDAR?` e `É Reclamação?`
- Mantenha os nodes de ação que eles conectavam (Chamar Bia, Preparar Escalação, Preparar Resposta Normal)

---

### Passo 2 — Adicionar Switch "Rotear por Intent"

Logo após o node `Parsear Intent`, adicione um **Switch**:

| Campo | Valor |
|---|---|
| Mode | `Rules` |
| Value | `={{ $json.intent }}` |

**Regras (6 outputs):**

| # | Equals | Label | Conecta para |
|---|---|---|---|
| 1 | `AGENDAR` | Bia | `Chamar Bia` |
| 2 | `DUVIDA_PROCEDIMENTO` | Clara | `Chamar Clara` |
| 3 | `DUVIDA_PRECO` | Clara (preço) | `Chamar Clara` *(mesma)* |
| 4 | `LEAD_NOVO` | Clara (lead) | `Chamar Clara` *(mesma)* |
| 5 | `RECLAMACAO` | Escalação | `Preparar Escalação` |
| Fallback | — | Resposta padrão | `Preparar Resposta Normal` |

> **Dica:** as saídas 2, 3 e 4 podem todas conectar ao mesmo node `Chamar Clara`.
> No n8n, você pode ligar múltiplas saídas ao mesmo node destino.

**Renomear:** `Rotear por Intent`

---

### Passo 3 — Adicionar node "Chamar Clara" (Execute Workflow)

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | `03-atendimento-clara` |
| Wait For Sub-Workflow | Ativo |

**Input:** `={{ $json }}`

**Renomear:** `Chamar Clara`

**Conecte:** saídas 2, 3 e 4 do Switch → `Chamar Clara`

---

### Passo 4 — Reconectar os nodes existentes

| Switch output | Destino |
|---|---|
| 1 (AGENDAR) | `Chamar Bia` (já existe do guia anterior) |
| 2, 3, 4 (Clara) | `Chamar Clara` (novo) |
| 5 (RECLAMACAO) | `Preparar Escalação` (já existe) |
| Fallback | `Preparar Resposta Normal` (já existe) |

---

## Diagrama final do Workflow 01

```
[Webhook WhatsApp]
        ↓
[Normalizar Payload]
        ↓
[Buscar Sessão Ativa]           ← verifica se há sessão ativa (BIA ou CLARA)
        ↓
[Verificar Sessão Ativa]        ← Code: filtra por telefone + Status = ativo
        ↓
[Tem Sessão?]                   ← IF: temSessao = true
     ↙ TRUE                          ↘ FALSE
[Redirecionar para Agente]       [Montar Prompt Haiku]
  ↓(BIA)      ↓(CLARA)                  ↓
[Chamar Bia  [Chamar Clara          [Claude Haiku]
 (Sessão)]    (Sessão)]                  ↓
     ↓             ↓               [Parsear Intent]
     ↓             ↓                    ↓
     ↓             ↓          [Rotear por Intent]
     ↓             ↓        ↙(1)  ↙(2,3,4) ↙(5)  ↘(fallback)
     ↓             ↓    [Bia]   [Clara]  [Escalar] [Normal]
     ↓             ↓       ↓        ↓       ↓         ↓
     ↓             ↓       ↓        ↓  [Notificar]   ↓
     ↓             ↓       ↓        ↓  [Equipe]      ↓
     └─────────────┘       └────────┴──────┴──────────┘
                                          ↓
                                  [Enviar Mensagem]
                                          ↓
                                   [Log no Sheets]
```

---

## Verificação de sessão ativa para Clara

No node `Redirecionar para Agente` (Switch), adicione a regra para `CLARA`:

| # | Equals | Output |
|---|---|---|
| 1 | `BIA` | Chamar Bia (Sessão) |
| 2 | `CLARA` | Chamar Clara (Sessão) |

E adicione o node `Chamar Clara (Sessão Ativa)`:

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | `03-atendimento-clara` |
| Wait For Sub-Workflow | Ativo |

**Renomear:** `Chamar Clara (Sessão Ativa)`

---

## Nota sobre `POS_PROCEDIMENTO`

O intent `POS_PROCEDIMENTO` ainda não tem sub-workflow (Diana é o próximo). Por enquanto, deixe no **Fallback** do Switch — a Aurora responde com a mensagem de transição que já foi enviada pelo Orquestrador, e a recepção assume manualmente.

Quando o Workflow 04 (Diana) for criado, você adiciona mais uma regra no Switch.

---

## Checklist

- [ ] Switch "Rotear por Intent" com 5 regras + fallback
- [ ] Node "Chamar Clara" (Execute Workflow) conectado às saídas 2, 3 e 4
- [ ] Node "Chamar Clara (Sessão Ativa)" no roteamento de sessões ativas
- [ ] Workflow 03 ativo antes de testar
- [ ] Teste com `intent = DUVIDA_PRECO` → Clara responde com tabela de preços
- [ ] Teste com `intent = LEAD_NOVO` → Clara faz apresentação calorosa
- [ ] Sessão Clara criada em `Sessoes_Ativas` após o teste
