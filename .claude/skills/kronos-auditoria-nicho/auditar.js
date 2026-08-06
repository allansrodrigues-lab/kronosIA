/**
 * Auditoria das 8 familias de bug dos bots Kronos.
 * Roda DENTRO do container do n8n:
 *   cd /usr/local/lib/node_modules/n8n && NODE_PATH=... node /tmp/auditar.js [filtro]
 * O filtro opcional casa o nome do workflow (ex: "ARQ", "SOLAR").
 */
const s = require("sqlite3");
const db = new s.Database("/home/node/.n8n/database.sqlite");
const FILTRO = (process.argv[2] || "").toLowerCase();

const RX_SEGREDO = /gsk_[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}/;
const Q = String.fromCharCode(39);

const achados = [];
const nota = (fam, wf, node, msg) => achados.push({ fam, wf, node, msg });

db.all("SELECT id,name,nodes,activeVersionId FROM workflow_entity WHERE active=1", (e, ws) => {
  if (e) { console.log("ERRO SQL", e); return db.close(); }
  const alvos = ws.filter((w) => !FILTRO || w.name.toLowerCase().includes(FILTRO));
  console.log("auditando " + alvos.length + " workflows ativos" + (FILTRO ? ' (filtro: "' + FILTRO + '")' : "") + "\n");

  alvos.forEach((w) => {
    let ns;
    try { ns = JSON.parse(w.nodes); } catch (x) { return; }

    // agente conversacional = tem parser de resposta. Nos de EXTRACAO (visao/OCR) devolvem
    // um JSON pequeno e nao precisam de 1200 tokens.
    const ehAgente = ns.some((n) => /^Parsear Resposta /.test(n.name));

    ns.forEach((n) => {
      const c = (n.parameters && n.parameters.jsCode) || "";
      const todo = JSON.stringify(n.parameters || {});

      // 1 - segredo hardcoded
      if (RX_SEGREDO.test(todo)) nota(1, w.name, n.name, "SEGREDO hardcoded no no");

      // 2 - sonnet 5 sem thinking
      const temSonnet = /claude-sonnet-5/.test(c) || /claude-sonnet-5/.test(todo);
      if (temSonnet) {
        const alvo = /claude-sonnet-5/.test(c) ? c : todo;
        if (!/thinking/.test(alvo)) nota(2, w.name, n.name, "Sonnet 5 SEM thinking declarado (thinking adaptativo come o max_tokens)");
        const mt = (alvo.match(/max_tokens[^0-9]{0,4}(\d+)/) || [])[1];
        if (ehAgente && mt && Number(mt) < 1200) nota(2, w.name, n.name, "max_tokens baixo: " + mt + " (minimo 1200 em agente conversacional)");
      }

      // 3 - fallback do parser
      if (/^Parsear Resposta /.test(n.name)) {
        if (/mensagem:\s*rawText/.test(c)) nota(3, w.name, n.name, "fallback manda texto CRU ao cliente");
        else if (!/pareceJson|msgResgatada/.test(c)) nota(3, w.name, n.name, "fallback sem os 3 niveis (descarta prosa pura legitima)");
      }

      // 4 - midia mal classificada
      if (c.includes("documentMessage") && /tipoMensagem\s*=/.test(c)) {
        if (!c.includes("startsWith(" + Q + "image/")) nota(4, w.name, n.name, "imagem enviada como ARQUIVO nao e reconhecida");
      }

      // 5 - bot sem data (so quem AGENDA de verdade; "Montar Prompt Haiku" so classifica intent)
      const ehClassificador = /Haiku/i.test(n.name) || /claude-haiku/.test(c);
      if (/^Montar Prompt /.test(n.name) && !ehClassificador && /registrar_(visita|briefing|consulta)/i.test(c)) {
        if (!/DATA DE HOJE|agendaTxt/.test(c)) nota(5, w.name, n.name, "agenda: prompt NAO informa a data de hoje");
      }

      // 6 - promessa sem gatilho
      if (/^Detectar .*(Completa|Qualifica)/.test(n.name)) {
        if (!/anunciou|mensagem/i.test(c)) nota(6, w.name, n.name, "gatilho ignora o que o bot ANUNCIOU na mensagem");
      }
      if (/^Montar Prompt /.test(n.name) && /escalar_humano/.test(c) && !/nesse MESMO turno/.test(c)) {
        nota(6, w.name, n.name, "prompt sem regra ligando anuncio de encaminhamento a acao=escalar_humano");
      }

      // 7 - perfil: dado autoritativo e chave composta
      if (/^Parsear Resposta /.test(n.name) && /perfilFinal/.test(c)) {
        if (/if \(!perfilFinal\.(valor_conta|area_m2)\)/.test(c) && !/mContaLida|autoritativ/i.test(c)) {
          nota(7, w.name, n.name, "dado lido de documento NAO sobrescreve o que o cliente declarou");
        }
      }
      const dic = c.match(/([A-Z_]{3,})\[\s*(?:ctx\.)?perfil(?:Final)?\.[a-z_]+\s*\]/);
      if (dic) nota(7, w.name, n.name, "dicionario indexado por campo do perfil (" + dic[0] + ") — quebra com valor composto");

      // 8 - buffer
      if (n.name === "Aguardar Buffer") {
        const amt = Number(n.parameters.amount);
        if (!(amt >= 1.5 && amt <= 2.5)) nota(8, w.name, n.name, "buffer fora da faixa recomendada (1,5-2,5s): " + amt + "s");
      }
    });
  });

  // segredo tambem na versao publicada
  db.all("SELECT workflowId,versionId,nodes FROM workflow_history", (e2, hs) => {
    (hs || []).forEach((h) => {
      if (RX_SEGREDO.test(h.nodes || "")) nota(1, "(publicada) wf=" + h.workflowId, h.versionId, "SEGREDO na versao publicada");
    });

    const NOMES = {
      1: "segredo hardcoded", 2: "thinking do Sonnet 5", 3: "fallback do parser",
      4: "midia mal classificada", 5: "bot sem data", 6: "promessa sem gatilho",
      7: "perfil (dado autoritativo / chave composta)", 8: "buffer",
    };
    if (!achados.length) {
      console.log("nenhum achado. nicho limpo nas 8 familias.");
    } else {
      for (let f = 1; f <= 8; f++) {
        const desta = achados.filter((a) => a.fam === f);
        if (!desta.length) continue;
        console.log("\n### familia " + f + " - " + NOMES[f] + "  (" + desta.length + ")");
        desta.forEach((a) => console.log("   " + a.wf + " / " + a.node + "\n      " + a.msg));
      }
      console.log("\nTOTAL: " + achados.length + " achados");
    }
    db.close();
  });
});
