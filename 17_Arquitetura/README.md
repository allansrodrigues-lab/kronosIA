# Nicho Arquitetura — Estúdio Traço (fictício)

7º nicho Kronos, padrão A-ao-Z (mesma régua de 15_Solar e 16_ClinicaMedica).

## Persona
- **Escritório:** Estúdio Traço — Arquitetura & Interiores (fictício, Campinas/SP)
- **Agente de IA:** **Marina** — recepção, qualificação de projeto, estimativa de investimento e agendamento de reunião de briefing
- **Identidade visual:** navy Kronos `#020c2a` + acento terracota `#c47a5a` (cor do nicho)

## ⭐ Diferenciais do nicho (vs. os 6 existentes)
1. **Qualificação por tipo e fase de projeto** — residencial/comercial/reforma/interiores × terreno/planta pronta/obra em andamento. É o "matching" da Schalletti adaptado a projeto.
2. **Calculadora de estimativa de investimento** (Code node determinístico, padrão payback/financiamento): área m² × faixa de honorário por tipo → devolve **faixa**, nunca valor fechado. Normalização BR obrigatória (150m², R$ 15.000).
3. **Compliance CAU:** Marina NUNCA fornece solução técnica, planta, dimensionamento ou parecer — isso é ato privativo de arquiteto. Ela qualifica e agenda o briefing.
4. **Reunião de briefing** (30 min, online ou presencial) como conversão principal — equivalente à "visita técnica" do Solar.

## Estrutura
```
17_Arquitetura/
├── README.md                          ← este arquivo
├── 00_agente_orquestrador_arquitetura.md
├── 01_agente_marina.md
└── base_conhecimento/
    ├── 01_servicos_e_projetos.md
    ├── 02_precos_honorarios.md
    ├── 03_faq_clientes.md
    ├── 04_politicas_escritorio.md
    └── 05_tom_de_voz.md
```

## Componentes
| Componente | ID / caminho | Status |
|---|---|---|
| Planilha CRM própria | `1rXds8GoSGT5zT4LHzn7atNSJObStcxsgq65pUHRWKTY` | ✅ compartilhada, 4 abas + headers, gravação testada |
| Workflow orquestrador | `tHFU2KbsogpVq3wE` (DEMO-ARQ-01) | ✅ ativo, smoke test ok |
| Workflow Marina | `NDwmJkELDwXMnOPx` (DEMO-ARQ-02) | ✅ ativo, smoke test ok |
| Calculadora estimativa | Code node "Calculadora de Estimativa" DENTRO da Marina (decisão: determinística pré-prompt, não sub-workflow) | ✅ testada (150m² → R$ 12.000-22.500) |
| Chavinha central de demos | `/arquitetura` no `kronos-roteador-demo` | ✅ registrada |
| Test harness | cenários ARQ01-ARQ08 (inclui ⭐ PEDIDO_TECNICO) | ✅ persistido no run_tests.py do VPS |
| Voice Agent ElevenLabs | `agent_9701kx8jhnz1fvrtegsajhn8cegr` (voz Amanda Kelly, Sonnet 4.6, ferramenta `agendar_briefing` → workflow `Vg23r2dgGs3utjEV` `/webhook/marina-briefing`) | ✅ publicado, testado E2E (chat → n8n → aba Briefings) |
| Logo (Canva) | `17_Arquitetura/logo_estudio_traco.png` (design Canva `DAHPFDB2Q7g`) | ✅ |
| Demo PNG | `07_Recursos/demo_arquitetura.png` | pendente |
| Aba landing | `#seg-arquitetura` | pendente |
| Skill | `.claude/skills/kronos-arquitetura` | ✅ criada |

## Abas do CRM (criar após o compartilhamento)
- `Sessoes_Arquitetura`: jid, nome, tipo_projeto, area_m2, cidade, fase_projeto, prazo, status, historico, data_contato
- `Briefings`: data_briefing, periodo, modalidade, jid, nome, tipo_projeto, area_m2, faixa_estimada, status, obs
- `Leads_Arquitetura`: Data_Contato, Nome, Telefone_JID, Tipo_Projeto, Area_m2, Cidade, Fase_Projeto, Prazo, Faixa_Estimada, Status, Observacoes
- `Log_Conversas`: timestamp, jid, quem, mensagem
