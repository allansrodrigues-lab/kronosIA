---
name: kronos-advocacia
description: Operar e customizar o nicho Advocacia da Kronos — demo completa com Léa (triagem de casos) + análise de PDF. Use para testar a demo, corrigir Léa, ajustar prompt, criar abas CRM, adaptar para cliente real, limpar sessão travada, ou diagnosticar falha nos workflows. Gatilhos: "advocacia", "Léa", "léa", "triagem jurídica", "análise de PDF", "análise de documento", "bot jurídico", "escritório demo", "sessão advocacia".
---

# Kronos Advocacia — Demo + Serviço #6 (PDF)

Tudo operado via `mcp__n8n__*` e `mcp__google-sheets__*`. Construído em 17/06/2026.

## Arquitetura

```
WhatsApp → clinica01 → Roteador (/advocacia) → DEMO-01-orquestrador-advocacia
                                                    ├─ É PDF?  → kronos-analise-pdf (direto)
                                                    ├─ É Áudio? → kronos-transcrever-audio → Léa
                                                    ├─ Haiku classifica intent
                                                    │     ├─ TRIAGEM / CONSULTA_AGENDAMENTO / DUVIDA_AREA / DOCUMENTO → Léa
                                                    │     ├─ RECLAMACAO / ACOMPANHAMENTO → escalação WhatsApp equipe
                                                    │     └─ fallback → Léa
                                                    └─ DEMO-02-agente-lea (Léa responde)
```

## IDs dos workflows

| Workflow | ID | Webhook | Status |
|---|---|---|---|
| Orquestrador advocacia | `QEawJtNsqlNGwrw0` | `/webhook/whatsapp-advocacia-demo` | ✅ ATIVO |
| Agente Léa | `TZDQobW44zZwkjOB` | Execute Workflow (sub) | ✅ ATIVO |
| Análise de PDF | `VFtnXxDmZYEf1saI` | `/webhook/whatsapp-pdf` | ✅ ATIVO |
| Roteador central | `2hYQv4sOQq5AOXmt` | `/webhook/whatsapp-demo` | ✅ ATIVO |

## Chavinha

Do número Kronos (`5519971266736`) → mandar pro `5519971514971`:
- `/advocacia` → troca perfil para "Escritório Demo Advocacia ⚖️" + status "Triagem jurídica gratuita 🤝", roteia para orquestrador Léa
- `/pdf` → troca perfil para "Kronos · Análise de Documentos ⚖️", só responde PDFs

## CRM — Google Sheets

Planilha: `1ZlDFYkgx6aXUM0ayj1e1_K6uX0cruo7VuCcmg1_w5ps`

| Aba | Colunas (linha 1 — **exatas**, o workflow casa por nome) | Função |
|---|---|---|
| `Sessoes_Advocacia` | `Telefone \| ID \| Agente \| Fase \| Historico \| Dado_Temp \| Atualizado_Em \| Status` | Memória da sessão de cada cliente (Léa lê e faz appendOrUpdate por `Telefone`) |
| `Log_Advocacia` | `Data \| Telefone \| Nome \| Mensagem \| Acao \| Fase \| Escalacao` | Log de todas as interações (append) |

⚠️ **O cabeçalho tem que bater EXATAMENTE com esses nomes.** O nó "Montar Prompt Léa" busca a sessão por `Telefone` + `Agente==='LEA'` + `Status==='ativo'`, e "Atualizar Sessão Léa" faz `appendOrUpdate` casando por `Telefone`. Se o cabeçalho estiver com nomes diferentes (schema legado tipo `Numero`/`ID_Sessao`/`Tipo_Consulta`), o `find` nunca acha → Léa **se re-apresenta a cada mensagem** (amnésia) e a gravação empilha linhas-fantasma (só `Status=ativo`). Os nós de Sheets usam `onError: continueRegularOutput`, então isso falha **silencioso** (execução fica "success").

Ambas as abas **existem** (verificado 02/07/2026) com o schema correto. Se voltar a amnésia, primeiro conferir a linha 1 (ver [[advocacia-kronos]]).

## Intents do orquestrador (Claude Haiku classifica)

| Intent | Rota |
|---|---|
| `TRIAGEM` | → Léa |
| `CONSULTA_AGENDAMENTO` | → Léa |
| `DUVIDA_AREA` | → Léa |
| `DOCUMENTO` | → Léa |
| `ACOMPANHAMENTO` | → escalação humana |
| `RECLAMACAO` | → escalação humana |
| `OUTRO` | → Léa (fallback) |

## Léa — regras absolutas

A Léa **NUNCA**:
- Dá pareceres jurídicos ou opiniões sobre o caso
- Cita artigos de lei ou percentuais de chance de ganhar
- Promete resultado ("vai ganhar", "tem direito")
- Diz que é robô (usa: "Essa parte precisa ser avaliada pelo advogado")

A Léa **SEMPRE**:
- Acolhe o cliente (situações sensíveis: demissão, divórcio, acidente)
- Coleta: nome completo + melhor horário + preferência presencial/online
- Identifica a área (trabalhista, família, civil, consumidor, previdenciário)
- Oferece o próximo passo: agendar consulta inicial

## Áreas de atuação (base de conhecimento)

`12_Advocacia/base_conhecimento/01_areas_atuacao.md`
- Trabalhista: demissão, rescisão, horas extras, assédio
- Família: divórcio, guarda, pensão, inventário
- Civil: contratos, dívidas, indenização, vizinhança
- Consumidor: produtos/serviços, planos de saúde, bancos
- Previdenciário: aposentadoria, benefícios INSS

## Análise de PDF — o que entrega

1. Tipo do documento (contrato, petição, sentença…)
2. Partes envolvidas (nomes + papéis)
3. Datas e prazos (⚠️ nos próximos 30 dias)
4. Valores financeiros
5. Pontos de atenção (até 5: obrigações, penalidades, riscos)
6. Resumo executivo (3-5 linhas)
7. Rodapé: "análise informativa, não consultoria jurídica"

Limite: só arquivos PDF. Outros tipos → "Só consigo analisar PDF."

## Consertos comuns

### Léa se re-apresenta a cada mensagem (amnésia / perde histórico)
**Causa nº 1: cabeçalho da aba `Sessoes_Advocacia` fora do schema** (ver seção CRM). Conferir a linha 1 — tem que ser exatamente `Telefone | ID | Agente | Fase | Historico | Dado_Temp | Atualizado_Em | Status`. Se estiver com nomes legados, o `find` não acha a sessão e ela re-sauda. Confirmar no dado LIVE lendo a execução da Léa (nó "Montar Prompt Léa": se `sessao_id: null` e `historico` só tem a msg atual → é isso). Corrigir reescrevendo a linha 1 + limpar linhas-fantasma. Aconteceu em 02/07/2026.

### Léa dando resposta da conversa anterior (sessão travada)
Limpar linha do telefone na aba `Sessoes_Advocacia`:
```
mcp__google-sheets__find_in_spreadsheet → achar linha pelo telefone → update_cells Status=encerrado (ou deletar linha)
```

> 💡 Sheets MCP fora do ar? Dá pra ler/escrever a planilha direto com a service account (`C:/Users/Usuario/.claude/kronos-service-account.json`) via `uv run --with google-auth --with google-api-python-client python script.py` — não precisa do MCP nem de restart.

### Orquestrador não chama Léa
Verificar se `DEMO-02-agente-lea` está ATIVO — o Execute Workflow exige sub-workflow publicado.
```
mcp__n8n__n8n_get_workflow id=TZDQobW44zZwkjOB → checar active:true
```

### PDF não é analisado (modo /advocacia)
O `/advocacia` roteia para `whatsapp-advocacia-demo` (orquestrador → sub-workflow `whatsapp-pdf` quando é PDF). Verificar:
1. Nó "É PDF?" no orquestrador — condição `$json.ehPdf === true`
2. Nó "Baixar PDF" — endpoint `getBase64FromMediaMessage/clinica01`
3. Nó "Claude Sonnet" — header `x-api-key`, não `Authorization`

### Modo /pdf não responde
Verificar `kronos-analise-pdf` (ID `VFtnXxDmZYEf1saI`) está ATIVO e que `EVO_BASE_URL` resolve.

## Testar sem enviar PDF real

```bash
curl -X POST https://n8n.kronosintelligence.com.br/webhook/whatsapp-advocacia-demo \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica01",
    "data": {
      "key": {"remoteJid": "5519971266736@s.whatsapp.net", "fromMe": false, "id": "TEST-LEA-01"},
      "pushName": "Teste",
      "message": {"conversation": "Fui demitido sem justa causa, o que faço?"},
      "messageType": "conversation",
      "messageTimestamp": 1718640000
    }
  }'
```

## Adaptar para cliente real (escritório de advocacia)

1. Criar instância Evolution própria: `POST /instance/create` com nome do escritório
2. Criar planilha CRM própria com abas `Sessoes_Advocacia` e `Log_Advocacia`
3. Atualizar IDs nos workflows (spreadsheetId, instancia, EVO_INSTANCE)
4. Ajustar áreas de atuação em `12_Advocacia/base_conhecimento/01_areas_atuacao.md`
5. Ajustar horários e nome do escritório no prompt da Léa
6. Testar com número pessoal (SEM bot) → número do escritório

## Arquivos locais

```
12_Advocacia/
  agentes/
    00_orquestrador_advocacia.md   — intents + roteamento
    01_agente_triagem_lea.md       — prompt completo da Léa
    02_agente_analise_pdf.md       — spec técnica do serviço de PDF
  base_conhecimento/
    01_areas_atuacao.md
    02_politicas.md                — regras do bot (o que Léa nunca faz)
    03_tom_de_voz_lea.md
  workflows/
    workflow_analise_pdf_montagem.md  — guia técnico do PDF workflow
```

## Gotchas

- **Número-com-bot contra número-com-bot = loop** ([[feedback-teste-whatsapp-kronos]]). Sempre testar do Kronos (`5519971266736`).
- `DEMO-01` depende de `DEMO-02` publicado. Se desativar a Léa, o orquestrador quebra.
- A Léa usa `onError: continueRegularOutput` nos nós do Sheets → funciona mesmo sem as abas CRM, mas não tem memória.
- Anti-loop: `['5519971514971','5519997237404']` bloqueados no orquestrador.
- PDF analisado pelo Claude Sonnet 4.6 (não Haiku) — custo maior mas qualidade necessária pra documentos jurídicos.
