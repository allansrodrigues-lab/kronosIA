# Guia do Sistema — eletrônica do Ferrão, do zero

Curso em aulas curtas. Cada uma tem uma ideia central, uma analogia e um teste.
Não precisa ter comprado nada para começar.

---

## Aula 1 — O robô inteiro cabe em 5 blocos

Todo robô do mundo, do Ferrão ao braço industrial de fábrica, é a mesma coisa: **cinco blocos conversando**. Se você entender esses cinco, entendeu robótica — o resto é detalhe de tamanho.

| Bloco | No Ferrão | Analogia |
|---|---|---|
| **Energia** | Fonte ATX | A **caixa d'água** da casa. Guarda pressão pra quando alguém abrir a torneira. |
| **Cérebro** | ESP32 | O **maestro**. Decide tudo, mas não toca nenhum instrumento — sozinho ele não move nem uma folha de papel. |
| **Driver** | BTS7960, PCA9685 | A **torneira**. O maestro só encosta o dedo; a torneira é quem libera a água grossa. |
| **Músculo** | Motor de limpador, servos | Quem realmente faz força. |
| **Sentidos** | Ultrassônico, câmera, microfone | Os **olhos e ouvidos**, que devolvem informação pro cérebro. |

### A regra que evita queimar tudo

> **Sinal e força andam em vias separadas, e só se encontram dentro do driver.**

O fio que sai do ESP32 carrega **ordem** — uma corrente minúscula, milésimos de ampere. É um bilhete escrito: "gire 45 graus".

O fio que sai da fonte carrega **força** — dezenas de amperes. É o caminhão de carga.

O driver é o único lugar onde os dois se encontram: ele **lê o bilhete** e **libera o caminhão**. Se você ligar o caminhão direto no pino que era pra receber bilhete, o ESP32 morre na hora — e esse é o erro número 1 de quem começa em hardware.

É por isso que o projeto tem PCA9685 (torneira dos servos) e BTS7960 (torneira dos motores). Não são luxo: são o que impede R$35 de cérebro virar carvão.

### O ciclo que faz o robô parecer vivo

O robô não "executa uma sequência". Ele repassa o mesmo ciclo, muitas vezes por segundo:

```
   SENTIR  ──►  DECIDIR  ──►  AGIR  ──►  (volta pro SENTIR)
     │             │            │
  ultrassônico   ESP32       driver
   câmera       compara     → motor
   microfone    com o alvo   → servo
```

Exemplo real do Ferrão levantando o braço:

1. **Sentir**: o potenciômetro do ombro diz "estou em 20°".
2. **Decidir**: o ESP32 compara com o alvo (45°) e conclui: "faltam 25°, vai rápido".
3. **Agir**: manda o driver girar o motor.
4. **Sentir de novo**: agora está em 43°. "Faltam 2°, vai devagar."
5. Chegou em 45° → para.

Repare que ele **nunca sabe onde vai parar** — ele só corrige o erro, sem parar, muitas vezes por segundo. É exatamente o que sua mão faz equilibrando o cabo de vassoura. Isso se chama **malha fechada** (feedback), e é a diferença entre um robô e um brinquedo de dar corda.

Um motor **sem** potenciômetro é malha aberta: você manda girar por 2 segundos e torce pra ter parado no lugar certo. Funciona pra ventilador, não pra braço.

### O que isso significa na prática

Quando o braço não parar no lugar certo, o problema vai estar em **um desses três**:
- o sentido está mentindo (potenciômetro solto no eixo),
- a decisão está errada (o cálculo no código),
- ou a força não chega (driver ou alimentação fraca).

Saber que só existem três suspeitos é o que transforma "não funciona" em "vou testar o primeiro".

---

### ✅ Teste da Aula 1

Sem tocar em nenhuma peça, responda em voz alta:

1. Por que o ESP32 não pode alimentar o motor direto?
2. Qual bloco é a "torneira" e o que ele faz com a ordem que recebe?
3. Se o braço passa do ponto e volta, tremendo, qual dos três suspeitos você investiga primeiro?

*(Resposta da 3: a decisão — o cálculo está corrigindo forte demais perto do alvo. Isso se chama ganho alto, e a gente ajusta um número no código.)*

---

## Aula 2 — em breve: montar o circuito no simulador, sem gastar nada
