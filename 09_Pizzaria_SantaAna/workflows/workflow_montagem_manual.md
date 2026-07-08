# Montagem Manual — Pizzaria Bella Massa

Guia passo a passo para importar e ativar os workflows no n8n quando o cliente fechar contrato.

---

## Pré-requisitos

- [ ] Número WhatsApp da pizzaria com chip disponível
- [ ] Instância Evolution criada (`instancia_santaana` — nome a definir)
- [ ] Planilha Google Sheets criada e compartilhada com a service account
- [ ] Abas da planilha criadas (ver seção abaixo)
- [ ] Variáveis de ambiente configuradas no n8n

---

## 1. Configurar variáveis de ambiente no n8n

**Settings → Variables** — adicionar:

| Variável | Valor |
|---|---|
| `ANTHROPIC_API_KEY` | (já existe — compartilhada) |
| `EVO_BASE_URL` | `https://evo.kronosintelligence.com.br` |
| `EVO_API_KEY` | `kronos-evo-key-2024` |
| `EVO_INSTANCE_SANTAANA` | nome da instância criada (ex: `santaana`) |
| `EVO_TEAM_NUMBER_SANTAANA` | número do grupo da equipe (com 55 + DDD) |
| `GOOGLE_SHEETS_CRM_ID_SANTAANA` | ID da planilha Google Sheets do cliente |

---

## 2. Criar a planilha Google Sheets

Criar planilha nova e compartilhar com: `kronos-n8n@kronos-ia-498605.iam.gserviceaccount.com` (Editor)

**Abas obrigatórias** (criar com exatamente esses nomes):

| Aba | Colunas |
|---|---|
| `Sessoes_Ativas` | Telefone, Nome, Agente, Status, Historico, Dado_Temp, UltimaInteracao |
| `Log_Pedidos` | Timestamp, Telefone, Nome, Acao, CarrinhoJSON |
| `Pedidos` | Timestamp, Telefone, Nome, CarrinhoJSON, Status |

---

## 3. Criar instância Evolution

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "curl -s -X POST https://evo.kronosintelligence.com.br/instance/create \
  -H 'Content-Type: application/json' \
  -H 'apikey: kronos-evo-key-2024' \
  -d '{
    \"instanceName\": \"santaana\",
    \"webhook\": \"https://n8n.kronosintelligence.com.br/webhook/whatsapp-santaana\",
    \"webhookByEvents\": false,
    \"events\": [\"MESSAGES_UPSERT\"]
  }'"
```

Depois escanear o QR:
```bash
curl -s https://evo.kronosintelligence.com.br/instance/connect/santaana \
  -H 'apikey: kronos-evo-key-2024' | python3 -c "import sys,json; print(json.load(sys.stdin).get('base64',''))"
```
Usar `/fix-n8n-auth` se der 401. Mostrar QR ao cliente via Read no chat.

---

## 4. Importar os workflows

```bash
# Na máquina local (Windows) — copiar os JSONs para o VPS
scp -i ~/.ssh/kronos_vps "09_Pizzaria_SantaAna/workflows/workflow_01_orquestrador_santaana.json" root@2.24.101.180:/tmp/
scp -i ~/.ssh/kronos_vps "09_Pizzaria_SantaAna/workflows/workflow_02_agente_pedido_santaana.json" root@2.24.101.180:/tmp/

# No VPS — importar
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "
  docker exec n8n-xve0-n8n-1 n8n import:workflow --input=/tmp/workflow_01_orquestrador_santaana.json
  docker exec n8n-xve0-n8n-1 n8n import:workflow --input=/tmp/workflow_02_agente_pedido_santaana.json
"
```

---

## 5. Ativar os workflows

```bash
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 "
  docker exec n8n-xve0-n8n-1 n8n update:workflow --id=01-orquestrador-santaana --active=true
  docker exec n8n-xve0-n8n-1 n8n update:workflow --id=02-agente-pedido-santaana --active=true
  docker restart n8n-xve0-n8n-1
"
```

⚠️ **O orquestrador exige que o sub-workflow da Ana esteja publicado.** Publicar os dois antes de reiniciar.

---

## 6. Smoke test

```bash
curl -X POST https://n8n.kronosintelligence.com.br/webhook/whatsapp-santaana \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "santaana",
    "data": {
      "key": { "remoteJid": "5519999999999@s.whatsapp.net", "fromMe": false, "id": "TEST-SA-01" },
      "pushName": "Teste",
      "message": { "conversation": "Oi, quero pedir uma pizza" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

Verificar no n8n se a execução aparece com `status=success` e se o número da pizzaria recebeu a resposta da Ana.

---

## 7. Checklist de go-live

- [ ] Variáveis de ambiente salvas no n8n
- [ ] Planilha criada com as 3 abas e cabeçalhos
- [ ] Instância Evolution `santaana` conectada (QR escaneado)
- [ ] Workflows importados e ativados
- [ ] n8n reiniciado
- [ ] Smoke test passou
- [ ] Cliente testou ao vivo e aprovou
- [ ] Número do grupo da equipe configurado em `EVO_TEAM_NUMBER_SANTAANA`

---

## Estrutura do carrinho (Dado_Temp na sessão)

```json
{
  "etapa": "confirmando",
  "itens": [
    {
      "tipo": "pizza",
      "sabor": "Calabresa",
      "metade2": "Bacon",
      "borda": "requeijao",
      "qtd": 1,
      "preco": 50.00
    }
  ],
  "total": 50.00,
  "tipo_entrega": "entrega",
  "endereco": "Rua das Flores, 123",
  "pagamento": "pix"
}
```

## Fluxo de finalização de pedido

Quando `acao = finalizar_pedido`:
1. n8n monta o resumo formatado com todos os itens, endereço e total
2. Envia para o grupo da equipe no WhatsApp (`EVO_TEAM_NUMBER_SANTAANA`)
3. Salva na aba `Pedidos` com status `aguardando_confirmacao`
4. A equipe confirma manualmente com o cliente (tempo de entrega + forma de pagamento)
