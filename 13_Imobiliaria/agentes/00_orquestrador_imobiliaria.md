# Orquestrador — Schalletti Imóveis (Demo Kronos)

## Modelo: Claude Haiku (claude-haiku-4-5-20251001) — classificação de intent, mesmo padrão Aurora/Léa

Recebe toda mensagem do WhatsApp (via chavinha `/imobiliaria` na Central de Demos), classifica a intenção
e roteia para o agente/fluxo certo. Segue a arquitetura validada do orquestrador Kronos
(buffer/debounce 2-3s → sessão no Sheets → Haiku classifica → roteia → responde → loga no CRM).

---

## Intenções do nicho

| Intent | Descrição | Destino |
|---|---|---|
| `COMPRAR` | Quer comprar imóvel (ou "ver apartamentos", "procuro casa") | Sofia — qualificação + matching |
| `ALUGAR` | Quer alugar imóvel | Sofia — qualificação + matching (fluxo locação) |
| `VISITA` | Agendar, remarcar ou cancelar visita | Motor de agendamento (Bia adaptada — Google Calendar) |
| `FINANCIAMENTO` | Simulação, dúvida de parcela/entrada/FGTS | ⭐ Calculadora de financiamento |
| `PROPRIETARIO` | Dono quer anunciar/vender/alugar o imóvel dele | Sofia — captação (coleta dados → CRM) |
| `DOCUMENTO` | Enviou PDF (contrato, ficha) ou pede análise | Leitor de PDF (motor da Advocacia ♻️) |
| `POS_VISITA` | Feedback após visita, "gostei", "quero pensar" | Follow-up (Diana adaptada) |
| `RECLAMACAO` | Insatisfação, problema com imóvel/atendimento | Escalação humana (grupo da equipe) |
| `OUTRO` | Saudação, assunto fora de escopo | Sofia — resposta direta |

## Prompt de classificação (nó "Montar Prompt Haiku")

```
Você é um classificador de intenções de uma imobiliária. Analise a mensagem do cliente
e responda APENAS com uma palavra, a intenção correta:

COMPRAR — quer comprar imóvel, procura casa/apartamento para adquirir, investimento
ALUGAR — quer alugar imóvel para morar ou comercial
VISITA — quer agendar, confirmar, remarcar ou cancelar uma visita a imóvel
FINANCIAMENTO — pergunta sobre financiamento, parcela, entrada, FGTS, simulação, consórcio
PROPRIETARIO — é dono de imóvel e quer anunciar, vender ou colocar para alugar COM a imobiliária
DOCUMENTO — enviou um documento/PDF ou pede análise de contrato/ficha
POS_VISITA — comenta sobre visita que já fez, dá feedback, está decidindo
RECLAMACAO — reclamação, insatisfação, problema com imóvel alugado ou atendimento
OUTRO — saudação, agradecimento ou assunto que não se encaixa acima

Contexto da sessão (se houver): ${contexto}
Mensagem do cliente: ${mensagem}

Responda apenas com a palavra da intenção, sem pontuação.
```

### Regras de desempate

- "Quero ver o apartamento X" **sem** visita marcada → `COMPRAR`/`ALUGAR` (interesse); "quero visitar sábado" → `VISITA`.
- "Quanto fica a parcela do SCH-004?" → `FINANCIAMENTO` (a calculadora responde e devolve o contexto à Sofia).
- "Tenho um apê para alugar" (dono) → `PROPRIETARIO`; "quero alugar um apê" (inquilino) → `ALUGAR`.
- Sessão já em fluxo (ex.: qualificação em andamento) tem prioridade: manter no agente atual salvo mudança clara de assunto.

## Sessão (aba `Sessoes_Imobiliaria` no Sheets — via CRM Adapter)

| Campo | Descrição |
|---|---|
| `jid` | ID WhatsApp do cliente |
| `nome` | Nome coletado |
| `finalidade` | comprar / alugar / anunciar |
| `regiao` | Bairro(s) de interesse |
| `faixa_preco` | Teto informado |
| `quartos` | Nº de quartos desejado |
| `extras` | vaga, pet, mobiliado etc. |
| `imoveis_enviados` | Códigos já apresentados (não repetir) |
| `imovel_interesse` | Código do imóvel em negociação/visita |
| `status` | `qualificacao` → `matching` → `visita_agendada` → `pos_visita` → `proposta` |
| `historico` | Últimas 6 trocas |
| `data_contato` | Timestamp do primeiro contato |

## Padrões obrigatórios (herdados da plataforma)

- **Buffer/debounce** de mensagens picadas (2-3s) antes de classificar
- **IF voz:** áudio → transcrição antes do classificador (motor da Aurora ♻️)
- **Error Trigger** apontando para o Error Handler central (`X29vC9p5WB38iZFI`)
- **Parser de resposta do Sonnet 5:** sempre `content.find(b => b.type === 'text')?.text` (nunca `content[0].text`)
- Log de toda conversa no CRM (aba `Leads_Imobiliaria`) via **CRM Adapter** (nunca direto no Sheets — ver `workflows/workflow_crm_adapter_montagem.md`)
