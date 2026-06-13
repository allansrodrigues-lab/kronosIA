# DEBUG.md — log de troubleshooting Kronos (n8n / WhatsApp)

> Diário de problemas + causa-raiz + o que já foi tentado. Atualizar a cada sessão de debug.
> Atalho: rodar `/n8n-debug` pro roteiro completo. Acesso: `ssh -i ~/.ssh/kronos_vps root@2.24.101.180`.

---

## STATUS ATUAL (12/06/2026)
✅ **Os dois bots funcionando ponta a ponta** (testado ao vivo pelo Allan):
- Aurora (`5519971514971`, instância `clinica01`) — webhook `/webhook/whatsapp`
- OdontoVita (`5519997237404`, instância `kronosdemo`) — webhook `/webhook/whatsapp-odonto`
- Claude Haiku classificando OK · agendamento fechando OK · ambas instâncias `state=open`.

---

## INCIDENTE: loop de disparo (5.305 execuções) — RESOLVIDO 12/06
**Sintoma:** bot disparando mensagem sem parar.
**Causa-raiz:** dois números-COM-bot conversando entre si (Odonto ↔ Aurora) → cada bot respondia o outro pra sempre.
**Fixes aplicados (e resultado):**
1. `docker stop` no container n8n → ✅ estancou na hora.
2. `n8n unpublish:workflow --all` + `docker restart` → ✅ desativou tudo (CLI só aplica após restart).
3. Religado controlado: `publish` dos 2 orquestradores + 4 sub-workflows + restart → ✅ bots de volta.
**Lição/regra:** testar SEMPRE pelo número da Kronos `5519971266736` (sem automação). Nunca bot-contra-bot.

## INCIDENTE 2: loop bot-a-bot LENTO (madrugada 12/06) — RESOLVIDO + BLINDADO
**Sintoma:** Allan reportou "nada bom". Infra toda verde, mas os dois bots se respondendo (lento, ~4 exec/5min, por isso não soou flood). Aurora↔Odonto trocando "Sou a Clara..." e "tive instabilidade".
**Causa-raiz:** (1) nada impedia um bot de responder mensagem vinda do número de OUTRO bot; (2) gatilho: `EVO_TEAM_NUMBER` = número da Aurora → escalação/erro da Odonto caía no WhatsApp da Aurora e voltava.
**Fix permanente (blindagem):** guard anti-loop no nó "Normalizar Payload" dos 2 orquestradores — denylist `BOTS_KRONOS = ['5519971514971','5519997237404']`; mensagem vinda de número-bot nosso → `return []` (ignora). Loop bot-a-bot agora IMPOSSÍVEL.
**Verificado:** msg simulada do bot Aurora → parou em Normalizar (ignorada); msg da Kronos (humano) → fluxo completo + agendamento `success`. ⚠️ Ao adicionar cliente novo, incluir o número-bot dele na lista `BOTS_KRONOS` de todos os orquestradores.

## SUB-FALHA: "bot não respondia" após reativar — RESOLVIDO 12/06
**Sintoma:** mensagem não gerava execução / orquestrador dava erro.
**Causa-raiz:** `Execute Workflow is not active and cannot be executed` — nessa versão do n8n o orquestrador só chama sub-workflow **publicado**; o `unpublish --all` tinha desativado os subs.
**Fix:** publicar também os subs (`02-agendamento-bia`, `TDJQkNQDJh9PnmSh`=03-atendimento-clara, `02-agendamento-odonto`, `03-atendimento-odonto`) + restart → ✅ resolvido.
**Verificação:** webhooks respondem HTTP 200; execução de teste injetada deu `success`.

---

## REFERÊNCIA: erro 401 do Haiku (Anthropic) — NÃO ATIVO em 12/06
Histórico de sessões antigas. Se voltar, checar **nesta ordem** (causas já vistas):
1. **API key revogada/inválida** — `ANTHROPIC_API_KEY` é env var no container n8n.
2. **`$env` não resolve** no nó do Haiku (expressão errada).
3. **Modo header vs body** da requisição trocado.
4. **Nome da variável corrompido pela auto-tradução do Chrome** — conferir config CRUA do nó, não a UI traduzida. (Esse foi o vilão escondido que custou horas.)
Como testar a key rápido: rodar `bash vps-health.sh` (item 4) — 200 = key OK · 401 = revogada/errada.
(⚠️ o container do n8n NÃO tem `curl`; pra testar à mão use `node` com `fetch`, não curl.)

---

## PRÓXIMOS PASSOS (plano combinado)
1. **Blindar a base** (#1): separar planilha (CRM) e instância por cliente. Hoje Aurora e Odonto dividem o mesmo "Kronos CRM".
2. **Polir Odonto:** roteamento grudado (pergunta geral fica na Bia em vez de ir pra Clara; ex.: "onde fica" → Bia mandou "contate a clínica" sendo que ELA é a clínica) + Bia usa slots inline (sem persistência).
3. **Disjuntor anti-loop:** script no servidor que detecta pico de execuções, desliga o workflow e avisa no WhatsApp.
4. **MCP do n8n:** conectar Claude direto no n8n (verificar pacote + criar API key + URL `https://n8n.kronosintelligence.com.br`).
5. **Limpar duplicatas** no n8n (3x orquestrador-whatsapp, 2x atendimento-clara, cópias 06, 03-bia-ref).
6. **Quiz dos números de venda** com o Allan.
