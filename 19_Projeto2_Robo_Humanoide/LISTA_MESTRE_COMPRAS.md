# LISTA MESTRE DE COMPRAS — Ferrão (tudo novo)

**Atualizada em 25/07/2026.**
✅ = preço **confirmado** hoje na Curto Circuito · ~ = **estimativa** minha, confira antes de fechar

Ordem de compra por fase. **Só compre a fase seguinte depois que a anterior passou no teste.**

---

## FASE A — Bancada (o cérebro e um músculo) · ≈ R$ 150

| Item | Qtd | Preço | Para quê |
|---|---|---|---|
| ESP32 DevKit V1 (38 pinos) | 1 | ~R$ 35 | O cérebro |
| PCA9685 (driver de servo I2C) | 1 | ~R$ 25 | A "torneira" dos servos |
| ✅ Servo MG996R | 1 | **R$ 37,80** | O primeiro músculo (vira o pescoço depois) |
| HC-SR04 (ultrassônico) | 1 | ~R$ 12 | O primeiro sentido |
| Protoboard 830 + kit jumpers | 1 | ~R$ 35 | Bancada de teste |
| Kit resistores (1k e 2k2) | 1 | ~R$ 5 | Divisor de tensão do sensor |

**Teste que libera a Fase B:** você aproxima a mão do sensor e o servo se move.

---

## FASE B — Cabeça · ≈ R$ 130

| Item | Qtd | Preço | Para quê |
|---|---|---|---|
| ✅ Servo MG996R | 1 | **R$ 37,80** | Giro do pescoço (pan) |
| ✅ Servo MG90S | 2 | **R$ 23,90** cada | Inclinação da cabeça + reserva |
| HC-SR04 | 1 | ~R$ 12 | Segundo "olho" |
| Anel de LED WS2812 (12 ou 16 LEDs) | 2 | ~R$ 18 cada | **Os olhos** — o item de maior impacto visual |
| Kit parafusos M3 + porca nylock | 1 | ~R$ 20 | Fixar servos e sensores |

**Teste:** a cabeça vira sozinha para o lado de quem se aproxima, com os olhos acesos.

---

## FASE C — Estrutura · ≈ R$ 200

| Item | Qtd | Preço | Para quê |
|---|---|---|---|
| **Mala rígida** | 1 | ~R$ 40-200 | Torso. Usada em bazar/OLX: R$ 30-80. Nova: R$ 200 |
| **Necessaire rígida** | 1 | ~R$ 30 | Cabeça (de preferência da mesma linha) |
| Tubo quadrado alumínio 25×25 mm | 1 m | ~R$ 40 | Braços |
| Tubo quadrado alumínio 20×20 mm | 1 m | ~R$ 35 | Antebraços |
| Kit parafusos M4/M5/M6 + nylock + arruelas | 1 | ~R$ 45 | Todas as junções |
| Cantoneiras + fita perfurada | — | ~R$ 25 | Suportes |
| Serra-copo Ø 30 mm | 1 | ~R$ 25 | O furo do eixo na mala |

*(A cadeira e o caixote você já tem.)*

**Teste:** empurrão firme no topo — não tomba, não balança mais que 2-3 cm.

---

## FASE D — Ombro, a etapa mais importante · ≈ R$ 400-600

| Item | Qtd | Preço | Para quê |
|---|---|---|---|
| **Motor de limpador de para-brisa 12 V** | 2 | ~R$ 150-250 cada (novo) | Atuador do ombro |
| Driver BTS7960 (IBT-2) | 2 | ~R$ 40 cada | A "torneira" dos motores |
| Potenciômetro 10 kΩ linear | 4 | ~R$ 5 cada | Diz ao ESP32 o ângulo real do braço |
| Microswitch (fim de curso) | 4 | ~R$ 3 cada | Limite físico de segurança |
| Fonte 12 V 10 A (ou fonte ATX) | 1 | ~R$ 120 (nova) / R$ 0 (sucata de PC) | Energia |
| Fusível 10 A + 5 A com porta-fusível | 2+2 | ~R$ 12 | **Não é opcional** |
| Chave gangorra (botão de emergência) | 1 | ~R$ 10 | Corta os 12 V num tapa |
| Fio flexível 1,5 mm² (verm/preto) | 5 m | ~R$ 20 | Linha de força |
| Capacitores 1000 µF + 100 nF | kit | ~R$ 10 | Anti-ruído (evita reset fantasma) |

**Teste:** você comanda "vá para 45°" e o braço vai e **para** a ±5°.

---

## FASE E–H — Braços, garra e acabamento · ≈ R$ 250

| Item | Qtd | Preço | Para quê |
|---|---|---|---|
| ✅ Servo MG996R | 2 | **R$ 37,80** cada | Os dois cotovelos |
| ✅ Servo MG90S | 2 | **R$ 23,90** cada | Garra e punho |
| Barra roscada M8 + porcas | 1 m | ~R$ 15 | Eixos das juntas |
| Rolamento 608 | 4 | ~R$ 8 cada | Mancais (ou tire de skate velho) |
| Cabo de freio de bike + elásticos | — | ~R$ 20 | Tendão da garra |
| Primer spray + tinta preta fosca | 2+3 | ~R$ 90 | Acabamento |
| Lixa 180/220 | — | ~R$ 15 | Preparo da pintura |

---

## FASE I — Voz, visão e impressora (o que dá "vida") · ≈ R$ 280

| Item | Qtd | Preço | Para quê |
|---|---|---|---|
| DFPlayer Mini + cartão microSD | 1 | ~R$ 35 | O robô **fala** frases prontas |
| Alto-falante 3 W | 2 | ~R$ 20 | Voz e som |
| Microfone INMP441 (I2S) | 1 | ~R$ 20 | O robô **ouve** |
| ESP32-CAM | 1 | ~R$ 45 | O robô **vê** e segue rosto |
| Fita LED endereçável (1 m) | 1 | ~R$ 25 | Luz do torso |
| **Impressora térmica 58 mm** (serial) | 1 | ~R$ 150 | Cupom com QR do WhatsApp |
| Bobina papel térmico 58 mm | 5 | ~R$ 15 | Consumível (sem tinta) |

---

## SEGURANÇA — compre junto com a Fase A, não depois

| Item | Preço | Por quê |
|---|---|---|
| Óculos de proteção | ~R$ 15 | Dremel joga caco de disco. Item mais barato e o único insubstituível. |
| Luva de raspa | ~R$ 15 | Peça de metal cortado tem aresta viva |
| Jogo de brocas p/ metal (3-8 mm) | ~R$ 30 | Furo-guia certo evita rachar tudo |

---

## Total

| Fase | Valor |
|---|---|
| A · Bancada | R$ 150 |
| B · Cabeça | R$ 130 |
| C · Estrutura | R$ 200 |
| D · Ombro | R$ 400-600 |
| E-H · Braços e acabamento | R$ 250 |
| I · Voz, visão, impressora | R$ 280 |
| Segurança | R$ 60 |
| **TOTAL (tudo novo)** | **≈ R$ 1.470 a 1.670** |

**Diluído em 6 compras ao longo de ~4 meses = R$ 250-400/mês.**

---

## ⚠️ A decisão que economiza R$ 400 sem perder nada

A Fase D é quase metade do orçamento, e o culpado é o **motor de limpador novo** (R$ 150-250 cada).

**Essa é a única peça do projeto onde comprar usado não tem desvantagem nenhuma.** É um motor escovado com redução por engrenagem — construção simples, feita pra durar 15 anos exposta a chuva e calor debaixo do capô. Um motor de ferro-velho com 5 anos de uso é funcionalmente idêntico a um novo, e custa R$ 0 a R$ 60.

- Comprando os dois **novos**: R$ 300-500
- Pegando os dois no **ferro-velho**: R$ 0-120
- **Diferença: até R$ 400** — o que paga as Fases A e B inteiras

A regra vale pro resto: **peça burra e robusta (motor, fonte, mala), usado serve. Peça inteligente e frágil (eletrônica), compre nova** — eletrônica de sucata dá bug fantasma que custa semanas de debug.

Mesma lógica na fonte: ATX de PC velho é grátis e melhor que fonte nova de R$ 120.

---

## Onde comprar

| Loja | Bom para | Prazo |
|---|---|---|
| **Curto Circuito** | Servos e módulos — preços confirmados aqui | Dias |
| **Eletrogate / Baú da Eletrônica / RoboCore** | Eletrônica em geral, com nota | Dias |
| **Mercado Livre** | Motor de limpador, mala, alumínio | Rápido |
| **AliExpress** | Só o que não é urgente (metade do preço) | 20-40 dias |
| **Ferro-velho / OLX / bazar** | Motor, fonte ATX, mala, rolamento | Agora |

💡 Junte tudo da mesma fase num pedido só — frete costuma custar mais que uma peça.
