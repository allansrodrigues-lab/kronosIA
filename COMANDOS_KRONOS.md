# Comandos Kronos — Claude Code

> Digite no chat do Claude Code (projeto teste Automação)

| Comando | O que faz |
|---|---|
| `/test-harness` | Roda 13 testes nos bots Aurora e Odonto — mostra verde/vermelho |
| `/monitor` | Checa saúde do n8n, bots ativos e execuções com erro |
| `/kronos-monitor` | Documenta e aplica padrão de monitoramento (error-handler + self-healing) |
| `/restart-n8n` | Reinicia o container n8n no VPS com segurança |
| `/n8n-debug` | Debugar bot parado, em loop ou com erro |
| `/fix-n8n-auth` | Resolve erro 401 do Haiku passo a passo |
| `/kronos-deploy` | Deploy de infra ou site no VPS |
| `/kronos-workflow` | Criar ou editar workflow n8n |
| `/kronos-agente` | Criar ou adaptar agente de IA para novo nicho |
| `/kronos-central-demos` | Gerencia a central de demos (chavinha, roteador, nichos) |

---

## Regra de ouro

**Antes de editar qualquer workflow → `/test-harness`**
**Depois de editar → `/test-harness`**
Se verde: ok. Se vermelho: tem regressão, investiga antes de continuar.

---

## VPS Kronos

- IP: `2.24.101.180`
- n8n: https://n8n.kronosintelligence.com.br
- Site: https://kronosintelligence.com.br
- WhatsApp teste: `5519971266736` (nunca testar bot contra bot)
