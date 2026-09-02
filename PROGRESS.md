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
Wed Sep  2 17:44:14 UTC 2026
Wed Sep  2 17:56:29 UTC 2026
Wed Sep  2 18:02:19 UTC 2026
Wed Sep  2 18:26:12 UTC 2026
Wed Sep  2 18:58:15 UTC 2026
Wed Sep  2 19:45:05 UTC 2026
Wed Sep  2 19:53:09 UTC 2026
Wed Sep  2 20:20:02 UTC 2026
