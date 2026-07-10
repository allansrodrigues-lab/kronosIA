# -*- coding: utf-8 -*-
"""
Catálogo de Serviços & Planos da Kronos Intelligence — PDF A4 p/ impressão/encadernação.
Usa a IDENTIDADE OFICIAL da Kronos: logo real (identidade_visual/), cores da landing
(#020c2a / #4a0e90 / #8898bb) e slogan oficial.

Rodar:  uv run --with reportlab --with pillow python gerar_catalogo_servicos.py
Saída:  Kronos_Catalogo_Servicos.pdf
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit, ImageReader
from PIL import Image, ImageChops

W, H = A4
MX = 52

# ---- Paleta OFICIAL Kronos (landing) ----
NAVY      = (0.008, 0.047, 0.165)   # #020c2a
NAVY_CARD = (0.043, 0.102, 0.227)   # #0b1a3a
NAVY_SOFT = (0.063, 0.133, 0.290)   # #10224a
VIO       = (0.290, 0.055, 0.565)   # #4a0e90 (accent em fundo claro)
VIO_L     = (0.651, 0.576, 0.847)   # #a693d8 (accent em fundo navy)
SILVER    = (0.914, 0.929, 0.965)   # texto claro sobre navy
CREAM     = (0.765, 0.796, 0.878)   # texto 2º sobre navy
CINZA     = (0.533, 0.596, 0.733)   # #8898bb
INK       = (0.043, 0.086, 0.188)   # texto escuro em fundo claro
GRAY      = (0.40, 0.44, 0.55)
GRAY_L    = (0.55, 0.60, 0.71)
LIGHT     = (0.965, 0.969, 0.984)
CARD      = (0.925, 0.937, 0.961)
LINE      = (0.847, 0.863, 0.910)
WHITE     = (1, 1, 1)

IDV = "identidade_visual"
ASSETS = "_assets_cat"
os.makedirs(ASSETS, exist_ok=True)


def autocrop(src, dst, pad=14, tol=20):
    """Recorta as sobras (transparência ou fundo sólido) do logo."""
    im = Image.open(src).convert("RGBA")
    alpha = im.split()[3]
    bbox = alpha.getbbox()
    solid = (bbox is None) or (bbox[2] - bbox[0] > im.width * 0.985)
    if solid:
        rgb = im.convert("RGB")
        bg = rgb.getpixel((2, 2))
        diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, bg)).convert("L")
        bbox = diff.point(lambda p: 255 if p > tol else 0).getbbox()
    crop = im.crop(bbox)
    out = Image.new("RGBA", (crop.width + 2 * pad, crop.height + 2 * pad), (0, 0, 0, 0))
    out.paste(crop, (pad, pad), crop)
    out.save(dst)
    return dst


LOGO_LIGHT = autocrop(f"{IDV}/kronos_logo_oficial_claro.png", f"{ASSETS}/logo_light.png")      # navy s/ claro
LOGO_DARK  = autocrop(f"{IDV}/kronos_logo_oficial_transparente.png", f"{ASSETS}/logo_dark.png")  # prata s/ escuro
_ldim = {p: Image.open(p).size for p in (LOGO_LIGHT, LOGO_DARK)}

# ---- fontes (tenta Inter, cai p/ Helvetica) ----
FONT, FONT_B = "Helvetica", "Helvetica-Bold"
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for cand in [r"C:\Windows\Fonts\Inter-Regular.ttf", "Inter-Regular.ttf"]:
        if os.path.exists(cand):
            pdfmetrics.registerFont(TTFont("Inter", cand))
            pdfmetrics.registerFont(TTFont("Inter-B", cand.replace("Regular", "Bold")))
            FONT, FONT_B = "Inter", "Inter-B"
            break
except Exception:
    pass

c = canvas.Canvas("Kronos_Catalogo_Servicos.pdf", pagesize=A4)
c.setTitle("Kronos Intelligence — Catálogo de Serviços & Planos")
c.setAuthor("Kronos Intelligence")
SLOGAN = "Inteligência que automatiza. Resultado que transforma."


# ---------- helpers ----------
def rect(x, y, w, h, color, radius=0):
    c.setFillColorRGB(*color)
    if radius:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)
    else:
        c.rect(x, y, w, h, fill=1, stroke=0)


def circle(x, y, r, color):
    c.setFillColorRGB(*color)
    c.circle(x, y, r, fill=1, stroke=0)


def para(x, y, s, size=10, color=INK, font=None, width=W - 2 * MX, leading=None):
    font = font or FONT
    leading = leading or size * 1.5
    c.setFillColorRGB(*color)
    c.setFont(font, size)
    for ln in simpleSplit(s, font, size, width):
        c.drawString(x, y, ln)
        y -= leading
    return y


def logo(path, x, y, target_h, anchor="left"):
    iw, ih = _ldim[path]
    w = target_h * iw / ih
    if anchor == "center":
        x -= w / 2
    elif anchor == "right":
        x -= w
    c.drawImage(ImageReader(path), x, y, w, target_h, mask="auto", preserveAspectRatio=True)
    return w


def footer(pagenum, label):
    c.setFillColorRGB(*GRAY_L)
    c.setFont(FONT, 8)
    c.drawString(MX, 30, "Kronos Intelligence")
    c.drawCentredString(W / 2, 30, label)
    c.drawRightString(W - MX, 30, str(pagenum))
    c.setStrokeColorRGB(*LINE)
    c.setLineWidth(0.6)
    c.line(MX, 42, W - MX, 42)


def page_header(kicker, title):
    rect(0, 0, W, H, LIGHT)
    rect(0, H - 3, W, 3, VIO)
    logo(LOGO_LIGHT, W - MX, H - 84, 40, anchor="right")
    c.setFillColorRGB(*VIO)
    c.setFont(FONT_B, 10)
    c.drawString(MX, H - 70, kicker.upper())
    c.setFillColorRGB(*INK)
    c.setFont(FONT_B, 24)
    c.drawString(MX, H - 98, title)
    c.setStrokeColorRGB(*LINE)
    c.setLineWidth(0.8)
    c.line(MX, H - 112, W - MX, H - 112)


# =====================================================================
# CAPA
# =====================================================================
rect(0, 0, W, H, NAVY)
rect(0, H - 5, W, 5, VIO)
logo(LOGO_DARK, W / 2, H - 250, 150, anchor="center")

c.setFillColorRGB(*CINZA)
c.setFont(FONT, 11)
c.drawCentredString(W / 2, H - 300, SLOGAN)

c.setFillColorRGB(*WHITE)
c.setFont(FONT_B, 40)
c.drawCentredString(W / 2, H / 2 - 70, "Catálogo de")
c.setFillColorRGB(*VIO_L)
c.drawCentredString(W / 2, H / 2 - 118, "Serviços & Planos")

c.setStrokeColorRGB(*NAVY_SOFT)
c.setLineWidth(1)
c.line(W / 2 - 120, H / 2 - 150, W / 2 + 120, H / 2 - 150)

para(MX + 40, H / 2 - 185,
     "Uma equipe de atendimento com Inteligência Artificial dentro do WhatsApp do seu "
     "negócio: conversa como gente, agenda, tira dúvidas, lembra, faz o pós-venda e cuida "
     "das tarefas chatas — 24 horas por dia.",
     size=12, color=CREAM, width=W - 2 * MX - 80, leading=19)

# rodapé capa
c.setFillColorRGB(*CINZA)
c.setFont(FONT, 9)
c.drawString(MX, 66, "kronosintelligence.com.br")
c.drawString(MX, 52, "WhatsApp (19) 97126-6736")
c.drawRightString(W - MX, 52, "Edição 2026")
c.showPage()

# =====================================================================
# PÁGINA 2 — Manifesto
# =====================================================================
page_header("Quem somos", "A Kronos em uma frase")
y = H - 150
y = para(MX, y,
         "Colocamos uma assistente de Inteligência Artificial dentro do WhatsApp do seu "
         "negócio. Ela atende como uma pessoa — entende texto e áudio, responde até por voz — "
         "e realmente resolve: agenda, tira dúvidas com base no seu catálogo, envia lembretes, "
         "conduz o pós-venda e ainda cuida de tarefas que tomam tempo do dono, como montar "
         "orçamento e emitir nota fiscal. Sem folga, sem esquecer, sem custo de mais um funcionário.",
         size=12, color=INK, leading=19)

y -= 18
cols = [
    ("Atende 24/7", "Nenhum cliente fica sem resposta — nem de madrugada, nem no fim de semana."),
    ("Fala como gente", "IA de última geração (Claude). Nada de menuzinho ';digite 1'. Conversa natural."),
    ("Resolve de verdade", "Não só responde: agenda, calcula, emite nota e registra tudo no seu CRM."),
]
cw = (W - 2 * MX - 2 * 16) / 3
for i, (t, d) in enumerate(cols):
    x = MX + i * (cw + 16)
    rect(x, y - 110, cw, 104, CARD, radius=10)
    circle(x + 20, y - 34, 5, VIO)
    c.setFillColorRGB(*INK)
    c.setFont(FONT_B, 12)
    c.drawString(x + 34, y - 38, t)
    para(x + 16, y - 60, d, size=9.5, color=GRAY, width=cw - 32, leading=13)

y -= 150
c.setFillColorRGB(*VIO)
c.setFont(FONT_B, 11)
c.drawString(MX, y, "COMO FUNCIONA")
y -= 26
steps = [
    ("1", "Cliente manda mensagem", "WhatsApp (texto, áudio ou documento)"),
    ("2", "A IA entende o pedido", "Classifica a intenção e busca no seu conteúdo"),
    ("3", "Age e responde", "Agenda, calcula, emite nota, escala p/ humano"),
    ("4", "Registra tudo", "Cada conversa e cada dado vão pro seu CRM"),
]
sw = (W - 2 * MX - 3 * 12) / 4
for i, (n, t, d) in enumerate(steps):
    x = MX + i * (sw + 12)
    rect(x, y - 96, sw, 90, NAVY, radius=10)
    c.setFillColorRGB(*VIO_L)
    c.setFont(FONT_B, 18)
    c.drawString(x + 14, y - 30, n)
    c.setFillColorRGB(*SILVER)
    c.setFont(FONT_B, 9.5)
    for j, ln in enumerate(simpleSplit(t, FONT_B, 9.5, sw - 24)):
        c.drawString(x + 14, y - 46 - j * 12, ln)
    c.setFillColorRGB(*CREAM)
    c.setFont(FONT, 7.8)
    for j, ln in enumerate(simpleSplit(d, FONT, 7.8, sw - 24)):
        c.drawString(x + 14, y - 74 - j * 10, ln)

footer(2, "Catálogo de Serviços & Planos")
c.showPage()

# =====================================================================
# PÁGINA 3 — Catálogo de serviços
# =====================================================================
page_header("O que entregamos", "Catálogo de serviços")
y = H - 138
para(MX, y,
     "A Kronos é uma plataforma, não um robô solto. Cada negócio ativa o conjunto de "
     "serviços que precisa — do essencial ao carro-chefe do seu setor.",
     size=11, color=GRAY, leading=16)

universais = [
    ("Atendimento 24h", "Recepção e dúvidas com IA, dia e noite."),
    ("Entende áudio", "Transcreve o áudio do cliente e responde."),
    ("Responde por voz", "Devolve em áudio quando o cliente prefere falar."),
    ("Agendamento", "Marca, remarca e cancela sozinho."),
    ("Lembrete automático", "Avisa 24h antes — corta faltas e no-shows."),
    ("Pós-venda", "Acompanha, coleta feedback e reativa cliente."),
    ("Emissão de nota fiscal", "Dispara a NF-e — a chatice que o dono odeia."),
    ("Qualificação de leads", "Filtra e organiza quem chega, registra no CRM."),
]
modulares = [
    ("Leitor de documentos / PDF", "Lê contratos, laudos, processos e resume."),
    ("Calculadora / orçamento", "Monta valores na hora, sem erro humano."),
    ("Parecer científico", "Checa a evidência por trás de um produto/serviço."),
    ("Relatório automático", "Envia o resumo do negócio toda semana."),
    ("Conteúdo recorrente", "Gera posts e e-mails prontos pra publicar."),
    ("Triagem de e-mail", "Prioriza a caixa de entrada e rascunha respostas."),
]


def service_grid(y, items, cols=2):
    gw = (W - 2 * MX - (cols - 1) * 14) / cols
    rowh = 46
    for i, (t, d) in enumerate(items):
        r, cc = divmod(i, cols)
        x = MX + cc * (gw + 14)
        yy = y - r * (rowh + 8)
        rect(x, yy - rowh, gw, rowh, CARD, radius=8)
        circle(x + 18, yy - 20, 4.5, VIO)
        c.setFillColorRGB(*INK)
        c.setFont(FONT_B, 10.5)
        c.drawString(x + 32, yy - 17, t)
        c.setFillColorRGB(*GRAY)
        c.setFont(FONT, 8.6)
        for j, ln in enumerate(simpleSplit(d, FONT, 8.6, gw - 44)):
            c.drawString(x + 32, yy - 31 - j * 10, ln)
    rows = (len(items) + cols - 1) // cols
    return y - rows * (rowh + 8)


y -= 34
c.setFillColorRGB(*VIO)
c.setFont(FONT_B, 11)
c.drawString(MX, y, "UNIVERSAIS  —  todo negócio usa")
y -= 22
y = service_grid(y, universais, cols=2)

y -= 10
c.setFillColorRGB(*VIO)
c.setFont(FONT_B, 11)
c.drawString(MX, y, "MODULARES  —  ativados conforme o setor")
y -= 30
y = service_grid(y, modulares, cols=2)

footer(3, "Catálogo de Serviços & Planos")
c.showPage()

# =====================================================================
# PÁGINA 4 — Matriz serviços x nichos
# =====================================================================
page_header("Por setor", "O que cada setor ativa")
y = H - 138
para(MX, y,
     "Os três setores abaixo já estão prontos e testados. Cada linha mostra o combo de "
     "serviços — e o círculo maior marca o carro-chefe daquele setor.",
     size=11, color=GRAY, leading=16)

cols_h = ["Setor", "24h", "Áudio", "Voz", "Agenda", "Lembr.", "Pós", "PDF", "Orçam.", "Parecer", "NF-e"]
rows = [
    ("Estética",       [1, 1, 1, 1, 1, 1, 0, 1, 2, 1]),
    ("Odonto",         [1, 1, 1, 1, 1, 1, 1, 1, 0, 1]),
    ("Advocacia",      [1, 1, 1, 1, 1, 1, 2, 1, 1, 1]),
    ("Imobiliária",    [1, 1, 0, 1, 1, 1, 1, 2, 0, 0]),
    ("Energia Solar",  [1, 1, 1, 1, 1, 0, 0, 2, 0, 0]),
    ("Clínica Médica", [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]),
]
tx = MX
ty = y - 40
tw = W - 2 * MX
first_col = 92
ncols = len(cols_h) - 1
col_w = (tw - first_col) / ncols
rowh = 40
headh = 30

rect(tx, ty - headh, tw, headh, NAVY, radius=6)
c.setFillColorRGB(*WHITE)
c.setFont(FONT_B, 9)
c.drawString(tx + 12, ty - headh + 11, cols_h[0])
c.setFont(FONT_B, 7.6)
for i in range(ncols):
    cx = tx + first_col + i * col_w + col_w / 2
    c.setFillColorRGB(*CREAM)
    c.drawCentredString(cx, ty - headh + 11, cols_h[i + 1])

for ri, (name, vals) in enumerate(rows):
    ry = ty - headh - (ri + 1) * rowh
    rect(tx, ry, tw, rowh, CARD if ri % 2 == 0 else WHITE)
    c.setFillColorRGB(*INK)
    c.setFont(FONT_B, 10.5)
    c.drawString(tx + 12, ry + rowh / 2 - 4, name)
    for i, v in enumerate(vals):
        cx = tx + first_col + i * col_w + col_w / 2
        cy = ry + rowh / 2
        if v == 1:
            circle(cx, cy, 4.5, VIO)
        elif v == 2:
            circle(cx, cy, 8.5, VIO)
            circle(cx, cy, 3.2, WHITE)
        else:
            c.setStrokeColorRGB(*GRAY_L)
            c.setLineWidth(1.4)
            c.line(cx - 4, cy, cx + 4, cy)
c.setStrokeColorRGB(*LINE)
c.setLineWidth(0.8)
c.rect(tx, ty - headh - len(rows) * rowh, tw, headh + len(rows) * rowh, fill=0, stroke=1)

# legenda
ly = ty - headh - len(rows) * rowh - 30
circle(tx + 6, ly + 3, 4.5, VIO)
c.setFillColorRGB(*GRAY); c.setFont(FONT, 9); c.drawString(tx + 18, ly, "serviço incluído")
circle(tx + 150, ly + 3, 8, VIO); circle(tx + 150, ly + 3, 3, WHITE)
c.drawString(tx + 164, ly, "carro-chefe do setor")
c.setStrokeColorRGB(*GRAY_L); c.setLineWidth(1.4); c.line(tx + 322, ly + 3, tx + 332, ly + 3)
c.drawString(tx + 342, ly, "não se aplica")

ny = ly - 40
rect(MX, ny - 54, tw, 50, NAVY_SOFT, radius=10)
c.setFillColorRGB(*VIO_L)
c.setFont(FONT_B, 10)
c.drawString(MX + 16, ny - 22, "Novos setores sob demanda")
para(MX + 16, ny - 38,
     "Nutrição, Fisioterapia, Psicologia, Contábil e Laboratórios usam a mesma base — "
     "montamos o setor sob medida a partir do combo que ele precisa.",
     size=9, color=CREAM, width=tw - 32, leading=12)

footer(4, "Catálogo de Serviços & Planos")
c.showPage()


# =====================================================================
# PÁGINAS 5-10 — Nichos detalhados
# =====================================================================
def nicho_page(pagenum, kicker, title, marca, assistentes, carro, faz, exemplo):
    page_header(kicker, title)
    y = H - 138
    rect(MX, y - 20, W - 2 * MX, 44, CARD, radius=8)
    c.setFillColorRGB(*GRAY); c.setFont(FONT, 8)
    c.drawString(MX + 14, y + 7, "MARCA-DEMONSTRAÇÃO")
    c.setFillColorRGB(*INK); c.setFont(FONT_B, 10.5)
    c.drawString(MX + 14, y - 9, marca)
    c.setFillColorRGB(*GRAY); c.setFont(FONT, 8)
    c.drawRightString(W - MX - 14, y + 7, "ASSISTENTE(S)")
    c.setFillColorRGB(*VIO); c.setFont(FONT_B, 10)
    c.drawRightString(W - MX - 14, y - 9, assistentes)

    y -= 56
    rect(MX, y - 74, W - 2 * MX, 68, NAVY, radius=12)
    c.setFillColorRGB(*VIO_L); c.setFont(FONT_B, 10)
    c.drawString(MX + 18, y - 24, "CARRO-CHEFE")
    c.setFillColorRGB(*WHITE); c.setFont(FONT_B, 13)
    c.drawString(MX + 18, y - 44, carro[0])
    para(MX + 18, y - 60, carro[1], size=9.5, color=CREAM, width=W - 2 * MX - 36, leading=12)

    y -= 100
    c.setFillColorRGB(*VIO); c.setFont(FONT_B, 11)
    c.drawString(MX, y, "O QUE A ASSISTENTE FAZ")
    y -= 24
    gw = (W - 2 * MX - 14) / 2
    for i, (t, d) in enumerate(faz):
        r, cc = divmod(i, 2)
        x = MX + cc * (gw + 14)
        yy = y - r * 56
        rect(x, yy - 50, gw, 50, CARD, radius=8)
        circle(x + 18, yy - 22, 4.5, VIO)
        c.setFillColorRGB(*INK); c.setFont(FONT_B, 10.5)
        c.drawString(x + 32, yy - 19, t)
        c.setFillColorRGB(*GRAY); c.setFont(FONT, 8.6)
        for j, ln in enumerate(simpleSplit(d, FONT, 8.6, gw - 44)):
            c.drawString(x + 32, yy - 33 - j * 10, ln)
    y -= ((len(faz) + 1) // 2) * 56 + 16

    c.setFillColorRGB(*VIO); c.setFont(FONT_B, 11)
    c.drawString(MX, y, "EXEMPLO DE CONVERSA")
    y -= 20
    bubble_w = W - 2 * MX - 120
    for who, msg in exemplo:
        lines = simpleSplit(msg, FONT, 9.5, bubble_w - 24)
        bh = 16 + len(lines) * 12
        if who == "cli":
            rect(MX, y - bh, bubble_w, bh, CARD, radius=10)
            c.setFillColorRGB(*GRAY); c.setFont(FONT_B, 7.5)
            c.drawString(MX + 12, y - 12, "CLIENTE")
            c.setFillColorRGB(*INK); c.setFont(FONT, 9.5)
            for j, ln in enumerate(lines):
                c.drawString(MX + 12, y - 26 - j * 12, ln)
        else:
            bx = W - MX - bubble_w
            rect(bx, y - bh, bubble_w, bh, NAVY, radius=10)
            c.setFillColorRGB(*VIO_L); c.setFont(FONT_B, 7.5)
            c.drawString(bx + 12, y - 12, "ASSISTENTE")
            c.setFillColorRGB(*SILVER); c.setFont(FONT, 9.5)
            for j, ln in enumerate(lines):
                c.drawString(bx + 12, y - 26 - j * 12, ln)
        y -= bh + 8

    footer(pagenum, "Catálogo de Serviços & Planos")
    c.showPage()


nicho_page(
    5, "Setor 1 — Clínicas de estética", "Estética",
    "Aurora Estética — clínica de demonstração",
    "Aurora · Bia · Clara · Diana",
    ("Parecer de eficácia + orçamento na hora",
     "Explica a ciência por trás de cada procedimento e monta o orçamento (avulso, pacote e PIX) "
     "no meio da conversa — o que mais gera confiança e fecha venda em estética."),
    [
        ("Atende e tira dúvidas 24h", "Sobre procedimentos, indicações e contraindicações."),
        ("Agenda e lembra", "Marca com a profissional certa e avisa 24h antes."),
        ("Orçamento instantâneo", "Avulso, pacote com desconto e opção no PIX."),
        ("Responde por voz", "Se o cliente manda áudio, ela responde em áudio."),
        ("Pós-procedimento", "Cuidados, feedback e reativação de pacote."),
        ("Emite a nota (NF-e)", "Dispara a nota fiscal do serviço automaticamente."),
    ],
    [
        ("cli", "Quanto custa uma limpeza de pele?"),
        ("bot", "A sessão avulsa sai R$ 220 (R$ 209 no PIX). No pacote de 6 fica "
                "R$ 1.120 — economia de R$ 200. Quer que eu veja um horário?"),
    ],
)

nicho_page(
    6, "Setor 2 — Advocacia", "Advocacia",
    "Ferraz & Nogueira Advogados — demonstração",
    "Léa (triagem)",
    ("Leitura de processos e documentos + cálculo de causa",
     "Lê petições, contratos e laudos em segundos, estima custos da ação e analisa a "
     "metodologia de uma perícia — o que libera horas do advogado."),
    [
        ("Triagem de casos 24h", "Acolhe, entende a situação e identifica a área do direito."),
        ("Lê documentos/PDF", "Resume petições, contratos e laudos periciais."),
        ("Estima custos", "Honorários (Tabela OAB) + sucumbência + custas."),
        ("Análise de perícia", "Aponta fragilidades e sugere quesitos."),
        ("Agenda a consulta", "Presencial ou online, com o especialista certo."),
        ("NF-e de honorários", "Emite a nota do serviço jurídico."),
    ],
    [
        ("cli", "Fui demitido sem justa causa, quanto fica uma ação de 50 mil?"),
        ("bot", "Compreendo, senhor. É uma rescisão trabalhista — área do Dr. Ferraz. "
                "A estimativa fica entre R$ 6 mil e R$ 12 mil. Posso agendar a consulta?"),
    ],
)

nicho_page(
    7, "Setor 3 — Odontologia", "Odonto",
    "OdontoVita — clínica de demonstração",
    "Recepção · Bia · Clara",
    ("Orçamento de procedimentos + leitura de raio-x/documentos",
     "Monta o orçamento do tratamento na hora e lê exames e documentos enviados — "
     "acelerando o fechamento de procedimentos de ticket mais alto."),
    [
        ("Atende e agenda 24h", "Marca avaliação e procedimentos sem fila."),
        ("Orçamento na hora", "Do procedimento simples ao tratamento completo."),
        ("Lê documentos/raio-x", "Recebe e organiza exames enviados pelo paciente."),
        ("Lembrete de consulta", "Reduz faltas com aviso 24h antes."),
        ("Pós-atendimento", "Cuidados e retorno de manutenção."),
        ("Emite a nota (NF-e)", "Nota fiscal do procedimento automática."),
    ],
    [
        ("cli", "Vocês fazem clareamento? Quanto fica?"),
        ("bot", "Fazemos! O clareamento a laser sai R$ 890, em até 3x. "
                "Quer agendar uma avaliação gratuita pra confirmar?"),
    ],
)

nicho_page(
    8, "Setor 4 — Imobiliárias e corretores", "Imobiliária",
    "Schalletti Imóveis — imobiliária de demonstração",
    "Sofia",
    ("Simulação de financiamento + match automático com a carteira",
     "Calcula entrada, parcela e prazo (tabela Price/SAC) na conversa e cruza o perfil do "
     "cliente com os imóveis disponíveis — acelera a conversão de lead pra visita."),
    [
        ("Qualifica o lead 24h", "Comprar ou alugar, região, faixa de preço e nº de quartos."),
        ("Match com a carteira", "Envia as 2-3 opções mais aderentes, com foto e ficha."),
        ("Simula financiamento", "Entrada, parcela e prazo (Price/SAC) na hora."),
        ("Agenda e faz follow-up", "Marca a visita com o corretor e pergunta depois o que achou."),
        ("Responde por voz", "Entende e responde áudio na conversa."),
        ("Lê ficha e contrato (PDF)", "Extrai pontos-chave e sinaliza o que precisa de atenção."),
    ],
    [
        ("cli", "Vi um apê de 2 quartos no Cambuí, ainda tá disponível?"),
        ("bot", "Encontrei uma opção que combina com você: SCH-001 — Cambuí, 2 quartos, "
                "74m², R$ 690.000. Quer que eu simule o financiamento ou já agende uma visita?"),
    ],
)

nicho_page(
    9, "Setor 5 — Instaladoras de energia solar", "Energia Solar",
    "Zênite Energia Solar — instaladora de demonstração",
    "Helena",
    ("Cálculo de payback real, nunca chuta",
     "Calcula número de placas, investimento e economia mensal na conversa a partir do valor "
     "da conta de luz (ou foto dela) — sem esperar dias pelo orçamento do concorrente."),
    [
        ("Qualifica o lead 24h", "Valor da conta, tipo de imóvel e fase da rede."),
        ("Calcula payback na hora", "Placas, investimento e economia mensal, com número real."),
        ("Lê foto da conta de luz", "Confirma o valor médio sem precisar digitar nada."),
        ("Agenda a visita técnica", "Marca grátis e confirma na véspera."),
        ("Atende por ligação de voz", "Calcula a simulação e agenda tudo na mesma ligação."),
        ("Responde na hora", "Dia e noite, sem esperar o vendedor humano."),
    ],
    [
        ("cli", "Minha conta de luz vem uns R$ 480 por mês, vale a pena energia solar?"),
        ("bot", "Prontinho! Sistema de 11 placas (6,0 kWp). Investimento estimado R$ 18.000, "
                "economia de R$ 734/mês. Se paga em 2 anos e 1 mês!"),
    ],
)

nicho_page(
    10, "Setor 6 — Clínicas médicas", "Clínica Médica",
    "Cedro Saúde — clínica de demonstração",
    "Vera",
    ("Triagem de urgência que não depende da IA",
     "Um filtro determinístico (não é a IA que decide) identifica sinais de urgência — dor "
     "no peito, falta de ar, sinais de AVC — orienta o SAMU 192 e aciona a equipe na hora, "
     "antes de qualquer conversa com o robô."),
    [
        ("Consentimento LGPD antes de tudo", "Pede o aceite antes de coletar qualquer dado, com data/hora."),
        ("Triagem de urgência automática", "Filtro determinístico escala pra equipe, sem depender da IA."),
        ("Zero diagnóstico pelo bot", "Dúvida sobre sintoma vira consulta agendada, nunca palpite (CFM)."),
        ("Agenda por convênio ou particular", "Confere o convênio, marca por especialidade e registra no CRM."),
        ("Lembrete D-1 reduz falta", "Confirma a véspera — agenda mais cheia."),
        ("Atende por ligação de voz", "Recepção só entra quando precisa de verdade."),
    ],
    [
        ("cli", "Boa noite, queria marcar uma consulta com cardiologista"),
        ("bot", "Boa noite! Antes de começar, preciso registrar alguns dados tratados com "
                "sigilo conforme a LGPD. Posso seguir? Depois já vejo os horários disponíveis."),
    ],
)

# =====================================================================
# PÁGINA 11 — Planos e preços
# =====================================================================
page_header("Investimento", "Planos e preços")
y = H - 140
para(MX, y,
     "Um valor fixo por mês, sem surpresa. A implantação cobre a montagem completa da sua "
     "assistente (conteúdo, integrações e testes). Sem fidelidade — fica porque funciona.",
     size=11, color=GRAY, leading=16)

y -= 30
planos = [
    ("Essencial", "397", "1.500",
     ["Atendimento 24h", "Entende áudio", "Agendamento", "Lembrete 24h", "1 número WhatsApp"], False),
    ("Profissional", "697", "2.500",
     ["Tudo do Essencial", "Pós-venda ativo", "Orçamento / calculadora",
      "Emissão de NF-e", "Relatório semanal"], True),
    ("Completo", "1.497", "5.000",
     ["Tudo do Profissional", "Leitor de PDF/documentos", "Resposta por voz",
      "Conteúdo + triagem e-mail", "Prioridade no suporte"], False),
]
pw = (W - 2 * MX - 2 * 16) / 3
ptop = y
ph = 300
for i, (nome, mens, impl, feats, destaque) in enumerate(planos):
    x = MX + i * (pw + 16)
    base = ptop - ph
    if destaque:
        rect(x, base, pw, ph, NAVY, radius=14)
        rect(x, ptop - 26, pw, 26, VIO, radius=6)
        c.setFillColorRGB(*WHITE); c.setFont(FONT_B, 8.5)
        c.drawCentredString(x + pw / 2, ptop - 18, "MAIS ESCOLHIDO")
        name_c, feat_c, sub_c, accent = SILVER, SILVER, CREAM, VIO_L
    else:
        rect(x, base, pw, ph, CARD, radius=14)
        name_c, feat_c, sub_c, accent = INK, INK, GRAY, VIO
    yy = ptop - (48 if destaque else 26)
    c.setFillColorRGB(*accent); c.setFont(FONT_B, 15)
    c.drawString(x + 18, yy, nome)
    yy -= 34
    c.setFillColorRGB(*name_c); c.setFont(FONT_B, 30)
    c.drawString(x + 18, yy, "R$ " + mens)
    c.setFillColorRGB(*sub_c); c.setFont(FONT, 10)
    c.drawString(x + 18 + c.stringWidth("R$ " + mens, FONT_B, 30) + 4, yy + 2, "/mês")
    yy -= 18
    c.setFillColorRGB(*sub_c); c.setFont(FONT, 9)
    c.drawString(x + 18, yy, "+ R$ " + impl + " de implantação")
    yy -= 12
    c.setStrokeColorRGB(*(NAVY_SOFT if destaque else LINE)); c.setLineWidth(0.8)
    c.line(x + 18, yy, x + pw - 18, yy)
    yy -= 20
    for f in feats:
        circle(x + 22, yy + 3, 3, accent)
        c.setFillColorRGB(*feat_c); c.setFont(FONT, 9.3)
        c.drawString(x + 32, yy, f)
        yy -= 20

y = ptop - ph - 26
rect(MX, y - 58, W - 2 * MX, 54, NAVY_SOFT, radius=10)
c.setFillColorRGB(*VIO_L); c.setFont(FONT_B, 10)
c.drawString(MX + 16, y - 22, "ADD-ON  —  Parecer Científico")
para(MX + 16, y - 38,
     "Análise de evidência científica por IA (ideal para estética, saúde e nutrição): "
     "R$ 197 por parecer avulso  ou  R$ 490/mês (até 8 pareceres).",
     size=9.5, color=CREAM, width=W - 2 * MX - 32, leading=12)

footer(11, "Catálogo de Serviços & Planos")
c.showPage()

# =====================================================================
# PÁGINA 12 — ROI + Contato (contracapa navy)
# =====================================================================
rect(0, 0, W, H, NAVY)
rect(0, H - 5, W, 5, VIO)
logo(LOGO_DARK, MX, H - 118, 58)
c.setFillColorRGB(*WHITE); c.setFont(FONT_B, 24)
c.drawString(MX, H - 170, "Quanto custa NÃO ter?")
para(MX, H - 198, "Todo mês, um negócio sem atendimento automatizado deixa dinheiro na mesa:",
     size=11, color=CREAM, leading=15)

roi = [
    ("R$ 1.600", "em faltas e no-shows (8 × R$ 200) que um lembrete evitaria"),
    ("R$ 1.200", "em leads que chegam fora do horário e não são respondidos a tempo"),
    ("R$ 528", "em horas da equipe gastas no WhatsApp repetitivo"),
]
y = H - 238
for val, desc in roi:
    rect(MX, y - 52, W - 2 * MX, 46, NAVY_CARD, radius=10)
    c.setFillColorRGB(*VIO_L); c.setFont(FONT_B, 20)
    c.drawString(MX + 18, y - 36, val)
    para(MX + 150, y - 26, desc, size=10, color=CREAM, width=W - 2 * MX - 170, leading=13)
    y -= 60

y -= 6
rect(MX, y - 52, W - 2 * MX, 48, VIO, radius=10)
c.setFillColorRGB(*WHITE); c.setFont(FONT_B, 13)
c.drawString(MX + 18, y - 24, "≈ R$ 2.300 evaporam por mês")
c.setFont(FONT, 10)
c.drawString(MX + 18, y - 40, "A Kronos custa uma fração disso — e se paga na primeira semana.")

cy = 150
c.setStrokeColorRGB(*NAVY_SOFT); c.setLineWidth(1); c.line(MX, cy + 30, W - MX, cy + 30)
c.setFillColorRGB(*WHITE); c.setFont(FONT_B, 16)
c.drawString(MX, cy, "Vamos montar a sua?")
c.setFillColorRGB(*CINZA); c.setFont(FONT, 10)
c.drawString(MX, cy - 22, "Fale com a gente e veja a demonstração ao vivo, no seu WhatsApp.")
c.setFillColorRGB(*VIO_L); c.setFont(FONT_B, 11)
c.drawString(MX, cy - 50, "WhatsApp (19) 97126-6736")
c.drawString(MX, cy - 68, "kronosintelligence.com.br")
c.setFillColorRGB(*CINZA); c.setFont(FONT, 8)
c.drawRightString(W - MX, 40, SLOGAN)
c.showPage()

c.save()
print("OK: Kronos_Catalogo_Servicos.pdf gerado")
