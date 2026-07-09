# Filtro de Urgência — Cedro Saúde (⭐ diferencial do nicho)

Detecção de sinais de risco à saúde no WhatsApp, **antes** de qualquer classificação por IA.
**Não é a IA que decide se é uma emergência** — decide uma lista de sinais de alerta reconhecidos
pela literatura de triagem (protocolo inspirado no Manchester, simplificado para uso administrativo,
NUNCA clínico), rodando em um **Code node determinístico**. Mesma filosofia da calculadora de
payback da Zênite e da calculadora de financiamento da Schalletti: **decisão crítica não fica na mão
do LLM.**

**Por que isso importa mais aqui do que em qualquer outro nicho:** errar a triagem de uma dúvida
sobre limpeza de pele custa uma venda perdida. Errar a triagem de "dor no peito" tratando como
agendamento de rotina pode custar uma vida. O filtro roda em milissegundos, sem depender de a IA
"entender" a gravidade — e **sempre erra para o lado seguro** (falso positivo de urgência é só um
paciente que recebe orientação de procurar ajuda mais cedo do que precisava; falso negativo é
inaceitável).

---

## Fluxo

1. Mensagem chega ao orquestrador (já passou pelo buffer/debounce e pela transcrição de voz, se for áudio)
2. **Code node "Filtro de Urgência"** roda ANTES do nó Haiku — varre o texto por lista de sinais
3. Bateu sinal de risco → pula toda a classificação normal, dispara escalação imediata
4. Não bateu → segue pro fluxo normal (Haiku classifica intent)

## Sinais de alerta (lista-base, revisar com profissional de saúde antes de uso real)

| Categoria | Termos/expressões que disparam o filtro |
|---|---|
| Cardiovascular | dor no peito, aperto no peito, dor forte no peito, dor irradiando pro braço |
| Respiratório | falta de ar, não consigo respirar, respiração muito difícil, sufocando |
| Hemorragia | sangramento intenso, sangrando muito, hemorragia, não para de sangrar |
| Neurológico (sinais de AVC) | fraqueza súbita de um lado, boca torta, fala enrolada, não consigo falar direito, formigamento súbito de um lado |
| Consciência | desmaiei, perdi a consciência, desmaiou, não tá respondendo |
| Convulsão | convulsão, crise convulsiva, crise epiléptica |
| Alergia grave | reação alérgica grave, garganta fechando, inchaço na garganta, anafilaxia |
| Trauma | acidente grave, trauma na cabeça, batida forte na cabeça, caiu e bateu a cabeça |
| Saúde mental (crise aguda) | quero morrer, vou me matar, não aguento mais viver, pensamento suicida |
| Pediátrico | bebê com febre muito alta, recém-nascido não para de chorar, bebê roxo, bebê não respira direito |

## Code node — `filtrar_urgencia` (JavaScript)

```javascript
// Entrada: $json.mensagemTexto (já transcrita, se veio de áudio)
const texto = ($json.mensagemTexto || '').toLowerCase();

const SINAIS_URGENCIA = [
  /dor (forte |muito forte )?no peito/, /aperto no peito/, /dor.*(irradia|braço)/,
  /falta de ar/, /n[ãa]o consigo respirar/, /sufocando/, /respira[çc][ãa]o.*dif[ií]cil/,
  /sangramento intenso/, /sangrando muito/, /hemorragia/, /n[ãa]o para de sangrar/,
  /fraqueza s[uú]bita/, /boca torta/, /fala enrolada/, /n[ãa]o consigo falar direito/,
  /desmaiei/, /perdi a consci[eê]ncia/, /desmaiou/, /n[ãa]o (t[aá]|est[aá]) respondendo/,
  /convuls[ãa]o/, /crise convulsiva/, /crise epil[eé]ptica/,
  /rea[çc][ãa]o al[eé]rgica grave/, /garganta fechando/, /inchaço na garganta/, /anafilaxia/,
  /acidente grave/, /trauma na cabe[çc]a/, /bateu a cabe[çc]a/,
  /quero morrer/, /vou me matar/, /n[ãa]o aguento mais viver/,
  /bebe.*febre muito alta/, /rec[eé]m.nascido.*chorar/, /bebe roxo/, /bebe n[ãa]o respira/
];

const bateu = SINAIS_URGENCIA.some(padrao => padrao.test(texto));

if (bateu) {
  return [{ json: {
    urgencia: true,
    mensagemResposta:
      'Pelo que você descreveu, isso pode precisar de atendimento IMEDIATO. ' +
      'Por favor, ligue agora para o SAMU (192) ou vá até o pronto-socorro mais próximo. ' +
      'Já avisei nossa equipe aqui da Cedro Saúde e alguém vai te dar suporte também. ' +
      'Não espere — sua segurança vem primeiro.',
    escalarEquipe: true,
    motivoEscalacao: 'FILTRO_URGENCIA — sinal de risco detectado, encaminhar humano imediatamente'
  }}];
}

return [{ json: { urgencia: false } }];
```

## O que acontece quando dispara

1. Vera **não** processa a mensagem normalmente — a resposta acima (orientação de emergência) é
   enviada IMEDIATAMENTE, sem passar por Sonnet 5 (velocidade importa mais que personalização aqui)
2. Notificação simultânea no grupo da equipe (WhatsApp/Telegram) com a mensagem original do paciente
3. Sessão marcada com `status = urgencia_escalada` — quando um humano assume, o bot não reprocessa
   essa conversa automaticamente
4. Log na aba `Pacientes_ClinicaMedica` com motivo `FILTRO_URGENCIA`, para auditoria

## Limites conhecidos (documentar, não esconder)

- É uma lista de palavras-chave, **não é diagnóstico nem substitui triagem humana real** — existe
  pra pegar o caso óbvio e reduzir o risco do bot "conversar normalmente" com alguém em emergência,
  não pra ser um sistema clínico de verdade
- Falso positivo é aceitável e esperado (ex: "vi uma reportagem sobre dor no peito" pode disparar);
  falso negativo é o risco que a lista tenta minimizar, nunca eliminar
- Antes de qualquer uso com paciente real, a lista de termos deve ser revisada por um profissional
  de saúde do cliente — isso é MVP de demonstração, não dispositivo médico certificado
- Nunca prometer ao cliente real que isso substitui uma central de triagem telefônica humana
