---
name: kronos-landing
description: Edição e manutenção da landing page da Kronos Intelligence. Use esta skill sempre que precisar: alterar textos, slogan, cores, seções, adicionar depoimentos, mudar o fundo SVG Spirograph, ajustar o formulário de contato, adicionar novos serviços, ou qualquer modificação visual/textual na página. Também use quando o usuário mencionar "landing page", "site", "página", "alterar texto", "mudar cor", "adicionar seção", "atualizar site", "página da Kronos". O arquivo principal é 07_Recursos/index.html.
---

# Kronos Landing Page

## Arquivos principais
- **Landing page:** `07_Recursos/index.html` — arquivo único, tudo embutido
- **Fundo SVG:** embutido inline no `index.html` (seção `.hero-bg`)
- **Fundo alternativo:** `07_Recursos/fundo_kronos_final.svg`

## Estrutura da página
1. **Navbar** — logo + links + botão CTA
2. **Hero** — título, slogan, botões + fundo Spirograph metálico
3. **Serviços** — 5 cards
4. **Como funciona** — 4 passos
5. **Nichos atendidos** — tags
6. **Contato** — formulário + dados de contato
7. **Footer**
8. **Botão WhatsApp fixo**

## Identidade visual
- **Fundo:** `#020c2a` (azul marinho profundo)
- **Destaque:** gradiente violeta `#4a0e90` → azul `#3060c8`
- **Texto principal:** `#f0f4ff`
- **Texto secundário:** `#8898bb`
- **Fonte:** Inter (Google Fonts)
- **Fundo hero:** Spirograph SVG metálico deslocado à direita

## Contatos atuais
- **WhatsApp:** +55 19 97126-6736 / wa.me/5519971266736
- **E-mail:** allansrodrigues@gmail.com

## Como editar

### Alterar texto/slogan
Localizar no `index.html` e editar diretamente. Seções identificadas por comentários HTML e IDs (`#servicos`, `#contato`, etc.).

### Adicionar novo serviço
Duplicar um bloco `.card` dentro da div `.cards` e atualizar ícone, título e descrição.

### Alterar cores
Modificar as variáveis CSS no `:root`:
```css
:root {
  --azul:    #020c2a;
  --violeta: #4a0e90;
  --indigo:  #3060c8;
  --turq:    #1890c0;
  --branco:  #f0f4ff;
  --cinza:   #8898bb;
}
```

### Adicionar seção de depoimentos
Inserir nova `<section>` após `#nichos` seguindo o padrão das seções existentes.

### Atualizar fundo Spirograph
O SVG está embutido inline dentro de `.hero-bg`. Para alterar cores das ovals, modificar os gradientes `#m1` a `#m4b` no `<defs>`.

## Após editar
1. Testar localmente abrindo `index.html` no navegador
2. Fazer upload para o VPS (usar skill `kronos-deploy`)
3. Verificar em `https://kronosintelligence.com.br`
