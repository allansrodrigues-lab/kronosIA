# Guia de Montagem Manual — Workflow 03 Atendimento (Clara)

> Siga esta ordem exata. Para contexto técnico completo, consulte `workflow_03_atendimento_guide.md`.
> Clara é mais simples que a Bia — nenhuma aba nova de Sheets é necessária.

---

## Antes de começar

1. Confirme que o **Workflow 02 (Bia) já está criado e ativo** — Clara pode chamá-lo
2. Crie um **novo workflow em branco** no n8n
3. Renomeie para: **`03-atendimento-clara`**
4. Salve com **Ctrl+S**

---

## PARTE 1 — Adicionar os nodes

---

### Node 1 — Trigger — Receber do Orquestrador

**Como adicionar:**
- Clique no `+` no canvas
- Digite: `execute workflow trigger`
- Selecione **Execute Workflow Trigger**

**Renomear:** `Trigger — Receber do Orquestrador`

---

### Node 2 — Buscar Sessão Clara

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Get Many Rows` |
| Document | ID da planilha (`GOOGLE_SHEETS_CRM_ID`) |
| Sheet Name | `Sessoes_Ativas` |
| Return All Rows | **Ativo** |

**"Continue on Fail":** ative (engrenagem ⚙️).

**Renomear:** `Buscar Sessão Clara`

---

### Node 3 — Montar Prompt Clara

**Como adicionar:**
- `+` → `code` → **Code**

**O que configurar:**
- Language: `JavaScript`
- Apague o código padrão e cole:

```javascript
const ctx = $('Trigger — Receber do Orquestrador').first().json;
const { telefone, nome, texto, remoteJid, instancia, timestamp, messageId, intent } = ctx;

const todasSessoes = $('Buscar Sessão Clara').all();
const sessao = todasSessoes.find(
  s => s.json.Telefone === telefone && s.json.Agente === 'CLARA' && s.json.Status === 'ativo'
)?.json ?? null;

let historico = [];
if (sessao?.Historico) {
  try { historico = JSON.parse(sessao.Historico); } catch(e) {}
}

historico.push({ role: 'user', content: texto });

const systemPrompt = `Você é Clara, atendente especializada da Clínica de Estética.

Sua missão é tirar dúvidas com clareza e empatia, sempre baseando a resposta NA BASE DE CONHECIMENTO abaixo.
SE A INFORMAÇÃO NÃO ESTIVER NA BASE DE CONHECIMENTO → diga "Vou confirmar com a nossa equipe e te retorno em breve."

━━━━━━━━━━━━━━━━━━━━━━━
BASE DE CONHECIMENTO
━━━━━━━━━━━━━━━━━━━━━━━

## PROCEDIMENTOS

### Limpeza de Pele Profunda
- Duração: 60 min | Preço: R$ 220 (avulso) | Pacote 6 sessões: R$ 1.120 (15% off)
- Indicações: cravos, oleosidade, pele congestionada
- Contraindicações: pele em processo inflamatório, herpes ativo, uso recente de ácidos fortes
- Recuperação: 24-48h de leve vermelhidão | Frequência: a cada 30-45 dias
- Avaliação prévia: não obrigatória

### Peeling Químico
- Duração: 45 min | Preço: R$ 290 (avulso) | Pacote 6 sessões: R$ 1.480 (15% off)
- Indicações: manchas, textura irregular, sinais de envelhecimento leve
- Contraindicações: gestantes, pele bronzeada, lesões ativas
- Recuperação: descamação por 3-7 dias | Frequência: série de 4-6 sessões, a cada 15 dias
- Avaliação prévia: não obrigatória

### Botox / Toxina Botulínica
- Duração: 30 min | Preço: R$ 650 (1 área) / R$ 1.500 (3 áreas)
- Indicações: rugas dinâmicas (testa, glabela, pés-de-galinha)
- Contraindicações: gestantes, lactantes, doenças neuromusculares
- Recuperação: sem downtime; evitar deitar 4h após
- Resultado: aparece em 5-15 dias, dura 4-6 meses
- Avaliação prévia: OBRIGATÓRIA (gratuita, 30 min)

### Drenagem Linfática
- Duração: 60 min | Preço: R$ 180 (avulso) | Pacote 10 sessões pós-cirúrgico: R$ 1.440 (20% off)
- Indicações: retenção líquida, pós-cirúrgico, pernas pesadas
- Contraindicações: trombose, infecções agudas, câncer em tratamento
- Frequência: série de 10 sessões, 2-3x/semana
- Avaliação prévia: não obrigatória (exceto pós-cirúrgico)

### Criolipólise
- Duração: 60 min por área | Preço: R$ 590 (1 área) | Pacote 2 áreas: R$ 1.060 (10% off)
- Indicações: gordura localizada (abdômen, flancos, culote)
- Contraindicações: hérnia na área, crioglobulinemia, gestantes
- Recuperação: sensibilidade local 1-2 semanas | Resultado: 30-45 dias
- Avaliação prévia: OBRIGATÓRIA (gratuita, 30 min)

### Massagem Modeladora
- Duração: 50 min | Preço: R$ 160 (avulso) | Pacote 10 sessões: R$ 1.280 (20% off)
- Indicações: modelagem corporal, celulite leve a moderada
- Frequência: série de 10 sessões, 2x/semana
- Avaliação prévia: não obrigatória

### Avaliação Inicial
- Duração: 30 min | Gratuita
- Inclui: anamnese, análise visual, plano de tratamento personalizado

## FORMAS DE PAGAMENTO
- PIX: 5% de desconto adicional | Cartão: até 3x sem juros; 4x-10x com juros

## DESCONTOS
- Indicação de amiga: 10% para quem indicou + 10% para a indicada
- Aniversariante do mês: 15% em qualquer procedimento avulso

## FAQ
- Horário: Seg-Sex 9h-19h | Sáb 9h-14h | Dom fechado
- Remarcação: gratuita até 4h antes; depois retém 50%
- Tolerância de atraso: 15 min
- Gestante: apenas drenagem suave (2º tri) com autorização médica
- Plano de saúde: não aceito | Nota fiscal: sim (NFS-e)
- Estacionamento: conveniado R$ 10/4h

━━━━━━━━━━━━━━━━━━━━━━━

GUARDRAILS:
❌ Nunca diagnóstico, prescrição ou promessa de resultado
✅ Cite contraindicações relevantes | ✅ Indique avaliação para casos específicos
✅ Se não souber → "Vou confirmar com a equipe"

ESTRUTURA: 1) Reconheça a dúvida | 2) Responda com KB | 3) Convide para próximo passo

TOM: Acolhedora e profissional. Frases curtas. Máx 1 emoji. Nome: ${nome}.
Sem abreviações. Ortografia impecável. Nunca: "Querida", "Amor", "Linda".

RESPONDA SEMPRE EM JSON VÁLIDO (sem texto fora):
{"mensagem": "texto (max 400 chars)", "acao": "responder|passar_para_bia|escalar_humano|encerrar", "topico": "procedimento|preco|faq|lead|outro", "procedimento_interesse": null, "encerrar_sessao": false}

- passar_para_bia: cliente quer agendar/marcar horário
- escalar_humano: dúvida médica específica ou reclamação
- encerrar: conversa claramente encerrada`;

return [{
  json: {
    telefone, nome, texto, remoteJid, instancia, timestamp, messageId, intent,
    historico,
    sessao_id: sessao?.ID ?? null,
    sessao_fase: sessao?.Fase ?? 'novo',
    anthropicBody: {
      model: 'claude-sonnet-4-6',
      max_tokens: 500,
      temperature: 0.4,
      system: systemPrompt,
      messages: historico
    }
  }
}];
```

**Renomear:** `Montar Prompt Clara`

---

### Node 4 — Claude Sonnet — Clara

**Como adicionar:**
- `+` → `http request` → **HTTP Request**

**O que configurar:**

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `https://api.anthropic.com/v1/messages` |

**Headers (3 headers):**

| Name | Value |
|---|---|
| `x-api-key` | `={{ $env.ANTHROPIC_API_KEY }}` |
| `anthropic-version` | `2023-06-01` |
| `Content-Type` | `application/json` |

**Body:**
- Ative **Send Body** → Body Content Type: **JSON**
- Campo Body: `={{ $json.anthropicBody }}`

**"Continue on Fail":** ative.

**Renomear:** `Claude Sonnet — Clara`

---

### Node 5 — Parsear Resposta Clara

**Como adicionar:**
- `+` → `code` → **Code**

**Cole o código:**

```javascript
const input = $input.first().json;
const ctx = $('Montar Prompt Clara').first().json;

if (input.error || !input.content) {
  return [{
    json: {
      ...ctx,
      mensagem: `Oi ${ctx.nome}! Tive uma instabilidade. Pode repetir sua dúvida? 😊`,
      acao: 'responder',
      topico: 'outro',
      procedimento_interesse: null,
      encerrar_sessao: false,
      historicoAtualizado: ctx.historico,
      erro: true
    }
  }];
}

const rawText = input.content?.[0]?.text ?? '{}';

let parsed;
try {
  const cleaned = rawText.replace(/```json?/g, '').replace(/```/g, '').trim();
  parsed = JSON.parse(cleaned);
} catch(e) {
  parsed = {
    mensagem: `Oi ${ctx.nome}! Pode repetir sua pergunta de outro jeito?`,
    acao: 'responder',
    topico: 'outro',
    procedimento_interesse: null,
    encerrar_sessao: false
  };
}

const validAcoes = ['responder', 'passar_para_bia', 'escalar_humano', 'encerrar'];
if (!validAcoes.includes(parsed.acao)) parsed.acao = 'responder';

const historicoAtualizado = [...ctx.historico, { role: 'assistant', content: parsed.mensagem }];

return [{
  json: {
    telefone: ctx.telefone,
    nome: ctx.nome,
    remoteJid: ctx.remoteJid,
    instancia: ctx.instancia,
    timestamp: ctx.timestamp,
    messageId: ctx.messageId,
    intent: ctx.intent,
    sessao_id: ctx.sessao_id,
    sessao_fase: ctx.sessao_fase,
    mensagem: parsed.mensagem,
    acao: parsed.acao,
    topico: parsed.topico ?? 'outro',
    procedimento_interesse: parsed.procedimento_interesse ?? null,
    encerrar_sessao: parsed.encerrar_sessao ?? false,
    historicoAtualizado,
    clara_raw: rawText
  }
}];
```

**Renomear:** `Parsear Resposta Clara`

---

### Node 6 — Switch por Ação

**Como adicionar:**
- `+` → `switch` → **Switch**

**O que configurar:**
- Mode: `Rules`
- Value: `={{ $json.acao }}`

**Adicione 2 regras + ative Fallback:**

| # | Equals | Label |
|---|---|---|
| 1 | `passar_para_bia` | Passar para Bia |
| 2 | `escalar_humano` | Escalar Humano |
| Fallback | — | Responder |

**Renomear:** `Switch por Ação`

---

### Node 7 — Preparar Passagem para Bia
*(branch: saída 1 "Passar para Bia")*

**Como adicionar:**
- Arraste da **saída 1 (Passar para Bia)** do Switch → `code` → **Code**

**Cole o código:**

```javascript
const { telefone, nome, remoteJid, instancia, timestamp, messageId,
        procedimento_interesse, mensagem, historicoAtualizado } = $input.first().json;

const textoParaBia = procedimento_interesse
  ? `Quero agendar: ${procedimento_interesse}`
  : 'Quero agendar um horário';

return [{
  json: {
    telefone, nome, remoteJid, instancia, timestamp, messageId,
    mensagem,
    acao: 'passar_para_bia',
    historicoAtualizado,
    encerrar_sessao: true,
    procedimento_interesse,
    topico: 'procedimento',
    contexto_bia: {
      telefone, nome, remoteJid, instancia, timestamp, messageId,
      texto: textoParaBia,
      intent: 'AGENDAR'
    }
  }
}];
```

**Renomear:** `Preparar Passagem para Bia`

---

### Node 8 — Chamar Bia
*(branch: após "Preparar Passagem para Bia")*

**Como adicionar:**
- `+` → `execute workflow` → **Execute Workflow**

**O que configurar:**

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | Selecione **`02-agendamento-bia`** |
| Wait For Sub-Workflow | **Ativo** |

**Input Data:**
- No campo de dados, selecione: `={{ $json.contexto_bia }}`

**Renomear:** `Chamar Bia`

---

### Node 9 — Preparar Sessão
*(Ponto de convergência — recebe dos 3 branches)*

**Como adicionar:**
- Crie em posição central abaixo do Switch → `code` → **Code**

**Cole o código:**

```javascript
const input = $input.first().json;
const { telefone, nome, acao, topico, historicoAtualizado,
        encerrar_sessao, sessao_id, timestamp } = input;

const agora = new Date().toLocaleString('pt-BR');
const statusSessao = (encerrar_sessao || acao === 'encerrar' || acao === 'passar_para_bia')
  ? 'encerrado'
  : 'ativo';
const historicoLimitado = (historicoAtualizado ?? []).slice(-16);

return [{
  json: {
    telefone, nome, timestamp, acao, topico,
    mensagem: input.mensagem,
    remoteJid: input.remoteJid,
    instancia: input.instancia,
    sessao_id,
    sessao_update: {
      Agente: 'CLARA',
      Fase: acao,
      Historico: JSON.stringify(historicoLimitado),
      Dado_Temp: JSON.stringify({ topico, procedimento_interesse: input.procedimento_interesse }),
      Atualizado_Em: agora,
      Status: statusSessao
    }
  }
}];
```

**Renomear:** `Preparar Sessão`

**Conectar os 3 branches a este node:**
- Saída do `Chamar Bia` → `Preparar Sessão`
- Saída 2 (Escalar Humano) do Switch → `Preparar Sessão`
- Saída Fallback (Responder) do Switch → `Preparar Sessão`

---

### Node 10 — Enviar Mensagem WhatsApp

**Como adicionar:**
- `+` à direita de `Preparar Sessão` → `http request` → **HTTP Request**

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

**Renomear:** `Enviar Mensagem WhatsApp`

---

### Node 11 — Atualizar Sessão Clara

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Append Row` |
| Document | ID da planilha |
| Sheet | `Sessoes_Ativas` |

**Campos:**

| Column | Value |
|---|---|
| `Telefone` | `={{ $json.telefone }}` |
| `Agente` | `CLARA` |
| `Fase` | `={{ $json.sessao_update.Fase }}` |
| `Historico` | `={{ $json.sessao_update.Historico }}` |
| `Dado_Temp` | `={{ $json.sessao_update.Dado_Temp }}` |
| `Criado_Em` | `={{ $json.sessao_update.Atualizado_Em }}` |
| `Atualizado_Em` | `={{ $json.sessao_update.Atualizado_Em }}` |
| `Status` | `={{ $json.sessao_update.Status }}` |

**Renomear:** `Atualizar Sessão Clara`

---

### Node 12 — Log Interação Clara

**Como adicionar:**
- `+` → `google sheets` → **Google Sheets**

**O que configurar:**

| Campo | Valor |
|---|---|
| Credential | Google Sheets — Clinica |
| Operation | `Append Row` |
| Document | ID da planilha |
| Sheet | `Log_Interacoes` |

**Campos:**

| Column | Value |
|---|---|
| `Data` | `={{ new Date($json.timestamp * 1000).toLocaleString('pt-BR') }}` |
| `Telefone` | `={{ $json.telefone }}` |
| `Nome` | `={{ $json.nome }}` |
| `Mensagem` | `={{ $json.mensagem }}` |
| `Intent` | `={{ $json.topico }}` |
| `Resposta` | `={{ $json.mensagem }}` |
| `Escalacao` | `={{ $json.acao === 'escalar_humano' ? 'SIM' : 'NAO' }}` |

**Renomear:** `Log Interação Clara`

---

## PARTE 2 — Verificar as conexões

```
[Trigger — Receber do Orquestrador]
           ↓
[Buscar Sessão Clara]
           ↓
[Montar Prompt Clara]
           ↓
[Claude Sonnet — Clara]
           ↓
[Parsear Resposta Clara]
           ↓
[Switch por Ação]
  ↓(1)             ↓(2)        ↓(fallback)
[Preparar       (Escalar)    (Responder)
 Passagem Bia]
  ↓
[Chamar Bia]
  ↓                ↓               ↓
  └────────────────┴───────────────┘
                   ↓
         [Preparar Sessão]
                   ↓
     [Enviar Mensagem WhatsApp]
                   ↓
     [Atualizar Sessão Clara]
                   ↓
      [Log Interação Clara]
```

---

## PARTE 3 — Ativar e testar

**1. Salve** — Ctrl+S

**2. Ative** — toggle verde

**3. Anote o ID do workflow** (URL do n8n)

**4. Teste via "Test workflow":**

Cole no Execute Workflow Trigger:
```json
{
  "telefone": "5511999999999",
  "nome": "Ana Teste",
  "texto": "Quanto custa o botox?",
  "remoteJid": "5511999999999@s.whatsapp.net",
  "instancia": "clinica",
  "timestamp": 1748908800,
  "messageId": "TEST-CLARA-001",
  "intent": "DUVIDA_PRECO"
}
```

**Resultado esperado:**
- `acao = "responder"`
- `mensagem` com R$ 650 (1 área) / R$ 1.500 (3 áreas) + avaliação obrigatória
- `topico = "preco"`

---

## PARTE 4 — Checklist final

- [ ] 12 nodes criados e renomeados
- [ ] Workflow 02 (Bia) ativo antes de testar Clara
- [ ] Code node "Montar Prompt Clara" com KB completa
- [ ] "Continue On Fail" ativo em: Sheets, Claude Sonnet
- [ ] Execute Workflow "Chamar Bia" apontando para `02-agendamento-bia`
- [ ] Conexões dos 3 branches → `Preparar Sessão` corretas
- [ ] Workflow ativo (toggle verde)
- [ ] Teste de preço executado com sucesso
- [ ] ID do workflow anotado para configurar no Workflow 01
