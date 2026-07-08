---
name: kronos-central-demos
description: Operar a Central de Demos da Kronos — um único chip de WhatsApp (clinica01) que mostra todas as demos, com uma "chavinha" trocada pelo WhatsApp do dono. Use para trocar/adicionar uma demo na chavinha, plugar entendimento de áudio (transcrição) em qualquer bot, ajustar o delay do buffer, limpar sessão travada ("dados da conversa anterior"), ou redirecionar o webhook de uma instância. Gatilhos: "central de demos", "chavinha", "adiciona demo X", "bot entender áudio", "transcrever áudio no bot", "sessão travada", "bot preso na conversa anterior", "delay do buffer", "redirecionar webhook da instância".
---

# Kronos — Central de Demos (1 chip, várias demos) + áudio nos bots

Tudo via `mcp__n8n__*` (ver [[kronos-mcp]]). Construído em 16/06/2026. Ref: memória [[kronos-multi-servico]].

## Arquitetura

```
1 chip WhatsApp = instância clinica01 (5519971514971)
  → Evolution webhook → /webhook/whatsapp-demo → Roteador (kronos-roteador-demo)
       ├─ comando do dono (/pizzaria /odonto /aurora /resumo /status) → troca o modo (staticData)
       └─ msg normal → encaminha (HTTP) pro webhook do bot do modo atual
```

- **Dono/controle** = Kronos `5519971266736` (número SEM bot — evita loop). Fixado no código do Roteador.
- **Modo atual** persiste no `staticData` do próprio Roteador (não em tabela).
- Comandar: do Kronos → mandar o comando pro número da central (`5519971514971`).

## IDs e caminhos (essenciais)

| Peça | ID | Webhook / nó |
|---|---|---|
| Roteador | `2hYQv4sOQq5AOXmt` (kronos-roteador-demo) | `/webhook/whatsapp-demo` |
| Pizzaria (Bella Massa) | `4X99dI4CyL0IWbNI` (DEMO-01-orquestrador-santaana) | `/webhook/whatsapp-santaana-demo` |
| OdontoVita | `01-orquestrador-odonto` | `/webhook/whatsapp-odonto` |
| Aurora (estética) | `Orq01RouterV2aa1` (01-orquestrador-v2) | `/webhook/whatsapp` |
| Resumo de áudio (serviço) | `PmVvapxMMtjH0GsC` (kronos-resumo-audio) | `/webhook/whatsapp-resumo` |
| **Advocacia / Léa** | `QEawJtNsqlNGwrw0` (DEMO-01-orquestrador-advocacia) | `/webhook/whatsapp-advocacia-demo` |
| **Análise de PDF** | `VFtnXxDmZYEf1saI` (kronos-analise-pdf) | `/webhook/whatsapp-pdf` |
| **Módulo transcrição** | `LYKIjXBKHxSZXQcN` (kronos-transcrever-audio) | Execute Workflow (sub) |

O Roteador encaminha pra `base + caminho`, onde `base = https://n8n.kronosintelligence.com.br`.

## Trocar/checar a chavinha
O dono manda `/status` (vê modo), `/pizzaria`, `/odonto`, `/aurora`, `/resumo`. A lógica vive no nó **Roteia** do Roteador (Code): detecta dono+`/comando`, grava `sd.modo`, responde via `clinica01`; senão monta `forwardUrl` e encaminha o `body` original.

## Adicionar uma NOVA demo à chavinha
1. Garantir que o bot novo **responde pela `clinica01`** (= chip da central). Se ele envia por outra instância, ou trocar pra `clinica01`, ou melhor: deixar **dinâmico** `{{ $json.instancia }}` (responde pelo número que recebeu — funciona standalone E na central).
2. No nó **Roteia** do Roteador, via `patchNodeField` em `parameters.jsCode`:
   - adicionar o comando no `if (cmd === '/x' || ...)`,
   - adicionar `x: 'NOME 😀'` no objeto `nomeModo`,
   - adicionar `x: base + '/webhook/<path-do-bot>'` no objeto `urls`.
3. Validar (`n8n_validate_workflow`) e testar (ver abaixo).

## Plugar ÁUDIO num bot (módulo compartilhado)
O módulo `kronos-transcrever-audio` (`LYKIjXBKHxSZXQcN`, ATIVO) recebe o ctx (precisa de `instancia`, `remoteJid`, `messageId`), baixa o áudio na Evolution, transcreve no **Groq Whisper** e devolve o ctx com `texto`=transcrição e `tipoMensagem='texto'`. A chave do Groq está **hardcoded** no nó "Transcrever Groq" do módulo (e também no nó "Transcrever (Groq Whisper)" do `kronos-resumo-audio`) — rotacionar nos dois lugares.

Padrão de integração (via `n8n_update_partial_workflow`), logo após o "Normalizar Payload":
1. `addNode` IF **"É Áudio?"** — condição `{{ $json.tipoMensagem }}` equals `audio`.
2. `addNode` **"Transcrever Áudio"** — `executeWorkflow` typeVersion `1.3`, `workflowId={__rl:true,value:"LYKIjXBKHxSZXQcN",mode:"id"}`, `workflowInputs={mappingMode:"defineBelow",value:{},schema:[]}` (passa o ctx inteiro — trigger do módulo sem schema = passthrough).
3. `addNode` **"Mensagem Pronta"** — Code passthrough: `return [{ json: $input.first().json }];`.
4. `rewireConnection` o "Normalizar Payload" do antigo destino → "É Áudio?".
5. `addConnection` "É Áudio?" branch `true` → "Transcrever Áudio"; branch `false` → "Mensagem Pronta".
6. `addConnection` "Transcrever Áudio" → "Mensagem Pronta" → (destino original do Normalizar).
7. **Recuperação de ctx pós-Sheets**: se algum nó downstream recupera o ctx por nome (`$('Normalizar Payload')`), repontar pra `$('Mensagem Pronta')` (foi preciso no odonto, no nó "Decidir Rota"). Na pizzaria NÃO precisou: o texto entra pelo **buffer** (transcreve antes de "Gravar no Buffer"; o "Decidir Processar" monta o texto das linhas do buffer).

## Consertos comuns

### "Bot dando dados da conversa anterior" → sessão travada
Sessão nunca expira. Limpar a sessão do telefone:
- Pizzaria: DataTable `santaana_demo_sessoes` (`k10iXpiDZ8FNY6Gf`) — `n8n_manage_datatable deleteRows` filtro `telefone eq <num>`.
- Odonto/Aurora: Google Sheet `Sessoes_Ativas` (CRM `1ZlDFYkgx6aXUM0ayj1e1_K6uX0cruo7VuCcmg1_w5ps`) — achar a linha por telefone e marcar `Status` ≠ ativo (ver [[kronos-mcp]]).
- Melhoria pendente: auto-reset por inatividade ou comando "novo pedido".

### Delay do buffer (pizzaria)
Nó **"Aguardar Buffer"** (Wait) no `4X99dI4CyL0IWbNI`. `updateNode` `parameters.amount`. Hoje **3.5s**. Piso seguro ~3s (abaixo arrisca cortar endereço picado). Buffer table: `demo_buffer_mensagens` (`nGMa7pY70kK6k8ZA`).

### Redirecionar webhook de uma instância (Evolution) — precisa SSH
```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 '
KEY=$(docker exec n8n-xve0-n8n-1 printenv EVO_API_KEY)
BASE=$(docker exec n8n-xve0-n8n-1 printenv EVO_BASE_URL)
curl -s -X POST -H "apikey: $KEY" -H "Content-Type: application/json" \
  -d "{\"webhook\":{\"enabled\":true,\"url\":\"http://2.24.101.180:5678/webhook/<PATH>\",\"webhookByEvents\":false,\"events\":[\"MESSAGES_UPSERT\"]}}" \
  "$BASE/webhook/set/<INSTANCIA>"
'
```
Ver instâncias: `curl -H "apikey:$KEY" "$BASE/instance/fetchInstances"`. Ver webhook atual: `.../webhook/find/<INSTANCIA>`.

## Testar com segurança
- **Teste de sintaxe sem disparar msg**: POST no webhook do Roteador um payload com `fromMe:true` → o Roteador recebe e ignora (zero envio). Conferir execução `success` em `n8n_executions`.
```bash
curl -s -X POST -H "Content-Type: application/json" \
 -d '{"event":"messages.upsert","instance":"clinica01","data":{"key":{"remoteJid":"5519971266736@s.whatsapp.net","fromMe":true,"id":"T1"},"pushName":"Teste","message":{"conversation":"ping"},"messageType":"conversation","messageTimestamp":1}}' \
 "http://localhost:5678/webhook/whatsapp-demo"
```
- **Áudio**: só valida com voz real. Conferir execução do módulo (`LYKIjXBKHxSZXQcN`) — nós "Transcrever Groq" (campo `text`) e "Retornar".
- Bots de demo **não salvam execuções de sucesso** — não estranhar lista vazia/antiga; inspecionar o módulo ou as tabelas.

## Gotchas
- Editar via MCP mexe na workflow ativa e **pega na hora** pros webhooks (testado). Não precisa restart pra esses casos. (Regra geral de restart: ver [[kronos-mcp]]/`n8n-edit`.)
- `patchNodeField` com emoji no `find` funciona, mas é frágil — preferir âncoras sem emoji (ex.: desligar bloco com `if (false) {`).
- Nunca número-com-bot contra número-com-bot ([[feedback-teste-whatsapp-kronos]]). Comandar a chavinha sempre do Kronos (sem bot).
- Chaves de API ficam no n8n/servidor, **nunca no repo** ([[feedback-claude-cuida-das-keys]]).
