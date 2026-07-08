#!/usr/bin/env python3
"""
Kronos Self-Healing Monitor
Roda o test harness (13 cenarios Aurora+Odonto). Se falhar, tenta diagnosticar
e aplicar NO MAXIMO um fix seguro (reiniciar container n8n se estiver fora do
ar, OU reativar o workflow monitorado se foi desativado). Nunca edita codigo
de no nem mexe em workflow fora dos dois monitorados aqui.

Loga o resultado em Log_Monitoramento via webhook kronos-selfheal-ingest.
So fica sem alerta se resolver sozinho (Status=AUTO-CORRIGIDO); quando precisa
de humano, loga Status=ERRO e o monitor existente (kronos-monitor-selfhealing,
que ja varre a planilha a cada 30min) dispara o alerta de WhatsApp — nao
duplica logica de notificacao.

Cron sugerido (hourly):
0 * * * * /usr/bin/python3 /docker/test-harness/selfheal.py >> /var/log/kronos-selfheal.log 2>&1
"""
import re
import subprocess
import time
from datetime import datetime, timezone

import requests

N8N_URL = "https://n8n.kronosintelligence.com.br"
N8N_API_KEY = open("/root/.kronos/n8n_api_key").read().strip()
HEADERS = {"X-N8N-API-KEY": N8N_API_KEY}
INGEST_WEBHOOK = f"{N8N_URL}/webhook/selfheal-log"

N8N_CONTAINER = "n8n-xve0-n8n-1"
MONITORED_WORKFLOWS = {
    "Orq01RouterV2aa1": "Aurora",
    "01-orquestrador-odonto": "OdontoVita",
}

RUN_TESTS = ["/usr/bin/python3", "/docker/test-harness/run_tests.py"]


def run_suite():
    r = subprocess.run(RUN_TESTS, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def parse_failures(output):
    failures = []
    lines = output.splitlines()
    for i, line in enumerate(lines):
        m = re.search(r"❌ \[(\w+)\] (.+?)\.\.\.", line)
        if m:
            reason = ""
            for j in range(i, min(i + 4, len(lines))):
                rm = re.search(r"FALHOU: (.+)", lines[j])
                if rm:
                    reason = rm.group(1)
                    break
            failures.append({"id": m.group(1), "name": m.group(2), "reason": reason})
    return failures


def container_running(name):
    r = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", name],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and r.stdout.strip() == "true"


def workflow_active(wf_id):
    r = requests.get(f"{N8N_URL}/api/v1/workflows/{wf_id}", headers=HEADERS, timeout=15)
    if r.ok:
        return r.json().get("active", False)
    return None


def activate_workflow(wf_id):
    return requests.post(f"{N8N_URL}/api/v1/workflows/{wf_id}/activate", headers=HEADERS, timeout=15)


def diagnose_and_fix(failures):
    """Retorna (tipo_erro, mensagem, fix_aplicado: bool). No maximo 1 fix por rodada."""
    reasons = " | ".join(f"[{f['id']}] {f['reason']}" for f in failures)

    if any("webhook retornou" in f["reason"] for f in failures):
        if not container_running(N8N_CONTAINER):
            subprocess.run(["docker", "restart", N8N_CONTAINER])
            time.sleep(20)
            return "N8N_DOWN", f"Container {N8N_CONTAINER} estava parado. Reiniciado. Falhas originais: {reasons}", True
        return "WEBHOOK_ERRO", f"Webhook respondeu erro mas o container esta rodando (pode ser Traefik/rede). Falhas: {reasons}", False

    if any("execução não encontrada" in f["reason"] for f in failures):
        for wf_id, label in MONITORED_WORKFLOWS.items():
            active = workflow_active(wf_id)
            if active is False:
                activate_workflow(wf_id)
                return "WORKFLOW_INATIVO", f"{label} ({wf_id}) estava INATIVO. Reativado. Falhas originais: {reasons}", True
        return "EXEC_NAO_ENCONTRADA", f"Execucao nao apareceu no n8n mas os workflows monitorados estao ativos (possivel 401/$env/cache Evolution). Falhas: {reasons}", False

    if any("esperado=" in f["reason"] for f in failures):
        return "INTENT_MISMATCH", f"Classificacao de intent errada — possivel bug de prompt/logica, NAO auto-corrigivel com seguranca. Falhas: {reasons}", False

    return "DESCONHECIDO", f"Falha nao categorizada pelos padroes conhecidos. Falhas: {reasons}", False


def log_result(workflow, tipo_erro, mensagem, status, exec_id):
    payload = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workflow": workflow,
        "ultimo_no": "selfheal",
        "tipo_erro": tipo_erro,
        "mensagem": mensagem[:500],
        "exec_id": exec_id,
        "status": status,
    }
    try:
        requests.post(INGEST_WEBHOOK, json=payload, timeout=15)
    except Exception as e:
        print(f"Falha ao logar no n8n: {e}")


def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    code, output = run_suite()

    if code == 0:
        print(f"[{ts}] OK - 13/13 passou, nada a fazer")
        return

    failures = parse_failures(output)
    print(f"[{ts}] FALHOU - {len(failures)} cenario(s): {failures}")

    tipo_erro, mensagem, fix_aplicado = diagnose_and_fix(failures)

    if fix_aplicado:
        code2, output2 = run_suite()
        if code2 == 0:
            log_result("Test-Harness", tipo_erro, f"AUTO-CORRIGIDO: {mensagem}", "AUTO-CORRIGIDO", f"selfheal-{ts}")
            print(f"[{ts}] Corrigido automaticamente ({tipo_erro}) e a suite voltou a passar.")
            return
        else:
            failures2 = parse_failures(output2)
            mensagem += f" | Apos o fix, ainda falhou: {failures2}"

    log_result("Test-Harness", tipo_erro, mensagem, "ERRO", f"selfheal-{ts}")
    print(f"[{ts}] Requer intervencao humana ({tipo_erro}). Logado — alerta sai no proximo digest de 30min.")


if __name__ == "__main__":
    main()
