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

### Agentes definidos (quadro completo)

| Agente | O que faz | Observação crítica |
|---|---|---|
| **Orquestrador** | Recebe a demanda interna e aciona o agente certo | Mesmo padrão da Aurora, virado pra dentro da empresa |
| **Compras/Estoque** | Controla estoque, calcula reposição, alerta ruptura e validade | Ponto de partida do piloto — valor rápido, risco baixo |
| **Fornecedores** | Pesquisa fornecedor principal + alternativo, compara preço/risco | Formato validado em `19_Projeto2_Robo_Humanoide/FORNECEDORES.md`. **Nunca compra sozinho** — só apresenta pra aprovação |
| **Marketing/Conteúdo** | Cria foto, vídeo e texto de post; publica em rede social | **Revisão humana antes de publicar** (lição da Meli IA) |
| **Vendas** | Acompanha pedido, funil, cliente | — |
| **Fiscal/Contabilidade** | Prepara o dado e aciona emissão de NF-e | **Não reinventa cálculo fiscal** — integra com provedor de NF-e já homologado. Erro fiscal é problema jurídico do cliente, não bug |
| **RH** | Cálculo de folha, INSS, FGTS, admissão | Mesma regra: tabela oficial sempre atualizada, **nunca hardcoded** (muda todo ano) |
| **Financeiro** | Contas a pagar/receber, fluxo de caixa, saldo | Construível direto (registro + alerta), mas é o dado mais sensível — segurança de acesso pesa mais aqui |

### Etapas do serviço (iguais para qualquer loja)

1. **Diagnóstico** — como a loja trabalha hoje (caderno, planilha, sistema), onde o dado está e em que formato.
2. **Escopo da Fase 1** — Estoque + Fornecedores primeiro (valor rápido, pouco dado sensível).
3. **Modelagem do catálogo** — base compartilhada por todos os agentes; **é aqui que os nichos se separam** (ver tabela abaixo).
4. **Implantação local + permissões** — instalar na máquina da loja, menor privilégio por agente desde o dia 1.
5. **Hardening** — credencial protegida, acesso restrito a pasta, aprovação humana antes de ação irreversível (comprar, publicar, emitir nota).
6. **Treinamento do dono + operação assistida** — ele precisa saber conferir o que o agente fez.
7. **Expansão por fase** — Marketing → Vendas → e só no fim os regulados (Fiscal, RH, Financeiro).

### O que muda em cada nicho

| | **Autopeças** | **Roupas** | **Farmácia** |
|---|---|---|---|
| **Chave do catálogo** | Compatibilidade veículo (marca/modelo/ano) | Grade: tamanho × cor × modelo (1 produto = 15-30 SKUs) | Lote + **validade** |
| **Dor #1** | Achar a peça certa rápido no balcão | Encalhe de coleção fora de estação | Vencimento e ruptura de controlado |
| **Agente de maior valor** | Consulta de compatibilidade no balcão | **Marketing/Conteúdo** (moda vende por foto) | Estoque com alerta de validade |
| **Fornecedores** | Original × paralelo × similar (preço não decide sozinho) | Atacado/confecção, compra por grade fechada | Distribuidor regulado |
| **Marketing** | Técnico ("tem pro seu carro") | Forte, visual, Instagram/TikTok | **Restrito por Anvisa** — foca perfumaria/higiene |
| **Dado sensível** | Margem e custo de fornecedor | Margem | **Máximo**: dado de saúde (LGPD) + controlados/SNGPC |
| **Compliance extra** | — | — | Anvisa, SNGPC, receita de controlado |

**Leitura:** autopeças e roupas têm risco parecido (dado sensível = margem). Farmácia é outro patamar — fiscalização + dado de saúde: é o que mais justifica cobrar por segurança, mas também o que exige mais rigor pra entregar.

**Em aberto / próximos passos:**
- Pesquisar provedores reais de NF-e e de folha/RH pra saber com quem a Kronos integraria.
- Nome do projeto/próximo número de pasta (seguiria `20_...`) — ainda não criado.

**Decisão de prioridade (2026-09-02):** **autopeças é o primeiro nicho a construir.** Roupas e farmácia seguem fechados como próximos, nessa ordem de aparição na conversa.

---

## 2026-09-02 — Posicionamento do site: Linha A no topo

**Decisão:** o site (`07_Recursos/index.html`) tem duas linhas de serviço, e a **Linha A (Agente de Operação — o serviço novo, multi-departamento) vai pro topo/carro-chefe.** A Linha B (Agente de Atendimento — os bots de WhatsApp que já existem: Aurora, Bia, Clara, Léa, Sofia, Helena, Vera etc.) **não é excluída** — continua vendável (WhatsApp Business API cobra por conversa, "grátis" do Meta tem limite) e as 6 demos animadas viram prova de capacidade técnica.

**O que muda em cada seção do site (levantado, ainda não implementado):**

| Seção | Hoje | Como fica |
|---|---|---|
| Hero | Só fala da Linha B | Comunicar as duas linhas, Linha A primeiro |
| `#servicos` | Lista única | Dividido: Operação / Atendimento |
| `#segmentos` | 6 abas, todas com chat de WhatsApp animado | Mantém as 6 (Linha B) + abas novas de Autopeças/Roupas/Farmácia (Linha A) — **a demo da Linha A NÃO pode ser chat de WhatsApp animado**, senão o site continua parecendo empresa de chatbot. Precisa mostrar alerta de estoque, tabela de fornecedor comparado, post esperando aprovação |
| `#planos` | Plano de bot | Somar faixa de projeto de implantação + mensalidade de manutenção |
| `#implantacao` | "7 a 14 dias" (vale pra Linha B) | Linha A usa as 7 etapas (diagnóstico → hardening → expansão por fase) |

**Ainda não implementado no HTML** — só desenhado nesta conversa.

---

## 2026-09-02 — Desenho técnico: autopeças, fase 1 (Estoque + Fornecedores)

**Onde o agente se encaixa em relação ao que a loja já usa:**

A loja já tem PDV/ERP (Bling, Tiny, Omie, ou sistema local antigo) — isso é **cadastro e registro**, não agente. Guarda dado com perfeição, mas não decide nada; o máximo que faz é alarme de regra fixa ("avise quando chegar a 3 unidades"). **A Kronos não substitui o ERP — fica por cima dele**, lendo via API (Bling/Tiny têm API) e agindo como o "funcionário experiente que lê o caderno todo dia de manhã". Primeira pergunta do diagnóstico: *"qual sistema você usa hoje, e ele deixa exportar/consultar os dados?"*

**Stack (o que muda em relação aos bots de clínica):**

| Camada | Bots (hoje) | Agente de loja (novo) |
|---|---|---|
| Onde roda | VPS da Kronos | Máquina da loja — dado não sai de lá |
| Dados | Google Sheets | SQLite local (exporta pra planilha quando o dono quiser ver) |
| Raciocínio | Claude Haiku+Sonnet via n8n | Claude + Skill de autopeças (regras do nicho) |
| Ferramentas | Nós do n8n | MCP por domínio (banco, pasta de fotos, busca web, API de marketplace/ERP) |
| Agendamento | Cron do n8n | Tarefa agendada do SO **ou** n8n local — Fase 1 talvez nem precise de n8n/Docker |

**As 4 operações do agente:**

| Operação | O que faz | Risco |
|---|---|---|
| Checar | Lê o ERP via API, cruza com histórico de venda, detecta ruptura/parado/vencendo | Baixo (só leitura) |
| Transcrever mercadoria | Foto da peça chegando → identifica → preenche cadastro (nome, categoria, compatibilidade, preço) | Médio (escreve no sistema) |
| Administrar orquestrado | Estoque detecta falta → Fornecedores pesquisa → Financeiro checa caixa → decisão única | Médio |
| Notificar | Avisa o dono (peça acabando, lote vencendo, peça sem cadastro) | Baixo |

**Gradiente de autonomia (não é liga/desliga — por nível de risco):**
- 🟢 **Autônomo desde o dia 1:** ler, analisar, calcular, notificar — nada disso muda o mundo real.
- 🟡 **Prepara e pede confirmação:** cadastrar produto, alterar preço, escrever no ERP — dono confirma no começo; libera automático por categoria depois que o agente prova acerto consistente.
- 🔴 **Sempre com aprovação humana:** comprar de fornecedor, emitir nota fiscal — qualquer coisa que mexe em dinheiro ou tem efeito jurídico.

**Canal de notificação:** WhatsApp do dono — é onde ele já vive. **Diferença importante do modelo antigo:** não é bot de atendimento falando com cliente (isso o Meta comoditizou) — é **alerta operacional interno**, dono para consigo mesmo/equipe. Mesmo canal, papel completamente diferente.

**Ainda em aberto:**
- Como o agente identifica a peça pela foto tecnicamente (visão + busca de compatibilidade).
- Detalhar Fornecedores e os agentes seguintes (Vendas, depois Fiscal/RH/Financeiro) no mesmo nível de profundidade.
- Criar a pasta do projeto (`20_AutoPecas` ou nome a definir) — ainda não criada, tudo até aqui é desenho em backlog.
