# Pizzaria Bella Massa — Bot de Pedidos WhatsApp

**Cliente:** Pizzaria Bella Massa
**Endereço:** Av. Itália, 1200 — Centro/SP — CEP 13000-000
**WhatsApp:** (19) 98289-4384
**Horário:** 18h00 – 23h55 (todos os dias)
**Facebook:** Pizzaria Bella Massa (3.082 curtidas)

---

## Agente

| Arquivo | Nome | Papel |
|---|---|---|
| `agentes/00_orquestrador_santaana.md` | Haiku | Classifica intent e roteia |
| `agentes/01_agente_pedido_ana.md` | **Ana** | Recebe pedido, monta carrinho, passa para humano finalizar |

## Base de conhecimento

| Arquivo | Conteúdo |
|---|---|
| `base_conhecimento/01_cardapio_completo.md` | Todos os sabores por categoria com preços |
| `base_conhecimento/02_combos_e_promocoes.md` | Combos pizza e esfiha |
| `base_conhecimento/03_bordas_e_extras.md` | Bordas, refrigerantes, extras |
| `base_conhecimento/04_politicas.md` | Entrega, pagamento, tempo estimado |
| `base_conhecimento/05_tom_de_voz.md` | Identidade de comunicação |

## Arquitetura do fluxo

```
WhatsApp → Evolution API → n8n Webhook
    └─ Orquestrador (Haiku classifica intent)
            ├─ FAZER_PEDIDO / VER_CARDAPIO / VER_COMBO → Ana (Sonnet)
            ├─ RASTREAR_PEDIDO → resposta direta
            ├─ HORARIO_ENTREGA → resposta direta
            └─ RECLAMACAO → escalação humana
```

## Carrinho (Dado_Temp na sessão)

```json
{
  "etapa": "montando_pedido | confirmando | finalizado",
  "itens": [
    {
      "tipo": "pizza | esfiha | mini_calzone | combo",
      "sabor": "calabresa",
      "metade2": null,
      "borda": "requeijao",
      "qtd": 1,
      "preco": 40.00
    }
  ],
  "total": 40.00,
  "tipo_entrega": "entrega | retirada",
  "endereco": null,
  "pagamento": null
}
```

## Intents suportados

| Intent | Exemplo |
|---|---|
| `FAZER_PEDIDO` | "quero uma pizza", "me manda o cardápio" |
| `VER_CARDAPIO` | "quais sabores vocês têm?" |
| `VER_COMBO` | "tem combo?", "quero combo" |
| `RASTREAR_PEDIDO` | "cadê meu pedido?", "quanto tempo?" |
| `PRECO` | "quanto custa?", "qual o valor?" |
| `HORARIO_ENTREGA` | "vocês estão abertos?", "até que horas?" |
| `RECLAMACAO` | "chegou fria", "errou o pedido" |

## Observações importantes

- **Meia a meia:** pizza pode ser dividida em 2 sabores — cobra-se o maior preço
- **Borda de requeijão:** GRÁTIS (destacar sempre)
- **Entrega vs retirada:** perguntar sempre
- **Finalização:** Ana monta o pedido completo e passa para atendente humano confirmar via WhatsApp — a pizzaria NÃO tem sistema integrado ainda
- **Horário fora do expediente:** avisar que abre às 18h
