# Time de Agentes IA

A clínica opera com um **time de 5 agentes** especializados, coordenados por um **agente principal (orquestrador)**. Cada agente tem persona, escopo, ferramentas e prompt próprios.

## Organograma

```
                ┌────────────────────────────┐
                │    AGENTE PRINCIPAL         │
                │       (Orquestrador)        │
                │  Nome interno: "Aurora"     │
                └──────────────┬──────────────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────┐
        ▼          ▼           ▼           ▼          ▼
   ┌─────────┐┌─────────┐ ┌─────────┐ ┌─────────┐┌─────────┐
   │Agendam. ││Atendim. │ │Pós-venda│ │Marketing││ Backup  │
   │ "Bia"   ││ "Clara" │ │ "Diana" │ │ "Eva"   ││ Humano  │
   └─────────┘└─────────┘ └─────────┘ └─────────┘└─────────┘
```

## Mapa dos agentes

| Arquivo | Agente | Papel |
|---|---|---|
| `00_agente_principal_orquestrador.md` | **Aurora** | Recepciona, classifica intenção, roteia |
| `01_agente_agendamento.md` | **Bia** | Agendar, remarcar, cancelar |
| `02_agente_atendimento.md` | **Clara** | Tirar dúvidas sobre procedimentos |
| `03_agente_pos_venda.md` | **Diana** | Acompanha pós-procedimento e recompra |
| `04_agente_marketing.md` | **Eva** | Captação e qualificação de leads |

## Base de conhecimento

Os agentes consultam a pasta `base_conhecimento/` via RAG. Quando algo muda na clínica (novo serviço, novo preço, nova política), basta atualizar o arquivo correspondente — todos os agentes passam a usar a informação nova automaticamente.

## Princípios do time

1. **Especialização** — cada agente sabe muito bem um pedaço, não tenta saber tudo
2. **Mesma voz** — todos seguem o mesmo `05_tom_de_voz.md`
3. **Handoff fluido** — quando um agente passa para outro, o cliente nem percebe
4. **Humano > Agente** — qualquer agente pode escalar para humano sem fricção
5. **Guardrails fortes** — nada de diagnóstico médico, prescrição ou promessa de resultado
