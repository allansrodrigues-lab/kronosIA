---
name: kronos-bot-patterns
description: Padrões de arquitetura validados dos bots de WhatsApp Kronos (orquestrador + Clara atendimento + Bia agendamento). Use ao criar bot pra novo cliente, adaptar fluxo existente, revisar handoff entre agentes, configurar sessão/memória em Google Sheets, ou caçar bug de "bot esquece a conversa", "não passa pro agendamento", "instabilidade", "mensagem some". Complementa kronos-workflow (criação) e n8n-debug (diagnóstico).
---

# Padrões de bots Kronos (validados em produção 12/06/2026)

Arquitetura: **Orquestrador** (webhook Evolution → decide rota) → **Clara** (atendimento/dúvidas) e **Bia** (agendamento), sessão em Google Sheets aba `Sessoes_Ativas`.

## 1. Sessão/memória (Sheets) — regras que NÃO podem quebrar
- Colunas: `ID, Telefone, Agente, Fase, Historico (JSON), Dado_Temp, Criado_Em, Atualizado_Em, Status`.
- Roteamento do orquestrador ("Decidir Rota"): sessão com `Telefone` igual + `Status='ativo'` → roteia pelo `Agente` (BIA/CLARA). Sem sessão ativa → Clara.
- **Ler e gravar na MESMA aba.** Bug clássico: "Buscar Sessão" apontando pra aba errada (ex.: Agendamentos) → bot se reapresenta a cada mensagem. Conferir `sheetName` de TODOS os nós de sessão.

## 2. Handoff Clara→Bia — o pulo do gato
`Execute Workflow` é **síncrono**: a Bia roda DENTRO da execução da Clara, e o "Preparar Sessão" da Clara roda DEPOIS, sobrescrevendo o que a Bia gravou.
**Regra:** no `passar_para_bia`, a Clara grava `Agente='BIA'` + `Status='ativo'` (passa o bastão — NUNCA 'encerrado'/'CLARA'):
```js
const ehHandoff = acao === 'passar_para_bia';
const statusSessao = (!ehHandoff && (encerrar_sessao || acao === 'encerrar')) ? 'encerrado' : 'ativo';
// ... Agente: ehHandoff ? 'BIA' : 'CLARA',
```

## 3. Sub-workflow recebe handoff sem a mensagem do cliente
No handoff, o contexto chega com `mensagem` = fala da Clara e SEM `texto` do cliente (o pedido real está em `historicoAtualizado`). Sem tratar → Claude recebe `content: undefined` → **400 "messages.0.content: Field required"** → fallback "instabilidade". No "Montar Prompt Bia":
```js
let texto = ctx.texto;
let __histHandoff = null;
if (!texto && Array.isArray(ctx.historicoAtualizado) && ctx.historicoAtualizado.length) {
  const __h = ctx.historicoAtualizado.filter(m => m && m.content);
  const __u = [...__h].reverse().find(m => m.role === 'user');
  texto = __u ? __u.content : '';
  __histHandoff = __h.slice();
  while (__histHandoff.length && __histHandoff[__histHandoff.length-1].role === 'assistant') __histHandoff.pop();
}
// usar __histHandoff como historico quando existir; sempre: historico.filter(m => m && m.content)
```

## 4. Parser de resposta da IA — SEMPRE resiliente
O `Historico` guarda turns do assistant em texto puro → o Claude imita e às vezes responde texto em vez do JSON pedido. Parser frágil joga fora resposta boa. Padrão:
```js
let parsed = null;
try { parsed = JSON.parse(cleaned); } catch(_e1) {}
if (!parsed) { const _m = cleaned.match(/\{[\s\S]*\}/); if (_m) { try { parsed = JSON.parse(_m[0]); } catch(_e2) {} } }
if (!parsed || !parsed.mensagem) parsed = { mensagem: cleaned.replace(/\{[\s\S]*\}/, '').trim().slice(0, 400) || cleaned.slice(0, 400), encerrar_sessao: false };
```
(validação de `acao` existente já força default depois)

## 5. Dado morre depois de nó Google Sheets
Saída de nó Sheets = linha da planilha; campos do fluxo (mensagem, encerrar_sessao...) SOMEM. Nó downstream deve resgatar do nó de origem:
```js
let input = $input.first().json;
if (!input.mensagem) { try { const _pdr = $('Preparar Dados Reserva').first().json; if (_pdr && _pdr.mensagem) input = _pdr; } catch(_e) {} }
```

## 6. Nó Sheets update — nunca "Map Automatically" às cegas
Update exige `Column to match on` + nomes de campos IGUAIS às colunas. Se o Code anterior emite `slot_id` e a planilha tem `ID` → "Could not find column for key". Preferir **Map Each Column Manually**: match `ID = {{ $json.slot_id }}`, e mapear SÓ as colunas a atualizar (as não mapeadas ficam preservadas).

## 7. Envio WhatsApp (Evolution sendText)
- `jsonBody: {{ { number: $json.telefone, text: ... } }}`.
- **On Error = Continue (using error output)** — número sem WhatsApp devolve 400 (`exists:false`) e não pode derrubar o fluxo.
- **Despedida automática** (anexada no envio quando a sessão encerra — cobre agendamento concluído E encerramento):
```
={{ { number: $json.telefone, text: ($json.sessao_update && $json.sessao_update.Status === "encerrado") ? ($json.mensagem + String.fromCharCode(10,10) + "Foi um prazer te atender! A <CLINICA> agradece o contato 💙 Estou sempre por aqui quando precisar.") : $json.mensagem } }}
```

## 9. Error Trigger centralizado — padrão monitor (obrigatório em todo workflow)

Nunca adicionar Error Trigger individualmente em cada workflow. O padrão Kronos usa **um workflow centralizador** apontado via `settings.errorWorkflow`.

**Workflow:** `kronos-error-handler` (ID: `X29vC9p5WB38iZFI`) — ativo em produção.
**Monitor:** `kronos-monitor-selfhealing` (ID: `ADmfpDIilh48WwV3`) — cron 30min, lê `Log_Monitoramento` e envia digest WA.

**Ao criar ou clonar qualquer workflow** — aplicar imediatamente:
```js
// via MCP n8n_update_partial_workflow:
{ type: "updateSettings", settings: { errorWorkflow: "X29vC9p5WB38iZFI" } }
```

**O error-handler faz automaticamente:**
1. Formata o erro com diagnóstico de tipo: `AUTH_401 | SHEETS | TIMEOUT | WHATSAPP | LLM | GERAL`
2. Loga em `Log_Monitoramento` (CRM `1ZlDFYkgx6aXUM0ayj1e1_K6uX0cruo7VuCcmg1_w5ps`)
3. Envia alerta WA para `$env.EVO_TEAM_NUMBER`

**Aba `Log_Monitoramento` colunas:** `Timestamp | Workflow | Ultimo_No | Tipo_Erro | Mensagem | Exec_ID | Status`

**Gotcha:** workflows com nó `Call '03-bia-ref'` (jNvIB83x2sWWbkW1 — arquivado) bloqueiam republish. Remover o nó antes de qualquer update de settings: `{ type: "removeNode", name: "Call '03-bia-ref'" }`.

## 10. Adicionar uma intent nova a um orquestrador existente (via MCP, sem restart)
Padrão validado 03-04/07 (parecer científico plugado no Odonto replicando o que já existia na Aurora).
Uma ÚNICA chamada `mcp__n8n__n8n_update_partial_workflow` com `operations` atômicas — não precisa reescrever o workflow, nem restart do container (a ativação via MCP registra a versão publicada na hora):
1. **`patchNodeField`** no nó "Parsear Intent" (Code) — find/replace no array `validos` do jsCode pra incluir a intent nova.
2. **`patchNodeField`** no nó "Montar Prompt Haiku" (Code) — find/replace no systemPrompt pra adicionar a definição da intent na lista `INTENÇÕES DISPONÍVEIS` (definição ESTREITA — dizer explicitamente o que NÃO é essa intent, senão o Haiku classifica errado por excesso de zelo).
3. **`addNode`** dos nós novos: 1 IF (`Intent e <Nome>?`, condição `{{ $json.intent }}` equals `<INTENT>`) + os nós de ação (ex.: 2 httpRequest — avisa o cliente + dispara o serviço).
4. **`rewireConnection`** — pegar a conexão FALSE de onde a rota cai hoje (ex.: `Intent e Agendar?` false → `Chamar Clara`) e apontar pro IF novo; dele, `branch:"true"` → ação, `branch:"false"` → o destino antigo (`Chamar Clara`).
⚠️ **SEMPRE usar `branch:"true"/"false"`, nunca `sourceIndex`** — usar o mesmo `sourceIndex` em duas conexões de um IF manda as duas pro MESMO braço (quebra a lógica sem erro nenhum).
**Antes de escrever as operations:** buscar `n8n_get_workflow(mode:"full")` de um workflow IRMÃO que já tem a intent (ex.: a Aurora tem parecer, a Advocacia tem outro padrão) — copiar a estrutura exata dos nós de lá em vez de inventar do zero.
**Depois:** `n8n_validate_workflow` (esperar `errorCount:0`) e testar com um payload webhook simulado (`5500TEST*`) — checar via `n8n_executions` que a intent nova classificou certo E que a rota antiga (o "OUTRO"/fallback) não regrediu.

## 8. Checklist novo cliente (resumo operacional)
1. Instância Evolution própria + planilha própria (regra-mãe: blindar a base).
2. Clonar workflows; conferir TODOS os pontos 1–7 acima no clone.
3. `Execute Workflow` exige sub **publicado** — publicar subs antes do orquestrador (inclusive relays tipo 03-bia-ref).
4. Testar via webhook simulado (número Kronos `5519971266736`) ANTES de teste real: fluxo completo dúvida → handoff → 3 slots → escolha → confirmação → CRM salvo → despedida.
5. Limpar `Sessoes_Ativas` entre baterias de teste (histórico sujo contamina o prompt).
