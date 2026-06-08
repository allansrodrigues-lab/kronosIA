# Como conectar o Workflow 01 ao Workflow 02 (Bia)

> Este guia explica como adicionar ao Workflow 01 (Orquestrador):
> 1. Verificação de sessão ativa — para redirecionar mensagens durante uma conversa em andamento
> 2. Chamada ao sub-workflow da Bia — quando o intent for `AGENDAR`

---

## Visão geral das mudanças

### Estado atual do Workflow 01:

```
[Webhook] → [Normalizar] → [Montar Prompt] → [Classificar] → [Parsear] → [É Reclamação?]
                                                                                 ↙    ↘
                                                                          [Escalar] [Normal] → [Enviar] → [Log]
```

### Estado após as mudanças:

```
[Webhook] → [Normalizar] → [Buscar Sessão Ativa] → [Tem Sessão?]
                                                         ↙         ↘
                                              SIM: [Redirecionar     NÃO: [Montar Prompt] → [Classificar] → [Parsear]
                                                    para Agente]               ↓                                  ↓
                                                         ↓              [É Reclamação?]                  [Switch Intent]
                                                    [Bia/Clara]             ↙    ↘                            ↓(AGENDAR)
                                                                     [Escalar] [Normal]              [Chamar Bia]
                                                                         ↓        ↓                       ↓
                                                                     [Enviar]  [Enviar]              [Enviar] → [Log]
```

---

## Parte 1 — Adicionar verificação de sessão ativa

### Passo 1.1 — Adicionar node "Buscar Sessão Ativa"

Abra o Workflow 01 no n8n.

Insira um novo node **entre** `Normalizar Payload` e `Montar Prompt Haiku`:

1. Clique na seta que conecta `Normalizar Payload` → `Montar Prompt Haiku`
2. Clique no `+` que aparece no meio da seta
3. Adicione: `google sheets` → **Google Sheets**

**Configuração:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Get Many Rows` |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Sessoes_Ativas` |
| Return All Rows | **Ativo** |

**"Continue on Fail":** ative.

**Renomear:** `Buscar Sessão Ativa`

---

### Passo 1.2 — Adicionar node "Tem Sessão Ativa?"

Insira um **IF node** entre `Buscar Sessão Ativa` e `Montar Prompt Haiku`:

1. Clique na seta `Buscar Sessão Ativa` → `Montar Prompt Haiku`
2. `+` no meio → `if` → **IF**

**Configuração:**

Este node precisa checar, via Code, se existe sessão ativa para o telefone atual.
Como o IF não permite código JavaScript, use um **Code node** em vez de um IF:

> **Substitua o IF por um Code node chamado "Verificar Sessão Ativa":**

```javascript
const telefone = $('Normalizar Payload').first().json.telefone;
const todasSessoes = $input.all();

// Procura sessão ativa para este telefone (qualquer agente)
const sessaoAtiva = todasSessoes.find(
  s => s.json.Telefone === telefone && s.json.Status === 'ativo'
)?.json ?? null;

const ctx = $('Normalizar Payload').first().json;

return [{
  json: {
    ...ctx,
    sessaoAtiva,
    temSessao: sessaoAtiva !== null,
    agenteSessao: sessaoAtiva?.Agente ?? null
  }
}];
```

**Renomear:** `Verificar Sessão Ativa`

---

### Passo 1.3 — Adicionar IF "Tem Sessão?"

Após `Verificar Sessão Ativa`, adicione um **IF node**:

| Campo | Valor |
|---|---|
| Value 1 | `={{ $json.temSessao }}` |
| Operation | `is true` |

- **True branch** → Redirecionar para o agente ativo
- **False branch** → Continua para `Montar Prompt Haiku` (fluxo normal)

**Conecte o False branch** para `Montar Prompt Haiku`.

**Renomear:** `Tem Sessão?`

---

### Passo 1.4 — Adicionar node "Redirecionar para Agente"

Na branch **TRUE** do node `Tem Sessão?`, adicione um **Switch node**:

| Campo | Valor |
|---|---|
| Mode | `Rules` |
| Value | `={{ $json.agenteSessao }}` |

**Regras:**

| # | Equals | Output |
|---|---|---|
| 1 | `BIA` | Redirecionar para Bia |
| 2 | `CLARA` | Redirecionar para Clara *(futuro)* |

**Renomear:** `Redirecionar para Agente`

---

### Passo 1.5 — Conectar output "Redirecionar para Bia" ao sub-workflow

Na saída 1 (BIA) do Switch, adicione um **Execute Workflow node**:

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | `02-agendamento-bia` (selecione pelo nome) |
| Wait For Sub-Workflow | Ativo |

**Campos para passar:**
- Use `={{ $json }}` no corpo — passa todos os campos do contexto atual

**Renomear:** `Chamar Bia (Sessão Ativa)`

---

## Parte 2 — Chamar Bia quando intent = AGENDAR

### Passo 2.1 — Adicionar Switch de Intent

Após o node `Parsear Intent` (que já existe no Workflow 01), a ramificação atual é apenas `É Reclamação?` com dois branches.

Você precisa substituir ou expandir esta lógica para ter um roteamento por intent completo.

**Opção recomendada:** Mantenha o `É Reclamação?` como está, mas adicione um **Switch node** antes dele, especificamente para o intent `AGENDAR`:

1. Insira um **IF node** entre `Parsear Intent` e `É Reclamação?`

**Configuração:**

| Campo | Valor |
|---|---|
| Value 1 | `={{ $json.intent }}` |
| Operation | `equals` |
| Value 2 | `AGENDAR` |

- **True branch** → Chamar Bia
- **False branch** → `É Reclamação?` (fluxo existente)

**Renomear:** `É AGENDAR?`

---

### Passo 2.2 — Adicionar node "Chamar Bia"

Na branch **TRUE** do `É AGENDAR?`, adicione um **Execute Workflow node**:

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | `02-agendamento-bia` |
| Wait For Sub-Workflow | Ativo |

**Renomear:** `Chamar Bia`

> **Nota:** Quando "Wait For Sub-Workflow" está ativo, o Orquestrador aguarda a Bia terminar.
> A Bia já envia a mensagem diretamente ao cliente — o Orquestrador não precisa reenviar.

---

### Passo 2.3 — Conectar o Log do Sheets ao resultado de Bia

Após o `Chamar Bia`, adicione o node `Log no Sheets` (ou conecte ao existente para registrar que o Orquestrador redirecionou para a Bia):

```javascript
// Code node "Montar Log Bia" (opcional — para registrar no log principal do Orquestrador)
const ctx = $input.first().json;
return [{
  json: {
    telefone: ctx.telefone,
    nome: ctx.nome,
    texto: ctx.texto,
    intent: 'AGENDAR',
    mensagemParaCliente: '[redirecionado para Bia]',
    ehEscalacao: false,
    timestamp: ctx.timestamp
  }
}];
```

---

## Diagrama final do Workflow 01 atualizado

```
[Webhook WhatsApp]
        ↓
[Normalizar Payload]
        ↓
[Buscar Sessão Ativa]  ← novo
        ↓
[Verificar Sessão Ativa]  ← novo (Code)
        ↓
[Tem Sessão?]  ← novo (IF: temSessao = true)
     ↙ TRUE                     ↘ FALSE
[Redirecionar para Agente]   [Montar Prompt Haiku]
     ↓(BIA)                        ↓
[Chamar Bia (Sessão Ativa)]   [Claude Haiku — Classificar]
     ↓                              ↓
[Log no Sheets]             [Parsear Intent]
                                    ↓
                           [É AGENDAR?]  ← novo (IF)
                            ↙ TRUE         ↘ FALSE
                        [Chamar Bia]    [É Reclamação?]
                            ↓               ↙    ↘
                        [Log Sheets]  [Escalar] [Normal]
                                          ↓         ↓
                                       [Enviar] [Enviar]
                                          ↓         ↓
                                      [Log Sheets] [Log Sheets]
```

---

## Checklist para a conexão

- [ ] Node `Buscar Sessão Ativa` inserido entre `Normalizar Payload` e `Montar Prompt Haiku`
- [ ] Node `Verificar Sessão Ativa` (Code) configurado
- [ ] Node `Tem Sessão?` (IF) com branch TRUE → Redirecionar e FALSE → Montar Prompt Haiku
- [ ] Node `Redirecionar para Agente` (Switch) com regra BIA
- [ ] Node `Chamar Bia (Sessão Ativa)` (Execute Workflow) apontando para `02-agendamento-bia`
- [ ] Node `É AGENDAR?` (IF) inserido entre `Parsear Intent` e `É Reclamação?`
- [ ] Node `Chamar Bia` (Execute Workflow) na branch TRUE
- [ ] Workflow 02 ativado antes de testar o Workflow 01
- [ ] Teste com mensagem "quero agendar" → deve chamar Bia e criar sessão
- [ ] Teste com resposta de retorno → deve ser roteada para Bia via sessão ativa

---

## Importante: ordem de ativação

1. Ative primeiro o **Workflow 02** (02-agendamento-bia) — se estiver inativo, o Execute Workflow falhará
2. Depois ative (ou mantenha ativo) o **Workflow 01**
3. Certifique-se que as **4 novas abas** do Sheets existem antes de ativar
