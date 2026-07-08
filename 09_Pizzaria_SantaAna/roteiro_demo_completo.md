# Roteiro de Demo — Pizzaria Bella Massa (Ana, atendente virtual Kronos)

Guia para **gravar a tela** do WhatsApp da Kronos (5519971266736) conversando com o bot (clinica01 = 5519971514971).
Você digita as falas do **CLIENTE**. O bot responde sozinho. As linhas `→ [bot]` são só o que esperar (não digite).

> **Bella Massa** é uma pizzaria fictícia — protótipo genérico para demonstrar o fluxo a qualquer cliente, sem expor o nome de nenhuma pizzaria real.

**Antes de gravar:**
1. Confirmar que o bot está no ar e em modo Ana (`demo status` deve mostrar `whatsapp-santaana-demo`).
2. Limpar a sessão/linha de teste se quiser começar do zero.
3. Gravação de tela ligada → começar.

---

## 🍕 Fluxo da demo — Bella Massa

### Parte 1 — Pedido completo
1. **Cliente:** `Oi, boa noite!`
   → [bot] cumprimenta como Ana da Bella Massa e pergunta: Pizza, Esfirra ou Calzone?
2. **Cliente:** `Pizza`
   → [bot] pergunta: Grande ou Média?
3. **Cliente:** `Grande`
   → [bot] pergunta: com borda ou sem borda?
4. **Cliente:** `Com borda`
   → [bot] lista bordas (informa que a de **requeijão é grátis** ⭐)
5. **Cliente:** `Requeijão`
   → [bot] pergunta a categoria/sabor desejado
6. **Cliente:** `Quero de calabresa`
   → [bot] mostra opções de calabresa com ingredientes e preço
7. **Cliente:** `Calabresa Especial`
   → [bot] confirma o item e pergunta se deseja adicionar mais alguma pizza
8. **Cliente:** `Não, só essa`
   → [bot] pergunta se deseja algo para beber
9. **Cliente:** `Uma Coca 2 litros`
   → [bot] registra a bebida e pergunta: retirar no local ou entrega?
10. **Cliente:** `Entrega`
    → [bot] pede o endereço
11. **Cliente:** `Rua das Flores, 123, centro`
    → [bot] pergunta a forma de pagamento
12. **Cliente:** `Pix`
    → [bot] **confirma o pedido completo + total + tempo 30-45 min + despedida cordial** ✅

> 🎬 *Aqui termina o pedido. Mostre na tela o resumo com o total. Esse é o "momento uau" do fluxo guiado.*

### Parte 2 — Reclamação + solução (fechamento da demo)
13. **Cliente:** `A pizza chegou fria e demorou mais de uma hora, fiquei bem insatisfeito`
    → [bot] **acolhe com empatia** (lamenta, garante cuidado) e **encaminha a um responsável**
    → [bastidores] dispara alerta pra equipe + **registra a reclamação na tabela**

> 🎬 *Narre: "Repara que ele não ignora o cliente irritado — acolhe na hora E avisa a equipe pra assumir, além de guardar o registro pro dono."*

14. (opcional, mostrar a "solução" humana) **Cliente:** `Obrigado, fico no aguardo`
    → [bot] reforça que a equipe já foi avisada e vai resolver

> 🎬 *Fim da demo. Fecha mostrando: pediu sozinho, foi atendido com educação, e até a reclamação virou acolhimento + registro.*

---

## 🔁 Variação opcional (segundo take)
Pra um segundo vídeo sem repetir igual, troque só os itens — o fluxo é o mesmo:
- Pizza **sem borda** → vai direto pro sabor
- Sabor **Frango com Catupiry** + adicionar uma **Portuguesa**
- Bebida **Guaraná 2 litros**
- **Retirar no local** (sem taxa) → pagamento no **Cartão**
- Reclamação: `Pedi semana passada e veio o sabor errado, ninguém resolveu`

---

## Dicas de gravação
- Vá **devagar** entre as mensagens (dá tempo do bot responder e fica natural no vídeo).
- Pode cortar na edição os tempinhos de espera.
- Grave na vertical (formato de celular) — fica melhor pra mandar no WhatsApp do dono.
- No fim, uma tela com seu logo Kronos + contato fecha com chave de ouro.

## Depois de gravar
- Pedir ao Claude: voltar o chip pra **Aurora** (`demo aurora`).
- Limpar a tabela de reclamações de teste se quiser.
