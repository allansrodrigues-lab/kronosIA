# Guia de Montagem Manual — Workflow 02 Agendamento (Bia)

> Siga esta ordem exata. Cada seção mostra onde clicar, o que digitar e o código a colar.
> Para contexto técnico completo de cada node, consulte `workflow_02_agendamento_guide.md`.

---

## Antes de começar

1. Abra o n8n e crie um **novo workflow** em branco
2. Clique no nome no topo e renomeie para: **`02-agendamento-bia`**
3. Salve com **Ctrl+S**
4. Confirme que as 4 abas do Google Sheets foram criadas:
   - `Slots_Disponiveis`
   - `Sessoes_Ativas`
   - `Agendamentos`
   - `Log_Agendamentos`
   
   (Ver estrutura das colunas em `workflow_02_agendamento_guide.md` → seção "Estrutura de abas")

---

## PARTE 1 — Adicionar os nodes

---

### Node 1 — Trigger — Receber do Orquestrador

**Como adicionar:**
- Clique no `+` no canvas
- Digite: `execute workflow trigger`
- Selecione **Execute Workflow Trigger**

**Não há nada para configurar neste node.**

**Renomear:**
- Clique duas vezes no título do node
- Digite: `Trigger — Receber do Orquestrador`

---

### Node 2 — Buscar Slots Disponíveis

**Como adicionar:**
- Clique no `+` à direita do node anterior
- Digite: `google sheets` → selecione **Google Sheets**

**O que configurar (painel direito):**

| Campo | Valor |
|---|---|
| Credential | Selecione **Google Sheets — Clinica** |
| Resource | `Spreadsheet` |
| Operation | `Get Many Rows` |
| Document | Cole o ID da planilha ou clique em "By URL" e cole a URL |
| Sheet Name | `Slots_Disponiveis` |
| Return All Rows | **Ativo (toggle ON)** |

**Configurar "Continue on Fail":**
- Ícone de **engrenagem** (⚙️) → ative **"Continue On Fail"**

**Renomear:** `Buscar Slots Disponíveis`

---

### Node 3 — Buscar Sessão Bia

**Como adicionar:**
- Clique no `+` à direita do node anterior
- `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Resource | `Spreadsheet` |
| Operation | `Get Many Rows` |
| Document | ID da planilha (mesmo do node anterior) |
| Sheet Name | `Sessoes_Ativas` |
| Return All Rows | **Ativo** |

**Configurar "Continue on Fail":** ative (engrenagem ⚙️).

**Renomear:** `Buscar Sessão Bia`

---

### Node 4 — Montar Prompt Bia

**Como adicionar:**
- `+` → `code` → **Code**

**O que configurar:**
- Language: `JavaScript`
- Apague o código padrão e cole:

```javascript
const ctx = $('Trigger — Receber do Orquestrador').first().json;
const { telefone, nome, texto, remoteJid, instancia, timestamp, messageId } = ctx;

const todosSlots = $('Buscar Slots Disponíveis').all();
const hoje = new Date();
const em14dias = new Date(hoje.getTime() + 14 * 24 * 60 * 60 * 1000);

const slotsDisponiveis = todosSlots
  .filter(item => {
    if (!item.json.Data || !item.json.Hora) return false;
    const dataSlot = new Date(`${item.json.Data}T${item.json.Hora}`);
    return dataSlot >= hoje && dataSlot <= em14dias;
  })
  .slice(0, 25)
  .map(item => `ID:${item.json.ID} | ${item.json.Data} | ${item.json.Hora} | ${item.json.Profissional} | ${item.json.Procedimento_Tipo}`);

const slotsFormatados = slotsDisponiveis.length > 0
  ? slotsDisponiveis.join('\n')
  : 'Nenhum horário disponível nos próximos 14 dias.';

const todasSessoes = $('Buscar Sessão Bia').all();
const sessao = todasSessoes.find(
  s => s.json.Telefone === telefone && s.json.Agente === 'BIA' && s.json.Status === 'ativo'
)?.json ?? null;

let historico = [];
if (sessao?.Historico) {
  try { historico = JSON.parse(sessao.Historico); } catch(e) {}
}

historico.push({ role: 'user', content: texto });

const systemPrompt = `Você é Bia, especialista em agendamentos da Clínica de Estética.

Seu objetivo é conduzir o cliente até a confirmação do agendamento em no máximo 4 mensagens.

PROCEDIMENTOS DISPONÍVEIS (e duração):
- Limpeza de Pele Profunda (60 min)
- Peeling Químico (45 min)
- Botox / Toxina Botulínica (30 min)
- Drenagem Linfática (60 min)
- Criolipólise (60 min por área)
- Massagem Modeladora (50 min)
- Avaliação Inicial (30 min, gratuita)

HORÁRIOS DISPONÍVEIS (próximos 14 dias):
${slotsFormatados}

REGRAS:
1. Se o cliente não informou o procedimento → pergunte antes de mostrar horários
2. Se já sabe o procedimento → mostre EXATAMENTE 3 opções formatadas assim:
   1️⃣ [dia da semana], [DD/MM] às [HH:mm] com [Profissional]
   2️⃣ ...
   3️⃣ ...
3. Quando o cliente escolher → confirme: procedimento + data + hora + profissional e peça confirmação
4. Após "sim" → acao: criar_agendamento com dados preenchidos
5. Cancelamento: confirme antes (acao: confirmar_cancelamento); só cancela após "sim" (acao: cancelar_agendamento)
6. Sem horários disponíveis → informe e acao: escalar_humano
7. Responda SEMPRE em JSON válido, sem texto fora do JSON

FORMATO OBRIGATÓRIO (JSON):
{"mensagem": "texto para o cliente (max 280 chars)", "acao": "aguardar_resposta|criar_agendamento|cancelar_agendamento|confirmar_cancelamento|encerrar|escalar_humano", "dados": {"procedimento": null, "slot_id": null, "data_hora": null, "profissional": null}, "encerrar_sessao": false}

TOM: Objetiva e calorosa. Máximo 1 emoji por mensagem. Nome do cliente: ${nome}.`;

return [{
  json: {
    telefone, nome, texto, remoteJid, instancia, timestamp, messageId,
    historico,
    sessao_id: sessao?.ID ?? null,
    sessao_fase: sessao?.Fase ?? 'novo',
    anthropicBody: {
      model: 'claude-sonnet-5',
      max_tokens: 2048,
      system: systemPrompt,
      messages: historico
    }
  }
}];
```

**Renomear:** `Montar Prompt Bia`

---

### Node 5 — Claude Sonnet — Bia

**Como adicionar:**
- `+` → `http request` → **HTTP Request**

**O que configurar:**

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `https://api.anthropic.com/v1/messages` |

**Aba Headers — clique em "Add Header" 3 vezes:**

| Name | Value |
|---|---|
| `x-api-key` | `={{ $env.ANTHROPIC_API_KEY }}` |
| `anthropic-version` | `2023-06-01` |
| `Content-Type` | `application/json` |

**Body:**
- Ative **Send Body**
- Body Content Type: **JSON**
- Campo Body: `={{ $json.anthropicBody }}`

**Configurar "Continue on Fail":** ative (engrenagem ⚙️).

**Renomear:** `Claude Sonnet — Bia`

---

### Node 6 — Parsear Resposta Bia

**Como adicionar:**
- `+` → `code` → **Code**

**Cole o código:**

```javascript
const input = $input.first().json;
const ctx = $('Montar Prompt Bia').first().json;

if (input.error || !input.content) {
  return [{
    json: {
      ...ctx,
      mensagem: `Oi ${ctx.nome}! Tive uma instabilidade aqui. Pode repetir o que você quer fazer? 😊`,
      acao: 'aguardar_resposta',
      dados: { procedimento: null, slot_id: null, data_hora: null, profissional: null },
      encerrar_sessao: false,
      historicoAtualizado: ctx.historico,
      erro: true
    }
  }];
}

const rawText = input.content?.find(b => b.type === 'text')?.text ?? '{}';

let parsed;
try {
  const cleaned = rawText.replace(/```json?/g, '').replace(/```/g, '').trim();
  parsed = JSON.parse(cleaned);
} catch(e) {
  parsed = {
    mensagem: `Oi ${ctx.nome}! Poderia me dizer novamente o que você quer fazer?`,
    acao: 'aguardar_resposta',
    dados: {},
    encerrar_sessao: false
  };
}

const validAcoes = ['aguardar_resposta', 'criar_agendamento', 'cancelar_agendamento',
                    'confirmar_cancelamento', 'encerrar', 'escalar_humano'];
if (!validAcoes.includes(parsed.acao)) parsed.acao = 'aguardar_resposta';

const historicoAtualizado = [...ctx.historico, { role: 'assistant', content: parsed.mensagem }];

return [{
  json: {
    telefone: ctx.telefone,
    nome: ctx.nome,
    remoteJid: ctx.remoteJid,
    instancia: ctx.instancia,
    timestamp: ctx.timestamp,
    messageId: ctx.messageId,
    sessao_id: ctx.sessao_id,
    sessao_fase: ctx.sessao_fase,
    mensagem: parsed.mensagem,
    acao: parsed.acao,
    dados: parsed.dados ?? {},
    encerrar_sessao: parsed.encerrar_sessao ?? false,
    historicoAtualizado,
    bia_raw: rawText
  }
}];
```

**Renomear:** `Parsear Resposta Bia`

---

### Node 7 — Switch por Ação

**Como adicionar:**
- `+` → `switch` → **Switch**

**O que configurar:**
- Mode: `Rules`
- Value (campo de input): `={{ $json.acao }}`

**Adicione 3 regras** (botão "Add Rule"):

| # | Condition | Value | Output Label |
|---|---|---|---|
| 1 | equals | `criar_agendamento` | Criar Agendamento |
| 2 | equals | `cancelar_agendamento` | Cancelar |
| 3 | equals | `escalar_humano` | Escalar Humano |

- Ative **"Fallback Output"** (ou "Has Fallback") para capturar os demais casos
- O Fallback será o output 4 (aguardar/encerrar)

**Renomear:** `Switch por Ação`

---

### Node 8 — Preparar Dados Reserva
*(branch: saída 1 "Criar Agendamento")*

**Como adicionar:**
- Passe o mouse sobre a **saída 1 (Criar Agendamento)** do Switch
- Clique no `+` que aparecer → `code` → **Code**

**Cole o código:**

```javascript
const { telefone, nome, remoteJid, instancia, timestamp, dados, mensagem,
        historicoAtualizado, encerrar_sessao } = $input.first().json;

const instrucoes = {
  'Limpeza de Pele Profunda': '• Não use ácidos 5 dias antes\n• Venha sem maquiagem\n• Evite sol 24h antes',
  'Peeling Químico': '• Não use ácidos 7 dias antes\n• Sem sol 48h antes\n• Venha com pele hidratada',
  'Botox / Toxina Botulínica': '• Evite álcool 24h antes\n• Não tome AAS/anti-inflamatório 7 dias antes',
  'Drenagem Linfática': '• Venha com roupa confortável\n• Beba bastante água no dia',
  'Criolipólise': '• Sem atividade física intensa no dia\n• Venha com roupa larga',
  'Massagem Modeladora': '• Beba bastante água antes\n• Venha com roupa confortável',
  'Avaliação Inicial': '• Venha com a pele limpa se possível\n• Pode trazer fotos de resultados desejados'
};

const instrucao = instrucoes[dados.procedimento] ?? '• Siga as orientações da profissional no dia';
const mensagemFinal = `${mensagem}\n\n📋 *Antes do procedimento:*\n${instrucao}\n\nVou te lembrar 24h antes! ✨`;
const agendamentoId = `AGD-${Date.now()}`;

return [{
  json: {
    telefone, nome, remoteJid, instancia, timestamp,
    mensagem: mensagemFinal,
    acao: 'criar_agendamento',
    dados, historicoAtualizado,
    encerrar_sessao: true,
    agendamentoId,
    slot_id: dados.slot_id,
    procedimento: dados.procedimento,
    data_hora: dados.data_hora,
    profissional: dados.profissional
  }
}];
```

**Renomear:** `Preparar Dados Reserva`

---

### Node 9 — Reservar Slot
*(branch: após "Preparar Dados Reserva")*

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Update Row` |
| Document | ID da planilha |
| Sheet | `Slots_Disponiveis` |
| Lookup Column | `ID` |
| Lookup Value | `={{ $json.slot_id }}` |

**Campos a atualizar (clique em "Add Field" 3 vezes):**

| Column | Value |
|---|---|
| `Status` | `reservado` |
| `Reservado_Para` | `={{ $json.telefone }}` |
| `Agendamento_ID` | `={{ $json.agendamentoId }}` |

**"Continue on Fail":** ative.

**Renomear:** `Reservar Slot`

---

### Node 10 — Salvar no CRM
*(branch: após "Reservar Slot")*

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Append Row` |
| Document | ID da planilha |
| Sheet | `Agendamentos` |

**Campos (clique em "Add Field" para cada):**

| Column | Value |
|---|---|
| `ID` | `={{ $json.agendamentoId }}` |
| `Telefone` | `={{ $json.telefone }}` |
| `Nome` | `={{ $json.nome }}` |
| `Procedimento` | `={{ $json.procedimento }}` |
| `Data` | `={{ $json.data_hora?.split(' ')[0] }}` |
| `Hora` | `={{ $json.data_hora?.split(' ')[1] }}` |
| `Profissional` | `={{ $json.profissional }}` |
| `Status` | `confirmado` |
| `Criado_Em` | `={{ new Date().toLocaleString('pt-BR') }}` |

**Renomear:** `Salvar no CRM`

---

### Node 11 — Cancelar no CRM
*(branch: saída 2 "Cancelar" do Switch)*

**Como adicionar:**
- Passe o mouse sobre a **saída 2 (Cancelar)** do Switch
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Update Row` |
| Document | ID da planilha |
| Sheet | `Agendamentos` |
| Lookup Column | `Telefone` |
| Lookup Value | `={{ $json.telefone }}` |

**Campos:**

| Column | Value |
|---|---|
| `Status` | `cancelado` |

**"Continue on Fail":** ative.

**Renomear:** `Cancelar no CRM`

---

### Node 12 — Liberar Slot
*(branch: após "Cancelar no CRM")*

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Update Row` |
| Document | ID da planilha |
| Sheet | `Slots_Disponiveis` |
| Lookup Column | `Reservado_Para` |
| Lookup Value | `={{ $json.telefone }}` |

**Campos:**

| Column | Value |
|---|---|
| `Status` | `disponivel` |
| `Reservado_Para` | ` ` (um espaço) |
| `Agendamento_ID` | ` ` (um espaço) |

**Renomear:** `Liberar Slot`

---

### Node 13 — Preparar Sessão (Code)
*(Ponto de convergência de todos os branches)*

**Como adicionar:**
- Crie o node em posição central, abaixo de todos os branches
- `+` → `code` → **Code**

**Cole o código:**

```javascript
const { telefone, nome, acao, dados, historicoAtualizado,
        encerrar_sessao, sessao_id, timestamp } = $input.first().json;

const agora = new Date().toLocaleString('pt-BR');
const statusSessao = (encerrar_sessao || acao === 'encerrar') ? 'encerrado' : 'ativo';
const historicoLimitado = (historicoAtualizado ?? []).slice(-20);

return [{
  json: {
    telefone, nome, timestamp, acao, dados,
    mensagem: $input.first().json.mensagem,
    remoteJid: $input.first().json.remoteJid,
    instancia: $input.first().json.instancia,
    sessao_id,
    sessao_update: {
      Agente: 'BIA',
      Fase: acao,
      Historico: JSON.stringify(historicoLimitado),
      Dado_Temp: JSON.stringify(dados ?? {}),
      Atualizado_Em: agora,
      Status: statusSessao
    }
  }
}];
```

**Renomear:** `Preparar Sessão`

**Conectar todos os branches a este node:**
- Arraste uma seta de `Salvar no CRM` → `Preparar Sessão`
- Arraste uma seta de `Liberar Slot` → `Preparar Sessão`
- Arraste a saída 3 (Escalar Humano) do Switch → `Preparar Sessão`
- Arraste a saída 4 (Fallback) do Switch → `Preparar Sessão`

---

### Node 14 — Enviar Mensagem WhatsApp

**Como adicionar:**
- `+` à direita de `Preparar Sessão` → `http request` → **HTTP Request**

**O que configurar:**

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `={{ $env.EVO_BASE_URL }}/message/sendText/{{ $env.EVO_INSTANCE }}` |

**Headers (2 headers):**

| Name | Value |
|---|---|
| `apikey` | `={{ $env.EVO_API_KEY }}` |
| `Content-Type` | `application/json` |

**Body → JSON:**
```
={{ { number: $json.telefone, text: $json.mensagem } }}
```

**Renomear:** `Enviar Mensagem WhatsApp`

---

### Node 15 — Atualizar Sessão Bia

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Append Row` |
| Document | ID da planilha |
| Sheet | `Sessoes_Ativas` |

**Campos:**

| Column | Value |
|---|---|
| `Telefone` | `={{ $json.telefone }}` |
| `Agente` | `BIA` |
| `Fase` | `={{ $json.sessao_update.Fase }}` |
| `Historico` | `={{ $json.sessao_update.Historico }}` |
| `Dado_Temp` | `={{ $json.sessao_update.Dado_Temp }}` |
| `Criado_Em` | `={{ $json.sessao_update.Atualizado_Em }}` |
| `Atualizado_Em` | `={{ $json.sessao_update.Atualizado_Em }}` |
| `Status` | `={{ $json.sessao_update.Status }}` |

> Usamos Append em vez de Upsert para simplicidade. O Code node do turno seguinte
> sempre filtra a sessão mais recente via `Atualizado_Em`.

**Renomear:** `Atualizar Sessão Bia`

---

### Node 16 — Log Interação Bia

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Append Row` |
| Document | ID da planilha |
| Sheet | `Log_Agendamentos` |

**Campos:**

| Column | Value |
|---|---|
| `Data_Hora` | `={{ new Date($json.timestamp * 1000).toLocaleString('pt-BR') }}` |
| `Telefone` | `={{ $json.telefone }}` |
| `Nome` | `={{ $json.nome }}` |
| `Acao` | `={{ $json.acao }}` |
| `Procedimento` | `={{ $json.dados?.procedimento ?? '' }}` |
| `Detalhes` | `={{ ($json.dados?.slot_id ?? '') + ' ' + ($json.dados?.data_hora ?? '') }}` |

**Renomear:** `Log Interação Bia`

---

## PARTE 2 — Verificar as conexões

Após criar todos os nodes, confirme:

```
[Trigger — Receber do Orquestrador]
           ↓
[Buscar Slots Disponíveis]
           ↓
[Buscar Sessão Bia]
           ↓
[Montar Prompt Bia]
           ↓
[Claude Sonnet — Bia]
           ↓
[Parsear Resposta Bia]
           ↓
[Switch por Ação]
    ↓(1)           ↓(2)         ↓(3)       ↓(4)
[Preparar      [Cancelar    (Escalar)   (Aguardar/
 Dados Reserva] no CRM]                  Encerrar)
    ↓               ↓            ↓            ↓
[Reservar Slot] [Liberar Slot]  ↓            ↓
    ↓               ↓            ↓            ↓
[Salvar no CRM]    ↓            ↓            ↓
    ↓               └────────────┴────────────┘
    └──────────────────────────────────────────→ [Preparar Sessão]
                                                         ↓
                                              [Enviar Mensagem WhatsApp]
                                                         ↓
                                              [Atualizar Sessão Bia]
                                                         ↓
                                              [Log Interação Bia]
```

---

## PARTE 3 — Ativar e testar

**1. Salve** — Ctrl+S

**2. Ative** — toggle verde no canto superior direito

**3. Copie o ID do workflow:**
- No n8n → clique no nome do workflow
- A URL mostra o ID: `https://seu-n8n.com/workflow/ID_AQUI`
- Anote este ID — será necessário para configurar o Workflow 01

**4. Teste manual (Execute Workflow Trigger):**
- No n8n → clique em **"Test workflow"**
- No primeiro node, clique em **"Execute Workflow Trigger"**
- Cole este JSON de teste:

```json
{
  "telefone": "5511999999999",
  "nome": "Maria Teste",
  "texto": "Quero agendar uma limpeza de pele",
  "remoteJid": "5511999999999@s.whatsapp.net",
  "instancia": "clinica",
  "timestamp": 1748908800,
  "messageId": "TEST-BIA-001",
  "intent": "AGENDAR"
}
```

**5. Resultado esperado:**
- Todos os nodes verdes
- Node "Parsear Resposta Bia": `acao = "aguardar_resposta"`, mensagem com 3 opções de horário
- Aba `Sessoes_Ativas` com nova linha Status = `ativo`
- Aba `Log_Agendamentos` com nova linha

---

## PARTE 4 — Checklist final

- [ ] 16 nodes criados e renomeados
- [ ] Todos os Code nodes com código correto colado
- [ ] "Continue On Fail" ativo nos nodes: Slots, Sessão, Claude Sonnet, Reservar Slot, Cancelar CRM
- [ ] Credencial Google Sheets configurada em todos os 7 Sheets nodes
- [ ] Todas as conexões entre branches e Preparar Sessão estão corretas
- [ ] Workflow ativo (toggle verde)
- [ ] Teste manual executado com sucesso (todos os nodes verdes)
- [ ] ID do workflow anotado para configurar no Workflow 01
- [ ] 4 abas do Sheets criadas com pelo menos 1 slot disponível
