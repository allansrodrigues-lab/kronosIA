# Robô de Prospecção Ativa — Kronos Operação (autopeças)

Reaproveita a máquina já construída pra Linha B (`07_Recursos/prospeccao_robo_disparador.md`, skill `kronos-prospeccao-robo`) — mesmo disparador n8n, mesmos chips do rodízio (Comercial + cobaia, 20 msgs/dia cada, ver `CLAUDE.md`). O que muda pra autopeças é **o conteúdo**: templates próprios da Linha A (nunca linguagem de "atendimento"/chatbot — regra de posicionamento já registrada em `20_AutoPecas/README.md`).

## ⚠️ Isto ainda não está configurado — falta a parte que só dá pra fazer com os MCPs locais

Esta sessão (Claude Code na nuvem) **não tem acesso aos MCPs `mcp__n8n__*` e `mcp__google-sheets__*`** — são MCPs locais, só existem na sessão do computador do Allan (ver skill `kronos-mcp`). Tudo abaixo está pronto pra copiar, mas quem efetivamente abastece a fila e ajusta o disparador precisa ser uma sessão local.

## O que falta fazer (na sessão local, com skill `kronos-prospeccao-robo`)

1. **Adicionar as linhas na aba `Prospeccao`** do Kronos CRM Interno (`1tOXVM8frTwxbhCR1Gmb2dyPFNks8INCNSKWeg9t1UK4`) — usar os 40 leads de `20_AutoPecas/LEADS.md` (Captação #3, já com celular/WhatsApp confirmado). Preencher `Status = Fila`, WhatsApp só dígitos, e uma coluna que marque nicho = "autopeças" (conferir o nome exato da coluna na planilha real antes de escrever).
2. **Editar o nó `Preparar Rodada`** do workflow `qVgwvD3ZW9COqdMA` pra escolher o conjunto de templates certo por nicho: se a linha for autopeças, usar os templates da Linha A abaixo (não os templates antigos de "atendimento" que já existem pra clínica/advocacia).
3. Confirmar que o jsCode do nó já reflete **20/dia por chip** e o par de chips **Comercial + cobaia** (a correção de cap/chip foi feita no doc geral em 03/09 — conferir se o código do nó já bate com isso ou se ainda está com o valor antigo de 6/dia só-cobaia).
4. Restart do n8n depois de qualquer edição (skill `restart-n8n`), senão não pega.

## Templates da 1ª abordagem — Linha A / Kronos Operação (girando)

Mesma lógica de rotação dos templates de atendimento (nunca texto idêntico), mas sem nenhuma menção a WhatsApp/chatbot/atendimento — é outro produto.

1. "Olá, {empresa}! 👋 Sou o Allan, da Kronos Intelligence. Construí um agente de IA que cuida do estoque de loja de autopeças — avisa quando uma peça tá acabando, compara fornecedor e mostra o que virou capital parado, tudo sozinho, todo dia. Posso te mostrar rapidinho como funciona?"
2. "Oi, tudo bem? Falo com {empresa}? Trabalho com IA aplicada a negócio local aqui na região de Campinas. Pra loja de autopeças, monto um agente que confere estoque, pesquisa fornecedor e avisa antes de faltar peça — sem você precisar lembrar de checar. Quer ver como funciona?"
3. "Olá! Aqui é o Allan, da Kronos Intelligence. Ajudo loja de autopeças a não perder venda por ruptura de estoque nem deixar capital parado: um agente de IA cuida disso sozinho, todo dia, e nunca compra nada sem sua aprovação. Se fizer sentido, te mostro em 2 minutos. Posso?"
4. "Oi, {empresa}! Vi o trabalho de vocês aí em {cidade}. Construí um agente de IA pra loja de autopeças — confere estoque, compara fornecedor, avisa antes do problema. Topa ver uma demonstração rápida?"

Follow-up (único, 4+ dias sem resposta): "Oi! Passando só pra saber se você chegou a ver minha mensagem 🙂 Se quiser, te mostro o agente cuidando do estoque funcionando — leva 2 minutos. Se não for o momento, sem problema nenhum, é só me dizer."

## Guardrails que continuam valendo (não mudam por ser outro nicho)

- Nunca mandar o Protótipo disparar (fora do rodízio, automação própria rodando).
- Sem link na 1ª mensagem fria.
- Robô manda e para — nunca responde sozinho.
- Se o chip banir: perda aceita, nunca burlar.
- 20/dia é o teto **por chip**, contando tudo que o chip disparar naquele dia — se Comercial/cobaia já estiverem rodando prospecção de clínica/advocacia, autopeças **divide** a cota do dia, não soma em cima.
