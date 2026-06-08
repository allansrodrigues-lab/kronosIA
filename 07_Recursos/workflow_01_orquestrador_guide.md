# Workflow 01 — Orquestrador WhatsApp (Guia de Configuração)

> Este guia detalha cada node do workflow principal. Para importar direto no n8n,
> use o arquivo `workflow_01_orquestrador.json` na mesma pasta.

---

## Visão geral do fluxo

```
Webhook (Evolution)
  └─ Normalizar Payload
       └─ Montar Prompt (Haiku)
            └─ Claude Haiku — Classificar Intent  ← continueOnFail ativo
                 └─ Parsear Intent  ← trata erro de API com fallback
                      └─ É Reclamação?
                           ├─ SIM → Preparar Escalação → Notificar Equipe → Enviar Mensagem → Log Sheets
                           └─ NÃO → Preparar Resposta                    → Enviar Mensagem → Log Sheets
```

**Agentes especialistas (AGENDAR, DUVIDA, etc.)** serão adicionados como sub-workflows
nas próximas etapas. Por enquanto, Aurora responde com a mensagem de transição.

---

## Pré-requisitos

| Item | Onde configurar |
|---|---|
| Evolution API rodando + instância pareada | `setup_evolution_api_n8n.md` |
| `ANTHROPIC_API_KEY` | n8n → Settings → Variables |
| `EVO_BASE_URL`, `EVO_API_KEY`, `EVO_INSTANCE` | n8n → Settings → Variables |
| `GOOGLE_SHEETS_CRM_ID` | n8n → Settings → Variables |
| Credencial Google Sheets (OAuth2) | n8n → Settings → Credentials |

---

## Node 1 — Webhook WhatsApp

| Campo | Valor |
|---|---|
| HTTP Method | `POST` |
| Path | `whatsapp` |
| Authentication | None |
| Response Mode | **Immediately** (responde 200 na hora) |

URL gerada: `https://SEU-N8N/webhook/whatsapp`

> Cole esta URL no webhook da Evolution API (passo 3 do setup).

---

## Node 2 — Normalizar Payload (Code)

```javascript
const body = $input.first().json.body ?? $input.first().json;

// Ignora mensagens enviadas pelo próprio bot
if (body.data?.key?.fromMe === true) return [];

// Ignora eventos que não sejam nova mensagem
if (body.event !== 'messages.upsert') return [];

const data = body.data;
const remoteJid = data.key?.remoteJid;
if (!remoteJid) return [];

// Ignora grupos
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

---

## Node 3 — Montar Prompt Haiku (Code)

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

EXEMPLOS DE RESPOSTA:
- AGENDAR: "Que ótimo, ${nome}! Já vou abrir a agenda pra você. 📅"
- DUVIDA_PROCEDIMENTO: "Oi ${nome}! Vou te conectar com nossa especialista pra explicar tudo."
- DUVIDA_PRECO: "Claro, ${nome}! Deixa eu te passar as informações sobre valores."
- POS_PROCEDIMENTO: "Oi ${nome}, que bom te ver por aqui! Vou chamar a Diana pra te ajudar."
- LEAD_NOVO: "Seja bem-vinda, ${nome}! Fico feliz em apresentar nossa clínica pra você. ✨"
- RECLAMACAO: "${nome}, sinto muito pelo inconveniente. Já estou acionando nossa equipe."
- OUTRO (áudio): "Oi ${nome}! Para te ajudar melhor, você pode escrever sua mensagem? 😊"

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
      model: "claude-haiku-4-5-20251001",
      max_tokens: 300,
      system: systemPrompt,
      messages: [
        { role: "user", content: userMessage }
      ]
    }
  }
}];
```

---

## Node 4 — Claude Haiku — Classificar (HTTP Request)

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `https://api.anthropic.com/v1/messages` |
| Authentication | None (usaremos header manual) |

**Headers:**

| Name | Value |
|---|---|
| `x-api-key` | `={{ $env.ANTHROPIC_API_KEY }}` |
| `anthropic-version` | `2023-06-01` |
| `Content-Type` | `application/json` |

**Body:** Selecione **JSON/RAW** e cole:
```
={{ JSON.stringify($json.anthropicBody) }}
```

---

## Node 5 — Parsear Intent (Code)

```javascript
const input = $input.first().json;

// Resposta do Anthropic: input.content[0].text
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

// Recupera os campos do node anterior pelo nome
const ctx = $('Montar Prompt Haiku').first().json;

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
  }
}];
```

> **Atenção:** `$('Montar Prompt Haiku')` referencia o node pelo nome exato.
> Se você renomear o node, atualize esta linha.

---

## Node 6 — É Reclamação? (IF)

| Campo | Valor |
|---|---|
| Condition | `{{ $json.intent }}` |
| Operation | `equals` |
| Value | `RECLAMACAO` |

- **True branch** → Preparar Escalação
- **False branch** → Preparar Resposta Normal

---

## Node 7a — Preparar Escalação (Code) — branch TRUE

```javascript
const { telefone, nome, texto, intent, resposta, remoteJid, instancia, timestamp } = $input.first().json;

const mensagemParaCliente = resposta || `${nome}, sinto muito pelo inconveniente. Nossa equipe já foi notificada e entrará em contato em breve.`;

const mensagemParaEquipe =
  `🚨 *ESCALAÇÃO — ATENDIMENTO MANUAL NECESSÁRIO*\n\n` +
  `👤 Cliente: ${nome}\n` +
  `📱 Telefone: ${telefone}\n` +
  `💬 Mensagem: "${texto}"\n` +
  `🏷️ Intent: ${intent}\n\n` +
  `Por favor, assuma o atendimento manualmente.`;

return [{
  json: {
    telefone,
    nome,
    texto,
    intent,
    remoteJid,
    instancia,
    timestamp,
    mensagemParaCliente,
    mensagemParaEquipe,
    ehEscalacao: true
  }
}];
```

---

## Node 7b — Preparar Resposta Normal (Code) — branch FALSE

```javascript
const { telefone, nome, texto, intent, resposta, remoteJid, instancia, timestamp } = $input.first().json;

return [{
  json: {
    telefone,
    nome,
    texto,
    intent,
    remoteJid,
    instancia,
    timestamp,
    mensagemParaCliente: resposta,
    ehEscalacao: false
  }
}];
```

---

## Node 8 — Notificar Equipe (HTTP Request — Evolution API) — branch RECLAMACAO

> **Este node só existe no caminho de escalação.** Envia `mensagemParaEquipe` para o
> número/grupo da equipe antes de responder ao cliente.
> `onError: continueRegularOutput` — se falhar, o cliente ainda recebe a resposta.

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `={{ $env.EVO_BASE_URL }}/message/sendText/{{ $env.EVO_INSTANCE }}` |

**Headers:** (mesmos do Node 9)

**Body (JSON/RAW):**
```json
{
  "number": "={{ $env.EVO_TEAM_NUMBER }}",
  "text": "={{ $json.mensagemParaEquipe }}"
}
```

> Habilite **"Continue on Fail"** neste node nas configurações do node (ícone de engrenagem).

---

## Node 9 — Enviar Mensagem (HTTP Request — Evolution API)

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
```json
{
  "number": "={{ $json.telefone }}",
  "text": "={{ $json.mensagemParaCliente }}"
}
```

---

## Node 10 — Log no Sheets (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Append Row` |
| Document | ID da planilha (var: `GOOGLE_SHEETS_CRM_ID`) |
| Sheet | `Log_Interacoes` |

**Colunas mapeadas:**

| Coluna da Planilha | Expressão n8n |
|---|---|
| Data | `={{ new Date($json.timestamp * 1000).toLocaleString('pt-BR') }}` |
| Telefone | `={{ $json.telefone }}` |
| Nome | `={{ $json.nome }}` |
| Mensagem | `={{ $json.texto }}` |
| Intent | `={{ $json.intent }}` |
| Resposta | `={{ $json.mensagemParaCliente }}` |
| Escalacao | `={{ $json.ehEscalacao ? 'SIM' : 'NAO' }}` |

> Crie a aba `Log_Interacoes` na sua planilha CRM com essas colunas antes de ativar.

---

## Variáveis de Ambiente no n8n

Em **Settings → Variables**, adicione:

```
ANTHROPIC_API_KEY    = sk-ant-...
EVO_BASE_URL         = https://evo.clinicacliente.com.br
EVO_API_KEY          = sua-chave-da-evolution
EVO_INSTANCE         = clinica
EVO_TEAM_NUMBER      = 5511999990000   ← número ou JID do grupo da equipe (para escalações)
GOOGLE_SHEETS_CRM_ID = 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms
```

> `EVO_TEAM_NUMBER`: pode ser o número pessoal do responsável (`5511999990000`) ou o JID
> de um grupo WhatsApp da equipe (`120363xxxxxxx@g.us`). O JID do grupo você obtém
> consultando `GET /group/fetchAllGroups/clinica` na Evolution API.

---

## Como testar

### 1. Testar o webhook (sem WhatsApp)

```bash
curl -X POST https://SEU-N8N/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica",
    "data": {
      "key": { "remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false, "id": "TEST001" },
      "pushName": "Maria Teste",
      "message": { "conversation": "Quero agendar uma limpeza de pele" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

No n8n → **Executions** → deve aparecer com:
- `intent: "DUVIDA_PROCEDIMENTO"` ou `"AGENDAR"`
- `resposta`: frase de transição gerada pelo Haiku

### 2. Testar com mensagens reais

Após ativar o workflow, envie mensagens para o número WhatsApp e verifique as execuções no n8n.

---

## Troubleshooting

| Problema | Solução |
|---|---|
| Node recebe mensagens do próprio bot | Verifique o filtro `fromMe` no Node 2 |
| Haiku retorna texto fora do JSON | O Node 5 tem fallback — verifique o log em `haiku_raw` |
| Evolution API retorna 401 | Verifique `EVO_API_KEY` e se a instância está conectada |
| Google Sheets dá erro | Verifique o ID da planilha e se a aba `Log_Interacoes` existe |
| n8n não executa após webhook | Confirme que o workflow está **ativo** (toggle verde) |

---

## Próximos passos

- [ ] Adicionar sub-workflow `02-agente-agendamento` (Bia) para branch AGENDAR
- [ ] Adicionar sub-workflow `03-agente-atendimento` (Clara) para DUVIDA_*
- [ ] Integrar Redis para memória de conversa entre sessões
- [ ] Adicionar notificação (Telegram/email) na branch de RECLAMACAO
- [ ] Buscar contato no Sheets antes do classificador (para personalizar com histórico)
