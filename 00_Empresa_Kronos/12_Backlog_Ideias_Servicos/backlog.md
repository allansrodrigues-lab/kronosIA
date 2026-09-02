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
