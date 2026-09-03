# Protótipo — Agente Estoque + Fornecedores (Fase 1)

**Dados 100% fictícios.** Não é loja real, não é fornecedor real, não é preço real — serve só pra provar que o desenho da Fase 1 (ver `../README.md`) funciona antes de conectar num PDV/ERP de verdade.

## O que faz

1. `seed_dados_ficticios.py` cria `estoque.db` (SQLite) com 12 peças fictícias de autopeças.
2. `agente_estoque.py` lê o banco e:
   - Detecta **ruptura** (quantidade ≤ mínimo).
   - Detecta **capital parado** (sem venda há 90+ dias, calcula valor parado).
   - Cruza cada peça em ruptura com `fornecedores_mock.json` (principal + alternativo, categoria original/paralela/similar).
   - Formata tudo no texto que iria pro WhatsApp do dono.

## Como rodar

```bash
python3 seed_dados_ficticios.py   # roda uma vez, cria o banco
python3 agente_estoque.py         # roda toda vez que quiser ver o alerta
```

## O que isso prova

- A lógica de ruptura/capital parado funciona com SQLite puro (sem dependência externa).
- O formato de saída (ruptura + fornecedor comparado + capital parado) é exatamente o desenhado no README do projeto.
- **O Agente nunca decide compra sozinho** — a última linha da notificação reforça isso, e o script não tem nenhuma função de "comprar".

## O que isso NÃO prova ainda

- Não lê PDV/ERP real (Bling, Tiny) — os dados são inseridos à mão no seed.
- `fornecedores_mock.json` é preenchido à mão, não é busca real (isso seria o Agente Fornecedores de verdade, que pesquisa ao vivo).
- Não envia WhatsApp de verdade — só imprime o texto formatado.

## Próximo passo real

Trocar `seed_dados_ficticios.py` por uma leitura real via API do PDV/ERP de uma loja de verdade (depende do diagnóstico — ver `../LEADS.md`), e o `fornecedores_mock.json` por uma busca ao vivo (Mercado Livre + distribuidoras).
