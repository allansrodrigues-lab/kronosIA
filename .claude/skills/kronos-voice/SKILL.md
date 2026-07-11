---
name: kronos-voice
description: >-
  Operar o Voice Agent da Kronos (ElevenLabs) e a voz dos bots. Use para criar/editar
  agente de voz conversacional (ligação), gerar TTS, plugar ferramentas (webhook) que
  o agente chama durante a conversa, escolher voz brasileira, e enviar áudio no WhatsApp
  pelo n8n. Gatilhos: "voice agent", "agente de voz", "ligação", "Aurora voz", "ElevenLabs",
  "TTS", "texto em voz", "áudio no WhatsApp", "ferramenta do agente de voz", "sotaque brasileiro".
---

# Kronos Voice — ElevenLabs + n8n

Construído em 01–02/07/2026. Serviço "Voice Agent" da Kronos em duas superfícies:
- **A) Voz no WhatsApp** — bot responde em áudio (n8n + ElevenLabs TTS + Evolution).
- **B) Ligação telefônica** — agente conversacional ao vivo (ElevenAgents), com ferramentas que chamam o n8n.

Ver também [[voice-agent-kronos]] (memória com IDs) e `TOM_DE_VOZ_KRONOS.md` (persona + casting de voz).

---

## Como o Claude opera o ElevenLabs
O painel do ElevenLabs é detalhado (como o n8n) e o formulário de ferramentas confunde. **O Allan delega essas tarefas ao Claude.** Operar via **claude-in-chrome** (a extensão do navegador dele fica conectada):
1. `list_connected_browsers` → `navigate` pra URL do agente (cria aba MCP própria; mesma sessão logada).
2. `find` (linguagem natural) pega refs; `form_input` preenche por ref (limpo, sem digitar em editor de código); `computer` clica botões/dropdowns; `browser_batch` pra encadear.
3. Preferir **form_input por ref** a digitar coordenadas. Ler estrutura com "Editar como JSON" quando precisar entender o schema.

**MCP oficial (próximo passo, ainda NÃO instalado):** existe o `elevenlabs-mcp` (pacote da ElevenLabs) que daria ferramentas de API diretas (TTS, criar agente, etc.) sem browser. Instalar quando fizer sentido — ⚠️ a chave atual está RESTRITA a Text-to-Speech + Speech-to-Text (não gerencia agentes); precisaria de chave com escopo de Conversational AI.

---

## Superfície A — TTS de voz (WhatsApp)
Workflow n8n de teste: `Kronos Voz — Teste TTS (Aurora)` (ID `GvL0m9UQ2DRMtVFg`).
Fluxo: Manual/Trigger → Set (text + voice_id) → HTTP ElevenLabs TTS → Code (áudio→base64) → HTTP Evolution `sendWhatsAppAudio`.
- **TTS:** `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128`, header `xi-api-key` (credencial n8n Header Auth `ElevenLabs (Kronos)`, ID `5FFlfR4VJIwKFg3d`), body `{text, model_id:"eleven_multilingual_v2"}`, response = File (binário `audio`).
- **Áudio → base64 (nó Code):** `getBinaryDataBuffer(i,'audio').toString('base64')` (o nó `extractFromFile` NÃO existe nessa versão do n8n; usar Code).
- **Enviar no WhatsApp (Evolution):** `POST {EVO_BASE_URL}/message/sendWhatsAppAudio/{EVO_INSTANCE}`, header `apikey`, body `{number, audio: <base64>}`.
- ⚠️ **Acento em chamada de API no Windows (curl):** mandar o corpo via ARQUIVO UTF-8 (`--data-binary @file`), nunca inline (senão `invalid_unicode`).
- ⚠️ **Rede do Allan sem IPv6:** curl com `-4`; Node com `--dns-result-order=ipv4first`.

## Superfície B — Agente de voz (ligação)
Agente `Aurora - Kronos` (`agent_1501kwfqpeszfkhr9wj4h0bn0xk9`). Config: idioma Português (Brasil), LLM **Claude Sonnet** (o mais novo; built-in, não pede chave), voz **Carla** (BR — ⚠️ sotaque vem da VOZ, filtrar Idioma Portuguese + Sotaque Brasileiro; voz britânica fala "de Portugal"), system prompt = persona do `TOM_DE_VOZ_KRONOS.md`.
- Testar por voz: painel de teste (esfera azul + ícone 📞) OU "Pré-visualização". O "Novo chat / Pergunte qualquer coisa" e "Construa com o Architect" é o assistente de build, NÃO a Aurora.

### Ferramentas do agente (dar "mãos") — chama o n8n
Ferramenta webhook `agendar_avaliacao` → `POST https://n8n.kronosintelligence.com.br/webhook/aurora-agendar` (workflow n8n `DHXZHNTOQdjOwMJz`, ATIVO, lê body OU query).
⚠️ **Armadilhas do formulário de ferramenta (queimaram tempo):**
1. "Parâmetros do corpo" SEMPRE força 1 propriedade + a descrição do objeto — se vazia → "Property description cannot be empty". Só tem modo JSON / URL, não dá pra desligar.
2. **NÃO repetir o mesmo nome de parâmetro na consulta E no corpo** → "Falha ao criar ferramenta". Usar nomes distintos (ex: corpo=`nome`, consulta=`dia`+`horario`).
3. Schema (Editar como JSON): `api_schema.query_params_schema` (array) + `api_schema.request_body_schema.properties` (array de `{id,type:"string",description,value_type:"llm_prompt",required,enum:null}`).
4. Publicar depois de criar (botão Publicar → Revisar alterações → Publicar).

---

⚠️ **Estado sujo TAMBÉM no diálogo de criação do agente (11/07, Marina):** o campo "Nome do Agente" do fluxo "Agente em Branco" veio pré-preenchido com o nome do ÚLTIMO agente criado ("Vera - Cedro Saúde"). Regra: **Ctrl+A antes de digitar em QUALQUER campo do ElevenLabs**, mesmo em fluxo "novo". Já o modal da 1ª ferramenta de um agente novo veio limpo — o bug entre ferramentas é do MESMO agente.

💡 **Pegar voice_id TTS de uma voz salva (pro nó `Responder em Voz` do nicho):** Vozes → Minhas Vozes → ⋮ da voz → "Copiar ID de voz" → `Get-Clipboard` no PowerShell. A voz escolhida no AGENTE não vale como voice_id do TTS — configs separadas; sempre atualizar o nó do workflow com o id copiado (Marina/Amanda Kelly = `oi8rgjIfLgJRsQ6rbZh3`).

💡 **Colar prompt longo por clipboard funciona (11/07):** em vez de `type` (timeout CDP), `Set-Clipboard` no PowerShell + clicar no campo + Ctrl+A + Ctrl+V — 2.000 chars entraram instantâneo, sem timeout.

## Padrão pra novo agente de voz (qualquer nicho) — receita v2 (validada 08/07 com Sofia e Léa; re-validada 11/07 com Marina)
1. **n8n:** criar workflow webhook (Webhook `responseNode` + `onError:"continueRegularOutput"` → Respond to Webhook JSON; settings `errorWorkflow: X29vC9p5WB38iZFI`). Ativar. Testar por curl (`-4` na rede do Allan).
2. **ElevenLabs (via claude-in-chrome):** `/app/agents/new` → "Agente em Branco" → nome. Na aba Agente:
   - **Prompt do sistema:** é DIV contenteditable (form_input FALHA) → clicar + Ctrl+A + `type`. ⚠️ Texto longo dá timeout CDP 30s **mas entra completo** — NÃO repetir; conferir por screenshot.
   - **Primeira mensagem:** mesmo método (curta, sem timeout).
   - **Idioma:** existe "Português (Brasil)" com bandeira BR — usar esse.
   - **Voz:** aba "Minhas Vozes" já tem as BR salvas: Carla (Aurora), Ana Alice (Sofia), Elena Vinter (Léa), Roberta (livre). Sem precisar filtrar no Explorar.
   - **LLM:** Claude Sonnet mais novo da lista (08/07 = Sonnet 4.6; painel já manda "não envie temperatura").
3. **Ferramenta webhook — criar pelo modo "Editar como JSON" + clipboard (NUNCA digitar JSON nem usar o formulário):**
   - Montar o JSON num arquivo UTF-8 → `Get-Content -Raw -Encoding UTF8 arq.json | Set-Clipboard` → no editor JSON: clicar, Ctrl+A, Ctrl+V (colar não dispara auto-close de brackets; digitar corrompe).
   - Schema: template do modal + `name`, `description`, `api_schema.url`, `method: "POST"`, `query_params_schema` (array) e `request_body_schema` ({id:"body", type:"object", description, properties: [...]}).
   - ⚠️ **TODO parâmetro (query, body-objeto e cada property) exige** `"value_type": "llm_prompt"`, `"dynamic_variable": ""`, `"constant_value": ""`, `"required": true`, `"enum": null` — faltar `dynamic_variable` dá `invalid_type`.
   - Continua valendo: nomes distintos entre corpo e consulta (padrão: body=`nome`+específico do nicho; query=`dia`+`horario`).
   - ⚠️ **Formulário visual (alternativa ao JSON) FUNCIONA, mas tem bug de estado sujo entre ferramentas (09/07):** ao criar a 2ª+ ferramenta webhook no mesmo agente ("Adicionar ferramenta" → "Adicionar ferramenta webhook"), o modal reabre **pré-preenchido com os dados da ferramenta anterior** — e qualquer texto novo digitado nos campos Nome/Descrição/URL entra CONCATENADO ao texto antigo (ex: campo Nome virou `"calcular_paybackagendar_visita_tecnica"`), e as propriedades do corpo já vêm com o identificador antigo (`contaMensal` sobrevivendo quando eu queria `nome`). **Sempre**, ao abrir o modal pra uma nova ferramenta, clicar em cada campo (Nome, Descrição, URL, cada propriedade) e dar **Ctrl+A antes de digitar** — nunca assumir campo vazio, mesmo em formulário "novo". Rolar a tela toda e conferir propriedade por propriedade antes de salvar.
4. Publicar (Publicar → diff "Revisar alterações" → Publicar; botão fica cinza = publicado). Testar por voz (painel de teste). Verificar execução no n8n.
5. Depois: ações reais (gravar Sheets/Calendar) + número real (trial p/ portfólio; custo por minuto só com cliente pagante).

### Agentes existentes (Superfície B)
| Agente | ID | Voz | Ferramenta → webhook n8n |
|---|---|---|---|
| Aurora - Kronos | `agent_1501kwfqpeszfkhr9wj4h0bn0xk9` | Carla | `agendar_avaliacao` → `/webhook/aurora-agendar` (`DHXZHNTOQdjOwMJz`) |
| Sofia - Schalletti | `agent_6101kx1kmf3dfs9bkxzpx2rn6a5x` | Ana Alice | `agendar_visita` → `/webhook/sofia-visita` (`VLvrdcMi4NxKUMSK`) |
| Léa - Ferraz & Nogueira | `agent_1901kx1mrywjer3rx653s0y6aa3t` | Elena Vinter | `agendar_consulta` → `/webhook/lea-consulta` (`OaalbpYTvNdypGiP`) |
| Helena - Zênite Solar | `agent_1801kx3zb2wtem6v923vgy8mwy5f` | Roberta | `calcular_payback` → `/webhook/helena-payback` (`5IrRDmb7ViJOyPhU`) + `agendar_visita_tecnica` → `/webhook/helena-visita` (`l6mcqTExEPS9eZGJ`) — 1º agente com 2 ferramentas (calcular + agendar), confirma que dá pra plugar mais de uma sem problema além do bug de estado sujo acima |
| Vera - Cedro Saúde | `agent_4901kx6pg7rmf94aysjhz7yd0jqa` | Luna (nova, BR — soft/calm/soothing) | `agendar_consulta` → `/webhook/vera-consulta` (`Ucn2jpnVQqJkWwQm`) — LGPD como portão de entrada no próprio prompt de voz; testado ponta a ponta (chat simulado → n8n → planilha Consultas) 10/07 |
| Marina - Estúdio Traço | `agent_9701kx8jhnz1fvrtegsajhn8cegr` | Amanda Kelly (BR — sweet/warm/clear; TTS `oi8rgjIfLgJRsQ6rbZh3`) | `agendar_briefing` → `/webhook/marina-briefing` (`Vg23r2dgGs3utjEV`) — prompt de voz só cita R$/m², NUNCA multiplica (número calculado não sai do LLM); testado E2E 11/07 |
