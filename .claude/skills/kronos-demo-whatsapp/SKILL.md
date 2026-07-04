---
name: kronos-demo-whatsapp
description: Gera imagens de demonstração de conversa de WhatsApp por nicho (print realista do bot Kronos em ação) para anexar na 1ª abordagem de prospecção. Use ao criar/ajustar a demo visual de um nicho (clínicas, advocacia, parecer científico, etc.), montar a página dupla navy com vários nichos, ou converter o SVG em PNG pra mandar no WhatsApp. Gatilhos: "demo de conversa", "print do bot", "imagem de demonstração", "demo do nicho", "material de prospecção visual", "gerar PNG da conversa".
---

# Demo de WhatsApp da Kronos (material de prospecção)

Gera **prints realistas de conversa de WhatsApp** mostrando o assistente da Kronos em ação,
com **observações em azul do lado de fora** apontando cada capacidade. Aprovado pelo Allan
em 20/06/2026. Usado anexado à mensagem inicial de prospecção (prova visual > explicação).

## Arquivos (em `07_Recursos/`)
- `gerar_demo_whatsapp.py` — gera 1 SVG por nicho (celular único + callouts azuis). Saída: `demo_<nicho>.svg`.
- `gerar_demo_poster.py` — gera a **página dupla navy** (vários nichos lado a lado, cabeçalho Kronos). Saída: `demo_poster.svg`.
- Saídas PNG entregues: `demo_clinicas.png`, `demo_advocacia.png`, `demo_imobiliaria.png`, `demo_poster.png`.

## Como usar
1. **Editar o roteiro**: cada nicho é uma lista de mensagens no fim do script. Campos por mensagem:
   - `{"who":"in"}` = cliente (balão branco, esquerda) · `{"who":"out"}` = bot (balão verde, direita).
   - `"text"`, `"time"`, `"note"` (a observação azul — só nos balões do bot). `"file":"nome.pdf"` desenha card de anexo. `{"date":"ontem"}` insere separador.
   - 4 a 6 `note` por nicho (as capacidades). Tom caloroso, nomes fictícios (ex: Clínica Aurora/Dra. Helena; Martins Advocacia/Léa).
2. **Gerar SVG**: `cd 07_Recursos && python gerar_demo_whatsapp.py` (ou `gerar_demo_poster.py`).
3. **Converter SVG→PNG** (Windows, Edge headless — `--headless=new` NÃO funciona pra screenshot, usar o clássico):
   ```powershell
   $edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
   & $edge --headless --disable-gpu --no-sandbox --hide-scrollbars --force-device-scale-factor=2 `
     --run-all-compositor-stages-before-draw --virtual-time-budget=3000 `
     --user-data-dir="$env:TEMP\edgeshot" --window-size=380,<ALTURA_DO_SVG> `
     --screenshot="<saida>.png" ([System.Uri]"<caminho>.svg").AbsoluteUri
   ```
   A `<ALTURA>` é impressa pelo script ao rodar. Para o poster, `--window-size=<pageW>,<pageH>` (também impressos).
4. **Conferir** lendo o PNG (tool Read) antes de entregar; depois `SendUserFile`.
5. **⚠️ Checar corte de texto nas notes** (bug encontrado 03/07): a 1ª linha de cada `note` renderiza em **bold** e um pouco maior, então a largura real fica maior do que a estimativa de `wrap()` (calculada pra texto regular) — o texto pode vazar da borda direita do SVG sem dar erro nenhum (só corta visualmente). Fix aplicado: o `wrap(note, tw)` da coluna de notes usa `tw * 0.76` (margem de segurança). Se ainda cortar com notes muito longas, reduzir esse fator ainda mais. Pra conferir de verdade (a pré-visualização pode "esconder" o corte se você só olhar por cima): recortar a faixa direita do PNG com PIL (`im.crop((420, 0, im.width, im.height))`) e ler o recorte.

## Padrão visual (aprovado)
- Celular realista: header verde `#075E54`, balão branco/verde `#DCF8C6`, tique azul, horário, separador ontem/hoje, barra de input.
- Observações: **fora do celular**, azul `#1f74e6` (versão clara `#5ab0ff` no fundo navy), com linha leader apontando o balão. NUNCA dentro da conversa (polui o contexto).
- Página dupla: fundo navy `#020c2a`, cabeçalho "Kronos Intelligence", divisória central, título+subtítulo por nicho.
- Fonte: `Inter,Segoe UI,sans-serif` (Edge usa Segoe UI no Windows).

## Capacidades por nicho (referência)
- **Clínicas**: atende 24h · base científica · agendamento · agenda da médica · lembrete 24h · pós-atendimento.
- **Advocacia**: atende 24h · triagem do caso · recebe documentos · lê PDF e extrai prazos · direciona pro responsável · base científica (jurisprudência).
- **Parecer Científico** (a fazer): envio do tema · análise de evidências · resumo com referências · nível de confiança · laudo em PDF.

Relacionado: [[operacao-prospeccao-organica]], skill `kronos-landing` (mesma paleta navy).
