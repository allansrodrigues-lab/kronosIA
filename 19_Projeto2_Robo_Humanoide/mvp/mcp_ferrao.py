# -*- coding: utf-8 -*-
"""MCP do Ferrão — dá ao Claude o controle direto do robô.

Expõe o robô como ferramentas. O Claude passa a poder mover uma junta, mudar a
expressão do rosto, executar rotina, falar, imprimir cupom e ler os sensores —
tanto no simulador quanto, depois, no robô físico (a ponte é a mesma).

Protocolo MCP sobre stdio, JSON-RPC 2.0. Sem dependência externa.

Pré-requisito: a ponte precisa estar rodando (python ferrao_bridge.py).

Registrar em ~/.claude.json:

    "ferrao": {
      "command": "python",
      "args": ["C:/.../19_Projeto2_Robo_Humanoide/mvp/mcp_ferrao.py"]
    }
"""
import json
import sys
import urllib.error
import urllib.request

# Windows abre stdout em cp1252, e qualquer acento quebra o protocolo JSON-RPC.
# Sem estas duas linhas o MCP morre no primeiro "ê".
try:
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.stdin.reconfigure(encoding="utf-8")
except AttributeError:      # Python < 3.7
    pass

PONTE = "http://localhost:4700"


# ─────────────────────────── comunicação com a ponte ───────────────────────────

def ponte(caminho, payload=None):
    url = PONTE + caminho
    try:
        if payload is None:
            with urllib.request.urlopen(url, timeout=3) as r:
                return json.loads(r.read())
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as r:
            return json.loads(r.read())
    except urllib.error.URLError:
        return {"_offline": True}
    except Exception as e:
        return {"_erro": str(e)}


OFFLINE = ("O Ferrão está offline. Suba a ponte com:\n"
           "    cd 19_Projeto2_Robo_Humanoide/mvp && python ferrao_bridge.py\n"
           "e abra http://localhost:4700 para ver o robô.")


# ─────────────────────────────── as ferramentas ────────────────────────────────

FERRAMENTAS = [
    {
        "name": "ferrao_estado",
        "description": ("Lê o estado completo do Ferrão: ângulo de cada junta, leitura dos "
                        "sensores de distância, expressão do rosto, se a emergência está "
                        "acionada e o registro das últimas ações. Use antes de mover para "
                        "saber onde o robô está."),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ferrao_mover",
        "description": ("Move uma junta para um ângulo. A ponte limita ao curso real da junta, "
                        "então não há como forçar além do permitido."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "junta": {"type": "string",
                          "enum": ["ombro_e", "ombro_d", "cotovelo_e", "cotovelo_d",
                                   "pescoco_pan", "pescoco_tilt", "garra"],
                          "description": "Qual junta mover"},
                "angulo": {"type": "number", "description": "Ângulo alvo em graus"},
            },
            "required": ["junta", "angulo"],
        },
    },
    {
        "name": "ferrao_rotina",
        "description": ("Executa uma sequência pronta de movimentos: acenar, cumprimentar, "
                        "olhar_esquerda, olhar_direita, pegar ou descanso."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string",
                         "enum": ["acenar", "cumprimentar", "olhar_esquerda",
                                  "olhar_direita", "pegar", "descanso"]},
            },
            "required": ["nome"],
        },
    },
    {
        "name": "ferrao_rosto",
        "description": ("Muda a expressão do display do rosto. Use para dar retorno visual: "
                        "'atento' ao detectar alguém, 'pensando' ao processar, 'feliz' ao "
                        "confirmar, 'alerta' em erro."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "expressao": {"type": "string",
                              "enum": ["neutro", "atento", "pensando", "feliz",
                                       "confuso", "alerta", "dormindo"]},
            },
            "required": ["expressao"],
        },
    },
    {
        "name": "ferrao_falar",
        "description": "Faz o robô falar uma frase pelo alto-falante.",
        "inputSchema": {
            "type": "object",
            "properties": {"texto": {"type": "string", "description": "O que falar (até 200 caracteres)"}},
            "required": ["texto"],
        },
    },
    {
        "name": "ferrao_imprimir",
        "description": ("Imprime um cupom na impressora térmica do peito — normalmente com o "
                        "QR do WhatsApp, para levar a pessoa ao atendimento digital."),
        "inputSchema": {
            "type": "object",
            "properties": {"texto": {"type": "string", "description": "Conteúdo do cupom"}},
        },
    },
    {
        "name": "ferrao_emergencia",
        "description": ("Aciona ou destrava a parada de emergência. Com ela acionada, nenhum "
                        "movimento é aceito. Use ao menor sinal de comportamento estranho."),
        "inputSchema": {
            "type": "object",
            "properties": {"ativar": {"type": "boolean", "description": "true aciona, false destrava"}},
            "required": ["ativar"],
        },
    },
]


def executar(nome, args):
    if nome == "ferrao_estado":
        e = ponte("/estado")
        if e.get("_offline"):
            return OFFLINE
        linhas = ["FERRÃO — modo %s%s" % (e["modo"], "  ⚠ EMERGÊNCIA ACIONADA" if e["emergencia"] else ""),
                  "", "Juntas:"]
        for k, j in e["juntas"].items():
            marca = "" if abs(j["atual"] - j["alvo"]) < 1 else "  (movendo → %.0f°)" % j["alvo"]
            linhas.append("  %-14s %6.0f°   curso %d a %d%s" %
                          (k, j["atual"], j["min"], j["max"], marca))
        linhas += ["", "Sensores: esquerdo %s cm · direito %s cm"
                   % (e["sensores"]["dist_esq"], e["sensores"]["dist_dir"]),
                   "Rosto: %s" % e["rosto"],
                   "Cupons impressos: %d" % e["cupons"]]
        if e["fala"]:
            linhas.append('Falando: "%s"' % e["fala"])
        if e["log"]:
            linhas += ["", "Últimas ações:"] + ["  %s  %s" % (l["t"], l["msg"]) for l in e["log"][:5]]
        return "\n".join(linhas)

    if nome == "ferrao_mover":
        r = ponte("/comando", {"acao": "mover", "junta": args["junta"], "angulo": args["angulo"]})
        if r.get("_offline"):
            return OFFLINE
        if not r.get("ok"):
            return "Não foi possível mover: %s" % r.get("msg")
        extra = "" if r.get("msg") == "ok" else " — %s" % r.get("msg")
        return "%s → %s°%s" % (args["junta"], args["angulo"], extra)

    if nome == "ferrao_rotina":
        r = ponte("/comando", {"acao": "rotina", "nome": args["nome"]})
        if r.get("_offline"):
            return OFFLINE
        return "Rotina '%s' em execução." % args["nome"] if r.get("ok") else str(r.get("msg"))

    if nome == "ferrao_rosto":
        r = ponte("/comando", {"acao": "rosto", "expressao": args["expressao"]})
        if r.get("_offline"):
            return OFFLINE
        return "Rosto agora está '%s'." % args["expressao"]

    if nome == "ferrao_falar":
        r = ponte("/comando", {"acao": "falar", "texto": args["texto"]})
        if r.get("_offline"):
            return OFFLINE
        return 'O robô falou: "%s"' % args["texto"]

    if nome == "ferrao_imprimir":
        r = ponte("/comando", {"acao": "imprimir", "texto": args.get("texto", "QR do WhatsApp")})
        if r.get("_offline"):
            return OFFLINE
        return "Cupom impresso. Total na sessão: %s" % r.get("cupons")

    if nome == "ferrao_emergencia":
        r = ponte("/comando", {"acao": "emergencia", "ativar": args["ativar"]})
        if r.get("_offline"):
            return OFFLINE
        return "EMERGÊNCIA ACIONADA — movimentos bloqueados." if r.get("emergencia") \
            else "Emergência destravada. O robô volta a aceitar comandos."

    return "Ferramenta desconhecida: %s" % nome


# ─────────────────────────────── loop JSON-RPC ─────────────────────────────────

def responder(id_, resultado=None, erro=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if erro:
        msg["error"] = erro
    else:
        msg["result"] = resultado
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    for linha in sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        try:
            req = json.loads(linha)
        except Exception:
            continue

        metodo, id_ = req.get("method"), req.get("id")

        if metodo == "initialize":
            responder(id_, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "ferrao", "version": "1.0.0"},
            })
        elif metodo == "tools/list":
            responder(id_, {"tools": FERRAMENTAS})
        elif metodo == "tools/call":
            p = req.get("params", {})
            try:
                texto = executar(p.get("name"), p.get("arguments") or {})
                responder(id_, {"content": [{"type": "text", "text": texto}]})
            except Exception as e:
                responder(id_, {"content": [{"type": "text", "text": "Erro: %s" % e}],
                                "isError": True})
        elif metodo and metodo.startswith("notifications/"):
            pass
        elif id_ is not None:
            responder(id_, erro={"code": -32601, "message": "método não suportado: %s" % metodo})


if __name__ == "__main__":
    main()
