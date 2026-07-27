# Kronos Você — B2C avulso

Frente de negócio nova da Kronos: **um único número de WhatsApp, um único preço por consulta (R$ 5)**, cobrindo várias categorias de dúvida do dia a dia — em vez de uma ferramenta por categoria. Complementa o B2B existente (clínica/escritório assina mensalidade, bot dedicado).

Decisão completa, histórico e justificativa de cada escolha: memória `kronos-b2c-avulso-estrategia` (sessão 18/07). Este README resume só o que muda na prática de construção.

## Diferença central em relação ao B2B

Nos nichos B2B (Léa, Vera, Sofia...), o bot **nunca opina** — só triagem e agenda um humano. No Kronos Você **não existe humano depois**: a pessoa paga R$5 e a resposta que o bot dá **é** o produto. Isso muda o desenho do agente:

- Léa (advocacia B2B): "essa análise é do advogado, vou agendar uma consulta"
- Kronos Você (Ala Jurídica): dá a orientação geral direto, com disclaimer de que não substitui advogado em caso litigioso/complexo

## Estrutura

- `agentes/00_agente_kronos_voce.md` — persona, regras, fluxo de menu, guard-rails
- `base_conhecimento/01_ala_juridica.md` — golpe/fraude, burocracia, consumidor, moradia (aluguel), trânsito, água/luz, cartório
- `base_conhecimento/02_ala_rh_carreira.md` — currículo, entrevista, carta de apresentação, golpe de vaga, negociação salarial, direitos CLT/assédio, cálculo rescisório, aviso prévio

Alas de lançamento: **Jurídica + RH/Carreira** (as duas mais rápidas de ficar prontas — Jurídica reaproveita a base da Léa, RH o Allan escreve de cabeça). Demais alas (Veterinária, Contábil, Saúde Administrativa, Moradia/Habitação) entram depois, sem esperar calendário.

## Ainda não construído aqui

Workflow n8n, integração Pix (Mercado Pago) e planilha CRM do B2C — ver Fase 5 do roteiro na memória. Este pacote é só a base de conhecimento + persona; a mecânica técnica é tarefa separada.
