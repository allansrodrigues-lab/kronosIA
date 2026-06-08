# Workflow 02 — Agente de Agendamento "Bia" (Guia de Configuração)

> Sub-workflow chamado pelo Orquestrador quando `intent = AGENDAR`.
> Bia conduz o cliente da primeira mensagem até a confirmação do horário.
> Para importar no n8n, use `workflow_02_agendamento.json` na mesma pasta.

---

## Visão geral do fluxo

```
[Trigger — Receber do Orquestrador]
         ↓
[Buscar Slots Disponíveis]     ← Sheets: tab Slots_Disponiveis
         ↓
[Buscar Sessão Bia]            ← Sheets: tab Sessoes_Ativas (filtra em código)
         ↓
[Montar Prompt Bia]            ← Code: monta prompt + contexto + histórico
         ↓
[Claude Sonnet — Bia]          ← HTTP: Anthropic API (temperature 0.3)
         ↓
[Parsear Resposta Bia]         ← Code: extrai mensagem + acao + dados
         ↓
[Switch por Ação]
   ├── criar_agendamento
   │     ↓
   │   [Preparar Dados Reserva]   ← Code: calcula instruções pré-procedimento
   │     ↓
   │   [Reservar Slot]            ← Sheets: atualiza Slots_Disponiveis → 'reservado'
   │     ↓
   │   [Salvar no CRM]            ← Sheets: append em Agendamentos
   │
   ├── cancelar_agendamento
   │     ↓
   │   [Cancelar no CRM]          ← Sheets: atualiza Agendamentos → 'cancelado'
   │     ↓
   │   [Liberar Slot]             ← Sheets: atualiza Slots_Disponiveis → 'disponivel'
   │
   └── aguardar / encerrar / escalar_humano  ← passa direto
         ↓ (todos os ramos convergem)
[Enviar Mensagem WhatsApp]     ← HTTP: Evolution API
         ↓
[Atualizar Sessão Bia]         ← Sheets: upsert em Sessoes_Ativas
         ↓
[Log Interação Bia]            ← Sheets: append em Log_Agendamentos
```

**Total: 14 nodes**

---

## Estrutura de abas no Google Sheets (CRM)

Crie estas abas na mesma planilha do Workflow 01 (`GOOGLE_SHEETS_CRM_ID`).

### Aba: `Slots_Disponiveis`

| ID | Data | Hora | Profissional | Procedimento_Tipo | Status | Reservado_Para | Agendamento_ID |
|---|---|---|---|---|---|---|---|
| S001 | 2026-06-05 | 14:00 | Dra. Marina | Limpeza de Pele Profunda | disponivel | | |
| S002 | 2026-06-05 | 16:00 | Dra. Marina | Peeling Químico | disponivel | | |

> - **Status:** `disponivel` ou `reservado`
> - **Reservado_Para:** telefone do cliente quando reservado
> - **Agendamento_ID:** ID do registro em Agendamentos quando reservado

### Aba: `Sessoes_Ativas`

| ID | Telefone | Agente | Fase | Historico | Dado_Temp | Criado_Em | Atualizado_Em | Status |
|---|---|---|---|---|---|---|---|---|
| SES001 | 5511999990000 | BIA | aguardando_resposta | [...JSON...] | {...JSON...} | 2026-06-03 10:00 | 2026-06-03 10:02 | ativo |

> - **Historico:** JSON array com `[{role, content}]` — histórico da conversa
> - **Dado_Temp:** JSON com dados acumulados `{procedimento, slot_id, data_hora, profissional}`
> - **Status:** `ativo` ou `encerrado`

### Aba: `Agendamentos`

| ID | Telefone | Nome | Procedimento | Data | Hora | Profissional | Status | Criado_Em | Observacoes |
|---|---|---|---|---|---|---|---|---|---|
| AGD-001 | 5511999990000 | Maria | Limpeza de Pele | 2026-06-05 | 14:00 | Dra. Marina | confirmado | | |

> - **Status:** `confirmado`, `cancelado`, `remarcado`, `no_show`

### Aba: `Log_Agendamentos`

| Data_Hora | Telefone | Nome | Acao | Procedimento | Detalhes |
|---|---|---|---|---|---|
| 03/06/2026 10:02 | 5511999990000 | Maria | criar_agendamento | Limpeza de Pele | Slot S001, Dra. Marina |

---

## Pré-requisitos

| Item | Onde configurar |
|---|---|
| Workflow 01 — Orquestrador configurado | `workflow_01_orquestrador_guide.md` |
| Abas do Sheets criadas (acima) | Google Sheets |
| `ANTHROPIC_API_KEY` | n8n → Settings → Variables |
| `EVO_BASE_URL`, `EVO_API_KEY`, `EVO_INSTANCE` | n8n → Settings → Variables |
| `GOOGLE_SHEETS_CRM_ID` | n8n → Settings → Variables |
| Credencial Google Sheets (OAuth2) | n8n → Settings → Credentials |

---

## Node 1 — Trigger — Receber do Orquestrador

**Tipo:** Execute Workflow Trigger

Este node recebe os dados passados pelo Workflow 01 via node "Execute Workflow".

**Dados recebidos (input):**

| Campo | Descrição |
|---|---|
| `telefone` | Número do cliente |
| `nome` | Nome do cliente |
| `texto` | Mensagem atual do cliente |
| `remoteJid` | JID completo para envio |
| `instancia` | Nome da instância Evolution |
| `timestamp` | Timestamp Unix da mensagem |
| `messageId` | ID da mensagem WhatsApp |
| `intent` | Sempre `AGENDAR` quando vindo do Orquestrador |

> Não é necessário configurar nada neste node além de renomear.

---

## Node 2 — Buscar Slots Disponíveis (Google Sheets)

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | **Get Many Rows** |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Slots_Disponiveis` |
| Filters | Status → equals → `disponivel` |
| Return All Rows | Ativo |

> Se não conseguir configurar o filtro na UI, deixe sem filtro — o Code node filtra por data.

---

## Node 3 — Buscar Sessão Bia (Google Sheets)

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | **Get Many Rows** |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Sessoes_Ativas` |
| Return All Rows | Ativo |

> Retorna todas as sessões — o Code node filtra pelo telefone e agente `BIA`.
> Configure **"Continue On Fail"** ativo (engrenagem ⚙️ do node).

---

## Node 4 — Montar Prompt Bia (Code)

```javascript
// Contexto do trigger original
const ctx = $('Trigger — Receber do Orquestrador').first().json;
const { telefone, nome, texto, remoteJid, instancia, timestamp, messageId } = ctx;

// Slots disponíveis (do node anterior via referência)
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

// Sessão ativa para este telefone
const todasSessoes = $('Buscar Sessão Bia').all();
const sessao = todasSessoes.find(
  s => s.json.Telefone === telefone && s.json.Agente === 'BIA' && s.json.Status === 'ativo'
)?.json ?? null;

// Histórico da conversa
let historico = [];
if (sessao?.Historico) {
  try { historico = JSON.parse(sessao.Historico); } catch(e) {}
}

// Adiciona mensagem atual ao histórico
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
2. Se já sabe o procedimento → mostre EXATAMENTE 3 opções de horário compatíveis formatadas assim:
   1️⃣ [dia da semana], [DD/MM] às [HH:mm] com [Profissional]
   2️⃣ ...
   3️⃣ ...
3. Quando o cliente escolher a opção → confirme: procedimento + data + hora + profissional e pergunte confirmação
4. Após "sim" de confirmação → use acao: criar_agendamento com dados preenchidos
5. Para remarcar: cancele o atual (acao: cancelar_agendamento) e inicie novo agendamento
6. Para cancelar: confirme antes (acao: confirmar_cancelamento); só cancela após confirmação explícita (acao: cancelar_agendamento)
7. Se não houver horários disponíveis → informe e use acao: escalar_humano
8. Responda SEMPRE em JSON válido, sem nenhum texto fora do JSON

FORMATO OBRIGATÓRIO (JSON):
{
  "mensagem": "texto para enviar ao cliente (max 280 chars)",
  "acao": "aguardar_resposta|criar_agendamento|cancelar_agendamento|confirmar_cancelamento|encerrar|escalar_humano",
  "dados": {
    "procedimento": "nome exato do procedimento ou null",
    "slot_id": "ID do slot (ex: S001) ou null",
    "data_hora": "YYYY-MM-DD HH:mm ou null",
    "profissional": "nome do profissional ou null"
  },
  "encerrar_sessao": false
}

TOM: Objetiva e calorosa. Máximo 1 emoji por mensagem. Nome do cliente: ${nome}.`;

return [{
  json: {
    telefone,
    nome,
    texto,
    remoteJid,
    instancia,
    timestamp,
    messageId,
    historico,
    sessao_id: sessao?.ID ?? null,
    sessao_fase: sessao?.Fase ?? 'novo',
    anthropicBody: {
      model: 'claude-sonnet-4-6',
      max_tokens: 600,
      temperature: 0.3,
      system: systemPrompt,
      messages: historico
    }
  }
}];
```

> **Atenção:** as referências `$('Buscar Slots Disponíveis')` e `$('Buscar Sessão Bia')` devem
> corresponder exatamente aos nomes dos nodes anteriores.

---

## Node 5 — Claude Sonnet — Bia (HTTP Request)

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

## Node 6 — Parsear Resposta Bia (Code)

```javascript
const input = $input.first().json;
const ctx = $('Montar Prompt Bia').first().json;

// Fallback se a API falhou
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

const rawText = input.content?.[0]?.text ?? '{}';

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

// Adiciona resposta da Bia ao histórico
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

---

## Node 7 — Switch por Ação (Switch)

| Campo | Valor |
|---|---|
| Mode | `Rules` |
| Value | `={{ $json.acao }}` |

**Outputs (em ordem):**

| Output | Condition | Rótulo |
|---|---|---|
| Output 1 | equals `criar_agendamento` | Criar Agendamento |
| Output 2 | equals `cancelar_agendamento` | Cancelar |
| Output 3 | equals `escalar_humano` | Escalar Humano |
| Output 4 (Fallback) | — (todos os demais) | Aguardar / Encerrar |

---

## Node 8 — Preparar Dados Reserva (Code) — branch criar_agendamento

```javascript
const { telefone, nome, remoteJid, instancia, timestamp, dados, mensagem,
        historicoAtualizado, encerrar_sessao } = $input.first().json;

// Instruções pré-procedimento por tipo
const instrucoes = {
  'Limpeza de Pele Profunda':
    '• Não use ácidos 5 dias antes\n• Venha sem maquiagem\n• Evite sol 24h antes',
  'Peeling Químico':
    '• Não use ácidos 7 dias antes\n• Sem sol 48h antes\n• Venha com pele hidratada',
  'Botox / Toxina Botulínica':
    '• Evite álcool 24h antes\n• Não tome AAS/anti-inflamatório 7 dias antes',
  'Drenagem Linfática':
    '• Venha com roupa confortável\n• Beba bastante água no dia',
  'Criolipólise':
    '• Sem atividade física intensa no dia\n• Venha com roupa larga',
  'Massagem Modeladora':
    '• Beba bastante água antes\n• Venha com roupa confortável',
  'Avaliação Inicial':
    '• Venha com a pele limpa se possível\n• Pode trazer fotos de resultados desejados'
};

const instrucao = instrucoes[dados.procedimento]
  ?? '• Siga as orientações da profissional no dia';

const mensagemFinal = `${mensagem}\n\n📋 *Antes do procedimento:*\n${instrucao}\n\nVou te lembrar 24h antes! ✨`;

const agendamentoId = `AGD-${Date.now()}`;

return [{
  json: {
    telefone,
    nome,
    remoteJid,
    instancia,
    timestamp,
    mensagem: mensagemFinal,
    acao: 'criar_agendamento',
    dados,
    historicoAtualizado,
    encerrar_sessao: true,  // encerra a sessão após criação
    agendamentoId,
    slot_id: dados.slot_id,
    procedimento: dados.procedimento,
    data_hora: dados.data_hora,
    profissional: dados.profissional
  }
}];
```

---

## Node 9 — Reservar Slot (Google Sheets) — branch criar_agendamento

| Campo | Valor |
|---|---|
| Operation | **Update Row** |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Slots_Disponiveis` |
| Lookup Column | `ID` |
| Lookup Value | `={{ $json.slot_id }}` |

**Campos a atualizar:**

| Column | Value |
|---|---|
| `Status` | `reservado` |
| `Reservado_Para` | `={{ $json.telefone }}` |
| `Agendamento_ID` | `={{ $json.agendamentoId }}` |

> Configure **"Continue On Fail"** ativo — se a reserva do slot falhar, o agendamento ainda é salvo.

---

## Node 10 — Salvar no CRM (Google Sheets) — branch criar_agendamento

| Campo | Valor |
|---|---|
| Operation | **Append Row** |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Agendamentos` |

**Campos:**

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

---

## Node 11 — Cancelar no CRM (Google Sheets) — branch cancelar_agendamento

| Campo | Valor |
|---|---|
| Operation | **Update Row** |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Agendamentos` |
| Lookup Column | `Telefone` |
| Lookup Value | `={{ $json.telefone }}` |

**Campos a atualizar:**

| Column | Value |
|---|---|
| `Status` | `cancelado` |

> Atenção: este lookup atualiza o agendamento mais recente do cliente. Se precisar de precisão maior, use o `Agendamento_ID` salvo na sessão (campo `dados.agendamento_id`).

---

## Node 12 — Liberar Slot (Google Sheets) — branch cancelar_agendamento

| Campo | Valor |
|---|---|
| Operation | **Update Row** |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Slots_Disponiveis` |
| Lookup Column | `Reservado_Para` |
| Lookup Value | `={{ $json.telefone }}` |

**Campos:**

| Column | Value |
|---|---|
| `Status` | `disponivel` |
| `Reservado_Para` | ` ` (espaço — limpa o campo) |
| `Agendamento_ID` | ` ` |

---

## Node 13 — Enviar Mensagem WhatsApp (HTTP Request) — todos os branches

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `={{ $env.EVO_BASE_URL }}/message/sendText/{{ $env.EVO_INSTANCE }}` |

**Headers:**

| Name | Value |
|---|---|
| `apikey` | `={{ $env.EVO_API_KEY }}` |
| `Content-Type` | `application/json` |

**Body (JSON/RAW):**
```
={{ { number: $json.telefone, text: $json.mensagem } }}
```

> Conecte os 4 outputs do Switch a este node (todos os branches chegam aqui).
> Para o branch `escalar_humano`, a mensagem já vem de Claude como aviso ao cliente.

---

## Node 14 — Atualizar Sessão Bia (Google Sheets)

```
Lógica: se encerrar_sessao = true → Status = 'encerrado'
        se encerrar_sessao = false → Status = 'ativo', atualiza histórico
```

Use um **Code** node antes deste para preparar os dados:

```javascript
const { telefone, nome, acao, dados, historicoAtualizado,
        encerrar_sessao, sessao_id, timestamp } = $input.first().json;

const agora = new Date().toLocaleString('pt-BR');
const statusSessao = encerrar_sessao || acao === 'encerrar' ? 'encerrado' : 'ativo';

// Limita histórico a últimas 10 trocas (20 mensagens) para não estourar a célula
const historicoLimitado = historicoAtualizado.slice(-20);

return [{
  json: {
    telefone,
    sessao_id,
    sessao_update: {
      Agente: 'BIA',
      Fase: acao,
      Historico: JSON.stringify(historicoLimitado),
      Dado_Temp: JSON.stringify(dados),
      Atualizado_Em: agora,
      Status: statusSessao
    }
  }
}];
```

Depois o **Google Sheets node**:

| Campo | Valor |
|---|---|
| Operation | **Upsert Row** (ou Append + filtro manual) |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Sessoes_Ativas` |
| Lookup Column | `Telefone` + `Agente` |

> Se o n8n não tiver Upsert nativo: use **Append Row** — cada turno da conversa cria uma linha nova, e o Montar Prompt sempre filtra a mais recente via `sort` por `Atualizado_Em`.

---

## Node 15 — Log Interação Bia (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | **Append Row** |
| Document | `={{ $env.GOOGLE_SHEETS_CRM_ID }}` |
| Sheet | `Log_Agendamentos` |

**Campos:**

| Column | Value |
|---|---|
| `Data_Hora` | `={{ new Date($json.timestamp * 1000).toLocaleString('pt-BR') }}` |
| `Telefone` | `={{ $json.telefone }}` |
| `Nome` | `={{ $json.nome }}` |
| `Acao` | `={{ $json.acao }}` |
| `Procedimento` | `={{ $json.dados?.procedimento ?? '' }}` |
| `Detalhes` | `={{ $json.dados?.slot_id ?? '' }} {{ $json.dados?.data_hora ?? '' }}` |

---

## Como conectar ao Workflow 01 (Orquestrador)

Veja o arquivo `workflow_01_conexao_bia.md` para instruções detalhadas de como adicionar ao Workflow 01:
1. Node de verificação de sessão ativa
2. Node "Execute Workflow → 02-agendamento-bia" na branch AGENDAR

---

## Variáveis necessárias

As mesmas do Workflow 01 — nenhuma variável adicional necessária.

---

## Como testar

### 1. Teste direto do sub-workflow

No n8n → abra o workflow `02-agendamento-bia` → clique em **"Test workflow"** → na aba "Execute Workflow Trigger", cole:

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

### 2. Verificar resultado esperado

- Node "Parsear Resposta Bia": `acao` deve ser `aguardar_resposta`
- `mensagem` deve conter opções de horário para limpeza de pele
- Node "Enviar Mensagem WhatsApp" deve executar com sucesso
- Aba `Sessoes_Ativas` deve ter nova linha com Status `ativo`

### 3. Simular conversa completa (multi-turn)

Rode o workflow 3 vezes com mensagens em sequência:
1. `"Quero agendar uma limpeza de pele"` → Bia mostra horários
2. `"Quero o primeiro horário"` → Bia confirma detalhes
3. `"Sim, pode confirmar"` → Bia cria agendamento (aba Agendamentos ganha nova linha)

---

## Troubleshooting

| Problema | Solução |
|---|---|
| Bia não encontra sessão | Verifique se a aba `Sessoes_Ativas` existe e tem as colunas corretas |
| Bia repete a pergunta do procedimento | O histórico não está sendo salvo — verifique o node "Atualizar Sessão" |
| Erro no Reservar Slot | Verifique se o slot_id retornado por Claude existe na aba `Slots_Disponiveis` |
| Claude retorna texto fora do JSON | O node "Parsear" tem fallback — verifique `bia_raw` nos logs |
| Node "Buscar Sessão" trava o fluxo | Certifique que "Continue On Fail" está ativo no node |

---

## Próximos passos

- [ ] Adicionar sub-workflow lembrete 24h (Cron + Calendar lookup)
- [ ] Integrar Google Calendar (criar eventos reais ao confirmar)
- [ ] Adicionar tratamento de "lista de espera" quando sem slots
- [ ] Migrar histórico de Sheets → Redis para mais velocidade
