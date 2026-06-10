# 🗺️ Guia Rápido — Kronos Intelligence

Guia em linguagem simples pra você não se perder. (Allan, dono do negócio.)

---

## 📍 Onde "mora" o projeto (3 lugares)

| Lugar | O que é | Pra que serve |
|---|---|---|
| 💻 **Seu PC** | A pasta `teste Automação` no OneDrive | Onde os arquivos ficam e onde editamos |
| ☁️ **GitHub** | Repositório `kronosIA` (público) | "Backup na nuvem" + de onde o servidor baixa as mudanças |
| 🌐 **VPS Hostinger** | Servidor com IP `2.24.101.180` | Onde o **site no ar** roda de verdade (`kronosintelligence.com.br`) |

> ⚠️ **Importante:** editar no PC e salvar no GitHub **NÃO** atualiza o site sozinho. Precisa do **deploy** (subir pro VPS). Quem faz isso é o Claude.

---

## 📂 Mapa das pastas

| Pasta | O que tem |
|---|---|
| `07_Recursos/` | **Site** (`index.html`), **workflows do n8n**, **identidade visual** (logos) |
| `04_Agentes_IA/` | Prompts e configs dos agentes de IA |
| `05_Comercial/` | 🔒 Materiais de venda (PRIVADO — não vai pro GitHub) |
| `.claude/skills/` | As "habilidades" do Claude pra este projeto |

---

## 🔄 Como funciona (o fluxo)

1. Você **pede** uma mudança ao Claude (ex: "muda o texto do hero")
2. Claude **edita** o arquivo e **salva no GitHub** (commit + push)
3. Claude faz o **deploy** (sobe pro VPS via SSH) — automático
4. Você dá **Ctrl + F5** no site pra ver (ou janela anônima `Ctrl + Shift + N` pra garantir)

---

## 🔗 Endereços importantes

- **Site:** https://kronosintelligence.com.br
- **n8n (automações):** https://n8n.kronosintelligence.com.br
- **GitHub:** https://github.com/allansrodrigues-lab/kronosIA
- **WhatsApp do negócio:** +55 19 97126-6736

---

## ⛔ Regras de ouro (pra não se perder)

1. **Não precisa mexer no GitHub Desktop** — o Claude cuida do Git. (Foi mexer lá que criou a confusão do Cloudflare.)
2. Se aparecer algo de **"Cloudflare", "branch", "merge", "conflito"** e você não entender → **não clique, pergunta pro Claude.**
3. Sempre teste o site na **janela anônima** (`Ctrl + Shift + N`) pra não ver versão velha (cache).
4. Materiais comerciais ficam em `05_Comercial/` e **nunca** vão pro GitHub público.

---

## 📌 Pendências (atualizar conforme resolver)

- [ ] Ativar o workflow `06-lead-landing` no n8n (resolver credencial do Google Sheets) pra leads caírem no CRM
