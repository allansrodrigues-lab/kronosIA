#!/usr/bin/env bash
# vps-health.sh — snapshot de saúde do VPS Kronos (n8n + Evolution + Anthropic).
# Somente LEITURA. Seguro de re-rodar quantas vezes quiser.
# Uso: bash vps-health.sh
# Overrides opcionais: KRONOS_KEY=~/.ssh/outra KRONOS_HOST=root@1.2.3.4 bash vps-health.sh
set -uo pipefail

KEY="${KRONOS_KEY:-$HOME/.ssh/kronos_vps}"
HOST="${KRONOS_HOST:-root@2.24.101.180}"

echo "================ Kronos VPS Health ================"
date
echo "Host: $HOST"
echo

if [ ! -f "$KEY" ]; then
  echo "ERRO: chave SSH nao encontrada em $KEY"
  exit 1
fi

ssh -i "$KEY" -o BatchMode=yes -o ConnectTimeout=15 "$HOST" bash -s <<'REMOTE'
set -uo pipefail

echo "--- 1) Containers ---"
docker ps --format '{{.Names}}\t{{.Status}}'
echo

echo "--- 2) n8n: ultimas 50 linhas de log ---"
docker logs --tail 50 n8n-xve0-n8n-1 2>&1
echo

echo "--- 3) Env vars resolvem no container n8n? (valor mascarado) ---"
for v in ANTHROPIC_API_KEY EVO_API_KEY EVO_BASE_URL EVO_TEAM_NUMBER; do
  val=$(docker exec n8n-xve0-n8n-1 printenv "$v" 2>/dev/null)
  if [ -n "$val" ]; then echo "  $v = OK (${#val} chars)"; else echo "  $v = AUSENTE ⚠️"; fi
done
echo

echo "--- 4) Teste Anthropic API (key valida?) ---"
code=$(docker exec n8n-xve0-n8n-1 node -e '
const ctrl=new AbortController(); setTimeout(()=>ctrl.abort(),20000);
fetch("https://api.anthropic.com/v1/messages",{method:"POST",signal:ctrl.signal,headers:{"x-api-key":process.env.ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},body:JSON.stringify({model:"claude-haiku-4-5-20251001",max_tokens:10,messages:[{role:"user",content:"hi"}]})}).then(r=>{console.log(r.status);process.exit(0);}).catch(()=>{console.log("ERR");process.exit(0);});
' 2>/dev/null)
echo "  HTTP $code  ( 200=key OK | 401=key revogada/invalida )"
echo

echo "--- 5) Evolution: estado das instancias ---"
for i in kronosdemo clinica01; do
  printf "  %s: " "$i"
  curl -s --max-time 10 -H "apikey: kronos-evo-key-2024" http://localhost:8080/instance/connectionState/$i || echo "(sem resposta)"
  echo
done
echo

echo "--- 6) Webhooks n8n registrados? (200 = vivo) ---"
for p in whatsapp whatsapp-odonto; do
  printf "  /webhook/%s -> " "$p"
  curl -s -o /dev/null -w "%{http_code}\n" --max-time 10 -X POST http://localhost:5678/webhook/$p -H "Content-Type: application/json" -d "{}"
done
echo

echo "--- 7) Ultimas execucoes (status) ---"
docker exec -w /usr/local/lib/node_modules/n8n n8n-xve0-n8n-1 node -e '
const s=require("sqlite3");
const db=new s.Database(process.env.HOME+"/.n8n/database.sqlite");
db.all("SELECT id,workflowId,status FROM execution_entity ORDER BY id DESC LIMIT 5",(e,r)=>{
  if(e){console.log("  (erro lendo db)");return;}
  r.forEach(x=>console.log("  "+x.id+" | "+x.workflowId+" | "+x.status));
});' 2>/dev/null || echo "  (nao consegui ler execucoes)"

echo
echo "================ fim ================"
REMOTE
