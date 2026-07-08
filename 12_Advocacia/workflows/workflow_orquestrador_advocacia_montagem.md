# Workflow: Orquestrador Advocacia — Guia de Montagem Manual

**Nome no n8n:** `[Advocacia] - Orquestrador Léa (v1.0)`
**Webhook:** `POST /webhook/whatsapp-advocacia`
**Dispara:** todo webhook da instância Evolution do escritório

---

## Fluxo completo

```
Webhook
  → Normalizar Payload
  → Filtrar (ignorar fromMe, grupos, eventos inválidos)
  → É PDF?
      → [SIM] Aviso Aguarde → Execute Workflow: kronos-analise-pdf → FIM
      → [NÃO] Buscar Sessão Ativa (Sheets)
                → Sessão Léa ativa?
                    → [SIM] Chamar Léa (com histórico) → Enviar WhatsApp → Salvar Sessão → FIM
                    → [NÃO] Montar Prompt Haiku → Claude Haiku → Parsear Intent
                                → TRIAGEM / CONSULTA_AGENDAMENTO / DUVIDA_AREA / OUTRO
                                      → Chamar Léa → Enviar WhatsApp → Salvar Sessão → FIM
                                → DOCUMENTO
                                      → Execute Workflow: kronos-analise-pdf → FIM
                                → ACOMPANHAMENTO / RECLAMACAO
                                      → Escalar Humano (WhatsApp equipe) → FIM
```

---

## Nó 1 — Webhook

- **Tipo:** Webhook
- **Path:** `whatsapp-advocacia`
- **Method:** POST
- **Authentication:** None
- **Respond:** Immediately (status 200)

---

## Nó 2 — Normalizar Payload (Code)

```javascript
const body = $input.first().json;
const data = body.data || {};
const msg  = data.message || {};

// Tipo de mensagem
const ehTexto    = !!(msg.conversation || msg.extendedTextMessage?.text);
const ehPdf      = !!(msg.documentMessage || msg.documentWithCaptionMessage);
const textoRaw   = msg.conversation || msg.extendedTextMessage?.text || '';

// Remetente
const remoteJid  = data.key?.remoteJid || '';
const fromMe     = data.key?.fromMe || false;
const ehGrupo    = remoteJid.includes('@g.us');
const nome       = data.pushName || 'Cliente';
const instancia  = body.instance || '';

// Documento (se for PDF)
const docMsg     = msg.documentMessage || msg.documentWithCaptionMessage?.documentMessage || {};
const mimetype   = docMsg.mimetype || '';
const ehPdfReal  = ehPdf && mimetype === 'application/pdf';
const msgKey     = JSON.stringify(data.key || {});

return [{
  json: {
    telefone: remoteJid.replace('@s.whatsapp.net','').replace('@g.us',''),
    remoteJid, fromMe, ehGrupo, nome, instancia,
    ehTexto, ehPdf: ehPdfReal,
    texto: textoRaw.trim(),
    msgKey,
    evento: body.event || ''
  }
}];
```

---

## Nó 3 — Filtrar Inválidos (IF)

Condição — manter apenas quando TUDO for verdade:
- `{{ $json.fromMe }}` igual a `false`
- `{{ $json.ehGrupo }}` igual a `false`
- `{{ $json.evento }}` igual a `messages.upsert`
- `{{ $json.ehTexto || $json.ehPdf }}` igual a `true`

Ramo FALSE → **NoOp** (ignorar silenciosamente)

---

## Nó 4 — É PDF? (IF)

- Condição: `{{ $json.ehPdf }}` igual a `true`
- Ramo TRUE → **Nó 5a** (aviso aguarde + sub-workflow PDF)
- Ramo FALSE → **Nó 5b** (buscar sessão)

---

## Nó 5a — Aviso Aguarde (HTTP Request)

Envia mensagem imediata enquanto processa o PDF.

- **Method:** POST
- **URL:** `{{ $env.EVO_BASE_URL }}/message/sendText/{{ $json.instancia }}`
- **Headers:** `apikey: {{ $env.EVO_API_KEY }}`
- **Body (JSON):**
```json
{
  "number": "{{ $json.remoteJid }}",
  "text": "Recebi o documento, *{{ $json.nome }}*. Aguarde um momento enquanto realizo a análise — em breve retorno com as informações relevantes."
}
```

---

## Nó 5b — Buscar Sessão Ativa (HTTP Request → Sheets)

Busca a aba `Sessoes_Advocacia` para verificar se há sessão ativa com o cliente.

- **Method:** GET
- **URL:** `https://sheets.googleapis.com/v4/spreadsheets/{{ $env.GOOGLE_SHEETS_CRM_ID }}/values/Sessoes_Advocacia!A:J`
- **Auth:** Google OAuth2

No nó seguinte (Code), filtrar linha onde `jid === remoteJid` e `status !== aguardando_advogado`.

---

## Nó 6a — Execute Workflow: kronos-analise-pdf

- **Tipo:** Execute Workflow
- **Workflow:** `kronos-analise-pdf` (ID: `VFtnXxDmZYEf1saI`)
- **Wait for completion:** true
- **Passar campos:** `remoteJid`, `instancia`, `msgKey`, `nome`

---

## Nó 6b — Sessão Ativa? (IF)

- Condição: resultado da busca no Sheets retornou linha com `status = triagem` ou `status = agendamento`
- Ramo TRUE → **Nó 7a** (chamar Léa direto com histórico)
- Ramo FALSE → **Nó 7b** (classificar intent com Haiku)

---

## Nó 7b — Montar Prompt Haiku (Code)

```javascript
const texto = $('Normalizar Payload').first().json.texto;

const prompt = `Você é um classificador de intenções para um escritório de advocacia.
Analise a mensagem e retorne APENAS um JSON com o intent.

INTENTS:
- TRIAGEM: cliente descreve problema ou caso jurídico
- CONSULTA_AGENDAMENTO: quer agendar consulta com advogado
- DUVIDA_AREA: pergunta sobre áreas de atuação do escritório
- DOCUMENTO: indica que enviou ou vai enviar PDF para análise
- ACOMPANHAMENTO: cliente existente quer saber do andamento do caso
- RECLAMACAO: reclamação sobre atendimento, prazo ou processo
- OUTRO: qualquer outra coisa

MENSAGEM: "${texto}"

Responda APENAS: {"intent": "INTENT_AQUI"}`;

return [{ json: { promptHaiku: prompt } }];
```

---

## Nó 7c — Claude Haiku (HTTP Request)

- **Method:** POST
- **URL:** `https://api.anthropic.com/v1/messages`
- **Headers:**
  - `x-api-key: {{ $env.ANTHROPIC_API_KEY }}`
  - `anthropic-version: 2023-06-01`
  - `content-type: application/json`
- **Body:**
```json
{
  "model": "claude-haiku-4-5-20251001",
  "max_tokens": 50,
  "messages": [
    { "role": "user", "content": "{{ $json.promptHaiku }}" }
  ]
}
```

---

## Nó 7d — Parsear Intent (Code)

```javascript
const raw = $input.first().json.content?.[0]?.text || '{"intent":"OUTRO"}';
let intent = 'OUTRO';
try {
  intent = JSON.parse(raw).intent;
} catch(e) {}
return [{ json: { intent } }];
```

---

## Nó 7e — Switch por Intent

- **TRIAGEM** → Chamar Léa
- **CONSULTA_AGENDAMENTO** → Chamar Léa
- **DUVIDA_AREA** → Chamar Léa
- **OUTRO** → Chamar Léa
- **DOCUMENTO** → Execute Workflow kronos-analise-pdf
- **ACOMPANHAMENTO** → Escalar Humano
- **RECLAMACAO** → Escalar Humano

---

## Nó 8 — Chamar Léa (HTTP Request)

- **Method:** POST
- **URL:** `https://api.anthropic.com/v1/messages`
- **Headers:**
  - `x-api-key: {{ $env.ANTHROPIC_API_KEY }}`
  - `anthropic-version: 2023-06-01`
  - `content-type: application/json`
- **Body (Expression):**

```javascript
// Montar histórico
const sessao   = $('Buscar Sessão Ativa').first().json; // pode ser vazio
const historico = sessao.historico || '(primeira mensagem)';
const nomeCliente = sessao.nome || $('Normalizar Payload').first().json.nome;
const mensagem  = $('Normalizar Payload').first().json.texto;

const systemPrompt = `[COLAR AQUI O PROMPT COMPLETO DA LÉA do arquivo 01_agente_triagem_lea.md]`
  .replace('${nomeCliente}', nomeCliente)
  .replace('${historico}', historico)
  .replace('${mensagemAtual}', mensagem);

return {
  model: 'claude-sonnet-4-6',
  max_tokens: 500,
  system: systemPrompt,
  messages: [{ role: 'user', content: mensagem }]
};
```

---

## Nó 9 — Extrair Resposta Léa (Code)

```javascript
const resposta = $input.first().json.content?.[0]?.text || '';
return [{ json: { respostaLea: resposta } }];
```

---

## Nó 10 — Enviar WhatsApp (HTTP Request)

- **Method:** POST
- **URL:** `{{ $env.EVO_BASE_URL }}/message/sendText/{{ $('Normalizar Payload').first().json.instancia }}`
- **Headers:** `apikey: {{ $env.EVO_API_KEY }}`
- **Body:**
```json
{
  "number": "{{ $('Normalizar Payload').first().json.remoteJid }}",
  "text": "{{ $json.respostaLea }}"
}
```

---

## Nó 11 — Salvar Sessão (HTTP Request → Sheets)

Append na aba `Sessoes_Advocacia` ou atualiza linha existente.

Campos a salvar: `jid`, `nome`, `area_direito`, `status`, `historico` (atualizado), `data_contato`.

---

## Nó 12 — Escalar Humano (HTTP Request)

- **URL:** `{{ $env.EVO_BASE_URL }}/message/sendText/{{ $json.instancia }}`
- **Body:**
```json
{
  "number": "{{ $env.EVO_TEAM_NUMBER }}",
  "text": "⚠️ *Atenção equipe*\nCliente *{{ $('Normalizar Payload').first().json.nome }}* ({{ $('Normalizar Payload').first().json.telefone }}) precisa de atendimento humano.\nMotivo: *{{ $('Parsear Intent').first().json.intent }}*\nMensagem: \"{{ $('Normalizar Payload').first().json.texto }}\""
}
```

E responder ao cliente:
```json
{
  "number": "{{ $('Normalizar Payload').first().json.remoteJid }}",
  "text": "Compreendo, *{{ $('Normalizar Payload').first().json.nome }}*. Vou encaminhar sua mensagem diretamente para um dos nossos advogados, que entrará em contato o mais breve possível."
}
```

---

## Variáveis de ambiente necessárias

```
ANTHROPIC_API_KEY
EVO_BASE_URL       = https://evo.escritoriocliente.com.br
EVO_API_KEY
EVO_INSTANCE       = instancia_advocacia
EVO_TEAM_NUMBER    = número do grupo da equipe jurídica
GOOGLE_SHEETS_CRM_ID = ID da planilha do escritório cliente
```

---

## Ordem de ativação

1. Publicar `kronos-analise-pdf` (já existe — confirmar ativo)
2. Montar e publicar este orquestrador
3. Configurar webhook na instância Evolution do escritório
4. Testar: mensagem de texto → Léa responde; PDF → análise automática
