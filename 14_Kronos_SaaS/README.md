# Kronos SaaS — Painel (conceito + planta)

> Decisão 03/07/2026: a Kronos vai nascer com **arquitetura SaaS desde já** (não é mais "médio prazo").
> O CLT do Allan banca as plataformas; os 1º–5º clientes são encarados como investimento; há reserva guardada.
> Mockup do painel **aprovado pelo Allan em 04/07** ("gostei"). Este README é a planta que a sessão Fable usa pra codar.

## Modelo de negócio — "pagou/usou, suspendeu/suspende"
SaaS de baixa burocracia e pouco contato preso (casa com a meta de ser nômade digital):
- **Cobrança recorrente automática** (Mercado Pago/Stripe): pagou → ativa; falhou o pagamento → **suspende sozinho**.
- **Self-service**: o cliente liga/desliga serviços no painel, sem falar com ninguém.
- **Contato humano só no toque inicial** (que é justamente onde o WhatsApp do cliente é vinculado no QR — o único passo não-automatizável hoje). Depois: e-mail/mensagem, presencial só quando raro.

## Duas visões (mockup: `mockup_painel.html`)

### Visão 1 — Painel do CLIENTE (o cockpit do negócio dele)
Transforma o bot de *gasto* em *investimento provado* → argumento de renovação.
- **KPIs**: atendimentos no mês · quantos viraram agendamento · tempo médio de resposta · **"o bot já se pagou X×"** (o número que segura o cliente).
- **Serviços com liga/desliga** (self-service): Atendimento 24h, Agendamento, Lembrete D-1, Áudio, Parecer científico, Pós-venda.
- **Estado de pagamento**: próxima cobrança, valor, método.
- **Status da conta**: Ativo / Pgto falhou / Suspenso.

### Visão 2 — Painel INTERNO da Kronos (cockpit do Allan)
- **KPIs da Kronos**: MRR, clientes ativos, inadimplentes, suspensos. (Evoluir p/ CAC, LTV, churn.)
- **Lista de clientes**: nome, nicho, MRR, status — com o modelo pagou/usou/suspende visível nos badges.
- Ações: provisionar / suspender / reativar (automático conforme pagamento).

## Camadas de construção (entregar em fatias finas, cada uma já demonstrável)
1. ✅ **Mockup visual** (04/07 — parte suave, sem Fable).
2. ✅ **1 tela real com KPIs do Sheets** (04/07, sessão Fable) — **`app/`**: servidor Node+TypeScript (Express)
   lendo os 2 CRMs reais via service account e servindo o painel em `http://localhost:4600`.
   Validado com dados reais: Aurora 298 atendimentos · Schalletti com as interações do teste ao vivo ·
   Ferraz 3 agendamentos. Como rodar/evoluir: skill **`kronos-saas`**.
3. ✅ **Login + visão por papel** (04/07) — senha scrypt + sessão em cookie HMAC (zero dependência nova,
   `src/auth.ts`). **Admin** (Allan) vê o cockpit inteiro; **cada cliente** loga e vê SÓ o painel dele
   (sem MRR, sem os outros — a blindagem por cliente vale também na tela). Usuários em `app/users.json`
   (FORA do git; modelo em `users.example.json`; gerar hash: `node dist/hashpass.js <senha>`).
   Testado: 401 sem login/senha errada, filtro por papel, logout. Telas: `/login.html` + redirect automático.
4. ⏭️ **Multi-cliente formal** — a config `app/clients.json` já é multi-tenant (1 entrada por cliente, CRM isolado).
5. **Billing** (Mercado Pago assinatura → pagou/ativa, falhou/suspende sozinho) + deploy no VPS.

## Stack (decidida na fatia 2)
- **Node + TypeScript + Express** — o TS do Módulo 1 virando produto real. Zero framework de front (HTML+JS vanilla, paleta navy do mockup).
- **google-auth-library** (JWT do service account) + REST `values:batchGet` — leve, sem googleapis gigante.
- Roda local agora; depois no **VPS que já existe**. Dados: Google Sheets/CRM atual; banco próprio só quando precisar.
- Billing futuro: Mercado Pago (já há IDs de plano).
- 🔌 **MCP**: deliberadamente adiado — hoje o painel só LÊ o que o MCP google-sheets já lê (seria duplicação). Vira MCP de verdade na fatia 5, quando ganhar AÇÕES próprias (ativar/suspender cliente, provisionar).

## Como construir (regras de sessão)
- **Build pesado = Fable 5** (comprar crédito antes; não começar no Sonnet pra não travar no meio).
- Fatias finas: nunca "sumir semanas e voltar com tudo pronto" — cada camada tem que poder ser mostrada/vendida.
- Ao fim de cada sessão Fable: gravar memória + atualizar este README.

Relacionado (memória): `kronos-dashboard-saas`, `estrategia-modelos-fable-sonnet`, `proximos-passos`.
