# -*- coding: utf-8 -*-
"""Gera o PDF da lista de materiais do robô Ferrão, organizada por vertente."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether)

NAVY = colors.HexColor('#1e2a4a')
AZUL = colors.HexColor('#3b82f6')
CINZA = colors.HexColor('#64748b')
CINZA_CLARO = colors.HexColor('#f1f5f9')
LINHA = colors.HexColor('#cbd5e1')
VERDE = colors.HexColor('#15803d')
VERDE_BG = colors.HexColor('#dcfce7')
AMBAR = colors.HexColor('#b45309')
AMBAR_BG = colors.HexColor('#fef3c7')
ROXO = colors.HexColor('#6d28d9')
ROXO_BG = colors.HexColor('#ede9fe')

W, H = A4
MARG = 16 * mm

st_titulo = ParagraphStyle('titulo', fontName='Helvetica-Bold', fontSize=23,
                           textColor=NAVY, leading=27, spaceAfter=2)
st_sub = ParagraphStyle('sub', fontName='Helvetica', fontSize=10.5,
                        textColor=CINZA, leading=14, spaceAfter=10)
st_h2 = ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=13.5,
                       textColor=NAVY, leading=17, spaceBefore=13, spaceAfter=5)
st_h3 = ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=10.5,
                       textColor=AZUL, leading=13, spaceBefore=7, spaceAfter=3)
st_p = ParagraphStyle('p', fontName='Helvetica', fontSize=9.2,
                      textColor=colors.HexColor('#334155'), leading=12.6, spaceAfter=5)
st_nota = ParagraphStyle('nota', fontName='Helvetica-Oblique', fontSize=8.4,
                         textColor=CINZA, leading=11.5, spaceAfter=4)
# celulas
st_c = ParagraphStyle('c', fontName='Helvetica', fontSize=8, leading=10.2,
                      textColor=colors.HexColor('#334155'))
st_cb = ParagraphStyle('cb', fontName='Helvetica-Bold', fontSize=8, leading=10.2,
                       textColor=NAVY)
st_ch = ParagraphStyle('ch', fontName='Helvetica-Bold', fontSize=8, leading=10.2,
                       textColor=colors.white)
st_badge = ParagraphStyle('badge', fontName='Helvetica-Bold', fontSize=6.6,
                          leading=8.4, alignment=1)


def badge(tipo):
    m = {'T': ('TENHO', VERDE), 'S': ('SUCATA', AMBAR), 'C': ('COMPRAR', ROXO)}
    txt, cor = m[tipo]
    return Paragraph('<font color="%s">%s</font>' % (cor.hexval(), txt), st_badge)


def bg(tipo):
    return {'T': VERDE_BG, 'S': AMBAR_BG, 'C': ROXO_BG}[tipo]


def tabela(linhas, larguras, cabecalho):
    """linhas: [(status, item, qtd, origem, funcao)]"""
    data = [[Paragraph(h, st_ch) for h in cabecalho]]
    estilo = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, LINHA),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
    ]
    for i, (s, item, qtd, orig, func) in enumerate(linhas, start=1):
        data.append([badge(s), Paragraph(item, st_cb), Paragraph(qtd, st_c),
                     Paragraph(orig, st_c), Paragraph(func, st_c)])
        estilo.append(('BACKGROUND', (0, i), (0, i), bg(s)))
        if i % 2 == 0:
            estilo.append(('BACKGROUND', (1, i), (-1, i), CINZA_CLARO))
    t = Table(data, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle(estilo))
    return t


LARG = [15 * mm, 33 * mm, 11 * mm, 42 * mm, 77 * mm]
CAB = ['Status', 'Item', 'Qtd', 'Onde consigo / custo', 'Para que serve no Ferrao']

story = []
A = story.append

# ---------------- CAPA / RESUMO ----------------
A(Paragraph('Projeto Ferrao - Lista de Materiais', st_titulo))
A(Paragraph('Robo humanoide de sucata &bull; Nivel 1 (torso em base fixa) &bull; '
            'organizado por vertente &bull; 25/07/2026', st_sub))

leg = Table([[badge('T'), Paragraph('Ja tenho em casa', st_c),
              badge('S'), Paragraph('Buscar no ferro-velho / sucata (custo zero)', st_c),
              badge('C'), Paragraph('Precisa comprar', st_c)]],
            colWidths=[17 * mm, 30 * mm, 17 * mm, 60 * mm, 19 * mm, 35 * mm])
leg.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, 0), VERDE_BG),
    ('BACKGROUND', (2, 0), (2, 0), AMBAR_BG),
    ('BACKGROUND', (4, 0), (4, 0), ROXO_BG),
    ('BOX', (0, 0), (-1, -1), 0.5, LINHA),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
A(leg)
A(Spacer(1, 9))

A(Paragraph('Onde voce esta agora', st_h2))
A(Paragraph('Boa noticia: <b>a parte estrutural do projeto ja esta praticamente resolvida</b>. '
            'As duas cadeiras de rodinha, o PVC e o caixote de madeira cobrem base, coluna, '
            'ossos e torso - que era o material mais volumoso e chato de conseguir. '
            'Sobrou o que cabe numa caixa de sapato: eletronica, motores e ferragem.', st_p))

resumo = Table([
    [Paragraph('O QUE JA TEM', st_ch), Paragraph('O QUE FALTA', st_ch)],
    [Paragraph('&bull; 2 cadeiras de rodinha (base + coluna, e uma vira doadora de pecas)<br/>'
               '&bull; Cano PVC (bracos, antebracos, pescoco)<br/>'
               '&bull; Caixote de madeira (torso e bandeja da eletronica)<br/>'
               '&bull; Ferramentas basicas (furadeira, chaves, alicate, Dremel)', st_c),
     Paragraph('&bull; 2 motores de limpador de para-brisa <b>(ferro-velho)</b><br/>'
               '&bull; Fonte ATX de PC velho <b>(sucata)</b><br/>'
               '&bull; Toda a eletronica de controle e sensores <b>(comprar)</b><br/>'
               '&bull; Ferragem: parafusos, cantoneiras, abracadeiras <b>(comprar)</b>', st_c)],
], colWidths=[89 * mm, 89 * mm])
resumo.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), NAVY),
    ('BACKGROUND', (0, 1), (0, 1), VERDE_BG),
    ('BACKGROUND', (1, 1), (1, 1), ROXO_BG),
    ('GRID', (0, 0), (-1, -1), 0.4, LINHA),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
A(resumo)
A(Spacer(1, 7))
A(Paragraph('<b>Total a comprar: aproximadamente R$ 595</b>, diluido em 7 compras pequenas '
            '(a primeira e de R$ 145). A estrutura que voce ja tem em casa vale uns R$ 150-200 '
            'que sairam da conta. Detalhe das compras por fase na ultima pagina.', st_p))

# ---------------- 1. MECANICA - ESTRUTURA ----------------
A(Paragraph('1. Vertente MECANICA - Estrutura (o esqueleto)', st_h2))
A(Paragraph('Tudo que sustenta peso e da forma ao robo. Nao tem eletricidade nenhuma aqui.', st_nota))
A(tabela([
    ('T', 'Cadeira de rodinha nº 1', '1',
     'Voce ja tem',
     'Estrela de 5 patas = base; coluna a gas = coluna vertebral. E o item que elimina '
     'a parte mais dificil do projeto (base estavel e alta).'),
    ('T', 'Cadeira de rodinha nº 2', '1',
     'Voce ja tem',
     'Doadora de pecas: rodizios reserva, parafusos M6, mecanismo do assento e a segunda '
     'coluna caso voce erre um furo. Nao desmonte antes da hora - guarde inteira.'),
    ('T', 'Cano PVC 40 mm (bracos)', '~1,2 m',
     'Voce ja tem',
     'Umero (28 cm x2) e antebraco (24 cm x2). Se o seu for 50 mm, use no umero e '
     'procure um mais fino pro antebraco - a ponta do braco tem que ser leve.'),
    ('T', 'Caixote de madeira', '1',
     'Voce ja tem',
     'As tabuas viram: quadro em H do torso, placa dos ombros, disco flange no topo da '
     'coluna e a bandeja da eletronica. Caixote de feira serve; ripa fina exige dobrar a espessura.'),
    ('S', 'Pote plastico rigido', '1',
     'Cozinha / sucata',
     'Cranio da cabeca. Tem que ser leve - quem segura ele e um servo pequeno.'),
    ('S', 'Rolamento de skate 608', '4',
     'Skate velho / bike',
     'Mancais das juntas (ombro e pescoco). Furo de 8 mm casa exato com barra roscada M8.'),
    ('S', 'Halter velho / saco de areia', '5-10 kg',
     'Casa / sucata',
     'Lastro na base. Braco esticado de 40 cm faz alavanca - sem lastro o robo tomba pra frente.'),
    ('S', 'Conexoes PVC (joelho, T)', '4-6',
     'Sobra de obra',
     'Junta falsa: da forma de ombro/punho sem precisar usinar nada.'),
], LARG, CAB))

# ---------------- 2. MECANICA - MOVIMENTO ----------------
A(Paragraph('2. Vertente MECANICA - Atuadores e movimento (os musculos)', st_h2))
A(Paragraph('Tudo que gira. Esta e a vertente que voce ainda nao tem nada - e a mais '
            'importante do projeto.', st_nota))
A(tabela([
    ('S', 'Motor de limpador de para-brisa 12V', '2',
     'Ferro-velho (R$ 0-60 cada se for comprado usado)',
     'ATUADOR DOS OMBROS - o coracao do projeto. Torque enorme e reducao sem-fim '
     '<b>autotravante</b>: desligou, o braco fica parado onde estava. IMPORTANTE: peca '
     '<b>o braco do limpador junto</b> (a haste da palheta) - o clamp dela e a sua fixacao pronta no eixo.'),
    ('C', 'Servo MG996R (metal, ~10 kg.cm)', '3',
     'R$ 35 cada = R$ 105 (online)',
     '2 cotovelos + 1 giro do pescoco (pan). Tem que ser de <b>engrenagem metalica</b> - '
     'os de plastico espanam no primeiro esbarrao.'),
    ('C', 'Servo MG90S (mini, metal)', '3',
     'R$ 20 cada = R$ 60 (online)',
     'Inclinacao da cabeca (tilt), garra e punho. Leves, ficam nas pontas onde peso atrapalha.'),
    ('S', 'Cabo de freio de bike ou linha encerada', '2 m',
     'Bicicletaria / sucata',
     'Tendao da garra: o servo puxa o cabo, os dedos fecham.'),
    ('S', 'Elastico / borracha de dinheiro', '6',
     'Casa',
     'Dorso dos dedos - reabrem a garra quando o servo solta. Se algo esbarra, o elastico '
     'cede em vez de espanar o servo.'),
    ('S', 'Mangueirinha de silicone fina', '10 cm',
     'Sucata (combustivel/aquario)',
     'Acoplamento flexivel entre o eixo do motor e o potenciometro. Acoplamento rigido '
     'quebraria o pot na primeira vibracao.'),
    ('S', 'Corrente + coroa de bike (opcional)', '1',
     'Ferro-velho',
     'So no Nivel 2 (rodas), se o eixo do motor nao alinhar com a roda. Nao usar agora.'),
], LARG, CAB))

# ---------------- 3. FIXACAO ----------------
A(Paragraph('3. Vertente FIXACAO - Ferragem (o que segura tudo junto)', st_h2))
A(Paragraph('Vertente barata e que todo mundo subestima. Parafuso errado = junta que afrouxa '
            'toda semana ou PVC rachado.', st_nota))
A(tabela([
    ('C', 'Kit parafusos M3 / M4 / M5 (varios comprimentos)', '1 kit',
     'R$ 40 (loja de parafuso ou online)',
     'M3 fixa servos e eletronica; M5 prende braco na haste do limpador; M4 nos suportes. '
     'Comprar kit sortido sai mais barato que avulso.'),
    ('C', 'Porca nylock (trava de nylon) M3/M4/M5', '~60',
     'R$ 15 (junto do kit)',
     'Porca comum <b>solta em uma semana</b> de robo mexendo. Nylock nao afrouxa com vibracao. '
     'Use em toda junta que se move.'),
    ('C', 'Arruela lisa M3/M4/M5', '~80',
     'R$ 10',
     'Espalha a pressao do aperto - e o que impede o parafuso de rachar o PVC e a madeira. '
     'Sempre dos dois lados.'),
    ('C', 'Parafuso M6 x 30/40 + porca', '10',
     'R$ 12',
     'Fixa o motor de limpador (as 3 orelhas originais dele) e o disco flange na coluna da cadeira.'),
    ('C', 'Cantoneira de aco pequena', '8',
     'R$ 15',
     'Junta madeira-com-madeira no torso. Cantoneira, nunca parafuso no topo da tabua - '
     'topo racha a madeira.'),
    ('C', 'Fita perfurada galvanizada', '1 rolo',
     'R$ 12',
     '"Meccano de loja de construcao": chapinha furada que voce dobra com alicate. '
     'Resolve 90% dos suportes de sensor, pot e motor.'),
    ('C', 'Abracadeira rosca sem-fim 1½" a 2"', '8',
     'R$ 24',
     'Prende coisas no cano PVC <b>sem furar</b> - furo no PVC enfraquece o braco.'),
    ('C', 'Barra roscada M8 + porcas + arruelas', '1 m',
     'R$ 15',
     'Eixos das juntas que giram em rolamento 608.'),
    ('S', 'Parafusos M3 diversos', 'punhado',
     'Sucata de PC / impressora',
     'Todo PC velho tem dezenas. Servem pra fixar placas na bandeja.'),
], LARG, CAB))

# ---------------- 4. ELETRICA ----------------
A(Paragraph('4. Vertente ELETRICA - Energia e protecao (o sangue)', st_h2))
A(Paragraph('Aqui mora o risco real de incendio do projeto. Nao economize nem improvise '
            'nesta vertente - e a mais barata de todas.', st_nota))
A(tabela([
    ('S', 'Fonte ATX de PC velho', '1',
     'Sucata de torre (R$ 0)',
     'Alimenta o robo inteiro: da <b>12V</b> (motores) e <b>5V</b> (servos e logica) com '
     'corrente de sobra e protecao contra curto embutida. Liga juntando o fio <b>verde</b> '
     'num <b>preto</b>. E a peca de sucata mais valiosa do projeto: economiza ~R$ 110.'),
    ('C', 'Fusivel lamina 10A + 5A com porta-fusivel inline', '2+2',
     'R$ 12 (auto pecas)',
     'A fonte entrega 15A+: um curto derrete fio e comeca incendio. O fusivel morre no lugar '
     'da fiacao. 10A na linha dos motores, 5A na dos servos.'),
    ('C', 'Chave gangorra grande (botao de emergencia)', '1',
     'R$ 10',
     'Corta a forca dos motores num tapa, mantendo a logica viva pra voce ver o que houve. '
     'Fica sempre ao alcance da mao durante os testes.'),
    ('C', 'Fio flexivel 1,5 mm² (vermelho e preto)', '5 m',
     'R$ 20',
     'Linha de 12V dos motores. Fio fino demais esquenta - 1,5 mm² e o minimo aqui.'),
    ('C', 'Capacitor 1000 uF/16V + 100 nF', '2 + 4',
     'R$ 10',
     'Filtro anti-ruido. Motor escovado "suja" a linha eletrica e reseta o microcontrolador '
     'do nada - esse e o bug mais chato de diagnosticar sem os capacitores.'),
    ('C', 'Termorretratil / fita isolante', '1 kit',
     'R$ 12',
     'Toda emenda coberta. Nada de fio encapado com esperanca.'),
    ('S', 'Fios e conectores diversos', '-',
     'Sucata de PC',
     'Os proprios cabos da fonte ATX ja tem conectores uteis. Nao corte tudo - va cortando '
     'conforme precisa.'),
], LARG, CAB))

# ---------------- 5. ELETRONICA ----------------
A(Paragraph('5. Vertente ELETRONICA - Controle e sensores (o cerebro e os sentidos)', st_h2))
A(Paragraph('A vertente que voce compra 100% online. Tudo cabe numa caixa de sapato.', st_nota))
A(tabela([
    ('C', 'ESP32 DevKit V1', '1',
     'R$ 35',
     'O cerebro. Escolhido no lugar do Arduino Uno porque ja tem <b>Wi-Fi embutido</b> - '
     'e ele que serve o painel de controle no navegador do seu celular, sem comprar modulo extra.'),
    ('C', 'PCA9685 (driver de 16 servos, I2C)', '1',
     'R$ 25',
     'O "maestro" dos servos: recebe um comando do ESP32 e cuida do sinal dos 6 servos sozinha, '
     'com alimentacao separada. Sem ela, os servos tremem e a placa reseta.'),
    ('C', 'Driver BTS7960 (IBT-2, 43A)', '2',
     'R$ 40 cada = R$ 80',
     'Um por motor de limpador. <b>NAO compre L298N</b>: motor travado puxa 12-20A e o L298N '
     '(2A) solta fumaca na primeira prendida. O driver e a torneira - precisa aguentar a pressao do cano.'),
    ('C', 'Sensor ultrassonico HC-SR04', '2',
     'R$ 12 cada = R$ 24',
     'Os "olhos": medem distancia por eco, igual morcego. Dois lado a lado dao nocao de '
     'esquerda/direita - e por eles que o robo percebe alguem chegando.'),
    ('C', 'Potenciometro 10k linear', '4',
     'R$ 5 cada = R$ 20',
     'O "labirinto do ouvido" do ombro: acoplado ao eixo, diz ao ESP32 o angulo real do braco. '
     'Sem ele o motor de limpador e cego. Compre 4: 2 em uso, 2 reserva.'),
    ('C', 'Protoboard 830 furos + kit jumpers', '1',
     'R$ 35',
     'Bancada de teste. Tudo funciona na protoboard <b>antes</b> de virar fiacao definitiva.'),
    ('S', 'Microswitch (chave fim-de-curso)', '4',
     'Impressora / mouse velho',
     'Limite fisico de cada ombro. O motor de limpador nao para por esforco - ele quebra o que '
     'estiver no caminho. O microswitch e o disjuntor mecanico da junta.'),
    ('C', 'Resistores 1k e 2k2', '10',
     'R$ 5',
     'Divisor de tensao no pino ECHO do HC-SR04: o sensor devolve 5V e o ESP32 e de 3,3V. '
     'Sem o divisor voce queima a entrada da placa.'),
], LARG, CAB))

# ---------------- 6. VOZ E VISAO ----------------
A(Paragraph('6. Vertente VOZ E VISAO - Camadas de inteligencia (opcional, depois)', st_h2))
A(Paragraph('Nao compre nada disso agora. Sao as camadas 2, 3 e 4 do documento tecnico - '
            'entram quando o corpo ja estiver funcionando.', st_nota))
A(tabela([
    ('C', 'DFPlayer Mini + cartao microSD', '1',
     'R$ 15 + R$ 20',
     'CAMADA 2 - FALAR. Toca MP3 sozinho: o ESP32 so diz "toca a faixa 3". Voce grava as '
     'frases com TTS e ele cumprimenta quem chega.'),
    ('S', 'Alto-falante pequeno (3W)', '1',
     'Caixinha de som velha',
     'Saida de audio do DFPlayer. Qualquer speaker de PC serve.'),
    ('C', 'Microfone INMP441 (I2S digital)', '1',
     'R$ 20',
     'CAMADA 3 - OUVIR. Manda o audio por Wi-Fi pro PC, que roda transcricao + Claude + voz '
     'e devolve a resposta. Mesma arquitetura dos seus bots de WhatsApp, trocando o WhatsApp por um microfone.'),
    ('C', 'ESP32-CAM', '1',
     'R$ 45',
     'CAMADA 4 - VER. Fica no cranio, <b>separada</b> do ESP32 de controle. Detecta rosto '
     'sozinha (a cabeca segue a pessoa) e manda o frame pro Claude quando precisa identificar algo.'),
], LARG, CAB))

# ---------------- 7. CONSUMIVEIS ----------------
A(Paragraph('7. Vertente CONSUMIVEIS E PROTECAO', st_h2))
A(tabela([
    ('C', 'Oculos de protecao', '1',
     'R$ 15',
     'Obrigatorio no Dremel: caco de disco de corte voa. Item mais barato da lista e o unico '
     'insubstituivel.'),
    ('C', 'Broca 3, 4, 5, 6 e 8 mm (metal)', '1 jogo',
     'R$ 30 (se nao tiver)',
     'Furo-guia do diametro certo e o que impede o PVC de rachar.'),
    ('C', 'Disco de corte para Dremel', '5',
     'R$ 15',
     'Cortar PVC, a haste do limpador e chapinha. Sao consumiveis - quebram mesmo.'),
    ('S', 'Lixa e lima pequena', '-',
     'Casa',
     'Toda peca cortada fica com rebarba afiada. Tirar na hora, nao "depois eu vejo".'),
    ('C', 'Luva de raspa (triagem de sucata)', '1 par',
     'R$ 15',
     'Peca de ferro-velho vem com graxa e aresta viva escondida.'),
    ('C', 'Desengraxante / detergente', '1',
     'R$ 10',
     'Lavar toda peca de sucata antes de montar. Graxa velha ataca plastico e suja tudo.'),
], LARG, CAB))

story.append(Spacer(1, 4))

# ---------------- ORDEM DE COMPRA ----------------
A(Paragraph('8. Ordem de compra - nao compre tudo de uma vez', st_h2))
A(Paragraph('Cada compra so acontece quando a etapa anterior passou no teste. Se o projeto '
            'pausar, voce nao fica com R$ 600 de peca parada na gaveta.', st_p))

fases = [
    ['FASE', 'O QUE COMPRAR', 'CUSTO', 'LIBERA A ETAPA'],
    ['A', 'ESP32 + PCA9685 + 1 servo MG996R + 1 HC-SR04 + protoboard e jumpers + resistores',
     'R$ 145', 'Bancada eletronica: servo varrendo e sensor medindo distancia'],
    ['B', '1 MG996R + 2 MG90S + 1 HC-SR04 + parafusos M3',
     'R$ 100', 'Cabeca e pescoco: ela vira sozinha pra quem chega'],
    ['C', 'Kit parafusos + nylock + arruelas + cantoneiras + fita perfurada + abracadeiras + M6',
     'R$ 90', 'Base e torso montados (usando cadeira e caixote que voce ja tem)'],
    ['D', '2 BTS7960 + potenciometros + fusiveis + chave de emergencia + fio 1,5mm² + capacitores',
     'R$ 150', 'Motor de limpador domado na bancada - a etapa mais importante'],
    ['E', '1 MG996R + barra roscada M8 + porcas',
     'R$ 50', 'Braco 1 completo: ombro + cotovelo levantando peso'],
    ['G', 'Reposicao de parafusos M5 e ferragem do segundo braco',
     'R$ 30', 'Braco 2 (voce ja sabe o caminho - vai 3x mais rapido)'],
    ['H', '1 MG90S + cabo de freio + elasticos',
     'R$ 30', 'Garra pegando um copo'],
    ['', 'TOTAL', 'R$ 595', 'Diluido em ~3 meses'],
]
tf = Table([[Paragraph(c, st_ch if i == 0 else (st_cb if j in (0, 2) else st_c))
             for j, c in enumerate(l)] for i, l in enumerate(fases)],
           colWidths=[13 * mm, 74 * mm, 18 * mm, 73 * mm])
tf.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), NAVY),
    ('BACKGROUND', (0, len(fases) - 1), (-1, len(fases) - 1), colors.HexColor('#e2e8f0')),
    ('GRID', (0, 0), (-1, -1), 0.4, LINHA),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('ALIGN', (0, 1), (0, -1), 'CENTER'),
    ('ALIGN', (2, 1), (2, -1), 'CENTER'),
    ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('ROWBACKGROUNDS', (0, 1), (-1, len(fases) - 2), [colors.white, CINZA_CLARO]),
]))
A(tf)

# ---------------- CHECKLIST FERRO-VELHO ----------------
A(Paragraph('9. Bilhete do ferro-velho (leve no celular)', st_h2))
A(Paragraph('Lista curta pra pedir de uma vez, sem esquecer nada:', st_p))
chk = [
    ['<b>2x motor de limpador de para-brisa 12V</b> - "com o braco da palheta junto, por favor" '
     '(o clamp do braco e a fixacao pronta no eixo)'],
    ['<b>1x fonte de PC (ATX)</b> - de qualquer torre velha; nao precisa saber se funciona, '
     'mas se puder testar, melhor'],
    ['<b>Rolamentos de skate</b> (608) - 4 unidades, de skate ou patins descartado'],
    ['<b>Impressora velha</b> - inteira, se deixarem: rende microswitches, engrenagens, '
     'eixos retificados e parafusos M3'],
    ['<b>Cabo de freio de bicicleta</b> - qualquer bicicletaria tem sobra'],
    ['<b>Se aparecer robo aspirador quebrado: leve.</b> Rende modulo de roda com encoder '
     '(motor + redutor + sensor de rotacao numa peca so), sensores de para-choque e talvez bateria. '
     'Nao serve de base pro Ferrao (ele pesa demais), mas as pecas valem ouro no Nivel 2.'],
]
tc = Table([[Paragraph('&#9744;', st_cb), Paragraph(c[0], st_c)] for c in chk],
           colWidths=[8 * mm, 170 * mm])
tc.setStyle(TableStyle([
    ('GRID', (0, 0), (-1, -1), 0.4, LINHA),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BACKGROUND', (0, 0), (0, -1), AMBAR_BG),
    ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
A(tc)

# ---------------- SEGURANCA ----------------
A(Paragraph('10. Tres regras de seguranca que nao se negocia', st_h2))
seg = [
    ['1', 'O motor de limpador nao para por resistencia.',
     'A reducao sem-fim nao recua: dedo entre o braco e o torso e esmagamento serio. Fim-de-curso '
     'instalado ANTES do primeiro teste com o braco montado, testes iniciais a 30-40% de forca, '
     'e a mao longe do arco sempre que houver 12V ligado.'],
    ['2', 'Fusivel nao e opcional.',
     'A fonte ATX entrega mais de 15A. Um curto sem fusivel derrete o fio e comeca um incendio. '
     'Fusivel custa R$ 3 - casa nao.'],
    ['3', 'Nao abra a fonte ATX.',
     'Mesmo desligada da tomada ela guarda carga da rede eletrica nos capacitores. Tudo que voce '
     'precisa (fio verde, preto, amarelo, vermelho) esta do lado de fora.'],
]
ts = Table([[Paragraph(n, st_cb), Paragraph('<b>%s</b><br/>%s' % (t, d), st_c)] for n, t, d in seg],
           colWidths=[8 * mm, 170 * mm])
ts.setStyle(TableStyle([
    ('GRID', (0, 0), (-1, -1), 0.4, LINHA),
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fee2e2')),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
A(ts)


# ---------------- RENDER ----------------
def rodape(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINHA)
    canvas.setLineWidth(0.5)
    canvas.line(MARG, 12 * mm, W - MARG, 12 * mm)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(CINZA)
    canvas.drawString(MARG, 8 * mm, 'Projeto Ferrao - lista de materiais por vertente')
    canvas.drawRightString(W - MARG, 8 * mm, 'Pagina %d' % doc.page)
    canvas.restoreState()


doc = BaseDocTemplate(
    r'C:\Users\Usuario\Desktop\Projeto_Ferrao_Lista_Materiais.pdf',
    pagesize=A4, leftMargin=MARG, rightMargin=MARG,
    topMargin=14 * mm, bottomMargin=18 * mm,
    title='Projeto Ferrao - Lista de Materiais',
    author='Allan Rodrigues')
frame = Frame(MARG, 18 * mm, W - 2 * MARG, H - 32 * mm, id='f')
doc.addPageTemplates([PageTemplate(id='p', frames=[frame], onPage=rodape)])
doc.build(story)
print('PDF gerado com sucesso')
