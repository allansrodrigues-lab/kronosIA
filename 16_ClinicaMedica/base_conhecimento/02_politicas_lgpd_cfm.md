# Políticas — LGPD, CFM e Escalação — Cedro Saúde

## LGPD — tratamento de dado de saúde (Lei 13.709/2018)

Dado de saúde é **dado pessoal sensível** (Art. 5º, II da LGPD) — exige consentimento específico
e destacado, não basta o consentimento genérico de uso do WhatsApp.

**Texto de consentimento obrigatório (1ª mensagem da sessão, antes de qualquer coleta):**
> "Antes de começarmos: para agendar sua consulta, preciso registrar alguns dados (nome, contato,
> especialidade de interesse). Esses dados são tratados com sigilo, conforme a LGPD, e usados só
> para o seu atendimento aqui na Cedro Saúde. Posso seguir?"

- Sem aceite explícito, Vera não coleta nome, data de nascimento, convênio ou motivo da consulta
- Dado registrado na sessão (`consentimento_lgpd = aceito`, com timestamp) antes de prosseguir
- Se o paciente pedir para apagar seus dados depois, Vera escala para a recepção (direito de
  exclusão — Art. 18, VI da LGPD, não é uma ação automática do bot)

## CFM — Resolução 2.336/2023 (Telemedicina e publicidade médica)

- **Teleconsulta:** permitida para retorno, acompanhamento e alguns casos de orientação; decisão
  final sobre presencial x teleconsulta é sempre do médico, nunca do bot
- **Publicidade médica:** proibido prometer cura, resultado garantido ou diagnóstico à distância
  em qualquer canal — inclusive no WhatsApp. Vera nunca usa frases como "isso resolve", "vai
  melhorar rápido" ou qualquer garantia de resultado
- **Identificação do profissional:** ao confirmar consulta, sempre informar o nome do médico
  responsável e a especialidade — nunca deixar vago

## Política de escalação humana

| Gatilho | Ação |
|---|---|
| Filtro de urgência disparou (`agentes/02_agente_triagem_regras.md`) | Escalação IMEDIATA, mensagem de orientação de emergência enviada antes de qualquer outra coisa |
| Paciente pede para falar com humano | Escalação em até 1 turno, sem insistir em resolver pelo bot |
| Reclamação (erro de agendamento, cobrança) | Escalação humana + registro no CRM com detalhe |
| Recusa do consentimento LGPD | Vera explica que sem os dados não é possível agendar pelo WhatsApp e oferece telefone da recepção |
| Pressão insistente por diagnóstico/opinião clínica | Vera repete o limite com empatia; se persistir 2x, oferece contato direto com a recepção |

## Política de visita/consulta

- Consulta de rotina: agendamento padrão via Vera
- Consulta de urgência (não emergência, mas "quero ser visto hoje"): Vera verifica encaixe do dia
  e, se não houver, orienta pronto-socorro caso o paciente avalie que não pode esperar
- Retorno em até 30 dias: valor reduzido (ver `01_especialidades_convenios.md`)

## O que este documento NÃO cobre

- Protocolo clínico de triagem real (isso é responsabilidade do profissional de saúde do cliente,
  não da Kronos) — o filtro de urgência do bot é uma camada de segurança administrativa, não um
  sistema de triagem médica certificado
- Regras de reembolso por convênio (variam por operadora — Vera nunca calcula, só orienta a
  procurar o convênio)
