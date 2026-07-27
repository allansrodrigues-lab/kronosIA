# -*- coding: utf-8 -*-
"""Converte o documento tecnico do Ferrao (markdown) em PDF, com os desenhos SVG embutidos.

Mini-parser de markdown -> ReportLab. Cobre: headers, tabelas, listas, blocos de codigo,
citacoes, imagens SVG, negrito/italico/code inline.
"""
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Preformatted, Spacer, Table, TableStyle, PageBreak)
from svglib.svglib import svg2rlg

NAVY = colors.HexColor('#1e2a4a')
AZUL = colors.HexColor('#3b82f6')
CINZA = colors.HexColor('#64748b')
CINZA_CLARO = colors.HexColor('#f1f5f9')
LINHA = colors.HexColor('#cbd5e1')
TEXTO = colors.HexColor('#334155')

W, H = A4
MARG = 16 * mm
LARG_UTIL = W - 2 * MARG

S = {
    'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=22, textColor=NAVY,
                         leading=26, spaceAfter=4),
    'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=14, textColor=NAVY,
                         leading=18, spaceBefore=14, spaceAfter=6),
    'h3': ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=11, textColor=AZUL,
                         leading=14, spaceBefore=9, spaceAfter=4),
    'p': ParagraphStyle('p', fontName='Helvetica', fontSize=9.3, textColor=TEXTO,
                        leading=13, spaceAfter=6),
    'li': ParagraphStyle('li', fontName='Helvetica', fontSize=9.3, textColor=TEXTO,
                         leading=13, spaceAfter=3, leftIndent=10, bulletIndent=2),
    'quote': ParagraphStyle('quote', fontName='Helvetica-Oblique', fontSize=9.6, textColor=NAVY,
                            leading=13.5, spaceAfter=6, leftIndent=8, borderPadding=6,
                            backColor=colors.HexColor('#eff6ff')),
    'cap': ParagraphStyle('cap', fontName='Helvetica-Oblique', fontSize=8.2, textColor=CINZA,
                          leading=11, spaceAfter=8, alignment=1),
    'cel': ParagraphStyle('cel', fontName='Helvetica', fontSize=7.6, textColor=TEXTO, leading=9.8),
    'celh': ParagraphStyle('celh', fontName='Helvetica-Bold', fontSize=7.6,
                           textColor=colors.white, leading=9.8),
    'code': ParagraphStyle('code', fontName='Courier', fontSize=6.6,
                           textColor=colors.HexColor('#1e293b'), leading=8.2),
}


def inline(t):
    """Converte marcacao inline de markdown para as tags do ReportLab."""
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', t)
    t = re.sub(r'`([^`]+?)`', r'<font face="Courier" size="8">\1</font>', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)   # links viram texto
    # simbolos que a fonte padrao nao tem
    for k, v in [('⚠️', '[!] '), ('⭐', '* '), ('🤖', ''), ('→', '-&gt;'), ('►', '&gt;'),
                 ('✅', '[ok] '), ('≈', '~'), ('·', '-'), ('—', '-'), ('–', '-'),
                 ('“', '"'), ('”', '"'), ('‘', "'"), ('’', "'"), ('…', '...'),
                 ('½', '1/2'), ('⅓', '1/3'), ('×', 'x'), ('┌', '+'), ('└', '+'),
                 ('┐', '+'), ('┘', '+'), ('│', '|'), ('─', '-'), ('├', '+'), ('┤', '+')]:
        t = t.replace(k, v)
    return t


def larguras(linhas_tab):
    """Distribui a largura proporcional ao tamanho medio do texto de cada coluna."""
    n = len(linhas_tab[0])
    pesos = []
    for c in range(n):
        m = max(len(l[c]) for l in linhas_tab)
        med = sum(len(l[c]) for l in linhas_tab) / float(len(linhas_tab))
        pesos.append(max(6.0, (m * 0.35 + med * 0.65)) ** 0.72)
    tot = sum(pesos)
    ws = [LARG_UTIL * p / tot for p in pesos]
    minimo = 13 * mm
    # garante largura minima sem estourar o total
    falta = sum(minimo - w for w in ws if w < minimo)
    if falta > 0:
        sobra_idx = [i for i, w in enumerate(ws) if w > minimo]
        total_sobra = sum(ws[i] - minimo for i in sobra_idx)
        for i in sobra_idx:
            ws[i] -= falta * (ws[i] - minimo) / total_sobra
        ws = [max(w, minimo) for w in ws]
    return ws


def montar_tabela(bloco):
    linhas = []
    for ln in bloco:
        if re.match(r'^\|[\s:\-|]+\|$', ln.strip()):
            continue
        cels = [c.strip() for c in ln.strip().strip('|').split('|')]
        linhas.append(cels)
    if not linhas:
        return None
    n = max(len(l) for l in linhas)
    linhas = [l + [''] * (n - len(l)) for l in linhas]

    ws = larguras(linhas)
    data = [[Paragraph(inline(c), S['celh']) for c in linhas[0]]]
    for l in linhas[1:]:
        data.append([Paragraph(inline(c), S['cel']) for c in l])
    t = Table(data, colWidths=ws, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('GRID', (0, 0), (-1, -1), 0.4, LINHA),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
    ]))
    return t


ALTURA_UTIL = H - 42 * mm   # espaco vertical real do frame, com folga de seguranca


def desenho(caminho, largura_max):
    d = svg2rlg(caminho)
    if d is None:
        return None
    # escala pela largura E pela altura: um desenho alto nao pode estourar a pagina
    esc = min(largura_max / d.width, ALTURA_UTIL / d.height, 1.9)
    d.width *= esc
    d.height *= esc
    d.scale(esc, esc)
    d.hAlign = 'CENTER'
    return d


def converter(md_path, pdf_path, titulo):
    base = os.path.dirname(md_path)
    with open(md_path, encoding='utf-8') as f:
        linhas = f.read().split('\n')

    story = []
    i = 0
    while i < len(linhas):
        ln = linhas[i]
        s = ln.strip()

        if not s:
            i += 1
            continue

        # bloco de codigo
        if s.startswith('```'):
            i += 1
            buf = []
            while i < len(linhas) and not linhas[i].strip().startswith('```'):
                buf.append(linhas[i][:150])
                i += 1
            i += 1
            txt = '\n'.join(buf)
            for k, v in [('→', '->'), ('►', '>'), ('◄', '<'), ('│', '|'), ('─', '-'),
                         ('┌', '+'), ('┐', '+'), ('└', '+'), ('┘', '+'), ('├', '+'),
                         ('┤', '+'), ('┬', '+'), ('┴', '+'), ('─', '-'), ('•', '*')]:
                txt = txt.replace(k, v)
            p = Preformatted(txt, S['code'])
            tb = Table([[p]], colWidths=[LARG_UTIL])
            tb.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('BOX', (0, 0), (-1, -1), 0.5, LINHA),
                ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(tb)
            story.append(Spacer(1, 7))
            continue

        # tabela
        if s.startswith('|'):
            buf = []
            while i < len(linhas) and linhas[i].strip().startswith('|'):
                buf.append(linhas[i])
                i += 1
            t = montar_tabela(buf)
            if t:
                story.append(t)
                story.append(Spacer(1, 8))
            continue

        # imagem
        m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)', s)
        if m:
            arq = os.path.join(base, m.group(2))
            if os.path.exists(arq):
                d = desenho(arq, LARG_UTIL)
                if d is not None:
                    story.append(PageBreak())
                    story.append(d)
                    story.append(Spacer(1, 4))
            i += 1
            continue

        # separador
        if s in ('---', '***', '___'):
            story.append(Spacer(1, 5))
            i += 1
            continue

        # headers
        if s.startswith('### '):
            story.append(Paragraph(inline(s[4:]), S['h3']))
            i += 1
            continue
        if s.startswith('## '):
            story.append(Paragraph(inline(s[3:]), S['h2']))
            i += 1
            continue
        if s.startswith('# '):
            story.append(Paragraph(inline(s[2:]), S['h1']))
            i += 1
            continue

        # citacao
        if s.startswith('> '):
            buf = []
            while i < len(linhas) and linhas[i].strip().startswith('> '):
                buf.append(linhas[i].strip()[2:])
                i += 1
            story.append(Paragraph(inline(' '.join(buf)), S['quote']))
            story.append(Spacer(1, 3))
            continue

        # lista
        if re.match(r'^[-*] ', s) or re.match(r'^\d+\. ', s):
            while i < len(linhas) and (re.match(r'^\s*[-*] ', linhas[i])
                                       or re.match(r'^\s*\d+\. ', linhas[i])):
                item = linhas[i].strip()
                item = re.sub(r'^[-*] ', '', item)
                item = re.sub(r'^\d+\. ', '', item)
                story.append(Paragraph(inline(item), S['li'], bulletText='\u2022'))
                i += 1
            story.append(Spacer(1, 4))
            continue

        # legenda em italico (linha inteira entre asteriscos)
        if s.startswith('*') and s.endswith('*') and not s.startswith('**'):
            story.append(Paragraph(inline(s.strip('*')), S['cap']))
            i += 1
            continue

        # paragrafo
        story.append(Paragraph(inline(s), S['p']))
        i += 1

    def rodape(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINHA)
        canvas.setLineWidth(0.5)
        canvas.line(MARG, 12 * mm, W - MARG, 12 * mm)
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(CINZA)
        canvas.drawString(MARG, 8 * mm, 'Projeto Ferrao - robo humanoide de sucata')
        canvas.drawRightString(W - MARG, 8 * mm, 'Pagina %d' % doc.page)
        canvas.restoreState()

    doc = BaseDocTemplate(pdf_path, pagesize=A4, leftMargin=MARG, rightMargin=MARG,
                          topMargin=14 * mm, bottomMargin=18 * mm,
                          title=titulo, author='Allan Rodrigues')
    frame = Frame(MARG, 18 * mm, LARG_UTIL, H - 32 * mm, id='f')
    doc.addPageTemplates([PageTemplate(id='p', frames=[frame], onPage=rodape)])
    doc.build(story)
    print('OK ->', pdf_path)


if __name__ == '__main__':
    converter(sys.argv[1], sys.argv[2],
              sys.argv[3] if len(sys.argv) > 3 else 'Projeto Ferrao')
