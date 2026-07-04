---
name: kronos-saas
description: Operar e evoluir o painel SaaS da Kronos (14_Kronos_SaaS/app) — servidor TypeScript que lê KPIs reais do CRM (Google Sheets) e mostra a visão do cliente + o cockpit da Kronos. Use para rodar o painel, adicionar cliente novo, ajustar KPI/mensalidade, diagnosticar "erro ao ler o CRM", ou construir as próximas fatias (login, multi-cliente, billing). Gatilhos: "painel saas", "cockpit da kronos", "roda o painel", "adiciona cliente no painel", "kpis do cliente", "dashboard kronos", "fatia do saas".
---

# Kronos SaaS — painel de KPIs (fatia 2 construída em 04/07/2026)

Servidor **Node + TypeScript (Express)** em `14_Kronos_SaaS/app/` que lê os CRMs reais
(Google Sheets, via service account — a mesma conta-robô do n8n) e serve o painel navy
com **visão Kronos** (MRR, clientes, status) + **visão do cliente** (KPIs, serviços, últimas interações).
Mockup aprovado em `14_Kronos_SaaS/mockup_painel.html`; planta/roadmap no `14_Kronos_SaaS/README.md`.

## Rodar
```bash
cd "14_Kronos_SaaS/app"
npm install        # 1ª vez
npx tsc            # compila src/ -> dist/
node dist/server.js   # http://localhost:4600
```
- Também há config `saas` no `.claude/launch.json` (⚠️ o preview_start já mapeou errado uma vez — se cair no servidor errado, rodar `node dist/server.js` em background via Bash e navegar pra `http://localhost:4600`).
- Endpoints: `/api/overview` (tudo, cache 60s) · `/api/health`.

## Arquitetura (3 arquivos de src/)
- `sheets.ts` — auth JWT do service account + `batchGet` (1 chamada por planilha, economiza quota). Caminho da chave: env `KRONOS_SA_PATH`, default `C:/Users/Usuario/Downloads/kronos-ia-498605-3c56d6eafae9.json`. **Chave nunca vai pro git** (`credentials/` e `.env` no .gitignore).
- `kpis.ts` — calcula KPIs achando colunas **pelo NOME do cabeçalho** (não índice fixo): telefone|jid|contato, data|data_hora|timestamp, escalacao, mensagem|resposta, nome. Aguenta a variação entre nichos.
- `server.ts` — Express, static `public/`, agrupa clientes por spreadsheet pro batchGet, cache 60s em memória.

## Adicionar cliente novo
Editar `clients.json`: id, name, niche, icon (nome Tabler), plan, `monthlyFee` (alimenta o MRR),
`avgTicket`+`avgTicketLabel` (alimentam a estimativa "o bot já se pagou X×"), `spreadsheetId` (CRM
próprio do cliente — regra-mãe de isolamento), `tabs` (log/bookings/sessions/leads → nome real das abas)
e `services` (o que aparece com liga/desliga). Não precisa mexer em código; reiniciar o server.

## KPIs calculados (de onde vem cada um)
- **Atendimentos** (total e 30d) = linhas da aba `log` · **Contatos únicos** = telefones distintos no log
- **Agendamentos/visitas** = linhas da aba `bookings` · **Sessões ativas** = linhas da aba `sessions`
- **Escalações** = coluna Escalacao == SIM · **"Bot já se pagou X×"** = agendamentos × avgTicket ÷ monthlyFee (SEMPRE mostrar o asterisco de estimativa)
- Datas pt-BR "dd/mm/yyyy, hh:mm:ss" — o parse pega só a parte da data.

## Pegadinhas conhecidas (o extraordinário)
- **Sessoes_Ativas tem histórico GIGANTE na coluna E** — por isso `RANGE_BY_KIND.sessions = A1:D5000` (nunca ler a coluna E em massa, estoura payload).
- O classificador de auto mode **bloqueia ler o conteúdo dos JSON de credencial** — e não precisa: o app carrega a chave em runtime; eu só configuro o caminho.
- Preview do Claude pode reusar servidor errado (ver acima).
- Erros do front aparecem no banner "Erro ao ler o CRM: ..." — mensagem vem direto do server (500 JSON).

## Login (fatia 3 — 04/07)
- `src/auth.ts`: senha **scrypt** (salt+hash) + sessão em **cookie HMAC** (`ksess`, 7 dias, HttpOnly). Zero dependência nova; segredo auto-gerado em `.secret` (gitignored).
- Papéis: `admin` (cockpit completo) vs `client` (só o próprio painel — `/api/overview` filtra no SERVIDOR, não no front).
- Usuários em `users.json` (**gitignored** — repo público!); modelo `users.example.json`. Gerar hash de senha nova: `node dist/hashpass.js <senha>` → colar salt+hash no users.json.
- Rotas: `POST /api/login` `{user,pass}` · `POST /api/logout` · `GET /api/me`. Front redireciona pra `/login.html` em 401.
- Trocar senha = gerar novo hash e editar users.json (reinicia o server). Logins de demo criados em 04/07 — perguntar ao Allan antes de recriar.

## Fatias (roadmap — cada uma demonstrável sozinha)
1. ✅ Mockup (04/07) · 2. ✅ **Tela real com KPIs do Sheets (04/07)** · 3. ✅ **Login + visão por papel (04/07)** ·
4. ⏭️ Multi-cliente formal (a config já é multi-tenant) · 5. Billing (Mercado Pago assinatura → ativa/suspende sozinho) + deploy VPS.

Relacionado: memória `kronos-dashboard-saas` (visão/decisões), `14_Kronos_SaaS/README.md` (planta), skill `kronos-mcp` (ler o CRM via MCP pra conferir os números).
