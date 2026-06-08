# Workflow 05 — Diana (Pós-Venda) — Montagem Manual no n8n

> Siga este passo a passo depois de importar `workflow_05_pos_venda.json`.
> O JSON já cria todos os nodes — aqui você configura as credenciais e ajustes obrigatórios.

---

## Antes de começar

- [ ] Workflow 01 (Orquestrador) ativo
- [ ] Workflow 02 (Bia) ativo
- [ ] Credenciais Google Sheets configuradas no n8n
- [ ] Variáveis de ambiente configuradas (`ANTHROPIC_API_KEY`, `EVO_BASE_URL`, `EVO_API_KEY`, `EVO_INSTANCE`, `GOOGLE_SHEETS_CRM_ID`)
- [ ] Aba `Feedback_PosVenda` criada no Google Sheets (colunas: Data, Telefone, Nome, Procedimento, Nota, Comentario, Interesse_Reagendamento)

---

## Passo 1 — Importar o JSON

1. No n8n, clique em **"+ New Workflow"**
2. Menu superior → **"Import from file"**
3. Selecione `workflow_05_pos_venda.json`
4. O workflow abrirá com 14 nodes

---

## Passo 2 — Configurar credenciais Google Sheets

Há **3 nodes** de Google Sheets para configurar:

### Node "Buscar Sessão Diana"
1. Clique no node
2. Em **"Credential to connect with"** → selecione sua credencial Google Sheets
3. Confirme: Sheet = `Sessoes_Ativas`, Return All = ativo

### Node "Buscar Agendamento"
1. Clique no node
2. Em **"Credential to connect with"** → selecione sua credencial Google Sheets
3. Confirme: Sheet = `Agendamentos`, Return All = ativo

### Node "Salvar Feedback"
1. Clique no node
2. Em **"Credential to connect with"** → selecione sua credencial Google Sheets
3. Confirme: Sheet = `Feedback_PosVenda`
4. Verifique o mapeamento de colunas

### Node "Atualizar Sessão Diana"
1. Clique no node
2. Em **"Credential to connect with"** → selecione sua credencial Google Sheets
3. Confirme: Sheet = `Sessoes_Ativas`

### Node "Log Interação Diana"
1. Clique no node
2. Em **"Credential to connect with"** → selecione sua credencial Google Sheets
3. Confirme: Sheet = `Log_Interacoes`

---

## Passo 3 — Configurar "Chamar Bia" (Execute Workflow)

Este node precisa apontar para o Workflow 02:

1. Clique no node **"Chamar Bia"**
2. Em **"Workflow"** → clique no campo e selecione `02-agendamento-bia` (ou o nome que você deu ao Workflow 02)
3. Confirme **"Wait For Sub-Workflow"** = ativo
4. Salve

> Se o Workflow 02 não aparece na lista, verifique se ele está salvo (não apenas importado) no n8n.

---

## Passo 4 — Verificar conexões paralelas

O Workflow 05 tem uma particularidade: o Trigger dispara **dois nodes em paralelo** (Buscar Sessão Diana e Buscar Agendamento), e ambos convergem no "Montar Prompt Diana".

Para verificar:
1. Clique no node **"Trigger — Receber do Orquestrador"**
2. Veja que há **duas setas saindo** dele, uma para cada node de Sheets
3. Ambas as setas devem chegar ao **"Montar Prompt Diana"**

Se estiver faltando alguma conexão:
- Arraste da bolinha de saída do Trigger para o node de Sheets faltante
- Arraste da bolinha de saída do node de Sheets para o "Montar Prompt Diana"

---

## Passo 5 — Verificar Switch por Ação

O Switch tem **4 outputs**. Verifique que cada saída está conectada:

| Output | Conectado a |
|---|---|
| 1 — Passar para Bia | Preparar Passagem para Bia |
| 2 — Escalar Humano | Preparar Sessão (direto) |
| 3 — Salvar Feedback | Salvar Feedback |
| Fallback | Preparar Sessão (direto) |

E a saída do **"Salvar Feedback"** também deve ir para **"Preparar Sessão"**.

---

## Passo 6 — Ativar o workflow

1. Clique em **"Save"** (Ctrl+S)
2. Toggle no canto superior direito → **"Active"**
3. O status deve ficar verde

---

## Passo 7 — Teste manual (Trigger simulado)

1. Clique no node **"Trigger — Receber do Orquestrador"**
2. Clique em **"Test step"**
3. Cole o JSON abaixo e clique em **"Run"**:

```json
{
  "telefone": "5511999999999",
  "nome": "Ana Teste",
  "texto": "Oi",
  "remoteJid": "5511999999999@s.whatsapp.net",
  "instancia": "clinica",
  "timestamp": 1748908800,
  "messageId": "TEST-DIANA-001",
  "intent": "POS_PROCEDIMENTO"
}
```

**Esperado:**
- Node "Buscar Agendamento" retorna lista de agendamentos (pode estar vazia no teste)
- Node "Montar Prompt Diana" prepara o body com `procedimento_realizado = "procedimento"` (fallback, pois não há agendamento de teste)
- Node "Claude Sonnet — Diana" retorna JSON com `etapa = "checkin"`
- Node "Parsear Resposta Diana" extrai a mensagem
- Nenhuma mensagem é enviada pelo WhatsApp (não afeta cliente real)

---

## Passo 8 — Teste com agendamento real

Para testar com um procedimento real, primeiro verifique um registro na aba `Agendamentos` com:
- `Telefone` = o número que você vai testar
- `Status` = `confirmado`
- `Procedimento` = ex: `Limpeza de Pele Profunda`

Depois repita o teste do Passo 7 com esse telefone.

**Esperado:** A mensagem da Diana menciona o procedimento correto.

---

## Checklist de validação final

- [ ] Workflow importado e ativo
- [ ] Credenciais Google Sheets configuradas nos 5 nodes de Sheets
- [ ] "Chamar Bia" aponta para o Workflow 02 correto
- [ ] Conexões paralelas do Trigger verificadas
- [ ] Switch com 4 outputs todos conectados
- [ ] Aba `Feedback_PosVenda` existe no Sheets
- [ ] Teste manual executado sem erro
- [ ] Intent `POS_PROCEDIMENTO` adicionado no Workflow 01 (ver `workflow_01_conexao_diana.md`)

---

## Erros comuns

| Erro | Causa | Solução |
|---|---|---|
| "Cannot read property 'all' of undefined" | Node de Sheets não encontrado pelo nome | Verifique se o nome do node está exato: "Buscar Sessão Diana" e "Buscar Agendamento" |
| Feedback não aparece no Sheets | Aba `Feedback_PosVenda` não existe | Crie a aba com as colunas corretas |
| Diana não sabe o procedimento | `Status` do agendamento não é `confirmado` | Verifique o valor exato na coluna Status do Sheets |
| "Chamar Bia" falha | Workflow 02 não está ativo | Ative o Workflow 02 antes de testar |
