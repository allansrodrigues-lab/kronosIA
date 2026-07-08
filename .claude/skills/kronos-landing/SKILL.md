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
1. **Navbar** — logo + links (Serviços/Como funciona/Planos) + "Área do Cliente" (`/painel`) + CTA "Falar com especialista". `position:fixed`, some mobile abaixo.
2. **Hero** — título, slogan, botões + fundo Spirograph metálico
3. **Serviços** — 7 cards (`#servicos`)
4. **Por segmento** — abas por nicho (Clínicas/Advocacia/Imobiliária/Empresas de Serviços), cada uma com demo animada de WhatsApp + "Como funciona para [nicho]" + resultado típico (`#segmentos`). **Isso substituiu a antiga seção genérica "Como funciona" (removida em 05/07 por duplicar conteúdo).**
5. **Por que a Kronos** — tabela comparativa (`#por-que`)
6. **Planos** — cards de preço (`#planos`)
7. **Contato** — formulário + dados de contato
8. **Footer**
9. **Botão WhatsApp fixo**

### Menu mobile (hambúrguer) — adicionado 05/07
Antes disso, `nav ul { display:none }` no `@media (max-width:768px)` escondia o menu INTEIRO no celular (nenhum link, nem o CTA) — ninguém tinha reparado até então. Fix: botão `.nav-toggle` (3 barras, vira X) + `<ul id="navMenu">` que ganha a classe `.nav-open` via `toggleNav(this)` (função inline logo após a `</nav>`). No mobile, `#navMenu.nav-open` vira um dropdown fixo abaixo da nav com fundo sólido. Cada link fecha o menu sozinho ao ser clicado (listener em `DOMContentLoaded`). Ao adicionar novo item de menu, editar tanto o `<ul id="navMenu">` quanto (se precisar de estilo diferente) o bloco `@media (max-width:768px)` correspondente.

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
1. Testar localmente (preview_start com um servidor estático, ou `preview_resize` em modo mobile pra conferir o menu hambúrguer)
2. Commitar + push pro GitHub (`allansrodrigues-lab/kronosIA`)
3. Publicar no VPS via SSH direto (mais rápido que o CI/CD, que pode não disparar sozinho — ver [[deploy-landing-vps]]):
```bash
cp ~/.ssh/vps_key /tmp/vk && chmod 600 /tmp/vk && ssh -o BatchMode=yes -o IdentitiesOnly=yes -i /tmp/vk root@2.24.101.180 'cd /tmp && rm -rf kdeploy && git clone --depth 1 https://github.com/allansrodrigues-lab/kronosIA.git kdeploy && cp kdeploy/07_Recursos/index.html /opt/kronos-site/index.html && rm -rf kdeploy && echo DEPLOY_OK'; rm -f /tmp/vk
```
4. Confirmar de fora: `curl -s https://kronosintelligence.com.br | grep -o "trecho-novo"`
