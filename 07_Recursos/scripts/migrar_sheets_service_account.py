"""
Template reutilizavel: mover/copiar abas entre planilhas Google Sheets usando
a mesma service account que o n8n ja usa (sem passar pelo MCP, sem limite de
tokens do chat, idempotente).

Origem: script real que fez a separacao de CRM por nicho em 05/07/2026
(ver memoria 'separacao-planilhas-nichos'). As funcoes helper (get_all,
ensure_sheet, write) sao genericas; as listas MIGRATE/FRESH_HEADERS abaixo
sao o exemplo daquela migracao especifica -- trocar pelos IDs/abas da vez.

Rodar com: uv run --with google-auth --with google-api-python-client python migrar_sheets_service_account.py
Precisa: C:/Users/Usuario/.claude/kronos-service-account.json com acesso de
Editor na planilha de origem E na(s) de destino (planilha nova = Allan
compartilha manualmente com kronos-n8n@kronos-ia-498605.iam.gserviceaccount.com
antes de rodar -- ver skill kronos-mcp / memoria mcp-n8n-sheets-setup).
"""
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY_PATH = "C:/Users/Usuario/.claude/kronos-service-account.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
OLD_SS = "1ZlDFYkgx6aXUM0ayj1e1_K6uX0cruo7VuCcmg1_w5ps"

AURORA_SS = "1Py-l3rOw0bcahQXmkbWQeugArZqzBJsBRzfZz9oFcgs"
ODONTO_SS = "1tb9p9lhejjsy0Mf6_0MwGX-NpAhnqozEg-SI7iLOC-U"
ADV_SS = "19BlnT6xvRgZMAcEIMPjjnlunUo3QzdutrMBsuC3T5cg"
INTERNO_SS = "1tOXVM8frTwxbhCR1Gmb2dyPFNks8INCNSKWeg9t1UK4"

creds = service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
svc = build("sheets", "v4", credentials=creds)


def get_all(spreadsheet_id, sheet):
    r = svc.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f"{sheet}!A1:Z10000").execute()
    return r.get("values", [])


def existing_sheets(spreadsheet_id):
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}


def ensure_sheet(spreadsheet_id, title):
    """Cria a aba se nao existir. Se a planilha so tem a aba padrao 'Página1'
    (planilha recem-criada via conector do Drive), renomeia em vez de criar nova."""
    sheets = existing_sheets(spreadsheet_id)
    if title in sheets:
        return
    if "Página1" in sheets and len(sheets) == 1:
        svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
            "requests": [{"updateSheetProperties": {
                "properties": {"sheetId": sheets["Página1"], "title": title}, "fields": "title"}}]
        }).execute()
        return
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [{"addSheet": {"properties": {"title": title}}}]
    }).execute()


def write(spreadsheet_id, sheet, values):
    if not values:
        return
    svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=f"{sheet}!A1",
        valueInputOption="USER_ENTERED", body={"values": values}
    ).execute()


# ==== EXEMPLO REAL (05/07/2026) — adaptar pra proxima migracao ====

# 1) MIGRAR INTEIRO — so usar quando o dado de origem nao tem ambiguidade de
# dono (nunca foi compartilhado entre dois clientes/nichos na mesma aba).
MIGRATE = [
    ("Feedback_PosVenda", AURORA_SS, "Feedback_PosVenda"),
    ("Log_Lembretes", AURORA_SS, "Log_Lembretes"),
    ("Sessoes_Advocacia", ADV_SS, "Sessoes_Advocacia"),
    ("Log_Advocacia", ADV_SS, "Log_Advocacia"),
    ("Agendamentos_Advocacia", ADV_SS, "Agendamentos_Advocacia"),
    ("Leads", INTERNO_SS, "Leads"),
    ("Clientes", INTERNO_SS, "Clientes"),
    ("Config", INTERNO_SS, "Config"),
    ("Prospeccao", INTERNO_SS, "Prospeccao"),
    ("Prospeccao_Advocacia", INTERNO_SS, "Prospeccao_Advocacia"),
    ("Prospeccao_Pizzaria", INTERNO_SS, "Prospeccao_Pizzaria"),
    ("Prospeccao_Parecer", INTERNO_SS, "Prospeccao_Parecer"),
    ("Log_Monitoramento", INTERNO_SS, "Log_Monitoramento"),
]

for src, dest_ss, dest_sheet in MIGRATE:
    ensure_sheet(dest_ss, dest_sheet)
    data = get_all(OLD_SS, src)
    write(dest_ss, dest_sheet, data)
    print(f"OK migrado {src} -> {dest_sheet} ({len(data)} linhas)")

# 2) ABAS NOVAS EM BRANCO — quando o dado de origem estava misturado entre
# dois donos sem coluna discriminadora (nao da pra separar com seguranca).
FRESH_HEADERS = {
    "Sessoes_Ativas": ["ID", "Telefone", "Agente", "Fase", "Historico", "Dado_Temp", "Criado_Em", "Atualizado_Em", "Status"],
    "Log_Interacoes": ["Data", "Telefone", "Nome", "Mensagem", "Intent", "Resposta", "Escalacao"],
    "Agendamentos": ["ID", "Telefone", "Nome", "Procedimento", "Data", "Hora", "Profissional", "Status", "Criado_Em", "Observacoes"],
    "Log_Agendamentos": ["Data_Hora", "Telefone", "Nome", "Acao", "Procedimento", "Detalhes"],
}
SLOTS_HEADER = ["ID", "Data", "Hora", "Profissional", "Procedimento_Tipo", "Status", "Reservado_Para", "Agendamento_ID", "telefone", "nome"]

for dest_ss in [AURORA_SS, ODONTO_SS]:
    for title, header in FRESH_HEADERS.items():
        ensure_sheet(dest_ss, title)
        write(dest_ss, title, [header])
    ensure_sheet(dest_ss, "Slots_Disponiveis")
    write(dest_ss, "Slots_Disponiveis", [SLOTS_HEADER])
    print(f"OK abas frescas criadas em {dest_ss}")


def gen_slots():
    """Gera slots de agenda evergreen pros proximos dias uteis (exemplo especifico da Aurora/Odonto)."""
    out = []
    profs = ["Dra. Marina", "Dra. Julia"]
    horarios = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
    n = 1
    cur = datetime.date.today()
    dias_uteis = 0
    while dias_uteis < 10:
        cur += datetime.timedelta(days=1)
        if cur.weekday() >= 5:
            continue
        for i, h in enumerate(horarios):
            out.append([f"S{n:03d}", cur.isoformat(), h, profs[i % 2], "Qualquer", "disponivel", "", "", "", ""])
            n += 1
        dias_uteis += 1
    return out


slots = gen_slots()
for dest_ss in [AURORA_SS, ODONTO_SS]:
    write(dest_ss, "Slots_Disponiveis", [SLOTS_HEADER] + slots)
    print(f"OK {len(slots)} slots seedados em {dest_ss}")

print("MIGRACAO COMPLETA")
