# Guia de Montagem Manual — Workflow 04 Lembrete 24h

> Siga esta ordem exata. Para contexto técnico completo, consulte `workflow_04_lembrete_24h_guide.md`.
> Este workflow é **independente** — roda por Cron, não precisa do Orquestrador.

---

## Antes de começar

1. Adicione as 2 colunas novas na aba `Agendamentos`:
   - Coluna `Lembrete_Enviado` (após a coluna `Observacoes`)
   - Coluna `Confirmado_Pelo_Cliente`
2. Crie a aba `Log_Lembretes` com as colunas:
   `Data_Hora | Telefone | Nome | Procedimento | Data_Agendamento | Hora_Agendamento | Status`
3. Crie um **novo workflow em branco** no n8n
4. Renomeie para: **`04-lembrete-24h`**
5. Salve com **Ctrl+S**

---

## PARTE 1 — Adicionar os nodes

---

### Node 1 — Cron — A cada hora

**Como adicionar:**
- Clique no `+` no canvas
- Digite: `schedule trigger`
- Selecione **Schedule Trigger**

**O que configurar:**

| Campo | Valor |
|---|---|
| Trigger Interval | `Custom (Cron Expression)` |
| Expression | `0 9-18 * * 1-6` |

> Esta expressão: a cada hora cheia, das 9h às 18h, de segunda a sábado.
> Para testar a qualquer hora: use `* * * * *` (a cada minuto) temporariamente.

**Renomear:** `Cron — A cada hora`

---

### Node 2 — Calcular Janela 24h

**Como adicionar:**
- `+` → `code` → **Code**

**Cole o código:**

```javascript
const agora = new Date();
const amanha = new Date(agora.getTime() + 24 * 60 * 60 * 1000);
const dataAmanha = amanha.toISOString().split('T')[0];

const horaInicio = agora.getHours().toString().padStart(2, '0') + ':00';
const horaFim = ((agora.getHours() + 1) % 24).toString().padStart(2, '0') + ':00';

return [{
  json: {
    dataAmanha,
    horaInicio,
    horaFim,
    agoraBR: agora.toLocaleString('pt-BR')
  }
}];
```

**Renomear:** `Calcular Janela 24h`

---

### Node 3 — Buscar Agendamentos Amanhã

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Get Many Rows` |
| Document | ID da planilha |
| Sheet Name | `Agendamentos` |
| Return All Rows | **Ativo** |

**"Continue on Fail":** ative.

**Renomear:** `Buscar Agendamentos Amanhã`

---

### Node 4 — Filtrar Agendamentos

**Como adicionar:**
- `+` → `code` → **Code**

**Cole o código:**

```javascript
const dataAmanha = $('Calcular Janela 24h').first().json.dataAmanha;
const todos = $input.all();

const agendamentosAmanha = todos.filter(item => {
  const ag = item.json;
  return (
    ag.Data === dataAmanha &&
    ag.Status === 'confirmado' &&
    ag.Lembrete_Enviado !== 'SIM' &&
    ag.Telefone
  );
});

if (agendamentosAmanha.length === 0) return [];

return agendamentosAmanha.map(item => ({ json: item.json }));
```

**"Continue on Fail":** ative.

> Se não houver agendamentos para amanhã, retorna 0 itens e o workflow para — sem erros.

**Renomear:** `Filtrar Agendamentos`

---

### Node 5 — Para Cada Agendamento

**Como adicionar:**
- `+` → `loop over items` → **Loop Over Items**

> Se não encontrar "Loop Over Items", use **Split In Batches**:

| Campo | Valor |
|---|---|
| Batch Size | `1` |

**Renomear:** `Para Cada Agendamento`

> Este node tem **2 saídas**: `loop` (item atual) e `done` (quando terminar).
> - Saída `loop` → conecta para o próximo node
> - Saída `done` → pode deixar desconectada (workflow termina)

---

### Node 6 — Montar Mensagem Lembrete

**Como adicionar:**
- Da saída **`loop`** do node anterior: `+` → `code` → **Code**

**Cole o código:**

```javascript
const ag = $input.first().json;
const { Nome, Procedimento, Data, Hora, Profissional, Telefone } = ag;

let dataFormatada = Data;
try {
  const d = new Date(Data + 'T12:00:00');
  const diasSemana = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira',
                      'quinta-feira', 'sexta-feira', 'sábado'];
  dataFormatada = `${diasSemana[d.getDay()]}, ${d.getDate().toString().padStart(2,'0')}/${(d.getMonth()+1).toString().padStart(2,'0')}`;
} catch(e) {}

const mensagem =
  `Olá, ${Nome}! 💛\n\n` +
  `Lembrando seu agendamento *amanhã*:\n` +
  `📋 ${Procedimento}\n` +
  `📅 ${dataFormatada} às ${Hora}\n` +
  (Profissional ? `👩‍⚕️ ${Profissional}\n` : '') +
  `\nResponda:\n` +
  `*1* — Confirmar presença ✅\n` +
  `*2* — Quero remarcar 🔄`;

return [{
  json: { ...ag, mensagem, telefone: Telefone }
}];
```

**Renomear:** `Montar Mensagem Lembrete`

---

### Node 7 — Enviar WhatsApp

**Como adicionar:**
- `+` → `http request` → **HTTP Request**

**O que configurar:**

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `={{ $env.EVO_BASE_URL }}/message/sendText/{{ $env.EVO_INSTANCE }}` |

**Headers:**

| Name | Value |
|---|---|
| `apikey` | `={{ $env.EVO_API_KEY }}` |
| `Content-Type` | `application/json` |

**Body → JSON:**
```
={{ { number: $json.telefone, text: $json.mensagem } }}
```

**Renomear:** `Enviar WhatsApp`

---

### Node 8 — Marcar Lembrete Enviado

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Update Row` |
| Document | ID da planilha |
| Sheet | `Agendamentos` |
| Lookup Column | `ID` |
| Lookup Value | `={{ $json.ID }}` |

**Campo a atualizar:**

| Column | Value |
|---|---|
| `Lembrete_Enviado` | `SIM` |

**"Continue on Fail":** ative.

**Renomear:** `Marcar Lembrete Enviado`

---

### Node 9 — Log Lembrete

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Append Row` |
| Document | ID da planilha |
| Sheet | `Log_Lembretes` |

**Campos:**

| Column | Value |
|---|---|
| `Data_Hora` | `={{ new Date().toLocaleString('pt-BR') }}` |
| `Telefone` | `={{ $json.telefone }}` |
| `Nome` | `={{ $json.Nome }}` |
| `Procedimento` | `={{ $json.Procedimento }}` |
| `Data_Agendamento` | `={{ $json.Data }}` |
| `Hora_Agendamento` | `={{ $json.Hora }}` |
| `Status` | `enviado` |

**Renomear:** `Log Lembrete`

**Após o Log, conecte de volta ao node `Para Cada Agendamento`** para fechar o loop:
- Arraste uma seta do `Log Lembrete` → `Para Cada Agendamento`

---

## PARTE 2 — Verificar as conexões

```
[Cron — A cada hora]
         ↓
[Calcular Janela 24h]
         ↓
[Buscar Agendamentos Amanhã]
         ↓
[Filtrar Agendamentos]       ← 0 itens = para aqui (sem erro)
         ↓ (tem itens)
[Para Cada Agendamento] ←────────────────────────┐
    ↓ (saída loop)                               │
[Montar Mensagem Lembrete]                       │
         ↓                                       │
[Enviar WhatsApp]                                │
         ↓                                       │
[Marcar Lembrete Enviado]                        │
         ↓                                       │
[Log Lembrete] ──────────────────────────────────┘ (loop)
    ↓ (saída done do Loop Over Items — opcional)
    (fim)
```

---

## PARTE 3 — Ativar e testar

**1. Salve** — Ctrl+S

**2. Insira um agendamento de teste** na aba `Agendamentos`:

| Campo | Valor |
|---|---|
| ID | AGD-TESTE-001 |
| Telefone | seu número (ex: 5511999999999) |
| Nome | Seu Nome |
| Procedimento | Limpeza de Pele Profunda |
| Data | *data de amanhã* (ex: 2026-06-04) |
| Hora | 14:00 |
| Profissional | Dra. Marina |
| Status | confirmado |
| Lembrete_Enviado | *(deixe vazio)* |

**3. Execute manualmente:**
- No n8n → botão **"Execute Workflow"** (play manual, não o toggle de ativar)

**4. Verificar resultado:**
- Você recebe mensagem no WhatsApp com opções 1/2
- Na aba `Agendamentos`, a linha agora tem `Lembrete_Enviado = SIM`
- Na aba `Log_Lembretes`, nova linha com `Status = enviado`

**5. Ative o workflow:**
- Toggle verde no canto superior direito

---

## PARTE 4 — Checklist final

- [ ] 9 nodes criados e renomeados
- [ ] 2 colunas novas adicionadas na aba `Agendamentos` (`Lembrete_Enviado`, `Confirmado_Pelo_Cliente`)
- [ ] Aba `Log_Lembretes` criada com colunas corretas
- [ ] Expressão cron configurada: `0 9-18 * * 1-6`
- [ ] Loop fechado: `Log Lembrete` conecta de volta a `Para Cada Agendamento`
- [ ] Workflow ativo (toggle verde)
- [ ] Teste manual com agendamento de amanhã executado com sucesso
- [ ] Mensagem recebida no WhatsApp com opções 1 e 2
