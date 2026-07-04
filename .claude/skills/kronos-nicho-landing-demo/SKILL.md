---
name: kronos-nicho-landing-demo
description: Adiciona (ou edita) uma aba de NICHO na seção "Por segmento" da landing Kronos, com a conversa de WhatsApp ANIMADA rodando dentro de um celular — mesmo padrão de Clínicas, Advocacia e Imobiliária. Use ao publicar um nicho novo no site (energia solar, plástica, contábil, etc.), ajustar o roteiro animado de um nicho existente, ou trocar cor/persona de uma aba. Gatilhos: "aba de nicho no site", "demo animada na landing", "adicionar nicho no site igual às outras", "conversa animada do site", "novo segmento na landing". NÃO confundir com kronos-demo-whatsapp (que gera PNG estático de prospecção) nem kronos-landing (edição geral do site).
---

# Aba de nicho com demo animada na landing (Kronos)

Padrão validado em 03/07/2026. A seção **"Por segmento"** de `07_Recursos/index.html` tem uma aba por
nicho; cada aba de nicho-produto mostra uma **conversa de WhatsApp animada** (mensagens "digitando" +
balões que aparecem em sequência, com legenda de capacidade) dentro de um celular realista, ao lado de
uma coluna de capacidades. Hoje: **Clínicas** (toggle Estética/Odonto), **Advocacia** (Léa) e
**Imobiliária** (Sofia). "Empresas de Serviços" é aba genérica **sem** demo animada.

> ⚠️ Isto é diferente de `kronos-demo-whatsapp` (gera PNG estático pra anexar na prospecção). Aqui é
> HTML/CSS/JS animado que roda no site no ar.

## Anatomia (tudo em `07_Recursos/index.html`)

Uma aba de nicho animada tem **5 pontos de edição**. Ao clonar um nicho novo, replicar os 5:

1. **Botão da aba** (na lista de `.seg-tab`, ~linha 722):
   ```html
   <button class="seg-tab" onclick="abrirSeg('SLUG',this)">EMOJI Nome do Nicho</button>
   ```
2. **Div do segmento** `<div id="seg-SLUG" class="seg-conteudo" style="display:none">` contendo:
   - o bloco `.wa-demo` (celular `.wa-phone` + coluna `.wa-side` com `<ul class="wa-caps">`),
   - dentro do celular: `.wa-bar` (avatar + nome + `<em id="wa-st-SLUG">online</em>`), `.wa-chat` com `id="wa-chat-SLUG"`, e a legenda `.wa-caption CLASSE` com `<span id="wa-cap-SLUG">`,
   - abaixo: grid "Como funciona para ..." (5 itens, o último em destaque com badge NOVO) + card "O que ganha" (4 métricas).
3. **Classe de cor da legenda** no CSS (junto de `.wa-caption.adv` / `.wa-caption.cli`):
   ```css
   .wa-caption.SLUG span{color:#c9f5ec;background:rgba(R,G,B,0.18);border:1px solid rgba(R,G,B,0.5)}
   ```
4. **Gatilho no `abrirSeg`** (função ~linha 1030):
   ```js
   if (id === 'SLUG' && window.__waStartSLUG) window.__waStartSLUG();
   ```
5. **Motor da conversa** — um `<script>` IIFE próprio (clonar o da Sofia/Léa). Define o array `R` de
   mensagens e expõe `window.__waStartSLUG` (lazy start: só anima quando a aba é aberta pela 1ª vez).

## Formato do array de mensagens (R)
Cada item: `{s:'in'|'out', x:{...}, t:'HH:MM', cap:'legenda opcional', }`.
- `x.type:'text'` → `html:'...'` (aceita `<b>`, `<br>`).
- `x.type:'audio'` → `dur:'0:10'` (desenha player de áudio).
- `x.type:'file'` → `fn`/`fm` (card PDF) · `x.type:'an'` → bloco de análise (ver Léa).
- `x.rem:true` → balão verde-escuro de **lembrete** (usar no follow-up/D-1).
- `cap` só nos balões `out` = a legenda azul que aparece embaixo destacando a capacidade.
- Roteiro ideal: 10-12 mensagens, arco **qualifica → entrega valor → agenda → follow-up**, tom caloroso, nomes fictícios.

## Padrões de cor por nicho (accent)
- Clínicas = roxo `#a679ff` / bg `rgba(120,72,200,...)`
- Advocacia = azul `#5f8bff` / bg `rgba(48,96,200,...)`
- Imobiliária = teal `#3ec8b4` / bg `rgba(24,192,160,...)`
- Nicho novo: escolher um accent distinto na mesma família navy; aplicar em: `section-label`, o `<span>` do headline, a classe `.wa-caption.SLUG`, e o bg dos ícones do "Como funciona".

## Detalhes que já morderam (o extraordinário)
- **Motor lazy vs. auto:** Clínicas auto-inicia no load e roda em loop (tem toggle Estética/Odonto via `waCliSwitch`). Advocacia e Imobiliária usam **lazy start** (`__waStart` / `__waStartImob`) disparado pelo `abrirSeg` — evita animar aba escondida. Para nicho simples (1 persona), copiar o modelo **Imobiliária** (mais limpo).
- **`running` guard:** o motor lazy usa `var running=false` + `if(running)return` pra não abrir múltiplos loops se o usuário clicar a aba várias vezes.
- **IDs únicos por nicho:** `wa-chat-SLUG`, `wa-st-SLUG`, `wa-cap-SLUG` — se colar de outro nicho e esquecer de trocar um id, dois nichos brigam pelo mesmo elemento.

## Verificar antes de entregar (preview local)
1. `preview_start` (launch.json → `mapa`, serve 07_Recursos) e navegar pra `/index.html`.
2. `preview_eval`: achar o `.seg-tab` do nicho, `.click()`, checar `getComputedStyle(seg).display==='block'` e `typeof window.__waStartSLUG==='function'`.
3. Esperar ~6s e ler `#wa-chat-SLUG .wa-msg` — confirmar que as N mensagens apareceram e a caption final está certa.
4. `preview_console_logs level:error` = zero.

## Deploy (site no ar)
Ver skill `kronos-deploy` / memória deploy-landing-vps: commit + push GitHub, depois copiar `index.html` pra `/opt/kronos-site/` no VPS.
⚠️ **O SSH-deploy em produção é bloqueado pelo classificador de modo automático do Claude** — o Allan cola o bloco no Browser Terminal do VPS:
```
cd /tmp && rm -rf kdeploy && git clone --depth 1 https://github.com/allansrodrigues-lab/kronosIA.git kdeploy && cp kdeploy/07_Recursos/index.html /opt/kronos-site/index.html && rm -rf kdeploy && echo DEPLOY_OK
```
Confirmar de fora: `curl -sS https://kronosintelligence.com.br/ | grep -c "seg-SLUG"`.

Relacionado: `kronos-landing` (edição geral), `kronos-demo-whatsapp` (PNG de prospecção), `kronos-deploy`.
