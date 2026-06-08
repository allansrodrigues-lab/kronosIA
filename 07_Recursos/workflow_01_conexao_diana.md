# Como adicionar Diana ao Workflow 01 (intent POS_PROCEDIMENTO)

> Este guia expande o Workflow 01 para rotear o intent `POS_PROCEDIMENTO` para a Diana.
> Pré-requisito: você já executou `workflow_01_conexao_clara.md` e tem o Switch "Rotear por Intent" com 5+ regras.

---

## O que mudar no Workflow 01

### 1 — Adicionar regra ao Switch "Rotear por Intent"

Abra o node **"Rotear por Intent"** e adicione uma nova regra **antes do fallback**:

| # | Equals | Label | Conecta para |
|---|---|---|---|
| 6 | `POS_PROCEDIMENTO` | Diana | `Chamar Diana` |

O Switch completo fica assim:

| # | Intent | Destino |
|---|---|---|
| 1 | `AGENDAR` | Chamar Bia |
| 2 | `DUVIDA_PROCEDIMENTO` | Chamar Clara |
| 3 | `DUVIDA_PRECO` | Chamar Clara |
| 4 | `LEAD_NOVO` | Chamar Clara |
| 5 | `RECLAMACAO` | Preparar Escalação |
| 6 | `POS_PROCEDIMENTO` | Chamar Diana ← **novo** |
| Fallback | — | Preparar Resposta Normal |

---

### 2 — Adicionar node "Chamar Diana" (Execute Workflow)

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | `05-pos-venda-diana` |
| Wait For Sub-Workflow | Ativo |

**Input:** `={{ $json }}`

**Renomear:** `Chamar Diana`

**Conecte:** saída 6 do Switch → `Chamar Diana`

---

### 3 — Adicionar Diana no roteamento de sessões ativas

No node **"Redirecionar para Agente"** (Switch de sessões ativas), adicione:

| # | Equals | Output |
|---|---|---|
| 1 | `BIA` | Chamar Bia (Sessão Ativa) |
| 2 | `CLARA` | Chamar Clara (Sessão Ativa) |
| 3 | `DIANA` | Chamar Diana (Sessão Ativa) ← **novo** |

Adicione o node `Chamar Diana (Sessão Ativa)`:

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | `05-pos-venda-diana` |
| Wait For Sub-Workflow | Ativo |

**Renomear:** `Chamar Diana (Sessão Ativa)`

> Isso garante que, se o cliente enviar outra mensagem durante uma sessão pós-venda em andamento, o Orquestrador retoma a Diana sem reclassificar o intent.

---

## Diagrama final do Workflow 01 (completo)

```
[Webhook WhatsApp]
        ↓
[Normalizar Payload]
        ↓
[Buscar Sessão Ativa]
        ↓
[Verificar Sessão Ativa]
        ↓
[Tem Sessão?]
     ↙ TRUE                      ↘ FALSE
[Redirecionar para Agente]    [Montar Prompt Haiku]
  ↓(BIA) ↓(CLARA) ↓(DIANA)         ↓
 [Bia]  [Clara]  [Diana]       [Claude Haiku]
  (Sess) (Sess)  (Sess)             ↓
    ↓      ↓      ↓            [Parsear Intent]
    ↓      ↓      ↓                 ↓
    ↓      ↓      ↓     [Rotear por Intent]
    ↓      ↓      ↓   ↙(1)  ↙(2,3,4) ↙(5) ↙(6)  ↘
    ↓      ↓      ↓  [Bia] [Clara] [Esc] [Diana] [Normal]
    └──────┴──────┘      ↓       ↓      ↓      ↓      ↓
                         └───────┴──────┴──────┴──────┘
                                        ↓
                               [Enviar Mensagem]
                                        ↓
                                [Log no Sheets]
```

---

## Quando a Diana é acionada

A Aurora (Haiku) classifica como `POS_PROCEDIMENTO` quando o cliente envia mensagem após um procedimento realizado. Para isso funcionar bem, o intent precisa estar na lista de possíveis intents do prompt da Aurora.

### Verificar/atualizar prompt da Aurora no Workflow 01

No node **"Montar Prompt Haiku"** do Workflow 01, confirme que a lista de intents inclui `POS_PROCEDIMENTO`:

```
INTENTS DISPONÍVEIS:
- AGENDAR: quer marcar, remarcar, cancelar horário
- DUVIDA_PROCEDIMENTO: pergunta sobre procedimentos, contraindicações, resultados
- DUVIDA_PRECO: pergunta sobre valores, pacotes, formas de pagamento
- LEAD_NOVO: primeira mensagem ou apresentação sem intent claro
- RECLAMACAO: insatisfação, reclamação, problema com atendimento
- POS_PROCEDIMENTO: menciona que já fez um procedimento, como se sentiu, resultados, cuidados pós
- OUTRO: qualquer coisa fora dos casos acima
```

> Se `POS_PROCEDIMENTO` não estiver no prompt da Aurora, adicione a linha acima. O intent pode cair no fallback sem esta atualização.

---

## Estratégia de disparo proativo da Diana

Além de aguardar o cliente contatar, a Diana pode ser disparada **proativamente** 2-4h após o procedimento via Cron:

```
Cron Workflow (futuro):
  ├── A cada hora: busca em Agendamentos onde Data_Hora < agora - 2h
  ├── Status = confirmado AND Diana_Disparada IS NULL
  ├── Para cada agendamento: chama Workflow 05 com intent POS_PROCEDIMENTO
  └── Marca Diana_Disparada = SIM no Sheets
```

> Isso exige adicionar coluna `Diana_Disparada` na aba `Agendamentos`. Implementação descrita nos próximos passos do projeto.

---

## Checklist

- [ ] Regra `POS_PROCEDIMENTO` adicionada ao Switch "Rotear por Intent"
- [ ] Node "Chamar Diana" (Execute Workflow) conectado à saída 6
- [ ] Node "Chamar Diana (Sessão Ativa)" no roteamento de sessões
- [ ] Prompt da Aurora atualizado com intent `POS_PROCEDIMENTO`
- [ ] Workflow 05 ativo antes de testar
- [ ] Aba `Feedback_PosVenda` criada no Sheets
- [ ] Teste com `intent = POS_PROCEDIMENTO` → Diana pergunta sobre bem-estar
- [ ] Sessão Diana criada em `Sessoes_Ativas` após o teste
