# Workflow 05 — Agente de Pós-Venda "Diana" (Guia de Configuração)

> Sub-workflow chamado pelo Orquestrador quando `intent = POS_PROCEDIMENTO`.
> Diana faz o acompanhamento pós-atendimento: verifica bem-estar, coleta feedback, oferece orientações de cuidados e reaativa o cliente para nova sessão ou pacote.
> Para importar no n8n, use `workflow_05_pos_venda.json` na mesma pasta.

---

## Visão geral do fluxo

```
[Trigger — Receber do Orquestrador]
         ↓ (paralelo)
[Buscar Sessão Diana]   [Buscar Agendamento]   ← Sheets: Sessoes_Ativas + Agendamentos
         ↓
[Montar Prompt Diana]          ← Code: contexto do procedimento + histórico + KB de cuidados
         ↓
[Claude Sonnet — Diana]        ← HTTP: Anthropic API (temperature 0.5)
         ↓
[Parsear Resposta Diana]       ← Code: extrai mensagem + acao + etapa + feedback
         ↓
[Switch por Ação]
   ├── passar_para_bia  → [Preparar Passagem] → [Chamar Bia]
   ├── escalar_humano   → passthrough
   ├── tem feedback     → [Salvar Feedback] → Sheets: Feedback_PosVenda
   └── responder (default) → passthrough
         ↓ (todos convergem)
[Preparar Sessão]              ← Code: serializa histórico + etapa + dados de feedback
         ↓
[Enviar Mensagem WhatsApp]     ← HTTP: Evolution API
         ↓
[Atualizar Sessão Diana]       ← Sheets: append em Sessoes_Ativas
         ↓
[Log Interação Diana]          ← Sheets: append em Log_Interacoes
```

**Total: 14 nodes**

> **Diferença principal em relação à Clara:** Diana busca o agendamento do cliente no Sheets para personalizar as orientações ao procedimento realizado. Também grava feedback em aba dedicada.

---

## Abas do Google Sheets necessárias

| Aba | Uso | Nova? |
|---|---|---|
| `Sessoes_Ativas` | Histórico de conversa com Agente = `DIANA` | Não — já existe |
| `Log_Interacoes` | Log geral | Não — já existe |
| `Agendamentos` | Buscar procedimento realizado pelo telefone | Não — já existe |
| `Feedback_PosVenda` | Registrar nota + comentário do cliente | **Sim — criar** |

### Criar aba `Feedback_PosVenda`

Colunas (na ordem):

| Coluna | Tipo | Descrição |
|---|---|---|
| `Data` | Texto | Data/hora da avaliação |
| `Telefone` | Texto | Telefone do cliente |
| `Nome` | Texto | Nome do cliente |
| `Procedimento` | Texto | Procedimento avaliado |
| `Nota` | Número | 1 a 5 (pode ser null se não coletado) |
| `Comentario` | Texto | Comentário livre do cliente |
| `Interesse_Reagendamento` | Texto | `SIM` ou `NAO` |

---

## Pré-requisitos

Mesmos do Workflow 01, 02 e 03. Adicionalmente:
- Aba `Feedback_PosVenda` criada no Google Sheets
- Workflow 02 (Bia) ativo (para passagem de reagendamento)

---

## Fluxo conversacional da Diana

A Diana trabalha em 4 etapas progressivas ao longo da conversa:

| Etapa | Campo `etapa` | O que faz |
|---|---|---|
| Check-in | `checkin` | Pergunta como o cliente está se sentindo |
| Feedback | `feedback` | Coleta avaliação da experiência (nota 1-5) |
| Orientações | `orientacoes` | Dá cuidados específicos ao procedimento |
| Reativação | `reativacao` | Apresenta pacote / próxima sessão |

A Diana avança pelas etapas naturalmente ao longo da conversa, registrando a fase atual no Sheets para manter contexto entre mensagens.

---

## Node 1 — Trigger — Receber do Orquestrador

**Tipo:** Execute Workflow Trigger

**Dados recebidos:**

| Campo | Descrição |
|---|---|
| `telefone` | Número do cliente |
| `nome` | Nome do cliente |
| `texto` | Mensagem atual |
| `remoteJid` | JID para envio |
| `instancia` | Instância Evolution |
| `timestamp` | Timestamp Unix |
| `messageId` | ID da mensagem |
| `intent` | `POS_PROCEDIMENTO` |

---

## Node 2 — Buscar Sessão Diana (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Get Many Rows` |
| Sheet | `Sessoes_Ativas` |
| Return All Rows | Ativo |

Configure **"Continue On Fail"** ativo.

> Executa em **paralelo** com o Node 3. O Code node aguarda ambos.

---

## Node 3 — Buscar Agendamento (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Get Many Rows` |
| Sheet | `Agendamentos` |
| Return All Rows | Ativo |

Configure **"Continue On Fail"** ativo.

> Busca todos os agendamentos. O Code node filtra pelo telefone + status `confirmado` e pega o mais recente para saber qual procedimento foi realizado.

---

## Node 4 — Montar Prompt Diana (Code)

Node central. Faz três coisas:
1. Combina resultados de Sessão + Agendamento
2. Identifica o procedimento realizado (via `Agendamentos`)
3. Monta system prompt com KB de cuidados pós-procedimento

```javascript
const ctx = $('Trigger — Receber do Orquestrador').first().json;
const { telefone, nome, texto, remoteJid, instancia, timestamp, messageId, intent } = ctx;

// Buscar sessão Diana ativa
const todasSessoes = $('Buscar Sessão Diana').all();
const sessao = todasSessoes.find(
  s => s.json.Telefone === telefone && s.json.Agente === 'DIANA' && s.json.Status === 'ativo'
)?.json ?? null;

let historico = [];
if (sessao?.Historico) {
  try { historico = JSON.parse(sessao.Historico); } catch(e) {}
}

// Buscar último agendamento confirmado do cliente
const todosAgend = $('Buscar Agendamento').all();
const agendamento = todosAgend
  .filter(a => a.json.Telefone === telefone && a.json.Status === 'confirmado')
  .sort((a, b) => new Date(b.json.Data_Hora) - new Date(a.json.Data_Hora))
  [0]?.json ?? null;

const procedimentoRealizado = agendamento?.Procedimento ?? 'procedimento';
const dataAgendamento = agendamento?.Data_Hora ?? '';

historico.push({ role: 'user', content: texto });

// System prompt com KB de cuidados por procedimento
// (veja o JSON completo em workflow_05_pos_venda.json)
```

**Saída `anthropicBody`:**
- `model`: `claude-sonnet-4-6`
- `max_tokens`: 500
- `temperature`: 0.5 (ligeiramente mais calorosa que a Clara)
- `system`: prompt com 4 etapas + cuidados por procedimento

---

## Node 5 — Claude Sonnet — Diana (HTTP Request)

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `https://api.anthropic.com/v1/messages` |

**Headers:**

| Name | Value |
|---|---|
| `x-api-key` | `={{ $env.ANTHROPIC_API_KEY }}` |
| `anthropic-version` | `2023-06-01` |
| `Content-Type` | `application/json` |

**Body:** JSON/RAW → `={{ $json.anthropicBody }}`

Configure **"Continue On Fail"** ativo.

---

## Node 6 — Parsear Resposta Diana (Code)

Extrai os campos do JSON retornado pela Diana:

```javascript
const rawText = input.content?.[0]?.text ?? '{}';
// parsed contém:
// mensagem, acao, etapa, nota_feedback, comentario_feedback,
// interesse_reagendamento, encerrar_sessao
```

**Campos adicionais vs. Clara:**

| Campo | Tipo | Uso |
|---|---|---|
| `etapa` | string | Fase atual do pós-venda (checkin/feedback/orientacoes/reativacao) |
| `nota_feedback` | number\|null | Nota 1-5 coletada do cliente |
| `comentario_feedback` | string\|null | Comentário livre |
| `interesse_reagendamento` | boolean | Se cliente demonstrou interesse em reagendar |

---

## Node 7 — Switch por Ação (Switch)

| # | Condição | Label |
|---|---|---|
| 1 | `acao == "passar_para_bia"` | Passar para Bia |
| 2 | `acao == "escalar_humano"` | Escalar Humano |
| 3 | `nota_feedback != null` | Salvar Feedback |
| Fallback | — | Responder / Encerrar |

> **Atenção:** O branch "Salvar Feedback" é não-exclusivo — um mesmo item pode ter feedback **e** seguir para a sessão normalmente. Conecte a saída do Salvar Feedback também para o Preparar Sessão.

---

## Node 8 — Preparar Passagem para Bia (Code) — branch passar_para_bia

```javascript
const textoParaBia = `Quero agendar continuação: ${procedimento_realizado}`;

return [{
  json: {
    ...campos_base,
    contexto_bia: {
      telefone, nome, remoteJid, instancia, timestamp, messageId,
      texto: textoParaBia,
      intent: 'AGENDAR'
    }
  }
}];
```

---

## Node 9 — Chamar Bia (Execute Workflow) — branch passar_para_bia

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | `02-agendamento-bia` |
| Wait For Sub-Workflow | Ativo |

> A Bia receberá `texto = "Quero agendar continuação: [procedimento]"`, já sabendo o contexto.

---

## Node 10 — Salvar Feedback (Google Sheets) — branch tem feedback

| Campo | Valor |
|---|---|
| Operation | `Append Row` |
| Sheet | `Feedback_PosVenda` |

**Campos:**

| Column | Value |
|---|---|
| `Data` | `={{ new Date($json.timestamp * 1000).toLocaleString('pt-BR') }}` |
| `Telefone` | `={{ $json.telefone }}` |
| `Nome` | `={{ $json.nome }}` |
| `Procedimento` | `={{ $json.procedimento_realizado }}` |
| `Nota` | `={{ $json.nota_feedback }}` |
| `Comentario` | `={{ $json.comentario_feedback }}` |
| `Interesse_Reagendamento` | `={{ $json.interesse_reagendamento ? 'SIM' : 'NAO' }}` |

---

## Node 11 — Preparar Sessão (Code) — ponto de convergência

Conecte as saídas de: Escalar Humano, Responder/Encerrar, Chamar Bia e Salvar Feedback.

Diferença em relação à Clara: persiste `etapa`, `nota_feedback` e `interesse_reagendamento` em `Dado_Temp`.

---

## Node 12 — Enviar Mensagem WhatsApp (HTTP Request)

Mesmo padrão dos outros workflows.

**Body:** `={{ { number: $json.telefone, text: $json.mensagem } }}`

---

## Node 13 — Atualizar Sessão Diana (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Append Row` |
| Sheet | `Sessoes_Ativas` |
| `Agente` | `DIANA` |

Mesmo padrão do Workflow 02/03, com `Agente = 'DIANA'`.

---

## Node 14 — Log Interação Diana (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Append Row` |
| Sheet | `Log_Interacoes` |

Mesmo padrão dos outros workflows.

---

## Diagrama de conexões

```
[Trigger — Receber do Orquestrador]
           ↓ (fork paralelo)
[Buscar Sessão Diana]    [Buscar Agendamento]
           ↓ (merge no Code)
[Montar Prompt Diana]
           ↓
[Claude Sonnet — Diana]
           ↓
[Parsear Resposta Diana]
           ↓
[Switch por Ação]
   ↓(1)              ↓(2)       ↓(3)          ↓(4 fallback)
[Preparar         (Escalar)  [Salvar        (Responder/
 Passagem Bia]               Feedback]       Encerrar)
   ↓
[Chamar Bia]
   ↓                ↓            ↓                ↓
   └────────────────┴────────────┴────────────────┘
                    ↓
           [Preparar Sessão]
                    ↓
       [Enviar Mensagem WhatsApp]
                    ↓
       [Atualizar Sessão Diana]
                    ↓
        [Log Interação Diana]
```

---

## Como testar

### Teste 1 — Primeira interação pós-procedimento

```json
{
  "telefone": "5511999999999",
  "nome": "Ana Teste",
  "texto": "Oi",
  "remoteJid": "5511999999999@s.whatsapp.net",
  "instancia": "clinica",
  "timestamp": 1748908800,
  "messageId": "TEST-DIANA-001",
  "intent": "POS_PROCEDIMENTO"
}
```

**Esperado:** `etapa = "checkin"`, mensagem perguntando como a Ana está se sentindo após o procedimento.

### Teste 2 — Feedback positivo

```json
{
  ...
  "texto": "Adorei! Me senti ótima, a equipe foi maravilhosa",
  "messageId": "TEST-DIANA-002"
}
```

**Esperado:** `nota_feedback = 5` (ou similar), `etapa = "feedback"`, mensagem transitando para orientações.

### Teste 3 — Reação adversa (escalar)

```json
{
  ...
  "texto": "Estou com muita dor e inchaço no rosto, não está passando",
  "messageId": "TEST-DIANA-003"
}
```

**Esperado:** `acao = "escalar_humano"`, mensagem empática orientando a cliente a entrar em contato com a clínica.

### Teste 4 — Interesse em reagendamento

```json
{
  ...
  "texto": "Quero marcar mais sessões, adorei o resultado",
  "messageId": "TEST-DIANA-004"
}
```

**Esperado:** `acao = "passar_para_bia"`, `interesse_reagendamento = true`, Bia chamada com contexto do procedimento.

---

## Troubleshooting

| Problema | Solução |
|---|---|
| `procedimento_realizado` aparece como "procedimento" | Cliente não tem agendamento com status `confirmado` — verifique aba Agendamentos |
| Feedback não salvo | Verifique se aba `Feedback_PosVenda` existe e tem as colunas corretas |
| Diana não avança de etapa | O histórico não está sendo carregado — verifique node "Buscar Sessão Diana" |
| Paralelo não espera ambos os Sheets | O Code node "Montar Prompt Diana" precisa referenciar ambos os nodes pelo nome |

---

## Próximos passos

- [ ] Adicionar intent `POS_PROCEDIMENTO` no routing do Workflow 01
- [ ] Criar trigger automático: disparar Diana 2h após procedimento (Cron ou webhook da agenda)
- [ ] Dashboard de NPS com dados da aba `Feedback_PosVenda`
