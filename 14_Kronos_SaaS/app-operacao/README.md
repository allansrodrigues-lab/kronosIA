# Kronos Operação — Painel (autopeças)

Painel hospedado do serviço novo (Linha A — Kronos Operação), separado do painel de
atendimento (`14_Kronos_SaaS/app`, Linha B). Decisão de arquitetura em
`20_AutoPecas/README.md` e `00_Empresa_Kronos/12_Backlog_Ideias_Servicos/backlog.md`
(pivot local→SaaS hospedado, 2026-09-03).

## O que foi reaproveitado do painel de atendimento

- **`src/auth.ts`** — copiado sem alteração nenhuma. Login com senha (scrypt+salt) e
  sessão assinada por HMAC num cookie HttpOnly. Zero dependência nova.
- **`src/hashpass.ts`** — copiado sem alteração. Gera salt+hash pra colocar em `users.json`.
- **Padrão de isolamento por cliente** — mesmo modelo (`clientId` na sessão, role
  `admin` vê tudo, role `client` só o próprio painel). O que muda é o que cada
  `client` isola: lá é aba de planilha, aqui é **arquivo SQLite próprio**
  (`clients.json` → `dbPath`), o que é isolamento mais forte (nem fica na mesma
  planilha física).

## O que é novo (não existia)

- **`src/estoque.ts`** — substitui o `kpis.ts` do painel de atendimento. Lê o SQLite
  da loja via `node:sqlite` (nativo do Node 22+, sem dependência extra) e calcula
  ruptura + capital parado — é a mesma lógica de `20_AutoPecas/mvp/agente_estoque.py`
  portada pra TypeScript (validada: bate exatamente com a saída do protótipo Python —
  6 itens em ruptura, R$ 1.164,00 de capital parado nos dados fictícios).
- **`public/index.html`** — tela nova: lista de peças em ruptura com comparação de
  fornecedor (principal ✅ + alternativos), lista de capital parado, nota "o Agente
  não compra sozinho" (nenhuma ação de compra existe ainda — é só leitura).
- **`clients.json`** — 1 cliente piloto fictício, "Auto e Moto Peças Ouro Verde"
  (nome real de um lead levantado em `20_AutoPecas/LEADS.md`, usado só como
  identidade de demonstração — dado de estoque é fictício, do protótipo).

## Como rodar local

```bash
cd 14_Kronos_SaaS/app-operacao
npm install
npx tsc
node dist/hashpass.js "sua-senha"   # gera salt+hash
# cole o resultado em users.json (copiar de users.example.json, users.json NÃO vai pro git)
node dist/server.js                 # sobe em http://localhost:4700
```

Testado (2026-09-03): login admin/cliente funcionando, endpoint `/api/overview`
retornando ruptura e capital parado corretos, isolamento confirmado (role `client`
recebe `totals: null` e só o próprio `clientId`; sem cookie ou senha errada → 401).

## O que falta pra virar produto de verdade

1. **Dado real** — hoje só existe o cliente fictício `ouro-verde`. Onboardar o
   1º cliente pagante = criar o SQLite dele (schema de `seed_dados_ficticios.py`)
   a partir de export do PDV/ERP real, apontar `clients.json` pro arquivo dele.
2. **Deploy** — roda só local por enquanto (porta 4700). Falta subir no VPS
   (mesmo padrão do painel de atendimento, ver `14_Kronos_SaaS/deploy/`) com
   domínio/subdomínio próprio, por trás do Traefik.
3. **Ações de aprovação** — hoje o painel só mostra as opções de fornecedor; o
   botão "aprovar pedido" que aparece na demo do site (`20_AutoPecas/demo/`)
   ainda não existe aqui. Próxima fatia.
4. **Billing** — como no painel de atendimento, cobrança automática (Mercado
   Pago) ainda não existe; hoje é cadastro manual.
5. Sincronizar preço/plano do cliente com a tabela oficial
   (`00_Empresa_Kronos/06_Tabela_Precos/tabela_precos.md`) quando o 1º cliente
   fechar de verdade.
