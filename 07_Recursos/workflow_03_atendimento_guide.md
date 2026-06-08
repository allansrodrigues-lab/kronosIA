# Workflow 03 — Agente de Atendimento "Clara" (Guia de Configuração)

> Sub-workflow chamado pelo Orquestrador quando `intent = DUVIDA_PROCEDIMENTO`, `DUVIDA_PRECO` ou `LEAD_NOVO`.
> Clara responde dúvidas com base na KB da clínica e, quando o cliente quer agendar, passa para a Bia.
> Para importar no n8n, use `workflow_03_atendimento.json` na mesma pasta.

---

## Visão geral do fluxo

```
[Trigger — Receber do Orquestrador]
         ↓
[Buscar Sessão Clara]          ← Sheets: tab Sessoes_Ativas (Agente = CLARA)
         ↓
[Montar Prompt Clara]          ← Code: KB completa embutida + histórico da conversa
         ↓
[Claude Sonnet — Clara]        ← HTTP: Anthropic API (temperature 0.4)
         ↓
[Parsear Resposta Clara]       ← Code: extrai mensagem + acao
         ↓
[Switch por Ação]
   ├── passar_para_bia  → [Preparar Passagem] → [Chamar Bia]
   ├── escalar_humano   → passthrough
   └── responder (default) → passthrough
         ↓ (todos convergem)
[Preparar Sessão]              ← Code: serializa histórico + status
         ↓
[Enviar Mensagem WhatsApp]     ← HTTP: Evolution API
         ↓
[Atualizar Sessão Clara]       ← Sheets: append em Sessoes_Ativas
         ↓
[Log Interação Clara]          ← Sheets: append em Log_Interacoes
```

**Total: 12 nodes**

> **Diferença principal em relação à Bia:** Clara não precisa de CRUD em Agendamentos ou Slots.
> Toda a "base de dados" dela está embutida no prompt — sem nodes de Sheets adicionais.

---

## Abas do Google Sheets necessárias

Clara reutiliza as mesmas abas já criadas para o Workflow 01 e 02:

| Aba | Uso |
|---|---|
| `Sessoes_Ativas` | Histórico de conversa com Agente = `CLARA` (mesmo do Workflow 02) |
| `Log_Interacoes` | Log geral (mesmo do Workflow 01) |

**Nenhuma aba nova precisa ser criada.**

---

## Pré-requisitos

Mesmos do Workflow 01 e 02 — nenhuma configuração adicional necessária.

---

## Node 1 — Trigger — Receber do Orquestrador

**Tipo:** Execute Workflow Trigger

**Dados recebidos:**

| Campo | Descrição |
|---|---|
| `telefone` | Número do cliente |
| `nome` | Nome do cliente |
| `texto` | Mensagem atual |
| `remoteJid` | JID para envio |
| `instancia` | Instância Evolution |
| `timestamp` | Timestamp Unix |
| `messageId` | ID da mensagem |
| `intent` | `DUVIDA_PROCEDIMENTO`, `DUVIDA_PRECO` ou `LEAD_NOVO` |

---

## Node 2 — Buscar Sessão Clara (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Get Many Rows` |
| Sheet | `Sessoes_Ativas` |
| Return All Rows | Ativo |

Configure **"Continue On Fail"** ativo.

> Mesma lógica do Workflow 02: retorna todas as sessões e o Code node filtra pelo telefone + Agente = 'CLARA'.

---

## Node 3 — Montar Prompt Clara (Code)

Este é o node central da Clara. Ele embute toda a base de conhecimento da clínica no system prompt.

```javascript
const ctx = $('Trigger — Receber do Orquestrador').first().json;
const { telefone, nome, texto, remoteJid, instancia, timestamp, messageId, intent } = ctx;

// Sessão Clara ativa para este telefone
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
- Recuperação: 24-48h de leve vermelhidão
- Frequência recomendada: a cada 30-45 dias
- Avaliação prévia: não obrigatória

### Peeling Químico
- Duração: 45 min | Preço: R$ 290 (avulso) | Pacote 6 sessões: R$ 1.480 (15% off)
- Indicações: manchas, textura irregular, sinais de envelhecimento leve
- Contraindicações: gestantes, pele bronzeada, lesões ativas
- Recuperação: descamação por 3-7 dias
- Frequência: série de 4-6 sessões, a cada 15 dias
- Avaliação prévia: não obrigatória

### Botox / Toxina Botulínica
- Duração: 30 min | Preço: R$ 650 (1 área) / R$ 1.500 (3 áreas: testa + glabela + pés-de-galinha)
- Indicações: rugas dinâmicas (testa, glabela, pés-de-galinha)
- Contraindicações: gestantes, lactantes, doenças neuromusculares
- Recuperação: sem downtime; evitar deitar 4h após
- Resultado: aparece entre 5-15 dias, dura 4-6 meses
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
- Contraindicações: hérnia na área tratada, crioglobulinemia, gestantes
- Recuperação: sensibilidade local 1-2 semanas
- Resultado: 30-45 dias, pode precisar de 2ª sessão
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
- PIX: 5% de desconto adicional
- Cartão de crédito: até 3x sem juros; 4x a 10x com juros da operadora
- Não trabalhamos com fiado — pagamento no dia

## DESCONTOS E PROMOÇÕES
- Indicação de amiga: 10% para quem indicou + 10% para a indicada
- Aniversariante do mês: 15% em qualquer procedimento avulso
- Pacotes têm desconto já incluído (15% a 20%)
- Nunca prometer desconto além do acima sem autorização da gerente

## POLÍTICAS E FAQ
- Horário: Seg-Sex 9h-19h | Sáb 9h-14h | Dom fechado
- Avaliação gratuita antes de Botox e Criolipólise (obrigatória)
- Para limpeza de pele, massagem e drenagem: avaliação não é obrigatória
- Remarcação: gratuita até 4h antes; após isso, retém 50% do valor
- Tolerância de atraso: 15 min; acima disso pode ser necessário remarcar
- Gestante: apenas drenagem suave (2º trimestre) com autorização médica
- Plano de saúde: não aceito
- Nota fiscal: sim, NFS-e para todos
- Estacionamento: conveniado, R$ 10/4h no edifício
- Segurança dos produtos: marcas ANVISA. Responsável: Dra. Marina (CRBio XXXXX)
- Garantia de resultado: a clínica não promete resultado específico; garante qualidade do protocolo

━━━━━━━━━━━━━━━━━━━━━━━

GUARDRAILS (REGRA DE OURO):
❌ Nunca diagnóstico ("você tem rosácea")
❌ Nunca prescrição ("use ácido tal")
❌ Nunca prometa resultado ("vai sumir 100%")
❌ Nunca "isso é seguro pra você" sem avaliação presencial
✅ Sempre cite contraindicações relevantes
✅ Para casos específicos: indique avaliação presencial
✅ Se não souber → diga que vai confirmar com a equipe

ESTRUTURA DA RESPOSTA:
1. Reconheça a dúvida (1 frase)
2. Responda com base na KB (2-3 frases ou bullets curtos)
3. Convide para próximo passo (avaliação, agendamento, ou "fico por aqui se precisar")

TOM: Acolhedora e profissional. Frases curtas. Máximo 1 emoji por mensagem (💛 ✨ 💆‍♀️ 🌸 😊).
Nunca: "Querida", "Amor", "Linda". Use o nome ${nome}.
Sem abreviações (vc, blz, etc). Ortografia impecável.

RESPONDA SEMPRE EM JSON VÁLIDO — sem texto fora do JSON:
{
  "mensagem": "texto para o cliente (max 400 chars)",
  "acao": "responder | passar_para_bia | escalar_humano | encerrar",
  "topico": "procedimento | preco | faq | lead | outro",
  "procedimento_interesse": "nome do procedimento se cliente expressou interesse ou null",
  "encerrar_sessao": false
}

Quando usar cada acao:
- responder: padrão — responde a dúvida e aguarda possível follow-up
- passar_para_bia: cliente disse que quer agendar/marcar algum procedimento
- escalar_humano: dúvida muito específica de saúde, reclamação, situação fora da KB
- encerrar: conversa claramente encerrada ("obrigada", "até logo")`;

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

---

## Node 4 — Claude Sonnet — Clara (HTTP Request)

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `https://api.anthropic.com/v1/messages` |

**Headers:**

| Name | Value |
|---|---|
| `x-api-key` | `={{ $env.ANTHROPIC_API_KEY }}` |
| `anthropic-version` | `2023-06-01` |
| `Content-Type` | `application/json` |

**Body:** JSON/RAW → `={{ $json.anthropicBody }}`

Configure **"Continue On Fail"** ativo.

---

## Node 5 — Parsear Resposta Clara (Code)

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

---

## Node 6 — Switch por Ação (Switch)

| Campo | Valor |
|---|---|
| Mode | `Rules` |
| Value | `={{ $json.acao }}` |

**Outputs:**

| # | Equals | Label |
|---|---|---|
| 1 | `passar_para_bia` | Passar para Bia |
| 2 | `escalar_humano` | Escalar Humano |
| Fallback | — | Responder / Encerrar |

---

## Node 7 — Preparar Passagem para Bia (Code) — branch passar_para_bia

```javascript
const { telefone, nome, remoteJid, instancia, timestamp, messageId,
        procedimento_interesse, mensagem, historicoAtualizado } = $input.first().json;

// Monta contexto enriquecido para a Bia: inclui o procedimento que Clara identificou
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
    // Contexto que será passado para a Bia
    contexto_bia: {
      telefone, nome, remoteJid, instancia, timestamp, messageId,
      texto: textoParaBia,
      intent: 'AGENDAR'
    }
  }
}];
```

---

## Node 8 — Chamar Bia (Execute Workflow) — branch passar_para_bia

| Campo | Valor |
|---|---|
| Source | `Database` |
| Workflow | `02-agendamento-bia` |
| Wait For Sub-Workflow | Ativo |

**Campo de input:** `={{ $json.contexto_bia }}`

> A Bia receberá o contexto com `texto = "Quero agendar: [procedimento]"`, já sabendo o que o cliente quer.

---

## Node 9 — Preparar Sessão (Code) — ponto de convergência

Conecte as saídas dos branches "Escalar Humano", "Responder/Encerrar" e "Chamar Bia" a este node.

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

---

## Node 10 — Enviar Mensagem WhatsApp (HTTP Request)

| Campo | Valor |
|---|---|
| Method | `POST` |
| URL | `={{ $env.EVO_BASE_URL }}/message/sendText/{{ $env.EVO_INSTANCE }}` |

**Headers:** `apikey` + `Content-Type` (mesmo padrão dos outros workflows)

**Body:** `={{ { number: $json.telefone, text: $json.mensagem } }}`

> **Atenção:** no branch `passar_para_bia`, a Bia já enviará sua própria mensagem de boas-vindas.
> Aqui, a mensagem da Clara é a de **transição** (ex: "Que ótimo! Vou te passar para a Bia...").
> Não há mensagem duplicada porque a Bia começa o fluxo com sua própria saudação.

---

## Node 11 — Atualizar Sessão Clara (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Append Row` |
| Sheet | `Sessoes_Ativas` |

**Campos:** mesmos do Workflow 02 (Atualizar Sessão Bia), substituindo Agente = `CLARA`.

---

## Node 12 — Log Interação Clara (Google Sheets)

| Campo | Valor |
|---|---|
| Operation | `Append Row` |
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

---

## Diagrama de conexões

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
    ↓(1)               ↓(2)         ↓(3 fallback)
[Preparar          (Escalar)      (Responder/
 Passagem Bia]                     Encerrar)
    ↓
[Chamar Bia]
    ↓                  ↓                 ↓
    └──────────────────┴─────────────────┘
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

## Como testar

### Teste 1 — Dúvida sobre procedimento

```json
{
  "telefone": "5511999999999",
  "nome": "Ana Teste",
  "texto": "O peeling dói muito? Tenho medo",
  "remoteJid": "5511999999999@s.whatsapp.net",
  "instancia": "clinica",
  "timestamp": 1748908800,
  "messageId": "TEST-CLARA-001",
  "intent": "DUVIDA_PROCEDIMENTO"
}
```

**Esperado:** `acao = "responder"`, mensagem empática sobre peeling com informações de recuperação.

### Teste 2 — Pergunta de preço

```json
{
  ...
  "texto": "Quanto custa o botox?",
  "intent": "DUVIDA_PRECO"
}
```

**Esperado:** preço R$ 650 (1 área) / R$ 1.500 (3 áreas), menção de avaliação gratuita obrigatória.

### Teste 3 — Lead novo

```json
{
  ...
  "texto": "Olá, queria saber mais sobre a clínica",
  "intent": "LEAD_NOVO"
}
```

**Esperado:** apresentação calorosa + convite para avaliação gratuita.

### Teste 4 — Passagem para Bia

```json
{
  ...
  "texto": "Quero agendar uma limpeza de pele",
  "intent": "DUVIDA_PROCEDIMENTO"
}
```

**Esperado:** `acao = "passar_para_bia"`, workflow da Bia é chamado com `texto = "Quero agendar: Limpeza de Pele Profunda"`.

---

## Troubleshooting

| Problema | Solução |
|---|---|
| Clara inventa informações | Verifique se o guardrail da KB está no system prompt; teste com `bia_raw` para ver saída bruta |
| Clara diz valor errado | Atualize a KB no Code node "Montar Prompt Clara" (não em arquivo separado) |
| Passagem para Bia não dispara | Verifique que Workflow 02 está ativo; confira a conexão do Execute Workflow |
| Clara repete a mesma resposta | Histórico não está sendo carregado — verifique node "Buscar Sessão Clara" |

---

## Próximos passos

- [ ] Adicionar intents `DUVIDA_PROCEDIMENTO` e `DUVIDA_PRECO` no routing do Workflow 01
- [ ] Adicionar intent `LEAD_NOVO` no routing do Workflow 01
- [ ] Sub-workflow 04 — Diana (POS_PROCEDIMENTO)
- [ ] Lembrete 24h (workflow Cron)
