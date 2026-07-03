# 🎬 Cenário de Demo — Advocacia (Trabalhista) — Conversa Ponta a Ponta

Diferente do `roteiro_demo_advocacia.md` (que é um **menu** de funções soltas), este é uma **história única
encadeada** — um cliente do início ao fim, passando naturalmente por todas as capacidades. Ideal para gravar
o vídeo-demo "de ponta a ponta".

**Persona:** José Antônio Ferreira, operador de máquinas, demitido sem justa causa pela Metalúrgica Horizonte.
Chega inseguro, sem saber seus direitos. (Mesmo nome/empresa do PDF `docs_teste/03_reclamacao_trabalhista.pdf`,
então a análise casa com o documento.)

---

## ⚙️ Setup antes de gravar
1. Do número **teste** (`5519971266736`, sem bot) → mandar `/advocacia` pro chip `clinica01` (`5519971514971`).
   Aparece "✅ Chavinha trocada! Ferraz & Nogueira Advogados ⚖️".
2. Buffer está em **2,5s** — pode mandar mensagens picadas que ela agrupa.
3. Ter em mãos `12_Advocacia/docs_teste/03_reclamacao_trabalhista.pdf`.
4. Regra de ouro: número **sem bot** contra o chip (nunca bot-contra-bot).

> Legenda: 📱 = você (cliente) envia · 🤖 = resposta esperada da Léa · 🎬 = o que a demo prova · ⏱️ = nota técnica

---

## ATO 1 — Atendimento inicial (texto)

📱 **Você:** `Boa noite`
🤖 **Léa:** saudação acolhedora e elegante — apresenta-se como assistente do Ferraz & Nogueira e convida
a contar a situação. (Trata por "senhor".)

📱 **Você:** `vi que vocês trabalham com causas trabalhistas, é isso mesmo?`
🤖 **Léa:** confirma a atuação em **Direito Trabalhista** e menciona com naturalidade o **Dr. Eduardo Ferraz**
(sócio-fundador da área). Pergunta o que o traz até o escritório.

🎬 *Recepção humanizada + conhecimento das áreas do escritório.*

---

## ATO 2 — Dúvida e esclarecimento por ÁUDIO → resposta em ÁUDIO 🎙️

📱 **Você (ÁUDIO):** *grave um áudio dizendo, com suas palavras, algo como:*
> "Oi Léa, tudo bem? Olha, eu trabalhei quase seis anos numa metalúrgica aqui em Campinas e fui mandado
> embora sem justa causa mês passado. Fazia hora extra quase todo dia e nunca recebi direito, e acho que
> também tem coisa do FGTS que não caiu certo. Eu queria entender se vale a pena correr atrás disso."

🤖 **Léa (responde em ÁUDIO):** acolhe a situação, confirma que é da área **trabalhista**, explica
**sem dar parecer** que pontos como horas extras, adicional noturno, verbas rescisórias e FGTS costumam ser
avaliados numa consulta, e conduz para **agendar com o Dr. Eduardo Ferraz**.

🎬 *Transcrição de áudio (entende o cliente falando) + resposta falada com voz brasileira (Alice).*
⏱️ *A resposta sai em áudio porque a mensagem recebida foi áudio (nó "Resposta em Voz?" do workflow da Léa).*

---

## ATO 3 — Entrega de PDF + Análise 📄

📱 **Você:** `na verdade eu já tenho um documento que prepararam pra mim, posso mandar pra vocês darem uma olhada?`
🤖 **Léa:** com naturalidade, diz que pode receber e pede que envie.

📱 **Você:** *anexa* **`03_reclamacao_trabalhista.pdf`**
🤖 **Léa:** "🔍 Recebi seu documento! Analisando agora…" e em seguida a **análise estruturada**:
- **Tipo:** Reclamação Trabalhista
- **Partes:** José Antônio Ferreira (reclamante) × Metalúrgica Horizonte Ltda. (reclamada)
- **Datas/prazos:** admissão 10/02/2020 · dispensa 15/05/2026 · **audiência 18/08/2026**
- **Valores:** salário R$ 3.200 · danos morais R$ 10.000 · **valor da causa R$ 85.000**
- **Pontos de atenção:** horas extras, adicional noturno, FGTS + multa 40%, arts. 467/477 CLT
- **Resumo** + rodapé "análise informativa, não consultoria jurídica"

🎬 *O produto de leitura de PDF jurídico lendo um documento real e extraindo o que importa.*

---

## ATO 4 — Encaminhamento + Agendamento com horário 📅

📱 **Você:** `entendi! então quero marcar uma consulta com o Dr. Ferraz`
🤖 **Léa:** confirma o encaminhamento ao **Dr. Eduardo Ferraz** e pede: **nome completo, melhor horário e
preferência presencial ou online.**

📱 **Você:** `José Antônio Ferreira, pode ser quinta de manhã, presencial`
🤖 **Léa:** confirma a consulta (ex.: quinta às 9h, presencial, no endereço do Cambuí) e informa que a equipe
confirmará / o Dr. Ferraz entrará em contato, com elegância.

🎬 *Triagem que qualifica e agenda — coleta nome + horário + modalidade.*

---

## ATO 5 — Honorários (cálculo automático) 💰

📱 **Você:** `só uma dúvida, mais ou menos quanto fica de honorários numa causa de R$ 85.000?`
🤖 **Léa:** dispara a **ferramenta de cálculo** e devolve uma **estimativa** (faixa OAB-SP + sucumbência
10–20% + custas ~1%), deixando claro que o valor final é definido pelo advogado na consulta e que há a
possibilidade de honorários de êxito.

🎬 *Cálculo determinístico plugado na conversa.*
⏱️ *Gatilho: a frase precisa ter palavra de custo (quanto/valor/honorários) + um número (R$ 85.000).*

---

## ATO 6 — Confirmação + Lembrete D-1 🔔

📱 **Você:** `perfeito, obrigado Léa!`
🤖 **Léa:** encerra com cordialidade e se coloca à disposição 24h.

⏰ **No dia anterior à consulta (automático):** o workflow de lembrete (`DEMO-03-lembrete-advocacia`, cron)
lê a aba `Agendamentos_Advocacia` e envia sozinho:
> "Olá, Sr. José! Passando para lembrar da sua consulta com o Dr. Eduardo Ferraz **amanhã às 9h**, presencial,
> na Av. José de Souza Campos, 900 — 7º andar, Cambuí. Podemos confirmar sua presença?"

🎬 *Pós-atendimento ativo — o escritório não depende do cliente lembrar.*
⏱️ *Para gravar na hora: deixar uma linha na aba `Agendamentos_Advocacia` com a consulta marcada para "amanhã"
e rodar o workflow de lembrete manualmente (ou aguardar o cron). Me avisa que eu preparo a linha.*

---

## 🧩 Extra opcional — NFS-e de honorários
📱 **Você:** `depois da consulta vocês emitem nota fiscal dos honorários?`
🤖 **Léa:** confirma e, se citar um valor (ex. "emitir nota de R$ 3.000"), dispara a **NFS-e simulada**
(número + ISS 5%). *Fecha mostrando o ciclo administrativo completo.*

---

## ✅ O que este cenário cobre
Atendimento 24h · entende **áudio** e responde em **áudio** · **lê e analisa PDF** jurídico · conhece áreas e
**encaminha** ao advogado certo · **agenda** (nome+horário+modalidade) · estima **honorários** · **lembrete** D-1 ·
(opcional) **NFS-e**.

> Clonar para outra área: trocar trabalhista por **divórcio** (Dra. Marina Nogueira, `01_peticao_divorcio.pdf`)
> ou **alimentos** (`02_acao_alimentos.pdf`). A estrutura dos 6 atos é a mesma.
