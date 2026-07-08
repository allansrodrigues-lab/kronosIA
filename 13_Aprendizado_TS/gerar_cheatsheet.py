# -*- coding: utf-8 -*-
"""
Gera um PDF "Cola de Bolso" de programação para o Allan imprimir e carregar.
Duas tabelas: (1) Símbolos & Sintaxe (JS/n8n)  (2) Nomes Técnicos & Conceitos.
Rodar:  uv run --with reportlab python gerar_cheatsheet.py
Ancorado na analogia do hortifruti: cada símbolo tem nome e função, como cada código era uma fruta.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                Spacer, HRFlowable)

NAVY = colors.HexColor("#1B2A4A")
GOLD = colors.HexColor("#B8863B")
LIGHT = colors.HexColor("#EEF1F6")
GREY = colors.HexColor("#5A6478")

styles = getSampleStyleSheet()
h_title = ParagraphStyle("t", parent=styles["Title"], textColor=NAVY, fontSize=19, spaceAfter=1)
h_sub = ParagraphStyle("s", parent=styles["Normal"], textColor=GREY, fontSize=8.5, leading=11, spaceAfter=4)
h_sec = ParagraphStyle("sec", parent=styles["Heading2"], textColor=NAVY, fontSize=11.5, spaceBefore=6, spaceAfter=3)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=7.6, leading=9, textColor=colors.HexColor("#222222"))
cell_code = ParagraphStyle("code", parent=cell, fontName="Courier-Bold", textColor=NAVY, fontSize=8)
cell_ex = ParagraphStyle("ex", parent=cell, fontName="Courier", textColor=GREY, fontSize=7.2)
foot = ParagraphStyle("foot", parent=styles["Normal"], fontSize=8.5, textColor=GOLD, alignment=1)


def P(txt, st=cell):
    return Paragraph(txt, st)


def make_table(rows, headers, widths, code_col=0, ex_col=None):
    data = [[P(h, ParagraphStyle("hh", parent=cell, textColor=colors.white,
             fontName="Helvetica-Bold", fontSize=9)) for h in headers]]
    for r in rows:
        line = []
        for i, c in enumerate(r):
            if i == code_col:
                line.append(P(c, cell_code))
            elif ex_col is not None and i == ex_col:
                line.append(P(c, cell_ex))
            else:
                line.append(P(c, cell))
        data.append(line)
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD2DF")),
        ("BOX", (0, 0), (-1, -1), 0.6, NAVY),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(style))
    return t


# ---------- TABELA 1: SÍMBOLOS & SINTAXE ----------
simbolos = [
    ["[ ]", "Array (lista / colchetes)", "Lista de itens em ordem. Conta do ZERO.", 'frutas[0]'],
    ["{ }", "Object (objeto / chaves)", "Ficha com campos chave: valor.", '{nome: "Léa"}'],
    ["( )", "Parênteses", "Chama/executa algo ou agrupa.", 'enviar(msg)'],
    ['" "  \' \'', "String (aspas)", "Texto puro.", '"batata"'],
    [".", "Ponto (acesso)", "Entra numa propriedade do objeto.", 'cliente.nome'],
    ["=", "Atribuição", "Guarda um valor numa variável.", 'let n = 77'],
    ["===", "Igualdade estrita", "Compara valor E tipo (== é frouxo).", 'a === b'],
    ["=>", "Arrow function (seta)", "Função curtinha.", 'x => x * 2'],
    ["?.", "Optional chaining", "Acessa SÓ se existir (não quebra).", 'dado?.texto'],
    ["??", "Nullish coalescing", "Valor padrão se estiver vazio/null.", 'nome ?? "-"'],
    ["//", "Comentário", "Nota pra humano; o código ignora.", '// lembrete'],
    ["&&  ||", "E / OU lógicos", "Combina condições (e / ou).", 'ativo && pago'],
    ["!", "Negação (not)", "Inverte: verdadeiro vira falso.", '!ativo'],
    ["+", "Soma / concatena", "Soma números ou junta textos.", '"oi " + nome'],
    [";", "Ponto e vírgula", "Marca o fim de uma instrução.", 'let x = 5;'],
    ["\\n", "Escape de nova linha", "Quebra linha dentro do texto.", '"l1\\nl2"'],
    ["$('Nó')", "Referência (n8n)", "Pega dados de outro nó do fluxo.", "$('Normalizar')"],
    ["{{ }}", "Expressão (n8n)", "Código dentro de um campo do nó.", '{{ $json.texto }}'],
]

# ---------- TABELA 2: NOMES TÉCNICOS & CONCEITOS ----------
conceitos = [
    ["Variável", "Caixa etiquetada que guarda um valor.", "let preço = 77"],
    ["Função", "Máquina: recebe algo, devolve outro.", "somar(a, b)"],
    ["Array / Lista", "Fila de itens em ordem (índice do 0).", "content[0]"],
    ["Objeto / JSON", "Ficha com campos (chave → valor).", "resposta da IA"],
    ["String / Boolean", "Texto puro / verdadeiro-falso.", 'fromMe: false'],
    ["Parser", "Traduz texto bruto em dado organizado.", "o bug do { }"],
    ["Payload", "O 'pacote' de dados que chega.", "msg do WhatsApp"],
    ["Webhook", "Campainha: avisa quando algo chega.", "Evolution → n8n"],
    ["API", "Balcão de atendimento entre 2 sistemas.", "Anthropic, Evolution"],
    ["Buffer / Debounce", "Esperar terminar de falar pra agir.", "Léa juntando msgs"],
    ["Aggregator pattern", "Juntar vários pedaços num só.", "o buffer"],
    ["Race condition", "Dois processos se atropelando.", "'à prova de corrida'"],
    ["Timeout", "Tempo-limite de espera.", "30s nas chamadas"],
    ["Loop", "Repetir a mesma ação pra cada item.", "for (x of lista)"],
    ["Thinking (LLM)", "A IA 'pensa' antes de responder.", "Sonnet 5"],
]


def build():
    doc = SimpleDocTemplate(
        "cheatsheet_programacao.pdf", pagesize=A4,
        topMargin=9 * mm, bottomMargin=8 * mm,
        leftMargin=12 * mm, rightMargin=12 * mm,
        title="Cola de Bolso - Programação")
    W = A4[0] - 28 * mm
    flow = []
    flow.append(Paragraph("Cola de Bolso — Programação", h_title))
    flow.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=6))
    flow.append(Paragraph(
        'Cada símbolo tem um <b>nome</b> e uma <b>função</b> — igual quando cada código era uma fruta '
        'no hortifruti ("batata 77"). Você não decora: você associa, vendo todos os dias. '
        'Leia sem pressa. <i>Um pouco por vez, só não parar.</i>', h_sub))

    flow.append(Paragraph("1 · Símbolos &amp; Sintaxe (o que aparece nos Code nodes)", h_sec))
    flow.append(make_table(
        simbolos,
        ["Símbolo", "Nome técnico", "O que faz", "Exemplo"],
        [W * 0.16, W * 0.26, W * 0.36, W * 0.22],
        code_col=0, ex_col=3))

    flow.append(Paragraph("2 · Nomes Técnicos &amp; Conceitos (os que a gente usou de verdade)", h_sec))
    flow.append(make_table(
        conceitos,
        ["Conceito", "O que é (na prática)", "Onde a gente viu"],
        [W * 0.24, W * 0.50, W * 0.26],
        code_col=-99, ex_col=2))

    flow.append(Spacer(1, 8))
    flow.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=4))
    flow.append(Paragraph("Kronos Intelligence · feito pro Allan carregar no bolso · dirigir a IA é a competência", foot))
    doc.build(flow)
    print("PDF gerado: cheatsheet_programacao.pdf")


if __name__ == "__main__":
    build()
