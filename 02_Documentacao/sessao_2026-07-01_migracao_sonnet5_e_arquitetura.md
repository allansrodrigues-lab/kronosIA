# Sessão 2026-07-01 — Migração para Claude Sonnet 5 + arquitetura modular

Registro de decisões e mudanças. Branch de trabalho: `claude/sonnet-5-autonomous-ai-umphv5`.

---

## 1. Contexto de partida
Gatilho: artigo sobre o lançamento do **Claude Sonnet 5** (mais capaz para trabalho agêntico, mais barato, thinking adaptativo, preço promocional US$ 2/US$ 10 por MTok até 31/08/2026). ID oficial do modelo: **`claude-sonnet-5`** (sem sufixo de data). Objetivo: deixar os protótipos Kronos afinados e consistentes no Sonnet 5 para demonstração (US$ 20 de crédito no console; uso baixo de teste por enquanto).

Estado anterior dos modelos no repo:
- Classificação de intent (orquestrador Aurora): `claude-haiku-4-5-20251001` (Haiku)
- Agentes especialistas (Bia/Clara/Diana/Ana): `claude-sonnet-4-6`

---

## 2. Decisões tomadas
- **Escopo da migração:** só os **agentes** (Sonnet 4.6 → Sonnet 5). **Haiku 4.5 mantido** no classificador de intent (barato para alto volume; todo mundo passa por ele).
- **Thinking:** **adaptativo** (padrão do Sonnet 5) — prioridade em qualidade/perfeição para a demonstração. Se a latência incomodar ao vivo, baixar `output_config.effort` para `"low"`/`"medium"`.

---

## 3. Mudanças aplicadas (commitadas)

### Runtime — workflows de agente (`07_Recursos/`)
Workflows **02 (Bia/agendamento)**, **03 (Clara/atendimento)**, **05 (Diana/pós-venda)**:
- `claude-sonnet-4-6` → **`claude-sonnet-5`**
- **Removido `temperature`** (0.3/0.4/0.5) — no Sonnet 5 `temperature` não-default retorna **HTTP 400**.
- **`max_tokens` 500/600 → 2048** — folga para o thinking adaptativo não truncar a resposta JSON.
- **Parser corrigido:** `content?.[0]?.text` → `content?.find(b => b.type === 'text')?.text` — com thinking ligado, o bloco 0 pode ser um bloco de *thinking* (texto vazio, pois `display` padrão é `"omitted"`), então é preciso achar o bloco `text`.

### Correção de bug pré-existente — `workflow_05_pos_venda.json`
O `systemPrompt` da Diana havia sido escrito com **quebras de linha reais e aspas duplas não escapadas** dentro da string JSON → arquivo inteiro **inválido** para importação no n8n (defeito que já vinha do HEAD, não introduzido agora). O valor do nó foi reescrito com codificação JSON correta (`\n` e `\"` escapados), **texto do prompt idêntico**. Arquivo agora valida (14 nós).

### Documentação sincronizada
- Guides e montagem_manual dos workflows 02/03/05 (model, sem temperature, parser).
- `07_Recursos/google_sheets_setup.md` — variável `anthropic_model_agentes` → `claude-sonnet-5`.
- `CLAUDE.md` — linha do LLM atualizada (Sonnet 5 + nota de thinking adaptativo/sem temperature).
- `09_Pizzaria_SantaAna/agentes/01_agente_pedido_ana.md` — modelo → Sonnet 5.

Verificação final: nenhum `claude-sonnet-4-6` restante no repositório; os 3 workflows validam como JSON.

---

## 4. Protótipos e serviços do Kronos (mapa)

Bots WhatsApp de clínica (compartilham os MESMOS workflows de `07_Recursos`, mudando só instância + planilha → migração cobre os dois):

| Protótipo | Nicho | Instância | Número | Webhook |
|---|---|---|---|---|
| **Aurora** | Estética | `clinica01` | 5519971514971 | `/webhook/whatsapp` |
| **OdontoVita** | Odonto (fictícia) | `kronosdemo` | 5519997237404 | `/webhook/whatsapp-odonto` |

- OdontoVita é fictícia; será substituída pela **Dra. Débora Baruchi** (1ª prospect real — `08_Clinica_Odonto/`) quando fechar.
- **Pizzaria Santa Ana** (`09_`, agente Ana) — instância `instancia_santaana` ainda **não criada**; não está no ar.
- **Serviço de Parecer/Análise Científica** (`13_`) — gera parecer em PDF; hoje roda via `clinica01`. Ainda referencia Sonnet 4.6 (só doc/prompt): `13_Servico_AnaliseCientifica/base_conhecimento/01_motor_parecer.md` e `.claude/skills/kronos-parecer-cientifico/SKILL.md`. **Não migrado** ainda.

---

## 5. Arquitetura modular (visão do produto)

Princípio definido: **funções (ferramentas) reutilizáveis; cada nicho é uma composição das funções aplicáveis + base de conhecimento própria.** "Tudo se soma em um só."

O **parecer científico não é um nicho — é uma FUNÇÃO transversal.** Encaixa em: Saúde/Estética (piloto), Odonto, Advocacia, Nutrição, Marketing/Empresa. Não encaixa em Pizzaria.

### Matriz função × nicho
| Função (ferramenta) | Estética | Odonto | Advocacia | Nutrição | Pizzaria |
|---|:-:|:-:|:-:|:-:|:-:|
| Agendamento (Bia) | ✅ | ✅ | ✅ | ✅ | — |
| Atendimento/dúvidas (Clara) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Pós-venda (Diana) | ✅ | ✅ | — | ✅ | ✅ |
| Lembrete 24h | ✅ | ✅ | ✅ | ✅ | — |
| Captação/marketing (Eva) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Parecer científico** | ✅ | ✅ | ✅ | ✅ | — |
| Leitura de PDF | — | — | ✅ | — | — |
| Calculadora/pedido | — | — | — | — | ✅ |

### Como implementar no stack Kronos (sem reinventar)
1. **Cada função = um sub-workflow** (como Bia/Clara/Diana). Parecer vira `workflow_06_parecer` (lógica dos `.py` do `13_` como cadeia n8n: Config → Montar Prompt → **Sonnet 5** → apurar números por código → gerar PDF → enviar → CRM).
2. **Novo intent no orquestrador:** `PARECER` / `SOLICITAR_PARECER`, adicionado à lista de intents da Aurora.
3. **Composição por cliente via planilha de config:** flag por função (`func_parecer = on/off`, etc.). O mesmo orquestrador serve todos os nichos; muda só quais funções estão ligadas + a base de conhecimento.
4. **Modelo:** Sonnet 5, consistente com o resto.

---

## 6. Pendências / próximos passos
- [ ] **Deploy em produção:** editar versão **publicada** (`workflow_history`) no n8n e **reiniciar** o container (deactivate/reactivate) — editar o repo não aplica sozinho. Publicar também os subs. Rodar `/test-harness` (payloads `5500TEST*`) antes/depois.
- [ ] **Migrar o Parecer Científico para Sonnet 5** (doc/prompt em `13_` e na skill) — para consistência.
- [ ] **Documento de arquitetura modular** dedicado (`ARQUITETURA_MODULAR.md`) com a matriz função×nicho e o modelo de composição.
- [ ] **Embutir o parecer na Aurora:** intent `PARECER` no orquestrador + `workflow_06_parecer` (Sonnet 5) + flag na config.
- [ ] **Material TypeScript "da outra aula" (PENDENTE — fora deste repo):** não há TypeScript neste repositório (sem `.ts`/`package.json`). O usuário mencionou material de TS de outra aula para integrar. Falta trazer (caminho/repo, colar código, ou descrever). Hipótese: agente em TypeScript com o SDK da Anthropic (tool runner / Managed Agents) — encaixaria como "motor" de funções pesadas (ex.: o parecer) que o orquestrador n8n dispara. **A confirmar.**

---

## 7. Notas técnicas / lembretes
- Sonnet 5 usa **tokenizer novo (~30% mais tokens)** para o mesmo texto; preço promocional US$ 2/US$ 10 por MTok até 31/08/2026. Reavaliar custo/latência com tráfego real.
- Nos workflows n8n as chamadas são HTTP cru para `api.anthropic.com` (sem `temperature`, sem prompt caching configurado).
- `thinking` omitido no Sonnet 5 = adaptativo por padrão; `display` padrão `"omitted"` (blocos de thinking com texto vazio) — por isso o parser precisa achar o bloco `text`.
