"""
Gerador de PARECER CIENTÍFICO em PDF — Kronos Intelligence (modo plus).
Renderiza um parecer (resposta da IA) como documento profissional navy+violeta.
Em produção: o n8n manda as 7 seções (PERGUNTA, RESPOSTA, NIVEL, FUNDAMENTACAO,
METODO, RESSALVAS, FONTES) para este script gerar o PDF.

Rodar: uv run --with reportlab python gerar_parecer_pdf.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import os

# ══════════════════════════════════════════════════════════════════
# DADOS DO PARECER — em produção vêm do workflow n8n
# ══════════════════════════════════════════════════════════════════
CLIENTE_NOME = "Clínica Aurora Estética"
SOLICITANTE  = "Dra. Marina"
AREA         = "Saúde e Estética"
TIPO         = "Checagem de alegação"
DATA         = "20 de junho de 2026"

PERGUNTA = (
    "A aplicação tópica de vitamina C (ácido L-ascórbico e derivados) produz redução "
    "clinicamente relevante de hiperpigmentação cutânea (manchas) em humanos?"
)

RESPOSTA = (
    "Sim, com ressalvas importantes: a evidência apoia um efeito clareador modesto da vitamina C "
    "tópica, principalmente pela inibição da melanogênese, mas o benefício depende criticamente da "
    "formulação, concentração, estabilidade do produto e tipo de mancha. Não é um agente de primeira "
    "linha e seus efeitos são modestos quando usados isoladamente."
)

NIVEL = "Moderada"
NIVEL_JUST = (
    "Existem ensaios clínicos randomizados e estudos controlados demonstrando eficácia, mas o corpo "
    "de evidência é heterogêneo em metodologia, com amostras pequenas e grande variação nas formulações."
)

FUNDAMENTACAO = [
    ("Mecanismo biológico (bem estabelecido)",
     "A vitamina C inibe a tirosinase, enzima-chave na síntese de melanina, por quelação do cobre no "
     "sítio ativo. Reduz a oxidação de DOPA-quinona e tem atividade antioxidante que atenua a "
     "pigmentação induzida por UV. Mecanismo plausível e bem descrito na literatura."),
    ("O que os estudos clínicos mostram",
     "ECRs com ácido L-ascórbico a 5–20% demonstraram redução significativa em índices de melanina e "
     "melhora em escores de melasma e hiperpigmentação pós-inflamatória. Eficácia inferior à "
     "hidroquinona 4% (padrão ouro), mas com perfil de segurança mais favorável para uso prolongado. "
     "Combinações com niacinamida, ácido kójico e filtro solar superam o uso isolado."),
    ("O problema crítico: estabilidade",
     "O ácido L-ascórbico é instável: oxida rápido com luz, ar e pH elevado, tornando-se inativo. "
     "Derivados mais estáveis têm melhor prateleira mas exigem conversão enzimática na pele. Um produto "
     "mal formulado ou deteriorado pode ter eficácia próxima de zero."),
    ("Tipo de mancha importa",
     "Evidência mais consistente para melasma superficial e hiperpigmentação pós-inflamatória. Para "
     "manchas dérmicas profundas, a penetração tópica é insuficiente e os resultados decepcionam."),
]

METODO = (
    "Revisão da literatura disponível sobre vitamina C tópica em hiperpigmentação, priorizando ECRs, "
    "revisões sistemáticas e meta-análises de dermatologia, com desfechos objetivos (mexametria, MASI "
    "score). Estudos in vitro/animais usados apenas para fundamentar mecanismo. Alegações de fabricantes "
    "sem suporte independente foram excluídas."
)

RESSALVAS = [
    "Viés de publicação: estudos negativos são sub-representados na literatura.",
    "Variabilidade de produto: ECRs usam formulações de laboratório, não cosméticos comerciais.",
    "Fotoproteção confundidora: protocolos incluem filtro solar, dificultando isolar a vitamina C.",
    "Amostras pequenas e seguimento curto (8–12 semanas) na maioria dos estudos.",
    "Eficácia varia com fotótipo e etiologia da mancha — fatores raramente estratificados.",
]

FONTES = [
    "Revisões sistemáticas e meta-análises sobre agentes clareadores em melasma (J Am Acad Dermatol; J Cosmetic Dermatol).",
    "ECRs comparando vitamina C tópica vs. hidroquinona e vs. placebo em hiperpigmentação.",
    "Estudos de estabilidade físico-química do ácido L-ascórbico (literatura de farmacotecnia).",
    "Obras de referência: Draelos ZD e Baumann L (Cosmetic Dermatology) — rastreáveis.",
]
NOTA_TRANSPARENCIA = (
    "Nota de transparência: nenhuma citação foi fabricada. Referências específicas com autores e anos "
    "podem ser fornecidas mediante acesso a base de dados; o acima reflete veículos reais e verificáveis."
)
# ══════════════════════════════════════════════════════════════════

OUTPUT = r'C:\Users\Usuario\OneDrive\Documentos\Claude\Projects\teste Automação\13_Servico_AnaliseCientifica\parecer_exemplo.pdf'
LOGO   = r'C:\Users\Usuario\OneDrive\Documentos\Claude\Projects\teste Automação\07_Recursos\identidade_visual\kronos_logo_oficial_transparente.png'

AZUL_MARINHO = colors.HexColor('#020c2a')
VIOLETA      = colors.HexColor('#4a0e90')
BRANCO       = colors.HexColor('#f0f4ff')
CINZA_CLARO  = colors.HexColor('#8898bb')
LILAS        = colors.HexColor('#a080ff')
W, H = A4

ELIPSE_CORES = ['#f0f4ff','#f0f4ff','#f0f4ff','#f0f4ff','#f0f4ff','#f0f4ff','#f0f4ff','#f0f4ff']
ELIPSE_OPAC  = [0.80,0.80,0.80,0.80,0.76,0.76,0.76,0.76,0.72,0.72,0.72,0.72,0.68,0.68,0.68,0.68,
                0.64,0.64,0.64,0.64,0.60,0.60,0.60,0.60,0.55,0.55,0.55,0.55,0.50,0.50,0.50,0.50,
                0.44,0.44,0.44,0.44,0.38,0.38,0.38,0.38,0.30,0.30,0.30,0.30,0.22,0.22,0.22,0.22,
                0.14,0.14,0.14,0.14]

def draw_elipses(canvas):
    sx = W / 1920
    rcx = 1380 * sx; rcy = H * 0.50; off = (1580 - 1380) * sx
    erx = 560 * sx; ery = 220 * sx
    for i, ang in enumerate(range(0, 154, 3)):
        cor = colors.HexColor(ELIPSE_CORES[i % 8])
        op  = ELIPSE_OPAC[i] if i < len(ELIPSE_OPAC) else 0.14
        canvas.saveState(); canvas.translate(rcx, rcy); canvas.rotate(ang)
        canvas.setStrokeColor(cor); canvas.setStrokeAlpha(op); canvas.setLineWidth(1.2)
        canvas.ellipse(off - erx, -ery, off + erx, ery, fill=0, stroke=1)
        canvas.restoreState()

LOGO_TOP = 0.6*cm; LOGO_H = 2.6*cm
SEP_Y = H - LOGO_TOP - LOGO_H - 0.5*cm
TOP_MARGIN = H - SEP_Y + 0.6*cm

def fundo(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AZUL_MARINHO); canvas.rect(0, 0, W, H, fill=1, stroke=0)
    draw_elipses(canvas)
    canvas.setFillColor(colors.Color(0.008, 0.047, 0.165, alpha=0.62))
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    if os.path.exists(LOGO):
        lw = 5.5*cm
        canvas.drawImage(LOGO, (W - lw)/2, H - LOGO_TOP - LOGO_H, width=lw, height=LOGO_H,
                         preserveAspectRatio=True, mask='auto')
    canvas.setStrokeColor(colors.Color(1, 1, 1, alpha=0.10)); canvas.setLineWidth(0.5)
    canvas.line(2*cm, SEP_Y, W - 2*cm, SEP_Y)
    canvas.setFont('Helvetica', 8); canvas.setFillColor(CINZA_CLARO)
    canvas.drawCentredString(W/2, 0.9*cm,
        'Kronos Intelligence  |  kronosintelligence.com.br  |  contato@kronosintelligence.com.br')
    canvas.setFont('Helvetica', 7); canvas.setFillColor(colors.Color(1, 1, 1, alpha=0.35))
    canvas.drawCentredString(W/2, 0.5*cm,
        'Parecer informativo e técnico-científico — não substitui consultoria profissional especializada.')
    canvas.restoreState()

def s(name, **kw): return ParagraphStyle(name, **kw)

titulo = s('TI', fontSize=17, textColor=BRANCO, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)
sub    = s('SU', fontSize=9, textColor=CINZA_CLARO, alignment=TA_CENTER, spaceAfter=2)
secao  = s('SE', fontSize=12, textColor=BRANCO, spaceBefore=12, spaceAfter=4, fontName='Helvetica-Bold')
corpo  = s('CO', fontSize=9.5, textColor=CINZA_CLARO, spaceAfter=4, fontName='Helvetica', leading=14)
destaque = s('DE', fontSize=11, textColor=BRANCO, spaceAfter=4, fontName='Helvetica-Bold', leading=15)
subt   = s('ST', fontSize=10, textColor=LILAS, spaceBefore=6, spaceAfter=2, fontName='Helvetica-Bold')
bullet = s('BU', fontSize=9.5, textColor=BRANCO, spaceAfter=3, fontName='Helvetica', leftIndent=12, leading=13)
nota   = s('NO', fontSize=8, textColor=CINZA_CLARO, spaceBefore=4, fontName='Helvetica-Oblique', leading=11)

doc = BaseDocTemplate(OUTPUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                      topMargin=TOP_MARGIN, bottomMargin=1.4*cm)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
doc.addPageTemplates([PageTemplate(id='kronos', frames=frame, onPage=fundo)])

story = []
story.append(Paragraph('Parecer Científico', titulo))
story.append(Paragraph(f'{CLIENTE_NOME}  ·  Solicitante: {SOLICITANTE}', sub))
story.append(Paragraph(f'Área: {AREA}  ·  Tipo: {TIPO}  ·  {DATA}', sub))
story.append(Spacer(1, 0.15*cm))
_lw = doc.width * 0.35
ln = Table([['']], colWidths=[_lw])
ln.hAlign = 'CENTER'
ln.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1.0, VIOLETA),
                        ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 0)]))
story.append(ln); story.append(Spacer(1, 0.3*cm))

def bloco(t):
    story.append(Paragraph(t, secao))
    story.append(HRFlowable(width='100%', thickness=0.5, color=VIOLETA, spaceAfter=4))

# Caixa de confiança (resposta + nível)
def caixa(label, valor, cor):
    p = Paragraph(f'<b>{label}</b>  {valor}', s('CX', fontSize=10, textColor=BRANCO, fontName='Helvetica', leading=14))
    tb = Table([[p]], colWidths=[doc.width])
    tb.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0d1a3a')),
                            ('BOX', (0,0), (-1,-1), 1, cor), ('LEFTPADDING', (0,0), (-1,-1), 10),
                            ('RIGHTPADDING', (0,0), (-1,-1), 10), ('TOPPADDING', (0,0), (-1,-1), 8),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 8)]))
    story.append(tb); story.append(Spacer(1, 0.2*cm))

bloco('Pergunta analisada')
story.append(Paragraph(PERGUNTA, corpo))

bloco('Resposta direta')
story.append(Paragraph(RESPOSTA, destaque))
story.append(Spacer(1, 0.15*cm))
caixa('Nível de evidência:', f'{NIVEL}', LILAS)
story.append(Paragraph(NIVEL_JUST, corpo))

bloco('Fundamentação')
for t, txt in FUNDAMENTACAO:
    story.append(Paragraph(t, subt))
    story.append(Paragraph(txt, corpo))

bloco('Método')
story.append(Paragraph(METODO, corpo))

bloco('Ressalvas')
for r in RESSALVAS:
    story.append(Paragraph(f'<font color="#a080ff">•</font>  {r}', bullet))

bloco('Fontes')
for f in FONTES:
    story.append(Paragraph(f'<font color="#a080ff">•</font>  {f}', bullet))
story.append(Paragraph(NOTA_TRANSPARENCIA, nota))

doc.build(story)
print('PDF gerado:', OUTPUT)
