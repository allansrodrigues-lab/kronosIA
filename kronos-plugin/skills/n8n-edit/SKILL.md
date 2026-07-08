---
name: n8n-edit
description: Edição segura de workflows n8n direto no banco SQLite do VPS Kronos (sem UI). Use quando precisar corrigir código de nó (jsCode), trocar parâmetro de nó, aplicar fix em workflow publicado, deletar/restaurar workflow, ou quando uma correção "não pega" mesmo depois de editada. Também quando o usuário mencionar "corrigir nó", "editar workflow", "fix não aplicou", "versão publicada", "apagar workflow", "restaurar backup".
---

# n8n Edit — editar workflows via banco (validado 12/06/2026)

Técnica testada e aprovada em produção (bots Aurora/OdontoVita). Permite ao Claude consertar nós sem depender da UI.

## ⚠️ GOTCHA #1 — A REGRA DE OURO: rascunho ≠ versão que roda
Nesta versão do n8n, o que **executa** é a versão **publicada**, guardada em `workflow_history` e apontada pelo último evento `activated` de `workflow_publish_history`. Editar `workflow_entity.nodes` muda **só o rascunho** — o bot continua rodando o código velho e você acha que o fix falhou.

**Toda edição via DB precisa de 3 passos:**
1. `UPDATE workflow_entity SET nodes=? WHERE id=?` (rascunho — pra UI mostrar certo)
2. `UPDATE workflow_history SET nodes=?, connections=? WHERE versionId = (SELECT versionId FROM workflow_publish_history WHERE workflowId=? AND event='activated' ORDER BY createdAt DESC LIMIT 1)` (versão ativa — o que roda)
3. `docker restart n8n-xve0-n8n-1` (carregar)

Estado "publicado" se confere em `workflow_publish_history` (count>0). `workflow_published_version` fica vazio nesta versão — ignorar.

## Padrão de execução de scripts no container
sqlite3/flatted só resolvem de dentro da pasta do n8n. Heredoc evita inferno de escape de aspas:
```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 'cat > /tmp/q.js <<"EOF"
const s=require("sqlite3");const {parse}=require("flatted");
const db=new s.Database("/home/node/.n8n/database.sqlite");
// ... query ...
EOF
docker cp /tmp/q.js n8n-xve0-n8n-1:/tmp/q.js && docker exec n8n-xve0-n8n-1 sh -c "cd /usr/local/lib/node_modules/n8n && NODE_PATH=/usr/local/lib/node_modules/n8n/node_modules node /tmp/q.js"'
```

## ⚠️ GOTCHA #2 — strings em jsCode editado via script
- **NUNCA** newline literal dentro de string JS → erro de sintaxe. Usar `String.fromCharCode(10)` (ou `(10,10)` pra linha em branco no WhatsApp).
- Aspas simples em replaces: usar `String.fromCharCode(39)` no script de edição pra não brigar com o heredoc.
- O mesmo trecho de código pode ter formatação diferente entre workflows "gêmeos" (uma linha vs multilinha) — conferir `find=true/false` por workflow e ter variante.

## Validar sintaxe ANTES de publicar
jsCode de nó Code usa `return` no topo — validar **embrulhado**:
```js
new vm.Script("(async function(){"+code+"})") // OK
new vm.Script(code) // falso positivo "Illegal return statement"
```

## Backup e restauração (sempre antes de editar/apagar)
```bash
docker exec n8n-xve0-n8n-1 n8n export:workflow --id=<ID> --output=/home/node/.n8n/backup-<data>/<id>.json
docker exec n8n-xve0-n8n-1 n8n import:workflow --input=/caminho/arquivo.json  # restaura (volta DESpublicado!)
```
Após `import`, o workflow precisa de **Publish manual na UI** (ou update na workflow_history).

## Deletar workflow (CLI não tem delete)
1. **ANTES**: varrer TODOS os workflows por referências `executeWorkflow` ao ID (subs chamam subs! ex.: clara→03-bia-ref). Apagar um sub referenciado quebra o publish do pai.
2. Exportar backup.
3. Deletar via DB nas tabelas-filhas + principal: `execution_data`/`execution_entity` (por workflowId), `workflows_tags`, `shared_workflow`, `workflow_statistics`, `workflow_history`, `workflow_publish_history`, `workflow_dependency`, e por fim `workflow_entity`.
4. Restart.

## Ler execuções (diagnóstico cirúrgico)
`execution_data.data` é **flatted**. Estrutura útil:
```js
const j=parse(d.data);
const rd=(j.resultData&&j.resultData.runData)||(j[0]&&j[0].resultData&&j[0].resultData.runData);
rd["Nome Do Node"][0].data.main[0][0].json  // saída do nó
rd["Nome Do Node"][0].source[0].previousNode // quem alimentou
rd["Nome Do Node"][0].executionStatus / .error
```
Execuções `success` podem esconder falha de IA (nó HTTP devolve `{error:...}` como item normal). Sempre olhar a SAÍDA do nó do Claude, não só o status.

## Testar ponta a ponta sem celular
Simular mensagem no webhook como se fosse o Evolution (número Kronos `5519971266736`, sem bot):
```bash
curl -X POST https://n8n.kronosintelligence.com.br/webhook/whatsapp-odonto -H "Content-Type: application/json" -d '{"event":"messages.upsert","instance":"kronosdemo","data":{"key":{"remoteJid":"5519971266736@s.whatsapp.net","fromMe":false,"id":"TESTE-X"},"pushName":"Teste","message":{"conversation":"texto"},"messageTimestamp":1781290000}}'
```
Esperar ~15s entre mensagens (chamada Claude). Conferir resultado lendo as execuções (acima) — as respostas reais chegam no WhatsApp da Kronos.
