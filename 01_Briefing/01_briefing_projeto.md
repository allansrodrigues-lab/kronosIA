# Briefing do Projeto

## 1. Identificação

| Campo | Informação |
|---|---|
| **Nome do projeto** | Automação Clínica de Estética |
| **Cliente** | [Nome da clínica] |
| **Responsável técnico** | Allan Rodrigues |
| **Data de início** | 2026-05-27 |
| **Previsão de entrega MVP** | 30 dias |
| **Plataforma principal** | n8n (self-hosted) |

## 2. Sobre o cliente

**Segmento:** Clínica de estética facial e corporal
**Porte:** Pequeno/médio (ex.: 2-5 profissionais, 200-500 atendimentos/mês)
**Localização:** [cidade/estado]

**Procedimentos oferecidos (exemplo):**
- Limpeza de pele profunda
- Peeling químico
- Botox e preenchimento
- Drenagem linfática
- Massagem modeladora
- Criolipólise
- Depilação a laser

## 3. Dores atuais

1. **Agenda mal aproveitada** — muitos no-shows e horários ociosos
2. **Atendimento manual no WhatsApp** consome 3-4h/dia da recepção
3. **Sem follow-up estruturado** depois do procedimento — perde recompra
4. **Leads de Instagram/Ads não são qualificados rapidamente** — perde para concorrência
5. **Sem visão clara de métricas** de conversão e ticket médio

## 4. Objetivos do projeto

### Objetivos de negócio
- Reduzir no-show em **30%** em 60 dias
- Aumentar taxa de recompra em **20%** em 90 dias
- Reduzir tempo de resposta no WhatsApp para **<2 minutos** (24/7)
- Aumentar conversão de lead para agendamento em **25%**

### Objetivos operacionais
- Liberar **15h/semana** da recepção
- Centralizar dados de clientes em uma única base
- Ter dashboard em tempo real para a gestora

## 5. Escopo do MVP

### Dentro do escopo
- Agente IA principal no WhatsApp (orquestrador)
- Fluxo de agendamento automático com confirmação 24h antes
- Fluxo de pós-venda (mensagem D+1, D+7, D+30)
- Captação e qualificação de leads
- Dashboard básico de métricas

### Fora do escopo (fase 2)
- Integração com sistema de pagamento online
- Programa de fidelidade
- App próprio da clínica
- Automação de prontuário eletrônico

## 6. Premissas e restrições

- Cliente já possui número WhatsApp Business
- A clínica usará a API oficial Cloud ou Z-API/Evolution
- LGPD: dados sensíveis (saúde) devem ter consentimento explícito
- Profissional responsável continuará validando agendamentos críticos

## 7. Riscos identificados

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Cliente não responde para configurar integrações | Média | Alto | Cronograma com check-ins semanais |
| API do WhatsApp bloquear o número | Baixa | Alto | Usar API oficial + boas práticas anti-spam |
| Agente IA dar resposta médica indevida | Média | Alto | Guardrails fortes + escalonamento humano |
| Resistência da equipe à mudança | Alta | Médio | Treinamento + período de coexistência manual+auto |
