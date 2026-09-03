# Autopeças — Agente Operacional Inteligente para Negócios (Linha A)

**Nome oficial da Linha A, decidido em 2026-09-02: "Agente Operacional Inteligente para Negócios."** É a chamada principal do serviço novo da Kronos: implantação de IA sob medida dentro de empresa, com segurança por design, em vez de bot de atendimento (Linha B, já comoditizada pelo Meta).

**Status (2026-09-03): preço fechado, site implementado e NO AR.** Preço oficial em `00_Empresa_Kronos/06_Tabela_Precos/tabela_precos.md`. Aba "Autopeças (Kronos Operação)" está em produção em `07_Recursos/index.html` — primeira aba de `#segmentos`, com o terminal animado e os 3 planos em `#planos`. Deploy confirmado (scp 162723 bytes idênticos ao local, smoke test HTTP 200 — ver `PROGRESS.md`). Falta só a abordagem de uma loja real (leads em `LEADS.md`, imagem estática pronta em `demo/kronos-operacao-demo.png`).

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

## Próximos passos reais (não mais desenho)

1. Ver `PROVEDORES.md` — comparação de provedores de NF-e, folha/RH e base TecDoc já pesquisada.
2. Diagnóstico com uma loja real: qual PDV/ERP ela usa, e se ele tem API.
3. **Decidir a base de hospedagem do painel** — reaproveitar `14_Kronos_SaaS/app` (já lê KPIs de planilha e tem visão cliente + cockpit Kronos) ou construir novo, com banco isolado por cliente. Isso é pré-requisito pro piloto agora que o modelo é SaaS hospedado, não só o prototipo local que já existe.
4. Construir a Fase 1 (Estoque + Fornecedores) sobre essa base.
