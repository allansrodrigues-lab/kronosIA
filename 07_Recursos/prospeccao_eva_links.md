# Prospecção invertida — Links wa.me da Eva

O lead clica no link, o WhatsApp abre com a mensagem pronta, ele envia — e **ele** iniciou a conversa (zero risco de ban). A Eva assume: qualifica (setor, cidade, dor, urgência), registra no CRM (aba `Leads`, planilha interna) e avisa o Allan no WhatsApp quando o lead esquenta.

**Número:** 5519971514971 (`clinica01` — central de demos)
**Gatilho no roteador:** a mensagem precisa conter **"agente"** e **"Kronos"** (qualquer capitalização). A hashtag no fim identifica o canal.

## Links por canal

| Canal | Onde usar | Link |
|---|---|---|
| Site | Botão WhatsApp da landing | https://wa.me/5519971514971?text=Ol%C3%A1!%20Quero%20conhecer%20o%20agente%20de%20IA%20da%20Kronos%20%23site |
| E-mail | CTA dos e-mails de prospecção | https://wa.me/5519971514971?text=Ol%C3%A1!%20Quero%20conhecer%20o%20agente%20de%20IA%20da%20Kronos%20%23email |
| Ads | Google Ads (anúncio → WhatsApp) | https://wa.me/5519971514971?text=Ol%C3%A1!%20Quero%20conhecer%20o%20agente%20de%20IA%20da%20Kronos%20%23ads |
| Catálogo | QR code do catálogo impresso | https://wa.me/5519971514971?text=Ol%C3%A1!%20Quero%20conhecer%20o%20agente%20de%20IA%20da%20Kronos%20%23catalogo |
| Carta | QR code da carta de correio | https://wa.me/5519971514971?text=Ol%C3%A1!%20Quero%20conhecer%20o%20agente%20de%20IA%20da%20Kronos%20%23carta |
| LinkedIn | Bio / posts | https://wa.me/5519971514971?text=Ol%C3%A1!%20Quero%20conhecer%20o%20agente%20de%20IA%20da%20Kronos%20%23linkedin |

Mensagem pré-preenchida (todas): `Olá! Quero conhecer o agente de IA da Kronos #<canal>`

## Como funciona por dentro

```
wa.me → clinica01 → kronos-roteador-demo (gatilho "agente"+"kronos")
            └─ kronos-eva-prospeccao (bnwAPhtE8CSEJS9d)
                  ├─ sessão 24h por telefone (memória do workflow)
                  ├─ Sonnet 5 (Eva) — qualifica em até 4 trocas
                  ├─ linha de controle ###DADOS### → score/status
                  ├─ CRM: aba Leads (1tOXVM8f…), Origem = prospeccao-<canal>
                  └─ lead QUENTE → alerta no WhatsApp da Kronos (5519971266736)
                        com sugestão de chavinha (/advocacia, /solar, …)
```

- Fallback determinístico: lead que pede "falar com humano/Allan" vira quente mesmo se a IA falhar no JSON (lição do bug Schalletti).
- Sessão Eva expira em 24h; qualquer comando `/` do dono encerra a sessão Eva do número dele.
- Áudio ainda não é transcrito nesse fluxo (v2: plugar `kronos-transcrever-audio`); a Eva pede texto com jeitinho.

## Pendências

- [ ] Teste final ponta a ponta (bloqueado 10/07: crédito da API Anthropic zerado — afeta TODOS os bots)
- [ ] Colocar os links nos materiais (landing, e-mails, catálogo/QR, carta)
- [ ] v2: transcrição de áudio + buffer de mensagens picadas (padrão dos outros bots)
