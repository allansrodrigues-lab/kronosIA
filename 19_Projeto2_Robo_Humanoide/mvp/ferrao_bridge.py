# -*- coding: utf-8 -*-
"""Ferrão — Ponte de controle.

O cérebro em software do robô. Mantém o estado das juntas e atende três clientes:

    Claude (via MCP)  ─┐
    Painel no navegador├──> PONTE (localhost:4700) ──> simulador | ESP32 real
    Curl / script      ┘

Enquanto não há hardware, o modo é "simulado" e o painel desenha o robô.
Quando o ESP32 existir, muda-se ESP32_URL e o mesmo comando vai para o robô físico.

Rodar:  python ferrao_bridge.py
Painel: http://localhost:4700
"""
import json
import os
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORTA = 4700
PASTA = os.path.dirname(os.path.abspath(__file__))

# Quando o robô físico existir, colocar aqui o IP do ESP32 (ex.: "http://192.168.0.50")
ESP32_URL = None

# Limites reais do projeto — ver PADRAO_Kit_Estrutural.md
JUNTAS = {
    "ombro_e":     {"min": -20, "max": 100, "atual": 0, "alvo": 0, "nome": "Ombro esquerdo"},
    "ombro_d":     {"min": -20, "max": 100, "atual": 0, "alvo": 0, "nome": "Ombro direito"},
    "cotovelo_e":  {"min": 0,   "max": 120, "atual": 0, "alvo": 0, "nome": "Cotovelo esquerdo"},
    "cotovelo_d":  {"min": 0,   "max": 120, "atual": 0, "alvo": 0, "nome": "Cotovelo direito"},
    "pescoco_pan": {"min": -70, "max": 70,  "atual": 0, "alvo": 0, "nome": "Pescoço (girar)"},
    "pescoco_tilt":{"min": -25, "max": 25,  "atual": 0, "alvo": 0, "nome": "Cabeça (inclinar)"},
    "garra":       {"min": 0,   "max": 90,  "atual": 0, "alvo": 0, "nome": "Garra"},
}

EXPRESSOES = ["neutro", "atento", "pensando", "feliz", "confuso", "alerta", "dormindo"]

ROTINAS = {
    "acenar":      [("ombro_d", 70), ("cotovelo_d", 60), ("ombro_d", 90),
                    ("ombro_d", 60), ("ombro_d", 90), ("ombro_d", 0), ("cotovelo_d", 0)],
    "cumprimentar":[("pescoco_pan", 0), ("pescoco_tilt", 10), ("pescoco_tilt", 0)],
    "olhar_esquerda": [("pescoco_pan", -50)],
    "olhar_direita":  [("pescoco_pan", 50)],
    "descanso":    [("ombro_e", 0), ("ombro_d", 0), ("cotovelo_e", 0),
                    ("cotovelo_d", 0), ("pescoco_pan", 0), ("pescoco_tilt", 0), ("garra", 0)],
    "pegar":       [("ombro_d", 60), ("cotovelo_d", 80), ("garra", 90),
                    ("garra", 10), ("cotovelo_d", 40)],
}

estado = {
    "modo": "simulado",
    "energia": True,
    "emergencia": False,
    "juntas": JUNTAS,
    "sensores": {"dist_esq": 200, "dist_dir": 200},
    "rosto": "neutro",
    "fala": "",
    "cupons": 0,
    "log": [],
}
trava = threading.Lock()


def registrar(msg):
    estado["log"].insert(0, {"t": time.strftime("%H:%M:%S"), "msg": msg})
    del estado["log"][40:]


def encaminhar_para_esp32(payload):
    """Quando o robô físico existir, repassa o comando. Hoje não faz nada."""
    if not ESP32_URL:
        return
    try:
        req = urllib.request.Request(
            ESP32_URL + "/comando",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception as e:
        registrar("Falha ao falar com o ESP32: %s" % e)


def mover(junta, angulo):
    if estado["emergencia"]:
        return False, "Emergência acionada — destrave antes de mover"
    if junta not in estado["juntas"]:
        return False, "Junta desconhecida: %s" % junta
    j = estado["juntas"][junta]
    a = max(j["min"], min(j["max"], float(angulo)))
    limitado = a != float(angulo)
    j["alvo"] = a
    encaminhar_para_esp32({"acao": "mover", "junta": junta, "angulo": a})
    registrar("%s → %.0f°%s" % (j["nome"], a, " (limitado)" if limitado else ""))
    return True, ("Limitado a %.0f° pelo curso da junta" % a) if limitado else "ok"


def animar():
    """Move o 'atual' na direção do 'alvo' — simula a inércia do servo."""
    while True:
        with trava:
            if estado["energia"] and not estado["emergencia"]:
                for j in estado["juntas"].values():
                    d = j["alvo"] - j["atual"]
                    if abs(d) > 0.5:
                        j["atual"] += max(-4, min(4, d))
                    else:
                        j["atual"] = j["alvo"]
        time.sleep(0.04)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        corpo = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path in ("/", "/painel", "/index.html"):
            caminho = os.path.join(PASTA, "painel.html")
            if not os.path.exists(caminho):
                return self._json({"erro": "painel.html não encontrado"}, 404)
            corpo = open(caminho, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
        elif self.path == "/estado":
            with trava:
                self._json(estado)
        elif self.path == "/rotinas":
            self._json({"rotinas": list(ROTINAS), "expressoes": EXPRESSOES})
        else:
            self._json({"erro": "rota desconhecida"}, 404)

    def do_POST(self):
        tam = int(self.headers.get("Content-Length", 0))
        try:
            dados = json.loads(self.rfile.read(tam) or b"{}")
        except Exception:
            return self._json({"erro": "JSON inválido"}, 400)

        acao = dados.get("acao")
        with trava:
            if acao == "mover":
                ok, msg = mover(dados.get("junta"), dados.get("angulo", 0))
                return self._json({"ok": ok, "msg": msg})

            if acao == "rotina":
                nome = dados.get("nome")
                if nome not in ROTINAS:
                    return self._json({"ok": False, "msg": "rotina desconhecida"}, 400)
                threading.Thread(target=executar_rotina, args=(nome,), daemon=True).start()
                registrar("Rotina: %s" % nome)
                return self._json({"ok": True, "msg": "rotina '%s' iniciada" % nome})

            if acao == "rosto":
                exp = dados.get("expressao", "neutro")
                if exp not in EXPRESSOES:
                    return self._json({"ok": False, "msg": "expressão desconhecida"}, 400)
                estado["rosto"] = exp
                encaminhar_para_esp32({"acao": "rosto", "expressao": exp})
                registrar("Rosto: %s" % exp)
                return self._json({"ok": True})

            if acao == "falar":
                texto = (dados.get("texto") or "")[:200]
                estado["fala"] = texto
                encaminhar_para_esp32({"acao": "falar", "texto": texto})
                registrar('Falou: "%s"' % texto)
                return self._json({"ok": True})

            if acao == "imprimir":
                estado["cupons"] += 1
                registrar("Cupom impresso (%s)" % (dados.get("texto") or "QR do WhatsApp"))
                return self._json({"ok": True, "cupons": estado["cupons"]})

            if acao == "emergencia":
                estado["emergencia"] = bool(dados.get("ativar", True))
                registrar("EMERGÊNCIA " + ("ACIONADA" if estado["emergencia"] else "destravada"))
                return self._json({"ok": True, "emergencia": estado["emergencia"]})

            if acao == "sensor":  # o painel simula alguém se aproximando
                estado["sensores"]["dist_esq"] = float(dados.get("esq", 200))
                estado["sensores"]["dist_dir"] = float(dados.get("dir", 200))
                return self._json({"ok": True})

        return self._json({"erro": "ação desconhecida"}, 400)


def executar_rotina(nome):
    for junta, ang in ROTINAS[nome]:
        with trava:
            mover(junta, ang)
        time.sleep(0.7)


if __name__ == "__main__":
    threading.Thread(target=animar, daemon=True).start()
    print("=" * 58)
    print(" FERRÃO — ponte de controle")
    print(" Painel:  http://localhost:%d" % PORTA)
    print(" Modo:    %s" % ("FÍSICO (%s)" % ESP32_URL if ESP32_URL else "SIMULADO"))
    print(" Parar:   Ctrl+C")
    print("=" * 58)
    ThreadingHTTPServer(("127.0.0.1", PORTA), Handler).serve_forever()
