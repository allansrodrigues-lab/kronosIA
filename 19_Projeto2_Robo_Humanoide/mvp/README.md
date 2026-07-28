# MVP do Ferrão — o robô antes do robô

**Um Ferrão que funciona hoje, sem nenhuma peça comprada.**

Não é maquete: é o **mesmo cérebro** que vai comandar o robô físico. Quando o ESP32 chegar, muda-se **uma linha** e os mesmos comandos passam a mover motor de verdade.

---

## O que é

```
   Claude  ─────────┐
   (via MCP)        │
                    ├──>  PONTE  ──>  simulador na tela  (hoje)
   Painel no        │   localhost:4700
   navegador  ──────┤                 ESP32 no robô      (depois)
                    │
   curl / script ───┘
```

**A ponte é o cérebro.** Ela guarda o ângulo de cada junta, aplica os limites de curso, respeita a parada de emergência e registra tudo. Quem manda comando — você pelo painel, eu pelo MCP, ou um script — fala sempre com ela.

Trocar o simulador pelo robô real é mudar `ESP32_URL` no topo de `ferrao_bridge.py`. Nada mais.

---

## Como rodar

**1. Suba a ponte:**

```bash
cd 19_Projeto2_Robo_Humanoide/mvp
python ferrao_bridge.py
```

**2. Abra o painel:** http://localhost:4700

Você verá o robô desenhado, com 7 sliders (um por junta), botões de rotina, expressões do rosto, campo de fala, botão de emergência e o registro do que aconteceu.

Não precisa instalar nada — só Python, que você já tem.

---

## Como dar o controle ao Claude

Acrescente em `~/.claude.json`, dentro de `mcpServers`:

```json
"ferrao": {
  "command": "python",
  "args": ["C:/Users/Usuario/OneDrive/Documentos/Claude/Projects/teste Automação/19_Projeto2_Robo_Humanoide/mvp/mcp_ferrao.py"]
}
```

Reinicie o Claude Code. A partir daí dá pra pedir em português:

> *"Ferrão, olhe para a esquerda e acene."*
> *"Qual o estado das juntas?"*
> *"Fica com cara de pensando e imprime o cupom."*

### As 7 ferramentas

| Ferramenta | O que faz |
|---|---|
| `ferrao_estado` | Lê ângulo de todas as juntas, sensores, rosto e histórico |
| `ferrao_mover` | Move uma junta para um ângulo (respeitando o curso) |
| `ferrao_rotina` | acenar · cumprimentar · olhar_esquerda · olhar_direita · pegar · descanso |
| `ferrao_rosto` | neutro · atento · pensando · feliz · confuso · alerta · dormindo |
| `ferrao_falar` | Fala uma frase |
| `ferrao_imprimir` | Imprime cupom (o do QR do WhatsApp) |
| `ferrao_emergencia` | Aciona ou destrava a parada de emergência |

---

## Para que serve antes de existir o robô

1. **Desenvolver a lógica agora.** Rotinas, reações e diálogo ficam prontos e testados antes da primeira peça chegar.
2. **Demonstrar para cliente.** Dá para mostrar o conceito funcionando numa reunião **hoje**, sem robô montado.
3. **Treinar sem risco.** Errar ângulo no simulador não quebra servo de R$45.
4. **Ser o painel definitivo.** Quando o robô existir, é por esta tela que ele será operado.

---

## Segurança — o que a ponte impede

| Proteção | Como funciona |
|---|---|
| **Limite de curso** | Cada junta tem mín/máx do projeto. Pediu 500°? Vira 90°, com aviso |
| **Parada de emergência** | Acionada, nenhum comando de movimento passa — nem do Claude |
| **Movimento gradual** | O ângulo caminha até o alvo, não salta. Simula a inércia do servo |
| **Registro de tudo** | Toda ação fica no log, com hora |

Os limites são os mesmos de `PADRAO_Kit_Estrutural.md` — ombro −20 a 100°, cotovelo 0 a 120°, pescoço −70 a 70°.

---

## Quando o ESP32 chegar

1. Grave no ESP32 um servidor HTTP que aceite `POST /comando` com o mesmo JSON.
2. Em `ferrao_bridge.py`, mude:

```python
ESP32_URL = "http://192.168.0.50"   # IP do robô na sua rede
```

3. Pronto. Painel, MCP e scripts continuam iguais — agora movendo motor de verdade.

**É por isso que este MVP não é descartável:** ele é a camada de controle definitiva. O hardware entra por baixo.

---

## Arquivos

| Arquivo | O que é |
|---|---|
| `ferrao_bridge.py` | A ponte — estado, limites, rotinas, servidor HTTP |
| `painel.html` | O painel visual (SVG que se move) |
| `mcp_ferrao.py` | Servidor MCP — dá o controle ao Claude |

⚠️ **Detalhe do Windows que já quebrou uma vez:** o `mcp_ferrao.py` força UTF-8 no stdout. Sem isso, o primeiro acento derruba o protocolo JSON-RPC com `OSError: Invalid argument`. As duas linhas de `reconfigure` no topo não são enfeite.
