# -*- coding: utf-8 -*-
"""Gera 3 PDFs jurídicos fictícios (divórcio, alimentos, trabalhista) para
testar a análise de PDF da Léa. Documentos de DEMONSTRAÇÃO — partes fictícias.
Rodar: uv run --with reportlab python gerar_docs_teste.py
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUT = os.path.dirname(os.path.abspath(__file__))

ss = getSampleStyleSheet()
H = ParagraphStyle("H", parent=ss["Normal"], fontName="Times-Bold",
                   fontSize=11, alignment=TA_CENTER, spaceAfter=10, leading=15)
TIT = ParagraphStyle("TIT", parent=ss["Normal"], fontName="Times-Bold",
                     fontSize=12, alignment=TA_CENTER, spaceBefore=6, spaceAfter=12, leading=16)
SEC = ParagraphStyle("SEC", parent=ss["Normal"], fontName="Times-Bold",
                     fontSize=10.5, alignment=TA_JUSTIFY, spaceBefore=10, spaceAfter=4)
P = ParagraphStyle("P", parent=ss["Normal"], fontName="Times-Roman",
                   fontSize=10.5, alignment=TA_JUSTIFY, spaceAfter=6, leading=15, firstLineIndent=20)
ASS = ParagraphStyle("ASS", parent=ss["Normal"], fontName="Times-Roman",
                     fontSize=10.5, alignment=TA_CENTER, spaceBefore=6, leading=14)
RODAPE = ParagraphStyle("RODAPE", parent=ss["Normal"], fontName="Times-Italic",
                        fontSize=7.5, alignment=TA_CENTER, textColor="#888888")


def build(nome, blocos):
    path = os.path.join(OUT, nome)
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=2.2*cm, bottomMargin=2*cm,
                            leftMargin=2.5*cm, rightMargin=2.5*cm)
    story = []
    for style, txt in blocos:
        if style == "SP":
            story.append(Spacer(1, txt))
        else:
            story.append(Paragraph(txt, {"H": H, "TIT": TIT, "SEC": SEC,
                                          "P": P, "ASS": ASS, "RODAPE": RODAPE}[style]))
    doc.build(story)
    print("gerado:", path)


# ------------------------------------------------------------------ DIVÓRCIO
build("01_peticao_divorcio.pdf", [
 ("H", "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA 2ª VARA DE FAMÍLIA E SUCESSÕES DA COMARCA DE CAMPINAS – ESTADO DE SÃO PAULO"),
 ("SP", 10),
 ("P", "Processo nº 1002345-67.2026.8.26.0114 &nbsp;&nbsp;|&nbsp;&nbsp; Classe: Divórcio Consensual"),
 ("SP", 6),
 ("TIT", "AÇÃO DE DIVÓRCIO CONSENSUAL c/c PARTILHA DE BENS, GUARDA COMPARTILHADA E ALIMENTOS"),
 ("P", "<b>MARCELA RIBEIRO DE SOUZA</b>, brasileira, casada, professora, RG nº 34.567.890-1 SSP/SP, CPF nº 123.456.789-00, e <b>RODRIGO ALVES PEREIRA</b>, brasileiro, casado, engenheiro civil, RG nº 45.678.901-2 SSP/SP, CPF nº 987.654.321-00, ambos residentes e domiciliados na cidade de Campinas/SP, por sua advogada infra-assinada (procuração anexa), vêm, respeitosamente, à presença de Vossa Excelência, propor a presente ação, pelos fatos e fundamentos a seguir expostos."),
 ("SEC", "I – DOS FATOS"),
 ("P", "As partes contraíram matrimônio em <b>15 de março de 2015</b>, sob o regime de comunhão parcial de bens, conforme certidão de casamento anexa. Da união adveio um filho, <b>LUCAS RIBEIRO PEREIRA</b>, nascido em 08 de junho de 2018, atualmente com 8 anos de idade. As partes encontram-se separadas de fato desde <b>janeiro de 2026</b>, inexistindo qualquer possibilidade de reconciliação, razão pela qual pretendem formalizar o divórcio de maneira consensual."),
 ("SEC", "II – DA GUARDA E DA CONVIVÊNCIA"),
 ("P", "Ajustam as partes a <b>guarda compartilhada</b> do menor, fixada a residência de referência junto à genitora. O genitor exercerá a convivência em fins de semana alternados, das 18h de sexta-feira às 18h de domingo, além de metade dos períodos de férias escolares e datas comemorativas de forma alternada."),
 ("SEC", "III – DOS ALIMENTOS"),
 ("P", "O genitor pagará, a título de <b>pensão alimentícia</b> em favor do filho, quantia equivalente a <b>30% (trinta por cento) de seus rendimentos líquidos</b>, atualmente estimada em <b>R$ 2.400,00 (dois mil e quatrocentos reais)</b> mensais, mediante depósito em conta bancária da genitora até o dia 10 de cada mês, com início no mês subsequente à homologação."),
 ("SEC", "IV – DA PARTILHA DE BENS"),
 ("P", "Integram o patrimônio comum a ser partilhado: (a) imóvel residencial situado na Rua das Acácias, nº 250, bairro Taquaral, Campinas/SP, matrícula nº 78.912, avaliado em <b>R$ 480.000,00</b>, que caberá à requerente mediante reposição da meação; (b) veículo automotor marca Volkswagen, modelo Nivus, ano 2022, placa FKR-2A34, avaliado em <b>R$ 95.000,00</b>, que caberá ao requerente."),
 ("SEC", "V – DOS PEDIDOS"),
 ("P", "Ante o exposto, requerem: (a) a homologação do acordo e a <b>decretação do divórcio</b>; (b) a homologação da guarda compartilhada e do regime de convivência; (c) a fixação dos alimentos no percentual acima; (d) a homologação da partilha; (e) a designação de audiência de ratificação; (f) que a requerente volte a usar o nome de solteira."),
 ("P", "Dá-se à causa o valor de <b>R$ 575.000,00 (quinhentos e setenta e cinco mil reais)</b>."),
 ("SP", 6),
 ("P", "<b>Audiência de ratificação designada para o dia 24 de julho de 2026, às 14h00</b>, na sala 3 do Fórum de Campinas."),
 ("SP", 10),
 ("ASS", "Termos em que, pede deferimento.<br/>Campinas/SP, 30 de junho de 2026."),
 ("SP", 14),
 ("ASS", "_______________________________________<br/><b>Dra. Marina Nogueira</b> — OAB/SP nº 234.567<br/>Ferraz &amp; Nogueira Advogados Associados"),
 ("SP", 16),
 ("RODAPE", "Documento fictício gerado para demonstração da Kronos Intelligence. Nomes, números e processos são ilustrativos e não correspondem a pessoas ou autos reais."),
])

# ------------------------------------------------------------------ ALIMENTOS
build("02_acao_alimentos.pdf", [
 ("H", "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA 1ª VARA DE FAMÍLIA E SUCESSÕES DA COMARCA DE CAMPINAS – ESTADO DE SÃO PAULO"),
 ("SP", 10),
 ("P", "Processo nº 1004987-21.2026.8.26.0114 &nbsp;&nbsp;|&nbsp;&nbsp; Classe: Alimentos – Lei Especial nº 5.478/68"),
 ("SP", 6),
 ("TIT", "AÇÃO DE ALIMENTOS COM PEDIDO DE FIXAÇÃO DE ALIMENTOS PROVISÓRIOS"),
 ("P", "<b>SOFIA MARTINS LIMA</b>, menor impúbere, neste ato representada por sua genitora <b>ANA PAULA MARTINS</b>, brasileira, solteira, auxiliar administrativa, RG nº 28.111.222-3, CPF nº 111.222.333-44, residente na Rua Piracicaba, nº 78, Campinas/SP, por sua advogada, vem propor a presente <b>AÇÃO DE ALIMENTOS</b> em face de <b>CARLOS EDUARDO LIMA</b>, brasileiro, autônomo, CPF nº 555.666.777-88, residente na Av. John Boyd Dunlop, nº 1200, Campinas/SP, pelas razões a seguir."),
 ("SEC", "I – DA FILIAÇÃO E DA NECESSIDADE"),
 ("P", "A requerente, nascida em <b>12 de setembro de 2019</b>, é filha do requerido, conforme certidão de nascimento anexa. Com 6 anos de idade, encontra-se em fase escolar, demandando despesas com educação, saúde, vestuário e alimentação, cujo custo mensal é estimado em <b>R$ 1.800,00</b>. A genitora, sozinha, não possui condições de arcar integralmente com tais despesas."),
 ("SEC", "II – DA POSSIBILIDADE DO ALIMENTANTE"),
 ("P", "O requerido exerce atividade autônoma no ramo de comércio, auferindo renda mensal estimada em <b>R$ 6.000,00</b>, possuindo plena capacidade de contribuir com o sustento da filha, em observância ao binômio necessidade-possibilidade."),
 ("SEC", "III – DOS PEDIDOS"),
 ("P", "Requer-se: (a) a fixação de <b>alimentos provisórios</b> desde já, no importe de <b>R$ 1.100,00 (mil e cem reais)</b> mensais, equivalentes a aproximadamente 30% dos rendimentos do requerido; (b) a citação do requerido para, querendo, contestar no <b>prazo legal de 15 (quinze) dias</b>; (c) a procedência final para consolidar os alimentos definitivos; (d) os benefícios da justiça gratuita."),
 ("P", "Dá-se à causa o valor de <b>R$ 13.200,00 (treze mil e duzentos reais)</b>, correspondente a doze prestações."),
 ("SP", 6),
 ("P", "<b>Audiência de conciliação designada para 05 de agosto de 2026, às 10h30.</b> O não comparecimento injustificado do requerido poderá acarretar as penalidades legais."),
 ("SP", 10),
 ("ASS", "Termos em que, pede deferimento.<br/>Campinas/SP, 27 de junho de 2026."),
 ("SP", 14),
 ("ASS", "_______________________________________<br/><b>Dra. Marina Nogueira</b> — OAB/SP nº 234.567<br/>Ferraz &amp; Nogueira Advogados Associados"),
 ("SP", 16),
 ("RODAPE", "Documento fictício gerado para demonstração da Kronos Intelligence. Nomes, números e processos são ilustrativos e não correspondem a pessoas ou autos reais."),
])

# ------------------------------------------------------------------ TRABALHISTA
build("03_reclamacao_trabalhista.pdf", [
 ("H", "EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DO TRABALHO DA ___ª VARA DO TRABALHO DE CAMPINAS – SP"),
 ("SP", 10),
 ("P", "Processo nº 1000765-49.2026.5.15.0092 &nbsp;&nbsp;|&nbsp;&nbsp; Rito: Ordinário"),
 ("SP", 6),
 ("TIT", "RECLAMAÇÃO TRABALHISTA"),
 ("P", "<b>JOSÉ ANTÔNIO FERREIRA</b>, brasileiro, casado, operador de máquinas, CPF nº 222.333.444-55, CTPS nº 0012345 série 00234-SP, residente na Rua dos Trilhos, nº 340, Campinas/SP, por seu advogado, vem propor a presente <b>RECLAMAÇÃO TRABALHISTA</b> em face de <b>METALúRGICA HORIZONTE LTDA.</b>, CNPJ nº 12.345.678/0001-90, com sede na Rod. Dom Pedro I, km 132, Campinas/SP, pelos fundamentos a seguir."),
 ("SEC", "I – DO CONTRATO DE TRABALHO"),
 ("P", "O reclamante foi admitido em <b>10 de fevereiro de 2020</b> para exercer a função de operador de máquinas, com último salário mensal de <b>R$ 3.200,00</b>. Foi <b>dispensado sem justa causa em 15 de maio de 2026</b>, não lhe tendo sido quitadas corretamente as verbas rescisórias, tampouco recolhido integralmente o FGTS do período."),
 ("SEC", "II – DAS HORAS EXTRAS E ADICIONAL NOTURNO"),
 ("P", "Durante todo o contrato, o reclamante cumpriu jornada média das 14h00 às 23h30, de segunda a sábado, laborando habitualmente <b>2 horas extras diárias</b> não pagas, além de trabalho em horário noturno sem o respectivo <b>adicional noturno de 20%</b>, verbas ora postuladas com reflexos em férias, 13º salário, FGTS e aviso prévio."),
 ("SEC", "III – DOS PEDIDOS"),
 ("P", "Requer a condenação da reclamada ao pagamento de: (a) horas extras e reflexos; (b) adicional noturno e reflexos; (c) verbas rescisórias (aviso prévio indenizado, saldo de salário, férias proporcionais + 1/3, 13º proporcional); (d) <b>multa de 40% do FGTS</b> e diferenças de depósitos; (e) multa dos arts. 467 e 477 da CLT; (f) indenização por danos morais no valor de <b>R$ 10.000,00</b>; (g) justiça gratuita e honorários sucumbenciais."),
 ("P", "Dá-se à causa o valor de <b>R$ 85.000,00 (oitenta e cinco mil reais)</b>."),
 ("SP", 6),
 ("P", "<b>Audiência inicial (una) designada para 18 de agosto de 2026, às 09h15</b>, na sala de audiências da Vara. A ausência do reclamante importa arquivamento; a da reclamada, revelia e confissão."),
 ("SP", 10),
 ("ASS", "Termos em que, pede deferimento.<br/>Campinas/SP, 26 de junho de 2026."),
 ("SP", 14),
 ("ASS", "_______________________________________<br/><b>Dr. Eduardo Ferraz</b> — OAB/SP nº 198.432<br/>Ferraz &amp; Nogueira Advogados Associados"),
 ("SP", 16),
 ("RODAPE", "Documento fictício gerado para demonstração da Kronos Intelligence. Nomes, números e processos são ilustrativos e não correspondem a pessoas ou autos reais."),
])

print("\nOK — 3 PDFs em:", OUT)
