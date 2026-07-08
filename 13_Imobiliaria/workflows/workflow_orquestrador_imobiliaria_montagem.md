# Montagem — Orquestrador Imobiliária (Schalletti) no n8n

> Segue a arquitetura validada dos orquestradores Kronos (Aurora/Léa). Reuso ~80%:
> clonar o orquestrador da Advocacia e adaptar os pontos abaixo é mais rápido que montar do zero.

## Nomes no n8n

```
[Imobiliária] - Orquestrador Schalletti (v1.0)     ← principal
[Imobiliária] - Sofia Atendimento (v1.0)           ← sub-workflow matching/qualificação
[Imobiliária] - Calculadora Financiamento (v1.0)   ← sub-workflow ⭐
[Imobiliária] - CRM Adapter (v1.0)                 ← sub-workflow (ver doc própria)
```

## Fluxo do orquestrador

```
Webhook (chavinha /imobiliaria na Central de Demos)
 → Filtro fromMe/grupo → Buffer/debounce (2-3s, tabela buffer)
 → IF áudio? → transcrição (motor Aurora ♻️) → texto
 → CRM Adapter: upsert_lead + carregar sessão (Sessoes_Imobiliaria)
 → Montar Prompt Haiku (prompt de classificação em agentes/00_orquestrador_imobiliaria.md)
 → Claude Haiku (claude-haiku-4-5-20251001) → intent
 → Switch por intent:
      COMPRAR / ALUGAR / PROPRIETARIO / OUTRO → Execute Workflow: Sofia
      FINANCIAMENTO                            → Execute Workflow: Calculadora → volta p/ Sofia formatar
      VISITA                                   → motor agendamento (clonar Bia: Google Calendar + notificar corretor)
      DOCUMENTO                                → leitor de PDF (motor Advocacia ♻️)
      POS_VISITA                               → follow-up (motor Diana ♻️)
      RECLAMACAO                               → escalação: msg p/ EVO_TEAM_NUMBER + registro
 → Enviar resposta (Evolution API) → CRM Adapter: log_interacao + salvar sessão
```

## Sub-workflow Sofia

1. Execute Workflow Trigger (recebe sessão + mensagem + intent)
2. CRM Adapter `get_imoveis` (filtrado pela finalidade/faixa da sessão — só quando status ≥ matching; economiza tokens)
3. Montar prompt (`agentes/01_agente_atendimento_sofia.md`) injetando `${carteiraImoveis}`, sessão e histórico
4. Claude Sonnet 5 (`claude-sonnet-5`, **sem temperature**)
5. Parser: `content.find(b => b.type === 'text')?.text` (⚠️ nunca `content[0].text` — bug do thinking)
6. Atualizar sessão: perfil coletado, `imoveis_enviados` (append), status
7. Retornar texto ao orquestrador

## Sub-workflow Calculadora

1. Trigger → validar dados (valor, entrada, prazo; se citou código SCH-*, buscar preço via CRM Adapter)
2. Faltou dado → retorna pergunta da Sofia (uma por vez)
3. Code node `calcular_financiamento` (código em `agentes/02_agente_calculadora_financiamento.md`)
4. Sonnet 5 formata no tom da Sofia (com os 3 disclaimers) → retorna

## Checklist de publicação (pegadinhas conhecidas)

- [ ] Editar/criar sempre na versão **publicada** (workflow_history), não no draft
- [ ] Publicar **todos os sub-workflows** antes do orquestrador (Execute Workflow exige publicado)
- [ ] Restart do n8n após publicar (unpublish/publish sem restart não aplica)
- [ ] Error Trigger → Error Handler central (`X29vC9p5WB38iZFI`) em TODOS os 4 workflows
- [ ] Env vars: `CRM_PROVIDER=sheets` + `GOOGLE_SHEETS_CRM_ID` da planilha própria do nicho
- [ ] Registrar a demo na chavinha `/imobiliaria` (skill kronos-central-demos)
- [ ] Casos de teste no test harness (payloads `5500TEST*`) — cobrir os 9 intents
- [ ] Não referenciar nodes por nome depois de renomear (`$('Montar Prompt Haiku')` quebra)
