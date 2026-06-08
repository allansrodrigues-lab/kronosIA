# Credenciais — Template

> ⚠️ **NUNCA commite este arquivo preenchido em repositório público.**
> Use apenas como referência do que precisa ser configurado.
> Para produção, use o gerenciador de credenciais do n8n.

## Evolution API
- URL base: https://___________
- API Key global: ___________
- Nome da instância: clinica
- Webhook URL configurada: https://___________/webhook/whatsapp
- Status da conexão: [ ] Conectado / [ ] Desconectado

## Anthropic (Claude)
- Workspace: ___________
- API Key: ___________
- Limite de gasto/mês configurado: R$ ___________

## Google (Service Account)
- Project ID: ___________
- Service Account email: ___________@___________.iam.gserviceaccount.com
- JSON key: armazenado no n8n como credential
- Calendar ID compartilhado: ___________
- Sheets CRM ID: ___________

## n8n
- URL: https://___________
- Admin email: ___________
- Senha: gerenciada no 1Password/Bitwarden

## Vector DB (Pinecone ou Qdrant)
- Endpoint: ___________
- API Key: ___________
- Index name: clinica-kb
- Dimensão: 1536 (text-embedding-3-small da OpenAI) ou 768

## Redis (memória)
- Host: ___________
- Port: 6379
- Senha: ___________

## Alertas
- Telegram Bot token: ___________
- Chat ID do implementador: ___________
- Grupo WhatsApp da equipe: ___________
