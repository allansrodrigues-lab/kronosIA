# FASE A — a primeira compra (≈ R$ 150)

**Objetivo:** ter, na mesa, um servo girando e um sensor medindo distância, comandados pelo ESP32.
Nada de estrutura ainda. Isso é a bancada — o "cérebro e um músculo".

---

## O que comprar

| Item | Qtd | ≈ Preço | Como procurar (copie e cole na busca) |
|---|---|---|---|
| **ESP32 DevKit V1** (38 pinos) | 1 | R$ 35 | `ESP32 DevKit V1 38 pinos WiFi Bluetooth` |
| **PCA9685** driver de servo I2C | 1 | R$ 25 | `PCA9685 16 canais servo driver PWM I2C` |
| **Servo MG996R** (engrenagem metálica) | 1 | R$ 35 | `Servo MG996R 15kg metal digital` |
| **Sensor ultrassônico HC-SR04** | 1 | R$ 12 | `sensor ultrassonico HC-SR04` |
| **Protoboard 830 furos + kit jumpers** | 1 | R$ 35 | `protoboard 830 furos kit jumper macho femea` |
| **Resistores 1kΩ e 2,2kΩ** | 10 | R$ 5 | `kit resistores 1/4W sortido` |
| **Cabo USB** (dado, não só carga) | 1 | R$ 10 | `cabo micro USB dados` — ou use um que já tem |
| | | **≈ R$ 147** | |

### Onde comprar

- **Lojas de eletrônica BR** (chegam em dias, dão nota, têm suporte): Eletrogate, Curto Circuito, Baú da Eletrônica, RoboCore.
- **Mercado Livre**: mais rápido, preço parecido. Filtre por vendedor com reputação verde e muitas vendas.
- **AliExpress**: metade do preço, mas 20-40 dias. Só vale para o que você **não** vai usar agora.

💡 **Compre tudo do mesmo vendedor.** O frete costuma custar mais que uma peça.
💡 **Procure "kit iniciante ESP32"** antes de fechar — às vezes o kit com protoboard, jumpers e sensores sai mais barato que os itens avulsos.

### ⚠️ Cuidados na hora de comprar

- **ESP32 de 38 pinos**, não o de 30 — o de 38 tem os pinos de ADC que os potenciômetros vão usar depois.
- **MG996R tem que ser de engrenagem METÁLICA.** Se o anúncio não diz "metal gear" ou "engrenagem metálica", provavelmente é falsificado com plástico dentro.
- **Cabo USB de DADOS.** Cabo só de carregar não transfere programa, e você vai passar horas achando que o ESP32 veio quebrado. É o erro mais comum de todos.

---

## Enquanto as peças não chegam (custo zero)

Não fique parado esperando. Dá pra montar o circuito e escrever o código **no navegador**, num simulador gratuito de ESP32:

- Acesse **wokwi.com** (não precisa instalar nada, nem criar conta pra começar)
- Escolha "ESP32" → adicione um servo e um HC-SR04
- Você monta os fios arrastando e escreve o código na mesma tela

Quando as peças chegarem, você não vai estar aprendendo do zero — vai estar **repetindo no físico o que já funcionou na tela**. É o mesmo princípio do MK1 servir de gabarito pro MK2.

*(A Aula 2 do `Guia_Sistema_Eletronica.md` é exatamente esse passo a passo.)*

---

## Quando chegar: a ordem de montagem

Faça nesta ordem, testando cada etapa. **Não pule pro próximo item se o anterior não passou.**

| # | Passo | Teste que libera o próximo |
|---|---|---|
| 1 | Instalar Arduino IDE + suporte ao ESP32 | Rodar o "Blink": o LED da placa pisca |
| 2 | Ligar o HC-SR04 (com divisor de resistor no ECHO) | O Monitor Serial mostra a distância; aproxime a mão e o número cai |
| 3 | Ligar o PCA9685 no ESP32 (I2C: pinos 21 e 22) | Um scanner I2C encontra o endereço `0x40` |
| 4 | Ligar o servo no canal 0 do PCA9685 | O servo varre de 0° a 180° suavemente, sem tremer |
| 5 | Juntar os dois: sensor + servo | Aproxime a mão → o servo se move. **Esse é o primeiro reflexo do robô.** |

### ⚠️ A regra que vale mais que tudo nesta fase

**Alimente o servo pelo borne V+ do PCA9685, nunca pelo pino 5V do ESP32.**

Um MG996R puxa mais de 1 ampere quando força; o pino do ESP32 entrega uns 0,5. Ligando direto, ou o ESP32 reseta sozinho (e você vai caçar um bug que não existe no código), ou queima. Na bancada, use uma fonte 5 V separada ou um carregador de celular cortado — a fonte ATX só entra na Fase D.

---

## O que você vai saber fazer ao fim da Fase A

- Gravar programa no ESP32
- Ler um sensor e ver o dado em tempo real
- Comandar um servo com precisão de ângulo
- Entender por que sinal e força andam separados

Isso já é, literalmente, um robô de 1 grau de liberdade com um sentido. O resto do Ferrão é repetir isso mais vezes, com peças maiores.

---

**Custo total até aqui: R$ 147. Próxima compra só depois que o passo 5 funcionar.**
