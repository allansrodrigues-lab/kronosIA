# Testes — Fluxo de Agendamento

## Cenário 1: Agendamento feliz
**Setup:** cliente novo, primeiro contato.
1. Cliente: "Oi, quero marcar uma limpeza de pele"
2. **Esperado:** Bia apresenta 3 horários disponíveis nos próximos 14 dias
3. Cliente escolhe opção 2
4. **Esperado:** Bia confirma, cria evento no Calendar, registra no Sheets
5. **Esperado:** Cliente recebe mensagem com data, profissional e instruções pré-procedimento
6. **Verificar:** evento aparece na agenda do Google? Linha foi criada no Sheets?

## Cenário 2: Procedimento não existe
1. Cliente: "Quero marcar uma criocauterização"
2. **Esperado:** Bia diz que não tem esse procedimento, lista os disponíveis e pergunta qual mais se aproxima

## Cenário 3: Sem horário no dia pedido
1. Cliente: "Pode ser sexta às 14h?"
2. **Setup:** agenda lotada nessa sexta
3. **Esperado:** Bia oferece 3 horários próximos (sexta em outros horários, sábado, segunda)

## Cenário 4: Remarcação
1. Cliente já tem agendamento na segunda 10h
2. Cliente: "Preciso mudar meu horário de segunda"
3. **Esperado:** Bia identifica o agendamento atual, oferece novos horários
4. Cliente escolhe
5. **Esperado:** evento antigo é atualizado (não duplicado), Sheets atualizado, mensagem de confirmação

## Cenário 5: Cancelamento
1. Cliente: "Quero cancelar meu horário"
2. **Esperado:** Bia identifica o agendamento, pergunta motivo, confirma cancelamento
3. **Esperado:** evento removido do Calendar, linha marcada como "cancelado", pergunta se quer reagendar

## Cenário 6: Cliente desiste no meio
1. Cliente: "Quero marcar limpeza"
2. Bia: oferece horários
3. Cliente: para de responder
4. **Esperado:** após 1h sem resposta, Bia envia mensagem de retomada UMA vez
5. **Esperado:** após 24h sem resposta, conversa é arquivada (não fica tentando)

## Cenário 7: Lembrete 24h
1. **Setup:** cliente tem agendamento amanhã às 14h
2. **Disparo:** cron das 14h de hoje
3. **Esperado:** cliente recebe template: "Olá, lembrando sua limpeza amanhã às 14h..."
4. Cliente responde "1" (confirmar)
5. **Esperado:** Sheets marca como "confirmado_24h"

## Cenário 8: No-show
1. **Setup:** cliente não confirmou em 4h após lembrete
2. **Esperado:** segundo lembrete enviado
3. Se ainda não responder em 12h: linha marcada como "risco_no_show" e recepção é notificada

## Cenário 9: Conflito (cliente quer horário já ocupado)
1. Cliente: "Quero terça 10h"
2. **Setup:** já existe agendamento nesse slot
3. **Esperado:** Bia diz que está ocupado e oferece próximos horários no mesmo dia ou no dia seguinte

## Cenário 10: Cliente VIP (já compareceu 3+ vezes)
1. **Setup:** cliente com 4 atendimentos prévios
2. **Esperado:** Bia menciona o procedimento anterior ("vi que sua última limpeza foi em abril, hora da manutenção!")
