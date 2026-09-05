# PROGRESS

Checkpoint de sessão. O hook `SessionEnd` (`.claude/settings.json`) carimba a data aqui
e commita o que já está rastreado, para que uma sessão interrompida não custe contexto.
Atualizar **ao fim de cada fase**, sem esperar o Allan pedir.

---

## Checkpoint (2026-09-04/05, antes de clear — robô de autopeças ativo + 1º lead quente em conversa)

**MCPs locais configurados (finalmente):** n8n e google-sheets nunca tinham sido registrados no `~/.claude.json` desta máquina — não era bug, é que nunca foram adicionados. Corrigido: `n8n-mcp` (npm) apontando pra `n8n.kronosintelligence.com.br` com API key nova (a primeira vazou num print e foi revogada/trocada), e `mcp-google-sheets` trocado de `npx -y` (lento, estourava timeout de 60s) pro binário Python já instalado via `uv tool install` (`~/.local/bin/mcp-google-sheets.exe`) — conecta em <2s agora. Documentado pra próxima vez que sumir: skill `mcp-reload` (que na verdade não existe como skill formal ainda, só foi diagnosticado ad-hoc — considerar criar de verdade). Sessão nesta nuvem **não tem** esses MCPs (são locais) — pra mexer em n8n/Sheets sempre precisa da sessão local (Git Bash ou Claude Code Desktop, mesma engine, mesmo projeto).

**Rodízio de disparo corrigido e ativo:** o CLAUDE.md e a skill `kronos-prospeccao-robo` estavam desatualizados (diziam "só cobaia, 6/dia, Comercial nunca entra" — decisão de 10/07, superada). Corrigido pra bater com a decisão real de 24/07 + ajuste de 03/09: **Comercial (`comercial01`, 5519971266736) + cobaia (`prospeccao01`, 5519997237404) disparam, 20/dia cada, round-robin**; Protótipo fica de fora (já roda automação própria, sob risco). O Comercial já existia pareado desde 29/07 (o próprio Allan tinha feito, ninguém lembrava) — só faltou configurar o webhook. Workflow `qVgwvD3ZW9COqdMA` reescrito: checagem dupla de chip online, cap de verdade por chip (coluna `Chip` nova na aba `Prospeccao`), templates da Linha A (estoque/ruptura/fornecedor, sem linguagem de atendimento) só pra `Segmento=Autopecas`. Validado (`n8n_validate_workflow` 0 erros), n8n reiniciado, confirmado `active: true` com os dois chips `open`.

**Alerta de fila baixa testado de verdade:** dispara todo dia 8h se `Status=Fila` cair abaixo de 5 (mensagem real chegou no WhatsApp Kronos, teste forçado manualmente via Evolution API).

**Captação #3 (autopeças) inteira na fila:** as 20 primeiras (linhas 203-222) foram escritas e confirmadas por releitura direta. As 20 restantes (21-40, lista completa em `20_AutoPecas/LEADS.md` linhas 201-220) foram **pedidas** pro Allan escrever via sessão local — **não tenho confirmação de que entraram**, checar no início da próxima sessão (`get_sheet_data` na aba `Prospeccao`, deveria ter 242 linhas incluindo cabeçalho se deu certo).

**1º lead quente em conversa real:** Dorival, **Autopeças Romaninho** (Americana, 5519997551007) respondeu "Boa noite" → "Sim pode ser" ao pedido de demo. Enviei a demo (`20_AutoPecas/demo/kronos-operacao-demo.png`) e uma mensagem detalhada com preço real da tabela (`00_Empresa_Kronos/06_Tabela_Precos/tabela_precos.md` — Piloto Operacional: R$1.500 implantação + R$397/mês, framing de "valor de piloto"), deixando claro que o "R$1.164 de capital parado" é exemplo de dado fictício do protótipo, não número dele. Pergunta em aberto pra ele: qual sistema usa (Bling/Tiny/planilha) — resposta vira o diagnóstico real. Estado: mensagem visualizada, aguardando resposta. **Pendente:** Allan pediu pra atualizar `Observacoes` da linha do Romaninho na planilha com esse resumo — comando dado, não confirmado que rodou.

**Decisão tomada:** não construir os Níveis 2/3 (Transcrição por foto, Vendas, Marketing, Relatório, Financeiro, Fiscal, RH — nenhum tem código, só preço na tabela) até validar o Nível 1 com um cliente pagante real. Nível 1 (Estoque+Fornecedores, painel real em `14_Kronos_SaaS/app-operacao/`) já foi precificado pra se justificar sozinho pela dor de capital parado/ruptura — não depende dos outros agentes.

**Rotina de captação semanal (só nesta sessão nuvem):** criei um cron (`CronCreate`, job `b934776b`, dia 1/8/15/22/29 ~9h) pra levantar mais 20 leads de autopeças quando a fila esvaziar. ⚠️ **É session-only — se essa sessão terminar (o que um `/clear` provavelmente causa), o job some.** Se o Allan pedir "bora prospectar autopeças" numa sessão nova e nada tiver rodado sozinho, é por isso — recriar o cron ou fazer sob demanda.

**Allan sinalizou fricção com a sessão local (Git Bash) e cogitou configurar os mesmos MCPs nesta sessão nuvem também.** Orientação dada: não colar credencial no chat (já vazou uma vez); ele precisaria configurar `N8N_BASE_URL`/`N8N_API_KEY` (key nova, separada da local) e o JSON da service account como variáveis de ambiente do *ambiente* do Claude Code on the web (fora desta conversa), e essa sessão nuvem operaria via chamada HTTP direta (curl/script), não MCP formal. Ainda não decidido/feito.

---

## Build atual — aplicar recomendações do `/insights` (26/07/2026)

| # | Fase | Status | Arquivos tocados |
|---|---|---|---|
| 1 | Regras de navegador + verificação no CLAUDE.md | ✅ feito | `CLAUDE.md` |
| 2 | Protocolo de build de nicho + Deploy + Segurança no CLAUDE.md | ✅ feito | `CLAUDE.md` |
| 3 | Skill `/radar` (varredura de vagas e freelas) | ✅ feito | `.claude/skills/radar/SKILL.md` |
| 4 | Skill `/deploy` incrementada (teto 3 min, grep no ar, PROGRESS.md) | ✅ feito | `.claude/skills/deploy/SKILL.md` |
| 5 | Hooks: line endings + snapshot de sessão | ✅ feito | `.claude/settings.json`, `.claude/hooks/fix_line_endings.py` |
| 6 | Radar headless (`claude -p` em script) | ✅ feito | `scripts/radar_headless.sh` |
| 7 | MCPs gsheets/github | ⏭️ dispensado | — já conectados; `claude mcp add` duplicaria |
| 8 | Pesquisa de nicho via subagente | ⏸️ aguardando | — nicho não definido; Allan dispensou a pergunta |

### Detalhe das fases

**Fase 1–2 — CLAUDE.md.** Cinco seções novas em português: `Regras de automação de navegador`,
`Verificação antes de afirmar "pronto"`, `Protocolo de build de nicho (Kronos)`, `Deploy / Infra`
(incrementada, não duplicada) e `Segurança e dados sensíveis`. O comando `scp` inline saiu do
`deploy.yml` real (`root@2.24.101.180:/opt/kronos-site/index.html`), não foi inventado.
A regra de chip foi reescrita: o rascunho dizia "chip OdontoVita intocável", o que contradiz
a liberação dos 3 chips de 24/07 — virou "nunca disparar de número não declarado liberado".

**Fase 5 — hooks.** `git add -A` do rascunho virou `git add -u` (decisão do Allan): repo é
público e `-A` arrastaria `18_Kronos_Voce/`, `19_Projeto2_Robo_Humanoide/`, `qphotorec.log` e
`contatos_teste_v2.csv` para o histórico. O hook de line endings mira só o arquivo editado
(lido do stdin) em vez de varrer o projeto — `jq` não existe nesta máquina, então é Python.

**Fase 6 — radar headless.** Ver `scripts/radar_headless.sh`. Notifica só acima do limiar.

### Próxima ação exata

Rodar `bash scripts/radar_headless.sh --dry-run` para conferir a saída antes de agendar
na tarefa diária. Nada mais está bloqueado.

---

## Log de deploy

2026-09-03 — deploy landing via CI (`main` @ `12f559f`) — nova aba "Autopeças (Kronos Operação)" em #segmentos + preço da Linha A em #planos — verificado no ar: scp copiou 162723 bytes (idêntico ao local), smoke test HTTP 200.

2026-09-03 — deploy landing via CI (`main` @ `d8206c3`) — 9º agente (Relatório/Gestão) na Operação Completa + ponte jurídica com a Léa (nota no site, sem preço próprio) — verificado no ar: scp copiou 163826 bytes (idêntico ao local), smoke test HTTP 200.

2026-09-03 — deploy landing via CI (`main` @ `3e3428e`) — pivot local→SaaS hospedado (Kronos Operação): textos "roda local"/"no seu computador" trocados por "painel próprio na nuvem, isolamento por cliente" — scp e smoke test HTTP 200 passaram (run 33771698819); job geral marcou `failure` só porque a etapa "Notificar deploy" (webhook pro n8n) segue quebrada, problema pré-existente e não-bloqueante já registrado no CLAUDE.md.

2026-09-03 — **primeiro deploy do painel Kronos Operação** (`14_Kronos_SaaS/app-operacao/`), manual via `deploy.sh` no VPS (Docker + Traefik, mesmo padrão do painel de atendimento — container `kronos-operacao`, imagem `node:22-alpine`, subcaminho `/operacao`, sem porta exposta). Executado pelo Allan no Git Bash local (esta sessão remota não tem ssh/scp). Verificado no ar pelo próprio Allan: `curl .../operacao/login.html` → HTTP 200. Login testado com credenciais reais (senha aleatória de 16 caracteres, gerada nesta sessão, nunca commitada).

---

## Checkpoint (2026-09-03, antes de clear — painel Kronos Operação NO AR e confirmado)

**Autopeças/Kronos Operação — estado atual, tudo pronto pra prospectar:**
- **Painel real, hospedado, testado e confirmado funcionando:** https://kronosintelligence.com.br/operacao (`14_Kronos_SaaS/app-operacao/`, deploy Docker+Traefik, container `kronos-operacao`). Login confirmado pelo Allan com credenciais novas (senhas sem caracteres ambíguos, geradas nesta sessão, nunca commitadas — só o Allan tem). ⚠️ Não confundir com `/painel` (esse é o painel de atendimento, Linha B — outro sistema, outros usuários; já causou um "senha inválida" por engano de URL).
- **88 leads levantados** em `20_AutoPecas/LEADS.md` (3 captações): #1 (8, Campinas) e #2 (40, Pedreira/região — maioria telefone FIXO) e #3 (40, região ampliada DDD 19 — todos com CELULAR/WhatsApp confirmado na fonte, sem duplicata das anteriores).
- **Mensagem de prospecção completa** (o quê/como funciona/como acompanha) salva em `LEADS.md`, seção "Mensagem de prospecção (modelo)" — já **personalizada pras 5 primeiras** da Captação #3 (seção "Mensagens personalizadas — 5 primeiras da Captação #3"): Auto Peças Capuava (Valinhos), Autopeças Romaninho (Americana), Girley Suspensão (Americana), Auto Peças Europa (Sta. Bárbara D'Oeste — cuidado, tem outra com mesmo nome em Sta. Gertrudes), Garcia e Guedes Auto Peças (Nova Odessa). Faltam 35.
- Pivot de arquitetura (local→SaaS hospedado) está 100% concluído: decisão, docs, site e infra real, tudo consistente.

**Site/redesign (ainda não iniciado, fica pra depois):**
- Allan quer separar o site em 2 páginas (Agente de Atendimento / Agente Operacional) e deixar visual mais profissional — só mantém o fundo geométrico + azul da Kronos, resto muda. Continuar editando o site atual como está até ele sinalizar pra começar o redesign.
- Achado: plugin oficial `frontend-design` (Anthropic, repo `anthropics/claude-code`) resolve "cara de IA genérica" — não instalado nessa sessão, instalar via `/plugin` quando for a hora.

**Próxima ação real ("já pode prospectar" — instrução do Allan antes do clear):** ao retomar, seguir personalizando as mensagens das próximas lojas da Captação #3 (já tem 5/40 prontas) sem precisar perguntar de novo — ele quer continuidade automática nesse passo. **Continua valendo a regra-mãe: nunca enviar mensagem sozinho**, só preparar/personalizar; quem manda é o Allan pelo WhatsApp dele.

**Pergunta em aberto do Allan de sessão anterior, ainda não fechada:** se é cedo pra criar uma skill/MCP própria da Kronos pro Agente Operacional, ou ir direto pra versão completa. Recomendação registrada: é cedo — só formalizar depois de validar manualmente com 1 loja piloto real.

Wed Sep  2 17:44:14 UTC 2026
Wed Sep  2 17:56:29 UTC 2026
Wed Sep  2 18:02:19 UTC 2026
Wed Sep  2 18:26:12 UTC 2026
Wed Sep  2 18:58:15 UTC 2026
Wed Sep  2 19:45:05 UTC 2026
Wed Sep  2 19:53:09 UTC 2026
Wed Sep  2 20:20:02 UTC 2026
Wed Sep  2 20:29:37 UTC 2026
Wed Sep  2 20:35:30 UTC 2026
Wed Sep  2 20:45:28 UTC 2026
Wed Sep  2 20:51:23 UTC 2026
Wed Sep  2 21:12:15 UTC 2026
Wed Sep  2 21:42:22 UTC 2026
Wed Sep  2 21:45:36 UTC 2026
Wed Sep  2 21:52:45 UTC 2026
Wed Sep  2 21:53:19 UTC 2026
Wed Sep  2 21:58:15 UTC 2026
Thu Sep  3 01:04:27 UTC 2026
Thu Sep  3 01:26:36 UTC 2026
Thu Sep  3 01:56:33 UTC 2026
Thu Sep  3 02:09:46 UTC 2026
Thu Sep  3 02:18:38 UTC 2026
Thu Sep  3 02:37:50 UTC 2026
Thu Sep  3 02:45:30 UTC 2026
Thu Sep  3 03:32:04 UTC 2026
Thu Sep  3 06:11:59 UTC 2026
Thu Sep  3 07:34:36 UTC 2026
Thu Sep  3 07:55:17 UTC 2026
Thu Sep  3 13:36:47 UTC 2026
Thu Sep  3 14:13:22 UTC 2026
Thu Sep  3 14:26:30 UTC 2026
Thu Sep  3 14:36:48 UTC 2026
Thu Sep  3 15:29:07 UTC 2026
Thu Sep  3 17:55:56 UTC 2026
Thu Sep  3 18:01:31 UTC 2026
Thu Sep  3 18:10:25 UTC 2026
Thu Sep  3 18:34:07 UTC 2026
Thu Sep  3 19:00:13 UTC 2026
Thu Sep  3 19:10:04 UTC 2026
Thu Sep  3 19:17:04 UTC 2026
Thu Sep  3 19:52:43 UTC 2026
Thu Sep  3 20:26:57 UTC 2026
Thu Sep  3 20:32:20 UTC 2026
Thu Sep  3 20:58:22 UTC 2026
Thu Sep  3 21:15:12 UTC 2026
Thu Sep  3 21:21:04 UTC 2026
Fri Sep  4 17:20:43 UTC 2026
Fri Sep  4 17:34:17 UTC 2026
Fri Sep  4 17:39:22 UTC 2026
Fri Sep  4 17:47:55 UTC 2026
Fri Sep  4 17:59:55 UTC 2026
Fri Sep  4 18:11:56 UTC 2026
Fri Sep  4 18:29:26 UTC 2026
Fri Sep  4 18:37:27 UTC 2026
Fri Sep  4 18:50:41 UTC 2026
Fri Sep  4 19:01:08 UTC 2026
Fri Sep  4 19:44:57 UTC 2026
Fri Sep  4 20:15:41 UTC 2026
Fri Sep  4 20:41:48 UTC 2026
Fri Sep  4 21:39:31 UTC 2026
Fri Sep  4 23:10:12 UTC 2026
Sat Sep  5 03:09:05 UTC 2026
Sat Sep  5 03:15:12 UTC 2026
Sat Sep  5 13:10:52 UTC 2026
