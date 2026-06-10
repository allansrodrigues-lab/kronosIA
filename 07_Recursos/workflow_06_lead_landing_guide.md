# Workflow 06 — Lead da Landing Page

Recebe os leads enviados pelo formulário da landing page (`index.html`), salva no Google Sheets e notifica a equipe Kronos no WhatsApp.

## Fluxo

```
Receber Lead (Site)  ──▶  Validar e Normalizar  ──▶  Salvar Lead (Sheets)
                                                            │
                                                            ▼
              Responder ao Site  ◀──  Notificar Equipe (WhatsApp)
```

## Nós

| # | Nó | Tipo | Função |
|---|----|------|--------|
| 1 | **Receber Lead (Site)** | Webhook | Recebe o `POST` JSON do formulário. Path `contato-kronos`, CORS liberado (`allowedOrigins: *`). |
| 2 | **Validar e Normalizar Lead** | Code | Limpa os campos, valida nome+contato e monta a mensagem de alerta interno. |
| 3 | **Salvar Lead (Sheets)** | Google Sheets (append) | Grava o lead na aba **Leads** do CRM. |
| 4 | **Notificar Equipe (WhatsApp)** | HTTP Request → Evolution API | Manda o alerta do novo lead para o número interno da Kronos. |
| 5 | **Responder ao Site** | Respond to Webhook | Devolve `{ ok: true }` para o `fetch` do site (dispara a msg verde de sucesso). |

> Os nós 3 e 4 usam `onError: continueRegularOutput` — se o Sheets ou a Evolution falharem, o fluxo **ainda responde 200** ao site, evitando que o visitante veja erro.

## URL do webhook

Depois de **ativar** o workflow no n8n, a URL de produção fica:

```
https://SEU-N8N.com/webhook/contato-kronos
```

Cole essa URL na constante `WEBHOOK_URL` no topo do `<script>` em `07_Recursos/index.html`:

```js
var WEBHOOK_URL = 'https://SEU-N8N.com/webhook/contato-kronos';
```

> Use a URL **de produção** (`/webhook/`), não a de teste (`/webhook-test/`), que só funciona com o editor aberto.

## Variáveis de ambiente (n8n)

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `GOOGLE_SHEETS_CRM_ID` | ID da planilha do CRM | `1AbC...xyz` |
| `EVO_BASE_URL` | URL base da Evolution API | `https://evo.seudominio.com` |
| `EVO_INSTANCE` | Instância WhatsApp que envia o alerta | `kronos` |
| `EVO_API_KEY` | API key da Evolution | `••••••` |
| `EVO_TEAM_NUMBER` | Número que recebe os alertas de lead (com DDI+DDD) | `5519971266736` |

## Planilha — aba `Leads`

Crie a aba **Leads** com estas colunas (linha 1, exatamente nesta ordem):

```
Data_Hora | Nome | Contato | Segmento | Mensagem | Origem | Status
```

## Payload recebido do site

```json
{
  "nome": "Allan",
  "contato": "19 99999-0000",
  "segmento": "Clínica",
  "mensagem": "Quero automatizar o atendimento",
  "origem": "landing-page",
  "data": "2026-06-09T12:00:00.000Z"
}
```

## Teste rápido (curl)

```bash
curl -X POST https://SEU-N8N.com/webhook/contato-kronos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste","contato":"19 99999-0000","segmento":"Clínica","mensagem":"Olá"}'
```

Resposta esperada: `{"ok":true,"message":"Lead recebido com sucesso"}`

## Credenciais necessárias

- **Google Sheets OAuth2** — conta de serviço/credencial da Kronos com acesso à planilha do CRM.
- **Evolution API** — via variáveis de ambiente (não precisa de credencial nativa do n8n; usa header `apikey`).
