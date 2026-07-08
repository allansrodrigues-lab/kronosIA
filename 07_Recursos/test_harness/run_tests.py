#!/usr/bin/env python3
"""
Kronos WhatsApp Bot — Test Harness de Regressão
Envia payloads de teste nos webhooks e valida a classificação de intent.
DADOS DE TESTE — remoteJid prefixado com 5500TEST, nunca cliente real.

Uso:
    python3 run_tests.py            # roda todos os bots
    python3 run_tests.py aurora     # só Aurora
    python3 run_tests.py odonto     # só OdontoVita

Retorna exit code 0 se todos passarem, 1 se algum falhar.
"""

import json
import time
import sys
import requests
from datetime import datetime, timezone

N8N_URL     = "https://n8n.kronosintelligence.com.br"
# Chave REST API lida de arquivo fora do repo (renovar = sobrescrever /root/.kronos/n8n_api_key).
# Roda no VPS. Diferente da N8N_API_KEY env var (que NÃO funciona pra REST API).
N8N_API_KEY = open("/root/.kronos/n8n_api_key").read().strip()
HEADERS     = {"X-N8N-API-KEY": N8N_API_KEY}

WORKFLOWS = {
    "aurora": {
        "id":       "Orq01RouterV2aa1",
        "webhook":  "/webhook/whatsapp",
        "instance": "clinica01",
    },
    "odonto": {
        "id":       "01-orquestrador-odonto",
        "webhook":  "/webhook/whatsapp-odonto",
        "instance": "clinica01",
    },
}

# __SPLIT__ = endereço picado: envia 2 msgs rápidas separadas por |
SCENARIOS = {
    "aurora": [
        {"id": "A01", "name": "AGENDAR claro",
         "msg": "Quero agendar uma limpeza de pele",
         "expected": "AGENDAR"},
        {"id": "A02", "name": "DUVIDA_PRECO",
         "msg": "Quanto custa o botox?",
         "expected": "DUVIDA_PRECO"},
        {"id": "A03", "name": "DUVIDA_PROCEDIMENTO",
         "msg": "Como funciona o preenchimento labial?",
         "expected": "DUVIDA_PROCEDIMENTO"},
        {"id": "A04", "name": "RECLAMACAO",
         "msg": "Fui muito mal atendida semana passada, quero reclamar",
         "expected": "RECLAMACAO"},
        {"id": "A05", "name": "Agendamento ambíguo",
         "msg": "queria marcar pra semana que vem se possível",
         "expected": "AGENDAR"},
        {"id": "A06", "name": "POS_PROCEDIMENTO",
         "msg": "Fiz limpeza ontem e está vermelho, é normal?",
         "expected": "POS_PROCEDIMENTO"},
        {"id": "A07", "name": "Mensagem picada (buffering)",
         "msg": "__SPLIT__quero marcar uma limpeza de pele|amanhã de manhã se possível",
         "expected": "AGENDAR",
         "note": "buffer deve agrupar as 2 msgs em 1 execução — juntas = AGENDAR claro"},
    ],
    "odonto": [
        {"id": "O01", "name": "AGENDAR claro",
         "msg": "Quero agendar uma consulta de limpeza dental",
         "expected": "AGENDAR"},
        {"id": "O06", "name": "AGENDAR via marcar",
         "msg": "Quero marcar uma consulta para limpeza dental",
         "expected": "AGENDAR"},
        {"id": "O02", "name": "DUVIDA_PRECO",
         "msg": "Qual o valor do clareamento dental?",
         "expected": "DUVIDA_PRECO"},
        {"id": "O03", "name": "DUVIDA_PROCEDIMENTO",
         "msg": "Como funciona o aparelho invisível?",
         "expected": "DUVIDA_PROCEDIMENTO"},
        {"id": "O04", "name": "RECLAMACAO",
         "msg": "O dentista foi grosseiro comigo na última consulta",
         "expected": "RECLAMACAO"},
        {"id": "O05", "name": "Agendamento ambíguo",
         "msg": "será que dá pra agendar ainda essa semana?",
         "expected": "AGENDAR"},
    ],
}


def build_payload(instance, message, jid, msg_id):
    return {
        "event": "messages.upsert",
        "instance": instance,
        "data": {
            "key": {
                "remoteJid": f"{jid}@s.whatsapp.net",
                "fromMe": False,
                "id": msg_id,
            },
            "pushName": "[TESTE AUTOMATICO - NAO CLIENTE REAL]",
            "message": {"conversation": message},
            "messageType": "conversation",
            "messageTimestamp": int(time.time()),
        },
    }


def send_webhook(webhook, instance, message, jid, msg_id):
    try:
        r = requests.post(
            f"{N8N_URL}{webhook}",
            json=build_payload(instance, message, jid, msg_id),
            timeout=10,
        )
        return r.status_code
    except Exception as e:
        return f"ERR:{e}"


def list_executions(workflow_id, limit=5):
    """Lista execuções recentes (sem dados internos — o list endpoint não suporta includeData)."""
    try:
        r = requests.get(
            f"{N8N_URL}/api/v1/executions",
            headers=HEADERS,
            params={"workflowId": workflow_id, "limit": limit},
            timeout=20,
        )
        if r.ok:
            return r.json().get("data", [])
    except Exception:
        pass
    return []


def get_execution_full(exec_id):
    """Busca dados completos de uma execução pelo ID. includeData=true obrigatório."""
    try:
        r = requests.get(
            f"{N8N_URL}/api/v1/executions/{exec_id}",
            headers=HEADERS,
            params={"includeData": "true"},
            timeout=20,
        )
        if r.ok:
            return r.json()
    except Exception:
        pass
    return None


def extract_intent(ex):
    """Extrai o intent do nó 'Parsear Intent' na execução."""
    try:
        run_data = ex["data"]["resultData"]["runData"]
        node_runs = run_data.get("Parsear Intent", [])
        if node_runs:
            items = node_runs[0]["data"]["main"][0]
            return items[0]["json"].get("intent", "NOT_FOUND")
    except Exception:
        pass
    return "NOT_FOUND"


def poll_for_execution(workflow_id, jid, since_ts, timeout=40):
    """
    Aguarda execução após since_ts, busca dados completos e verifica JID.
    Prioriza execuções com intent classificado — o buffer cria 2 execuções para
    mensagens picadas: a que é dropada (sem intent) e a que processa (com intent).
    Continua polling até encontrar uma com intent ou expirar o timeout.
    """
    deadline = time.time() + timeout
    fallback = None  # execução com JID mas sem intent (buffer dropped)
    while time.time() < deadline:
        time.sleep(3)
        summaries = list_executions(workflow_id, limit=10)
        for summary in summaries:
            exec_id = summary.get("id")
            started = summary.get("startedAt", "")
            try:
                ex_ts = datetime.fromisoformat(started.replace("Z", "+00:00")).timestamp()
                if ex_ts < since_ts - 3:
                    continue
            except Exception:
                continue
            full = get_execution_full(exec_id)
            if not full or jid not in json.dumps(full):
                continue
            intent = extract_intent(full)
            if intent != "NOT_FOUND":
                return full  # execução real com intent — retorna imediatamente
            if full.get("status") in ("success", "error"):
                fallback = full  # buffer dropped — guarda como fallback
    return fallback


def run_scenario(bot, scenario, wf):
    s_id  = scenario["id"]
    jid   = f"5500TEST{s_id}"
    msg   = scenario["msg"]
    since = time.time()

    # Endereço picado: envia 2 msgs com 0.5s de intervalo (dentro do buffer de 2s)
    if msg.startswith("__SPLIT__"):
        parts = msg.replace("__SPLIT__", "").split("|")
        send_webhook(wf["webhook"], wf["instance"], parts[0], jid, f"TEST-{s_id}-1-{int(since)}")
        time.sleep(0.5)
        code = send_webhook(wf["webhook"], wf["instance"], parts[1], jid, f"TEST-{s_id}-2-{int(since)}")
    else:
        code = send_webhook(wf["webhook"], wf["instance"], msg, jid, f"TEST-{s_id}-{int(since)}")

    if str(code) not in ["200", "202"]:
        return {"id": s_id, "name": scenario["name"], "status": "FAIL",
                "reason": f"webhook retornou {code}"}

    ex = poll_for_execution(wf["id"], jid, since)
    if not ex:
        return {"id": s_id, "name": scenario["name"], "status": "FAIL",
                "reason": "execução não encontrada no n8n (timeout 30s)"}

    intent   = extract_intent(ex)
    expected = scenario["expected"]

    if intent == expected:
        return {"id": s_id, "name": scenario["name"], "status": "PASS", "intent": intent}
    else:
        return {"id": s_id, "name": scenario["name"], "status": "FAIL",
                "reason": f"esperado={expected}  obtido={intent}"}


def print_dashboard(results, bot):
    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] == "FAIL"]
    print(f"\n{'='*54}")
    print(f"  {bot.upper()} — {len(passed)}/{len(results)} passou")
    print(f"{'='*54}")
    for r in results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        print(f"  {icon} [{r['id']}] {r['name']}")
        if r["status"] == "PASS":
            print(f"       intent={r['intent']}")
        else:
            print(f"       FALHOU: {r.get('reason', '?')}")
    print(f"\n  {'🟢 VERDE — tudo ok' if not failed else '🔴 VERMELHO — há falhas'}")
    return not failed


def main():
    bots    = sys.argv[1:] if len(sys.argv) > 1 else list(WORKFLOWS.keys())
    all_ok  = True

    print(f"\n🧪 KRONOS TEST HARNESS — {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("⚠️  DADOS DE TESTE — remoteJid prefixado com 5500TEST, não são clientes reais\n")

    for bot in bots:
        if bot not in WORKFLOWS:
            print(f"Bot desconhecido: {bot} (use: aurora, odonto)")
            continue
        wf        = WORKFLOWS[bot]
        scenarios = SCENARIOS.get(bot, [])
        results   = []

        print(f"▶ Testando {bot} ({len(scenarios)} cenários)...")
        for s in scenarios:
            print(f"  → [{s['id']}] {s['name']}... ", end="", flush=True)
            r = run_scenario(bot, s, wf)
            results.append(r)
            print("✅" if r["status"] == "PASS" else "❌")

        if not print_dashboard(results, bot):
            all_ok = False

    print(f"\n{'='*54}")
    print(f"  SUITE COMPLETA: {'PASSOU ✅' if all_ok else 'FALHOU ❌'}")
    print(f"{'='*54}\n")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
