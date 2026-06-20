---
name: kronos-parecer-cientifico
description: Operar e customizar o serviço #7 da Kronos — Parecer Científico sob Demanda (análise científica por IA que entrega um parecer fundamentado em evidência). Use para testar o parecer, ajustar o motor/prompt, adaptar para um nicho (saúde, advocacia, nutrição), gerar a proposta, plugar /parecer na chavinha, ou evoluir do MVP (texto no WhatsApp) para o modo plus (PDF, análise de planilha, CRM). Gatilhos: "parecer científico", "análise científica", "checagem de evidência", "revisão de literatura por IA", "análise de dados", "serviço de parecer".
---

# Kronos — Parecer Científico (Serviço #7)

Análise científica por IA entregue como documento fundamentado. O cliente manda uma pergunta, recebe um parecer com resposta direta, força da evidência, método, ressalvas e fontes. É o motor de leitura de PDF da Advocacia ([[kronos-advocacia]]) ao contrário: em vez de LER o doc do cliente, a Kronos PRODUZ o doc.

Tudo operado via `mcp__n8n__*`. Construído em 20/06/2026.

## Workflow

| Item | Valor |
|---|---|
| Nome | `kronos-parecer-cientifico` |
| ID | `L7oEghqh6XA7j5RU` |
| Webhook | `/webhook/parecer-demo` (POST) |
| Status | ✅ ATIVO |
| Error handler | `X29vC9p5WB38iZFI` (padrão Kronos) |

**Cadeia:** Trigger Parecer → Config Parecer → Montar Prompt Parecer → Claude Sonnet 4.6 → Parsear Parecer → Enviar WhatsApp (clinica01).

## Como testar

```
POST /webhook/parecer-demo
{
  "pergunta": "Existe respaldo para X em Y?",
  "area": "saude e estetica",      // ou "direito trabalhista", "nutricao"...
  "tipo": "checagem de alegacao",  // | "revisao de evidencia" | "analise de dados" | "apoio academico"
  "dados": "",                      // opcional: números já apurados pelo código (IA só interpreta)
  "numero": "5519971266736"         // destino WhatsApp (default = Kronos)
}
```
Sem corpo, usa pergunta-demo de estética. Leva ~35s (Sonnet). Validado end-to-end (exec 8429, 20/06).

## O motor (regras inegociáveis)

Prompt completo em `13_Servico_AnaliseCientifica/base_conhecimento/01_motor_parecer.md`. Resumo:
- **Honestidade sobre a evidência** — diz quando é fraca; "não há evidência suficiente" é resposta válida.
- **Nunca fabrica fonte/número/estudo** — sem a citação exata, descreve o tipo de evidência.
- **Calibra confiança:** Forte | Moderada | Limitada | Inconclusiva.
- Saída com marcadores `[PERGUNTA] [RESPOSTA_DIRETA] [NIVEL_CONFIANCA] [FUNDAMENTACAO] [METODO] [RESSALVAS] [FONTES]` que o parser converte em mensagem WhatsApp (negrito `*` com 1 asterisco, `**`→`*` normalizado).
- Princípio Kronos: **código faz conta, IA faz narrativa** — análise de dados apura no código e passa só o resumo p/ a IA interpretar.

## ⚙️ MVP (entregue, funciona AGORA)

O que já roda sem nenhuma infra extra — é o que se vende no dia 1:
- Parecer em **texto formatado no WhatsApp** (pergunta entra → parecer sai).
- 4 tipos: checagem de alegação, revisão de evidência, análise de dados (colando números), apoio acadêmico.
- Operado on-demand via webhook / chavinha.
- **Adaptar a um nicho = trocar `area` e os defaults do nó Config Parecer.** Nada mais.

## ✨ Modo Plus (premium / add-on — montar ao fechar cliente)

Não construir antes de ter cliente pagando ([[feedback-lean-defer-infra-paga]]). Cada item é upsell:
- **PDF profissional** com identidade Kronos — reusar o gerador `13_Servico_AnaliseCientifica/gerar_proposta_cientifica.py` (mesmo motor visual navy+violeta) para renderizar o parecer, não só a proposta.
- **Análise de dados com planilha** — cliente manda Sheets/CSV → nó Code apura (totais, testes, deltas) + gera gráficos → IA interpreta. Plugar Google Sheets/DataTable na entrada.
- **CRM do parecer** — aba `Pareceres` (Timestamp, Cliente, Pergunta, Area, Tipo, Confianca, Status) pra histórico e cobrança por volume.
- **Plano mensal medido** — contador de pareceres no mês (staticData) p/ respeitar a cota do plano.
- **/parecer na chavinha** — plugar no roteador central (`2hYQv4sOQq5AOXmt`), padrão one-shot igual `/relatorio` e `/conteudo`: forward p/ `/webhook/parecer-demo` + perfil "Kronos · Parecer Científico 🔬". (Pendente.)

## 💰 Preço (calibrado por pesquisa de mercado 20/06)

Mercado humano: análise estatística completa de um trabalho ~R$500 (leva dias); consultoria estatística R$80–200/h. A Kronos entrega em minutos por uma fração.
- **Avulso (parecer/checagem):** R$ 197
- **Avulso (análise de dados c/ planilha):** R$ 397
- **Plano mensal:** R$ 490/mês — 8 pareceres + prioridade ← *alvo (recorrência)*
- **Implantação:** R$ 990

## Nicho-piloto

Saúde/Estética (base Aurora/Odonto já aberta — a pergunta "tenho respaldo pra oferecer isso?" aparece toda semana). 2º: Advocacia ([[kronos-advocacia]], Léa já existe). Na landing, entra no plano **Completo**.

## Armadilhas (ver [[debug-pitfalls]])

- Editou o nó e "não pegou" → conferir versão ativa; se necessário [[restart-n8n]].
- 401 no Sonnet → [[fix-n8n-auth]] (x-api-key, anthropic-version, $env não corrompido por tradução do Chrome).
- WhatsApp não chega → instância `clinica01` no ar; número-destino sem bot (nunca bot-contra-bot).
