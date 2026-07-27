# PADRÃO ESTRUTURAL FERRÃO — kit replicável

**v1.0 · 26/07/2026**
Documento de referência: qualquer Ferrão futuro sai destas medidas.

---

## O princípio: esqueleto padrão, casca variável

Se o robô vai existir em vários nichos, tem uma coisa que **não pode** ser padronizada: a mala. Mala usada varia de tamanho, modelo sai de linha, e cada unidade vai ser uma diferente.

A solução é a mesma da indústria automotiva: **o chassi é padrão, a carroceria muda.**

| Padronizado (sempre igual) | Variável (adapta por unidade) |
|---|---|
| Comprimento dos braços | Tamanho e cor da mala |
| Furação das peças de alumínio | Posição dos furos na casca |
| Suporte do motor (quadro interno) | Modelo da necessaire |
| Distância entre ombros | Altura da coluna da cadeira |
| Toda a eletrônica e o código | — |

**O que isso significa na prática:** você corta e fura o alumínio uma vez, do mesmo jeito, sempre. A mala é a única peça que exige medir de novo a cada robô.

---

## 1. Tubo quadrado ou perfil? — a decisão

Você perguntou "cubo quadrado ou encomendar". São três caminhos:

| Opção | Custo (2 braços) | Prós | Contras |
|---|---|---|---|
| **A · Tubo quadrado de alumínio** (comprar barra e cortar) | ~R$ 75-90 | Barato, acha em qualquer serralheria, leve, rígido | Você corta e fura tudo |
| **B · Barra cortada sob medida** (encomendar na serralheria) | ~R$ 110-140 | Corte reto e no esquadro, sem esforço | Só compensa a partir do 2º ou 3º robô |
| **C · Perfil estrutural V-slot 20×20** (tipo impressora 3D) | ~R$ 160-200 | Rasgo em toda a extensão: fixa em qualquer ponto **sem furar**, ajusta depois | Mais caro, precisa comprar porcas-T e cantoneiras |

### Recomendação

**Unidade 1 (protótipo): opção A.** Compre a barra e corte você mesmo. Motivo prático — no primeiro robô você ainda vai errar medida, e errar num pedaço de barra é barato. Encomendar corte antes de saber a medida final é pagar pra errar com precisão.

**A partir da unidade 2: opção B.** Aí as medidas já estão validadas por este documento, e você entrega a lista de corte pronta na serralheria. Sai cortado no esquadro, sem serra, sem lima.

**Opção C, sinceramente:** o V-slot é lindo e ajustável, mas o preço dobra e o ganho real é poder mudar a posição do servo depois — coisa que você faz uma vez. Não vale agora. Reconsidere se um dia for montar meia dúzia.

---

## 2. Lista de corte padrão (cut list)

> Esta é a lista que você entrega na serralheria a partir da unidade 2.

### Alumínio — tubo quadrado, parede 1,5 a 2 mm

| Cód | Peça | Perfil | Comprimento | Qtd |
|---|---|---|---|---|
| **A1** | Braço (úmero) | 25 × 25 mm | **280 mm** | 2 |
| **A2** | Antebraço | 20 × 20 mm | **240 mm** | 2 |
| **A3** | Suporte do pescoço | 20 × 20 mm | **90 mm** | 1 |

**Barras necessárias:** 1 barra de 1 m de 25×25 (sobra 440 mm) + 1 barra de 1 m de 20×20 (sobra 670 mm).
A sobra não é desperdício: vira gabarito de teste e suporte extra.

### Madeira — do caixote, 15 mm de espessura

| Cód | Peça | Medida | Qtd | Função |
|---|---|---|---|---|
| **M1** | Reforço do ombro | 200 × 160 mm | 2 | O "osso" atrás da casca — segura o motor |
| **M2** | Base do torso | 260 × 200 mm | 1 | Fundo da mala, apoia a fonte |
| **M3** | Bandeja da eletrônica | 200 × 140 mm | 1 | Placas parafusadas |
| **M4** | Flange da coluna | Ø 240 mm ou 240 × 240 mm | 1 | Une a mala à coluna da cadeira |
| **M5** | Bucha interna do tubo | 22 × 22 × 40 mm | 4 | Enfia na ponta do alumínio, impede amassar |

⚠️ **M1 tem que sobrar pelo menos 50 mm para cada lado do motor.** É essa sobra que distribui a força e impede a casca de rasgar.

---

## 3. Furação padrão das peças de alumínio

> Estas medidas são **fixas**. Uma vez marcadas, valem para todos os robôs.

### A1 — Braço (úmero), 25 × 25 × 280 mm

```
   ponta do OMBRO                                    ponta do COTOVELO
        ├── 20 ──┤                                   ├──── 60 ────┤
   ┌────●────────●───────────────────────────────────▭▭▭▭▭▭▭▭▭────┐
   │    ↑        ↑                                   janela do servo │
   │  Ø5,2     Ø5,2                                                 │
   └────────────────────────────────────────────────────────────────┘
   0   20      50                                  220          280
```

| Furo | Posição (do topo) | Ø | Para quê |
|---|---|---|---|
| F1 | 20 mm | 5,2 mm | Parafuso M5 que prende no clamp do motor |
| F2 | 50 mm | 5,2 mm | Segundo M5 — **dois parafusos, senão gira em falso** |
| F3 | janela 220 a 280 mm | recorte 40 × 20 mm | Encaixe do corpo do servo do cotovelo |
| F4 | 4 furos ao redor da janela | 3,2 mm | Orelhas do servo (M3 passante) |

### A2 — Antebraço, 20 × 20 × 240 mm

| Furo | Posição | Ø | Para quê |
|---|---|---|---|
| F5 | 15 mm da ponta do cotovelo | 3,2 mm ×2 | Cantoneira que recebe o horn do servo |
| F6 | 20 mm da ponta da mão | 3,2 mm ×2 | Base da garra |
| F7 | 60 mm da ponta da mão | 3,2 mm ×2 | Servo da garra (fica recuado, para tirar peso da ponta) |

### A3 — Suporte do pescoço, 20 × 20 × 90 mm

| Furo | Posição | Ø | Para quê |
|---|---|---|---|
| F8 | 12 mm de cada extremidade | 3,2 mm ×4 | Servo de pan embaixo, plataforma da cabeça em cima |

### Por que 5,2 mm para parafuso M5 e 3,2 mm para M3

Furo de passagem é sempre **0,2 mm maior** que o parafuso. Furo justo obriga a forçar a peça no lugar, e aí o alinhamento vai embora. Folga de 0,2 mm deixa assentar sozinho.

---

## 4. As duas regras que não mudam nunca

### ⚠️ Regra 1 — parafuso sempre passante, nunca roscado no alumínio
A parede tem 1,5 mm. Rosca feita nela espana no terceiro aperto. **Sempre atravesse e feche com porca nylock do outro lado.**

### ⚠️ Regra 2 — bucha de madeira (M5) nas pontas de aperto forte
Aperte um parafuso num tubo oco e ele **amassa**: a seção quadrada vira retângulo e a junta afrouxa pra sempre. Um taquinho de 22 × 22 × 40 mm enfiado na ponta resolve — o tubo aperta contra a madeira, não contra o vazio.

Use nas duas pontas do A1 (ombro e cotovelo). No A2 e A3 o esforço é baixo, não precisa.

---

## 4b. PADRÃO ELETRÔNICO — componente único e pinagem travada

> Se o robô vai existir em várias unidades, o componente precisa ter **modelo, controlador e pinagem fixos**. Trocar de modelo entre unidades significa reescrever código e refazer fiação.

### O display do rosto — especificação fechada

| Campo | Valor obrigatório |
|---|---|
| **Tamanho** | 2,4 polegadas |
| **Controlador** | **ILI9341** ← o que realmente importa |
| **Resolução** | 240 × 320 |
| **Interface** | SPI |
| **Tensão lógica** | 3,3 V (compatível direto com ESP32) |
| **Touch** | **sem** — não é preciso no rosto e economiza 2 pinos |
| **Placa** | ~42 × 60 mm · área visível ~37 × 49 mm |
| **Biblioteca** | `TFT_eSPI` (suporte nativo ao ILI9341) |

**Como buscar:** `display TFT 2.4 SPI ILI9341 240x320 arduino`
**Preço de referência:** R$ 45 a 70

⚠️ **O que NÃO comprar, mesmo parecendo igual:**

| Evite | Por quê |
|---|---|
| Controlador **ST7789**, **ILI9488**, **HX8357** | Outro driver = outro código. Parecem iguais na foto |
| Versão **paralela de 8 bits** | Come 13 pinos do ESP32 em vez de 5 |
| Versão de **5 V sem regulador** | Queima a lógica do ESP32 |
| Modelos **com touch** | Custa mais e ocupa pinos à toa neste uso |

**Por que ILI9341 e não outro:** é o controlador mais difundido do mundo em TFT 2,4". Isso significa biblioteca madura, milhares de exemplos prontos e reposição fácil em qualquer loja — que é exatamente o que um padrão precisa ter.

### Mapa de pinos do ESP32 — **travado**

> Esta tabela é a fonte da verdade da fiação. Toda unidade é ligada assim.

| GPIO | Ligado a | Sistema |
|---|---|---|
| **21** | SDA | I2C — PCA9685 (servos) |
| **22** | SCL | I2C — PCA9685 |
| **23** | MOSI / SDI | SPI — display |
| **18** | SCK | SPI — display |
| **19** | MISO | SPI — reservado |
| **5** | CS | Display |
| **16** | DC / RS | Display |
| **17** | RST | Display |
| **4** | LED / backlight | Display (PWM = controla o brilho) |
| **25** | RPWM | Driver BTS7960 — ombro esquerdo |
| **26** | LPWM | Driver BTS7960 — ombro esquerdo |
| **27** | RPWM | Driver BTS7960 — ombro direito |
| **14** | LPWM | Driver BTS7960 — ombro direito |
| **33** | TRIG (os dois juntos) | Ultrassônicos |
| **32** | ECHO esquerdo *(via divisor 1k/2k2)* | Ultrassônico |
| **35** | ECHO direito *(via divisor)* | Ultrassônico — **só entrada** |
| **34** | Potenciômetro ombro esquerdo | ADC — **só entrada** |
| **39** | Potenciômetro ombro direito | ADC — **só entrada** |
| **13** | Microswitches (fins de curso) | INPUT_PULLUP |
| **15** | Serial do DFPlayer / impressora | Áudio e cupom |
| **2** | LED da placa | Status |

**Livres para expansão:** GPIO 12 e 0 (cuidado: o 0 é usado na gravação).

⚠️ **Três armadilhas de pinagem do ESP32**, e é por isso que esta tabela existe:

1. **GPIO 34, 35, 36 e 39 são SÓ ENTRADA.** Não conseguem acionar nada — por isso ficaram com potenciômetro e ECHO, que só leem.
2. **Os pinos do ADC2 (0, 2, 4, 12-15, 25-27) não funcionam como analógicos com o Wi-Fi ligado.** Como o robô vive conectado, toda leitura analógica tem que estar no ADC1 (32-39). É a razão de os potenciômetros estarem no 34 e 39.
3. **I2C e SPI não se atrapalham** — são barramentos separados. Display e servos podem funcionar ao mesmo tempo sem disputa.

### Ficha de conferência do display

```
☐ O anúncio diz ILI9341? (não ST7789, não ILI9488)
☐ É SPI, não paralelo de 8 bits?
☐ Aceita 3,3 V na lógica?
☐ É 2,4" com 240×320?
☐ Vem com os pinos soldados ou tem que soldar?
```

---

## 5. Medidas de conjunto (o que define a silhueta)

| Medida | Valor | Por que esse valor |
|---|---|---|
| Distância entre ombros | **340 mm** | Proporção humana e cabe na largura de uma mala de bordo |
| Altura do ombro ao chão | **~1.050 mm** | Altura de olhar de quem está em pé, sem intimidar |
| Alcance do braço (ombro à garra) | **520 mm** | A1 + A2 + juntas |
| Arco de trabalho do ombro | **120°** | Limitado por software e microswitch |
| Peso máximo na mão | **250 g** | Limite do MG996R no cotovelo |
| Altura total | **~1.350 mm** | Com a cabeça |

---

## 6. Ficha de adaptação por unidade

Quando montar um Ferrão novo, só estes campos mudam. Preencha antes de furar:

```
UNIDADE Nº ____   NICHO: ______________   DATA: ____/____/____

MALA
  Modelo/marca ............ ______________________
  Medidas (L × A × P) ..... _____ × _____ × _____ mm
  Material (ABS/PP) ....... ______  → PP exige primer especial
  Profundidade útil ....... _____ mm   (mínimo 200)

MOTOR DE LIMPADOR (medir com paquímetro!)
  Diâmetro do eixo ........ _____ mm
  Distância entre orelhas . _____ mm
  Ø da porca do eixo ...... _____ mm

CADEIRA
  Altura da coluna ........ _____ mm
  Furos do mecanismo ...... _____ (quantos e qual bitola)

CONFERÊNCIA
  ☐ Furo do eixo = Ø eixo + 5 mm de folga
  ☐ Reforço M1 sobra ≥ 50 mm de cada lado do motor
  ☐ Servo do cotovelo é 180°, não 360°
```

---

## 7. E se um dia virar produto

Se o Ferrão for replicado a sério, três coisas mudam — e vale saber desde já para não fechar portas:

1. **A mala vira compra fixa** — um modelo escolhido e comprado em quantidade, para toda unidade sair igual.
2. **Os reforços de madeira viram peça cortada** — entrega a lista M1-M5 na marcenaria e recebe tudo pronto.
3. **As peças de precisão viram impressão 3D** — berço de servo, suporte de potenciômetro e garra, em OpenSCAD paramétrico. Aí sim a impressão se paga, porque o custo de desenho é diluído por várias unidades.

Nesse cenário, o tempo de montagem cai de semanas para dias — e é isso que separa "um robô" de "um produto".

---

*Este documento é a fonte da verdade das medidas. Se algo mudar na bancada, corrija aqui primeiro.*
