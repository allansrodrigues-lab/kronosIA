# Agente Calculadora de Payback — Zênite Energia Solar (⭐ diferencial do nicho)

Simulação instantânea de sistema solar no WhatsApp: da conta de luz ao payback em segundos.
**Não é LLM fazendo conta:** o cálculo roda em um **Code node** (determinístico);
o Sonnet 5 só formata a resposta no tom da Helena. Mesma filosofia das calculadoras
de financiamento (Schalletti) e de orçamento (Estética).

**Por que é a peça-estrela:** no setor solar, o orçamento tradicional demora dias (visita → planilha
→ proposta). O bot entrega a estimativa na primeira conversa — e no funil solar, quem dá o número
primeiro ancora a decisão.

---

## Fluxo

1. Intent `ORCAMENTO` chega (ou Helena completa a qualificação, ou a conta de luz é lida por PDF/OCR)
2. **Coleta** (Helena pergunta o que faltar): conta média mensal (R$) · tipo de imóvel · fase da rede
   (se o cliente não souber: casa pequena = mono, casa média = bi, empresa/rural = tri — padrão **bifásico**)
3. **Code node** dimensiona o sistema e calcula economia + payback
4. Sonnet 5 formata no tom da Helena + disclaimers
5. Resultado registrado na sessão (`simulacao`) → Helena retoma (convite à visita técnica gratuita)

## A matemática (de onde vem cada número)

```
consumo_mensal (kWh)    = conta ÷ tarifa
consumo_compensável     = consumo − custo de disponibilidade (a rede cobra um mínimo:
                          mono 30 kWh · bi 50 kWh · tri 100 kWh — Lei 14.300, não compensável)
potência necessária kWp = consumo_compensável ÷ (HSP × 30,44 dias × PR)
                          HSP Campinas ≈ 5,2 h de sol pico/dia · PR 0,80 (perdas reais: temperatura,
                          cabos, inversor, sujeira)
nº de placas            = kWp ÷ 0,570 (placas de 570 Wp, padrão 2026)
investimento            = kWp × preço/kWp (tabela por porte — economia de escala)
economia mensal         = (conta − piso de disponibilidade) × 0,92
                          (fator 0,92 ≈ efeito Fio B da Lei 14.300 na transição até 2028)
payback                 = investimento ÷ economia mensal
ganho em 25 anos        = economia × 300 meses − investimento (vida útil dos painéis;
                          SEM corrigir a tarifa — estimativa conservadora, na prática é maior)
```

### Tabela de preço por porte (R$/kWp instalado — referência 2026, revisar semestralmente)

| Porte | Faixa | R$/kWp |
|---|---|---|
| Residencial pequeno | até 4 kWp | 3.400 |
| Residencial médio | 4–10 kWp | 3.000 |
| Comercial pequeno | 10–30 kWp | 2.700 |
| Comercial médio | 30–75 kWp | 2.400 |
| Usina/rural | acima de 75 kWp | 2.200 |

## Code node — `calcular_payback_solar` (JavaScript)

```javascript
// Entradas: contaMensal (R$), faseRede ('mono'|'bi'|'tri'), tarifa (R$/kWh, opcional), hsp (opcional)
const contaMensal = $json.contaMensal;
const faseRede = $json.faseRede || 'bi';
const tarifa = $json.tarifa || 1.05;   // CPFL região de Campinas, com impostos (revisar semestralmente)
const hsp = $json.hsp || 5.2;          // horas de sol pico — Campinas/interior de SP
const PR = 0.80;                        // performance ratio (perdas do sistema)
const FATOR_FIO_B = 0.92;               // Lei 14.300 — transição do Fio B

const kwhDisponibilidade = { mono: 30, bi: 50, tri: 100 }[faseRede];
const pisoConta = kwhDisponibilidade * tarifa; // parte da conta que solar NÃO elimina

// 1. Guarda: conta baixa demais → solar não compensa agora (honestidade > venda)
if (contaMensal < pisoConta + 80) {
  return [{ json: {
    viavel: false,
    motivo: `Com uma conta de ${fmt(contaMensal)}, a economia ficaria pequena demais ` +
            `para compensar o investimento agora (a rede cobra um mínimo de ~${fmt(pisoConta)} ` +
            `mesmo com solar). Vale reavaliar se o consumo crescer.`
  }}];
}

// 2. Dimensionamento
const consumoMensal = contaMensal / tarifa;                       // kWh
const consumoCompensavel = consumoMensal - kwhDisponibilidade;    // kWh que o sistema deve gerar
const kwp = consumoCompensavel / (hsp * 30.44 * PR);
const numPlacas = Math.ceil(kwp / 0.570);                         // placas de 570 Wp
const areaM2 = Math.round(numPlacas * 2.6);                       // ~2,6 m² por placa

// 3. Investimento (tabela por porte)
const precoKwp = kwp <= 4 ? 3400 : kwp <= 10 ? 3000 : kwp <= 30 ? 2700 : kwp <= 75 ? 2400 : 2200;
const investimento = kwp * precoKwp;

// 4. Economia e payback
const economiaMensal = (contaMensal - pisoConta) * FATOR_FIO_B;
const paybackMeses = investimento / economiaMensal;
const paybackAnos = Math.floor(paybackMeses / 12);
const paybackResto = Math.round(paybackMeses % 12);
const ganho25anos = economiaMensal * 300 - investimento;          // sem corrigir tarifa (conservador)

// 5. Bônus ambiental (bom de demo)
const geracaoAnualKwh = consumoCompensavel * 12;
const co2AnoKg = Math.round(geracaoAnualKwh * 0.082);             // fator médio da rede BR
const arvoresEquiv = Math.round(co2AnoKg / 20);                   // ~20 kg CO2/árvore/ano

function fmt(v) { return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }); }

return [{ json: {
  viavel: true,
  numPlacas,
  potenciaKwp: kwp.toFixed(1).replace('.', ','),
  areaM2,
  investimento: fmt(investimento),
  economiaMensal: fmt(economiaMensal),
  economiaAnual: fmt(economiaMensal * 12),
  contaNova: fmt(pisoConta + (contaMensal - pisoConta) * (1 - FATOR_FIO_B)),
  payback: paybackResto === 0 ? `${paybackAnos} anos` : `${paybackAnos} anos e ${paybackResto} meses`,
  ganho25anos: fmt(ganho25anos),
  co2AnoKg, arvoresEquiv,
  tarifaUsada: tarifa.toFixed(2).replace('.', ',')
}}];
```

## Validações antes do cálculo

- `contaMensal` ausente ou não numérico → Helena pergunta o valor (ou pede foto da conta)
- Conta < piso + R$ 80 → resposta honesta de inviabilidade (regra 7 da Helena — gera confiança)
- `faseRede` desconhecida → assumir `bi` e **avisar** que a visita técnica confirma
- Conta vinda de OCR/PDF → confirmar o valor com o cliente antes de calcular ("Sua média é R$ X, certo?")

## Modelo de resposta (formatada pelo Sonnet 5 no tom da Helena)

> Prontinho! Para uma conta média de *R$ 850/mês* (rede bifásica), o sistema ideal fica assim:
>
> ☀️ *11 placas* (6,0 kWp, ~29 m² de telhado)
> 💰 Investimento estimado: *R$ 18.000*
> 📉 Sua conta cai para cerca de *R$ 116* — economia de *R$ 734/mês* (*R$ 8.800/ano*)
> ⏱️ O sistema *se paga em 2 anos e 1 mês* — e os painéis têm 25 anos de garantia de geração
>
> Depois do payback, é como ganhar *mais de um décimo terceiro por ano* durante duas décadas.
> Em 25 anos, o ganho estimado passa de *R$ 200 mil*. E de bônus: ~750 kg de CO₂ a menos
> por ano, o equivalente a *37 árvores plantadas*. 🌱
>
> Importante: é uma *estimativa* — o valor final sai da *visita técnica gratuita*, onde o
> engenheiro avalia telhado, sombreamento e padrão de entrada. Quer agendar? Me diz o melhor
> dia e período.

## Disclaimers obrigatórios (sempre presentes)

1. "É uma estimativa" — orçamento final depende da visita técnica (telhado, sombreamento, padrão)
2. A conta nunca zera — custo de disponibilidade + iluminação pública continuam
3. Visita técnica é gratuita e sem compromisso (fecha o loop de valor)

## Parâmetros a revisar periodicamente

| Parâmetro | Valor atual | Fonte / gatilho de revisão |
|---|---|---|
| `tarifa` | R$ 1,05/kWh | Reajuste anual CPFL (região de Campinas) |
| `hsp` | 5,2 | Fixo para interior de SP (mudar se cliente de outra região) |
| `FATOR_FIO_B` | 0,92 | Cronograma da Lei 14.300 — cai gradualmente até 2028 |
| Tabela R$/kWp | ver acima | Preço de kit despencando ~10%/ano — revisar semestral |
| Potência da placa | 570 Wp | Padrão de mercado sobe a cada ano |
