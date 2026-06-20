# Serviço #7 — Parecer Científico sob Demanda

> Análise científica feita por IA, entregue como um documento fundamentado.

A Kronos recebe uma pergunta do cliente e devolve um **parecer técnico-científico** em PDF: resposta clara, baseada em evidência real (estudos, dados, normas), com método explicado e fontes citadas. É o motor de **leitura de PDF** (nicho Advocacia) apontado para a direção contrária — em vez de ler o documento do cliente, a Kronos **produz** o documento.

---

## Para quem é (e a dor que paga)

| Público | Pergunta típica que ele paga pra responder |
|---|---|
| **Saúde / Estética** (Aurora, Odonto) | "Tenho respaldo científico pra oferecer/indicar esse tratamento?" |
| **Advocacia** (Léa já existe) | "Preciso de um parecer técnico pra instruir esse processo." |
| **Nutrição / Suplementação** | "Esse ativo realmente funciona pra X? O que diz a literatura?" |
| **Empresa / Marketing** | "Minha pesquisa de mercado tem significância? O que os dados dizem?" |

**Princípio de foco:** não vender "análise científica" genérica (largo demais, assusta). Vender **um entregável concreto** — *um parecer, uma pergunta, um PDF*.

---

## O que o cliente recebe

Um PDF profissional (identidade Kronos) com:

1. **Pergunta analisada** — reformulada com precisão
2. **Resposta direta** — sim / não / depende, em uma frase
3. **Fundamentação** — o que a evidência mostra, com nível de confiança
4. **Método** — como a análise foi feita (fontes consultadas, critérios)
5. **Pontos de atenção / ressalvas** — vieses, limitações, lacunas
6. **Fontes citadas** — referências reais e rastreáveis
7. **Rodapé**: caráter informativo, não substitui consultoria profissional especializada

---

## Tipos de parecer (escopo do serviço)

- **Revisão de evidência** — "o que a literatura diz sobre X" (síntese de estudos)
- **Checagem de alegação** — avaliar se um claim de saúde/marketing tem respaldo
- **Análise de dados** — cliente manda planilha → estatística + interpretação + gráficos
- **Apoio acadêmico** — estruturar/revisar metodologia, normas (ABNT/APA)

---

## Como funciona (operação remota, 100%)

```
Cliente manda a pergunta (+ anexo opcional: planilha/PDF)
        → IA pesquisa/analisa a evidência
        → código apura os números (IA nunca calcula, só interpreta)
        → Claude Sonnet redige o parecer estruturado
        → gera PDF Kronos
        → entrega (WhatsApp / e-mail)
        → registra no CRM
```

**Regra-mãe reusada:** código faz conta, IA faz narrativa/insight (mesmo padrão da Calculadora da pizzaria e do Relatório Automático).

---

## Investimento

| Item | Valor | Observação |
|---|---|---|
| **Parecer avulso** | R$ 150 – R$ 300 | por documento, conforme profundidade |
| **Plano mensal** | R$ 400 – R$ 600/mês | X pareceres + prioridade ← *o que empurrar* |

O plano mensal é o alvo: gera **recorrência** e casa com o objetivo de operação remota.

---

## Arquivos desta pasta

- `README.md` — este documento
- `base_conhecimento/01_motor_parecer.md` — prompt/spec do motor de IA que redige o parecer
- `base_conhecimento/02_tipos_e_escopo.md` — o que está dentro e fora do escopo
- `gerar_proposta_cientifica.py` — gera a proposta comercial em PDF (rodar com `uv run --with reportlab python gerar_proposta_cientifica.py`)

## Próximos passos

1. ✅ Definição do serviço + proposta comercial
2. ⬜ Montar o workflow n8n (`kronos-parecer-cientifico`) — webhook + motor + gerador de PDF
3. ⬜ Plugar `/parecer` na Central de Demos (chavinha)
4. ⬜ Escolher nicho-piloto pra primeira oferta (recomendação: **Saúde/Estética**, base já aberta)
