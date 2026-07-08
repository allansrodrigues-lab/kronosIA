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

## Padrão pra novo agente de voz (qualquer nicho)
1. n8n: criar workflow webhook (Webhook `responseNode` + `onError:"continueRegularOutput"` → Respond to Webhook JSON). Ativar. Testar por curl.
2. ElevenLabs: criar agente, idioma PT-BR, voz BR (filtro sotaque), LLM Claude, system prompt do `TOM_DE_VOZ_KRONOS.md` (temperar por nicho).
3. Criar ferramenta webhook apontando pro n8n (nomes de parâmetro distintos entre corpo/consulta).
4. Publicar. Testar por voz. Verificar execução no n8n.
5. Depois: ações reais (gravar Sheets/Calendar) + número real (trial p/ portfólio; custo por minuto só com cliente pagante).
