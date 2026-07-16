# -*- coding: utf-8 -*-
"""
Book Kronos — PDF único encadernável (A4) juntando toda a papelada oficial.
Identidade oficial: paleta navy da landing + logos reais (identidade_visual/).

Ordem: capa > sumário > história > catálogo completo (PDF existente) >
       demonstrações > onboarding > FAQ > glossário > contracapa.

Rodar (de dentro de 00_Empresa_Kronos/11_Book_Impressao/):
  uv run --with reportlab --with pillow --with pypdf python gerar_book.py
Saída: Kronos_Book.pdf
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit, ImageReader
from PIL import Image, ImageChops
from pypdf import PdfReader, PdfWriter

W, H = A4
MX = 52

NAVY      = (0.008, 0.047, 0.165)
NAVY_SOFT = (0.063, 0.133, 0.290)
VIO       = (0.290, 0.055, 0.565)
VIO_L     = (0.651, 0.576, 0.847)
SILVER    = (0.914, 0.929, 0.965)
CREAM     = (0.765, 0.796, 0.878)
CINZA     = (0.533, 0.596, 0.733)
INK       = (0.043, 0.086, 0.188)
GRAY_L    = (0.55, 0.60, 0.71)
LIGHT     = (0.965, 0.969, 0.984)
CARD      = (0.925, 0.937, 0.961)
LINE      = (0.847, 0.863, 0.910)
WHITE     = (1, 1, 1)

BASE = os.path.dirname(os.path.abspath(__file__))
IDV = os.path.join(BASE, "..", "..", "07_Recursos", "identidade_visual")
DEMOS = os.path.join(BASE, "..", "04_Demonstracoes")
CATALOGO = os.path.join(BASE, "..", "03_Catalogo_Servicos", "Kronos_Catalogo_Servicos.pdf")
ASSETS = os.path.join(BASE, "_assets_book")
os.makedirs(ASSETS, exist_ok=True)

FONT, FONT_B = "Helvetica", "Helvetica-Bold"


def autocrop(src, dst, pad=14, tol=20):
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


LOGO_LIGHT = autocrop(os.path.join(IDV, "kronos_logo_oficial_claro.png"), os.path.join(ASSETS, "logo_light.png"))
LOGO_DARK  = autocrop(os.path.join(IDV, "kronos_logo_oficial_transparente.png"), os.path.join(ASSETS, "logo_dark.png"))
_ldim = {p: Image.open(p).size for p in (LOGO_LIGHT, LOGO_DARK)}

N_CAT = len(PdfReader(CATALOGO).pages)

PARTS = os.path.join(BASE, "_book_parts.pdf")
c = canvas.Canvas(PARTS, pagesize=A4)
c.setTitle("Kronos Intelligence — Book Institucional")
c.setAuthor("Kronos Intelligence")
SLOGAN = "Inteligência que automatiza. Resultado que transforma."


def rect(x, y, w, h, color, radius=0):
    c.setFillColorRGB(*color)
    if radius:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)
    else:
        c.rect(x, y, w, h, fill=1, stroke=0)


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


# ---- numeração dinâmica ----
P_CAPA = 1
P_SUM = 2
P_HIST = 3
P_CAT = 4
P_DEMOS = P_CAT + N_CAT          # poster + 3 páginas de prints = 4
P_ONB = P_DEMOS + 4
P_FAQ = P_ONB + 1                # 2 páginas
P_GLOS = P_FAQ + 2
P_CONTRA = P_GLOS + 1

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
c.drawCentredString(W / 2, H / 2 - 70, "Book")
c.setFillColorRGB(*VIO_L)
c.drawCentredString(W / 2, H / 2 - 118, "Institucional")
c.setStrokeColorRGB(*NAVY_SOFT)
c.setLineWidth(1)
c.line(W / 2 - 120, H / 2 - 150, W / 2 + 120, H / 2 - 150)
para(MX + 40, H / 2 - 185,
     "Agentes de inteligência artificial construídos sob medida para o seu negócio: "
     "atendem, agendam, calculam, lembram e acompanham seus clientes 24 horas por dia — "
     "por texto, áudio e ligação de voz.",
     size=12, color=CREAM, width=W - 2 * MX - 80, leading=19)
c.setFillColorRGB(*CINZA)
c.setFont(FONT, 9)
c.drawString(MX, 66, "kronosintelligence.com.br")
c.drawString(MX, 52, "WhatsApp (19) 97126-6736")
c.drawRightString(W - MX, 52, "Edição 2026")
c.showPage()

# =====================================================================
# SUMÁRIO
# =====================================================================
page_header("Book Institucional", "Sumário")
itens = [
    ("Nossa História", P_HIST),
    ("Catálogo de Serviços & Planos", P_CAT),
    ("Demonstrações por segmento", P_DEMOS),
    ("Como funciona a implantação", P_ONB),
    ("Perguntas frequentes", P_FAQ),
    ("Glossário", P_GLOS),
    ("Contato", P_CONTRA),
]
y = H - 170
for titulo, pg in itens:
    rect(MX, y - 8, W - 2 * MX, 34, CARD, radius=8)
    c.setFillColorRGB(*INK)
    c.setFont(FONT_B, 12)
    c.drawString(MX + 16, y + 2, titulo)
    c.setFillColorRGB(*VIO)
    c.setFont(FONT_B, 12)
    c.drawRightString(W - MX - 16, y + 2, f"p. {pg}")
    y -= 48
footer(P_SUM, "Sumário")
c.showPage()

# =====================================================================
# HISTÓRIA
# =====================================================================
page_header("Quem somos", "Nossa História")
y = H - 150
y = para(MX, y,
         "A Kronos Intelligence é uma agência brasileira de inteligência artificial que constrói "
         "agentes de IA sob medida para pequenos e médios negócios — clínicas, consultórios, "
         "escritórios de advocacia, imobiliárias e empresas de serviços.", size=11) - 8
y = para(MX, y,
         "Nossos agentes atendem, agendam, calculam, lembram e acompanham clientes 24 horas por dia, "
         "7 dias por semana — por texto, áudio e até ligação de voz. Não vendemos ferramenta pra você "
         "montar sozinho: a gente constrói, personaliza e cuida. Você colhe o resultado.", size=11) - 16

c.setFillColorRGB(*VIO)
c.setFont(FONT_B, 13)
c.drawString(MX, y, "A história")
y -= 22
y = para(MX, y,
         "A Kronos nasceu em janeiro de 2025, fundada por Allan Rodrigues, em Campinas/SP. "
         "Antes da tecnologia, Allan empreendeu no mundo real: tocou um delivery por 4 anos — "
         "atendendo cliente no WhatsApp, anotando pedido, correndo contra o relógio. Ali aprendeu "
         "na pele a dor que hoje resolve: o pequeno negócio perde cliente porque não dá conta de "
         "responder a tempo. Quem chama fora do horário vai pro concorrente. Quem espera demais, desiste.",
         size=11) - 8
y = para(MX, y,
         "Autodidata, Allan mergulhou em inteligência artificial e automação e construiu, um a um, "
         "os agentes que hoje formam a plataforma Kronos — testados em operação real, com atendimento, "
         "agendamento, cálculo de orçamento, voz e relatórios rodando de ponta a ponta.", size=11) - 16

c.setFillColorRGB(*VIO)
c.setFont(FONT_B, 13)
c.drawString(MX, y, "No que acreditamos")
y -= 24
for t, d in [
    ("IA não é luxo de empresa grande.", "Nossa missão é democratizar a inteligência artificial pro pequeno negócio brasileiro."),
    ("Parceria, não dependência.", "Você entende o que está sendo feito, acompanha os resultados e fala com gente de verdade."),
    ("Número calculado, nunca inventado.", "Nossos agentes não chutam: cálculo é cálculo, e o que exige decisão humana vai pra um humano."),
]:
    rect(MX, y - 30, W - 2 * MX, 44, CARD, radius=8)
    c.setFillColorRGB(*INK)
    c.setFont(FONT_B, 10.5)
    c.drawString(MX + 14, y - 4, t)
    c.setFillColorRGB(*GRAY_L)
    c.setFont(FONT, 9.5)
    c.drawString(MX + 14, y - 19, d)
    y -= 58

rect(MX, y - 40, W - 2 * MX, 46, NAVY, radius=10)
c.setFillColorRGB(*VIO_L)
c.setFont(FONT_B, 12)
c.drawCentredString(W / 2, y - 20, f'"{SLOGAN}"')
footer(P_HIST, "Nossa História")
c.showPage()

# =====================================================================
# DEMONSTRAÇÕES — poster + prints 2 por página
# =====================================================================
page_header("Prova, não promessa", "Demonstrações por segmento")
y = H - 146
y = para(MX, y,
         "As páginas a seguir mostram conversas reais dos agentes Kronos em cada segmento. "
         "Todas as demos também funcionam AO VIVO: fale com um agente agora pelo WhatsApp e "
         "veja com seus próprios olhos.", size=11) - 6
poster = os.path.join(DEMOS, "demo_poster.png")
if os.path.exists(poster):
    pw, ph = Image.open(poster).size
    disp_w = W - 2 * MX
    disp_h = disp_w * ph / pw
    max_h = y - 70
    if disp_h > max_h:
        disp_h = max_h
        disp_w = disp_h * pw / ph
    c.drawImage(ImageReader(poster), (W - disp_w) / 2, y - disp_h - 10, disp_w, disp_h,
                preserveAspectRatio=True, mask="auto")
footer(P_DEMOS, "Demonstrações")
c.showPage()

nichos = [
    ("demo_clinicas.png", "Clínicas de Estética & Odontologia"),
    ("demo_advocacia.png", "Advocacia"),
    ("demo_imobiliaria.png", "Imobiliária"),
    ("demo_solar.png", "Energia Solar"),
    ("demo_clinica_medica.png", "Clínica Médica"),
    ("demo_arquitetura.png", "Arquitetura"),
]
for i in range(0, len(nichos), 2):
    page_header("Demonstrações", "O agente em ação")
    slots = nichos[i:i + 2]
    slot_w = (W - 2 * MX - 24) / 2
    for j, (fn, titulo) in enumerate(slots):
        p = os.path.join(DEMOS, fn)
        if not os.path.exists(p):
            continue
        x0 = MX + j * (slot_w + 24)
        iw, ih = Image.open(p).size
        disp_w = slot_w
        disp_h = disp_w * ih / iw
        max_h = H - 240
        if disp_h > max_h:
            disp_h = max_h
            disp_w = disp_h * iw / ih
        c.setFillColorRGB(*VIO)
        c.setFont(FONT_B, 10)
        c.drawString(x0, H - 138, titulo.upper())
        c.drawImage(ImageReader(p), x0 + (slot_w - disp_w) / 2, H - 160 - disp_h, disp_w, disp_h,
                    preserveAspectRatio=True, mask="auto")
    footer(P_DEMOS + 1 + i // 2, "Demonstrações")
    c.showPage()

# =====================================================================
# ONBOARDING
# =====================================================================
page_header("Depois do sim", "Como funciona a implantação")
y = H - 146
y = para(MX, y, "Do contrato ao agente no ar em 7 a 14 dias — com você aprovando antes do go-live.",
         size=11, color=VIO, font=FONT_B) - 10
etapas = [
    ("1. Contrato + entrada", "Assinatura e pagamento da implantação. A partir daqui o relógio corre por nossa conta.", "dia 0"),
    ("2. Formulário do negócio", "Você nos passa serviços e preços, horários, perguntas frequentes, tom de voz, logo e acesso à agenda.", "dias 0-2"),
    ("3. Construção", "Montamos seu agente: personalidade, conhecimento, agendamento, cálculos e lembretes. Base isolada e exclusiva.", "dias 2-8"),
    ("4. Testes com você", "Você conversa como se fosse cliente e aponta ajustes. O agente só vai ao ar com o seu OK.", "dias 8-12"),
    ("5. Go-live", "O agente entra no ar no seu WhatsApp oficial, com acompanhamento em tempo real nos primeiros dias.", "dia ~14"),
    ("6. Rotina", "Relatório semanal, ajustes de conteúdo inclusos, suporte direto e monitoramento 24/7.", "sempre"),
]
for t, d, prazo in etapas:
    rect(MX, y - 46, W - 2 * MX, 56, CARD, radius=8)
    c.setFillColorRGB(*INK)
    c.setFont(FONT_B, 11)
    c.drawString(MX + 14, y - 8, t)
    c.setFillColorRGB(*VIO)
    c.setFont(FONT_B, 9)
    c.drawRightString(W - MX - 14, y - 8, prazo)
    para(MX + 14, y - 24, d, size=9.5, color=GRAY_L, width=W - 2 * MX - 40, leading=12)
    y -= 68
footer(P_ONB, "Implantação")
c.showPage()

# =====================================================================
# FAQ — 2 páginas
# =====================================================================
faq = [
    ("Tá caro.",
     "Uma recepcionista custa R$ 2.500-3.500/mês, trabalha 8h e tira férias. O agente custa menos, trabalha 24h — inclusive madrugada e fim de semana, quando você mais perde cliente — e nunca fica doente."),
    ("IA erra, inventa coisa.",
     "IA solta inventa mesmo. Os agentes Kronos são travados: número é sempre calculado, nunca inventado. E o que exige julgamento humano — reclamação, urgência — o agente não resolve sozinho: ele te chama na hora."),
    ("Já tenho secretária.",
     "O agente não substitui, libera: segura o repetitivo (~3h/dia) e ela fica com o que precisa de gente. De noite e fim de semana, quando ela não está, o agente está."),
    ("Meu cliente quer falar com gente.",
     "E vai falar — na hora certa. O agente resolve o imediato e transfere quem pede humano. Na prática, o cliente prefere resposta em 30 segundos a esperar 3 horas."),
    ("Quanto tempo pra ficar pronto?",
     "Implantação típica: 7 a 14 dias entre fechamento e go-live, com testes aprovados por você antes de ir ao ar."),
    ("Preciso trocar de número?",
     "Não. O agente entra no SEU WhatsApp, com seu número e nome. Seus clientes não mudam nada."),
    ("E os dados dos meus clientes?",
     "Tratados conforme a LGPD: consentimento quando necessário, base isolada só do seu negócio, exportação ou exclusão quando você pedir."),
    ("Meu ramo é diferente, funciona?",
     "Cada agente é construído sob medida. Já operamos em estética, odontologia, clínica médica, advocacia, imobiliária, energia solar e arquitetura."),
    ("E se eu quiser cancelar?",
     "Condições claras no contrato, sem multa escondida. Nosso modelo depende de você renovar porque funciona — não de te prender."),
    ("Posso testar antes?",
     "Pode e deve: temos demos ao vivo no WhatsApp. Você conversa com o agente agora, do seu celular, como se fosse um cliente."),
]
for pg in range(2):
    page_header("Sem letra miúda", "Perguntas frequentes")
    y = H - 150
    for q, a in faq[pg * 5:pg * 5 + 5]:
        c.setFillColorRGB(*VIO)
        c.setFont(FONT_B, 11.5)
        c.drawString(MX, y, q)
        y -= 17
        y = para(MX, y, a, size=10, color=INK, leading=14) - 14
    footer(P_FAQ + pg, "Perguntas frequentes")
    c.showPage()

# =====================================================================
# GLOSSÁRIO
# =====================================================================
page_header("Sem tecniquês", "Glossário")
gloss = [
    ("Agente de IA", "Um 'funcionário digital' treinado pro seu negócio: entende, responde, agenda e resolve — conversa de verdade."),
    ("Automação", "Tarefa que acontece sozinha, sem ninguém apertar botão."),
    ("Implantação", "Período em que a Kronos constrói e personaliza o agente. Pago uma vez, no início."),
    ("Mensalidade", "Valor mensal pra manter o agente no ar: servidor, melhorias, monitoramento e suporte."),
    ("Atendimento por voz", "O agente que atende ligação telefônica com voz natural e agenda na mesma chamada."),
    ("Transcrição de áudio", "O agente 'escuta' o áudio do cliente, entende e resume pra você."),
    ("CRM", "O painel onde fica o histórico de cada cliente. O agente preenche sozinho."),
    ("Lead", "Pessoa interessada que ainda não fechou. O agente descobre o que ela quer e o quão pronta está."),
    ("Follow-up", "Mensagem de acompanhamento pra quem sumiu — o agente faz sozinho, na hora certa."),
    ("Qualificação", "As perguntas certas antes de passar pra você só quem vale seu tempo."),
    ("Payback", "Em quanto tempo um investimento se paga — o agente solar calcula na hora."),
    ("LGPD", "Lei de proteção de dados. Os agentes pedem consentimento e tratam dados conforme a lei."),
    ("NF-e / NFS-e", "Nota fiscal eletrônica emitida automaticamente após o serviço."),
    ("Demo", "Versão de teste do agente funcionando de verdade no WhatsApp, antes de contratar."),
    ("Go-live", "O dia em que o agente entra no ar atendendo seus clientes reais."),
]
col_w = (W - 2 * MX - 24) / 2
x = MX
y = H - 150
y0 = y
for i, (t, d) in enumerate(gloss):
    if i == 8:
        x = MX + col_w + 24
        y = y0
    c.setFillColorRGB(*INK)
    c.setFont(FONT_B, 10.5)
    c.drawString(x, y, t)
    y -= 14
    y = para(x, y, d, size=9, color=GRAY_L, width=col_w, leading=12) - 10
footer(P_GLOS, "Glossário")
c.showPage()

# =====================================================================
# CONTRACAPA
# =====================================================================
rect(0, 0, W, H, NAVY)
rect(0, H - 5, W, 5, VIO)
logo(LOGO_DARK, W / 2, H / 2 + 60, 120, anchor="center")
c.setFillColorRGB(*WHITE)
c.setFont(FONT_B, 20)
c.drawCentredString(W / 2, H / 2 - 20, "Vamos conversar?")
c.setFillColorRGB(*CREAM)
c.setFont(FONT, 13)
c.drawCentredString(W / 2, H / 2 - 60, "WhatsApp: (19) 97126-6736")
c.drawCentredString(W / 2, H / 2 - 82, "kronosintelligence.com.br")
c.drawCentredString(W / 2, H / 2 - 104, "Campinas/SP")
c.setFillColorRGB(*CINZA)
c.setFont(FONT, 9)
c.drawCentredString(W / 2, 60, SLOGAN)
c.showPage()

c.save()

# =====================================================================
# MERGE: partes + catálogo completo na posição certa
# =====================================================================
parts = PdfReader(PARTS)
cat = PdfReader(CATALOGO)
out = PdfWriter()

# parts: 0=capa 1=sumário 2=história 3..6=demos 7=onboarding 8-9=faq 10=glossário 11=contracapa
for i in (0, 1, 2):
    out.add_page(parts.pages[i])
for p in cat.pages:
    out.add_page(p)
for i in range(3, len(parts.pages)):
    out.add_page(parts.pages[i])

dest = os.path.join(BASE, "Kronos_Book.pdf")
with open(dest, "wb") as f:
    out.write(f)
os.remove(PARTS)
print(f"OK: {dest} — {len(out.pages)} paginas (catalogo tem {N_CAT})")
