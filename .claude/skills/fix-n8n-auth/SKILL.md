---
name: fix-n8n-auth
description: Diagnostica e conserta erros 401 de auth da API Anthropic/Claude Haiku nos workflows n8n do VPS Kronos. Use quando um nó de IA retornar 401/403, "credit balance too low", a key parecer revogada, $env.ANTHROPIC_API_KEY não resolver, ou os headers (x-api-key, anthropic-version) estiverem errados. Cobre também variável corrompida por auto-tradução do Chrome.
---

# fix-n8n-auth

Diagnose and fix Claude Haiku / Anthropic API 401 auth errors in n8n workflows.

## Steps

### 1 — Verify API key validity

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "docker exec n8n-xve0-n8n-1 printenv ANTHROPIC_API_KEY"
```

Take the key and confirm it is active at console.anthropic.com → API Keys.
If revoked: generate a new key, update the n8n variable (Settings → Variables), and restart the container.

### 2 — Verify $env resolution inside the node

In the failing n8n node, add a temporary **Set** node just before the HTTP Request node:

```
Field: debug_key
Value: {{ $env.ANTHROPIC_API_KEY }}
```

Run a test execution and confirm the Set node output shows the real key value (not `undefined` or an empty string).
If empty: the variable name is wrong or was not saved — re-enter it manually and restart n8n.

### 3 — Inspect for Chrome auto-translation corruption

Chrome can silently translate field labels and JSON keys in the n8n editor UI, corrupting variable names (e.g. `x-api-key` → `x-chave-api`).

Check the raw config:
```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "docker exec n8n-xve0-n8n-1 node -e \"
    const sqlite3 = require('sqlite3');
    const db = new sqlite3.Database('/home/node/.n8n/database.sqlite');
    db.get(\\\"SELECT nodes FROM workflow_entity WHERE name LIKE '%Haiku%' OR name LIKE '%Anthropic%' LIMIT 1\\\", (e,r) => { console.log(r?.nodes); db.close(); });
  \""
```

Inspect the JSON for the HTTP Request node. Confirm:
- Header name is literally `x-api-key` (not translated)
- Header value is `={{ $env.ANTHROPIC_API_KEY }}` (not `={{ $env.CHAVE_API_ANTHROPIC }}` or similar)
- `anthropic-version` header is present and untouched

If corrupted: edit the node in an English-language browser session (or with Chrome translate disabled for the n8n domain) and re-enter the correct values.

### 4 — Restart n8n

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "docker restart n8n-xve0-n8n-1 && docker logs -f --tail 30 n8n-xve0-n8n-1"
```

Wait for `n8n ready on port 5678` before proceeding.

### 5 — Re-run and confirm

Trigger a test message via the Kronos WhatsApp number (`5519971266736`) or curl:

```bash
curl -X POST https://SEU-N8N/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica01",
    "data": {
      "key": { "remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false, "id": "AUTHTEST01" },
      "pushName": "Teste Auth",
      "message": { "conversation": "Quero agendar" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

Check the n8n execution log: the Haiku node must show HTTP 200 and a valid `intent` in the response body.
If still 401: escalate — the key may have billing issues or the account may be rate-limited.

## Quick reference — common root causes

| Symptom | Root cause | Fix |
|---|---|---|
| 401 on every run | Key revoked | New key + restart |
| 401 only in production | `$env` not set in prod container | Re-enter variable + restart |
| Key resolves but wrong value | Chrome translated the variable name | Re-enter in English session |
| 401 after Chrome translated UI | Header key corrupted | Disable translate, fix headers |
| 200 in test, 401 in real run | Draft vs published version mismatch | Publish active version + restart |
