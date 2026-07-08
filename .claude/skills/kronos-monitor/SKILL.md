---
name: kronos-monitor
description: Padrão de monitoramento de erros da Kronos — Error Handler centralizado + Self-Healing Monitor. Use ao criar novo workflow, adicionar errorWorkflow a cliente existente, investigar falhas recorrentes, ou configurar o ciclo de alertas WA.
---

# Kronos Monitor — Error Handler + Self-Healing Monitor

Dois workflows de infraestrutura em produção no VPS Kronos.

## Arquitetura

```
Qualquer workflow falha
    └── n8n dispara settings.errorWorkflow
            └── kronos-error-handler (X29vC9p5WB38iZFI)
                    ├── Formatar Erro (diagnóstico de tipo)
                    ├── Log_Monitoramento (Google Sheets append)
                    └── Notificar Equipe WhatsApp (EVO_TEAM_NUMBER)

Cron 30min
    └── kronos-monitor-selfhealing (ADmfpDIilh48WwV3)
            ├── Ler Log_Monitoramento (últimas N rows)
            ├── Filtrar erros das últimas 31min
            └── (se houver) Enviar Digest WA com resumo agrupado por workflow
```

## IDs dos workflows

| Workflow | ID | Status |
|---|---|---|
| kronos-error-handler | `X29vC9p5WB38iZFI` | ativo |
| kronos-monitor-selfhealing | `ADmfpDIilh48WwV3` | ativo |

## Aba Log_Monitoramento

**Atualizado 05/07:** Sheet ID `1tOXVM8frTwxbhCR1Gmb2dyPFNks8INCNSKWeg9t1UK4` (CRM Interno — migrou da planilha compartilhada, ver skill de separação de planilhas / memória `separacao-planilhas-nichos`).
Colunas: `Timestamp | Workflow | Ultimo_No | Tipo_Erro | Mensagem | Exec_ID | Status`

Tipos de erro diagnosticados automaticamente:
- `AUTH_401` — API key inválida/expirada
- `SHEETS` — falha na planilha Google
- `TIMEOUT` — timeout de rede
- `WHATSAPP` — erro na Evolution API
- `LLM` — erro na API Anthropic
- `GERAL` — outros

## Aplicar errorWorkflow em novo workflow

```js
// Via MCP n8n_update_partial_workflow:
{ type: "updateSettings", settings: { errorWorkflow: "X29vC9p5WB38iZFI" } }
```

**Regra:** todo novo workflow criado para qualquer cliente deve receber esta configuração antes de ativar.

## Todos os workflows com errorWorkflow configurado (18/06/2026)

Orquestradores: `Orq01RouterV2aa1`, `01-orquestrador-odonto`, `4X99dI4CyL0IWbNI`, `QEawJtNsqlNGwrw0`
Sub-workflows: `02-agendamento-bia`, `02-agendamento-odonto`, `TDJQkNQDJh9PnmSh`, `03-atendimento-odonto`, `wItuI9j8dVSbq0F0`, `TZDQobW44zZwkjOB`, `jyCWf2czZn0JTru8`
Utilitários: `vGfBm7cdjsESJtIH`, `UrHGeigVUnisIMg1`, `2hYQv4sOQq5AOXmt`, `Enk8spJl85mFAQTD`, `PmVvapxMMtjH0GsC`, `smKNu8Nq9o8Ht3aQ`, `ytKAqBnxBKQanuEC`, `LYKIjXBKHxSZXQcN`, `VFtnXxDmZYEf1saI`

**NÃO aplicar em:** `X29vC9p5WB38iZFI` (o próprio handler) e `ADmfpDIilh48WwV3` (o monitor) — causaria loop.

## Gotcha: Call '03-bia-ref' bloqueia republish

Workflows `05-pos-venda-diana` e `03-atendimento-clara` tinham nó morto `Call '03-bia-ref'` referenciando workflow arquivado `jNvIB83x2sWWbkW1`. Qualquer tentativa de update via MCP falhava com VALIDATION_ERROR. Fix: `{ type: "removeNode", name: "Call '03-bia-ref'" }` + continueOnError.

## Env vars necessárias

Já configuradas no n8n:
- `EVO_BASE_URL` — base URL da Evolution API
- `EVO_API_KEY` — chave da Evolution
- `EVO_INSTANCE` — instância ativa (ex: `clinica01`)
- `EVO_TEAM_NUMBER` — número do grupo/equipe para alertas

## Self-Healing Monitor — como funciona

- Roda a cada 30min via Schedule Trigger
- Lê TODAS as rows de `Log_Monitoramento`
- Filtra rows com `Status=ERRO` e `Timestamp >= agora - 31min`
- Se 0 erros → execução termina silenciosamente (sem notificação)
- Se erros → agrupa por Workflow, conta ocorrências, lista tipos de erro, envia digest WA

**Formato do digest:**
```
🔍 Kronos Monitor — Digest 30min

Erros detectados: N

• workflow-x: 2x (AUTH_401)
• workflow-y: 1x (SHEETS)

Verifique o n8n.
```

## Self-heal v2 (implementado 05/07) — teste horário + auto-fix limitado

Camada nova em cima da existente (não substitui, não duplica alerta):

- **`selfheal.py`** no VPS (`/docker/test-harness/selfheal.py`, fonte `07_Recursos/test_harness/selfheal.py`), cron `0 * * * *`. Roda a suite de 13 testes (skill `test-harness`); se passar, não faz nada.
- Se falhar, tenta **NO MÁXIMO 1 fix seguro** (nunca edita código de nó, nunca mexe fora dos 2 workflows monitorados):
  - Container `n8n-xve0-n8n-1` parado → `docker restart`.
  - Workflow monitorado (Aurora `Orq01RouterV2aa1` / Odonto `01-orquestrador-odonto`) desativado → reativa via API.
  - Qualquer outra causa (401, cache, bug de prompt) → **não tenta corrigir sozinho**, só diagnostica.
- Roda a suite de novo uma vez. Se voltou a passar → loga `Status=AUTO-CORRIGIDO` (silencioso, não alerta). Se continua falhando → loga `Status=ERRO` via o workflow **`kronos-selfheal-ingest`** (`gwISohwPawZPhPj5`, webhook `/webhook/selfheal-log`) na mesma planilha `Log_Monitoramento` — o `kronos-monitor-selfhealing` (30min, já existia) detecta e alerta sozinho, sem lógica de notificação nova.
- Decisão deliberada de escopo (pedido original era "corrigir qualquer causa raiz até ficar verde"): reduzido pra só 2 fixes bem entendidos e reversíveis. Auto-editar workflow publicado sem revisão humana tem risco real de quebra silenciosa.
- **Não testado no caminho de falha real** (só o caminho feliz, 13/13 verde). Se aparecer `Status=ERRO` do Test-Harness na planilha, conferir se o diagnóstico fez sentido antes de confiar cegamente.

Detalhe completo: memória `monitor-pattern-kronos` (seção "Self-healing v2").
