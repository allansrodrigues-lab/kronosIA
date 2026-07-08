"""
Template de proposta comercial Kronos Intelligence.
Para usar em novo cliente: alterar apenas o bloco DADOS DO CLIENTE abaixo.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.utils import ImageReader
import os, math

# ══════════════════════════════════════════════════════════════════
# DADOS DO CLIENTE — alterar para cada nova proposta
# ══════════════════════════════════════════════════════════════════
CLIENTE_NOME        = "Pizzaria Bella Massa"
CLIENTE_PROPRIETARIO = "Lucas"
CLIENTE_ENDERECO    = "Av. Itália, 1200 — Centro/SP"
IMPLANTACAO_VALOR   = "R$ 1.760,00"
MENSALIDADE_VALOR   = "R$ 697,00/mes"
IMPLANTACAO_DESC    = "Configuracao completa, cardapio, testes e go-live\n(pagamento unico)"
MENSALIDADE_DESC    = "Atendimento automatico, suporte, atualizacoes e relatorio mensal"

PROBLEMA = (
    "Nos horarios de pico — sextas e sabados a noite — o volume de mensagens no WhatsApp "
    "supera a capacidade de atendimento manual. Clientes aguardam respostas por mais de uma hora "
    "e, sem retorno, migram para a concorrencia. Cada pedido perdido e receita que nao volta."
)
SOLUCAO = (
    "Um sistema de atendimento inteligente via WhatsApp que recebe todos os pedidos "
    "simultaneamente, das 18h as 23h55, sem pausas e sem erros. O cliente e atendido "
    "em segundos, escolhe sabor, borda e complementos, e o pedido chega formatado "
    "para sua equipe finalizar — sem digitacao, sem retrabalho."
)
COMO_FUNCIONA = [
    "Cliente manda mensagem no WhatsApp da pizzaria",
    "Sistema responde em segundos e guia a escolha do sabor",
    "Cliente escolhe borda, extras e informa endereco",
    "Sistema monta o resumo completo com total",
    "Pedido formatado chega para sua equipe confirmar e preparar",
]
DIFERENCIAIS = [
    "Atende todos os clientes ao mesmo tempo — sem fila, sem espera",
    "Suporta pizza meia a meia e bordas personalizadas",
    "Sugere combos automaticamente — mais vendas, mesmo esforco",
    "Pedido chega sem erro de digitacao para a equipe",
    "Funciona todos os dias, das 18h as 23h55, sem interrupcao",
    "Destaca borda de requeijao gratis em cada atendimento",
]
INCLUSO_IMPL = [
    "Configuracao completa do sistema de atendimento WhatsApp",
    "Cadastro de todo o cardapio (pizzas, esfihas, calzones, combos)",
    "Treinamento do agente com os fluxos da pizzaria",
    "Integracao com o numero WhatsApp da pizzaria",
    "Testes e validacao antes do go-live",
    "Treinamento da equipe para receber os pedidos",
]
INCLUSO_MENS = [
    "Atendimento automatico 18h-23h55, todos os dias",
    "Suporte e monitoramento continuo",
    "Atualizacoes de cardapio quando necessario",
    "Relatorio mensal de pedidos atendidos",
    "Manutencao e estabilidade do sistema",
]
ROI_TEXTO = (
    "Nos horarios de pico, uma pizzaria do porte da Bella Massa pode perder facilmente "
    "5 a 10 pedidos por noite por demora no atendimento. Considerando um ticket medio "
    "de R$ 65,00, isso representa ate R$ 2.600,00/mes em receita perdida. "
    "O sistema se paga no primeiro mes."
)
# ══════════════════════════════════════════════════════════════════

OUTPUT = r'C:\Users\Usuario\OneDrive\Documentos\Claude\Projects\teste Automação\09_Pizzaria_SantaAna\proposta_santaana.pdf'
LOGO   = r'C:\Users\Usuario\OneDrive\Documentos\Claude\Projects\teste Automação\07_Recursos\identidade_visual\kronos_logo_transparente.png'

# Paleta Kronos
AZUL_MARINHO  = colors.HexColor('#020c2a')
VIOLETA       = colors.HexColor('#4a0e90')
INDIGO        = colors.HexColor('#3060c8')
TURQ          = colors.HexColor('#1890c0')
BRANCO        = colors.HexColor('#f0f4ff')
CINZA_CLARO   = colors.HexColor('#8898bb')
ROXO_SUTIL    = colors.HexColor('#1a1040')

W, H = A4

# ── Elipses decorativas (mesmo padrão do site) ────────────────────
ELIPSE_CORES = ['#9060e0','#3060c8','#5040d8','#1890c0',
                '#7848c8','#2048a8','#3830b0','#1070a0']
ELIPSE_OPAC  = [0.80,0.80,0.80,0.80, 0.76,0.76,0.76,0.76,
                0.72,0.72,0.72,0.72, 0.68,0.68,0.68,0.68,
                0.64,0.64,0.64,0.64, 0.60,0.60,0.60,0.60,
                0.55,0.55,0.55,0.55, 0.50,0.50,0.50,0.50,
                0.44,0.44,0.44,0.44, 0.38,0.38,0.38,0.38,
                0.30,0.30,0.30,0.30, 0.22,0.22,0.22,0.22,
                0.14,0.14,0.14,0.14]

def draw_elipses(canvas):
    sx = W / 1920  # escala uniforme preservando proporção
    # No site: rotation center (1380,540), ellipse center (1580,540)
    # Em PDF: y invertido, centrado verticalmente
    rcx = 1380 * sx
    rcy = H * 0.50
    off = (1580 - 1380) * sx  # offset do centro da elipse = 200*sx
    erx = 560 * sx
    ery = 220 * sx
    for i, ang in enumerate(range(0, 154, 3)):
        cor = colors.HexColor(ELIPSE_CORES[i % 8])
        op  = ELIPSE_OPAC[i] if i < len(ELIPSE_OPAC) else 0.14
        canvas.saveState()
        canvas.translate(rcx, rcy)
        canvas.rotate(ang)          # PDF CCW ≈ visual site
        canvas.setStrokeColor(cor)
        canvas.setStrokeAlpha(op)
        canvas.setLineWidth(1.2)
        canvas.ellipse(off - erx, -ery, off + erx, ery, fill=0, stroke=1)
        canvas.restoreState()

def _base_fundo(canvas):
    canvas.saveState()
    # Fundo navy total
    canvas.setFillColor(AZUL_MARINHO)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # Elipses decorativas
    draw_elipses(canvas)
    # Máscara navy: esquerda opaca, direita revela elipses
    canvas.setFillColor(colors.Color(0.008, 0.047, 0.165, alpha=0.92))
    canvas.rect(0, 0, W * 0.55, H, fill=1, stroke=0)
    steps = 12
    strip_w = W * 0.45 / steps
    for i in range(steps):
        frac  = i / steps
        alpha = 0.92 * (1 - frac)
        canvas.setFillColor(colors.Color(0.008, 0.047, 0.165, alpha=alpha))
        canvas.rect(W * 0.55 + i * strip_w, 0, strip_w + 1, H, fill=1, stroke=0)
    # Rodapé — linha Kronos
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(CINZA_CLARO)
    canvas.drawCentredString(W/2, 0.9*cm,
        'Kronos Intelligence  |  kronosintelligence.com.br  |  contato@kronosintelligence.com.br')
    # Rodapé — dados do cliente
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.Color(1, 1, 1, alpha=0.35))
    canvas.drawCentredString(W/2, 0.45*cm,
        f'{CLIENTE_PROPRIETARIO}  |  {CLIENTE_ENDERECO}')
    canvas.restoreState()

LOGO_TOP   = 0.6*cm   # distância do topo ao início do logo
LOGO_H     = 2.6*cm   # altura reservada ao logo
SEP_Y      = H - LOGO_TOP - LOGO_H - 0.5*cm  # linha separadora
TOP_MARGIN = H - SEP_Y + 0.6*cm              # topMargin do doc

# ── Fundo e logo em todas as páginas ──────────────────────────────
def fundo(canvas, doc):
    _base_fundo(canvas)
    canvas.saveState()
    if os.path.exists(LOGO):
        lw = 5.5*cm
        canvas.drawImage(LOGO, (W - lw)/2, H - LOGO_TOP - LOGO_H,
                         width=lw, height=LOGO_H,
                         preserveAspectRatio=True, mask='auto')
    # Linha separadora alinhada com as margens do conteúdo
    canvas.setStrokeColor(colors.Color(1, 1, 1, alpha=0.10))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, SEP_Y, W - 2*cm, SEP_Y)
    canvas.restoreState()

# ── Estilos ───────────────────────────────────────────────────────
def s(name, **kw):
    return ParagraphStyle(name, **kw)

tit_proposta = s('TP', fontSize=11, textColor=BRANCO,
    fontName='Helvetica', alignment=TA_CENTER, spaceAfter=0)
tit_cliente = s('TC', fontSize=20, textColor=BRANCO,
    fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)
tit_endereco = s('TE', fontSize=9, textColor=CINZA_CLARO,
    fontName='Helvetica', alignment=TA_CENTER)
secao = s('SE', fontSize=12, textColor=BRANCO, spaceBefore=12, spaceAfter=5,
    fontName='Helvetica-Bold')
corpo = s('CO', fontSize=10, textColor=CINZA_CLARO, spaceAfter=4,
    fontName='Helvetica', leading=15)
bullet = s('BU', fontSize=10, textColor=BRANCO, spaceAfter=3,
    fontName='Helvetica', leftIndent=14, leading=14)

# ── Documento ─────────────────────────────────────────────────────
doc = BaseDocTemplate(OUTPUT, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=TOP_MARGIN, bottomMargin=1.5*cm)

frame = Frame(doc.leftMargin, doc.bottomMargin,
              doc.width, doc.height, id='normal')
doc.addPageTemplates([PageTemplate(id='kronos', frames=frame, onPage=fundo)])

story = []

# ── Bloco de identificação (no espaço da faixa violeta) ───────────
# A faixa superior tem 3.5cm; o topMargin é 4.2cm, então o conteúdo começa logo abaixo.
# Vamos colocar os dados do cliente dentro da faixa usando posição absoluta no fundo(),
# mas é mais simples deixar o primeiro conteúdo flutuar com espaçamento negativo.
# Alternativa: inserir os dados do cliente como primeiros parágrafos com margem negativa equivalente.
# Usaremos uma tabela de cabeçalho posicionada manualmente no fundo() para o lado direito.

# Já que o logo fica no canto esq da faixa, colocamos o nome do cliente no lado direito da faixa
# via canvas no fundo(). Para simplificar, apenas redesenhamos o fundo com os dados do cliente.

def fundo_com_cliente(canvas, doc):
    fundo(canvas, doc)

doc.addPageTemplates([PageTemplate(id='kronos', frames=frame, onPage=fundo_com_cliente)])

# ── Conteúdo ──────────────────────────────────────────────────────
def linha_secao():
    story.append(HRFlowable(width='100%', thickness=0.5, color=VIOLETA, spaceAfter=4))

def bloco_titulo(texto):
    story.append(Paragraph(texto, secao))
    linha_secao()

cliente_nome_style = s('CN', fontSize=18, textColor=BRANCO,
    fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)
cliente_end_style  = s('CE', fontSize=9, textColor=CINZA_CLARO,
    fontName='Helvetica', alignment=TA_CENTER, spaceAfter=14)

story.append(Paragraph(CLIENTE_NOME, cliente_nome_style))
story.append(Spacer(1, 0.2*cm))
# Linha curta centralizada sob o nome do cliente
_lw = doc.width * 0.35
linha_nome = Table([['']], colWidths=[_lw])
linha_nome.setStyle(TableStyle([
    ('LINEBELOW', (0,0), (-1,-1), 1.0, VIOLETA),
    ('TOPPADDING',    (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
]))
story.append(linha_nome)
story.append(Spacer(1, 0.35*cm))

bloco_titulo('O Problema')
story.append(Paragraph(PROBLEMA, corpo))

bloco_titulo('A Solucao')
story.append(Paragraph(SOLUCAO, corpo))

bloco_titulo('Como Funciona')
for i, passo in enumerate(COMO_FUNCIONA, 1):
    story.append(Paragraph(f'<b>{i}.</b>  {passo}', bullet))

story.append(Spacer(1, 0.3*cm))
bloco_titulo('Diferenciais')
for d in DIFERENCIAIS:
    story.append(Paragraph(f'<font color="#a080ff">+</font>  {d}', bullet))

story.append(Spacer(1, 0.3*cm))
bloco_titulo('Investimento')

cell = lambda txt, bold=False, color=BRANCO, size=10: Paragraph(
    txt, s('TC_'+txt[:4], fontSize=size, textColor=color,
           fontName='Helvetica-Bold' if bold else 'Helvetica',
           alignment=TA_CENTER, leading=14))

dados = [
    [cell('', bold=True), cell('Descricao', bold=True), cell('Valor', bold=True)],
    [cell('Implantacao'), cell(IMPLANTACAO_DESC), cell(IMPLANTACAO_VALOR, bold=True, color=colors.HexColor('#a080ff'), size=12)],
    [cell('Mensalidade'), cell(MENSALIDADE_DESC), cell(MENSALIDADE_VALOR, bold=True, color=colors.HexColor('#a080ff'), size=12)],
]
t = Table(dados, colWidths=[3.2*cm, 9.3*cm, 3.5*cm])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), VIOLETA),
    ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#0d1a3a')),
    ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#091228')),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#2a3060')),
    ('TOPPADDING', (0,0), (-1,-1), 10),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(Spacer(1, 0.4*cm))

bloco_titulo('O que esta incluso')

hdr  = lambda txt: Paragraph(txt, s('H2_'+txt[:4], fontSize=9, textColor=colors.HexColor('#a080ff'),
    fontName='Helvetica-Bold', alignment=TA_CENTER, leading=13))
item = lambda txt: Paragraph(txt, s('IT_'+txt[:4], fontSize=9, textColor=CINZA_CLARO,
    fontName='Helvetica', leading=13))

dados2 = [[hdr('Implantacao (' + IMPLANTACAO_VALOR + ')'), hdr('Mensalidade (' + MENSALIDADE_VALOR + ')')]]
for i in range(max(len(INCLUSO_IMPL), len(INCLUSO_MENS))):
    a = item('+ ' + INCLUSO_IMPL[i]) if i < len(INCLUSO_IMPL) else item('')
    b = item('+ ' + INCLUSO_MENS[i]) if i < len(INCLUSO_MENS) else item('')
    dados2.append([a, b])

t2 = Table(dados2, colWidths=[8*cm, 8*cm])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a1050')),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#091228')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#2a3060')),
    ('TOPPADDING', (0,0), (-1,-1), 7),
    ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
story.append(t2)
story.append(Spacer(1, 0.4*cm))

bloco_titulo('Retorno sobre o Investimento')
story.append(Paragraph(ROI_TEXTO, corpo))

doc.build(story)
print('PDF gerado com sucesso!')
