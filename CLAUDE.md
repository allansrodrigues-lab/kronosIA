# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Kronos Intelligence — automação de atendimento (n8n + WhatsApp)

Produto SaaS de bots WhatsApp para clínicas (agendamento + atendimento) via n8n, Evolution API e Google Sheets, rodando num VPS Hostinger. Landing page em `07_Recursos/index.html`. Protótipos ativos: TODOS rodam na central de demos `clinica01` (chavinha) — Aurora, OdontoVita, Léa, Sofia, Helena, Vera. A instância `kronosdemo` foi desativada; seu antigo número virou o chip de prospecção (ver abaixo).

---

## Comunicação / Estilo de resposta

- **Explicar o "porquê", não só o "como".** O Allan está aprendendo a programar e em busca de emprego (IA/automação). Quando ele pergunta sobre um termo técnico ou um comando, dar a explicação conceitual — de preferência com analogia do dia a dia — e não só a correção. Ele quer entender de verdade, não decorar.
- **Um passo por vez, mensagem focada.** Respostas diretas ao ponto; quebrar tarefas/explicações longas em etapas em vez de despejar tudo de uma vez. Conjuga com o ritmo dele: curto por passo, porém com o porquê explicado.
- **Cuidado com o limite de token de saída.** Ao gerar conteúdo longo (catálogo, banner, texto de proposta, documentação extensa), quebrar em blocos e avisar antes de despejar tudo de uma vez — resposta cortada no meio já corrompeu transcript em sessões anteriores. Isso não é desculpa pra rasear a explicação técnica: detalhar sem virar textão.
- **Não duplicar conhecimento já registrado.** Antes de adicionar regra ao CLAUDE.md ou criar memória, conferir se já existe — atualizar o que há em vez de criar cópia.

---

## Regras de automação de navegador

> **Antes de qualquer tarefa de navegador, ler [`BROWSER_PLAYBOOK.md`](BROWSER_PLAYBOOK.md).**
> Ele traz o catálogo completo de modos de falha já vividos (clique por coordenada que driva,
> campo BRL mascarado, editor de código que corrompe JSON, muros de moderação) e o formato de
> resultado estruturado. Para delegar a tarefa inteira, usar o subagente `web-operator`, que já
> segue o playbook. O resumo abaixo é o mínimo que vale mesmo sem abrir o playbook.

Ferramenta mais usada do projeto — essas regras vêm de fricção real, não de teoria.

- **SEMPRE reaproveitar a aba já aberta** em vez de re-navegar para a URL (principalmente `web.whatsapp.com`). Re-navegar causa reconexão lenta e derruba a sessão — já custou mensagem reenviada.
- **Antes de assumir que o site pede login, checar a aba/sessão existente.** LinkedIn, Catho, Gupy e WhatsApp normalmente já estão autenticados; assumir login derrubou uma varredura inteira.
- **NUNCA recarregar ou sair de uma página onde o Allan digitou dado à mão** (proposta, formulário, valor de honorário). Confirmar com ele antes — reload já apagou proposta preenchida manualmente.
- **Screenshot travou ou navegação deu timeout duas vezes → parar de tentar.** Cair para `get_page_text` / avaliação por JS, ou trocar de superfície (Browser pane ↔ Claude in Chrome). Nunca insistir no mesmo caminho pela terceira vez.
- **Preferir chamadas em lote e leitura de texto:** `browser_batch` para sequência de interações, `get_page_text` para verificação. Screenshot só quando o layout em si importa.

## Verificação antes de afirmar "pronto"

- **Depois de qualquer save/submit no navegador** (instruções de Project, candidatura de vaga, edição de perfil): **recarregar a página e reler o valor** antes de dizer que salvou. Já aconteceu de reportar sucesso duas vezes e o reload mostrar que a edição nunca persistiu.
- **Depois de deploy:** `curl` ou abrir a URL de produção e confirmar que o valor mudado aparece — citar a string encontrada. Status verde do Action não é prova.
- **Nunca reportar tarefa concluída só por inspeção de código.** Rodar o código, bater no endpoint ou reler a página. Se não der para verificar, dizer explicitamente o que ficou não verificado.

---

## Arquitetura geral

```
WhatsApp → Evolution API → n8n Webhook
                                └─ Orquestrador (Aurora) — Claude Haiku classifica intent
                                        ├─ AGENDAR       → Bia  (sub-workflow 02)
                                        ├─ DUVIDA_*      → Clara (sub-workflow 03)
                                        ├─ POS_PROCEDIMENTO → Diana (sub-workflow 05)
                                        ├─ RECLAMACAO    → escalação humana
                                        └─ demais         → resposta direta
                                                └─ Google Sheets (CRM / log)
```

**Intenções suportadas:** `AGENDAR`, `DUVIDA_PROCEDIMENTO`, `DUVIDA_PRECO`, `POS_PROCEDIMENTO`, `LEAD_NOVO`, `RECLAMACAO`, `OUTRO`.

### Agentes (04_Agentes_IA/)

| Arquivo | Nome | Papel |
|---|---|---|
| `00_agente_principal_orquestrador.md` | **Aurora** | Recepção, classificação de intent, roteamento |
| `01_agente_agendamento.md` | **Bia** | Agendar, remarcar, cancelar |
| `02_agente_atendimento.md` | **Clara** | Dúvidas sobre procedimentos e preços |
| `03_agente_pos_venda.md` | **Diana** | Pós-procedimento e recompra |
| `04_agente_marketing.md` | **Eva** | Captação e qualificação de leads |

Base de conhecimento compartilhada em `04_Agentes_IA/base_conhecimento/` — atualizar esses arquivos é suficiente para todos os agentes refletirem a mudança.

### Workflows (07_Recursos/)

| Arquivo JSON | Função |
|---|---|
| `workflow_01_orquestrador.json` | Orquestrador principal (Aurora + Haiku) |
| `workflow_02_agendamento.json` | Bia — agendamento via Google Calendar |
| `workflow_03_atendimento.json` | Clara — atendimento e dúvidas |
| `workflow_04_lembrete_24h.json` | Lembrete automático D-1 |
| `workflow_05_pos_venda.json` | Diana — follow-up pós-procedimento |

Cada workflow tem um `_guide.md` e um `_montagem_manual.md` correspondentes.

---

## Stack & Ambiente

- **Ambiente local é Windows** — evitar paths bash `/tmp`; cuidado com escape de barra invertida em `.claude.json` e arquivos de config (conferir backslashes). Usar barras normais `/`, caminhos relativos ou `$env:TEMP` para operações locais.
- **VPS Hostinger** — IP `2.24.101.180`, SSH root, chave `~/.ssh/kronos_vps` (sem senha). Operações no VPS usam **bash paths**.
- **n8n roda em Docker atrás do Traefik** — antes de escrever qualquer `docker-compose`, confirmar o nome real da rede com `docker network ls` (nunca assumir `traefik` ou `web`).
- **Containers Docker:** `n8n-xve0-n8n-1`, `evolution-api`, `evolution-postgres`, `evolution-redis`, `kronos-site-*`, `traefik-*`.
- **n8n usa SQLite** (`/home/node/.n8n/database.sqlite`). Para consultar via script: rodar `node` de dentro de `/usr/local/lib/node_modules/n8n` com `require('sqlite3')`. Campo `execution_data.data` usa formato **flatted** (`require('flatted')` para decodificar).
- **Evolution API v2.3.7** — instâncias: `clinica01` (`5519971514971`, central de demos/chavinha com TODOS os protótipos) e `prospeccao01` (`5519997237404`, chip **cobaia** da prospecção ativa — descartável, pode ser banido; webhook `/webhook/prospeccao-respostas`).
- **Prospecção fria em 3 chips (decisão 24/07):** `5519971514971` (Kronos Protótipo, ~10 anos), `5519971266736` (Kronos Comercial, ~6 anos) e `5519997237404` (cobaia/pessoal novo, ~3 meses) entram no rodízio de disparo, **cap de ~10 msgs/dia por chip**. Risco aceito conscientemente pelo Allan: suspensão de 24h (não ban permanente) — se algum chip levar restrição, **parar de disparar por ele imediatamente** e repensar a abordagem, não insistir. Protótipo e Comercial continuam sendo os números que sustentam demo ao vivo e teste de bot sem loop respectivamente — cautela redobrada neles por isso, não por risco técnico do WhatsApp em si.
- **LLM:** Claude Haiku (`claude-haiku-4-5-20251001`) para classificação de intent; Claude Sonnet 5 (`claude-sonnet-5`) para respostas dos agentes especialistas (thinking adaptativo — padrão do Sonnet 5; sem `temperature`, que retorna 400 nesse modelo).
- **Regra-mãe:** cada cliente novo nasce isolado — instância Evolution própria + planilha CRM própria. Nunca compartilhar base entre clientes.

### Variáveis de ambiente no n8n (Settings → Variables)

```
ANTHROPIC_API_KEY
EVO_BASE_URL      = https://evo.clinicacliente.com.br
EVO_API_KEY
EVO_INSTANCE      = clinica01 | kronosdemo
EVO_TEAM_NUMBER   = número ou JID do grupo da equipe (escalações)
GOOGLE_SHEETS_CRM_ID
```

---

## n8n Workflows

- Sempre editar a versão **publicada/ativa** (`workflow_history`), **não** o rascunho (`workflow_entity`). Editar só o draft **não tem efeito**.
- Após editar, **reiniciar o n8n para aplicar** (deactivate/reactivate ou restart do container) — unpublish/publish via UI não aplica sem restart. O deactivate+activate também **re-registra os webhooks**; se o deactivate não surtir efeito, reiniciar o container. Verificar que a versão ativa carregou.
- **Execute Workflow exige sub-workflow publicado** — ao reativar um orquestrador, publicar também os subs que ele chama.
- Referências a nodes pelo nome (`$('Montar Prompt Haiku')`) quebram se o node for renomeado.

### Convenção de nomes no n8n

```
[Categoria] - [Nome] (vX.Y)
Ex: [WhatsApp] - Orquestrador principal (v1.2)
    [Agendamento] - Criar evento (v1.0)
```

### Padrão de erro em todos os workflows

Todo workflow deve ter **Error Trigger** que: (1) loga na planilha de monitoramento, (2) envia alerta no Telegram do implementador, (3) em falha de IA → escala para humano no WhatsApp.

### Checklist de erro de auth 401 (Anthropic/Haiku) — nessa ordem

1. API key válida e não revogada.
2. `$env.ANTHROPIC_API_KEY` resolve corretamente dentro do nó (testar com nó Set antes).
3. Headers: `x-api-key` (não `Authorization`) + `anthropic-version: 2023-06-01`.
4. **Auto-tradução do Chrome não corrompeu** nomes de variáveis ou chaves JSON — conferir a config crua (não a UI traduzida) e desativar o auto-translate no editor do n8n. ⚠️ Essa é a pegadinha que já queimou horas de debug: o navegador traduz silenciosamente nomes de variável/`$env` e arquivos de config; verificar string por string antes de suspeitar do código.

---

## WhatsApp / Evolution API

Para problemas de conexão, checar **antes** de resetar DB/Redis:

1. **Versão Evolution API / Baileys** — versão obsoleta do Baileys empacotado é rejeitada pelo WhatsApp (causa crash loop). Verificar também se a versão suporta o endpoint chamado (ex: `pairing-code`).
2. **IP de datacenter Hostinger é bloqueado pelo WhatsApp** — se a instância cair / o vínculo falhar, usar **proxy residencial** (serve só pra vincular o chip no QR).

Só depois disso tentar DB delete / Redis clear / downgrade.

## Debugging

- Confirmar se o dado mostrado no n8n é **execução real ou test/mock** antes de diagnosticar.
- **Testar bot por número sem automação** (`5519971266736` — WhatsApp da Kronos). Número-com-bot contra número-com-bot → loop infinito.

### Testar webhook sem WhatsApp

```bash
curl -X POST https://SEU-N8N/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica01",
    "data": {
      "key": { "remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false, "id": "TEST001" },
      "pushName": "Maria Teste",
      "message": { "conversation": "Quero agendar uma limpeza de pele" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

---

## Branding

- **Sempre usar o logo e os assets oficiais da Kronos — nunca desenhar ou improvisar logo/identidade à mão.** Logo se gera via Canva (MCP). Estilo da marca: minimalista navy, monograma "iK"; nada de dourado ou banco de imagens.

## Localização (formatos brasileiros)

- **Normalização de moeda/número brasileiro exige cuidado**: `R$ 50.000` = 50000 (ponto é separador de milhar, vírgula é decimal) — parser ingênuo lê como 50. Validar o parsing de valores em qualquer lógica de bot ou workflow que receba números do usuário.

---

## Protocolo de build de nicho (Kronos)

Nicho novo segue **esta ordem exata** — é a sequência que já entregou Solar, Advocacia, Clínica Médica, Imobiliária, Arquitetura e Odonto:

1. Pesquisa de mercado + decisão do nicho
2. Base de conhecimento (`04_Agentes_IA/base_conhecimento/`)
3. Planilha CRM própria (regra-mãe: nunca compartilhar base entre clientes)
4. Workflows n8n
5. Prompts do voice agent
6. Roteiro de demo
7. Aba do nicho na landing (`/kronos-nicho-landing-demo`)
8. Deploy + verificação no ar
9. Salvar estado na memória antes de limpar a sessão

- **Desativar cron/workflow agendado que não estiver em uso ativo** — schedule parado ligado só queima crédito.
- A pesquisa da etapa 1 come muito contexto: delegar a um subagente e pedir só o resumo, deixando o contexto principal livre para CRM, workflows e deploy.

---

## Deploy / Infra

- Operações de arquivo no VPS usam **bash paths**; empacotamento/local usa caminhos relativos ou `$env:TEMP` (não assumir que `/tmp` funciona igual em bash vs PowerShell).
- Site (`07_Recursos/index.html`) roda no VPS via container `kronos-site-*` + Traefik (não na shared hosting).
- **Deploy padrão:** commitar e dar push na `main` → o Action `.github/workflows/deploy.yml` faz `scp` do `index.html` para `/opt/kronos-site/index.html`.
- **Se o CI/CD travar por mais de ~3 min, cair no fallback manual na hora** (já foi necessário em 3+ sessões — não ficar esperando):

```bash
scp -i ~/.ssh/kronos_vps -o StrictHostKeyChecking=no \
  "07_Recursos/index.html" root@2.24.101.180:/opt/kronos-site/index.html
```

- **Commitar o que estiver pendente ANTES de começar edição de preço/config**, para o diff do deploy sair limpo.
- **Todo deploy termina confirmando que a mudança está no ar** — buscar a URL de produção real (`https://kronosintelligence.com.br/`) e citar o valor atualizado (não confiar em status do Action nem em cache/flag).
- Confirmar o nome real da rede Traefik antes de qualquer `docker-compose up`.
- Skills disponíveis: `/kronos-deploy` (infra VPS), `/kronos-workflow` (editar n8n), `/n8n-debug` (diagnóstico de bot), `/kronos-agente` (criar/adaptar agente para novo nicho), `/radar` (varredura diária de vagas e freelas).

---

## Segurança e dados sensíveis

- **Nunca disparar mensagem de um número que o Allan não tenha declarado liberado.** Hoje os liberados são os 3 chips do rodízio de prospecção (ver *Stack & Ambiente*), com cap de ~10 msgs/dia cada. Qualquer número de cliente real ou fora dessa lista é **proibido** — na dúvida, perguntar antes, não depois.
- **Deixar campos de identidade e dinheiro para o Allan preencher à mão** em candidatura de vaga ou proposta: pretensão salarial, CPF, dados bancários, documentos pessoais. Eu preencho o resto e paro nesses.
- Repositório é **público** — conferir PDFs e pastas pessoais antes de commitar.
