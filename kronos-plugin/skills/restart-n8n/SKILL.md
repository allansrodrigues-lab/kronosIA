---
name: restart-n8n
description: Reinício seguro do container n8n no VPS Kronos, aplicando mudanças de workflow/config publicadas. Use quando precisar "reiniciar o n8n", "aplicar a versão publicada", "restart do container", ou quando uma alteração não pegou sem restart. Confirma a rede Traefik real antes, reinicia e valida que a versão ativa do workflow carregou.
---

# restart-n8n

Safe restart of the n8n container on the Kronos VPS. Confirms the Traefik network, stops, restarts, and verifies that the active workflow version loaded correctly.

> 🔑 **API key da REST:** lida de `~/.kronos/n8n_api_key` (fora do repo — nunca escrever a key neste arquivo). Se der `unauthorized`: criar key nova na UI (Settings → n8n API, sem expiração) e atualizar SÓ aquele arquivo: `printf 'NOVA_KEY' > ~/.kronos/n8n_api_key`. Renovada em 02/07/2026.

## Steps

### 1 — Confirm the real Traefik network name

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "docker network ls --format '{{.Name}}'"
```

Note the actual network name (never assume `traefik` or `web`). Check that the n8n container references it:

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "docker inspect n8n-xve0-n8n-1 --format '{{json .NetworkSettings.Networks}}'"
```

n8n runs with `network_mode: host`, so it does NOT join a named Docker network — it shares the host network directly. If you see it in a named network something is misconfigured.

### 2 — Stop and restart n8n via docker compose

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "cd /docker/n8n-xve0 && docker compose down && docker compose up -d"
```

Watch the startup log until `n8n ready`:

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "docker logs -f --tail 20 n8n-xve0-n8n-1 2>&1 | grep -m1 'n8n ready'"
```

### 3 — Verify the active (published) workflow version loaded

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "docker exec n8n-xve0-n8n-1 node -e \"
  const sqlite3 = require('sqlite3');
  const db = new sqlite3.Database('/home/node/.n8n/database.sqlite');
  db.all(\`
    SELECT we.name, wh.versionId, wh.createdAt
    FROM workflow_entity we
    JOIN workflow_history wh ON we.id = wh.workflowId
    WHERE we.active = 1
    ORDER BY wh.createdAt DESC
  \`, (err, rows) => {
    console.log(JSON.stringify(rows, null, 2));
    db.close();
  });
\""
```

Confirm the `versionId` matches what was last published (not a stale draft). If a workflow shows `active = 0` after restart, re-activate it via the n8n UI or the API:

```bash
curl -s -X PATCH https://n8n.kronosintelligence.com.br/api/v1/workflows/<ID>/activate \
  -H "X-N8N-API-KEY: $(cat ~/.kronos/n8n_api_key)"
```

### 4 — Smoke test: send a webhook and confirm execution

```bash
curl -s -X POST https://n8n.kronosintelligence.com.br/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica01",
    "data": {
      "key": { "remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false, "id": "RESTART-TEST-01" },
      "pushName": "Restart Test",
      "message": { "conversation": "Quero agendar" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

Then confirm an execution was created:

```bash
curl -s https://n8n.kronosintelligence.com.br/api/v1/executions?limit=1 \
  -H "X-N8N-API-KEY: $(cat ~/.kronos/n8n_api_key)" \
  | python3 -c "import sys,json; e=json.load(sys.stdin)['data'][0]; print(e['status'], e['startedAt'])"
```

Expected: `success <timestamp>`. If `error` → check logs with `/n8n-debug`. If `running` after 30s → likely a hanging Haiku call → run `/fix-n8n-auth`.

## Quick reference

| Situation | Command |
|---|---|
| Just restart | `cd /docker/n8n-xve0 && docker compose restart` |
| Full redeploy (picks up compose changes) | `docker compose down && docker compose up -d` |
| Watch live logs | `docker logs -f n8n-xve0-n8n-1` |
| List active workflows | `curl .../api/v1/workflows?active=true -H "X-N8N-API-KEY: ..."` |
