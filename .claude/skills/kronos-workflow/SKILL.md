---
name: kronos-workflow
description: Criação e configuração de workflows n8n para o projeto Kronos Intelligence. Use esta skill sempre que precisar: criar novo workflow de automação, adaptar fluxo existente para novo cliente, configurar integração WhatsApp/Google/agendamento, gerar JSON do workflow, escrever guia de montagem manual, ou configurar credenciais. Também use quando o usuário mencionar "workflow", "fluxo", "n8n", "automação", "novo cliente", "configurar atendimento", "agendamento automático", "lembrete", "pós-venda". Workflows ficam em 07_Recursos/.
---

# Kronos Workflow

## Contexto técnico
- **n8n:** rodando em container Docker no VPS (2.24.101.180)
- **Evolution API:** integração WhatsApp
- **Google Sheets:** base de dados dos clientes/agendamentos
- **Google Calendar:** agenda das clínicas
- **IA:** Claude/OpenAI via API (chaves da Kronos)

## Workflows existentes
| Arquivo | Função |
|---|---|
| `workflow_01_orquestrador.json` | Orquestrador principal — roteia mensagens para agentes |
| `workflow_02_agendamento.json` | Agendamento de consultas |
| `workflow_03_atendimento.json` | Atendimento geral via WhatsApp |
| `workflow_04_lembrete_24h.json` | Lembretes 24h antes da consulta |
| `workflow_05_pos_venda.json` | Pós-venda e fidelização |

## Padrão de nomenclatura
- Arquivos: `workflow_NN_nome.json`
- Guia: `workflow_NN_nome_guide.md`
- Montagem manual: `workflow_NN_nome_montagem_manual.md`

## Como criar novo workflow

### 1. Definir escopo
- Gatilho (webhook WhatsApp, schedule, manual)
- Objetivo do fluxo
- Integrações necessárias
- Agente de IA envolvido (se houver)

### 2. Estrutura padrão de um workflow
```
Webhook (Evolution API)
  → Extrai dados da mensagem
  → Verifica contexto (Google Sheets)
  → Chama Agente IA (Claude)
  → Resposta via WhatsApp
  → Atualiza Google Sheets
  → (opcional) Notificação interna
```

### 3. Variáveis de ambiente por cliente
Nunca hardcodar credenciais. Usar variáveis no n8n:
- `EVOLUTION_INSTANCE_{{CLIENTE}}` — instância WhatsApp
- `GOOGLE_SHEET_ID_{{CLIENTE}}` — planilha do cliente
- `GOOGLE_CALENDAR_ID_{{CLIENTE}}` — agenda do cliente

### 4. Entregáveis para cada workflow
1. **JSON do workflow** — importável no n8n
2. **Guia** (`_guide.md`) — explicação de cada nó
3. **Montagem manual** (`_montagem_manual.md`) — passo a passo visual

## Adaptação para novo nicho
Ao criar workflow para advocacia ou outro nicho:
- Substituir terminologia (consulta → reunião, paciente → cliente)
- Ajustar base de conhecimento do agente
- Manter estrutura técnica idêntica
- Documentar diferenças no guia

## Divisão de acesso por cliente
- **Kronos acessa:** n8n, Evolution API, chaves de IA, logs
- **Cliente acessa:** apenas Google Sheets/Calendar próprios
- **Cliente NÃO acessa:** n8n, fluxos, prompts, chaves de API
