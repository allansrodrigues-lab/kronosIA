---
name: test-harness
description: Roda a suite de regressão dos bots WhatsApp Kronos (Aurora e OdontoVita). Usa payloads de teste identificáveis (remoteJid 5500TEST*) para validar classificação de intent sem interferir com clientes reais. Dispare antes e depois de qualquer edição em workflow de produção.
---

# Test Harness — Regressão dos Bots Kronos

Suite automatizada de testes para os orquestradores WhatsApp.

## Localização no VPS

```
/docker/test-harness/run_tests.py
```

## Como rodar

```bash
# Todos os bots
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "python3 /docker/test-harness/run_tests.py"

# Só Aurora
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "python3 /docker/test-harness/run_tests.py aurora"

# Só Odonto
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "python3 /docker/test-harness/run_tests.py odonto"
```

Exit code 0 = tudo passou. Exit code 1 = há falhas. Útil para CI ou pre-deploy checks.

## Cenários cobertos

### Aurora (7 cenários)
| ID  | Cenário                    | Expected Intent     |
|-----|----------------------------|---------------------|
| A01 | AGENDAR claro              | AGENDAR             |
| A02 | Pergunta de preço          | DUVIDA_PRECO        |
| A03 | Pergunta de procedimento   | DUVIDA_PROCEDIMENTO |
| A04 | Reclamação explícita       | RECLAMACAO          |
| A05 | Agendamento ambíguo        | AGENDAR             |
| A06 | Dúvida pós-procedimento    | POS_PROCEDIMENTO    |
| A07 | **Endereço picado (2 msgs)**| AGENDAR ← valida buffering |

### OdontoVita (5 cenários)
| ID  | Cenário                    | Expected Intent     |
|-----|----------------------------|---------------------|
| O01 | AGENDAR claro              | AGENDAR             |
| O02 | Pergunta de preço          | DUVIDA_PRECO        |
| O03 | Pergunta de procedimento   | DUVIDA_PROCEDIMENTO |
| O04 | Reclamação explícita       | RECLAMACAO          |
| O05 | Agendamento ambíguo        | AGENDAR             |

## Como identificar dados de teste no n8n

- `remoteJid`: começa com `5500TEST` (ex: `5500TESTA01`)
- `pushName`: `[TESTE AUTOMATICO - NAO CLIENTE REAL]`
- `id` da mensagem: começa com `TEST-`

Nunca confundir com execução real ao debugar.

## Quando rodar

- **Antes** de editar qualquer workflow de produção (baseline)
- **Depois** da edição (verificar regressão)
- Ao suspeitar de quebra silenciosa no Haiku ou no roteamento

## Adicionar novo cenário

Edite `SCENARIOS` no script `/docker/test-harness/run_tests.py`:

```python
{"id": "A08", "name": "LEAD_NOVO",
 "msg": "Vi no Instagram e quero saber mais sobre os serviços",
 "expected": "LEAD_NOVO"},
```

## Adicionar novo bot (novo cliente)

```python
# Em WORKFLOWS:
"clinica_nova": {
    "id":       "ID_DO_WORKFLOW_N8N",
    "webhook":  "/webhook/whatsapp-clinicanova",
    "instance": "clinicanova",
},

# Em SCENARIOS:
"clinica_nova": [
    {"id": "C01", "name": "AGENDAR", "msg": "...", "expected": "AGENDAR"},
    ...
]
```

## Notas importantes

- O script envia mensagens para uma instância real (clinica01) — a Evolution API tentará responder para o JID de teste. Como o número é falso, a resposta falha silenciosamente. Isso é esperado e não afeta a validação do intent.
- O cenário A07 testa buffering: envia 2 msgs com 0.5s de intervalo, valida que o buffer (2s) as agrupa em 1 execução classificada.
- Timeout de polling: 40 segundos por cenário. Se o Haiku estiver lento, aumentar `timeout` em `poll_for_execution`.

## Lições aprendidas (gotchas da API n8n)

1. **Chave REST API ≠ N8N_API_KEY env var** — a env var não funciona para a REST API. A chave correta é um JWT gerado em Settings → API (label: kronos-claude). Buscar no SQLite se perdida: `SELECT apiKey FROM user_api_keys WHERE label='kronos-claude'`
2. **List endpoint não retorna dados de nó** — `GET /api/v1/executions` retorna só metadados. Para ver outputs dos nós, buscar cada execução individualmente com `GET /api/v1/executions/{id}?includeData=true`
3. **Buffering cria 2 execuções** — a execução "dropada" pelo buffer tem o JID mas não tem intent (para no Decidir Processar). A execução real tem o intent. O polling precisa continuar até achar uma com intent, não parar na primeira com o JID.
4. **Bug conhecido Odonto** — "marcar consulta" → OUTRO (gap no prompt Haiku). Documentado em O06. Quando corrigir o prompt do Odonto, mudar `expected` de O06 para `AGENDAR`.

## JWT expira em

`2026-07-12` (~3.5 semanas a partir de 18/06). Quando expirar, gerar novo em Settings → API no n8n e atualizar `N8N_API_KEY` no script.
