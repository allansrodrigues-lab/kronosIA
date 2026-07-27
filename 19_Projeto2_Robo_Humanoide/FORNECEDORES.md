# Cadastro de fornecedores — Ferrão

**Atualizado em 26/07/2026**

Cada peça tem **fornecedor principal e alternativo**. Componente eletrônico chinês sai de linha sem aviso — depender de um vendedor só é o jeito mais rápido de quebrar a padronização.

**Legenda:** ✅ verificado por mim · ⚠️ preciso confirmar preço/estoque · ❓ ainda não levantado

---

## 1. Peças críticas — sem elas não existe robô

### ESP32 DevKit V1 (38 pinos) · ~R$ 49

| | Fornecedor | Referência | Preço | Status |
|---|---|---|---|---|
| **Principal** | Mercado Livre | *"Placa Esp32d Esp32 32d Wroom Devkitc V4 38 Pinos Soldados"* · `MLB2048573048` · +5 mil vendidos | R$ 49,50 | ✅ |
| **Alt. 1** | Mercado Livre | `MLB2039477290` · +1000 vendidos | R$ 49,87 | ✅ |
| **Alt. 2** | Curto Circuito / Eletrogate | buscar "ESP32 DevKit" | ~R$ 60-80 | ❓ |
| **Alt. 3** | AliExpress | "ESP32 DevKitC V4 38 pin" | ~R$ 25 | 20-40 dias |

**Risco de descontinuar:** baixo. É o microcontrolador mais vendido do mundo — o modelo muda de revisão, mas sempre existe equivalente.

---

### Display TFT 2,4" SPI · R$ 75 a 122 ⚠️ **decisão pendente**

| | Fornecedor | Controlador | Preço | Status |
|---|---|---|---|---|
| **Opção A** | **Curto Circuito** | ST7789V · SPI · com touch | **R$ 75,50** | ✅ em estoque |
| **Opção B** | **AFELETRONICA** | ILI9341 · SPI · 3,3-5 V | **R$ 122,30** | ✅ 89 unidades |
| Descartado | Achei Componentes | ILI9341 mas **paralelo** | R$ 116,55 | ❌ esgotado |
| Descartado | Saravati | ILI9341 mas **paralelo** | R$ 127,90 | ❌ esgotado |
| **Alt.** | Amazon BR (HiLetgo) | ILI9341 SPI | ❓ | ❓ |

⚠️ **Este é o item de MAIOR risco da cadeia.** Modelo de display muda de controlador sem mudar a foto do anúncio, e cada controlador exige código diferente. **Ao comprar em escala, comprar sempre do mesmo anúncio e conferir o controlador na descrição.**

**Ação pendente:** confirmar a resolução do ST7789V da Curto Circuito (240×240 ou 240×320) para fechar o padrão.

---

### Servo MG996R 180° · R$ 45 a 53

| | Fornecedor | Referência | Preço | Status |
|---|---|---|---|---|
| **Principal** | **Curto Circuito** | *"Servo Motor - MG996R - Digital 180°"* — ângulo no nome do produto | **R$ 45,00** | ✅ |
| **Alt. 1** | Curto Circuito | MG996R avulso | R$ 37,80 | ✅ conferir se é 180° |
| **Alt. 2** | Mercado Livre | *"Servo Motor Tower Pro Mg996 180 Graus"* · `MLB3507456595` | R$ 53 | ✅ |
| **Alt. 3** | Mercado Livre | `MLB27412972` · +5 mil vendidos | R$ 50 | ⚠️ perguntar se é 180° |

⚠️ **A maioria dos anúncios é 360° (rotação contínua) e não serve.** Em compra de escala, sempre confirmar por escrito com o vendedor antes de fechar lote.

**Risco de descontinuar:** baixo. MG996R é padrão de mercado há mais de uma década.

---

### Servo MG90S · R$ 23,90

| | Fornecedor | Preço | Status |
|---|---|---|---|
| **Principal** | Curto Circuito | R$ 23,90 | ✅ |
| **Alt.** | Mercado Livre / AliExpress | R$ 18-25 | ❓ |

---

### Driver BTS7960 (IBT-2) · ~R$ 40

| | Fornecedor | Preço | Status |
|---|---|---|---|
| **Principal** | Mercado Livre — buscar `BTS7960 43A driver ponte H` | ~R$ 40 | ⚠️ |
| **Alt.** | Curto Circuito / Eletrogate | ~R$ 55 | ❓ |

⚠️ **Nunca substituir por L298N.** Se faltar BTS7960, o equivalente aceitável é outro driver de **no mínimo 30 A**.

---

### PCA9685 · R$ 39

| | Fornecedor | Referência | Preço | Status |
|---|---|---|---|---|
| **Principal** | Mercado Livre | `MLB4615275322` · +100 vendidos | R$ 39 | ✅ |
| **Alt. 1** | Mercado Livre | `MLB7079550368` | R$ 44 | ✅ |
| **Alt. 2** | Curto Circuito / RoboCore | ~R$ 50 | ❓ |

⚠️ Conferir se é **PCA9685** mesmo — alguns anúncios trazem LU9685, que é outro chip.

---

### Motor de limpador de para-brisa 12 V · R$ 0 a 250

| | Fonte | Preço | Observação |
|---|---|---|---|
| **Principal** | **Ferro-velho local** | R$ 0-60 | ⭐ Idêntico ao novo. Pedir com o braço da palheta |
| **Alt. 1** | Mercado Livre — usado | R$ 60-120 | ❓ |
| **Alt. 2** | Auto peças — novo universal | R$ 150-250 | ❓ |

**Para escala:** vale **fechar acordo com um ferro-velho** — comprar em lote (5-10 unidades) e negociar preço. É a peça mais barata de estocar e a mais cara se comprada nova.

❓ **Ação:** levantar 2-3 ferros-velhos da região e anotar contato aqui.

---

## 2. Peças de apoio

| Peça | Principal | Alternativo | Preço |
|---|---|---|---|
| HC-SR04 | ML `MLB46876142` ✅ | Qualquer loja de eletrônica | R$ 19 (25 o par) |
| Protoboard + regulador | ML `MLB37233619` ✅ | Eletrogate | R$ 37 |
| Kit resistores | ML `MLB3126214008` ✅ | qualquer | R$ 25 |
| Potenciômetro 10 kΩ | ❓ | eletrônica local | ~R$ 5 |
| Microswitch | Impressora velha ♻️ | ML, kit com 10 | ~R$ 3 |
| Fonte ATX | Sucata de PC ♻️ | ML usada | R$ 0-80 |
| Fusível + porta-fusível | Auto peças (qualquer) | ML | R$ 12 |
| DFPlayer Mini | ❓ | ML / AliExpress | ~R$ 15 |
| Microfone INMP441 | ❓ | ML / AliExpress | ~R$ 20 |
| ESP32-CAM | ❓ | ML / Curto Circuito | ~R$ 45 |
| Impressora térmica 58 mm | ❓ | ML — buscar "impressora térmica embarcada serial" | ~R$ 150 |

---

## 3. Estrutura e mecânica — fornecedor local

Estes **não vale comprar online** (frete de peça longa e pesada inviabiliza):

| Peça | Onde | Observação |
|---|---|---|
| Tubo quadrado alumínio 25×25 e 20×20 | **Serralheria / loja de alumínio** | A partir da 2ª unidade, encomendar cortado na medida |
| Parafusos, nylock, arruelas | Loja de parafusos | Comprar a granel sai muito mais barato que kit |
| Serra-copo, brocas | Material de construção | Compra única, serve para todas as unidades |
| Acrílico fumê (visor) | Loja de acrílico / vidraceiro | Pedir cortado 240 × 100 mm |
| MDF 15 mm | Caixote ♻️ ou marcenaria | Na escala, encomendar cortado (lista M1-M5) |
| Primer e tinta spray preta fosca | Material de construção / auto center | — |

❓ **Ação:** levantar e anotar aqui — 1 serralheria, 1 loja de parafusos, 1 marcenaria e 1 acrílico da região, com telefone.

---

## 4. Carcaça

| Peça | Principal | Alternativo | Preço |
|---|---|---|---|
| Mala rígida | Bazar / brechó / OLX | Mercado Livre novo | R$ 30-80 · R$ 200 nova |
| Necessaire rígida | idem, mesma linha | idem | R$ 20-40 |

⚠️ **Este é o item que NÃO padroniza.** Modelo usado varia sempre. **Se o robô virar produto**, o caminho é escolher **um modelo novo** e comprar em quantidade — aí toda unidade sai idêntica e a ficha de adaptação deixa de existir.

---

## 5. Kit de reposição rápida — para quando houver robô em campo

Quando existir robô na casa de cliente, um defeito precisa ser resolvido em dias, não semanas. Manter em casa:

| Item | Qtd em estoque | Por quê |
|---|---|---|
| **Servo MG996R 180°** | 2 | É o que mais desgasta — peça móvel sob carga |
| **Servo MG90S** | 2 | idem, garra e tilt |
| Display TFT | 1 | Quebra por impacto; e o modelo pode sair de linha |
| ESP32 DevKit | 1 | Barato e é o cérebro — não dá pra esperar frete |
| BTS7960 | 1 | Queima se o motor travar muito |
| Fonte ATX | 1 | Sucata, custo zero |
| Fusíveis 10 A e 5 A | 10 | Centavos, e é o que mais "queima" (de propósito) |
| Cabo de freio + elásticos | — | Tendão da garra é consumível |
| Bobina de papel térmico | 5 | Consumível do cliente |

**Custo do kit reserva: ~R$ 250.** É seguro operacional: sem ele, um servo queimado vira uma semana de robô parado na recepção do cliente — e o cliente vendo o robô morto todo dia.

---

## 6. Estratégia de compra por volume

| Volume | Estratégia |
|---|---|
| **1 unidade** (agora) | Comprar avulso, do anúncio com mais vendas. Prioridade é acertar, não economizar |
| **2 a 5 unidades** | Fechar tudo em 2 lojas (Curto Circuito + Mercado Livre) para reduzir frete. Encomendar alumínio cortado |
| **5+ unidades** | Falar direto com vendedor do ML pedindo preço de lote. Acordo com ferro-velho para motores. Considerar AliExpress para itens não urgentes (metade do preço) |

⚠️ **Antes de comprar lote, montar UMA unidade completa.** Comprar 10 displays antes de validar o modelo é como fechar 10 robôs antes de saber quanto tempo leva um.

---

## 7. Ações pendentes

```
☐ Confirmar resolução do display ST7789V da Curto Circuito
☐ Levantar 2-3 ferros-velhos da região (contato e se aceitam encomenda)
☐ Levantar serralheria (corte de alumínio) — pedir orçamento da lista de corte
☐ Levantar loja de parafusos a granel
☐ Levantar loja de acrílico (corte do visor)
☐ Confirmar preço de BTS7960, DFPlayer, INMP441, ESP32-CAM e impressora térmica
☐ Testar 1 pedido na AFELETRONICA (prazo e atendimento) antes de depender dela
```

---

*Atualize este cadastro toda vez que comprar de um fornecedor novo — anote prazo real de entrega e se o produto veio conforme o anúncio.*
