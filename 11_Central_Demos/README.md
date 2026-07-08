# Kronos · Central de Demos (1 chip, várias demos)

Um número de WhatsApp só que mostra **todas as demos da Kronos**. Você troca a "chavinha" pelo seu próprio celular, sem abrir o n8n na frente do cliente.

```
WhatsApp (1 chip) → Evolution → Webhook /whatsapp-demo → Roteador
   ├─ comando do dono (/pizzaria /aurora /resumo /status) → troca o modo
   └─ mensagem normal → encaminha pro bot do modo atual:
        · pizzaria → DEMO-01-orquestrador-santaana
        · resumo   → kronos-resumo-audio
        · aurora   → (entra na próxima atualização)
```

- Workflow: `kronos-roteador-demo` (ID `2hYQv4sOQq5AOXmt`)
- O modo fica salvo na memória do próprio workflow (staticData) — persiste entre mensagens.

### Realidade do deploy (16/06)
- **Chip da demo = instância `clinica01`** (número `5519971514971`). É por ela que tudo responde.
- Webhook do `clinica01` aponta para `http://2.24.101.180:5678/webhook/whatsapp-demo` (o roteador). ✅ já redirecionado.
- Caminho real do bot da pizzaria: `/webhook/whatsapp-santaana-demo`.
- Tudo fixado em `clinica01` no código (sem variável `EVO_INSTANCE_DEMO`); dono fixado em `5519971266736` (Kronos).
- Comandar a chavinha: do **Kronos** → mandar pro número da demo (`5519971514971`).

## Chavinha (mande do SEU WhatsApp pro número da demo)

| Comando | Efeito |
|---|---|
| `/pizzaria` | demo vira a Bella Massa 🍕 |
| `/resumo` | demo vira o Resumo de Áudio 🎙️ |
| `/aurora` | (em breve) |
| `/status` | mostra o modo atual |

Só o número em `DEMO_OWNER_NUMBER` consegue trocar. O cliente, mandando mensagem normal, cai no modo ativo.

## Estado / pendências

- ✅ Chavinha LIGADA: webhook redirecionado, roteador testado (execução `success`).
- ✅ Pizzaria e troca de modo funcionam sem nada extra.
- ⏳ **Único pendente: `GROQ_API_KEY`** (transcrição do áudio). Sem ela, o modo resumo troca normal, mas o áudio responde "não consegui processar". A key é `$env.GROQ_API_KEY` no container n8n (`/docker/n8n-xve0/`) — exige adicionar no env + restart do n8n, OU fixar direto no nó "Transcrever (Groq Whisper)".

## Próximo passo
Plugar a **Aurora** na chavinha (hoje a `clinica01` está dedicada à pizzaria/resumo; pra Aurora voltar e entrar no `/aurora` precisa de ajuste).
