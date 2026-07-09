# Orquestrador — Cedro Saúde (Demo Kronos)

## Modelo: Claude Haiku (claude-haiku-4-5-20251001) — classificação de intent, mesmo padrão Aurora/Léa/Sofia/Helena

Recebe toda mensagem do WhatsApp (via chavinha `/clinica-medica` na Central de Demos), classifica
a intenção e roteia para o agente/fluxo certo. Segue a arquitetura validada do orquestrador Kronos
(buffer/debounce 2-3s → sessão no Sheets → filtro de urgência → Haiku classifica → roteia → responde
→ loga no CRM) — **com uma camada extra que nenhum outro nicho tem: o filtro de urgência roda ANTES
de qualquer LLM.**

---

## ⭐ Filtro de urgência (determinístico, roda antes do Haiku)

Igual a calculadora de payback da Zênite não é "LLM fazendo conta", a segurança do paciente não pode
depender de um classificador probabilístico. Um Code node com regex/lista de sinais de alerta roda
**antes** do nó Haiku. Se bater, a mensagem NUNCA chega a ser classificada por intent normal — vai
direto para escalação humana. Detalhe completo (lista de sinais, código, texto de orientação) em
`02_agente_triagem_regras.md`.

```
Mensagem chega → [Filtro de Urgência - Code node] → bateu sinal de risco?
                                                        ├─ SIM → Escalação imediata (pula Haiku)
                                                        └─ NÃO → segue pro classificador Haiku normal
```

## Intenções do nicho (classificador Haiku, só roda se o filtro de urgência não disparou)

| Intent | Descrição | Destino |
|---|---|---|
| `AGENDAR` | Marcar, remarcar ou cancelar consulta/exame | Motor de agendamento (Bia adaptada — Google Calendar) |
| `DUVIDA_ADMINISTRATIVA` | Convênio, preparo de exame, documentos, horário, endereço, valores | Vera — resposta com base de conhecimento |
| `DUVIDA_CLINICA` | Descreve sintoma leve ou pergunta sobre saúde (NÃO urgente) | Vera — nunca opina, sempre direciona para consulta |
| `TELECONSULTA` | Pergunta sobre consulta online/por vídeo | Vera — explica regras (CFM 2.336/2023) |
| `POS_CONSULTA` | Já é paciente: retorno, resultado de exame, dúvida sobre receita | Follow-up (Diana adaptada) |
| `RECLAMACAO` | Insatisfação, atraso, erro de agendamento, cobrança indevida | Escalação humana |
| `OUTRO` | Saudação, agradecimento, assunto fora de escopo | Vera — resposta direta |

## Prompt de classificação (nó "Montar Prompt Haiku")

```
Você é um classificador de intenções de uma clínica médica. Analise a mensagem do paciente e
responda APENAS com uma palavra, a intenção correta:

AGENDAR — quer marcar, confirmar, remarcar ou cancelar consulta ou exame
DUVIDA_ADMINISTRATIVA — pergunta sobre convênio, preparo de exame, documentos, horário de
  funcionamento, endereço, formas de pagamento
DUVIDA_CLINICA — descreve um sintoma leve ou faz pergunta sobre saúde, sem sinal de gravidade
TELECONSULTA — pergunta se dá pra fazer consulta online, por vídeo ou chamada
POS_CONSULTA — já é paciente e pergunta sobre retorno, resultado de exame ou receita
RECLAMACAO — reclamação, insatisfação, atraso, erro de agendamento ou cobrança
OUTRO — saudação, agradecimento ou assunto que não se encaixa acima

Contexto da sessão (se houver): ${contexto}
Mensagem do paciente: ${mensagem}

Responda apenas com a palavra da intenção, sem pontuação.
```

### Regras de desempate

- **Qualquer sinal do filtro de urgência SEMPRE vence** — mesmo que o Haiku nunca chegue a rodar
  nesse caso, se por algum motivo a mensagem chegar até aqui com um sinal de risco não capturado,
  o prompt acima NÃO decide isso; é papel do filtro de urgência, não do classificador de intent.
- "Tá doendo muito aqui, marca uma consulta" → `AGENDAR` (dor mencionada, mas sem os sinais de
  alerta do filtro) — Vera agenda e, no fluxo, sugere o quanto antes disponível, sem alarmismo
  nem minimização.
- Mandou **foto de exame/receita** sem sinal de urgência no texto → `POS_CONSULTA` (o tipo de mídia
  ajuda a decidir, igual ao `CONTA_LUZ` da Zênite).
- Sessão já em fluxo de agendamento tem prioridade: manter no agente atual salvo mudança clara de
  assunto ou disparo do filtro de urgência (que sempre interrompe qualquer fluxo).
- Pergunta tipo "isso é grave?" sobre um sintoma já descrito → `DUVIDA_CLINICA`, e Vera NUNCA
  responde "não, não é grave" — sempre direciona para avaliação médica.

## Sessão (aba `Sessoes_ClinicaMedica` no Sheets)

| Campo | Descrição |
|---|---|
| `jid` | ID WhatsApp do paciente |
| `nome` | Nome coletado |
| `data_nascimento` | Data de nascimento (confirmação de identidade) |
| `especialidade_interesse` | Especialidade buscada |
| `convenio` | Nome do convênio ou "particular" |
| `consentimento_lgpd` | `pendente` / `aceito` — registrado na 1ª interação |
| `status` | `triagem` → `qualificacao` → `agendamento` → `confirmado` → `pos_consulta` |
| `historico` | Últimas 6 trocas |
| `data_contato` | Timestamp do primeiro contato |

## Padrões obrigatórios (herdados da plataforma)

- **Buffer/debounce** de mensagens picadas (2-3s) antes de classificar
- **IF voz:** áudio → transcrição antes do classificador (motor da Aurora ♻️)
- **Error Trigger** apontando para o Error Handler central (`X29vC9p5WB38iZFI`)
- **Parser de resposta do Sonnet 5:** sempre `content.find(b => b.type === 'text')?.text` (nunca `content[0].text`)
- Log de toda conversa no CRM (aba `Pacientes_ClinicaMedica`) — planilha própria do nicho (regra-mãe: base isolada)
- **Fallback por regex** nas ações estruturadas (lição Schalletti: nunca confiar só no prompt para `acao=`)
- **Consentimento LGPD explícito** logo na 1ª mensagem da sessão — não é opcional, é o 1º texto que Vera manda antes de coletar qualquer dado de saúde
