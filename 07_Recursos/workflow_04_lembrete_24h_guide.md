# Workflow 04 — Lembrete 24h (Guia de Configuração)

> Workflow Cron independente: roda a cada hora, busca agendamentos do dia seguinte
> na aba `Agendamentos`, e envia mensagem de confirmação pelo WhatsApp.
> O cliente responde 1 para confirmar ou 2 para remarcar.

---

## Visão geral do fluxo

```
[Cron — A cada hora]
         ↓
[Calcular Janela 24h]          ← Code: data de amanhã, faixa 24-25h
         ↓
[Buscar Agendamentos Amanhã]   ← Sheets: filtra Agendamentos pela data
         ↓
[Tem Agendamentos?]            ← IF: quantidade > 0
         ↓ SIM
[Para Cada Agendamento]        ← SplitInBatches (1 a 1)
         ↓
[Já foi lembrado?]             ← IF: campo Lembrete_Enviado != 'SIM'
         ↓ NÃO
[Montar Mensagem Lembrete]     ← Code: formata a mensagem
         ↓
[Enviar WhatsApp]              ← HTTP: Evolution API
         ↓
[Marcar Lembrete Enviado]      ← Sheets: atualiza Agendamentos → Lembrete_Enviado = SIM
         ↓
[Log Lembrete]                 ← Sheets: append em Log_Lembretes
```

**Total: 9 nodes**

> **Fluxo de resposta do cliente** (quando responde "1" ou "2") é tratado pelo
> Workflow 01 (Orquestrador) → Aurora classifica como AGENDAR → Bia cuida do restante.
> Não há um workflow separado para processar a resposta — o fluxo existente já funciona.

---

## Atualização na aba `Agendamentos`

Adicione 2 colunas novas na aba `Agendamentos`:

| Coluna | Tipo | Descrição |
|---|---|---|
| `Lembrete_Enviado` | Texto | `SIM` após envio; vazio = não enviado |
| `Confirmado_Pelo_Cliente` | Texto | `SIM` / `NAO` / vazio (preenchido pela resposta) |

---

## Nova aba: `Log_Lembretes`

| Data_Hora | Telefone | Nome | Procedimento | Data_Agendamento | Hora_Agendamento | Status |
|---|---|---|---|---|---|---|
| 03/06/2026 09:00 | 5511999 | Maria | Limpeza de Pele | 2026-06-04 | 14:00 | enviado |

---

## Node 1 — Cron — A cada hora (Schedule Trigger)

**Tipo:** Schedule Trigger

| Campo | Valor |
|---|---|
| Trigger Interval | `Hours` |
| Hours Between Triggers | `1` |

> Para produção, rode de hora em hora entre 8h e 20h.
> No n8n, configure uma expressão cron: `0 8-20 * * *` (a cada hora entre 8h e 20h).
> Na UI: selecione "Custom (Cron Expression)" e cole `0 8-20 * * *`.

**Renomear:** `Cron — A cada hora`

---

## Node 2 — Calcular Janela 24h (Code)

```javascript
const agora = new Date();

// Amanhã = daqui 24h
const amanha = new Date(agora.getTime() + 24 * 60 * 60 * 1000);

// Formato YYYY-MM-DD para comparar com a coluna Data da aba Agendamentos
const dataAmanha = amanha.toISOString().split('T')[0];

// Faixa: 24h a 25h a partir de agora (evita duplicata na próxima hora)
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

## Node 3 — Buscar Agendamentos Amanhã (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Get Many Rows` |
| Sheet | `Agendamentos` |
| Return All Rows | Ativo |

Configure **"Continue On Fail"** ativo.

> O filtro exato será feito no Code node seguinte.
> Retorna todos os agendamentos — o Code filtra por data + status.

**Renomear:** `Buscar Agendamentos Amanhã`

---

## Node 4 — Tem Agendamentos? (Code + IF)

Use um **Code node** para filtrar:

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

Configure **"Continue On Fail"** ativo (se retornar 0 itens, o workflow para graciosamente).

**Renomear:** `Filtrar Agendamentos`

---

## Node 5 — Para Cada Agendamento (Loop Over Items)

**Tipo:** Loop Over Items (ou SplitInBatches com batch size = 1)

No n8n, use o node **Loop Over Items** ou **Split In Batches**:

| Campo | Valor |
|---|---|
| Batch Size | `1` |

> Isso garante que cada agendamento seja processado individualmente,
> com a Evolution API recebendo uma mensagem por vez.

**Renomear:** `Para Cada Agendamento`

---

## Node 6 — Montar Mensagem Lembrete (Code)

```javascript
const ag = $input.first().json;

const { Nome, Procedimento, Data, Hora, Profissional, Telefone } = ag;

// Formata a data para exibição amigável
let dataFormatada = Data;
try {
  const d = new Date(Data + 'T12:00:00');
  const diasSemana = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado'];
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
  json: {
    ...ag,
    mensagem,
    telefone: Telefone
  }
}];
```

**Renomear:** `Montar Mensagem Lembrete`

---

## Node 7 — Enviar WhatsApp (HTTP Request)

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

## Node 8 — Marcar Lembrete Enviado (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Update Row` |
| Sheet | `Agendamentos` |
| Lookup Column | `ID` |
| Lookup Value | `={{ $json.ID }}` |

**Campos a atualizar:**

| Column | Value |
|---|---|
| `Lembrete_Enviado` | `SIM` |

Configure **"Continue On Fail"** ativo.

**Renomear:** `Marcar Lembrete Enviado`

---

## Node 9 — Log Lembrete (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Append Row` |
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

---

## Diagrama de conexões

```
[Cron — A cada hora]
         ↓
[Calcular Janela 24h]
         ↓
[Buscar Agendamentos Amanhã]
         ↓
[Filtrar Agendamentos]      ← retorna 0 itens = workflow para aqui
         ↓ (tem itens)
[Para Cada Agendamento]
         ↓ (item atual)
[Montar Mensagem Lembrete]
         ↓
[Enviar WhatsApp]
         ↓
[Marcar Lembrete Enviado]
         ↓
[Log Lembrete]
         ↓
[Para Cada Agendamento] ← loop volta para o próximo item
```

> O node **Loop Over Items** cria automaticamente o loop.
> Após o último item, o workflow termina.

---

## Como funciona a resposta do cliente

Quando o cliente responde **"1"** ou **"confirmo"**:
- O Orquestrador (Workflow 01) recebe → Aurora classifica como `OUTRO` ou `AGENDAR`
- A mensagem de confirmação vai para a Bia ou é tratada pelo fallback
- **Melhoria futura:** adicionar intent `CONFIRMAR_LEMBRETE` na Aurora para identificar respostas numéricas como "1" ou "2" e atualizar a coluna `Confirmado_Pelo_Cliente` diretamente

Quando o cliente responde **"2"** ou quer remarcar:
- Aurora classifica como `AGENDAR` → Bia assume e inicia fluxo de remarcação

---

## Configuração do Cron para produção

Para enviar lembretes apenas em horário comercial, use expressão cron customizada:

```
0 9-18 * * 1-6
```

(a cada hora, de 9h a 18h, segunda a sábado)

No n8n → node Schedule Trigger → selecione **"Custom (Cron Expression)"**.

---

## Como testar

### 1. Inserir agendamento de teste

Na aba `Agendamentos`, adicione uma linha com:
- `Data` = data de amanhã (ex: `2026-06-04`)
- `Status` = `confirmado`
- `Lembrete_Enviado` = (vazio)
- `Telefone` = seu número de teste

### 2. Executar manualmente

No n8n → workflow `04-lembrete-24h` → clique **"Execute Workflow"** (botão de play manual).

### 3. Verificar

- Você deve receber a mensagem no WhatsApp
- A aba `Agendamentos` deve ter `Lembrete_Enviado = SIM`
- A aba `Log_Lembretes` deve ter nova linha

---

## Troubleshooting

| Problema | Solução |
|---|---|
| Node "Filtrar" retorna 0 itens | Verifique: `Data` no formato `YYYY-MM-DD`, `Status = confirmado`, `Lembrete_Enviado` vazio |
| Mensagem enviada duplicada | `Lembrete_Enviado` não está sendo atualizado — verifique o Lookup Column (deve ser `ID`) |
| Workflow não dispara | Verifique se está ativo (toggle verde) e a expressão cron |
| Erro no Evolution API | Verifique se o telefone está no formato `5511999999999` (sem `+` ou espaço) |

---

## Próximos passos

- [ ] Adicionar segundo lembrete: se cliente não responder em 4h, enviar novo aviso
- [ ] Processar resposta "1" (confirmar) e "2" (remarcar) de forma inteligente via intent `CONFIRMAR_LEMBRETE`
- [ ] Integrar Google Calendar: criar eventos ao confirmar agendamento (via Workflow 02)
