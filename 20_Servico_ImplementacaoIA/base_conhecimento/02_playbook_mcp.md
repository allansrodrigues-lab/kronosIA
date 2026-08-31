# Playbook de MCP por tipo de processo

> Referência rápida: dado o processo escolhido no discovery, qual conector/ferramenta plugar
> e o que testar antes de considerar "pronto pra treinar o cliente".

---

## E-mail / triagem e resposta

**Conectar:** MCP de Gmail (ou provedor equivalente do cliente).
**Configurar:** rótulos/pastas que já existem no cliente, não inventar taxonomia nova.
**Testar com:** 10-20 e-mails reais recentes, verificar se a classificação bate com o que a pessoa faria.
**Risco a cobrir:** nunca enviar automático sem revisão — sempre rascunho pra aprovação humana no piloto.

## Relatório recorrente

**Conectar:** MCP de Google Sheets/Drive, ou export do sistema interno do cliente.
**Configurar:** código faz o cálculo (soma, média, comparação) — Claude só interpreta e redige. Nunca deixar a IA calcular número que vai pro relatório.
**Testar com:** dado do mês anterior, comparar o relatório gerado com o que a pessoa já fez manualmente.
**Risco a cobrir:** número errado em relatório é o pior tipo de falha silenciosa — validar a conta antes de validar a redação.

## Conciliação entre sistemas

**Conectar:** os dois MCPs/fontes de dado envolvidas (ex: Sheets + Gmail, ou Sheets + export de sistema).
**Configurar:** regra de comparação determinística primeiro (código bate os dados), Claude só narra a divergência encontrada.
**Testar com:** um mês com divergência conhecida, confirmar que o processo pega o mesmo problema que o humano pegou.

## Agenda / documentos

**Conectar:** MCP de Google Calendar + Drive.
**Configurar:** convenção de nomenclatura e pasta que o cliente já usa — não impor estrutura nova sem concordância.
**Testar com:** pergunta real em linguagem natural ("quando é a reunião com o cliente X", "cadê o contrato do fornecedor Y").

## Pesquisa / research aplicado

**Conectar:** busca web (WebSearch) + Drive pra salvar o resultado.
**Configurar:** formato de entrega fixo (mesma estrutura toda vez), fonte sempre citada.
**Testar com:** uma pergunta que o cliente já pesquisou manualmente antes, comparar qualidade/tempo.

---

## Regra geral de segurança em toda implementação

- Escopo mínimo de permissão no MCP — só o que o processo precisa, nunca acesso total "pra facilitar".
- Toda saída que sai da empresa (e-mail, mensagem, documento externo) passa por revisão humana no primeiro mês, mesmo que o processo pareça de baixo risco.
- Nunca plugar em sistema financeiro/contrato com ação automática de escrita sem confirmação explícita por chamada — só leitura + sugestão nesse tipo de processo.
