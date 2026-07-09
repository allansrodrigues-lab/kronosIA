# 16_ClinicaMedica — Cedro Saúde (Demo Kronos)

Nicho **Clínica Médica** (multiespecialidade) da Kronos Intelligence — padrão "do A ao Z", igual
Solar/Advocacia/Imobiliária. Marca 100% fictícia: **Cedro Saúde**, Campinas/SP.
Assistente: **Vera** (consentimento LGPD + dúvida administrativa + agendamento + orientação de
teleconsulta).

## Por que esse nicho é diferente dos outros

Compliance pesa mais aqui do que em qualquer outro nicho da Kronos:
- **CFM Resolução 2.336/2023** — regula telemedicina e publicidade médica; o bot não pode prometer
  diagnóstico à distância, cura ou resultado de tratamento.
- **LGPD Art. 11 (Lei 13.709/2018)** — dado de saúde é dado pessoal sensível; exige consentimento
  específico, não só o genérico de uso do WhatsApp.
- **Risco real, não só comercial** — errar a triagem de "dor no peito" é qualitativamente diferente
  de errar a triagem de "quero uma limpeza de pele". Por isso o nicho tem uma camada de segurança
  que nenhum outro tem (ver abaixo).

## Por que "Cedro" e "Vera"

- **Cedro** = árvore de vida longa e raiz funda — metáfora de solidez/saúde sem cair no clichê
  "vida/vitalidade" batido do setor de saúde.
- **Vera** = do latim "verus" (verdadeira). A promessa do agente é nunca fingir saber o que não
  sabe — ela é literalmente "verdadeira" sobre seus limites (não diagnostica, sempre encaminha ao
  médico). Segue o padrão dos outros nomes da Kronos (Aurora, Bia, Clara, Diana, Eva, Léa, Sofia, Helena).

## ⭐ Diferencial do nicho: Filtro de Urgência determinístico

Igual a calculadora de payback da Zênite não é "LLM fazendo conta", a segurança do paciente não
pode depender de um classificador probabilístico. Uma lista de sinais de alerta (dor no peito,
falta de ar, sangramento intenso, sinais de AVC, crise convulsiva, crise suicida, etc.) roda em um
**Code node determinístico ANTES do classificador Haiku** — se bater, a mensagem nunca é tratada
como conversa normal, vai direto pra escalação humana com orientação de emergência (SAMU 192).
Detalhe completo em `agentes/02_agente_triagem_regras.md`.

## Estrutura

```
base_conhecimento/
  00_cedro_saude_perfil.md        — identidade da clínica, equipe, endereço (fictícios)
  01_especialidades_convenios.md  — especialidades, valores, convênios, preparo de exames
  02_politicas_lgpd_cfm.md        — LGPD, CFM 2.336/2023, escalação
  03_tom_de_voz_vera.md           — persona Vera (acolhedora, nunca opina sobre saúde)
agentes/
  00_orquestrador_clinicamedica.md  — intents (Haiku) + filtro de urgência + sessão
  01_agente_atendimento_vera.md     — prompt LIVE da Vera (Sonnet 5): consentimento → dúvida → agendamento
  02_agente_triagem_regras.md       — ⭐ Code node: filtro de urgência determinístico
workflows/
  (a criar — montagem n8n)
```

## Status (09/07/2026)

- [x] Nome cravado: Cedro Saúde / persona Vera
- [x] Persona + agentes (Vera, orquestrador, filtro de urgência) — texto pronto, com dados fictícios
- [x] Base de conhecimento (4 arquivos: perfil, especialidades/convênios, políticas LGPD/CFM, tom de voz)
- [ ] Logo (Canva)
- [x] Workflows no n8n — ✅ 09/07: `DEMO-CLINMED-01-orquestrador-cedro` (`ocKeFwNKe6ZlWwoH`, 28 nós, filtro de urgência ANTES do Haiku) + `DEMO-CLINMED-02-agente-vera` (`DNyQkMnxKTPvlbLK`, 21 nós). Ambos ativos, validados, testados fim-a-fim (execuções 15694/15698)
- [x] Planilha CRM própria — ✅ 09/07 "Kronos CRM — Cedro Saúde" (`1LlYzHGOGSYR0CWPzNT15fMgtdkTjZTKMIHtZY1SoCfM`), abas `Pacientes_ClinicaMedica` + `Sessoes_ClinicaMedica` + `Consultas` + `Log_Conversas` + `Log_Monitoramento`
- [x] Chavinha na Central de Demos — ✅ 09/07 comando `/medica` (aliases `/clinica-medica`, `/clinicamedica`) no Roteador `2hYQv4sOQq5AOXmt`; perfil WhatsApp "Cedro Saúde 🩺"; webhook `/webhook/whatsapp-clinicamedica-demo`
- [x] Test harness — ✅ 09/07 bot `medica`, cenários M01-M07 (M07 = filtro de urgência via nó "Preparar Urgência"; M03 = teste negativo, sintoma leve NÃO dispara), suite 7/7 verde. Bônus: Solar S01-S07 registrado junto (estava fora do harness persistente — paridade corrigida), 7/7 verde
- [ ] Voice Agent (ElevenLabs)
- [x] Demo PNG — ✅ 09/07 `07_Recursos/demo_clinica_medica.png` (LGPD + não-opina + agendamento + urgência SAMU; notes encurtadas por causa do bug de corte do bold)
- [x] Aba animada na landing — ✅ 09/07 `seg-medica` (accent verde #4cd97b, motor `__waStartMedica`, 11 mensagens), verificada no preview local (ciclo completo + console limpo)
- [x] Skill `kronos-clinica-medica` dedicada — ✅ 09/07 (`.claude/skills/kronos-clinica-medica/SKILL.md`)
- [ ] Deploy da landing (push + VPS)

**Falta só: logo (Canva), Voice Agent (ElevenLabs) e deploy da landing.**

## Nota sobre uso real (não esconder do cliente)

Este é um protótipo de demonstração com dados fictícios. Antes de qualquer uso com paciente real:
1. A lista de sinais do filtro de urgência deve ser revisada por profissional de saúde do cliente.
2. O texto de consentimento LGPD deve passar por revisão jurídica do cliente.
3. Convênios, valores, equipe e CRMs (fictícios aqui) precisam ser substituídos pelos dados reais.
