# Orquestrador — Zênite Energia Solar (Demo Kronos)

## Modelo: Claude Haiku (claude-haiku-4-5-20251001) — classificação de intent, mesmo padrão Aurora/Léa/Sofia

Recebe toda mensagem do WhatsApp (via chavinha `/solar` na Central de Demos), classifica a intenção
e roteia para o agente/fluxo certo. Segue a arquitetura validada do orquestrador Kronos
(buffer/debounce 2-3s → sessão no Sheets → Haiku classifica → roteia → responde → loga no CRM).

---

## Intenções do nicho

| Intent | Descrição | Destino |
|---|---|---|
| `ORCAMENTO` | Quer saber preço, economia, "quanto custa", "vale a pena" | Helena — qualificação → ⭐ calculadora de payback |
| `DUVIDA_TECNICA` | Como funciona, painel, inversor, manutenção, garantia, chuva/noite | Helena — resposta com base de conhecimento |
| `VISITA_TECNICA` | Agendar, remarcar ou cancelar visita técnica | Motor de agendamento (Bia adaptada — Google Calendar) |
| `FINANCIAMENTO` | Parcelamento, linhas solares, "cabe no bolso", cartão/banco | Helena — condições + gancho pra calculadora (parcela vs economia) |
| `CONTA_LUZ` | Enviou foto/PDF da conta de energia | Leitor de PDF (motor da Advocacia ♻️) → extrai valor → calculadora |
| `POS_INSTALACAO` | Já é cliente: geração baixa, app de monitoramento, limpeza | Follow-up técnico (Diana adaptada) |
| `RECLAMACAO` | Insatisfação, atraso de obra, problema com equipe | Escalação humana (grupo da equipe) |
| `OUTRO` | Saudação, assunto fora de escopo | Helena — resposta direta |

## Prompt de classificação (nó "Montar Prompt Haiku")

```
Você é um classificador de intenções de uma empresa de energia solar. Analise a mensagem
do cliente e responda APENAS com uma palavra, a intenção correta:

ORCAMENTO — quer preço, orçamento, simulação de economia, "quanto custa", "vale a pena", quer instalar
DUVIDA_TECNICA — pergunta como funciona, painel, inversor, bateria, manutenção, garantia, funciona à noite/chuva
VISITA_TECNICA — quer agendar, confirmar, remarcar ou cancelar a visita técnica ao imóvel
FINANCIAMENTO — pergunta sobre parcelamento, financiamento, entrada, cartão, banco, consórcio
CONTA_LUZ — enviou uma foto ou PDF da conta de luz, ou diz que vai mandar a conta
POS_INSTALACAO — já tem sistema instalado: geração, app de monitoramento, limpeza, defeito
RECLAMACAO — reclamação, insatisfação, atraso, problema com atendimento ou obra
OUTRO — saudação, agradecimento ou assunto que não se encaixa acima

Contexto da sessão (se houver): ${contexto}
Mensagem do cliente: ${mensagem}

Responda apenas com a palavra da intenção, sem pontuação.
```

### Regras de desempate

- "Quanto fica pra minha casa?" → `ORCAMENTO` (mesmo sem dados — Helena inicia a qualificação).
- "Dá pra parcelar?" **durante** uma simulação em andamento → `FINANCIAMENTO`, mas a sessão mantém os dados
  da simulação (a resposta cruza parcela × economia — argumento-chave da venda).
- Mandou **imagem/PDF** sem texto → `CONTA_LUZ` (o tipo de mídia decide, não o Haiku).
- "Minha geração caiu" / "o app não conecta" → `POS_INSTALACAO` (cliente existente), nunca `DUVIDA_TECNICA`.
- Sessão já em fluxo (qualificação em andamento) tem prioridade: manter no agente atual salvo mudança clara de assunto.

## Sessão (aba `Sessoes_Solar` no Sheets)

| Campo | Descrição |
|---|---|
| `jid` | ID WhatsApp do cliente |
| `nome` | Nome coletado |
| `tipo_imovel` | casa / empresa / rural / condomínio |
| `valor_conta` | Conta média mensal (R$) |
| `fase_rede` | monofásico / bifásico / trifásico (padrão: bifásico se não souber) |
| `tipo_telhado` | cerâmico / metálico / fibrocimento / laje / solo |
| `cidade` | Cidade/bairro do imóvel |
| `simulacao` | JSON da última simulação (kWp, investimento, economia, payback) |
| `status` | `qualificacao` → `simulacao` → `visita_agendada` → `proposta` → `instalacao` → `pos_instalacao` |
| `historico` | Últimas 6 trocas |
| `data_contato` | Timestamp do primeiro contato |

## Padrões obrigatórios (herdados da plataforma)

- **Buffer/debounce** de mensagens picadas (2-3s) antes de classificar
- **IF voz:** áudio → transcrição antes do classificador (motor da Aurora ♻️)
- **Error Trigger** apontando para o Error Handler central (`X29vC9p5WB38iZFI`)
- **Parser de resposta do Sonnet 5:** sempre `content.find(b => b.type === 'text')?.text` (nunca `content[0].text`)
- Log de toda conversa no CRM (aba `Leads_Solar`) — planilha própria do nicho (regra-mãe: base isolada)
- **Fallback por regex** nas ações estruturadas (lição Schalletti: nunca confiar só no prompt para `acao=`)
