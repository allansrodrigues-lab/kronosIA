# Autopeças — Agente Operacional Inteligente para Negócios (Linha A)

**Nome oficial da Linha A, decidido em 2026-09-02: "Agente Operacional Inteligente para Negócios."** É a chamada principal do serviço novo da Kronos: implantação de IA sob medida dentro de empresa, com segurança por design, em vez de bot de atendimento (Linha B, já comoditizada pelo Meta).

**Status (2026-09-03): preço fechado, site no ar, painel hospedado NO AR.** Preço oficial em `00_Empresa_Kronos/06_Tabela_Precos/tabela_precos.md`. Aba "Autopeças (Kronos Operação)" em produção em `07_Recursos/index.html`. Painel real em `14_Kronos_SaaS/app-operacao/` — login + isolamento por cliente + ruptura/capital parado calculados do SQLite, testado e batendo com o protótipo Python (ver seção "Painel hospedado" abaixo). Falta: deploy do painel no VPS e abordagem de uma loja real (leads em `LEADS.md`, triagem + rascunho de mensagem prontos).

Histórico completo da decisão está em `00_Empresa_Kronos/12_Backlog_Ideias_Servicos/backlog.md` — este README consolida o desenho já fechado como ponto de partida do projeto.

## O que é

Não é um chatbot de atendimento a cliente. É um **conjunto de agentes de IA hospedado na nuvem da Kronos, com painel próprio por loja**, que fica **por cima do PDV/ERP que a loja já usa** (Bling, Tiny, Omie ou sistema local) — lê os dados de lá, nunca substitui o sistema de venda. O dono acessa o painel por login, de qualquer lugar (celular, outro computador) — mesmo princípio de isolamento por cliente já usado na Linha B (regra-mãe: cada cliente nasce isolado, nunca base compartilhada), aplicado agora a um ambiente/banco próprio por loja em vez de instância Evolution.

**Decisão 2026-09-03:** o desenho original (Fase 1, ver histórico no backlog) previa rodar 100% local, sem custo de servidor pra Kronos. O Allan optou por hospedar (SaaS completo) pra o dono acompanhar de qualquer lugar, não só do computador da loja — isso muda a regra 4 da tabela de preços (ver `tabela_precos.md`) e implica montar infraestrutura multi-tenant (painel + banco isolado por cliente), reaproveitando possivelmente `14_Kronos_SaaS/app` como base.

## Perfil do cliente-alvo

Loja física de autopeças, sem TI própria, que já tem algum PDV/ERP. Dado sensível central: margem/custo de fornecedor.

## Os 9 agentes (ordem de construção em 5 fases)

| Fase | Agente | Autonomia | Risco/observação |
|---|---|---|---|
| 1 | **Orquestrador** | — | Aciona o agente certo pra cada demanda, mesmo padrão da Aurora (bots), virado pra dentro da empresa |
| 1 | **Estoque** | 🟢 lê/calcula/alerta | Detecta ruptura, capital parado, validade |
| 1 | **Fornecedores** | 🔴 nunca compra sozinho | Original × paralela × similar — preço não decide sozinho |
| 2 | **Transcrição por foto** | 🟡 confiança baixa → pergunta ao balconista | Depende de base de referência cruzada (TecDoc) |
| 2 | **Vendas** | 🟢 análise/sugestão · 🟡 oferta direta exige opt-in LGPD | Histórico por cliente + cross-sell |
| 3 | **Marketing/Conteúdo** | 🟡 revisão humana antes de publicar | Foto/vídeo/post técnico ("tem pro seu carro") |
| 3 | **Relatório/Gestão** | 🟢 leitura agregada | Resumo semanal juntando dado dos outros agentes — mesmo padrão do "Relatório Automático" da Linha B |
| 4 | **Financeiro** | 🟢 registra/projeta · 🔴 nunca paga sozinho | Dado mais sensível dos 9 |
| 5 | **Fiscal** | 🟢 concilia/alerta · 🟡 sugere classificação NCM/CFOP | Não reinventa emissão — ERP já emite via provedor de NF-e |
| 5 | **RH** | 🟡 prepara rascunho, dono/contador confirma | Nunca calcula folha final sozinho — LGPD trabalhista |

**Jurídico não é um agente da lista.** Parecer jurídico é ato privativo de advogado (OAB) — não dá pra automatizar nem integrar com "provedor homologado" igual NF-e. A Kronos **conecta a loja com a Léa** (Linha B, Advocacia), que já faz triagem pra escritório real.

## Stack

| Camada | Escolha |
|---|---|
| Onde roda | Nuvem Kronos — painel próprio por loja, login individual, banco isolado (nunca compartilhado entre clientes) |
| Dados | Banco isolado por cliente (a definir: Postgres com schema/linha própria por loja, seguindo a regra-mãe de isolamento já usada na Linha B) |
| Raciocínio | Claude + Skill de autopeças |
| Ferramentas | MCP por domínio (banco, pasta de fotos, busca web, API de ERP/marketplace) |
| Agendamento | Job agendado no servidor da Kronos (n8n ou cron), por cliente |

## Princípio de segurança central

Cada agente só acessa o dado do próprio domínio (menor privilégio) — Marketing não lê financeiro, Compras não toca em RH. Nenhuma ação irreversível (comprar, publicar, emitir nota, pagar) roda sem aprovação humana na Fase 1. **Isolamento por cliente é obrigatório** (regra-mãe já usada na Linha B, agora aplicada ao SaaS hospedado): cada loja tem seu próprio banco/ambiente, nunca uma tabela compartilhada entre clientes — vazamento de margem/fornecedor de um cliente pra outro é o pior cenário possível nesse produto.

## Painel hospedado — NO AR (2026-09-03)

**`14_Kronos_SaaS/app-operacao/` existe, roda de verdade e está publicado.** Reaproveita
login e isolamento por cliente do painel de atendimento (`auth.ts`/`hashpass.ts`
copiados sem alteração); a fonte de dado é SQLite por loja (`node:sqlite`, nativo do
Node, zero dependência nova) em vez de Google Sheets. Testado: login admin + login de
loja (isolamento confirmado — role `client` não vê MRR nem dado de outra loja), ruptura
e capital parado batendo exatamente com o protótipo Python (`mvp/agente_estoque.py`) —
6 itens em ruptura, R$ 1.164,00 de capital parado nos dados fictícios do cliente piloto
`ouro-verde`. **No ar em `https://kronosintelligence.com.br/operacao`** (deploy manual
via Docker+Traefik, confirmado HTTP 200 pelo Allan). Ver
`14_Kronos_SaaS/app-operacao/README.md` pro que falta (ações de aprovação, billing,
dado real de cliente).

## Próximos passos reais

1. Ver `PROVEDORES.md` — comparação de provedores de NF-e, folha/RH e base TecDoc já pesquisada.
2. Diagnóstico com uma loja real: qual PDV/ERP ela usa, e se ele tem API.
3. **Ativar o rodízio de disparo pra autopeças** — ver `prospeccao_robo_disparador.md` (templates
   Linha A prontos, mas precisa de sessão local com MCP n8n/Sheets pra abastecer a fila e ajustar
   o disparador; esta sessão remota não tem esse acesso).
4. Abordar leads reais (`LEADS.md` — 88 lojas levantadas em 3 captações, 20/40 da Captação #3
   já com mensagem personalizada) e onboardar o 1º cliente pagante: trocar o SQLite fictício
   por um real, a partir de export do PDV/ERP dele.
