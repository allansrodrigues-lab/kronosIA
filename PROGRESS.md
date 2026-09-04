# PROGRESS

Checkpoint de sessão. O hook `SessionEnd` (`.claude/settings.json`) carimba a data aqui
e commita o que já está rastreado, para que uma sessão interrompida não custe contexto.
Atualizar **ao fim de cada fase**, sem esperar o Allan pedir.

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
