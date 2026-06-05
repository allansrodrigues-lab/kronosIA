# Projeto de Automação — Clínica de Estética

> Estrutura profissional para implementação de automações de agendamento, atendimento via WhatsApp, pós-venda e marketing usando **n8n** e agentes de IA.

---

## Visão geral

Este repositório organiza toda a documentação, fluxos, agentes e métricas do projeto de automação da clínica. A estrutura segue boas práticas de projetos de automação e foi pensada para facilitar manutenção, evolução e entrega de valor desde o dia 1.

## Estrutura de pastas

```
teste Automação/
├── 01_Briefing/              → Briefing, escopo, objetivos, stakeholders
├── 02_Documentacao/          → Arquitetura, integrações, glossário
├── 03_Fluxos_Automacao/      → Documentação dos fluxos n8n
├── 04_Agentes_IA/            → Time de agentes + base de conhecimento
│   └── base_conhecimento/    → Conteúdo que alimenta os agentes
├── 05_Checklist_Testes/      → Planos de teste e QA
├── 06_Metricas/              → KPIs, dashboard e relatórios
├── 07_Recursos/              → Prompts de referência, credenciais
└── README.md                 → Este arquivo
```

## Como navegar

| Quero... | Vá para... |
|---|---|
| Entender o projeto | `01_Briefing/01_briefing_projeto.md` |
| Ver os fluxos de automação | `03_Fluxos_Automacao/README.md` |
| Conhecer o time de agentes IA | `04_Agentes_IA/00_agente_principal_orquestrador.md` |
| Testar antes de subir para produção | `05_Checklist_Testes/01_checklist_geral.md` |
| Acompanhar resultados | `06_Metricas/01_kpis_principais.md` |

## Status do projeto

- **Fase atual:** Discovery / Estruturação inicial
- **Plataforma de automação:** n8n
- **Canal principal:** WhatsApp (via Z-API ou Evolution API)
- **Modelo de IA:** Claude / GPT (a definir conforme custo-benefício)

## Convenções

- Documentação em **Markdown** (`.md`)
- Nomenclatura de pastas com prefixo numérico para ordenação
- Cada fluxo possui: descrição, gatilhos, passos, integrações, tratamento de erros
- Cada agente possui: persona, escopo, ferramentas, prompt base, exemplos
