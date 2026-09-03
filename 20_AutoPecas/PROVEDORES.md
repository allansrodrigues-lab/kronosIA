# Provedores a integrar — Agente Fiscal, Agente RH, Transcrição por foto

Pesquisa feita em 2026-09-02. Nenhum destes é a Kronos construindo do zero — é integração/licença com quem já é homologado, mesmo princípio já aplicado à ideia descartada de "SaaS de marketplace" (usar API oficial, não bot).

---

## NF-e / NFS-e — Agente Fiscal

| Provedor | Observação |
|---|---|
| **Focus NFe** | Integração ativa em +3.000 municípios; garante integração com qualquer município novo por taxa fixa de R$199 em até 15 dias. API REST. Forte opção padrão. |
| **NFE.io** | Cobre NF-e (produto), NFC-e (consumidor) e NFS-e (serviço) na mesma API — relevante porque loja de autopeças pode emitir tanto nota de produto quanto de serviço (ex: instalação). |
| Notaas, Tecnospeed, Nuvem Fiscal, eNotas | Aparecem nos comparativos 2026 como alternativas — não aprofundado ainda qual encaixa melhor em custo/documentação. |

**Decisão pendente:** qual desses vira o padrão da Kronos — pesar cobertura municipal, preço e qualidade de documentação da API antes de fechar.

**Lembrete de segurança (já registrado no backlog):** o certificado digital (A1/A3) usado pra assinar a nota é do cliente — a Kronos nunca guarda a chave privada. Fica com o provedor ou no ERP.

Sources:
- [API para emissão de Notas Fiscais Eletrônicas - Focus NFe](https://focusnfe.com.br/)
- [Compare o Focus NFe com concorrentes](https://focusnfe.com.br/compare/)
- [NFE.io : sistema para emissão de notas fiscais eletrônicas](https://nfe.io/)
- [Comparativo de APIs NFSe para Desenvolvedores em 2026](https://www.notaas.com.br/blog/post/melhor-api-nfse-desenvolvedores-brasil-plugnotas-tecnospeed-enotas-nuvem-fiscal-focus-nfe-comparativo-2025-2026)

---

## Folha de pagamento / RH — Agente RH

Duas categorias diferentes de solução encontradas — importa não confundir:

1. **Terceirização completa** (Convenia, Solides, empresas de BPO de folha) — a empresa terceiriza o processo inteiro pra fora. Não é isso que a Kronos quer: o objetivo é o **agente preparar o rascunho**, não terceirizar tudo.
2. **API de integração** (o que interessa de verdade):
   - **Pontotel** — API que recebe batida de ponto, lança férias/afastamento/dispensa automaticamente, consulta banco de horas — sincronização em tempo real nos dois sentidos.
   - **RHID Ponto (Secullum)** — API RESTful com autenticação por Bearer Token, sincroniza dados cadastrais/batidas/cálculo de horas com ERP de RH.
   - **ADP** — internacional, também expõe API de folha/ponto/benefícios.

**Leitura:** pra loja pequena (2-6 balconistas), o caminho mais realista é integrar com uma API de ponto (tipo Pontotel/Secullum) que já calcula banco de horas, e o Agente RH usa isso pra montar o rascunho de folha — não processar o cálculo trabalhista bruto do zero.

**Decisão pendente:** qual API de ponto integrar primeiro; ainda não achei uma "API de folha pura" brasileira voltada a desenvolvedor terceiro (a maioria vende terceirização completa, não acesso de API).

Sources:
- [Integração sistema de ponto com folha de pagamento - Pontotel](https://www.pontotel.com.br/integracao-sistema-de-ponto-com-folha-de-pagamento/)
- [Como Integrar a API do RHID Ponto ao seu ERP de Folha](https://impactotecnologia.com.br/blog/integracao-api-rhid-ponto-erp-folha/)
- [10 melhores empresas de Terceirização de Folha de Pagamento em 2026](https://www.ohub.com.br/ideias/melhores-empresas-de-terceirizacao-de-folha-de-pagamento/)

---

## Base de referência cruzada de peças — Transcrição por foto

| Opção | Observação |
|---|---|
| **TecDoc (TecAlliance do Brasil)** | Padrão mundial da indústria, 26 anos de histórico. Catálogo Brasil cobre 560 marcas e 56 mil tipos de veículo. **TecDoc Catalogue Brasil Premium: R$400/licença/ano** (pagamento único anual) — inclui busca por placa e chassi. Existe também versão gratuita mais limitada via campanha da TecAlliance. Contato comercial: vendasbrasil@tecalliance.net. |

**✅ Confirmado (2026-09-02): existe acesso via API, não só manual.** A TecAlliance expõe **web service REST/SOAP** (`TecdocToCatDLB.jsonEndpoint`), autenticado por API key + provider ID, gerada na conta do desenvolvedor. Dá acesso a dado de veículo, referência cruzada OE↔aftermarket, especificação técnica, imagem e instrução de instalação — exatamente o que o Agente de Transcrição precisa. **Falta só confirmar se o plano Premium de R$400/ano inclui a chave de API ou se API é um plano/contrato separado do catálogo de uso manual** — isso só contato comercial direto responde.

Sources (API TecDoc):
- [TecAlliance API - Developer docs, APIs, SDKs, and auth](https://apitracker.io/a/tecalliance-net)
- [What is TecDoc? A Practical Integration Guide](https://dev-opla.com/resources/what-is-tecdoc-auto-parts-ecommerce-guide)
- [TECDOC API Connection for Importing Car Parts Information](https://www.corenio.com/tecdoc-api)

---

## Confirmação adicional — Focus NFe (2026-09-02)

**✅ API REST confirmada e documentada publicamente**, integra com qualquer linguagem moderna (JS/Node, PHP, Python, Java, C#, Ruby, Go) — inclusive tem [documentação no Postman](https://www.postman.com/focusnfe/focus-nfe/documentation/906jrtc/focus-nfe) pra testar antes de integrar de verdade. **Sem taxa de setup e sem tempo mínimo de contrato** — cancela sem multa se não fizer sentido. Preço exato por nota/mês não veio na busca pública; isso sim precisa de contato comercial ou checar `focusnfe.com.br/precos/` direto.

Sources:
- [TecDoc Catalogue – TecAlliance do Brasil](https://tecalliance.com.br/tecdoc-catalogue/)
- [TECDOC CATALOGUE BRASIL PREMIUM (busca por placa e chassi) – plano anual](https://tecalliance.com.br/produto/tecdoc-catalogue-brasil-premium/)
- [TecDoc disponibiliza acesso a catálogo eletrônico de peças - Revista O Mecânico](https://omecanico.com.br/tecdoc-disponibiliza-acesso-a-catalogo-eletronico-de-pecas/)

---

## Confirmação — Bling e Tiny têm escrita, não só leitura (2026-09-02)

Pergunta que motivou a checagem: o Agente de Transcrição consegue **gerar descrição/preço e gravar o produto direto na plataforma que a loja já usa** (Bling/Tiny), sem precisar de sistema paralelo da Kronos?

**✅ Confirmado — os dois suportam escrita:**
- **Bling API v3:** `POST /produtos` cria produto novo diretamente.
- **Tiny API:** endpoint "Alterar Produto" (edita cadastro) + endpoint específico "Atualizar Estoque" (separado, só pra quantidade).

Isso fecha tecnicamente o fluxo do Agente de Transcrição (Fase 2): foto → OCR do código → cruza no TecDoc → sugere descrição/preço/compatibilidade → grava via API do Bling/Tiny — sem inventar plataforma nova.

**Em aberto:** a regra de precificação (custo + margem fixa? olhar preço de peça parecida?) ainda não foi definida — depende do que a loja real usar como critério, é pergunta de diagnóstico, não de pesquisa.

Sources:
- [API Pública do Bling](https://www.bling.com.br/api-bling)
- [Alterar Produto — API Tiny](https://tiny.com.br/api-docs/api2-produtos-alterar)
- [Atualizar Estoque do Produto — API Tiny](https://tiny.com.br/api-docs/api2-produtos-atualizar-estoque)

---

## Próxima ação real

Contato comercial com Focus NFe (ou NFE.io) e com TecAlliance Brasil pra confirmar: (1) se a licença TecDoc dá acesso via API, (2) preço real de uso da API de NF-e por volume de nota/mês — nenhum dos dois foi confirmado além do que aparece no site público.
