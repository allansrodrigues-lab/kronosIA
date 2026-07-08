# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Kronos Intelligence — automação de atendimento (n8n + WhatsApp)

Produto SaaS de bots WhatsApp para clínicas (agendamento + atendimento) via n8n, Evolution API e Google Sheets, rodando num VPS Hostinger. Landing page em `07_Recursos/index.html`. Protótipos ativos: **Aurora** (estética, `clinica01`) e **OdontoVita** (odonto, `kronosdemo`).

---

## Comunicação / Estilo de resposta

- **Explicar o "porquê", não só o "como".** O Allan está aprendendo a programar e em busca de emprego (IA/automação). Quando ele pergunta sobre um termo técnico ou um comando, dar a explicação conceitual — de preferência com analogia do dia a dia — e não só a correção. Ele quer entender de verdade, não decorar.
- **Um passo por vez, mensagem focada.** Respostas diretas ao ponto; quebrar tarefas/explicações longas em etapas em vez de despejar tudo de uma vez. Conjuga com o ritmo dele: curto por passo, porém com o porquê explicado.
- **Cuidado com o limite de token de saída.** Ao gerar conteúdo longo (catálogo, banner, texto de proposta, documentação extensa), quebrar em blocos e avisar antes de despejar tudo de uma vez — resposta cortada no meio já corrompeu transcript em sessões anteriores. Isso não é desculpa pra rasear a explicação técnica: detalhar sem virar textão.
- **Não duplicar conhecimento já registrado.** Antes de adicionar regra ao CLAUDE.md ou criar memória, conferir se já existe — atualizar o que há em vez de criar cópia.

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
- **Evolution API v2.3.7** — instâncias: `kronosdemo` (Odonto `5519997237404`, webhook `/webhook/whatsapp-odonto`) e `clinica01` (Aurora `5519971514971`, webhook `/webhook/whatsapp`).
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
- Após editar, **reiniciar o n8n para aplicar** (deactivate/reactivate ou restart do container) — unpublish/publish via UI não aplica sem restart. Verificar que a versão ativa carregou.
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

## Deploy / Infra

- Operações de arquivo no VPS usam **bash paths**; empacotamento/local usa caminhos relativos ou `$env:TEMP` (não assumir que `/tmp` funciona igual em bash vs PowerShell).
- Site (`07_Recursos/index.html`) roda no VPS via container `kronos-site-*` + Traefik (não na shared hosting).
- **CI/CD (`.github/workflows/deploy.yml`) pode não fazer auto-deploy** — ter sempre o **fallback de `scp`** (clone+copy direto no VPS, ou colar o bloco no Browser Terminal). Confirmar o nome real da rede Traefik antes de qualquer `docker-compose up`.
- Skills disponíveis: `/kronos-deploy` (infra VPS), `/kronos-workflow` (editar n8n), `/n8n-debug` (diagnóstico de bot), `/kronos-agente` (criar/adaptar agente para novo nicho).
