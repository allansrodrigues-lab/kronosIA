"""Cria estoque.db com dados FICTÍCIOS de uma loja de autopeças.

Nenhum dado aqui é real — é só pra provar que o Agente Estoque funciona
antes de conectar num PDV/ERP de verdade. Rodar: python3 seed_dados_ficticios.py
"""
import sqlite3
from datetime import date, timedelta

DB_PATH = "estoque.db"

produtos = [
    # nome, categoria, sku, quantidade_atual, estoque_minimo, preco_custo, preco_venda, dias_desde_ultima_venda, fornecedor_principal
    ("Pastilha de freio dianteira - Onix",   "Freio",     "PF-ONX-001", 2,  5,  45.00, 89.90,   3,  "Bosch"),
    ("Filtro de óleo - Gol G5/G6",           "Filtro",    "FO-GOL-014", 18, 10, 12.00, 24.90,   7,  "Tecfil"),
    ("Óleo motor 5W30 sintético 1L",         "Fluído",    "OL-5W30-001",4,  8,  22.00, 41.90,   1,  "Mobil"),
    ("Vela de ignição - Corolla",            "Ignição",   "VI-COR-002", 30, 12, 9.50,  22.00,   40, "NGK"),
    ("Amortecedor traseiro - HB20",          "Suspensão", "AM-HB20-003",1,  3,  180.00,349.90,  5,  "Cofap"),
    ("Correia dentada - Uno/Palio",          "Motor",     "CD-UNO-005", 22, 6,  38.00, 79.90,   150,"Gates"),
    ("Bateria 60Ah",                         "Elétrica",  "BAT-60A-001",6,  4,  210.00,399.90,  2,  "Moura"),
    ("Disco de freio dianteiro - Civic",     "Freio",     "DF-CIV-004", 3,  5,  95.00, 189.90,  8,  "Fremax"),
    ("Lâmpada farol H4",                     "Elétrica",  "LP-H4-001",  40, 15, 6.00,  15.90,   4,  "Philips"),
    ("Palheta limpador 20\"",                "Acessório", "PL-20-001",  12, 10, 14.00, 29.90,   120,"Bosch"),
    ("Filtro de ar - Hilux",                 "Filtro",    "FA-HLX-006", 5,  6,  32.00, 65.90,   200,"Tecfil"),
    ("Kit embreagem - Fiesta",               "Transmissão","KE-FST-001",1,  2,  280.00,549.90,  12, "Sachs"),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS produtos")
    cur.execute("""
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            quantidade_atual INTEGER NOT NULL,
            estoque_minimo INTEGER NOT NULL,
            preco_custo REAL NOT NULL,
            preco_venda REAL NOT NULL,
            ultima_venda TEXT NOT NULL,
            fornecedor_principal TEXT NOT NULL
        )
    """)

    hoje = date.today()
    linhas = [
        (nome, categoria, sku, qtd, minimo, custo, venda,
         (hoje - timedelta(days=dias)).isoformat(), fornecedor)
        for nome, categoria, sku, qtd, minimo, custo, venda, dias, fornecedor in produtos
    ]
    cur.executemany("""
        INSERT INTO produtos
        (nome, categoria, sku, quantidade_atual, estoque_minimo, preco_custo, preco_venda, ultima_venda, fornecedor_principal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, linhas)

    conn.commit()
    conn.close()
    print(f"estoque.db criado com {len(produtos)} produtos fictícios.")

if __name__ == "__main__":
    main()
