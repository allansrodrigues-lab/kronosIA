#!/usr/bin/env python3
"""
Kronos Client Onboarding Pipeline — Pipeline A
Sobe um cliente novo do zero a partir de um arquivo de config.

Uso:
  python3 onboard-cliente.py config.json
  python3 onboard-cliente.py config.json --dry-run
  python3 onboard-cliente.py config.json --skip-evo     # pula Evolution
  python3 onboard-cliente.py config.json --skip-n8n     # pula workflows

Rodar no VPS (Evolution API é localhost):
  scp onboard-cliente.py config.json root@2.24.101.180:/docker/
  ssh root@2.24.101.180 "python3 /docker/onboard-cliente.py /docker/config.json"
"""

import json, sys, time, re, argparse, requests
from datetime import datetime

# ─── Config do servidor ───────────────────────────────────────────────────────
N8N_BASE    = "https://n8n.kronosintelligence.com.br"
# JWT expira 2026-07-12 — renovar em Settings → API (label: kronos-claude)
N8N_JWT     = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3NGNjNmViNi05MTFjLTRhZTEtYTFhZS1lMWMzM2M1Yjg4OTkiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDZjYTdiMDQtYWIzZS00MDhiLThkZmEtMDA3NzA3MDA3NGE4IiwiaWF0IjoxNzgxNDM3MjEyLCJleHAiOjE3ODM5OTgwMDB9.0Ikl1TLiNW9YQ7n8Qa3n5xV9p8WRMd6wJDNdY5FrPA4"
EVO_BASE    = "http://localhost:8080"
EVO_KEY     = "kronos-evo-key-2024"

# ─── Valores do template Aurora (o que será substituído por cliente) ──────────
TEMPLATE_SHEETS_ID     = "1ZlDFYkgx6aXUM0ayj1e1_K6uX0cruo7VuCcmg1_w5ps"
TEMPLATE_WEBHOOK_PATH  = "whatsapp"
TEMPLATE_BUFFER_TABLE  = "aurora_buffer_mensagens"
ERROR_WF_ID            = "X29vC9p5WB38iZFI"  # kronos-error-handler (compartilhado)

# ─── Templates por nicho (role → workflow_id) ─────────────────────────────────
# Ordem importa: sub-workflows antes do orquestrador (que referencia os subs)
TEMPLATES = {
    "estetica": [
        ("lembrete",     "vGfBm7cdjsESJtIH"),
        ("pos_venda",    "wItuI9j8dVSbq0F0"),
        ("atendimento",  "TDJQkNQDJh9PnmSh"),
        ("agendamento",  "02-agendamento-bia"),
        ("orquestrador", "Orq01RouterV2aa1"),
    ],
    "odonto": [
        ("lembrete",     "vGfBm7cdjsESJtIH"),
        ("atendimento",  "03-atendimento-odonto"),
        ("agendamento",  "02-agendamento-odonto"),
        ("orquestrador", "01-orquestrador-odonto"),
    ],
    "advocacia": [
        ("agente",       "TZDQobW44zZwkjOB"),
        ("orquestrador", "QEawJtNsqlNGwrw0"),
    ],
}

# IDs dos sub-workflows que o orquestrador referencia (para corrigir após clone)
SUB_REFS = {
    "estetica": {
        "02-agendamento-bia": "agendamento",
        "TDJQkNQDJh9PnmSh":  "atendimento",
        "wItuI9j8dVSbq0F0":  "pos_venda",
    },
    "odonto": {
        "02-agendamento-odonto": "agendamento",
        "03-atendimento-odonto": "atendimento",
    },
    "advocacia": {
        "TZDQobW44zZwkjOB": "agente",
    },
}


# ─── HTTP helpers ─────────────────────────────────────────────────────────────
def n8n(method, path, **kw):
    r = requests.request(method, f"{N8N_BASE}/api/v1{path}",
                         headers={"X-N8N-API-KEY": N8N_JWT}, timeout=30, **kw)
    r.raise_for_status()
    return r.json()

def evo(method, path, **kw):
    r = requests.request(method, f"{EVO_BASE}{path}",
                         headers={"apikey": EVO_KEY, "Content-Type": "application/json"},
                         timeout=20, **kw)
    r.raise_for_status()
    return r.json()

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ─── Stage 1: Validar config ──────────────────────────────────────────────────
def stage_validate(cfg):
    required = ["slug", "nome", "nicho", "numero_wa", "sheets_id", "webhook_path"]
    missing = [f for f in required if not cfg.get(f)]
    if missing:
        raise ValueError(f"Campos obrigatórios faltando: {missing}")
    if cfg["nicho"] not in TEMPLATES:
        raise ValueError(f"nicho='{cfg['nicho']}' inválido. Opções: {list(TEMPLATES)}")
    if not re.match(r'^[a-z0-9_-]+$', cfg["slug"]):
        raise ValueError(f"slug deve ser lowercase alfanumérico com _ ou -: '{cfg['slug']}'")
    log("✓ Config válido")


# ─── Stage 2: Criar instância Evolution ──────────────────────────────────────
def stage_evo(cfg, dry_run):
    slug = cfg["slug"]
    log(f"▶ Evolution: criando instância '{slug}'...")
    if dry_run:
        log("  [DRY-RUN] pulado"); return

    # Checar se já existe
    try:
        instances = evo("GET", "/instance/fetchInstances")
        if isinstance(instances, list):
            existing = [i.get("instance", {}).get("instanceName", "") for i in instances]
        elif isinstance(instances, dict):
            existing = [instances.get("instance", {}).get("instanceName", "")]
        else:
            existing = []
        if slug in existing:
            log(f"  ⚠ Instância '{slug}' já existe — reutilizando"); return
    except Exception as e:
        log(f"  ⚠ Não foi possível verificar instâncias existentes: {e}")

    payload = {
        "instanceName":  slug,
        "integration":   "WHATSAPP-BAILEYS",
        "qrcode":        True,
        "reject_call":   True,
        "groups_ignore": True,
        "always_online": False,
        "read_messages": True,
    }
    result = evo("POST", "/instance/create", json=payload)
    inst = result.get("instance", result)
    log(f"  ✓ Instância criada: {inst.get('instanceName','?')} "
        f"(state={inst.get('state', inst.get('connectionStatus','?'))})")
    log(f"  → Próximo: escanear QR em POST {EVO_BASE}/instance/connect/{slug}")


# ─── Stage 3: Clonar workflows ───────────────────────────────────────────────
def stage_clone_workflows(cfg, dry_run):
    slug      = cfg["slug"]
    nicho     = cfg["nicho"]
    sheets    = cfg["sheets_id"]
    wh_path   = cfg["webhook_path"]
    buf_table = f"{slug}_buffer"
    error_wf  = cfg.get("error_wf_id", ERROR_WF_ID)
    templates = TEMPLATES[nicho]
    sub_refs  = SUB_REFS.get(nicho, {})

    log(f"▶ n8n: clonando {len(templates)} workflow(s) (nicho={nicho})...")

    cloned = {}   # role → new_id
    id_map = {}   # old_id → new_id  (para corrigir referências)

    for role, tmpl_id in templates:
        log(f"  ↓ Baixando template '{role}' ({tmpl_id})...")
        if dry_run:
            cloned[role] = f"DRY_{role}"; log(f"    [DRY-RUN] pulado"); continue

        try:
            wf = n8n("GET", f"/workflows/{tmpl_id}")
        except Exception as e:
            log(f"    ✗ Falha ao baixar {tmpl_id}: {e}"); continue

        # ── Substituições por string no JSON serializado ──────────────────────
        raw = json.dumps(wf)
        raw = raw.replace(TEMPLATE_SHEETS_ID, sheets)
        raw = raw.replace(f'"{TEMPLATE_WEBHOOK_PATH}"', f'"{wh_path}"')
        raw = raw.replace(TEMPLATE_BUFFER_TABLE, buf_table)
        wf  = json.loads(raw)

        # ── Renomear e limpar campos gerenciados pelo servidor ────────────────
        original_name = wf.get("name", role)
        wf["name"]    = f"{slug}-{original_name}"
        for field in ("id", "createdAt", "updatedAt", "versionId",
                      "meta", "sharedWithProjects", "shared"):
            wf.pop(field, None)

        # ── Forçar error handler e iniciar inativo ────────────────────────────
        wf.setdefault("settings", {})["errorWorkflow"] = error_wf
        wf["active"] = False

        # ── Criar no n8n ──────────────────────────────────────────────────────
        log(f"    ↑ Criando '{wf['name']}'...")
        try:
            result = n8n("POST", "/workflows", json=wf)
            new_id = result["id"]
            cloned[role] = new_id
            id_map[tmpl_id] = new_id
            log(f"    ✓ Criado id={new_id}")
        except Exception as e:
            log(f"    ✗ Falha ao criar '{wf['name']}': {e}")

    # ── Corrigir referências executeWorkflow no orquestrador ─────────────────
    if "orquestrador" in cloned and not dry_run:
        orq_id = cloned["orquestrador"]
        log(f"  🔧 Corrigindo referências executeWorkflow no orquestrador ({orq_id})...")
        try:
            orq_wf = n8n("GET", f"/workflows/{orq_id}")
            raw = json.dumps(orq_wf)
            substituted = 0
            for old_id, role_name in sub_refs.items():
                if old_id in id_map:
                    raw = raw.replace(f'"{old_id}"', f'"{id_map[old_id]}"')
                    substituted += 1
                    log(f"    {old_id} → {id_map[old_id]} ({role_name})")
            if substituted:
                orq_wf = json.loads(raw)
                orq_wf.pop("versionId", None)
                n8n("PUT", f"/workflows/{orq_id}", json=orq_wf)
                log(f"    ✓ {substituted} referência(s) corrigida(s)")
            else:
                log(f"    ⚠ Nenhuma referência substituída — verificar manualmente")
        except Exception as e:
            log(f"    ✗ Falha ao corrigir referências: {e}")

    # ── Ativar todos ──────────────────────────────────────────────────────────
    log(f"  ▶ Ativando {len(cloned)} workflow(s)...")
    for role, wf_id in cloned.items():
        if dry_run or wf_id.startswith("DRY_"):
            log(f"    [DRY-RUN] {role}"); continue
        try:
            n8n("PATCH", f"/workflows/{wf_id}/activate")
            log(f"    ✓ Ativo: {role} ({wf_id})")
        except Exception as e:
            log(f"    ✗ Falha ao ativar {role} ({wf_id}): {e}")

    return cloned


# ─── Stage 4: Configurar webhook no Evolution ─────────────────────────────────
def stage_evo_webhook(cfg, dry_run):
    slug        = cfg["slug"]
    wh_path     = cfg["webhook_path"]
    webhook_url = f"{N8N_BASE}/webhook/{wh_path}"
    log(f"▶ Evolution: configurando webhook → {webhook_url}...")
    if dry_run:
        log("  [DRY-RUN] pulado"); return

    payload = {
        "webhook": {
            "enabled":         True,
            "url":             webhook_url,
            "webhookByEvents": False,
            "base64":          False,
            "events":          ["MESSAGES_UPSERT"],
        }
    }
    try:
        evo("POST", f"/webhook/set/{slug}", json=payload)
        log(f"  ✓ Webhook configurado")
    except Exception as e:
        log(f"  ⚠ Webhook falhou ({e}) — configurar manualmente na UI do Evolution")


# ─── Stage 5: Smoke test ──────────────────────────────────────────────────────
def stage_smoke_test(cfg, dry_run):
    slug    = cfg["slug"]
    wh_path = cfg["webhook_path"]
    url     = f"{N8N_BASE}/webhook/{wh_path}"
    log(f"▶ Smoke test: POST {url}...")
    if dry_run:
        log("  [DRY-RUN] pulado"); return "DRY-RUN"

    payload = {
        "event":    "messages.upsert",
        "instance": slug,
        "data": {
            "key":              {"remoteJid": "5511999999999@s.whatsapp.net",
                                 "fromMe": False, "id": "ONBOARD-SMOKE-TEST"},
            "pushName":         "Teste Onboarding",
            "message":          {"conversation": "Quero agendar uma consulta"},
            "messageType":      "conversation",
            "messageTimestamp": int(time.time()),
        },
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        log(f"  HTTP {r.status_code}")
        return r.status_code
    except Exception as e:
        log(f"  ⚠ {e}"); return 0


# ─── Stage 6: Relatório final ─────────────────────────────────────────────────
def stage_report(cfg, cloned, smoke, elapsed):
    slug   = cfg["slug"]
    status = "PASS" if smoke in (200, "DRY-RUN") else "WARN"

    print("\n" + "═" * 62)
    print(f"  KRONOS DEPLOY REPORT — {slug}")
    print("═" * 62)
    print(f"  nome          {cfg['nome']}")
    print(f"  nicho         {cfg['nicho']}")
    print(f"  número WA     {cfg['numero_wa']}")
    print(f"  webhook       /webhook/{cfg['webhook_path']}")
    print(f"  sheets_id     {cfg['sheets_id']}")
    print(f"  smoke HTTP    {smoke}")
    print(f"  status        {status}")
    print(f"  tempo         {elapsed:.1f}s")
    if cloned:
        print(f"  workflows:")
        for role, wf_id in cloned.items():
            print(f"    {role:<15} {wf_id}")
    print("═" * 62)
    if status == "PASS":
        print(f"  ✅ Deploy concluído!")
        print(f"  📱 Próximo: vincular WhatsApp do cliente")
        print(f"     1. (VPS) curl -X GET {EVO_BASE}/instance/connect/{slug}")
        print(f"     2. Abrir QR no WhatsApp do cliente → escanear")
        print(f"     3. Testar enviando mensagem para {cfg['numero_wa']}")
    else:
        print(f"  ⚠  Deploy com alertas — revisar smoke test e logs do n8n")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Kronos Client Onboarding Pipeline")
    ap.add_argument("config",       help="Arquivo JSON de config do cliente")
    ap.add_argument("--dry-run",    action="store_true", help="Simula sem alterações")
    ap.add_argument("--skip-evo",   action="store_true", help="Pula Evolution API")
    ap.add_argument("--skip-n8n",   action="store_true", help="Pula clonagem de workflows")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg.pop("_instrucoes", None)  # remove campo de documentação se presente

    t0 = time.time()
    prefix = "[DRY-RUN] " if args.dry_run else ""
    log(f"{prefix}Iniciando onboarding: {cfg.get('slug','?')} ({cfg.get('nicho','?')})")

    try:
        stage_validate(cfg)
        if not args.skip_evo:
            stage_evo(cfg, args.dry_run)
        cloned = {}
        if not args.skip_n8n:
            cloned = stage_clone_workflows(cfg, args.dry_run) or {}
        stage_evo_webhook(cfg, args.dry_run)
        smoke = stage_smoke_test(cfg, args.dry_run)
        stage_report(cfg, cloned, smoke, time.time() - t0)
    except ValueError as e:
        print(f"\n✗ Erro de validação: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
