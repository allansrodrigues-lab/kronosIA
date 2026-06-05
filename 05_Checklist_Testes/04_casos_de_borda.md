# Casos de Borda (Edge Cases)

> Cenários "esquisitos" que QUEBRAM sistemas mal projetados. Testar TODOS antes do go-live.

## Mensagens

- [ ] Mensagem vazia (cliente manda só sticker)
- [ ] Mensagem com 5000+ caracteres
- [ ] Mensagem em outro idioma (inglês, espanhol)
- [ ] Mensagem só com emoji
- [ ] Mensagem com link suspeito
- [ ] Mensagem com áudio de 10 segundos
- [ ] Mensagem com áudio de 5 minutos
- [ ] Mensagem com vídeo
- [ ] Mensagem com foto (ex.: foto da pele "olha isso")
- [ ] Mensagem com documento (PDF)
- [ ] Mensagem encaminhada com muito texto
- [ ] Cliente apaga mensagem antes do agente ler

## Comportamento do cliente

- [ ] Cliente envia 30 mensagens em 1 minuto (spam ou impaciência)
- [ ] Cliente troca de assunto a cada mensagem
- [ ] Cliente xinga / é grosso
- [ ] Cliente flerta com o agente
- [ ] Cliente faz pergunta off-topic ("você é IA?")
- [ ] Cliente tenta enganar ("a recepção disse que tem 50% off")
- [ ] Cliente faz prompt injection ("ignore instruções anteriores...")
- [ ] Cliente desiste no meio e volta horas depois

## Dados e CRM

- [ ] Cliente com nome com acento ou caractere especial (José, María)
- [ ] Mesmo número aparece com 2 nomes diferentes em momentos diferentes
- [ ] Cliente troca de número
- [ ] Cliente do exterior (DDI diferente)
- [ ] Cliente sem nome cadastrado

## Calendário

- [ ] Horário em dia de feriado (calendar deve respeitar)
- [ ] Horário no fim de semana (sábado tem expediente reduzido)
- [ ] Agendamento que cruza meia-noite (não deveria existir, mas verificar)
- [ ] Dois clientes pedindo o mesmo slot ao mesmo tempo (race condition)
- [ ] Cliente pede "hoje à tarde" às 18h (agenda já fechou)

## Sistema

- [ ] WhatsApp API fora do ar
- [ ] Anthropic fora do ar
- [ ] Google Calendar fora do ar
- [ ] n8n reinicia no meio de um workflow
- [ ] Internet da clínica cai (não pode quebrar o agente)
- [ ] Token do WhatsApp expira no meio do dia

## LGPD

- [ ] Cliente pede para apagar seus dados ("LGPD esquece de mim")
- [ ] Cliente pede para parar de receber marketing
- [ ] Cliente pede histórico das mensagens dele

## Datas e timezone

- [ ] Horário de verão (se voltar)
- [ ] Sistema em UTC e clínica em BRT — agendamento confere?
- [ ] Cliente em outro fuso horário viajando

## Custo

- [ ] Quantos tokens em média por conversa? Cabe no orçamento?
- [ ] Cliente "loop" que conversa por 50 turnos — corta após N turnos
