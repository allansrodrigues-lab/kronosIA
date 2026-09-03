# Autopeças — Agente Operacional Inteligente para Negócios (Linha A)

**Nome oficial da Linha A, decidido em 2026-09-02: "Agente Operacional Inteligente para Negócios."** É a chamada principal do serviço novo da Kronos: implantação de IA sob medida dentro de empresa, com segurança por design, em vez de bot de atendimento (Linha B, já comoditizada pelo Meta).

**Status: desenho fechado, execução não iniciada** (fora o protótipo em `mvp/`, que já roda com dado fictício, e o rascunho de demo em `demo/`, já aprovado na direção).

Histórico completo da decisão está em `00_Empresa_Kronos/12_Backlog_Ideias_Servicos/backlog.md` — este README consolida o desenho já fechado como ponto de partida do projeto.

## O que é

Não é um chatbot de atendimento a cliente. É um **conjunto de agentes de IA rodando local, na máquina da loja física de autopeças**, que fica **por cima do PDV/ERP que a loja já usa** (Bling, Tiny, Omie ou sistema local) — lê os dados de lá, nunca substitui o sistema de venda.

## Perfil do cliente-alvo

Loja física de autopeças, sem TI própria, que já tem algum PDV/ERP. Dado sensível central: margem/custo de fornecedor.

## Os 8 agentes (ordem de construção em 5 fases)

| Fase | Agente | Autonomia | Risco/observação |
|---|---|---|---|
| 1 | **Orquestrador** | — | Aciona o agente certo pra cada demanda, mesmo padrão da Aurora (bots), virado pra dentro da empresa |
| 1 | **Estoque** | 🟢 lê/calcula/alerta | Detecta ruptura, capital parado, validade |
| 1 | **Fornecedores** | 🔴 nunca compra sozinho | Original × paralela × similar — preço não decide sozinho |
| 2 | **Transcrição por foto** | 🟡 confiança baixa → pergunta ao balconista | Depende de base de referência cruzada (TecDoc) |
| 2 | **Vendas** | 🟢 análise/sugestão · 🟡 oferta direta exige opt-in LGPD | Histórico por cliente + cross-sell |
| 3 | **Marketing/Conteúdo** | 🟡 revisão humana antes de publicar | Foto/vídeo/post técnico ("tem pro seu carro") |
| 4 | **Financeiro** | 🟢 registra/projeta · 🔴 nunca paga sozinho | Dado mais sensível dos 8 |
| 5 | **Fiscal** | 🟢 concilia/alerta · 🟡 sugere classificação NCM/CFOP | Não reinventa emissão — ERP já emite via provedor de NF-e |
| 5 | **RH** | 🟡 prepara rascunho, dono/contador confirma | Nunca calcula folha final sozinho — LGPD trabalhista |

## Stack

| Camada | Escolha |
|---|---|
| Onde roda | Máquina da loja — dado não sai de lá |
| Dados | SQLite local, exporta pra planilha quando o dono quiser ver |
| Raciocínio | Claude + Skill de autopeças |
| Ferramentas | MCP por domínio (banco, pasta de fotos, busca web, API de ERP/marketplace) |
| Agendamento | Tarefa agendada do SO ou n8n local — Fase 1 talvez nem precise de n8n/Docker |

## Princípio de segurança central

Cada agente só acessa o dado do próprio domínio (menor privilégio) — Marketing não lê financeiro, Compras não toca em RH. Nenhuma ação irreversível (comprar, publicar, emitir nota, pagar) roda sem aprovação humana na Fase 1.

## Próximos passos reais (não mais desenho)

1. Ver `PROVEDORES.md` — comparação de provedores de NF-e, folha/RH e base TecDoc já pesquisada.
2. Diagnóstico com uma loja real: qual PDV/ERP ela usa, e se ele tem API.
3. Construir a Fase 1 (Estoque + Fornecedores).
