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

---

## Checkpoint (2026-09-03, antes de clear por contexto alto)

**Autopeças/Kronos Operação:**
- Captação #2 feita: 40 lojas (Pedreira e região), triagem de 5 candidatas + 5 rascunhos de mensagem de diagnóstico prontos em `20_AutoPecas/LEADS.md` — nenhuma contatada ainda.
- Checagem de WhatsApp dos 5 números **não deu pra fazer** (sessão remota sem navegador local) — Allan precisa checar manualmente ou ligar direto nos 4 números fixos.
- **Pivot de arquitetura decidido:** Kronos Operação vira SaaS hospedado (não mais "roda local"). Site, README, tabela de preços e demo já corrigidos e no ar. **Falta construir de verdade** a infra multi-tenant — hoje só existe o protótipo local (SQLite). Próxima decisão: reaproveitar `14_Kronos_SaaS/app` ou construir painel novo com banco isolado por cliente.

**Site/redesign:**
- Allan quer separar o site em 2 páginas (Agente de Atendimento / Agente Operacional) e deixar visual mais profissional — só mantém o fundo geométrico + azul da Kronos, resto muda. **Por enquanto continuar editando o site atual como está**, redesign fica pra depois.
- Achado: plugin oficial `frontend-design` (Anthropic, repo `anthropics/claude-code`) resolve "cara de IA genérica" — não instalado nessa sessão, instalar via `/plugin` quando for a hora do redesign.

**Pergunta em aberto do Allan (não respondida ainda no momento do clear):** se é cedo pra criar uma skill/MCP própria da Kronos (formalizar como MCP/skill) pro Agente Operacional, ou se deveria ir direto pra versão mais completa/"extraordinária". Recomendação a dar na próxima sessão: **é cedo** — a stack de MCP por domínio (ver `20_AutoPecas/README.md`) só compensa formalizar depois de validar manualmente com 1 loja piloto real; construir MCP/skill antes de ter cliente usando é risco de over-engineering.

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
