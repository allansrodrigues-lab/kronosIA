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

**Leitura:** R$400/ano por licença é barato frente ao valor que resolve (é literalmente o dado que faltava pro Agente de Transcrição funcionar) — mas precisa confirmar se a licença dá acesso via **API** (pra automação) ou só via app/site (uso manual) antes de fechar. Isso muda se o agente consegue consultar programaticamente ou se vira um passo manual do balconista.

Sources:
- [TecDoc Catalogue – TecAlliance do Brasil](https://tecalliance.com.br/tecdoc-catalogue/)
- [TECDOC CATALOGUE BRASIL PREMIUM (busca por placa e chassi) – plano anual](https://tecalliance.com.br/produto/tecdoc-catalogue-brasil-premium/)
- [TecDoc disponibiliza acesso a catálogo eletrônico de peças - Revista O Mecânico](https://omecanico.com.br/tecdoc-disponibiliza-acesso-a-catalogo-eletronico-de-pecas/)

---

## Próxima ação real

Contato comercial com Focus NFe (ou NFE.io) e com TecAlliance Brasil pra confirmar: (1) se a licença TecDoc dá acesso via API, (2) preço real de uso da API de NF-e por volume de nota/mês — nenhum dos dois foi confirmado além do que aparece no site público.
