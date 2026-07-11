# Robô de Prospecção Ativa — chip descartável `prospeccao01`

Disparo automático de 1ª abordagem pra prospects do CRM, com ritmo humano, pelo chip **queimável** do Allan (nunca clinica01/kronosdemo — esses têm login gov/demos). Decisão do Allan em 10/07: "vale o teste, temos que tentar".

## Workflows (n8n)

| Workflow | ID | Estado | Função |
|---|---|---|---|
| `kronos-prospeccao-disparador` | `qVgwvD3ZW9COqdMA` | ⏸️ **desativado** (até chip parear + aquecer) | Cron 9h/14h/19h → envia até 2 abordagens/rodada |
| `kronos-prospeccao-respostas` | `RCg1zCr7RcSz1zmC` | ✅ ativo (aguardando instância) | Resposta de prospect → alerta Allan + marca CRM |

## Regras fixas do disparador (cinto de segurança)

- Máx. **6 envios/dia** (contando 1ª abordagem + follow-up), 2 por rodada.
- Espera aleatória de até 30 min após o cron + 2-7 min entre envios (nunca rajada).
- 4 templates girando + nome da empresa/nicho/cidade (nunca texto idêntico).
- Follow-up único após 4+ dias sem resposta; depois encerra.
- Blocklist fixa: números da casa (5519971266736 / 5519971514971 / 5519997237404).
- Anti-loop: robô manda e **para** — nunca responde sozinho.
- Chip offline → rodada abortada + alerta no WhatsApp da Kronos.
- Resumo de cada rodada no WhatsApp da Kronos.

## Fila no CRM (aba `Prospeccao` do Kronos CRM — Interno `1tOXVM8f…`)

O robô só envia pra linha com **`Status = Fila`** e **WhatsApp preenchido só com dígitos** (55DDDNÚMERO). Ciclo de status:

```
Fila → Abordado_1 → (4+ dias) → Abordado_2 → (fim)
                 ↘ Respondeu (prospect respondeu — Allan assume)
                 ↘ Nao_Perturbe (pediu sair — nunca mais recebe)
```

Quem abastece a fila: Allan/Claude via skill `kronos-prospeccao` (coletor 100% automático via Google Places fica pra quando decidir a conta Google Cloud).

## Checklist de go-live (nessa ordem)

1. [ ] **Allan autoriza**: criar instância `prospeccao01` na Evolution (bloqueado por permissão em 10/07)
2. [ ] **Allan autoriza**: apagar a linha 1 vazia da aba `Prospeccao` (o range `A1:L500` do robô já pressupõe isso)
3. [ ] Configurar webhook da instância → `https://n8n.kronosintelligence.com.br/webhook/prospeccao-respostas` (evento MESSAGES_UPSERT)
4. [ ] Parear o chip novo (QR no chat; se o WhatsApp recusar IP de datacenter → proxy residencial ~R$15)
5. [ ] **Aquecer 7-10 dias**: conversa normal, grupos, áudio — sem robô
6. [ ] Marcar 3-5 contatos como `Fila` (começar devagar) e ativar o disparador + restart n8n
7. [ ] Semana 1 com limite mental de 4/dia; se o chip seguir saudável, manter 6/dia

## Templates da 1ª abordagem (girando)

1. "Olá, {empresa}! 👋 Sou o Allan, da Kronos Intelligence. A gente coloca um agente de IA no WhatsApp de {nicho} pra atender clientes 24h — responde dúvidas, agenda e manda lembrete sozinho. Posso te mostrar uma demonstração rápida por aqui mesmo?"
2. "Oi, tudo bem? Falo com {empresa}? Trabalho com atendimento por IA pra {nicho}. Muito cliente chama fora do horário e acaba indo pro concorrente — o agente que a gente monta responde na hora, dia e noite. Quer ver funcionando? Te mando uma demo aqui."
3. "Olá! Aqui é o Allan, da Kronos Intelligence. Ajudamos {nicho} a não perder cliente no WhatsApp: um agente de IA tira dúvidas, agenda e faz pós-atendimento sozinho, 24/7. Se fizer sentido, te mostro em 2 minutos uma demo do seu setor. Posso?"
4. "Oi, {empresa}! Vi o trabalho de vocês aí em {cidade}. A Kronos monta agentes de IA pro WhatsApp de {nicho} — atendimento 24h, agendamento e lembretes automáticos. Topa ver uma demonstração rápida por aqui?"

Follow-up: "Oi! Passando só pra saber se você chegou a ver minha mensagem 🙂 Se quiser, te mostro o agente de IA funcionando — leva 2 minutos. Se não for o momento, sem problema nenhum, é só me dizer."

⚠️ Sem link na 1ª mensagem (link em msg fria aumenta score de spam). A demo vai quando o prospect responde.

## Risco assumido

Cold outreach automatizado viola os termos do WhatsApp mesmo em volume baixo — o chip pode ser banido. Por isso: chip descartável, sem logins, sem contatos pessoais. Se banir → compra outro pré-pago e repete o pareamento (passos 3-4).
