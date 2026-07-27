---
name: kronos-ferrao
description: Operar o projeto Ferrão — o atendente presencial eletrônico da Kronos (robô humanoide de mala rígida sobre base de cadeira). Use para consultar a especificação padrão (medidas, pinagem, display, componentes), atualizar o manual em PDF, registrar decisão nova de projeto, abrir a ficha de uma unidade nova, montar o pacote comercial de comodato, ou tirar dúvida de montagem/compra. Gatilhos, "ferrão", "robô", "atendente presencial", "atualiza o manual do robô", "qual o padrão do display", "pinagem do ESP32", "quanto custa uma unidade", "comodato do robô", "monta outro robô", "prancha de furação", "lista de corte".
---

# Ferrão — atendente presencial eletrônico da Kronos

Robô humanoide construído com **mala rígida como torso** sobre **base de cadeira de escritório**, com braços de alumínio, rosto em display e cérebro ESP32 conectado aos mesmos workflows n8n dos agentes de WhatsApp.

**Posicionamento:** o par físico do atendente virtual. O cliente já tem a Vera no WhatsApp; o Ferrão é a Vera na recepção — capta o lead presencial, imprime cupom com QR e joga a pessoa no funil que já existe.

**Pasta:** `19_Projeto2_Robo_Humanoide/`

---

## A RECEITA — especificação canônica

> Como o Big Mac: a receita não muda. Dois hambúrgueres, alface, queijo, molho especial, cebola e picles num pão com gergelim. Se mudar um item, não é Big Mac.
>
> **Qualquer Ferrão, em qualquer nicho, é montado exatamente assim.**

### Estrutura

| Parte | Especificação fixa |
|---|---|
| Base | Cadeira de escritório giratória, 5 patas, rodízios travados |
| Coluna | A própria coluna a gás da cadeira |
| Torso | **Mala rígida**, bordo/20", mín. 200 mm de profundidade, ABS, zíper, preta |
| Cabeça | **Necessaire rígida**, de preferência da mesma linha da mala |
| Braço (úmero) | Tubo quadrado alumínio **25 × 25 mm × 280 mm** |
| Antebraço | Tubo quadrado alumínio **20 × 20 mm × 240 mm** |
| Reforço interno | MDF 15 mm — **é o osso**; a mala é só a pele |
| Distância entre ombros | **340 mm** |
| Altura do ombro | **~1.050 mm** · altura total ~1.350 mm |
| Peso máx. na mão | **250 g** |

### Atuadores

| Junta | Componente |
|---|---|
| Ombro (×2) | Motor de limpador de para-brisa 12 V + potenciômetro 10 kΩ + 2 microswitches |
| Cotovelo (×2) | Servo **MG996R 180°** (nunca 360°) |
| Pescoço | MG996R 180° (pan) + MG90S (tilt) |
| Garra | MG90S + tendão de cabo de freio + elástico |

### Eletrônica

| Item | Modelo travado |
|---|---|
| Cérebro | **ESP32 DevKit V1 — 38 pinos** |
| Driver de servo | **PCA9685** (I2C, 0x40) |
| Driver de motor | **BTS7960 (IBT-2)** ×2 — nunca L298N |
| Display do rosto | TFT 2,4" SPI — *controlador a confirmar: ILI9341 (R$122) ou ST7789V (R$75, Curto Circuito)* |
| Sensores | 2× HC-SR04 (com divisor 1k/2k2 no ECHO) |
| Áudio | INMP441 (mic, no topo) + alto-falante 3 W (na boca) |
| Visão | ESP32-CAM (placa separada) |
| Cupom | Impressora térmica 58 mm serial |
| Energia | Fonte ATX de PC + fusíveis 10 A e 5 A + botão de emergência |

### Pinagem do ESP32 — **travada**

```
21 SDA (PCA9685)      23 MOSI (display)     25/26 PWM motor E
22 SCL (PCA9685)      18 SCK  (display)     27/14 PWM motor D
19 MISO (reservado)    5 CS   (display)     33 TRIG ultrassônicos
16 DC  (display)      17 RST  (display)     32 ECHO E · 35 ECHO D
 4 backlight (PWM)    13 microswitches      34 pot E  · 39 pot D
15 serial (DFPlayer/impressora)              2 LED de status
livres: 12 e 0
```

⚠️ **34, 35, 36 e 39 são só entrada.** E os pinos do ADC2 não leem analógico com Wi-Fi ligado — por isso os potenciômetros estão no 34 e 39 (ADC1).

---

## Como operar

### Atualizar o manual (fazer SEMPRE que algo mudar)

```bash
cd "19_Projeto2_Robo_Humanoide" && python gerar_manual.py
```

Gera `Ferrao_MANUAL_COMPLETO.pdf` na pasta **e** na Área de Trabalho.

**Regra de ouro: nunca editar o PDF. Editar o `.md` fonte e regerar.**
Documento novo? Acrescentar na lista `DOCUMENTOS` dentro de `gerar_manual.py`.

### Mapa dos arquivos

| Arquivo | O que é |
|---|---|
| `Projeto_Robo_Sucata.md` | Documento técnico principal (com os desenhos embutidos) |
| `PADRAO_Kit_Estrutural.md` | **A receita**: lista de corte, furação, pinagem, padrão eletrônico |
| `Ferrao_GUIA_DE_COMPRA.md` | O que comprar, por fase, com link e especificação |
| `FORNECEDORES.md` | Fornecedor principal e alternativo de cada peça + kit de reposição + estratégia por volume |
| `FERRO_VELHO_Bilhete.md` | O que garimpar em vez de comprar |
| `FASE_A_Lista_de_Compra.md` | A primeira compra, passo a passo |
| `Guia_Sistema_Eletronica.md` | Curso de eletrônica do zero (aulas) |
| `Ferrao_*.svg` | Desenhos: frontal, lateral, acabamento, mapa de componentes, prancha do ombro, prancha de furação |
| `gerar_manual.py` | Junta tudo e gera o PDF |
| `md_para_pdf.py` | Conversor markdown→PDF genérico (**serve para qualquer doc da Kronos**) |

### Registrar uma unidade nova

Preencher a **Ficha de Adaptação** (seção 6 do `PADRAO_Kit_Estrutural.md`). Só três coisas variam entre unidades:

1. **A mala** — modelo, medidas, material
2. **O motor** — diâmetro do eixo e distância entre orelhas (medir com paquímetro!)
3. **A cadeira** — altura da coluna e furos do mecanismo

O resto é a receita.

---

## Fases de construção e custo

| Fase | O que | Custo | Teste que libera a próxima |
|---|---|---|---|
| **A** | Bancada: ESP32 + PCA9685 + servo + sensor | R$ 225 | Aproxima a mão → o servo se move |
| **B** | Cabeça: pescoço, display, sensores | R$ 175 | A cabeça vira sozinha pra quem chega |
| **C** | Estrutura: mala, alumínio, ferragem | R$ 250-420 | Empurrão firme → não tomba |
| **D** | Ombro: drivers, potenciômetros, energia | R$ 150 | "Vá a 45°" e ele para a ±5° |
| **E-H** | Braços, garra, pintura | R$ 200 | Pega um copo e segura 30 s |
| **I** | Voz, visão, impressora | R$ 280 | Ouve, responde e imprime o cupom |
| **J** | Tablet no peito (opcional) | R$ 0-300 | — |

**Total: ~R$ 1.300 a 1.500.** Com R$ 345/mês (3 domingos de hora extra do Allan), sai em 4-5 meses.

**Custo real por unidade, para fins comerciais:** ~R$ 2.500 (peças + 20-25 h de montagem).

---

## Pacote comercial — comodato

O robô **não é vendido nem dado**: é cedido em **comodato** enquanto durar o contrato de serviço. Cancelou, volta.

| Documento | Onde |
|---|---|
| Cláusula 9 do contrato | `05_Comercial/08_contrato_prestacao_servico.md` |
| Termo de Entrega e Devolução | `05_Comercial/10_termo_entrega_equipamento.md` |

**Como falar na venda:**
> Profissional: *"O equipamento é cedido em regime de comodato durante a vigência do contrato, sem custo de aquisição."*
> Simples: *"O robô fica com você enquanto for nosso cliente, sem pagar nada. Ele continua sendo nosso — se encerrar, a gente busca."*

**Modelos recomendados** (não prometer robô na proposta padrão antes de montar duas unidades):
1. Comodato para cliente âncora — 1 ou 2 no primeiro ano
2. **Aluguel por diária para evento** — receita repetida sem multiplicar montagem
3. Upsell — "quer o atendente presencial também? +R$X"

---

## Erros que custam caro — checar antes

| Erro | Consequência |
|---|---|
| Servo **360°** em vez de 180° | Gira sem parar, não posiciona. Maioria dos anúncios é 360 |
| Parafusar o motor **na casca da mala** | Rasga o plástico em dias. Tem que morder a madeira interna |
| **Broca** em vez de serra-copo | Trinca a casca. Furo >10 mm em plástico é serra-copo |
| ESP32 de **30 pinos** | Falta ADC para os potenciômetros |
| **L298N** no lugar do BTS7960 | Queima: o motor puxa 12-20 A |
| Servo alimentado pelo **pino do ESP32** | Reseta a placa. Usar V+ do PCA9685 |
| Rosca **direto no alumínio** de 1,5 mm | Espana no 3º aperto. Sempre passante + nylock |
| Microfone **perto** do alto-falante | O robô se escuta e entra em looping |
| Fonte no **topo** da mala | Centro de massa alto → tomba quando o braço estende |
| Cabo USB **de carga** | Não grava programa. Parece placa com defeito |

---

## Segurança — não negociável

- O motor de limpador **não para por esforço** (redução sem-fim). Dedo entre braço e torso = esmagamento. Fim-de-curso instalado **antes** do primeiro teste com braço montado.
- **Fusível não é opcional**: a fonte ATX entrega 15 A+. 10 A na linha dos motores, 5 A na dos servos.
- **Não abrir a fonte ATX** — guarda carga mesmo desligada.
- Botão de emergência ao alcance da mão em todo teste.
- Óculos de proteção no Dremel, sempre.
