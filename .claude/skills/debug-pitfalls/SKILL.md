---
name: debug-pitfalls
description: Checklist de armadilhas recorrentes no projeto Kronos antes de iniciar qualquer diagnóstico ou fix. Use sempre que algo "não funciona" ou "não pegou" após uma mudança. Cobre: versão publicada do n8n, tradução do Chrome corrompendo variáveis, API keys revogadas, paths /tmp entre bash/PowerShell, e execução success ocultando erros reais.
---

# Pitfalls Recorrentes — Kronos Debug

Antes de diagnosticar qualquer falha, percorra esta lista. Cada item já causou perda de tempo real neste projeto.

---

## 1. Editou o rascunho em vez da versão publicada

**O que acontece:** fix aplicado, restart feito, problema persiste. A edição foi no `workflow_entity` (rascunho), não no `workflow_history` (o que realmente roda).

**Detectar:**
```bash
docker exec -w /usr/local/lib/node_modules/n8n n8n-xve0-n8n-1 node -e "
const s=require('sqlite3');
const db=new s.Database(process.env.HOME+'/.n8n/database.sqlite');
db.get(\"SELECT workflowHistoryId FROM workflow_publish_history WHERE workflowId=? ORDER BY id DESC LIMIT 1\",['<WORKFLOW_ID>'],(e,r)=>console.log('active historyId:',r&&r.workflowHistoryId));
"
```

**Fix:** Editar sempre o registro em `workflow_history` com o `id` retornado acima. Ver skill `n8n-edit` para o procedimento completo.

**Verificar:** Após restart, re-ler o nó da versão publicada e confirmar que o novo valor está lá.

---

## 2. Chrome auto-tradução corrompeu nome de variável

**O que acontece:** nó HTTP do n8n mostra `x-api-key: {{ $env.ANTHROPIC_API_CHAVE }}` (ou outra tradução) na UI, mas o JSON raw ainda tem o nome original correto — ou vice-versa, a UI parece OK mas o JSON está corrompido.

**Detectar:** Ler o JSON raw da versão publicada, não confiar na UI:
```bash
docker exec -w /usr/local/lib/node_modules/n8n n8n-xve0-n8n-1 node -e "
const s=require('sqlite3');
const db=new s.Database(process.env.HOME+'/.n8n/database.sqlite');
db.get(\"SELECT nodes FROM workflow_entity WHERE id=?\",['<WORKFLOW_ID>'],(e,r)=>{
  const nodes=JSON.parse(r.nodes);
  const node=nodes.find(n=>n.name.includes('Haiku')||n.name.includes('Claude'));
  console.log(JSON.stringify(node&&node.parameters,null,2).substring(0,600));
});
"
```
Procurar por qualquer variável que não seja `ANTHROPIC_API_KEY` exato.

**Fix:** Abrir o n8n com Chrome sem auto-tradução (modo anônimo, ou desativar tradução automática para a página), corrigir o nome da variável para `ANTHROPIC_API_KEY`, salvar, republicar, restart.

**Verificar:** Rodar o comando acima de novo e confirmar `$env.ANTHROPIC_API_KEY` no JSON.

---

## 3. `execution status=success` mascarando erro real

**O que acontece:** todas as execuções mostram `success`, bot continua não respondendo. O nó HTTP de erro devolveu `{error: "..."}` como item normal e o fluxo seguiu com mensagem de fallback ("Tive uma instabilidade...").

**Detectar:** Inspecionar a SAÍDA do nó Claude na execução, não só o status:
```bash
docker exec -w /usr/local/lib/node_modules/n8n n8n-xve0-n8n-1 node -e "
const s=require('sqlite3'),F=require('flatted');
const db=new s.Database(process.env.HOME+'/.n8n/database.sqlite');
db.get(\"SELECT data FROM execution_data WHERE executionId=<EXEC_ID>\",(e,row)=>{
  const obj=F.parse(row.data);
  const runData=obj.resultData.runData;
  for(const k of Object.keys(runData)){
    if(k.includes('Claude')||k.includes('Haiku')||k.includes('Sonnet')){
      const out=runData[k][0].data.main[0][0];
      console.log(k,'->',JSON.stringify(out&&out.json).substring(0,300));
    }
  }
  db.close();
});
"
```
Se o output tiver `\"error\"` em vez de `\"model\"` e `\"content\"`, o Claude retornou erro.

**Fix:** Depende do erro retornado — 401 (API key), 429 (rate limit), 500 (Anthropic down), timeout (rede).

**Verificar:** Injetar mensagem real pelo número da Kronos (`5519971266736`) e confirmar que o output do nó Claude tem `model` e `content`.

---

## 4. API key revogada ou inválida

**O que acontece:** nó retorna 401. Pode ter sido rotacionada no painel Anthropic ou nunca foi definida no container.

**Detectar (2 passos):**
```bash
# Passo 1: confirma que a env var existe no container
docker exec n8n-xve0-n8n-1 sh -c 'echo $ANTHROPIC_API_KEY' | cut -c1-20

# Passo 2: testa a key de dentro do container (sem curl — usar Node)
docker exec n8n-xve0-n8n-1 node -e "
const https=require('https');
const data=JSON.stringify({model:'claude-haiku-4-5-20251001',max_tokens:5,messages:[{role:'user',content:'hi'}]});
const req=https.request({hostname:'api.anthropic.com',path:'/v1/messages',method:'POST',headers:{'x-api-key':process.env.ANTHROPIC_API_KEY,'anthropic-version':'2023-06-01','Content-Type':'application/json'}},r=>console.log(r.statusCode));
req.setTimeout(10000,()=>{console.log('TIMEOUT');req.destroy()});
req.write(data);req.end();
"
```
200 = key válida. 401 = inválida/revogada.

> ⚠️ O container n8n **não tem `curl`**. Sempre usar Node.js para testes HTTP de dentro do container.

**Fix:** Gerar nova key em console.anthropic.com → API Keys. Atualizar no `docker-compose.yml` do n8n (`ANTHROPIC_API_KEY=sk-ant-...`), depois `docker restart n8n-xve0-n8n-1`.

**Verificar:** Repetir o Passo 2 acima e confirmar 200.

---

## 5. Paths `/tmp` divergem entre Bash e PowerShell

**O que acontece:** script funciona no VPS (bash) mas falha localmente (PowerShell/Windows) porque `/tmp/arquivo` não existe.

**Detectar:** Qualquer path começando com `/tmp` em script executado no Windows.

**Fix:**
- No VPS (bash): usar `/tmp/arquivo`
- Local Windows (PowerShell): usar `$env:TEMP\arquivo` ou `C:\Users\Usuario\AppData\Local\Temp\arquivo`
- Para scripts cross-platform: usar variável: `$tmpFile = if ($IsLinux -or $IsMacOS) { "/tmp/arquivo" } else { "$env:TEMP\arquivo" }`

**Verificar:** Executar `[System.IO.Path]::GetTempPath()` no PowerShell para confirmar o path correto no ambiente.

---

## 6. Sub-workflows não publicados (Execute Workflow falha)

**O que acontece:** orquestrador reativado, mas sub-workflows (Bia, Clara) estão inativos → erro "Workflow is not active and cannot be executed".

**Detectar:**
```bash
docker exec n8n-xve0-n8n-1 node -e "
const s=require('sqlite3');
const db=new s.Database(process.env.HOME+'/.n8n/database.sqlite');
db.all(\"SELECT id,name,active FROM workflow_entity\",(e,r)=>{r.forEach(w=>console.log(w.active?'✓':'✗',w.id,w.name));db.close();});
"
```

**Fix:** Publicar todos os subs antes de ativar o orquestrador:
```bash
for id in Orq01RouterV2aa1 01-orquestrador-odonto 02-agendamento-bia TDJQkNQDJh9PnmSh 02-agendamento-odonto 03-atendimento-odonto; do
  docker exec n8n-xve0-n8n-1 n8n publish:workflow --id=$id
done
docker restart n8n-xve0-n8n-1
```

**Verificar:** Repetir o comando detect acima — todos os IDs críticos devem mostrar `✓`.

---

## 7. `[Errno 10054]` / connection reset — MCP google-sheets e SSH (não é bug seu)

**O que acontece:** `mcp__google-sheets__*` ou `ssh` pro VPS retornam `[Errno 10054] Foi forçado o cancelamento de uma conexão existente pelo host remoto` (ou `client_loop: send disconnect: Connection reset by peer`) no meio de uma chamada que estava funcionando segundos antes.

**Detectar:** o mesmo comando, repetido sem mudar nada, funciona na tentativa seguinte (1-2 retries). Se um spreadsheet/host novo nunca funcionou nenhuma vez, aí sim é permissão real (ver item abaixo), não instabilidade de rede.

**Fix:** simplesmente tentar de novo (1-3x). Não é sinal de erro de lógica, config ou permissão — é instabilidade de rede local/transitória observada repetidamente em 05/07 em ambas as ferramentas.

**Não confundir com 403 de permissão real:** planilha recém-criada sem compartilhamento com a service account (`kronos-n8n@kronos-ia-498605.iam.gserviceaccount.com`) dá `HttpError 403 "The caller does not have permission"` — isso NÃO se resolve com retry, precisa o Allan compartilhar (ver skill de setup do MCP / memória `mcp-n8n-sheets-setup`). Conferir quem tem acesso via `get_file_permissions` do conector do Drive antes de insistir tentando o MCP às cegas.

---

## 8. `patchNodeField` falha em nó com config incompleta/quebrada

**O que acontece:** `n8n_update_partial_workflow` com `patchNodeField` em `parameters.documentId.value` retorna `"property does not exist on node"` — mesmo o nó sendo um Google Sheets normal.

**Causa real:** o nó já estava com config incompleta ANTES da sua tentativa (ex: faltando `documentId`/`sheetName` inteiro, ou usando `sheetName` por `gid` numérico em vez de nome). `patchNodeField` só faz find/replace num campo que já existe — não cria campo novo.

**Detectar:** `n8n_get_workflow` (mode `full`) no nó específico e olhar o `parameters` cru — se faltar `documentId`/`sheetName` ou algo estiver com valor estranho (número solto em vez de objeto `{__rl,value,mode}`), a config já estava quebrada antes de você mexer (achado real: `05-pos-venda-diana` tinha 3 nós assim, provavelmente quebrados desde a criação — ver memória `separacao-planilhas-nichos`).

**Fix:** usar `updateNode` com `updates` em notação de ponto pra reconstruir o campo inteiro (ex: `{"parameters.documentId": {"__rl": true, "value": "...", "mode": "id"}, "parameters.sheetName": {"__rl": true, "value": "NomeDaAba", "mode": "name"}}`), usando `sheetName` por NOME (não gid — mais robusto e legível). Comparar com um nó irmão que já funciona (ex: outro "Buscar Sessão X" no mesmo workflow) pra saber o formato correto.

**Verificar:** `n8n_validate_workflow` depois — `errorCount:0` (os avisos de `cachedResultName` ausente são cosméticos, não bloqueiam).
