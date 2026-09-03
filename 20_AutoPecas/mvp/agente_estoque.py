"""Protótipo do Agente Estoque + Fornecedores (Fase 1), com dados FICTÍCIOS.

Faz o que o desenho do README.md descreve pra Fase 1:
  1. Checa ruptura (quantidade <= mínimo) e capital parado (sem venda há 90+ dias).
  2. Cruza cada item em ruptura com o Agente Fornecedores (aqui, dado mockado).
  3. Monta a notificação no formato que iria pro WhatsApp do dono.

Nunca decide compra sozinho — só apresenta. Rodar:
  python3 seed_dados_ficticios.py   (uma vez, cria o banco fictício)
  python3 agente_estoque.py
"""
import json
import sqlite3
from datetime import date

DB_PATH = "estoque.db"
FORNECEDORES_PATH = "fornecedores_mock.json"
DIAS_CAPITAL_PARADO = 90


def carregar_produtos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT * FROM produtos")
    produtos = [dict(row) for row in cur.fetchall()]
    conn.close()
    return produtos


def checar_ruptura(produtos):
    return [p for p in produtos if p["quantidade_atual"] <= p["estoque_minimo"]]


def checar_capital_parado(produtos):
    hoje = date.today()
    parados = []
    for p in produtos:
        ultima = date.fromisoformat(p["ultima_venda"])
        dias_parado = (hoje - ultima).days
        if dias_parado >= DIAS_CAPITAL_PARADO and p["quantidade_atual"] > 0:
            valor_parado = p["quantidade_atual"] * p["preco_custo"]
            parados.append({**p, "dias_parado": dias_parado, "valor_parado": valor_parado})
    return parados


def buscar_fornecedores(sku, catalogo_fornecedores):
    return catalogo_fornecedores.get(sku, [])


def formatar_notificacao(ruptura, parados, catalogo_fornecedores):
    linhas = []
    linhas.append("🔔 *Alerta do Agente — Estoque*\n")

    if ruptura:
        linhas.append(f"*{len(ruptura)} peça(s) precisam de reposição:*\n")
        for p in ruptura:
            linhas.append(f"⚠️ *{p['nome']}* ({p['sku']}) — {p['quantidade_atual']} em estoque, mínimo é {p['estoque_minimo']}")
            opcoes = buscar_fornecedores(p["sku"], catalogo_fornecedores)
            if opcoes:
                for op in opcoes:
                    tag = "✅ principal" if op["tipo"] == "principal" else "· alternativo"
                    linhas.append(
                        f"   {tag} — {op['fornecedor']} · R$ {op['preco']:.2f} · "
                        f"{op['prazo_dias']}d · {op['categoria_peca']}"
                    )
            else:
                linhas.append("   (Agente Fornecedores ainda não pesquisou este item)")
            linhas.append("")
    else:
        linhas.append("Nenhuma peça em ruptura hoje.\n")

    if parados:
        total_parado = sum(p["valor_parado"] for p in parados)
        linhas.append(f"*{len(parados)} item(ns) com capital parado (sem venda há {DIAS_CAPITAL_PARADO}+ dias):*\n")
        for p in parados:
            linhas.append(
                f"🐢 *{p['nome']}* — {p['quantidade_atual']} un. parada(s) há {p['dias_parado']} dias "
                f"(R$ {p['valor_parado']:.2f} de capital parado)"
            )
        linhas.append(f"\n💰 Total parado: R$ {total_parado:.2f}")
    else:
        linhas.append("Nenhum item com capital parado no momento.")

    linhas.append("\n_O Agente não compra sozinho — essas são só as opções pra você aprovar._")
    return "\n".join(linhas)


def main():
    produtos = carregar_produtos()
    with open(FORNECEDORES_PATH, encoding="utf-8") as f:
        catalogo_fornecedores = json.load(f)

    ruptura = checar_ruptura(produtos)
    parados = checar_capital_parado(produtos)

    print(formatar_notificacao(ruptura, parados, catalogo_fornecedores))


if __name__ == "__main__":
    main()
