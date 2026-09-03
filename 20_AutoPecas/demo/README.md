# Demo ilustrativa — Painel do Agente (rascunho de site)

**Status: rascunho aprovado na direção, não implementado no site ainda.** Preview publicado: https://claude.ai/code/artifact/b616955e-c1b7-410d-822f-1e0b2bb24f50

`painel-agente-autopecas.html` é o arquivo-fonte (self-contained, abre direto no navegador).

## Decisão de formato (2026-09-02)

**Primeira versão usava um cartão parecido com celular — foi rejeitada.** Risco identificado: misturar visualmente com o chat de WhatsApp animado das abas da Linha B (Aurora, Léa, Sofia etc.) desvaloriza o produto que já existe e vende — o Agente de Atendimento continua ativo, é outro produto, não pode parecer substituído ou de segunda categoria.

**Segunda versão (atual): janela de terminal**, não celular. Por quê:
- É literalmente o que a Linha A é — roda **no computador da loja**, não no WhatsApp. O formato reforça isso na primeira olhada, sem precisar explicar em texto.
- Silhueta widescreen, sem nenhuma referência de app de mensagem (sem bolha, sem avatar, sem "digitando...").
- Conteúdo é a saída real do protótipo (`20_AutoPecas/mvp/agente_estoque.py`), só estilizada — não é texto inventado.
- Termina num prompt estilo CLI ("aprovar pedido de reposição das 6 peças? [revisar depois / s — aprovar]") que reforça visualmente o princípio de segurança: o Agente nunca compra sozinho.

**Copy de abertura já resolve a preocupação de canibalização** direto no texto: "O Agente de Atendimento (WhatsApp) já existe, já funciona e continua sendo vendido — nada muda nele. Este é um produto diferente."

## Próximo passo

Levar esse formato pra dentro de `07_Recursos/index.html`, na seção `#segmentos`, como aba nova — reaproveitando o container de celular só pras abas de atendimento (Linha B) e esse formato de terminal só pras abas de operação (Linha A, a partir de autopeças).
