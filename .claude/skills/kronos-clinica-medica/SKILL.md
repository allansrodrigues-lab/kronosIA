---
name: kronos-clinica-medica
description: Operar e customizar o nicho Clínica Médica da Kronos — Cedro Saúde (fictícia) com a Vera (agendamento + dúvida administrativa + ⭐ filtro de urgência determinístico + consentimento LGPD). Use para testar a demo, corrigir a Vera, ajustar a lista de sinais de urgência, adaptar para cliente real, ou diagnosticar falha nos workflows. Gatilhos: "clínica médica", "Cedro", "Vera", "filtro de urgência", "triagem de urgência", "bot médico", "demo médica", "consentimento LGPD".
---

# Kronos — Nicho Clínica Médica (Cedro Saúde / Vera)

Montado em 09/07/2026 (sessão Fable), padrão A-ao-Z clonado do Solar/Zênite.
Fonte de conteúdo: `16_ClinicaMedica/` (agentes + base_conhecimento + README com status).

## O que diferencia este nicho de TODOS os outros

1. **⭐ Filtro de urgência determinístico** — Code node "Filtro de Urgência" roda ANTES do
   classificador Haiku. Lista de regex de sinais de risco (dor no peito, falta de ar, AVC,
   convulsão, crise suicida, pediátrico grave...). Se bater: orientação SAMU 192 + alerta equipe +
   sessão `urgencia_escalada` — o Haiku nem roda. Falso positivo aceitável; falso negativo não.
2. **Silêncio pós-urgência** — sessão com status `urgencia_escalada` faz o "Decidir Rota" devolver
   `[]` (bot não reprocessa a conversa; humano assumiu). Pra reativar o bot pro número: mudar o
   status da linha em `Sessoes_ClinicaMedica` para `encerrado`.
3. **Consentimento LGPD como portão** — Vera não coleta dado algum antes do aceite (dado de saúde =
   sensível, Art. 11 LGPD). Fallback determinístico: regex de aceite ("sim/pode/claro/autorizo")
   marca `consentimento_lgpd=aceito` mesmo se o modelo esquecer.
4. **Vera NUNCA opina sobre sintoma** — prompt com 9 regras absolutas (CFM 2.336/2023): sem
   diagnóstico, sem medicamento, sem promessa de cura, teleconsulta só com decisão do médico.

## IDs e caminhos

| Peça | ID / caminho |
|---|---|
| Orquestrador | `ocKeFwNKe6ZlWwoH` (DEMO-CLINMED-01-orquestrador-cedro, 28 nós) |
| Agente Vera | `DNyQkMnxKTPvlbLK` (DEMO-CLINMED-02-agente-vera, 21 nós) |
| Webhook | `/webhook/whatsapp-clinicamedica-demo` |
| Chavinha | `/medica` (aliases `/clinica-medica`, `/clinicamedica`) no Roteador `2hYQv4sOQq5AOXmt` |
| CRM | `1LlYzHGOGSYR0CWPzNT15fMgtdkTjZTKMIHtZY1SoCfM` ("Kronos CRM — Cedro Saúde") |
| Abas CRM | `Sessoes_ClinicaMedica` · `Pacientes_ClinicaMedica` · `Consultas` · `Log_Conversas` · `Log_Monitoramento` |
| Test harness | bot `medica`, cenários M01-M07 em `/docker/test-harness/run_tests.py` (VPS) |
| Demo PNG | `07_Recursos/demo_clinica_medica.png` (gerador: `gerar_demo_whatsapp.py`, lista `medica`) |
| Landing | aba `seg-medica` + motor `__waStartMedica` em `07_Recursos/index.html` (accent verde #4cd97b) |

## Intents (Haiku, 7 + urgência fora do classificador)

`AGENDAR` · `DUVIDA_ADMINISTRATIVA` · `DUVIDA_CLINICA` (nunca opina — vira convite pra consulta) ·
`TELECONSULTA` · `POS_CONSULTA` · `RECLAMACAO` (escala) · `OUTRO`. Urgência NÃO é intent — é o
Code node antes de tudo.

## Testar

```bash
# suite de regressão (do VPS)
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 'cd /docker/test-harness && python3 run_tests.py medica'
# M07 = urgência: extract_intent devolve "URGENCIA" quando o nó "Preparar Urgência" rodou
```

Teste manual sem WhatsApp: POST no webhook com JID `5500...` fake (payload padrão Evolution).
Urgência: mandar "dor forte no peito" → conferir execução com só ~5 nós (pula Haiku/Vera).

## Consertos comuns

- **Sessão travada / bot mudo pro número** → ver status na `Sessoes_ClinicaMedica`; se
  `urgencia_escalada`, é intencional (humano assumiu) — mudar pra `encerrado` reativa.
- **Ajustar sinais de urgência** → editar o array `SINAIS_URGENCIA` no nó "Filtro de Urgência"
  (patchNodeField em `parameters.jsCode`). ⚠️ Ao adaptar pra cliente real, a lista DEVE ser
  revisada por profissional de saúde do cliente (está documentado como MVP, não dispositivo médico).
- **Vera opinando sobre sintoma** → reforçar prompt no nó "Montar Prompt Vera" (workflow
  `DNyQkMnxKTPvlbLK`) — regras absolutas 1-4; nunca só prompt: conferir se o texto do paciente
  passou pelo filtro (a resposta certa pode ser adicionar o termo à lista).
- **Consulta confirmada mas sem linha na aba Consultas** → mesmo padrão do bug Schalletti; o
  fallback por regex no "Parsear Resposta Vera" já cobre dia+período+"confirmad"; conferir se a
  mensagem da Vera usa outra palavra (ex.: "reservado") e ampliar o regex.

## Adaptar para cliente real (checklist)

1. Substituir TODOS os dados fictícios da base (`16_ClinicaMedica/base_conhecimento/`): equipe,
   CRMs (médicos), convênios, valores, endereço.
2. Revisão da lista de urgência por profissional de saúde + texto LGPD por jurídico do cliente.
3. Instância Evolution própria + planilha CRM própria (regra-mãe: nunca compartilhar base).
4. Trocar `clinica01` hardcoded nos nós de notificação de equipe pela instância do cliente.
5. Rodar a suite `medica` do harness apontando pro webhook novo antes de ir ao vivo.
