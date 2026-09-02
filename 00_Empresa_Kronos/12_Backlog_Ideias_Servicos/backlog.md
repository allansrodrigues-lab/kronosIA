# Backlog de ideias de novo serviço

Ideias capturadas durante o pivot de serviço (ver `CLAUDE.md`) — ainda **não especificadas**, sem CRM, sem workflow. Servem pra não perder a ideia enquanto ela ainda está sendo garimpada (vídeo, conversa, prospecção). Quando uma ideia amadurecer o suficiente pra virar projeto, ela sai daqui e segue o **Protocolo de build de nicho** do `CLAUDE.md` (pesquisa → base de conhecimento → CRM → workflows → ...).

---

## 2026-09-02 — Automação de conteúdo + publicação em marketplace

**Origem:** vídeo no YouTube sobre mercado de IA (ideação livre). A Novaes Imóveis foi citada como referência de que já existiu procura por algo parecido — **não é o nicho escolhido, nicho segue em aberto.**

**O que seria:**
- Sistema que **cria conteúdo** (texto/imagem de post ou de anúncio de produto).
- **Posta automaticamente** em plataformas de venda — Mercado Livre, TikTok Shop (e possivelmente redes sociais).
- Usa **MCP + Skill** pra automatizar a postagem (mesmo padrão de automação que já usamos no Claude Code).
- Tem **checklist** de acompanhamento — o que já foi criado/postado, o que falta.
- Sincroniza/inclui item no **catálogo de vendas** do cliente.

**Por que encaixa no pivot:** em vez de bot de atendimento genérico, é "implementação de IA" que automatiza uma operação real dentro da empresa (conteúdo + vendas em marketplace) — puxa o mesmo know-how de agentes + integração que a Kronos já tem, só que a serviço de um caso de uso diferente do WhatsApp.

**Pesquisa de concorrência feita (2026-09-02) — Meli IA (meliia.com.br):**
- SaaS de cadastro em massa no Mercado Livre, só com API oficial (sem bot), integra com ERP (Bling/Tiny/Tray), humano revisa antes de publicar, cobra por anúncio publicado.
- Módulo **AutoParts** é o diferencial deles: profundidade vertical em autopeças (compatibilidade de veículo via tabela FIPE) por cima de uma base genérica multi-categoria.
- Leitura: "genérico" sozinho não basta pra diferenciar — quem já tá no mercado ganha por profundidade vertical num nicho específico.
- Gap identificado: **nenhum concorrente encontrado até agora cobre TikTok Shop.**
- Mercado Livre não é canal natural pra imóvel — então mesmo que o nicho vire imobiliário, a solução provavelmente não seria "cadastro estilo Meli IA", seria outra coisa (conteúdo pra portal/rede social). Não assumir sem confirmar a real necessidade do cliente.

**Em aberto / precisa decidir antes de virar projeto:**
- **Qual nicho/vertical atacar primeiro — ainda não decidido.** Autopeças no Mercado Livre já tem concorrente estabelecido (Meli IA); TikTok Shop está livre em qualquer nicho.
- Qual marketplace validar primeiro (Mercado Livre tem API oficial documentada; TikTok Shop precisa checar disponibilidade de API no Brasil).
- Se o "criar conteúdo" inclui geração de imagem de produto ou só texto/descrição.
- Nome do nicho/próximo número de pasta (seguiria `20_...` pela numeração atual do repo) — só depois do nicho decidido.

**Status: evoluída/substituída pela entrada abaixo (2026-09-02, mesmo dia).** A pesquisa de TikTok Shop mostrou que "automação genérica de conteúdo/marketplace" como produto multi-cliente também já tem concorrente e até feature nativa da própria plataforma (mesmo padrão do Meta com WhatsApp) — não escapa do problema "big tech dá de graça". A ideia evoluiu de "SaaS de marketplace" pra "agente local sob medida, por cliente" — ver seção seguinte.

---

## 2026-09-02 — Agente local multi-departamento pra loja física (serviço definido)

**Como o serviço ficou definido, na ordem que foi decidida na conversa:**

1. O motivo de errar nas duas ideias anteriores (bot de atendimento, SaaS de automação de marketplace) é o mesmo: são produtos **genéricos, multi-cliente, hospedados pela Kronos** — competem de frente com quem tem mais dinheiro pra escalar a mesma coisa (Meta deu bot de graça; TikTok/concorrentes já cobrem automação de conteúdo/catálogo). Ver padrão documentado na seção acima.
2. O que **não** tem como uma big tech dar de graça: um agente **feito sob medida, rodando local, pro fluxo de trabalho exato daquele cliente específico** — não é produto de prateleira.
3. Cliente-alvo mudou de "empresa de atendimento/agendamento" (clínica, advocacia, imobiliária — já cobertos de graça pela Meta) para **loja física que vende produto** — tem demanda real de estoque/compra/venda que nenhum chatbot de plataforma resolve.

**Arquitetura do serviço — multi-agente, reaproveitando o padrão já validado no projeto (orquestrador + especialistas, igual Aurora → Bia/Clara/Diana), só que virado pra dentro da empresa em vez de atendendo cliente externo:**

- **Orquestrador central** — recebe a demanda interna e aciona o agente certo.
- **Agente Marketing/Conteúdo** — cria foto, vídeo, texto de post; **revisão humana antes de publicar** (mesma lição aprendida da pesquisa da Meli IA — nunca publicar sem checagem).
- **Agente Compras/Estoque** — controla estoque, calcula o que precisa repor, alerta validade/ruptura.
- **Agente Vendas** — acompanha pedido, funil, cliente.
- *(Futuro, mais sensível — não é ponto de partida do piloto)*: Agente Contabilidade, Agente RH, Agente Financeiro.

**Princípio de segurança central (isso é o produto, não só um cuidado técnico):** cada agente só acessa o dado do próprio domínio — Marketing não lê financeiro, Compras não toca em RH. Quanto mais agente, maior a superfície de ataque; segregação de acesso por agente é o que torna essa arquitetura seguível de vender como diferencial (aplica o mesmo princípio de menor privilégio já usado no fix do webhook da landing em `07_Recursos/workflow_06_lead_landing.json`).

**Nichos fechados para começar (escolhidos nesta conversa, 2026-09-02):**
1. **Autopeças (loja física)** — muita variação (marca/modelo/ano), dado sensível = margem/custo de fornecedor.
2. **Loja de roupas** — variação de tamanho/cor/coleção, forte encaixe no módulo de Marketing/Conteúdo (moda vende por foto/vídeo).
3. **Farmácia** — camada extra de regulação: controle de validade (não só ruptura de estoque), dado de saúde se houver histórico de cliente (reaproveita o padrão de consentimento LGPD já usado na Vera/Clínica Médica), marketing restrito por regulação de saúde.

**Candidatos levantados mas NÃO fechados ainda (mercado de alimento — aplicar se/quando decidido):**
Mercadinho/mercearia de bairro, padaria (módulo de estoque vira previsão de produção, não só contagem), açougue (estoque por peso + validade curta + fiscalização sanitária), hortifruti (validade curtíssima, preço variável, desperdício é a dor #1), restaurante/lanchonete pequeno (estoque de ingrediente com ficha técnica, não produto pronto), loja de conveniência, distribuidora de bebida.

**Em aberto / próximos passos:**
- Detalhar o Módulo Compras/Estoque e o Módulo Marketing/Conteúdo em profundidade técnica (schema de dado, ferramentas/MCP necessárias) antes de criar a pasta de projeto.
- Escolher qual dos 3 nichos fechados vira o primeiro piloto real.
- Nome do projeto/próximo número de pasta (seguiria `20_...`) — só depois de escolhido o piloto.
