"""
Proposta comercial Kronos Intelligence — Serviço de Parecer Científico sob Demanda.
Para usar: alterar apenas o bloco DADOS DO CLIENTE abaixo.
Rodar: uv run --with reportlab python gerar_proposta_cientifica.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
import os

# ══════════════════════════════════════════════════════════════════
# DADOS DO CLIENTE — alterar para cada nova proposta
# ══════════════════════════════════════════════════════════════════
CLIENTE_NOME         = "Clínica Exemplo Estética"
CLIENTE_PROPRIETARIO = "Dra. Marina"
CLIENTE_ENDERECO     = "Av. das Palmeiras, 1200 — Cambuí — Campinas/SP"
IMPLANTACAO_VALOR    = "R$ 990,00"
MENSALIDADE_VALOR    = "R$ 490,00/mês"
IMPLANTACAO_DESC     = "Configuração do motor de parecer para a área da clínica,\ncalibração e go-live (pagamento único)"
MENSALIDADE_DESC     = "Até 8 pareceres/mês, prioridade de entrega e suporte"

PROBLEMA = (
    "Antes de oferecer um novo tratamento, protocolo ou ativo, o profissional precisa saber se "
    "existe respaldo científico — mas levantar e ler estudos consome horas que ele não tem. "
    "Sem esse embasamento, a decisão vira aposta, e uma indicação sem respaldo é risco para a "
    "reputação e para o paciente."
)

SOLUCAO = (
    "A Kronos entrega um parecer técnico-científico sob demanda: o profissional manda a pergunta, "
    "e recebe de volta um documento fundamentado em evidência real — resposta direta, força da "
    "evidência, método e fontes citadas. Decisões com respaldo, em vez de achismo, sem o "
    "profissional precisar virar pesquisador."
)

COMO_FUNCIONA = [
    "O profissional manda a pergunta (ex: 'há respaldo para indicar o ativo X na condição Y?')",
    "A IA pesquisa e analisa a evidência disponível sobre o tema",
    "O parecer é redigido com resposta direta, nível de confiança da evidência e ressalvas",
    "As fontes são citadas de forma rastreável — nada de achismo",
    "O profissional recebe um PDF profissional, pronto para embasar a decisão",
]

DIFERENCIAIS = [
    "Resposta fundamentada em evidência, não em opinião",
    "Calibra a força da evidência (forte / moderada / limitada / inconclusiva)",
    "Honestidade intelectual — diz quando a evidência é fraca, nunca inventa certeza",
    "Fontes citadas e rastreáveis em cada parecer",
    "Entrega em PDF profissional, pronto para arquivar ou compartilhar",
    "100% remoto — pergunta entra, parecer sai, sem reunião",
]

INCLUSO_IMPL = [
    "Calibração do motor para a área de atuação",
    "Definição dos tipos de parecer mais usados pela clínica",
    "Modelo de PDF com identidade do cliente",
    "Parecer-piloto de demonstração",
    "Treinamento de como solicitar",
    "Go-live acompanhado",
]

INCLUSO_MENS = [
    "Até 8 pareceres por mês",
    "Prioridade de entrega",
    "Revisão de evidência e checagem de alegações",
    "Análise de dados de pesquisa (planilha)",
    "Suporte contínuo",
    "Histórico dos pareceres arquivado",
]

ROI_TEXTO = (
    "Levantar e ler evidência para uma única decisão consome de 2 a 4 horas do profissional — "
    "tempo que, na cadeira, vale centenas de reais. Uma indicação equivocada por falta de respaldo "
    "custa muito mais: retrabalho, perda de confiança do paciente e risco à reputação. "
    "Por uma fração de uma hora de atendimento, o parecer entrega a segurança de decidir com base em evidência."
)
# ══════════════════════════════════════════════════════════════════

OUTPUT = r'C:\Users\Usuario\OneDrive\Documentos\Claude\Projects\teste Automação\13_Servico_AnaliseCientifica\proposta_cientifica.pdf'
LOGO   = r'C:\Users\Usuario\OneDrive\Documentos\Claude\Projects\teste Automação\07_Recursos\identidade_visual\kronos_logo_transparente.png'

# Paleta Kronos
AZUL_MARINHO = colors.HexColor('#020c2a')
VIOLETA      = colors.HexColor('#4a0e90')
INDIGO       = colors.HexColor('#3060c8')
TURQ         = colors.HexColor('#1890c0')
BRANCO       = colors.HexColor('#f0f4ff')
CINZA_CLARO  = colors.HexColor('#8898bb')

W, H = A4

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
    sx = W / 1920
    rcx = 1380 * sx
    rcy = H * 0.50
    off = (1580 - 1380) * sx
    erx = 560 * sx
    ery = 220 * sx
    for i, ang in enumerate(range(0, 154, 3)):
        cor = colors.HexColor(ELIPSE_CORES[i % 8])
        op  = ELIPSE_OPAC[i] if i < len(ELIPSE_OPAC) else 0.14
        canvas.saveState()
        canvas.translate(rcx, rcy)
        canvas.rotate(ang)
        canvas.setStrokeColor(cor)
        canvas.setStrokeAlpha(op)
        canvas.setLineWidth(1.2)
        canvas.ellipse(off - erx, -ery, off + erx, ery, fill=0, stroke=1)
        canvas.restoreState()

LOGO_TOP   = 0.6*cm
LOGO_H     = 2.6*cm
SEP_Y      = H - LOGO_TOP - LOGO_H - 0.5*cm
TOP_MARGIN = H - SEP_Y + 0.6*cm

def fundo(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AZUL_MARINHO)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    draw_elipses(canvas)
    canvas.setFillColor(colors.Color(0.008, 0.047, 0.165, alpha=0.92))
    canvas.rect(0, 0, W * 0.55, H, fill=1, stroke=0)
    steps = 12
    strip_w = W * 0.45 / steps
    for i in range(steps):
        frac  = i / steps
        alpha = 0.92 * (1 - frac)
        canvas.setFillColor(colors.Color(0.008, 0.047, 0.165, alpha=alpha))
        canvas.rect(W * 0.55 + i * strip_w, 0, strip_w + 1, H, fill=1, stroke=0)
    if os.path.exists(LOGO):
        lw = 5.5*cm
        canvas.drawImage(LOGO, (W - lw)/2, H - LOGO_TOP - LOGO_H,
                         width=lw, height=LOGO_H,
                         preserveAspectRatio=True, mask='auto')
    canvas.setStrokeColor(colors.Color(1, 1, 1, alpha=0.10))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, SEP_Y, W - 2*cm, SEP_Y)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(CINZA_CLARO)
    canvas.drawCentredString(W/2, 0.9*cm,
        'Kronos Intelligence  |  kronosintelligence.com.br  |  contato@kronosintelligence.com.br')
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.Color(1, 1, 1, alpha=0.35))
    canvas.drawCentredString(W/2, 0.45*cm,
        f'{CLIENTE_PROPRIETARIO}  |  {CLIENTE_ENDERECO}')
    canvas.restoreState()

def s(name, **kw):
    return ParagraphStyle(name, **kw)

secao  = s('SE', fontSize=12, textColor=BRANCO, spaceBefore=12, spaceAfter=5,
           fontName='Helvetica-Bold')
corpo  = s('CO', fontSize=10, textColor=CINZA_CLARO, spaceAfter=4,
           fontName='Helvetica', leading=15)
bullet = s('BU', fontSize=10, textColor=BRANCO, spaceAfter=3,
           fontName='Helvetica', leftIndent=14, leading=14)

doc = BaseDocTemplate(OUTPUT, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=TOP_MARGIN, bottomMargin=1.5*cm)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
doc.addPageTemplates([PageTemplate(id='kronos', frames=frame, onPage=fundo)])

story = []

cliente_nome_style = s('CN', fontSize=18, textColor=BRANCO,
    fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)

story.append(Paragraph(CLIENTE_NOME, cliente_nome_style))
story.append(Spacer(1, 0.2*cm))
_lw = doc.width * 0.35
linha_nome = Table([['']], colWidths=[_lw])
linha_nome.setStyle(TableStyle([
    ('LINEBELOW', (0,0), (-1,-1), 1.0, VIOLETA),
    ('TOPPADDING',    (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
]))
story.append(linha_nome)
story.append(Spacer(1, 0.35*cm))

def linha_secao():
    story.append(HRFlowable(width='100%', thickness=0.5, color=VIOLETA, spaceAfter=4))

def bloco_titulo(texto):
    story.append(Paragraph(texto, secao))
    linha_secao()

bloco_titulo('O Problema')
story.append(Paragraph(PROBLEMA, corpo))

bloco_titulo('A Solução')
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
    [cell('', bold=True), cell('Descrição', bold=True), cell('Valor', bold=True)],
    [cell('Implantação'), cell(IMPLANTACAO_DESC), cell(IMPLANTACAO_VALOR, bold=True, color=colors.HexColor('#a080ff'), size=12)],
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

bloco_titulo('O que está incluso')

hdr  = lambda txt: Paragraph(txt, s('H2_'+txt[:4], fontSize=9, textColor=colors.HexColor('#a080ff'),
    fontName='Helvetica-Bold', alignment=TA_CENTER, leading=13))
item = lambda txt: Paragraph(txt, s('IT_'+txt[:4], fontSize=9, textColor=CINZA_CLARO,
    fontName='Helvetica', leading=13))

dados2 = [[hdr('Implantação (' + IMPLANTACAO_VALOR + ')'), hdr('Mensalidade (' + MENSALIDADE_VALOR + ')')]]
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
print('PDF gerado:', OUTPUT)
