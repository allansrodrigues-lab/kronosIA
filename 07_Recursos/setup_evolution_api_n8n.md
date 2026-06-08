# Setup: Evolution API + n8n

> Guia prático para conectar a Evolution API ao n8n e começar a receber mensagens do WhatsApp.

---

## Pré-requisitos

- n8n rodando e acessível via HTTPS (ex: `https://automacao.clinicacliente.com.br`)
- Evolution API instalada (v2.x recomendado)
- Número WhatsApp Business disponível para parear

---

## 1. Instalar a Evolution API (se ainda não estiver rodando)

### Via Docker Compose (recomendado)

Crie o arquivo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  evolution_api:
    image: atendai/evolution-api:latest
    container_name: evolution_api
    restart: always
    ports:
      - "8080:8080"
    volumes:
      - evolution_store:/evolution/store
      - evolution_instances:/evolution/instances
    environment:
      # Servidor
      SERVER_URL: https://evo.clinicacliente.com.br   # URL pública da sua Evolution API
      
      # Autenticação (troque por uma chave forte)
      AUTHENTICATION_TYPE: apikey
      AUTHENTICATION_API_KEY: SUA_CHAVE_FORTE_AQUI
      
      # Webhook global (opcional — pode configurar por instância depois)
      WEBHOOK_GLOBAL_ENABLED: "false"
      
      # Armazenamento
      STORE_MESSAGES: "true"
      STORE_MESSAGE_UP: "true"
      STORE_CONTACTS: "true"
      
      # Log
      LOG_LEVEL: ERROR
      LOG_COLOR: "true"

volumes:
  evolution_store:
  evolution_instances:
```

```bash
docker compose up -d
```

Teste: acesse `https://evo.clinicacliente.com.br` — deve retornar `{"status":"ok"}`.

---

## 2. Criar a instância WhatsApp

### Via API REST (Swagger em `/manager` ou `curl`)

```bash
curl -X POST https://evo.clinicacliente.com.br/instance/create \
  -H "apikey: SUA_CHAVE_FORTE_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "clinica",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

Resposta esperada:
```json
{
  "instance": { "instanceName": "clinica", "status": "created" },
  "hash": { "apikey": "CHAVE_DA_INSTANCIA" },
  "qrcode": { "base64": "data:image/png;base64,..." }
}
```

### Conectar via QR Code

```bash
curl https://evo.clinicacliente.com.br/instance/connect/clinica \
  -H "apikey: SUA_CHAVE_FORTE_AQUI"
```

Ou acesse `https://evo.clinicacliente.com.br/manager` no navegador, selecione a instância e escaneie o QR Code com o WhatsApp do número da clínica.

---

## 3. Configurar o Webhook na Evolution API

Aponta o webhook para o n8n **antes** de criar o workflow (você pode ativar depois).

```bash
curl -X POST https://evo.clinicacliente.com.br/webhook/set/clinica \
  -H "apikey: SUA_CHAVE_FORTE_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "https://automacao.clinicacliente.com.br/webhook/whatsapp",
      "webhookByEvents": false,
      "webhookBase64": false,
      "events": [
        "MESSAGES_UPSERT",
        "MESSAGES_UPDATE",
        "CONNECTION_UPDATE"
      ]
    }
  }'
```

> **MESSAGES_UPSERT** = nova mensagem recebida (principal)
> **MESSAGES_UPDATE** = status de entrega (lido/entregue)
> **CONNECTION_UPDATE** = status da conexão WhatsApp (para alertas)

---

## 4. Criar o Webhook no n8n

### Passo a passo

1. No n8n, crie um novo workflow: **`01-orquestrador-whatsapp`**
2. Adicione o node **Webhook**:
   - **HTTP Method:** `POST`
   - **Path:** `whatsapp`
   - **Authentication:** None (ou Header Auth com a chave da Evolution)
   - **Response Mode:** `Immediately` (responde 200 imediatamente)
3. Ative o workflow para gerar a URL: `https://automacao.clinicacliente.com.br/webhook/whatsapp`

### Payload recebido (formato Evolution API v2)

```json
{
  "event": "messages.upsert",
  "instance": "clinica",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "3EB0A1234567890"
    },
    "pushName": "Maria Silva",
    "message": {
      "conversation": "Olá, quero agendar uma limpeza de pele"
    },
    "messageType": "conversation",
    "messageTimestamp": 1716825600,
    "source": "android"
  }
}
```

---

## 5. Normalizar o payload (node Code no n8n)

Adicione um node **Code** (JavaScript) logo após o Webhook para extrair os campos:

```javascript
const body = $input.first().json.body ?? $input.first().json;

// Ignora mensagens enviadas pelo próprio bot
if (body.data?.key?.fromMe === true) {
  return [];
}

// Ignora eventos que não são mensagens recebidas
if (body.event !== 'messages.upsert') {
  return [];
}

const data = body.data;
const remoteJid = data.key.remoteJid;

// Extrai o número limpo (só dígitos)
const telefone = remoteJid.replace('@s.whatsapp.net', '').replace('@g.us', '');
const ehGrupo = remoteJid.endsWith('@g.us');

// Extrai o texto da mensagem (suporta os tipos mais comuns)
let texto = '';
let tipoMensagem = data.messageType;

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
} else if (data.message?.documentMessage) {
  tipoMensagem = 'documento';
  texto = '[documento]';
}

return [{
  json: {
    telefone,
    nome: data.pushName ?? 'Cliente',
    texto: texto.trim(),
    tipoMensagem,
    ehGrupo,
    messageId: data.key.id,
    timestamp: data.messageTimestamp,
    instancia: body.instance,
    remoteJid
  }
}];
```

---

## 6. Enviar resposta via Evolution API

No final do workflow, use o node **HTTP Request** para enviar a resposta:

```
Method: POST
URL: https://evo.clinicacliente.com.br/message/sendText/clinica
Headers:
  apikey: SUA_CHAVE_FORTE_AQUI
  Content-Type: application/json

Body (JSON):
{
  "number": "{{ $json.telefone }}",
  "text": "{{ $json.resposta }}"
}
```

---

## 7. Testar a integração

### Teste rápido via curl (simula Evolution enviando para n8n)

```bash
curl -X POST https://automacao.clinicacliente.com.br/webhook/whatsapp \
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
      "pushName": "Teste",
      "message": { "conversation": "Quero agendar" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

Verifique no n8n: **Executions** → deve aparecer a execução com os dados normalizados.

---

## 8. Credenciais a registrar no n8n

Em **Settings → Credentials → New**, adicione:

| Nome | Tipo | Campos |
|---|---|---|
| `Evolution API - Clinica` | Header Auth | `apikey: SUA_CHAVE_FORTE_AQUI` |
| `Evolution API - Base URL` | variável de env | `EVO_BASE_URL=https://evo.clinicacliente.com.br` |

Ou use as variáveis de ambiente no `.env` do n8n:

```bash
EVO_BASE_URL=https://evo.clinicacliente.com.br
EVO_API_KEY=SUA_CHAVE_FORTE_AQUI
EVO_INSTANCE=clinica
```

---

## 9. Monitorar a conexão WhatsApp

Adicione um workflow separado **`00-monitor-conexao`** com:

1. **Cron** (a cada 5 minutos)
2. **HTTP Request** → `GET /instance/fetchInstances` (Evolution API)
3. **If** → se `status !== 'open'`
4. **Telegram/Email** → alerta para você

---

## Próximos passos

- [ ] Workflow `01-orquestrador-whatsapp` com classificador de intenção (Claude Haiku)
- [ ] Integrar Google Sheets como CRM
- [ ] Configurar Redis para memória de conversa
- [ ] Conectar agentes especializados (agendamento, atendimento, pós-venda)
