# Workflow: kronos-analise-pdf — Guia de Montagem Manual

**ID n8n:** `VFtnXxDmZYEf1saI`
**Status:** ATIVO
**Webhook:** `POST /webhook/whatsapp-pdf`

---

## Fluxo de nós

```
Webhook WhatsApp PDF
  → Normalizar Payload        (Code: detecta documentMessage)
  → É PDF?                    (IF: ehPdf === true)
      → [TRUE]  Aviso Aguarde      (HTTP: envia "Analisando...")
                → Baixar PDF       (HTTP: Evolution getBase64FromMediaMessage)
                → Montar Request   (Code: monta anthropicBody com document block)
                → Claude Sonnet    (HTTP: POST Anthropic /v1/messages)
                → Formatar Análise (Code: extrai texto + formata)
                → Enviar WhatsApp  (HTTP: Evolution sendText)
      → [FALSE] Enviar Erro Tipo  (HTTP: "Só aceito PDF")
```

---

## Nó: Normalizar Payload

Detecta `documentMessage` ou `documentWithCaptionMessage`.
- Extrai: `telefone`, `nome`, `remoteJid`, `instancia`, `ehPdf`, `nomeArquivo`, `msgKey`
- Filtra: `fromMe === true`, event !== 'messages.upsert', grupos

## Nó: Baixar PDF (Evolution)

```
POST {EVO_BASE_URL}/chat/getBase64FromMediaMessage/clinica01
Headers: apikey, Content-Type: application/json
Body: { "message": { "key": msgKey }, "convertToMp4": false }
Timeout: 30s
```

Retorna: `{ "base64": "...", "mimetype": "application/pdf" }`

## Nó: Montar Request Claude

Constrói o `anthropicBody` com:
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1500,
  "messages": [{
    "role": "user",
    "content": [
      {
        "type": "document",
        "source": {
          "type": "base64",
          "media_type": "application/pdf",
          "data": "<base64>"
        }
      },
      {
        "type": "text",
        "text": "<prompt de análise>"
      }
    ]
  }]
}
```

## Nó: Claude Sonnet — Analisar PDF

```
POST https://api.anthropic.com/v1/messages
Headers:
  x-api-key: $env.ANTHROPIC_API_KEY
  anthropic-version: 2023-06-01
  Content-Type: application/json
Body: $json.anthropicBody
Timeout: 60s
```

---

## Erros tratados

| Erro | Resposta ao cliente |
|---|---|
| `base64` ausente no retorno | "Não consegui baixar o documento. Pode reenviar?" |
| `content[0].text` vazio | "Não consegui analisar. Tente novamente." |
| Arquivo não é PDF | "Só consigo analisar arquivos PDF." |

---

## Adaptar para cliente real

1. Trocar `clinica01` por `instancia_advocacia` nos nós HTTP
2. Ajustar prompt de análise conforme especialidade do escritório
3. Adicionar nó de log no Google Sheets (CRM do cliente)
4. Conectar ao orquestrador da Léa (sub-workflow)
