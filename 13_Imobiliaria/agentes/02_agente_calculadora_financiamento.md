# Agente Calculadora de Financiamento — Schalletti Imóveis (⭐ diferencial do nicho)

Simulação instantânea de financiamento imobiliário no WhatsApp — Price e SAC.
**Não é LLM fazendo conta:** o cálculo roda em um **Code node** (determinístico);
o Sonnet 5 só formata a resposta no tom da Sofia. Mesma filosofia da calculadora de orçamento da Estética.

---

## Fluxo

1. Intent `FINANCIAMENTO` chega (ou Sofia aciona via handoff)
2. **Coleta** (Sofia pergunta o que faltar): valor do imóvel · entrada (R$ ou %) · prazo em anos (padrão 30)
   - Se o cliente citar um código da carteira (ex.: "parcela do SCH-004"), puxar o preço automaticamente
3. **Code node** calcula Price e SAC
4. Sonnet 5 formata no tom da Sofia + disclaimers
5. Resultado registrado na sessão (`simulacao_feita`) → Sofia retoma a conversa (convite à visita)

## Parâmetros de referência (atualizar periodicamente)

| Parâmetro | Valor |
|---|---|
| Taxa de juros referência | **10,49% a.a. + TR** (TR ignorada na simulação) |
| Entrada mínima | 20% (FGTS pode compor) |
| Prazo máximo | 35 anos (420 meses) |
| Renda mínima estimada | parcela ≤ 30% da renda bruta |

## Code node — `calcular_financiamento` (JavaScript)

```javascript
// Entradas: valorImovel, entrada (R$), prazoMeses, taxaAnual (ex.: 0.1049)
const valorImovel = $json.valorImovel;
const entrada = $json.entrada;
const prazoMeses = $json.prazoMeses || 360;
const taxaAnual = $json.taxaAnual || 0.1049;

const financiado = valorImovel - entrada;
const i = Math.pow(1 + taxaAnual, 1 / 12) - 1; // taxa efetiva mensal

// PRICE — parcela fixa
const parcelaPrice = financiado * (i * Math.pow(1 + i, prazoMeses)) / (Math.pow(1 + i, prazoMeses) - 1);
const totalPrice = parcelaPrice * prazoMeses;

// SAC — amortização constante, parcela decrescente
const amortizacao = financiado / prazoMeses;
const primeiraSAC = amortizacao + financiado * i;
const ultimaSAC = amortizacao + amortizacao * i;
const totalSAC = prazoMeses * amortizacao + i * financiado * (prazoMeses + 1) / 2;

const rendaMinima = parcelaPrice / 0.30; // parcela ≤ 30% da renda

const fmt = v => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });

return [{ json: {
  financiado: fmt(financiado),
  percentEntrada: Math.round(entrada / valorImovel * 100),
  prazoAnos: Math.round(prazoMeses / 12),
  parcelaPrice: fmt(parcelaPrice),
  totalPrice: fmt(totalPrice),
  primeiraSAC: fmt(primeiraSAC),
  ultimaSAC: fmt(ultimaSAC),
  totalSAC: fmt(totalSAC),
  rendaMinima: fmt(rendaMinima),
  taxaAnualPct: (taxaAnual * 100).toFixed(2).replace('.', ',') + '% a.a.'
}}];
```

## Validações antes do cálculo

- `entrada < 20%` do valor → avisar que a entrada mínima usual é 20% e perguntar se quer simular com ela (FGTS pode compor)
- `prazoMeses > 420` → limitar a 420 e avisar
- Valores ausentes → Sofia pergunta apenas o que falta (nunca refaz perguntas já respondidas)

## Modelo de resposta (formatada pelo Sonnet 5 no tom da Sofia)

> Prontinho! Simulação para um imóvel de *R$ 690.000* com entrada de *R$ 138.000* (20%), em *30 anos*:
>
> 💰 *Price* (parcela fixa): *R$ 5.045/mês*
> 📉 *SAC* (começa maior e diminui): primeira *R$ 6.360*, última *R$ 1.540*
>
> Renda familiar estimada para aprovação: a partir de *R$ 16.800*.
>
> Importante: é uma *estimativa* com taxa de referência de *10,49% a.a.* — a taxa final é definida
> pelo banco na análise de crédito, e nossa equipe te acompanha em todo o processo, sem custo extra.
> Quer que eu já agende uma visita ao imóvel enquanto isso? 🏡

## Disclaimers obrigatórios (sempre presentes)

1. "É uma estimativa" — taxa final é do banco, na análise de crédito
2. Não garantimos aprovação
3. Assessoria da Schalletti é sem custo extra (fecha o loop de valor)
