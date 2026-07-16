---
name: kronos-brand
description: Guia de identidade visual e de linguagem da Kronos Intelligence — aplicar SEMPRE que criar ou revisar qualquer peça nova (logo, landing page, catálogo, proposta, contrato, slide, PDF, post, banner de prospecção). Use também quando o usuário mencionar "identidade visual", "brand", "marca", "cor da Kronos", "paleta", "logo novo", "isso parece profissional?", ou antes de gerar qualquer asset visual do zero. Cobre paleta de cores, tipografia, uso do logo oficial, regras de estilo (o que evitar) e o posicionamento de linguagem ("agente inteligente", nunca "chatbot").
---

# Kronos Brand Guidelines

Checklist de identidade a aplicar em QUALQUER peça nova antes de considerar pronta — landing, catálogo, proposta, contrato, book, post, banner, PDF, apresentação.

## Paleta de cores (fixa, não inventar variação)

```css
--azul:    #020c2a;  /* navy profundo — fundo padrão */
--violeta: #4a0e90;  /* gradiente destaque, início */
--indigo:  #3060c8;  /* gradiente destaque, meio */
--turq:    #1890c0;  /* gradiente destaque, fim / acento */
--branco:  #f0f4ff;  /* texto principal sobre navy */
--cinza:   #8898bb;  /* texto secundário */
```

Fundo padrão = navy `#020c2a`. Destaque = gradiente violeta→azul→turquesa. Nunca inventar cor fora dessa paleta sem aprovação do Allan.

## Tipografia

**Inter** (Google Fonts) em toda peça — títulos e corpo de texto.

## Logo oficial

Arquivos em `07_Recursos/identidade_visual/`:
- `kronos_logo_oficial_marinho.png` — logo claro sobre navy (padrão, usar por default)
- `kronos_logo_oficial_claro.png` — logo navy sobre fundo claro (usar só quando o fundo da peça for claro)
- `kronos_logo_oficial_transparente.png` — logo branco fundo transparente (ideal pra PDF/fundo escuro sem retângulo visível)
- `kronos_icone_transparente.png` — só o monograma "iK", usado em navbar/favicon
- `kronos_perfil_azul_marinho.png` — favicon/social atual

**⛔ PROIBIDO:** `kronos_logoC_azul_marinho.png` e `kronos_logoC_clara.png` — eram opções rejeitadas pelo Allan, foram deletadas. NUNCA recriar nem usar.

**Regra de ouro:** ao precisar do logo num asset novo, usar SOMENTE um dos arquivos oficiais acima. Nunca pegar "um arquivo qualquer parecido" da pasta — em dúvida, perguntar ao Allan.

## Estilo visual — o que fazer

- Minimalista, muito espaço em branco, traços finos (monoline)
- Monograma "iK" como elemento de marca recorrente
- Gradiente violeta→azul→turquesa como único elemento "colorido" de destaque

## Estilo visual — o que NUNCA fazer

- Dourado, relógios, engrenagens, robôs genéricos (ícones clichê de "automação")
- Qualquer coisa com "cara de banco de imagens" / stock photo genérico
- Gradientes fora da paleta acima
- Logo desenhado à mão em SVG/GDI+/PowerShell — **logo/ícone novo sempre via Canva MCP** (`mcp__9f413a50-...generate-design`, `design_type: "logo"`), nunca improvisado em código. Ver receita detalhada em memória `feedback-logo-sempre-canva`.

## Posicionamento de linguagem (aplica a todo texto, não só visual)

**Nunca usar "chatbot"** — nem para descrever, nem para negar ("não é um chatbot..."). Sempre **"agente inteligente"** / **"agente de IA"**. "Chatbot" soa commodity e derruba o ticket; "agente inteligente" justifica o posicionamento premium. Único lugar onde "chatbot" sobrevive é como palavra-chave de SEO/busca, nunca como identidade de venda.

Isso vale para: site, catálogo, proposta, contrato, discurso de prospecção (porta a porta ou WhatsApp), qualquer copy nova.

## Checklist final antes de publicar qualquer peça nova

1. Cores batem com a paleta acima? (nada de hex inventado)
2. Fonte é Inter?
3. Logo usado é um dos arquivos oficiais (não um dos proibidos, não desenhado à mão)?
4. Nenhuma palavra "chatbot" sobrou no texto?
5. Nada de ícone clichê (relógio/engrenagem/robô) ou visual "banco de imagens"?

Se algum item falhar, corrigir antes de considerar a peça pronta — não é opcional.
