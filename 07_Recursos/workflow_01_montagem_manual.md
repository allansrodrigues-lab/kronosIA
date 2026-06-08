# Guia de Montagem Manual — Workflow 01 Orquestrador WhatsApp

> Siga esta ordem exata. Cada seção mostra onde clicar, o que digitar e o código a colar.

---

## Antes de começar

1. Abra o n8n e vá no workflow **"teste clinic edit"** (ou crie um novo)
2. Clique no nome no topo e renomeie para: **`01-orquestrador-whatsapp`**
3. Salve com **Ctrl+S**

---

## PARTE 1 — Adicionar os nodes

---

### Node 1 — Webhook WhatsApp

**Como adicionar:**
- Clique no `+` no centro do canvas
- Digite: `webhook`
- Selecione **Webhook**

**O que configurar (painel direito):**

| Campo | Valor |
|---|---|
| HTTP Method | `POST` |
| Path | `whatsapp` |
| Respond | **Immediately** |

**Renomear o node:**
- Clique duas vezes no título do node
- Digite: `Webhook WhatsApp`

---

### Node 2 — Normalizar Payload

**Como adicionar:**
- Clique no `+` à direita do node anterior
- Digite: `code`
- Selecione **Code**

**O que configurar:**
- Language: `JavaScript`
- Apague o código padrão e cole o código abaixo:

```javascript
const body = $input.first().json.body ?? $input.first().json;

if (body.data?.key?.fromMe === true) return [];
if (body.event !== 'messages.upsert') return [];

const data = body.data;
const remoteJid = data.key?.remoteJid;
if (!remoteJid) return [];
if (remoteJid.endsWith('@g.us')) return [];

const telefone = remoteJid.replace('@s.whatsapp.net', '');

let texto = '';
let tipoMensagem = data.messageType ?? 'unknown';

if (data.message?.conversation) {
  texto = data.message.conversation;
} else if (data.message?.extendedTextMessage?.text) {
  texto = data.message.extendedTextMessage.text;
} else if (data.message?.imageMessage?.caption) {
  texto = data.message.imageMessage.caption;
  tipoMensagem = 'imagem';
} else if (data.message?.audioMessage) {
  tipoMensagem = 'audio';
  texto = '[áudio]';
} else {
  return [];
}

if (!texto.trim()) return [];

return [{
  json: {
    telefone,
    nome: data.pushName ?? 'Cliente',
    texto: texto.trim(),
    tipoMensagem,
    messageId: data.key?.id ?? '',
    timestamp: data.messageTimestamp ?? Math.floor(Date.now() / 1000),
    instancia: body.instance ?? 'clinica',
    remoteJid
  }
}];
```

**Renomear:** `Normalizar Payload`

---

### Node 3 — Montar Prompt Haiku

**Como adicionar:**
- Clique no `+` à direita do node anterior
- Digite: `code` → selecione **Code**

**Cole o código:**

```javascript
const { telefone, nome, texto, tipoMensagem, remoteJid, instancia, timestamp, messageId } = $input.first().json;

const systemPrompt = `Você é Aurora, recepcionista virtual de uma clínica de estética.

Classifique a intenção da mensagem do cliente e gere uma resposta curta de transição.

Retorne APENAS um JSON válido neste formato exato:
{"intent": "INTENT", "confidence": 0.0, "resposta": "Frase de transição"}

INTENÇÕES DISPONÍVEIS:
- AGENDAR: marcar, desmarcar, reagendar, consultar horários/agenda
- DUVIDA_PROCEDIMENTO: dúvidas sobre tratamentos, procedimentos, cuidados, indicações
- DUVIDA_PRECO: valores, preços, promoções, pacotes, formas de pagamento
- POS_PROCEDIMENTO: retorno pós-atendimento, efeitos, resultados, cuidados pós
- LEAD_NOVO: primeiro contato, quer conhecer a clínica, sem histórico
- RECLAMACAO: insatisfação, problema, crítica, urgência, pedido de reembolso
- OUTRO: cumprimento genérico, áudio, não identificado

TOM: Caloroso, profissional, máximo 2 frases curtas, máximo 1 emoji.
Use o nome "${nome}" se disponível.

Resposta de transição = o que Aurora fala ANTES de passar para o especialista.

Responda APENAS com o JSON. Nenhum texto adicional.`;

const userMessage = tipoMensagem === 'audio'
  ? '[cliente enviou áudio — use intent OUTRO e peça para escrever]'
  : texto;

return [{
  json: {
    telefone,
    nome,
    texto,
    tipoMensagem,
    remoteJid,
    instancia,
    timestamp,
    messageId,
    anthropicBody: {
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 300,
      system: systemPrompt,
      messages: [
        { role: 'user', content: userMessage }
      ]
    }
  }
}];
```

**Renomear:** `Montar Prompt Haiku`

---

### Node 4 — Claude Haiku — Classificar

**Como adicionar:**
- Clique no `+` → digite `http request` → selecione **HTTP Request**

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
- Body Content Type: selecione **JSON**
- No campo Body, cole:

```
={{ $json.anthropicBody }}
```

**Configurar "Continue on Fail":**
- Clique no ícone de **engrenagem** (⚙️) no canto do node
- Ative **"Continue On Fail"**

**Renomear:** `Claude Haiku — Classificar`

---

### Node 5 — Parsear Intent

**Como adicionar:**
- Clique no `+` → `code` → **Code**

**Cole o código:**

```javascript
const input = $input.first().json;
const ctx = $('Montar Prompt Haiku').first().json;

if (input.error || !input.content) {
  return [{
    json: {
      telefone: ctx.telefone,
      nome: ctx.nome,
      texto: ctx.texto,
      tipoMensagem: ctx.tipoMensagem,
      remoteJid: ctx.remoteJid,
      instancia: ctx.instancia,
      timestamp: ctx.timestamp,
      messageId: ctx.messageId,
      intent: 'OUTRO',
      confidence: 0,
      resposta: `Oi, ${ctx.nome}! Estou com uma instabilidade agora. Pode me repetir em instantes? 😊`,
      haiku_raw: JSON.stringify(input.error ?? 'sem resposta da API')
    }
  }];
}

const rawText = input.content?.[0]?.text ?? '{}';

let parsed;
try {
  const cleaned = rawText.replace(/```json?/g, '').replace(/```/g, '').trim();
  parsed = JSON.parse(cleaned);
} catch(e) {
  parsed = { intent: 'OUTRO', confidence: 0.5, resposta: 'Olá! Como posso te ajudar hoje? 😊' };
}

const validIntents = ['AGENDAR', 'DUVIDA_PROCEDIMENTO', 'DUVIDA_PRECO', 'POS_PROCEDIMENTO', 'LEAD_NOVO', 'RECLAMACAO', 'OUTRO'];
if (!validIntents.includes(parsed.intent)) {
  parsed.intent = 'OUTRO';
}

return [{
  json: {
    telefone: ctx.telefone,
    nome: ctx.nome,
    texto: ctx.texto,
    tipoMensagem: ctx.tipoMensagem,
    remoteJid: ctx.remoteJid,
    instancia: ctx.instancia,
    timestamp: ctx.timestamp,
    messageId: ctx.messageId,
    intent: parsed.intent,
    confidence: parsed.confidence ?? 0.8,
    resposta: parsed.resposta ?? 'Como posso te ajudar?',
    haiku_raw: rawText
  }
}];
```

**Renomear:** `Parsear Intent`

---

### Node 6 — É Reclamação?

**Como adicionar:**
- Clique no `+` → digite `if` → selecione **IF**

**O que configurar:**

- Clique em **"Add Condition"**
- Value 1: `={{ $json.intent }}`
- Operation: `is equal to` (ou `equals`)
- Value 2: `RECLAMACAO`

**Renomear:** `É Reclamação?`

> Este node tem **2 saídas**: `true` (lado verde/esquerdo) e `false` (lado vermelho/direito).
> Os próximos 2 nodes se conectam a saídas diferentes.

---

### Node 7 — Preparar Escalação

**Como adicionar:**
- Arraste da saída **TRUE** (verde) do node IF
- Clique no `+` que aparecer → `code` → **Code**

**Cole o código:**

```javascript
const { telefone, nome, texto, intent, resposta, remoteJid, instancia, timestamp, messageId, confidence } = $input.first().json;

const mensagemParaCliente = resposta || `${nome}, sinto muito pelo inconveniente. Nossa equipe já foi notificada e entrará em contato em breve.`;

const mensagemParaEquipe =
  '🚨 *ESCALAÇÃO — ATENDIMENTO MANUAL NECESSÁRIO*\n\n' +
  `👤 Cliente: ${nome}\n` +
  `📱 Telefone: ${telefone}\n` +
  `💬 Mensagem: "${texto}"\n` +
  `🏷️ Intent: ${intent}\n\n` +
  'Por favor, assuma o atendimento manualmente.';

return [{
  json: {
    telefone,
    nome,
    texto,
    intent,
    confidence,
    remoteJid,
    instancia,
    timestamp,
    messageId,
    mensagemParaCliente,
    mensagemParaEquipe,
    ehEscalacao: true
  }
}];
```

**Renomear:** `Preparar Escalação`

---

### Node 8 — Notificar Equipe

**Como adicionar:**
- Clique no `+` à direita do node `Preparar Escalação`
- `http request` → **HTTP Request**

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

**Body:**
- Ative **Send Body** → Body Content Type: **JSON**
- Cole:

```
={{ { number: $env.EVO_TEAM_NUMBER, text: $json.mensagemParaEquipe } }}
```

**Configurar "Continue on Fail":**
- Ícone de **engrenagem** (⚙️) → ative **"Continue On Fail"**

**Renomear:** `Notificar Equipe`

---

### Node 9 — Preparar Resposta Normal

**Como adicionar:**
- Volte ao node `É Reclamação?`
- Arraste da saída **FALSE** (vermelho)
- Clique no `+` → `code` → **Code**

**Cole o código:**

```javascript
const { telefone, nome, texto, intent, resposta, confidence, remoteJid, instancia, timestamp, messageId } = $input.first().json;

return [{
  json: {
    telefone,
    nome,
    texto,
    intent,
    confidence,
    remoteJid,
    instancia,
    timestamp,
    messageId,
    mensagemParaCliente: resposta,
    ehEscalacao: false
  }
}];
```

**Renomear:** `Preparar Resposta Normal`

---

### Node 10 — Enviar Resposta (Evolution)

**Como adicionar:**
- Clique no `+` à direita de `Notificar Equipe`
- `http request` → **HTTP Request**

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
={{ { number: $json.telefone, text: $json.mensagemParaCliente } }}
```

**Renomear:** `Enviar Resposta (Evolution)`

> Depois de criar este node, **conecte também** a saída do node `Preparar Resposta Normal`
> até este node (arraste a seta de lá até cá).

---

### Node 11 — Log no Sheets

**Como adicionar:**
- Clique no `+` à direita de `Enviar Resposta (Evolution)`
- Digite `google sheets` → selecione **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Selecione ou crie: **Google Sheets — Clinica** |
| Operation | `Append Row` |
| Document | Cole o ID da planilha ou selecione pelo Google |
| Sheet | `Log_Interacoes` |

**Mapping de colunas** — clique em **"Add Field"** para cada coluna:

| Column Name | Value |
|---|---|
| `Data` | `={{ new Date($json.timestamp * 1000).toLocaleString('pt-BR') }}` |
| `Telefone` | `={{ $json.telefone }}` |
| `Nome` | `={{ $json.nome }}` |
| `Mensagem` | `={{ $json.texto }}` |
| `Intent` | `={{ $json.intent }}` |
| `Confianca` | `={{ $json.confidence }}` |
| `Resposta` | `={{ $json.mensagemParaCliente }}` |
| `Escalacao` | `={{ $json.ehEscalacao ? 'SIM' : 'NAO' }}` |

**Renomear:** `Log no Sheets`

---

## PARTE 2 — Verificar as conexões

Após criar todos os nodes, confirme que as conexões estão assim:

```
[Webhook WhatsApp]
        ↓
[Normalizar Payload]
        ↓
[Montar Prompt Haiku]
        ↓
[Claude Haiku — Classificar]
        ↓
[Parsear Intent]
        ↓
[É Reclamação?]
    ↙ TRUE          ↘ FALSE
[Preparar Escalação]   [Preparar Resposta Normal]
        ↓                         ↓
[Notificar Equipe]                ↓
        ↓                         ↓
        └──────────┬──────────────┘
                   ↓
        [Enviar Resposta (Evolution)]
                   ↓
           [Log no Sheets]
```

**Como conectar manualmente:**
- Passe o mouse sobre um node → aparece um ponto cinza na borda direita
- Clique e arraste esse ponto até o node destino

---

## PARTE 3 — Configurar variáveis de ambiente

No n8n: **Settings** (menu lateral) → **Variables** → **Add Variable**

| Nome | Valor de exemplo |
|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` |
| `EVO_BASE_URL` | `https://evo.seudominio.com.br` |
| `EVO_API_KEY` | `sua-chave-aqui` |
| `EVO_INSTANCE` | `clinica` |
| `EVO_TEAM_NUMBER` | `5511999990000` |
| `GOOGLE_SHEETS_CRM_ID` | `ID da sua planilha` |

> O ID da planilha Google Sheets está na URL:
> `docs.google.com/spreadsheets/d/**ID_AQUI**/edit`

---

## PARTE 4 — Ativar e testar

**1. Salve o workflow** — Ctrl+S

**2. Ative o workflow** — clique no toggle no canto superior direito (deve ficar verde)

**3. Copie a URL do webhook:**
- Clique no node `Webhook WhatsApp`
- Copie a URL que aparece (ex: `https://seu-n8n.com/webhook/whatsapp`)

**4. Teste com curl** (no terminal do seu computador):

```bash
curl -X POST https://SEU-N8N/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "TEST001"
      },
      "pushName": "Maria Teste",
      "message": { "conversation": "Quero agendar uma limpeza de pele" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

**5. Verifique a execução:**
- No n8n: menu lateral → **Executions**
- Clique na execução mais recente
- Cada node deve aparecer verde
- No node `Parsear Intent`, verifique os campos `intent` e `resposta`

---

## PARTE 5 — Checklist final antes de ligar para produção

- [ ] Todos os 11 nodes criados e renomeados
- [ ] Todos os nodes Code com o código correto colado
- [ ] Node "Claude Haiku" com **Continue on Fail** ativo
- [ ] Node "Notificar Equipe" com **Continue on Fail** ativo
- [ ] Webhook com **Respond: Immediately**
- [ ] Credencial Google Sheets configurada
- [ ] Todas as 6 variáveis de ambiente preenchidas
- [ ] Workflow ativo (toggle verde)
- [ ] Teste com curl funcionando (execução verde no histórico)
- [ ] Webhook configurado na Evolution API apontando para a URL do n8n
