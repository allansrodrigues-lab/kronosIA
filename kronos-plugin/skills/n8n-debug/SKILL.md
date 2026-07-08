---
name: n8n-debug
description: Diagnóstico e conserto dos bots de WhatsApp no n8n do VPS Kronos. Use sempre que um bot de clínica parar de responder, der erro, disparar mensagem em loop, ou quando precisar inspecionar execuções/workflows do n8n. Também use quando o usuário mencionar "bot não responde", "não chega mensagem", "erro 401", "loop", "disparando sozinho", "ver execução", "debugar n8n", "Aurora parou", "Odonto parou". Roda via SSH direto no servidor.
---

# n8n Debug

## Checklist rápido (na ordem)
1. Editar sempre `workflow_history` (versão publicada/ativa) — nunca o rascunho `workflow_entity`
2. Verificar validade da API key e se `$env` resolve no nó
3. Confirmar que a versão do Evolution/Baileys suporta o recurso
4. Reiniciar n8n (`docker restart n8n-xve0-n8n-1`) e re-testar com **execução real**, não dados de teste

---

Roteiro completo pra diagnosticar e consertar os bots (Aurora/OdontoVita) sem chute. Claude tem acesso SSH direto.

## Integração via MCP (opcional)
Para controlar o n8n direto do Claude Code sem SSH manual:
```bash
claude mcp add n8n -- npx n8n-mcp-server --url https://kronosintelligence.com.br/n8n --api-key $N8N_API_KEY
```
Exige `N8N_API_KEY` no ambiente local. Gerar em: n8n → Settings → API → Create API Key.

> **⚠️ Hook de restart automático** — É possível configurar restart do n8n após edições de workflow:
> ```json
> {
>   "hooks": {
>     "PostToolUse": [{"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "docker restart n8n-xve0-n8n-1"}]}]
>   }
> }
> ```
> **Não usar esse hook globalmente** — ele dispara em *qualquer* Edit/Write (inclusive da landing page, etc.) e reinicia o n8n desnecessariamente. Se quiser, criar um hook com matcher mais específico, ex. só para arquivos de workflow JSON.

> **Skills irmãs:** `n8n-edit` (editar workflow via DB com segurança — inclui o gotcha da versão publicada) · `kronos-bot-patterns` (padrões de arquitetura: handoff, sessão, parser resiliente).

## ⚠️ GOTCHA Nº1 (causa raiz de "fix não pegou")
O que RODA é a **versão publicada** (`workflow_history`, apontada pelo último `activated` em `workflow_publish_history`) — NÃO o `workflow_entity` (rascunho). Edição via DB só vale após atualizar a versão ativa + `docker restart`. Detalhes na skill **n8n-edit**.

## ⚠️ Execução `success` ≠ bot funcionou
Nós HTTP com erro tratado devolvem `{error:...}` como item normal e o fluxo segue com fallback ("Tive uma instabilidade..."). Sempre inspecionar a SAÍDA do nó do Claude na execução (flatted → `resultData.runData["Claude ..."][0].data.main[0][0].json`).

## Acesso
- SSH: `ssh -i ~/.ssh/kronos_vps -o BatchMode=yes root@2.24.101.180`
- Container n8n: **`n8n-xve0-n8n-1`** · Evolution: **`evolution-api`** (apikey `kronos-evo-key-2024`, porta 8080)
- n8n usa **SQLite**: `/home/node/.n8n/database.sqlite`
- Webhooks: Aurora → `/webhook/whatsapp` · Odonto → `/webhook/whatsapp-odonto`
- Números: Aurora `5519971514971` (instância `clinica01`) · Odonto `5519997237404` (instância `kronosdemo`) · Kronos teste `5519971266736` (sem bot)

## ⛔ EMERGÊNCIA: bot disparando em loop
Estancar AGORA (desliga o n8n inteiro):
```bash
docker stop $(docker ps --format "{{.Names}}" | grep -i n8n)
```
Depois religar controlado: `docker start n8n-xve0-n8n-1` e reativar só o necessário.
**Causa quase sempre:** dois números-com-bot conversando. Regra: testar SÓ pelo número da Kronos (sem automação).

## Roteiro de diagnóstico (na ordem)

### 1. Containers e logs
```bash
docker ps --format "{{.Names}}\t{{.Status}}"
docker logs --tail 50 n8n-xve0-n8n-1
```

### 2. As mensagens estão CHEGANDO no n8n?
Confirma se o webhook está vivo (200 = registrado/ativo):
```bash
for p in whatsapp whatsapp-odonto; do
  curl -s -o /dev/null -w "/webhook/$p -> %{http_code}\n" -X POST http://localhost:5678/webhook/$p -H "Content-Type: application/json" -d "{}"
done
```
Confere a config de webhook do Evolution (a porta tem que bater com a do workflow):
```bash
for i in kronosdemo clinica01; do curl -s -H "apikey: kronos-evo-key-2024" http://localhost:8080/webhook/find/$i; echo; done
```
Estado das instâncias (tem que ser `open`):
```bash
for i in kronosdemo clinica01; do curl -s -H "apikey: kronos-evo-key-2024" http://localhost:8080/instance/connectionState/$i; echo; done
```

### 3. Workflows ativos e execuções (via SQLite)
O driver sqlite resolve rodando node de dentro da pasta do n8n. `execution_data.data` é formato **flatted**.
```bash
docker exec -w /usr/local/lib/node_modules/n8n n8n-xve0-n8n-1 node -e '
const s=require("sqlite3"), F=require("flatted");
const db=new s.Database(process.env.HOME+"/.n8n/database.sqlite");
db.all("SELECT id,workflowId,status,startedAt FROM execution_entity ORDER BY id DESC LIMIT 10",(e,r)=>{r.forEach(x=>console.log(x.id,"|",x.workflowId,"|",x.status,"|",x.startedAt));});
'
```
Pra ver o ERRO de uma execução, parsear flatted e ler `obj.resultData.runData` / `obj.resultData.error`.

### 4. Checklist de erro 401 (auth Anthropic)
Nesta ordem: (1) API key válida/não revogada (`ANTHROPIC_API_KEY` é env var no container); (2) `$env` resolve no nó; (3) modo header vs body expression correto; (4) **nome da variável corrompido por auto-tradução do Chrome** — conferir config CRUA, não a UI traduzida.

### 5. Reativar workflows (publish) + restart
⚠️ Nessa versão, o **Execute Workflow exige o sub-workflow publicado** ("Workflow is not active and cannot be executed"). Ao ligar um orquestrador, publicar TAMBÉM os subs que ele chama.
Conjunto que funciona (validado 12/06): `Orq01RouterV2aa1` (Aurora), `01-orquestrador-odonto`, `02-agendamento-bia`, `TDJQkNQDJh9PnmSh` (03-atendimento-clara), `02-agendamento-odonto`, `03-atendimento-odonto`.
```bash
for id in Orq01RouterV2aa1 01-orquestrador-odonto 02-agendamento-bia TDJQkNQDJh9PnmSh 02-agendamento-odonto 03-atendimento-odonto; do
  docker exec n8n-xve0-n8n-1 n8n publish:workflow --id=$id
done
docker restart n8n-xve0-n8n-1 && sleep 10
```
**Mudanças via CLI/`unpublish`/`publish` só aplicam após `docker restart`.**

### 6. Re-testar com execução real
Injetar mensagem como se viesse da Kronos (sem bot = sem loop) e ver a execução:
```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:5678/webhook/whatsapp-odonto -H "Content-Type: application/json" \
  -d '{"instance":"kronosdemo","data":{"key":{"remoteJid":"5519971266736@s.whatsapp.net","fromMe":false,"id":"TESTE-1"},"pushName":"Teste","message":{"conversation":"oi, queria agendar"},"messageType":"conversation","messageTimestamp":1749700000}}'
```
Depois repetir o passo 3 e confirmar `status=success`.

## Atenção (histórico)
- IP de datacenter já foi bloqueado pelo WhatsApp; Baileys/Evolution antigos podem ser rejeitados. Se a conexão cair, considerar proxy residencial / atualizar Evolution. (Em 12/06 ambas conectaram normal no IP do VPS.)
- Aurora e Odonto ainda compartilham o mesmo "Kronos CRM" — separar (regra: blindar a base por cliente).
