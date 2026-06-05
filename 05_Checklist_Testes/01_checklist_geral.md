# Checklist Geral de QA

> Rodar TODO este checklist antes de cada deploy em produção. Marcar `[x]` quando OK.

## 1. Infraestrutura
- [ ] n8n está rodando e acessível pela URL final
- [ ] Backup automático do n8n configurado (export workflows diário)
- [ ] Variáveis de ambiente conferidas (sem token em texto claro nos workflows)
- [ ] HTTPS ativo no domínio
- [ ] Limite de execução do n8n configurado (timeout dos workflows)

## 2. Credenciais
- [ ] Token WhatsApp Cloud API válido (expira a cada 60 dias se for token temporário)
- [ ] Service Account do Google com permissões corretas (Calendar + Sheets)
- [ ] Chave da Anthropic com limite de gasto configurado
- [ ] Webhook verify_token do WhatsApp confere com o configurado na Meta

## 3. Fluxos n8n
- [ ] Workflow `01-orquestrador-whatsapp` ativo
- [ ] Workflow `02-fluxo-agendamento` ativo
- [ ] Workflow `03-fluxo-pos-venda` ativo (cron diário 09:00)
- [ ] Workflow `04-fluxo-marketing` ativo
- [ ] Workflow `05-error-handler` ativo (recebe erros de todos os outros)
- [ ] Workflow `06-lembrete-24h` ativo (cron por hora)

## 4. Integrações
- [ ] Envio de mensagem WhatsApp funciona
- [ ] Recebimento via webhook chega ao n8n
- [ ] Criar evento no Google Calendar funciona
- [ ] Atualizar evento funciona
- [ ] Buscar eventos por intervalo funciona
- [ ] Salvar linha no Sheets CRM funciona
- [ ] Buscar contato no Sheets funciona
- [ ] Chamada à Anthropic retorna resposta válida em < 5s

## 5. Agentes IA
- [ ] Aurora classifica corretamente as 6 intents (testar 5 exemplos de cada)
- [ ] Bia consegue listar horários e criar agendamento
- [ ] Clara consulta a base de conhecimento (verificar source nas respostas)
- [ ] Diana detecta sinais de alerta (testar com prompt "está doendo muito")
- [ ] Eva calcula score corretamente
- [ ] Handoff para humano funciona quando cliente pede "humano"

## 6. Base de conhecimento
- [ ] Todos os arquivos de `base_conhecimento/` estão vetorizados
- [ ] Busca semântica retorna chunks relevantes
- [ ] Atualizar arquivo dispara reindexação

## 7. Tratamento de erros
- [ ] Mensagem com mídia (foto) não quebra o fluxo
- [ ] Mensagem com áudio é tratada (transcrita ou pede texto)
- [ ] Erro 5xx da API do WhatsApp dispara retry com backoff
- [ ] Erro da Anthropic gera mensagem fallback humanizada
- [ ] Alertas chegam no Telegram do implementador

## 8. LGPD / Segurança
- [ ] Termo de consentimento enviado na primeira interação de novo lead
- [ ] Opt-out de marketing funciona (cliente responde "PARAR" → marca no CRM)
- [ ] Logs não contêm CPF, dados de saúde, senhas
- [ ] Apenas pessoas autorizadas têm acesso ao n8n

## 9. Performance
- [ ] Tempo médio de resposta < 5 segundos
- [ ] Suporta 50 conversas simultâneas sem queda

## 10. Equipe humana
- [ ] Recepção sabe como pegar handoff
- [ ] Gerente recebe relatório semanal
- [ ] Há um número de telefone backup caso a automação caia
