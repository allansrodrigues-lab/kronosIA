# Orquestrador — Estúdio Traço (Arquitetura)

## Papel
Recepção da conversa no WhatsApp do Estúdio Traço, classificação de intenção via Claude Haiku e roteamento. Mesmo padrão do orquestrador Aurora/Cedro.

## Intenções do nicho
| Intent | Descrição | Destino |
|---|---|---|
| `PROJETO_NOVO` | Lead quer projeto (residencial, comercial, interiores, reforma) | Marina — qualificação |
| `ESTIMATIVA` | Pergunta de preço/quanto custa/valor por m² | Marina — calculadora de estimativa |
| `AGENDAR_BRIEFING` | Quer marcar reunião/conversa com arquiteto | Marina — agendamento |
| `DUVIDA_PROCESSO` | Como funciona projeto, prazos, etapas, acompanhamento de obra | Marina — FAQ |
| `REGULARIZACAO` | Regularizar imóvel, planta na prefeitura, habite-se | Marina — qualificação (subtipo regularização) |
| `RECLAMACAO` | Insatisfação, problema com projeto/obra | Escalação humana imediata |
| `OUTRO` | Fora de escopo | Resposta direta educada |

## Regras fixas (antes do classificador)
1. **Filtro determinístico de pedido técnico** (Code node, ANTES do Haiku — mesma filosofia do filtro de urgência da Cedro): mensagens pedindo dimensionamento, cálculo estrutural, laudo, assinatura de projeto (ART/RRT) ou "só uma dica técnica" NÃO viram conversa de venda — resposta padrão explicando que isso é ato privativo do arquiteto responsável + oferta de briefing. Nunca deixar o LLM improvisar resposta técnica.
2. Primeira mensagem sempre se apresenta: "Marina, assistente do Estúdio Traço".
3. Toda conversa registrada no CRM próprio do nicho (planilha exclusiva — regra-mãe de isolamento).

## Classificador (Haiku)
Modelo: `claude-haiku-4-5-20251001`. Saída: JSON `{"intent": "...", "confianca": 0-1}`. Confiança < 0.6 → tratar como `OUTRO` e pedir esclarecimento.

## Handoffs
- `RECLAMACAO` → alerta no grupo da equipe (`EVO_TEAM_NUMBER`) + mensagem de acolhimento.
- Falha de IA (erro no nó Anthropic) → Error Workflow central (`X29vC9p5WB38iZFI`) + escalação humana.
