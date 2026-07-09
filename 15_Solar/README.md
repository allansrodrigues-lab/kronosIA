# 15_Solar — Zênite Energia Solar (Demo Kronos)

Nicho **Energia Solar** da Kronos Intelligence — escolhido em 09/07/2026 como próximo nicho "do A ao Z"
(ticket alto, venda pontual — bom pra destravar caixa antes do nicho Contábil, que é o de recorrência eterna).
Marca 100% fictícia (padrão Bella Massa / Ferraz & Nogueira / Schalletti): **Zênite Energia Solar**, Campinas/SP.
Assistente: **Helena** (qualificação de lead + ⭐ calculadora de payback + agendamento de visita técnica).

## Por que este nicho vende (pesquisa 09/07/2026)

- **47 empresas de energia solar só em Campinas**; cidade cresceu 20% em capacidade instalada em 2025 (87,81 MW) — interior de SP é polo de geração distribuída
- Custo de sistema caiu 33% em 5 anos (R$19.800 → R$13.200 residencial); payback caiu de 5,5 para 3,5 anos — venda fica mais fácil de justificar com números
- Comprador decide rápido e fala a língua de ROI — a peça-estrela (calculadora de payback) mostra valor na hora da demo
- Lista de prospecção pronta (47 instaladoras em Campinas) — mais fácil de validar demanda local que nicho recorrente (contábil)

## Por que "Zênite" e "Helena"

- **Zênite** = ponto mais alto do sol no céu = pico de geração solar. Amarra com a métrica de "horas de sol pico" usada na calculadora. Evita clichê "sol/verde/sustentável".
- **Helena** = raiz em "Hélios" (sol, grego), sem ser óbvio demais ("Sol", "Lumi"). Segue o padrão dos nomes dos outros agentes (Aurora, Bia, Clara, Diana, Eva, Léa, Sofia). Tom: consultiva, direta em número (economia/payback), nunca vendedora agressiva.

## Estrutura

```
base_conhecimento/
  00_zenite_solar.md        — perfil da Zênite (identidade, equipe, endereço fictícios)
  01_produtos_precos.md     — tipos de sistema, faixas de preço, garantias, geração distribuída
  02_politicas.md           — visita técnica, financiamento, manutenção, LGPD, escalação
  03_tom_de_voz_helena.md   — persona Helena (consultiva, foco em ROI, sem jargão técnico)
agentes/
  00_orquestrador_solar.md          — intents (Haiku) + sessão + regras de desempate
  01_agente_atendimento_helena.md   — prompt LIVE da Helena (Sonnet 5): qualificação → calculadora → visita
  02_agente_calculadora_payback.md  — ⭐ Code node: conta de luz → kWp → economia → payback
workflows/
  workflow_orquestrador_solar_montagem.md — montagem n8n (reuso do padrão Advocacia/Imobiliária)
```

## Status (09/07/2026)

- [x] Pesquisa de mercado do nicho
- [x] Nome cravado: Zênite Energia Solar / persona Helena
- [x] Logo via Canva IA (`logo_zenite.png`) — navy + monograma "Z" com arco de nascer do sol/zênite, acento âmbar, estilo vetorial minimalista
- [x] Peça 1 — Persona + agentes (Helena, orquestrador, calculadora) — ✅ sessão Fable 09/07
- [x] Peça 2 — Arquitetura n8n + fluxo documentados (`workflows/workflow_orquestrador_solar_montagem.md`) — ✅ Fable 09/07
- [x] Peça 3 — Base de conhecimento (fase Sonnet) — ✅ 09/07
- [x] Workflows no n8n — ✅ 09/07 (3 workflows, não 4 — ver nota abaixo)
- [x] Planilha CRM própria — ✅ 09/07 "Kronos CRM — Zênite (Energia Solar)"
- [x] Chavinha `/solar` na Central de Demos — ✅ 09/07
- [x] Test harness (7 cenários S01-S07, incluindo fim-a-fim da calculadora) — ✅ 09/07, 7/7 verde
- [x] Voz (ElevenLabs) — ✅ 09/07 agente `agent_1801kx3zb2wtem6v923vgy8mwy5f`, testado por chat
- [x] Demo PNG + aba animada na landing — ✅ 09/07, `demo_solar.png` + `#seg-solar` no ar
- [x] Skill `kronos-solar` dedicada — ✅ 09/07
- [x] Deploy — ✅ 09/07, publicado em kronosintelligence.com.br (fallback SSH, CI/CD não propagou)

**Proposta comercial PDF: decisão consciente de NÃO criar.** A Imobiliária — nicho-irmão mais
recente e referência direta desta montagem — também não tem `gerar_proposta.py` próprio (só
Pizzaria, Advocacia e Parecer Científico têm, por razões históricas de prospecção). Criar um só
pra Solar quebraria a paridade entre nichos. O catálogo de serviços (`07_Recursos/gerar_catalogo_servicos.py`)
já cobre todos os nichos num documento só. Revisitar se/quando um cliente real pedir proposta formal.

**NICHO 100% COMPLETO — sem pendências técnicas conhecidas.**

## Montagem n8n — o que foi construído (09/07/2026)

**3 workflows, não 4** — decisão tomada na montagem: a visita técnica ficou embutida no
`02-agente-helena` (mesmo padrão real da Sofia/Imobiliária, que também não tem workflow
de agendamento separado — só a Bia, que tem slots pré-cadastrados, precisa disso). Reduz
superfície de erro sem perder funcionalidade.

| Workflow | ID n8n | Papel |
|---|---|---|
| `DEMO-SOLAR-01-orquestrador-zenite` | `hbDX9SmUjturOrW7` | Buffer, Haiku (8 intents), roteamento, escalação RECLAMACAO |
| `DEMO-SOLAR-02-agente-helena` | `B0ck0jtpAH0ZJs0I` | Qualificação, visita técnica, escalação, aciona calculadora |
| `DEMO-SOLAR-03-calculadora-payback` | `1CAQyhiSw2pKvdXK` | Code node determinístico + formatação Sonnet + grava `Simulacoes` |

Planilha CRM: `120rfE1JNfh0H0slWXZlvf1GVvHxn8MRoB-0NTw1S4Tk` ("Kronos CRM — Zênite").

**Bug real encontrado e corrigido no teste fim-a-fim:** o node "Atualizar Sessão c/
Simulação" (workflow 03) referenciava `$json.numero`/`$json.resultado`, mas nesse ponto
da cadeia `$json` já era a saída do node anterior (Google Sheets), sem esses campos —
gravava `jid`/`simulacao` vazios na sessão (a linha em `Simulacoes` saía certa, só a
sessão não recebia o vínculo). Corrigido para `$('Parsear Formatação').first().json...`.

**Limitação conhecida (MVP):** `CONTA_LUZ` (foto/PDF da conta) não faz OCR de verdade
ainda — a Helena pede o valor digitado quando recebe imagem sem legenda. Documentado
na base de conhecimento e no prompt live. Adicionar leitura real é trabalho futuro.

**Criação da planilha:** `create_spreadsheet` do MCP google-sheets falhou com
`storageQuotaExceeded` (mesma pegadinha de sempre — service account sem cota própria).
Contornado criando via conector do Drive (`create_file`) + Allan compartilhando com a
service account. Ver memória `mcp-n8n-sheets-setup`.
