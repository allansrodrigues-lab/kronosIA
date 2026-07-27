# FERRÃO — Guia de compra completo

**26/07/2026** · Leia aos poucos. Cada bloco é independente.

---

## O que mudou no projeto (decisões de 25-26/07)

O robô não é mais o de PVC e madeira aparente. Três trocas:

| Era | Virou | Por quê |
|---|---|---|
| Braços de **cano PVC** | **Tubo quadrado de alumínio** | A face plana deixa o servo do cotovelo assentar reto — no cano redondo ele balança. E cano pintado continua parecendo cano. |
| Torso de **MDF aparente** | **Mala rígida** | Casca pronta e bonita, que abre pelo zíper (painel de manutenção) e guarda a eletrônica dentro. Pula a etapa de "encapar". |
| Crânio de **pote plástico** | **Necessaire rígida** | Leve, abre para dar acesso aos sensores, e casa a textura com a mala. |

⚠️ **A madeira continua no projeto — mas por dentro.** O caixote deixou de ser carcaça e virou o **reforço estrutural** que segura os motores dos ombros por trás da casca da mala. Sem ele, o parafuso rasga o plástico. A mala é a pele; a madeira é o osso.

E o **PVC que você já tem** não foi jogado fora: serve de gabarito para testar cortes e furos antes de estragar o alumínio.

---

## As três colunas

| ✅ JÁ TENHO | 🛒 COMPRAR | ♻️ GARIMPAR |
|---|---|---|
| 2 cadeiras de rodinha (base + coluna) | Eletrônica e sensores | 2 motores de limpador |
| Caixote de madeira → **reforço interno** | **Mala + necessaire** | Fonte ATX de PC |
| Cano PVC → **gabarito de teste** | **Tubo de alumínio** (braços) | Rolamentos, microswitches |
| Ferramentas básicas | Parafusos e serra-copo | Alto-falantes, cabo de bike |

**A base já está resolvida.** As "pernas" (cadeira) você tem duas — uma vira o robô, a outra é doadora de peças.

---

# BLOCO 1 — ELETRÔNICA (Fase A) · R$ 225

> Compre tudo junto, num carrinho só. É o que faz o robô se mexer pela primeira vez.

### 1.1 ESP32 DevKit V1 — **R$ 49,50**

🔗 https://lista.mercadolivre.com.br/esp32-devkit-v1-38-pinos

**Procure:** *"Placa Esp32d Esp32 32d Wroom Devkitc V4 38 Pinos Soldados"*
· +5 mil vendidos · 4.8 ⭐ · frete grátis · `MLB2048573048`

**Especificação que importa:**
| | |
|---|---|
| Pinos | **38** (não o de 30) |
| Chip | ESP32-WROOM-32 ou 32D |
| Wi-Fi | 2,4 GHz embutido |
| Lógica | 3,3 V ⚠️ |
| USB | Micro-USB ou USB-C, tanto faz |

**Por que 38 pinos:** o de 30 não expõe os pinos ADC (GPIO 34, 35, 36, 39) que vão ler os potenciômetros dos ombros na Fase D. Comprar o de 30 hoje = comprar outro depois.

**Por que ESP32 e não Arduino Uno:** Wi-Fi embutido. É ele que serve o painel de controle no navegador do celular sem comprar módulo extra.

---

### 1.2 PCA9685 — driver de servo — **R$ 39,00**

🔗 https://lista.mercadolivre.com.br/pca9685-16-canais-servo-driver-i2c

**Procure:** *"Módulo Driver Servo Motor 16 Canais Pca9685"*
· +100 vendidos · `MLB4615275322`

**Especificação:**
| | |
|---|---|
| Canais | 16 servos |
| Comunicação | I2C (2 fios: SDA + SCL) |
| Endereço padrão | 0x40 |
| Resolução | 12 bits |
| Alimentação dos servos | borne V+ separado ⚠️ |

**Para que serve:** é o "maestro" dos servos. O ESP32 manda uma ordem pela I2C e essa placa segura o sinal dos 6 servos sozinha, com energia própria. Sem ela: servo tremendo e ESP32 resetando.

⚠️ Alguns anúncios misturam com **LU9685**, que é outro chip. Confirme "PCA9685" na descrição.

---

### 1.3 Servo MG996R — **R$ 50** — ⚠️ LEIA ISTO

🔗 https://lista.mercadolivre.com.br/servo-motor-mg996r-metal-15kg

**Especificação:**
| | |
|---|---|
| Torque | 15 kg·cm a 6 V |
| Engrenagem | **metal** (obrigatório) |
| Tensão | 4,8 a 7,2 V |
| Corrente de pico | ~2,5 A ⚠️ |
| Ângulo | **180° — de posição** |

## ⚠️ O erro mais caro da lista

Existem **duas versões idênticas por fora**:

- **180°** = servo de **posição**. Você manda "vá para 45°" e ele vai. ✅ É o que precisamos.
- **360°** = **rotação contínua**. Gira sem parar, não sabe onde está. ❌ Não serve.

O MG996R de fábrica é 180°. As versões 360° são modificadas para carrinho de brinquedo — e no Mercado Livre **são maioria**. O nome "MG996R" sozinho não garante nada.

**Três formas de acertar:**

**A) Curto Circuito — ⭐ recomendado**
🔗 https://curtocircuito.com.br → buscar `MG996R`
Produto: *"Servo Motor - MG996R - Digital 180°"* — **R$ 45,00**
O ângulo está no nome do produto. Mais barato que o ML e zero risco.

**B) Mercado Livre com 180 no título**
*"Servo Motor Tower Pro Mg996 180 Graus"* — R$ 53 · `MLB3507456595`
Tower Pro é a fabricante original.

**C) Mercado Livre, o mais vendido — pergunte antes**
*"Servo Digital Mg996r 15kg Alto Torque Metal Para Arduino"* — R$ 50 · +5 mil vendidos · `MLB27412972`

Copie e mande ao vendedor:
> *"Boa tarde! Este servo é de posição 180 graus ou rotação contínua 360 graus?"*

**Teste no dia que chegar:** mande ir a 0° e a 180°. Se **parar** nas duas → certo. Se **girar sem parar** → é 360, peça devolução dentro do prazo.

---

### 1.4 Sensor ultrassônico HC-SR04 — **R$ 19 (ou 25 o par)**

🔗 https://lista.mercadolivre.com.br/sensor-ultrassonico-hc-sr04

**Procure:** *"Sensor Ultrassônico HC-SR04 com Módulo 5V da DIP MECATRÔNICA"*
· +5 mil vendidos · `MLB46876142`
**Melhor:** *"2x Sensor Ultrassonico De Distância Hc-sr04"* — R$ 25 · `MLB2043575349`

**Especificação:**
| | |
|---|---|
| Alcance | 2 cm a 4 m |
| Precisão | ±3 mm |
| Tensão | 5 V |
| Pinos | VCC, TRIG, ECHO, GND |

⚠️ **O pino ECHO devolve 5 V e o ESP32 é 3,3 V.** Precisa do divisor com resistor 1k + 2,2k — por isso o kit de resistores está na lista. Ligar direto queima a entrada da placa.

**Leve 2:** o segundo é usado na Fase B (cabeça), e sai mais barato agora que depois com outro frete.

---

### 1.5 Protoboard + jumpers + regulador — **R$ 37** ⭐

🔗 https://lista.mercadolivre.com.br/protoboard-830-furos-kit-jumper

**Procure:** *"Kit Protoboard 830 + Regulador Tensão + 65 Jumpers"*
· +5 mil vendidos · `MLB37233619`

**O que vem:**
- Protoboard 830 furos
- 65 jumpers
- **Módulo regulador MB102** ← o motivo de escolher este

**Por que é o melhor item da lista:** o regulador é a fonte 5 V separada que o servo precisa. Sem ele, o servo puxa corrente do ESP32, a placa reseta sozinha e você vai caçar um bug que não existe no código. R$ 6 a mais que o kit sem regulador, e resolve um problema inteiro.

---

### 1.6 Kit de resistores — **R$ 25**

🔗 https://lista.mercadolivre.com.br/kit-resistores-1-4w-sortido-valores

**Procure:** *"400 Resistores Valores Variados - 1/4w"* · +1000 vendidos · `MLB3126214008`

Precisa de **1 kΩ** e **2,2 kΩ** para o divisor de tensão do sensor. O kit tem 30 valores e serve o projeto inteiro.

---

### 1.7 Óculos de proteção — **~R$ 15** — loja física

Não compre online. Vá numa loja de material de construção ou agropecuária e **experimente**. Óculos que incomoda não é usado, e aí não protege nada. Peça: *"óculos de proteção incolor com CA"*.

Você vai usar no Dremel — caco de disco de corte voa, e olho não tem peça de reposição.

---

**SUBTOTAL BLOCO 1: R$ 225,50** (+ R$15 dos óculos)

---

# BLOCO 2 — A CARCAÇA (mala + necessaire)

> Esta é a peça de **design** do projeto. Vale escolher com calma.

Não consegui extrair os anúncios de mala do Mercado Livre (o site travou a leitura automática), então aqui vão **critérios objetivos** em vez de um link específico. Com eles você escolhe melhor do que eu escolheria.

### O que buscar

🔗 https://lista.mercadolivre.com.br/mala-de-bordo-rigida-preta
🔗 https://lista.mercadolivre.com.br/kit-mala-bordo-necessaire

Termos que funcionam: `mala de bordo rígida preta`, `kit mala + necessaire`, `mala 20 polegadas ABS`

### Especificação — o que o robô exige

| Critério | O que precisa | Por quê |
|---|---|---|
| **Tipo** | Rígida (casco duro) | Mala mole não sustenta forma nem parafuso |
| **Tamanho** | Bordo / 20 polegadas · ~55 × 35 × 23 cm | Proporção de torso humano e cabe a fonte ATX |
| **Profundidade** | **mínimo 20 cm** | Menos que isso não cabe a fonte + placas |
| **Material** | **ABS** de preferência | Aceita primer comum. Polipropileno exige primer especial (+R$40) |
| **Fechamento** | **Zíper** | Vira o painel de manutenção. Fecho rígido com cadeado atrapalha |
| **Cor** | **Preta fosca** | Alinha com a marca e esconde imperfeição de corte |
| **Textura** | Frisos verticais | Depois de montada, lê como armadura — é o visual que o render mostrou |
| **Peso** | Quanto mais leve, melhor | Tudo que ela pesa, a coluna da cadeira carrega |

### O acerto de design: comprar o KIT

Vários vendedores oferecem **mala + necessaire da mesma linha**. É o que dá coerência de fábrica: mesma cor, mesma textura, mesmos frisos no torso e na cabeça. Isso é exatamente o que faz um projeto parecer pensado — e sai mais barato que comprar separado.

**Se achar kit preto rígido com necessaire, é ele.**

### Faixa de preço e a alternativa

| Origem | Preço | Avaliação |
|---|---|---|
| **Usada** (OLX, bazar, brechó) | R$ 30-80 | ⭐ Melhor custo. O defeito que faz alguém jogar fora — rodinha quebrada, trolley emperrado, zíper do fundo rasgado — **não atrapalha nada** no uso como torso. Você quer a casca. |
| **Kit novo** (mala + necessaire) | R$ 200-350 | Chega na cor certa, acabamento de fábrica, e você pula a pintura. É 1/4 do orçamento do robô numa peça só — mas é a peça que todo mundo vai ver. |

**Minha leitura:** se é pra ser bonito e servir de vitrine da Kronos, o kit novo preto se justifica. É o único item do projeto onde o dinheiro vira imagem. Mas espere achar um kit com necessaire junto — comprar mala e necessaire de linhas diferentes perde justamente o efeito.

⚠️ **Antes de furar, leia a Prancha do Ombro.** A mala é a *pele*: quem segura o motor é uma placa de madeira por dentro. Parafusar direto na casca rasga em poucos dias.

---

## 2.2 Os braços — tubo quadrado de alumínio (substituiu o PVC)

🔗 Onde comprar: **loja de alumínio / esquadria / serralheria**, ou ferragem grande.
No Mercado Livre busque: `tubo quadrado aluminio 25x25 1 metro`

### Especificação

| Peça | Medida | Comprimento | ≈ Preço |
|---|---|---|---|
| **Braço (úmero)** | 25 × 25 mm · parede 1,5-2 mm | 28 cm ×2 | barra de 1 m ~R$ 40 |
| **Antebraço** | 20 × 20 mm · parede 1,5 mm | 24 cm ×2 | barra de 1 m ~R$ 35 |

**Uma barra de cada bitola cobre os dois braços.** Total ~R$ 75-90.

### Por que quadrado e não redondo

> O servo do cotovelo precisa de **superfície plana** para assentar. No tubo redondo ele apoia em dois pontos e balança — você teria que improvisar um berço. No quadrado ele parafusa direto na face, reto e firme. É por isso que todo braço robótico comercial usa perfil, não tubo.

De quebra: alumínio é **mais leve que PVC** na mesma rigidez, não amarela, e depois de pintado tem cara de máquina.

### ⚠️ Dois cuidados específicos do alumínio

1. **Nunca deixe o parafuso roscar direto na parede do tubo.** Rosca em alumínio de 1,5 mm espana no terceiro aperto. **Sempre passante, com porca nylock do outro lado.**
2. **Bucha de madeira dentro do tubo** nas pontas de aperto forte (a junção com o ombro). Um taquinho de 3-4 cm impede que o tubo **amasse** quando você aperta. Sem ela, o tubo achata e a junta afrouxa pra sempre.

### Como cortar

Serra de arco com lâmina para metal (~R$ 25) ou disco de corte no Dremel. Alumínio é macio — fura mais fácil que aço, com broca comum. **Passe lima na borda**: corte em alumínio deixa rebarba que corta de verdade.

---

## 2.3 Ferragem da montagem

| Item | ≈ Preço | Para quê |
|---|---|---|
| Kit parafusos M3 / M4 / M5 | R$ 40 | M3 fixa servos e placas; M5 prende braço no motor |
| Porcas **nylock** M3/M4/M5 (~60) | R$ 15 | Porca comum afrouxa em uma semana de vibração |
| Arruelas M3/M4/M5 (~80) | R$ 10 | Espalham a pressão — é o que impede rachar |
| Parafuso M6 × 30/40 + porca (10) | R$ 12 | Fixa o motor de limpador nas orelhas originais |
| **Serra-copo Ø 30 mm** | R$ 25 | O furo do eixo na mala. Broca grande **trinca** plástico |
| Broca 3, 4, 5, 6 mm (metal) | R$ 30 | Furo-guia do diâmetro certo |
| Fita perfurada galvanizada | R$ 12 | Suportes de sensor e potenciômetro |

**Subtotal ferragem: ~R$ 145** — compre junto com o alumínio, na mesma loja de construção.

---

# BLOCO 3 — FERRO-VELHO (não compre isto)

> Economia total: **R$ 450 a 600**. Leve luva e mochila.

### ☐ 2× Motor de limpador de para-brisa 12 V — economia até R$ 400
**Peça o braço da palheta junto!** O clamp dele é a fixação pronta no eixo.

| Especificação | |
|---|---|
| Tensão | 12 V |
| Torque | 10-25 N·m (100-250 kg·cm) |
| Velocidade | ~45-70 RPM |
| Peso | ~1,2 kg cada |
| Redução | Rosca sem-fim — **autotravante** |

**Como escolher:** gire o eixo com a mão. Deve estar duro (é a rosca sem-fim, normal), mas sem ranger nem travar. Fios inteiros é melhor.

**Por que não comprar novo:** R$ 150-250 cada. É um motor feito pra durar 15 anos debaixo do capô, na chuva e no calor — um usado de 5 anos é funcionalmente idêntico. Esta é a única peça onde usado não tem desvantagem nenhuma.

### ☐ 1× Fonte ATX de PC — economia R$ 120
Entrega 12 V e 5 V ao mesmo tempo, com proteção de curto embutida. Melhor que fonte nova de bancada.
Liga juntando o fio **verde** num **preto**. ⚠️ **Não abra a carcaça** — guarda carga mesmo desligada.

### ☐ Peças pequenas

| | Item | Onde | Vira |
|---|---|---|---|
| ☐ | 4× rolamento 608 | Skate/patins velho | Mancais das juntas |
| ☐ | 1 impressora velha inteira | Sucata eletrônica | 4 microswitches + parafusos M3 + eixos |
| ☐ | 2 alto-falantes pequenos | Caixinha de som de PC | A voz do robô |
| ☐ | Cabo de freio de bicicleta | Bicicletaria (sobra) | Tendão da garra |
| ☐ | Elásticos | Casa | Reabrem a garra |
| ☐ | 5-10 kg de peso | Halteres, saco de areia | Lastro — impede tombar |
| ☐ | Fios, conectores, parafusos M3 | Sucata de PC | Fiação |

### ☐ Se cruzar: robô aspirador quebrado
Não serve de base (o Ferrão pesa demais), mas rende **módulo de roda com encoder** — motor + redutor + sensor de rotação numa peça só. Ouro para o Nível 2 (rodas).

### ⛔ O que NÃO pegar usado
**Nada com chip.** ESP32, drivers, sensores, servos — sempre novos. Eletrônica de sucata dá bug fantasma: funciona no teste, falha depois, e você perde semanas debugando código que está certo.

> **Peça burra e robusta: usada serve. Peça inteligente e frágil: nova, sempre.**

---

# BLOCO 4 — O QUE VEM DEPOIS (não compre agora)

| Fase | O que comprar | Quando | ≈ |
|---|---|---|---|
| **B** · Cabeça | +1 MG996R (180°), 2 MG90S, **1 display TFT 2,4" ILI9341 SPI**, 1 HC-SR04, acrílico fumê | Depois que a Fase A funcionar | R$ 175 |

### O display padrão — modelo travado

**Busque exatamente:** `display TFT 2.4 SPI ILI9341 240x320 arduino` · **R$ 45 a 70**

| Obrigatório | Recusar |
|---|---|
| Controlador **ILI9341** | ST7789, ILI9488, HX8357 |
| Interface **SPI** | paralelo de 8 bits (come 13 pinos) |
| Lógica **3,3 V** | 5 V sem regulador (queima o ESP32) |
| 2,4" · 240 × 320 | modelos com touch (custam mais, sem uso aqui) |

⚠️ **O controlador é o que importa, não a foto.** Displays com controladores diferentes são visualmente idênticos e exigem código diferente. Confirme "ILI9341" na descrição antes de fechar.

**Pinagem oficial e mapa completo de GPIO:** ver *Parte II — Padrão Estrutural, seção 4b*.
| **C** · Estrutura | **Mala + necessaire**, tubo de alumínio, ferragem, serra-copo | Junto ou logo após a B | R$ 420* |
| **D** · Ombro | 2 BTS7960, potenciômetros, fusíveis, botão de emergência, fio 1,5 mm², capacitores | Com os motores do ferro-velho em mãos | R$ 150 |
| **E-H** · Braços e garra | +2 MG996R, +2 MG90S, barra roscada M8, tinta e primer | — | R$ 200 |
| **I** · Voz e visão | DFPlayer, microfone INMP441, ESP32-CAM, impressora térmica | Por último | R$ 280 |
| **J** · Tela do peito | **Tablet usado 7-10"** + berço rígido + fonte de alimentação | Opcional, quando quiser mostrar catálogo/QR na tela | R$ 0-300 |

\* Considerando kit de mala novo (R$ 250). Com mala usada de bazar, cai para ~R$ 250.

**Regra:** cada fase só é comprada quando a anterior passou no teste. Se o projeto pausar, você não fica com peça encalhada.

### Total revisado do projeto

| | Com mala nova | Com mala usada |
|---|---|---|
| Eletrônica + estrutura + acabamento | ~R$ 1.400 | ~R$ 1.230 |
| Motores e fonte no ferro-velho | já descontado | já descontado |

Com **R$ 345/mês** (os três domingos), o robô completo sai em **4 a 5 meses**.

---

## Checklist da compra do dia 7

```
☐ Servo é 180°? (perguntou ao vendedor ou comprou na Curto Circuito)
☐ ESP32 é o de 38 pinos?
☐ Levou 2 sensores?
☐ Protoboard COM regulador de tensão?
☐ Tudo no mesmo carrinho (frete único)?
☐ Tem cabo USB de DADOS em casa?
☐ Óculos de proteção comprado em loja física?
```

**Total do dia 7: R$ 225,50 + R$ 15 dos óculos = R$ 240,50**

> Nada de mala, alumínio ou ferragem agora. Isso é Fase C — e só faz sentido comprar
> depois que o servo estiver girando na bancada, porque é o teste da Fase A que confirma
> que o resto do projeto faz sentido.
