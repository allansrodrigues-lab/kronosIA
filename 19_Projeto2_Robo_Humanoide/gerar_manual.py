# -*- coding: utf-8 -*-
"""Gera o MANUAL COMPLETO do Ferrão: junta todos os documentos num PDF único.

Rode sempre que qualquer arquivo .md da pasta mudar:

    python gerar_manual.py

Saída: Ferrao_MANUAL_COMPLETO.pdf (na pasta do projeto e na Área de Trabalho).
Para incluir um documento novo, basta acrescentá-lo na lista DOCUMENTOS abaixo.
"""
import os
import shutil
import subprocess
import sys
from datetime import date

PASTA = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
SAIDA = "Ferrao_MANUAL_COMPLETO.pdf"

# Ordem do manual. Para adicionar capítulo novo, inclua aqui.
DOCUMENTOS = [
    ("Projeto_Robo_Sucata.md",      "PARTE I — O PROJETO"),
    ("PADRAO_Kit_Estrutural.md",    "PARTE II — PADRÃO ESTRUTURAL"),
    ("Ferrao_GUIA_DE_COMPRA.md",    "PARTE III — GUIA DE COMPRA"),
    ("FORNECEDORES.md",             "PARTE IV — FORNECEDORES E REPOSIÇÃO"),
    ("FERRO_VELHO_Bilhete.md",      "PARTE V — BILHETE DO FERRO-VELHO"),
    ("FASE_A_Lista_de_Compra.md",   "PARTE VI — PRIMEIRA COMPRA"),
    ("Guia_Sistema_Eletronica.md",  "PARTE VII — CURSO DE ELETRÔNICA"),
    ("mvp/README.md",               "PARTE VIII — MVP: O ROBÔ EM SOFTWARE"),
]

CAPA = """# FERRÃO

**Manual completo do projeto**

Robô humanoide de sucata · torso de mala rígida sobre base de cadeira
Agente físico da Kronos Intelligence

Versão de {data}

---

## Como usar este manual

Este arquivo é gerado automaticamente a partir dos documentos da pasta do projeto.
Sempre que uma decisão mudar, o documento correspondente é editado e o manual
é regerado — nunca há duas versões divergentes circulando.

| Parte | O que traz |
|---|---|
| I | Projeto técnico: veredito, peças, montagem, controle, funções, acabamento |
| II | Padrão estrutural: lista de corte, furação e pinagem (replicável entre unidades) |
| III | Guia de compra por bloco |
| IV | Fornecedores, alternativos e kit de reposição |
| V | O que garimpar no ferro-velho |
| VI | A primeira compra, item a item |
| VII | Curso de eletrônica, do zero |

**Para regerar:** `python gerar_manual.py`

---
"""


def montar():
    partes = [CAPA.format(data=date.today().strftime("%d/%m/%Y"))]
    faltando = []

    for arquivo, titulo in DOCUMENTOS:
        caminho = os.path.join(PASTA, arquivo)
        if not os.path.exists(caminho):
            faltando.append(arquivo)
            continue
        with open(caminho, encoding="utf-8") as f:
            texto = f.read()
        # o título de nível 1 do arquivo vira nível 2, para o capítulo ficar acima
        linhas = []
        for ln in texto.split("\n"):
            if ln.startswith("# "):
                ln = "#" + ln
            linhas.append(ln)
        partes.append("\n\n# " + titulo + "\n\n" + "\n".join(linhas))

    if faltando:
        print("AVISO — nao encontrados:", ", ".join(faltando))

    return "\n\n---\n\n".join(partes)


def main():
    juntado = os.path.join(PASTA, "_manual_temp.md")
    with open(juntado, "w", encoding="utf-8") as f:
        f.write(montar())

    conversor = os.path.join(PASTA, "md_para_pdf.py")
    destino = os.path.join(PASTA, SAIDA)

    r = subprocess.run(
        [sys.executable, conversor, juntado, destino, "Ferrao - Manual Completo"],
        capture_output=True, text=True
    )
    print(r.stdout.strip() or r.stderr.strip())

    os.remove(juntado)

    if os.path.exists(destino):
        shutil.copy(destino, os.path.join(DESKTOP, SAIDA))
        kb = os.path.getsize(destino) // 1024
        print("Manual gerado: %s (%d KB) — copia na Area de Trabalho." % (SAIDA, kb))
    else:
        print("ERRO: o PDF nao foi criado.")


if __name__ == "__main__":
    main()
