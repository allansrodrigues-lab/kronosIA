# Roteiro de Demo — Advocacia (Ferraz & Nogueira · Léa)

Demo "do A ao Z" para gravar/apresentar e virar material no site.
Cada bloco demonstra UMA função. Teste do número da Kronos (`5519971266736`) contra o chip da demo.

## Pré-requisitos
- Na chavinha, ativar o modo `/advocacia` (perfil "Ferraz & Nogueira Advogados ⚖️").
- Testar de um número **sem bot** (senão dá loop).
- clinica01 logada (`state: open`).

---

## Roteiro (ordem sugerida)

**1. Abertura + triagem** — *atende 24h, identifica a área*
- Você: `Boa noite, fui demitido sem justa causa e queria entender meus direitos`
- Esperado: Léa acolhe com elegância, identifica **Trabalhista**, menciona o Dr. Eduardo Ferraz.

**2. Áudio → responde falando** — *entende áudio + VOZ (espelha o canal)*
- Você: manda um **áudio** contando o caso.
- Esperado: a Léa **responde em áudio** (voz Alice, BR). Se mandar texto depois, ela volta a responder em texto.

**3. Cálculo de causa** — *estima honorários + custas*
- Você: `Quanto fica de honorários uma causa trabalhista de 50 mil?`
- Esperado: a Léa acolhe **e** chega a *Estimativa de Custos* (contratuais + sucumbência CPC art. 85 + custas).

**4. Análise de PDF** — *lê processo/contrato (⭐)*
- Você: manda um **PDF** (contrato ou petição).
- Esperado: resumo com partes, prazos, valores e pontos de atenção.

**5. Parecer de perícia** — *analisa laudo pericial*
- Você: `Pode analisar tecnicamente esse laudo pericial contábil? Apurou horas extras de R$ 12.000 sem registro de ponto.`
- Esperado: análise técnica (metodologia, pontos-chave, **fragilidades**, quesitos sugeridos).

**6. Agendamento** — *marca consulta com o advogado certo*
- Você: `Consigo falar com um advogado dessa área?`
- Esperado: Léa conduz ao agendamento (nome, horário, presencial/online).

**7. NFS-e de honorários** — *emite a nota (simulada na demo)*
- Você: `Preciso emitir a nota fiscal de honorários de R$ 3.500`
- Esperado: espelho da *NFS-e* (número, ISS 5%, valor líquido, código).

**8. Escalação humana** — *sabe a hora de passar pra pessoa*
- Você: `Na verdade é urgente, a audiência é amanhã de manhã`
- Esperado: Léa reconhece a urgência e escala à equipe com elegância.

**+ Lembrete (roda sozinho)** — *Cron D-1 / prazo D-3*
- A aba `Agendamentos_Advocacia` tem 2 exemplos (consulta 03/07, prazo 05/07). O Cron dispara nas horas cheias (9h–18h) e manda o lembrete pro número cadastrado.

---

## Observações
- **NFS-e é simulada** (Ferraz & Nogueira é fictício, sem CNPJ/certificado A1). Em cliente real, plugar gateway (Focus NFe/eNotas) + certificado do cliente.
- **Cálculo/perícia** são estimativa/análise informativas — não substituem o advogado (disclaimer já vai na mensagem).
- Voz: cota grátis do ElevenLabs (~10k chars/mês) — para gravar a demo, ok; para deixar ligado em volume, avaliar plano pago ao fechar cliente.
