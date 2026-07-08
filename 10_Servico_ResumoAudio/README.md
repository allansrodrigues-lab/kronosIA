# Kronos · Serviço #2 — Resumo de Áudio do WhatsApp

> Cliente manda um áudio no WhatsApp → o bot devolve **transcrição + resumo organizado** (assunto, pontos principais, o que precisa ser feito, urgência).

Perfeito pra quem recebe muito áudio longo: **advogado, corretor, gestor, médico**. Ninguém mais perde 5 minutos ouvindo áudio de 3 minutos.

---

## Como funciona (o fluxo)

```
Áudio no WhatsApp → Evolution API → n8n (webhook /whatsapp-resumo)
   1. Normaliza payload (só processa áudio, ignora grupos e mensagens do próprio bot)
   2. Baixa o áudio da Evolution (getBase64FromMediaMessage)
   3. Converte base64 → arquivo
   4. Transcreve com Groq Whisper (whisper-large-v3, em PT)   ← peça nova
   5. Claude Haiku resume e organiza em JSON
   6. Formata bonito e devolve no WhatsApp
```

Arquivo do workflow: `workflow_resumo_audio.json`

---

## A ÚNICA peça nova: a chave do Groq (grátis)

O Claude não transcreve áudio sozinho — precisa de um serviço de transcrição antes. Usamos o **Groq** porque tem Whisper de graça e é rápido.

**Como pegar a chave (2 minutos):**
1. Entrar em https://console.groq.com
2. Login com Google
3. Menu **API Keys → Create API Key**
4. Copiar a chave (começa com `gsk_...`)

> Tier gratuito do Groq é generoso (centenas de áudios/dia). Pra demo e primeiros clientes, **custo zero**.

---

## Variáveis de ambiente no n8n (Settings → Variables)

Já existem (reaproveitadas dos outros bots):
```
ANTHROPIC_API_KEY   = (a mesma de sempre)
EVO_BASE_URL        = https://evo.clinicacliente.com.br
EVO_API_KEY         = (a mesma da Evolution)
```

Novas pra esse serviço:
```
GROQ_API_KEY        = gsk_...            ← criar no console.groq.com
EVO_INSTANCE_DEMO   = instância do chip único da Central de Demos
DEMO_OWNER_NUMBER   = seu número (só ele troca a chavinha)
```

> Esse serviço agora roda dentro da **Central de Demos** (`kronos-roteador-demo`).
> Não recebe direto — chega pelo roteador quando o modo está em `/resumo`.

---

## Como subir e testar

1. **Importar** `workflow_resumo_audio.json` no n8n.
2. Conferir as variáveis acima (principalmente `GROQ_API_KEY`).
3. **Ativar** o workflow.
4. No painel da Evolution, apontar o webhook da instância pra:
   `https://SEU-N8N/webhook/whatsapp-resumo` (evento `messages.upsert`).
5. Mandar um **áudio** pra esse número de outro WhatsApp → deve voltar o resumo.

⚠️ Lembrete de sempre: testar com número **sem bot** (não número-com-bot contra número-com-bot).

---

## Como vender

- **Pitch:** "Você recebe áudio demais? A Kronos coloca uma assistente que escuta por você e te manda o resumo em texto na hora — só o que importa."
- **Mensalidade sugerida:** R$ 150 a R$ 400 (depende do volume).
- **Add-on:** pra quem já tem o chatbot, é só somar na mensalidade — não precisa de número novo.
- **Custo seu:** transcrição grátis (Groq) + centavos de Claude por resumo. Margem altíssima.

---

## Próximo passo do catálogo

Esse é o serviço **#2** dos 6 da Kronos. Depois vêm: relatório automático (#3), conteúdo recorrente (#4), triagem de e-mail (#5), leitura de documentos/PDF (#6 — fecha o nicho advocacia).
