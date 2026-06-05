# Fluxos de Automação — n8n

Esta pasta contém a documentação de cada fluxo implementado no n8n. Cada arquivo segue o mesmo template:

1. **Objetivo** — o que o fluxo resolve
2. **Gatilho** — o que dispara o fluxo
3. **Passos** — sequência de nós no n8n
4. **Integrações usadas**
5. **Tratamento de erros**
6. **Métricas geradas**

## Mapa dos fluxos

| Arquivo | Fluxo | Status |
|---|---|---|
| `01_fluxo_agendamento.md` | Agendamento + confirmação 24h antes | Documentado |
| `02_fluxo_whatsapp.md` | Atendimento via WhatsApp (orquestrador IA) | Documentado |
| `03_fluxo_pos_venda.md` | Pós-venda D+1 / D+7 / D+30 | Documentado |
| `04_fluxo_marketing.md` | Captação e qualificação de leads | Documentado |

## Convenção de nomes dos workflows no n8n

```
[Categoria] - [Nome] (vX.Y)

Exemplos:
[Agendamento] - Criar evento (v1.0)
[WhatsApp]   - Orquestrador principal (v1.2)
[PósVenda]   - Followup D+7 (v1.0)
```

## Padrão de erro

Todo fluxo deve ter um nó **Error Trigger** que:
1. Loga o erro na planilha de monitoramento
2. Envia alerta no Telegram do implementador
3. Em caso de falha de IA → escala para humano no WhatsApp
