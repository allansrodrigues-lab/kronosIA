---
name: kronos-agente
description: Criação e configuração de agentes de IA para o projeto Kronos Intelligence. Use esta skill sempre que precisar: criar novo agente de IA, adaptar agente para novo nicho (advocacia, clínica médica, etc.), escrever ou atualizar prompt base, definir persona e tom de voz, configurar base de conhecimento, ou documentar escopo e ferramentas do agente. Também use quando o usuário mencionar "novo agente", "criar agente", "prompt do agente", "persona", "base de conhecimento", "agente para advocacia", "agente para clínica", "tom de voz", "Bia", "Clara", "Diana". Agentes ficam em 04_Agentes_IA/.
---

# Kronos Agente IA

## Agentes existentes
| Arquivo | Nome | Função |
|---|---|---|
| `00_agente_principal_orquestrador.md` | Orquestrador | Roteia para agentes especializados |
| `01_agente_agendamento.md` | — | Gerencia agendamentos |
| `02_agente_atendimento.md` | Bia | Atendimento geral WhatsApp |
| `03_agente_pos_venda.md` | Clara | Pós-venda e fidelização |
| `04_agente_marketing.md` | Diana | Campanhas e reativação |

## Base de conhecimento (04_Agentes_IA/base_conhecimento/)
- `01_servicos_e_procedimentos.md` — o que a clínica oferece
- `02_precos_e_pacotes.md` — tabela de preços
- `03_faq_clientes.md` — perguntas frequentes
- `04_politicas_clinica.md` — regras e políticas
- `05_tom_de_voz.md` — identidade de comunicação

## Estrutura padrão de um agente

```markdown
# Nome do Agente

## Persona
Nome, personalidade, tom de voz, como se apresenta

## Escopo
O que este agente faz e NÃO faz (limites claros)

## Ferramentas disponíveis
- Google Calendar (leitura/escrita)
- Google Sheets (leitura/escrita)
- WhatsApp via Evolution API
- Handoff para outros agentes

## Prompt base
[Prompt completo que define o comportamento]

## Exemplos de interação
[Diálogos de referência]

## Condições de handoff
Quando passar para outro agente
```

## Como criar agente para novo nicho

### Passo 1 — Definir persona
- Nome (humanizado, ex: Ana, Carlos)
- Tom: formal (advocacia) ou acolhedor (clínica)
- Limitações do que pode responder

### Passo 2 — Construir base de conhecimento
Criar os 5 arquivos adaptados para o nicho:
- Serviços → áreas de atuação (advocacia) ou especialidades (clínica médica)
- Preços → honorários ou tabelas
- FAQ → dúvidas comuns do setor
- Políticas → regras do escritório/clínica
- Tom de voz → linguagem do setor

### Passo 3 — Escrever prompt base
Seguir o padrão:
```
Você é [Nome], assistente de IA de [Nome do Cliente].
Sua função é [objetivo principal].
Você pode: [lista do que pode fazer]
Você NÃO deve: [limites claros]
Sempre que [condição], faça [ação].
Tom: [descrição do tom]
```

### Passo 4 — Definir handoffs
Mapear quando o agente passa o atendimento para:
- Outro agente especializado
- Atendimento humano
- Confirmação de agendamento

## Divisão por nicho
| Nicho | Diferenças principais |
|---|---|
| Clínica estética | Agendamento, pós-venda, reativação |
| Clínica médica | + Triagem, + protocolos de urgência |
| Advocacia | Tom formal, sem dar pareceres jurídicos, foco em captação |

## Regra de ouro
O agente nunca deve: dar diagnósticos médicos, pareceres jurídicos, comprometer valores sem aprovação humana, ou prometer o que o cliente não autorizou.
