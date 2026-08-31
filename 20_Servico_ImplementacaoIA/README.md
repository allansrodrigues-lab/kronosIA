# Serviço #8 — Implantação de IA Operacional (Claude + MCP)

> A Kronos entra na empresa, mapeia o trabalho repetitivo que o time já faz manual, e configura Claude + MCP em cima do que a empresa já usa (Gmail, Drive, planilha, Slack, sistema interno) — pra devolver horas pro time, não pra substituir atendimento.

Nasce da constatação de que "atendente de IA 24h no WhatsApp" virou commodity — a Meta lançou de graça em junho/2026 (Meta Business Agent). O que a Meta **não** dá de graça é trabalho de descoberta + configuração específica dentro de uma empresa: entender o processo real do cliente, plugar as ferramentas certas e treinar quem vai usar. Isso é consultoria de implementação, não produto de prateleira — não tem "grátis" que substitua.

---

## Para quem é (e a dor que paga)

| Critério | O que procurar |
|---|---|
| **Porte** | PME — grande o bastante pra ter orçamento e time, pequena o bastante pra não ter TI/RPA própria já resolvendo isso |
| **Sinal de dor** | Time fazendo trabalho manual repetitivo hoje: copiar dado de planilha pra sistema, responder e-mail padrão, gerar relatório toda semana, conciliar informação entre duas fontes |
| **Stack já existente** | Já usa Google Workspace, Slack, planilha, algum CRM — é em cima disso que o MCP conecta. Sem isso, não tem o que plugar |
| **Setor com "trabalho de escritório" repetitivo** | Contabilidade, escritório de advocacia (back-office, não atendimento), imobiliária (papelada), corretora de seguros, agência de marketing/design, RH/recrutamento (triagem de currículo), financeiro/cobrança |

**Quem compra:** dono ou gerente operacional — sente "minha equipe perde X horas por semana nisso" e tem orçamento pra resolver.
**Quem usa no dia a dia:** analista administrativo, financeiro, assistente jurídico, corretor — a pessoa que hoje faz manual e passa a operar o Claude configurado.

**Princípio de foco:** não vender "implanta IA na empresa" genérico (largo demais, assusta e não fecha). Vender **um processo específico resolvido** — *essa planilha, esse relatório, essa triagem de e-mail* — e expandir depois que o time confia.

---

## O que o cliente recebe

1. **Diagnóstico do processo** — qual tarefa repetitiva vale automatizar primeiro (ROI em horas/mês)
2. **Configuração MCP** — Claude conectado às ferramentas reais da empresa (Gmail, Drive, Calendar, Sheets, Slack, sistema interno via API)
3. **O fluxo funcionando** — testado com dado real da empresa, não com exemplo genérico
4. **Treinamento da pessoa que vai operar** — não é entrega técnica pra TI, é capacitação de quem usa
5. **Documentação enxuta** — como pedir, o que esperar, o que fazer se der errado
6. **Suporte de ajuste no primeiro mês** — processo real sempre revela exceção que o discovery não previu

---

## Tipos de implementação (escopo do serviço)

- **Triagem e resposta de e-mail** — classificar, priorizar e rascunhar resposta padrão
- **Relatório automático recorrente** — planilha/CRM → relatório redigido, toda semana/mês
- **Conciliação de dados entre sistemas** — comparar duas fontes e sinalizar divergência
- **Organização de agenda e documentos** — Calendar + Drive arrumados e consultáveis por linguagem natural
- **Pesquisa e research aplicado** — levantar informação externa estruturada (preço de concorrente, dado de mercado, due diligence simples)

**Fora de escopo (por ora):** decisão automática sobre dinheiro/contrato sem revisão humana, e qualquer processo sem dado real pra testar (não se implementa "no vácuo").

---

## Como funciona (operação)

```
Chamada de diagnóstico (30-45min)
        → mapear 1-3 processos candidatos, escolher o de maior ROI/menor risco
        → configurar MCP nas ferramentas da empresa (permissão do cliente, escopo mínimo necessário)
        → testar com dado real do cliente, ajustar
        → treinar a pessoa que vai operar
        → acompanhar 2-4 semanas de uso real, corrigir exceção
        → suporte contínuo / expandir pro próximo processo
```

**Regra-mãe reusada:** código/ferramenta faz a parte determinística (buscar, comparar, calcular), Claude faz a parte de linguagem (redigir, interpretar, decidir o que priorizar) — mesmo padrão do resto do Kronos.

---

## Investimento (referência — cada proposta é dimensionada pelo escopo real)

| Item | Faixa | Observação |
|---|---|---|
| **Diagnóstico** | R$ 0 – R$ 300 | Chamada de mapeamento; abatido do valor se fechar implementação |
| **Implementação (1º processo)** | R$ 1.500 – R$ 3.000 | Setup MCP + configuração + teste + treinamento, pagamento único |
| **Retainer mensal** | R$ 500 – R$ 1.200/mês | Suporte, ajuste, monitoramento; escala com nº de processos ativos |
| **Processo adicional** | R$ 800 – R$ 1.800 | Cada novo processo automatizado depois do primeiro |

Comparação âncora: um analista júnior dedicado a essa tarefa custa R$ 2.000-3.000/mês trabalhando só nisso — a implementação libera a pessoa que já existe pra fazer outra coisa.

---

## Arquivos desta pasta

- `README.md` — este documento
- `base_conhecimento/01_roteiro_discovery.md` — roteiro de perguntas pra chamada de diagnóstico
- `base_conhecimento/02_playbook_mcp.md` — quais MCP/ferramentas plugar por tipo de processo
- `gerar_proposta_implementacao.py` — gera a proposta comercial em PDF (rodar com `uv run --with reportlab python gerar_proposta_implementacao.py`)

## Próximos passos

1. ✅ Definição do serviço + ICP + proposta comercial
2. ⬜ Rodar o roteiro de discovery com o contato que já testou o Kronos e comparou com a Meta
3. ⬜ Escolher o processo-piloto (1 empresa, 1 processo, medir ROI real antes de escalar)
4. ⬜ Documentar o primeiro caso como referência pra próxima venda
