---
name: kronos-auditoria-nicho
description: Auditar e endurecer um nicho Kronos antes de teste ao vivo ou entrega a cliente. Roda a varredura das 8 famílias de bug já encontradas em produção (segredo hardcoded, thinking do Sonnet 5, mídia mal classificada, bot sem data, promessa sem gatilho, dado autoritativo ignorado, dicionário com chave composta, buffer) e aplica as correções validadas. Use quando for testar um nicho ponta a ponta, quando um bot der resposta estranha, antes de mandar demo pra lead real, ou quando o Allan disser "audita o nicho X", "vai testar o X", "prepara o X pro teste", "replica os fixes no X".
---

# Auditoria de nicho Kronos

Checklist forjado no dia 06/08/2026, quando um teste ponta a ponta do Solar e da
Arquitetura destapou 8 famílias de bug. Todas silenciosas: **execução `success`, cliente
recebendo lixo**. Nunca confie no status verde.

## Antes de tudo

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180
```

Script pronto de varredura: `auditar.js` (nesta pasta). Copie via **scp**, nunca heredoc —
código com aspas simples quebra o argumento do ssh:

```bash
scp -i ~/.ssh/kronos_vps auditar.js root@2.24.101.180:/tmp/auditar.js
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 'docker cp /tmp/auditar.js n8n-xve0-n8n-1:/tmp/ && docker exec n8n-xve0-n8n-1 sh -c "cd /usr/local/lib/node_modules/n8n && NODE_PATH=/usr/local/lib/node_modules/n8n/node_modules node /tmp/auditar.js"'
```

## As 8 famílias

### 1. Segredo hardcoded no nó
**Sintoma:** nenhum — só vaza quando alguém exporta o workflow pro repo público.
**Detecção:** regex `gsk_|sk-ant-|AIza|ghp_|xox[baprs]-` em `workflow_entity` **e**
`workflow_history` (versão publicada guarda cópia própria — limpar só o rascunho deixa o
segredo no banco).
**Fix:** trocar por `={{ $env.NOME_DA_KEY }}` e pôr a variável no `environment:` do
`/docker/n8n-xve0/docker-compose.yml`. Ver [[n8n-env-vars-docker-compose]] — exige
`docker compose up -d`, **`docker restart` não relê o compose**.

### 2. Thinking do Sonnet 5 comendo a resposta
**Sintoma:** JSON cru no WhatsApp do cliente, ou resposta cortada no meio.
**Causa:** sem `thinking` declarado, o Sonnet 5 usa thinking adaptativo, e `max_tokens`
limita raciocínio **+** texto juntos.
**Detecção:** nó com `claude-sonnet-5` e sem `thinking` no corpo. **Audite por conteúdo,
nunca por nome de nó** — calculadora e parecer montam o `anthropicBody` em nós com nomes
fora do padrão `Montar Prompt *`.
**Fix:** `thinking: { type: 'disabled' }` + `max_tokens >= 1200`.
**Diagnóstico:** `stop_reason: max_tokens` e `usage.output_tokens_details.thinking_tokens`
alto na execução.

### 3. Fallback do parser que joga fora resposta boa
**Sintoma:** "Tive uma instabilidade" no meio de conversa saudável.
**Causa:** o modelo às vezes responde em **prosa pura**, sem JSON — e a resposta é ótima.
Fallback de 1 nível descarta.
**Fix obrigatório — 3 níveis:** JSON válido → campo `mensagem` · JSON truncado → resgata
`"mensagem"` por regex · **prosa pura → usa o texto** (cortando JSON grudado no fim) ·
nada aproveitável → frase educada. Referência: `Parsear Resposta Sofia`.

### 4. Mídia mal classificada
**Sintoma:** cliente manda a conta/planta e o bot pede pra digitar.
**Causa:** `.jpg` enviado **como arquivo** vira `documentMessage` com mimetype `image/jpeg`;
código que só testa `pdf` classifica como `documento` e não roteia.
**Fix** (nos dois blocos, `documentMessage` e `documentWithCaptionMessage`):
```js
tipoMensagem = mime.includes('pdf') ? 'pdf' : (mime.startsWith('image/') ? 'imagem' : 'documento');
texto = tipoMensagem === 'pdf' ? '[pdf]' : (tipoMensagem === 'imagem' ? '[foto]' : '[documento]');
```

### 5. Bot não sabe que dia é hoje
**Sintoma:** aceita "dia 10, terça" quando dia 10 é segunda; grava visita com ano passado.
**Fix duplo:** tabela de 14 dias calculada em JS injetada no prompt (`AAAA-MM-DD = dia`,
timezone `America/Sao_Paulo`, fim de semana marcado `[FECHADO]` se o nicho não atende) +
trava no parser corrigindo ano de data no passado. **Injete só a DATA, nunca a hora** —
hora quebra o `cache_control` a cada turno. Ver [[bug-bot-nao-sabe-data-hoje]].

### 6. Promessa sem gatilho (a família mais cara)
**Sintoma:** o bot anuncia uma ação e o sistema não executa. Cliente fica no vácuo.
Já apareceu em: calcular, agendar visita, encaminhar pra equipe, recalcular.
**Regra:** liste **cada verbo de ação que o bot pode prometer em prosa** e garanta duas pontas:
- **prompt** — regra amarrando o anúncio ao campo (`se a SUA mensagem diz que vai X, marque acao=X nesse MESMO turno`)
- **código** — gatilho que dispara mesmo se o modelo esquecer:
```js
const anunciou = /vou calcular|calcular agora|refazer a simula|encaminhar/i.test(String(j.mensagem||''));
aciona: completo && (!jaFez || anunciou || mudouBase)
```
Ver [[bug-calculadora-nao-dispara-perfil-vazio]].

### 7. Dado autoritativo ignorado / chave composta
Dois primos que aparecem no mesmo lugar: montagem do perfil.

**7a — dado da fatura não sobrescreve.** `if (!perfil.valor_conta)` só preenche campo vazio,
então o valor lido do documento nunca substitui o que o cliente chutou de cabeça.
**Fix:** o que vem de leitura de documento é autoritativo — detecte o padrão do texto
sintetizado e sobrescreva.

**7b — dicionário com chave composta.** `FAIXAS[perfil.tipo_projeto]` quebra porque a LLM
salva `"reforma residencial"`, e a chave é `"reforma"`. **Fix:** normalizar por regex, do
mais específico pro mais genérico (reforma antes de residencial).

### 8. Buffer de mensagem picada
Todos os orquestradores em **1,5s** (06/08). Curto demais parte a frase em duas execuções e
o bot responde duas vezes; longo demais deixa a conversa lenta. Se o cliente reclamar de
resposta duplicada, subir pra 2s. Ver [[buffering-debounce-bots]].

## Aplicar correção

Sempre em `workflow_entity` **e** na linha de `workflow_history` cujo `versionId` =
`activeVersionId`, seguido de restart. Ver skill `n8n-edit`.

Toda edição de código deve terminar com validação de sintaxe:
```js
new vm.Script("(async function(){" + jsCode + "})")   // embrulhado, senão dá falso "Illegal return"
```

## Checklist de aceitação — só entregue o nicho depois disto

Rode como conversa real, multi-turno (mandar tudo de uma vez não pega os bugs):

- [ ] Preço/estimativa **aparece com número** na mensagem, não "vou calcular"
- [ ] Estimativa **sobrevive** aos turnos seguintes (pergunte outra coisa e volte)
- [ ] Documento **como foto** e **como arquivo** — os dois leem
- [ ] Documento que não é do nicho → fallback educado, sem inventar dado
- [ ] Dado do documento diferente do declarado → recalcula e comenta a diferença
- [ ] Data errada de propósito ("dia 10, terça" quando é segunda) → **corrige e não agenda**
- [ ] Agendamento no CRM com **ano correto** e formato `AAAA-MM-DD`
- [ ] Escalação: o bot diz que vai encaminhar → equipe **realmente** notificada
- [ ] Mensagem picada em 2 partes rápidas → não responde duas vezes
- [ ] Áudio → transcreve
- [ ] Nenhum `stop_reason: max_tokens` nas execuções do teste

## Como ler execuções sem UI

`execution_data.data` é **flatted**. Status `success` esconde falha de IA — olhe a saída do
nó do Claude, não o status:

```js
const {parse} = require("flatted");
const j = parse(d.data);
const rd = (j.resultData && j.resultData.runData) || (j[0] && j[0].resultData && j[0].resultData.runData);
rd["Nome Do Node"][0].data.main[0][0].json     // saída
rd["Nome Do Node"][0].error                    // erro do nó
```

## Google Sheets sem MCP

Quando o MCP cai com `Errno 10053` (processo vivo, socket morto — só restart do Claude
resolve), use o mesmo interpretador dele, que já tem as libs:

```
~/AppData/Roaming/uv/tools/mcp-google-sheets/Scripts/python.exe
```
com `google.oauth2.service_account` + `kronos-service-account.json`. Ver
[[mcp-n8n-sheets-setup]]. No Windows, `export PYTHONIOENCODING=utf-8` antes de imprimir
acento.
