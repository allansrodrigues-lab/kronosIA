# -*- coding: utf-8 -*-
W = 380
PX, PW = 12, 196
PAD = 10
MAXB = 150
FS = 11
LH = 15
CW = 0.55 * FS
HEADERH = 46
FOOTERH = 44
BLUE = "#1f74e6"
BG = "#ffffff"

def wrap(text, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) * CW <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def gen(title, initial, msgs, outfile):
    parts = []
    inner_w = PW - 2 * PAD - 12
    bubw = min(MAXB, inner_w)
    txtw = bubw - 16

    y = PX + HEADERH + 10
    bubbles = []
    for m in msgs:
        if m.get("date"):
            bubbles.append(("date", m["date"], y)); y += 26; continue
        side = m["who"]
        bx = (PX + PAD + 2) if side == "in" else (PX + PW - PAD - bubw)
        if m.get("file"):
            h = 46
            bubbles.append(("file", m, y, bx, bubw, h)); y += h + 7; continue
        lines = wrap(m["text"], txtw)
        h = 8 + len(lines) * LH + 14
        bubbles.append(("bub", m, y, bx, bubw, h, lines)); y += h + 7

    chat_bottom = y + 4
    frame_bottom = chat_bottom + FOOTERH
    H = frame_bottom + 16

    parts.append(f'<rect x="0" y="0" width="{W}" height="{H:.0f}" fill="{BG}"/>')
    parts.append(f'<rect x="{PX}" y="{PX}" width="{PW}" height="{frame_bottom-PX}" rx="20" fill="#E5DDD5" stroke="rgba(0,0,0,0.18)" stroke-width="1"/>')
    hx, hy = PX, PX
    parts.append(f'<path d="M{hx+20},{hy} H{hx+PW-20} A20,20 0 0 1 {hx+PW},{hy+20} V{hy+HEADERH} H{hx} V{hy+20} A20,20 0 0 1 {hx+20},{hy} Z" fill="#075E54"/>')
    parts.append(f'<path d="M{hx+14},{hy+16} l-6,7 l6,7" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append(f'<circle cx="{hx+40}" cy="{hy+23}" r="13" fill="#cfd8d4"/>')
    parts.append(f'<text x="{hx+40}" y="{hy+23}" dy="0.34em" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif" font-size="13" font-weight="600" fill="#075E54">{esc(initial)}</text>')
    parts.append(f'<text x="{hx+60}" y="{hy+19}" font-family="Inter,Segoe UI,sans-serif" font-size="13" font-weight="600" fill="#ffffff">{esc(title)}</text>')
    parts.append(f'<text x="{hx+60}" y="{hy+34}" font-family="Inter,Segoe UI,sans-serif" font-size="10.5" fill="#d7ece6">online</text>')
    parts.append(f'<circle cx="{hx+PW-20}" cy="{hy+22}" r="2" fill="#cfe3dc"/><circle cx="{hx+PW-13}" cy="{hy+22}" r="2" fill="#cfe3dc"/>')

    notes = []
    for item in bubbles:
        if item[0] == "date":
            _, dt, by = item
            cx = PX + PW / 2; wpx = len(dt) * 6 + 16
            parts.append(f'<rect x="{cx-wpx/2:.0f}" y="{by}" width="{wpx:.0f}" height="18" rx="6" fill="rgba(255,255,255,0.8)"/>')
            parts.append(f'<text x="{cx:.0f}" y="{by+12}" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif" font-size="10.5" fill="#54656f">{esc(dt)}</text>')
            continue
        if item[0] == "file":
            _, m, by, bx, bw, h = item
            fill = "#ffffff" if m["who"] == "in" else "#DCF8C6"
            parts.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{h}" rx="9" fill="{fill}"/>')
            ix, iy = bx + 10, by + 12
            parts.append(f'<path d="M{ix},{iy} h11 l5,5 v15 h-16 z" fill="#eef2f8" stroke="#9fb0c8" stroke-width="1"/>')
            parts.append(f'<path d="M{ix+11},{iy} v5 h5" fill="none" stroke="#9fb0c8" stroke-width="1"/>')
            parts.append(f'<text x="{bx+34}" y="{by+22}" font-family="Inter,Segoe UI,sans-serif" font-size="11" font-weight="600" fill="#111b21">{esc(m["file"])}</text>')
            parts.append(f'<text x="{bx+34}" y="{by+36}" font-family="Inter,Segoe UI,sans-serif" font-size="10" fill="#667781">PDF</text>')
            tm = m.get("time", "")
            if tm:
                parts.append(f'<text x="{bx+bw-8}" y="{by+h-6}" text-anchor="end" font-family="Inter,Segoe UI,sans-serif" font-size="10" fill="#667781">{esc(tm)}</text>')
            if m.get("note"):
                notes.append((by + h / 2, bx + bw, m["note"]))
            continue
        _, m, by, bx, bw, h, lines = item
        fill = "#ffffff" if m["who"] == "in" else "#DCF8C6"
        parts.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{h}" rx="9" fill="{fill}"/>')
        ty = by + 8 + FS
        for ln in lines:
            parts.append(f'<text x="{bx+8}" y="{ty}" font-family="Inter,Segoe UI,sans-serif" font-size="{FS}" fill="#111b21">{esc(ln)}</text>')
            ty += LH
        tm = m.get("time", "")
        if tm:
            extra = "  ✓✓" if m["who"] == "out" else ""
            parts.append(f'<text x="{bx+bw-8}" y="{by+h-6}" text-anchor="end" font-family="Inter,Segoe UI,sans-serif" font-size="10.5" fill="#667781">{esc(tm)}{extra}</text>')
        if m.get("note"):
            notes.append((by + h / 2, bx + bw, m["note"]))

    fy = chat_bottom + 6
    parts.append(f'<rect x="{PX+10}" y="{fy}" width="{PW-58}" height="26" rx="13" fill="#ffffff"/>')
    parts.append(f'<text x="{PX+22}" y="{fy+17}" font-family="Inter,Segoe UI,sans-serif" font-size="11" fill="#8696a0">Mensagem</text>')
    parts.append(f'<circle cx="{PX+PW-22}" cy="{fy+13}" r="14" fill="#075E54"/>')
    parts.append(f'<path d="M{PX+PW-27},{fy+13} h10 M{PX+PW-21},{fy+8} l5,5 l-5,5" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')

    CXL = PX + PW + 14
    TXX = PX + PW + 22
    tw = W - TXX - 6
    prev_bottom = 0
    notes.sort(key=lambda n: n[0])
    for cy, bxr, note in notes:
        nlines = wrap(note, tw * 0.76)  # margem extra: 1ª linha renderiza em bold + fonte maior (mais larga que a estimativa)
        block = len(nlines) * 14
        ny = max(cy - block / 2, prev_bottom + 10)
        center = ny + block / 2
        parts.append(f'<circle cx="{bxr+2:.0f}" cy="{cy:.0f}" r="2.4" fill="{BLUE}"/>')
        parts.append(f'<path d="M{bxr+2:.0f},{cy:.0f} L{CXL:.0f},{cy:.0f} L{TXX-4:.0f},{center:.0f}" fill="none" stroke="{BLUE}" stroke-width="1.3"/>')
        tyy = ny + 11
        for i, ln in enumerate(nlines):
            weight = "600" if i == 0 else "400"
            parts.append(f'<text x="{TXX:.0f}" y="{tyy:.0f}" font-family="Inter,Segoe UI,sans-serif" font-size="11.5" font-weight="{weight}" fill="{BLUE}">{esc(ln)}</text>')
            tyy += 14
        prev_bottom = ny + block

    svg = f'<svg width="100%" viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Demo {esc(title)}">' + "".join(parts) + "</svg>"
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(svg)
    print(outfile, int(H))


clinicas = [
    {"date": "ontem"},
    {"who": "in", "text": "Oi! Vocês fazem limpeza de pele? Quanto fica?", "time": "09:11"},
    {"who": "out", "text": "Oi, Maria! Fazemos sim, R$180. Quer que eu veja um horário?", "time": "09:11", "note": "Atende e responde na hora, 24h"},
    {"who": "in", "text": "Tem respaldo científico?", "time": "09:12"},
    {"who": "out", "text": "Tem sim! Te envio um resumo das evidências.", "time": "09:12", "note": "Mostra base científica do procedimento"},
    {"who": "in", "text": "Pode marcar quinta à tarde?", "time": "09:13"},
    {"who": "out", "text": "Quinta, 15h com a Dra. Helena. Confirmo?", "time": "09:13", "note": "Agenda direto na agenda da médica"},
    {"date": "hoje"},
    {"who": "out", "text": "Oi, Maria! Lembrete: sua consulta é hoje às 15h.", "time": "08:00", "note": "Lembrete automático 24h antes"},
    {"who": "out", "text": "Como ficou sua pele após a limpeza?", "time": "17:30", "note": "Pós-atendimento e recompra"},
]

advocacia = [
    {"date": "ontem"},
    {"who": "in", "text": "Boa tarde. Sofri um acidente de trânsito, tenho direito a indenização?", "time": "14:02"},
    {"who": "out", "text": "Boa tarde! Sou a Léa, assistente do escritório. Sinto muito pelo ocorrido, vou te ajudar.", "time": "14:02", "note": "Atende 24h, com acolhimento"},
    {"who": "out", "text": "Pode me contar quando foi e se há boletim de ocorrência?", "time": "14:03", "note": "Faz a triagem inicial do caso"},
    {"who": "in", "text": "Foi semana passada. Tenho o BO e os laudos.", "time": "14:05"},
    {"who": "in", "file": "BO_e_laudos.pdf", "time": "14:05"},
    {"who": "out", "text": "Recebi seu documento!", "time": "14:05", "note": "Recebe processos e documentos"},
    {"who": "out", "text": "Já li tudo: prazo até 12/08 e há provas da culpa do outro condutor.", "time": "14:06", "note": "Lê o PDF e extrai prazos e pontos-chave"},
    {"who": "out", "text": "Vou direcionar ao Dr. Martins, especialista em trânsito.", "time": "14:06", "note": "Direciona pro advogado responsável"},
    {"who": "out", "text": "Posso te enviar decisões recentes de casos parecidos.", "time": "14:07", "note": "Base científica: jurisprudência"},
]

imobiliaria = [
    {"date": "ontem"},
    {"who": "in", "text": "Oi! Procuro um apê de 2 quartos pra comprar no Cambuí, até uns 700 mil.", "time": "10:04"},
    {"who": "out", "text": "Oi! Sou a Sofia, da Schalletti Imóveis. Adorei o perfil, deixa eu ver o que temos por aí.", "time": "10:04", "note": "Atende 24h e qualifica o perfil"},
    {"who": "out", "text": "Achei o SCH-001: Cambuí, 2 quartos, 74m², varanda gourmet, R$ 690.000. Quer ver outra opção também?", "time": "10:05", "note": "Faz matching com a carteira (2-3 opções)"},
    {"who": "in", "text": "Gostei desse! Dá pra financiar? Quanto ficaria a parcela?", "time": "10:07"},
    {"who": "out", "text": "Dá sim! Com 20% de entrada e 30 anos, a parcela inicial fica em torno de R$ 4.850 (tabela Price). Quer que eu simule outra entrada?", "time": "10:08", "note": "Calcula financiamento na hora (Price/SAC)"},
    {"who": "in", "text": "Perfeito, quero conhecer pessoalmente. Pode ser sábado de manhã?", "time": "10:10"},
    {"who": "out", "text": "Combinado! Visita no SCH-001 sábado às 10h, com a corretora Beatriz. Te aviso um dia antes.", "time": "10:10", "note": "Agenda a visita direto na agenda"},
    {"date": "hoje"},
    {"who": "out", "text": "Oi! Passando pra saber: o que achou do apê depois da visita de sábado?", "time": "16:00", "note": "Follow-up pós-visita, sem deixar o lead esfriar"},
]

solar = [
    {"date": "ontem"},
    {"who": "in", "text": "Oi, quanto custa colocar energia solar na minha casa?", "time": "19:20"},
    {"who": "out", "text": "Oi! Sou a Helena, da Zênite Energia Solar. Posso calcular sua economia agora mesmo — qual o valor médio da sua conta de luz?", "time": "19:20", "note": "Atende 24h e qualifica o lead na hora"},
    {"who": "in", "text": "Uns 850 reais por mês", "time": "19:21"},
    {"who": "out", "text": "Perfeito! É casa, empresa ou rural? E a rede é mono, bi ou trifásica?", "time": "19:21"},
    {"who": "in", "text": "Casa, e é bifásico sim", "time": "19:22"},
    {"who": "out", "text": "Prontinho! Sistema de 11 placas (6,0 kWp). Investimento estimado R$ 18.000, economia de R$ 734/mês. Se paga em 2 anos e 1 mês!", "time": "19:22", "note": "Calcula payback real na hora (nunca chuta número)"},
    {"who": "out", "text": "Depois disso é mais de 20 anos de energia quase de graça. Quer agendar a visita técnica gratuita?", "time": "19:23", "note": "Convida pra visita técnica sem pressão"},
    {"who": "in", "text": "Quero sim! Pode ser sábado de manhã?", "time": "19:24"},
    {"who": "out", "text": "Combinado! Visita sábado de manhã, nosso engenheiro confirma com você em breve.", "time": "19:24", "note": "Agenda a visita direto no CRM da equipe"},
    {"date": "hoje"},
    {"who": "out", "text": "Bom dia! Só confirmando: nosso engenheiro chega às 9h pra avaliar seu telhado. Até já!", "time": "08:00", "note": "Lembrete automático antes da visita"},
]

gen("Clínica Aurora", "A", clinicas, "demo_clinicas.svg")
gen("Martins Advocacia", "M", advocacia, "demo_advocacia.svg")
gen("Schalletti Imóveis", "S", imobiliaria, "demo_imobiliaria.svg")
gen("Zênite Energia Solar", "Z", solar, "demo_solar.svg")
