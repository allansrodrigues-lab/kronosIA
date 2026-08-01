// Cálculo dos KPIs a partir das linhas cruas das abas do CRM.
// Colunas são achadas PELO NOME do cabeçalho (não por índice fixo) —
// aguenta variação entre nichos (Telefone vs jid, Data vs timestamp etc).

export interface ServiceCfg {
  id: string;
  label: string;
  on: boolean;
}

export interface ClientCfg {
  id: string;
  name: string;
  niche: string;
  icon: string;
  plan: string;
  monthlyFee: number;
  avgTicket: number;
  avgTicketLabel: string;
  status: string;
  spreadsheetId: string;
  tabs: Record<string, string>;
  services: ServiceCfg[];
}

export interface RecentRow {
  data: string;
  nome: string;
  mensagem: string;
}

export interface BookingRow {
  data: string;
  hora: string;
  nome: string;
  telefone: string;
  servico: string;
  status: string;
  // Detalhe do item da carteira (só quando o serviço bate com um código do catálogo,
  // ex.: SCH-006 numa aba "catalog" tipo Carteira_Imoveis). Fica vazio se não houver catálogo
  // configurado pro cliente, ou se o código não for encontrado (texto livre do bot de voz).
  finalidade: string;
  quartos: string;
  garagem: string;
  descricao: string;
}

export interface Kpis {
  atendimentos: number;
  atendimentos30d: number;
  contatosUnicos: number;
  agendamentos: number;
  sessoes: number;
  escalacoes: number;
  roiEstimado: number;
  ultimaAtividade: string;
  recentes: RecentRow[];
  proximosAgendamentos: BookingRow[];
}

function findCol(header: string[], candidates: string[]): number {
  const lower = header.map((h) => (h || '').trim().toLowerCase());
  for (const c of candidates) {
    const i = lower.indexOf(c);
    if (i >= 0) return i;
  }
  return -1;
}

// "03/07/2026, 18:38:56" (pt-BR) -> Date
function parseDate(s: string): Date | null {
  const m = (s || '').match(/(\d{2})\/(\d{2})\/(\d{4})/);
  if (!m) return null;
  const d = new Date(Number(m[3]), Number(m[2]) - 1, Number(m[1]));
  return isNaN(d.getTime()) ? null : d;
}

// Aceita "03/07/2026" (pt-BR) OU "2026-07-03" (ISO, usado em alguns nichos).
// Bots de voz às vezes gravam só "quinta-feira" ou "quinta-feira (10/07)" sem ano —
// nesse caso devolve null (linha entra no painel mesmo assim, sem filtrar por mês,
// porque é melhor mostrar um agendamento real com data incompleta do que escondê-lo).
function parseFlexibleDate(s: string): Date | null {
  const v = (s || '').trim();
  const br = v.match(/(\d{2})\/(\d{2})\/(\d{4})/);
  if (br) {
    const d = new Date(Number(br[3]), Number(br[2]) - 1, Number(br[1]));
    return isNaN(d.getTime()) ? null : d;
  }
  const iso = v.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (iso) {
    const d = new Date(Number(iso[1]), Number(iso[2]) - 1, Number(iso[3]));
    return isNaN(d.getTime()) ? null : d;
  }
  return null;
}

function dataRows(sheet: string[][]): string[][] {
  if (sheet.length <= 1) return [];
  return sheet.slice(1).filter((r) => r.some((c) => (c || '').trim() !== ''));
}

function normPhone(s: string): string {
  return (s || '').replace('@s.whatsapp.net', '').trim();
}

// Algumas abas de agendamento (ex.: Visitas da Sofia) não guardam o nome —
// só o jid. A sessão da conversa (Sessoes_*) geralmente sabe o nome de quem
// está falando. Monta telefone -> nome a partir da sessão pra preencher esse buraco.
function buildNomePorTelefone(sessions: string[][]): Map<string, string> {
  const map = new Map<string, string>();
  const header = sessions[0] ?? [];
  const iSTel = findCol(header, ['telefone', 'jid', 'contato', 'id']);
  const iSNome = findCol(header, ['nome']);
  if (iSTel < 0 || iSNome < 0) return map;
  for (const r of dataRows(sessions)) {
    const tel = normPhone(r[iSTel]);
    const nome = (r[iSNome] || '').trim();
    if (tel && nome) map.set(tel, nome);
  }
  return map;
}

interface CatalogItem {
  finalidade: string;
  quartos: string;
  garagem: string;
  descricao: string;
}

// Catálogo opcional (ex.: Carteira_Imoveis) — só existe pro nicho Imobiliária hoje.
// Cruza o código do item (SCH-006 etc.) citado no agendamento com os detalhes reais:
// finalidade (compra/aluguel), quartos, vagas de garagem, descrição/destaque.
function buildCatalogMap(catalog: string[][]): Map<string, CatalogItem> {
  const map = new Map<string, CatalogItem>();
  const header = catalog[0] ?? [];
  const iCod = findCol(header, ['codigo', 'código']);
  if (iCod < 0) return map;
  const iFin = findCol(header, ['finalidade']);
  const iQuartos = findCol(header, ['quartos']);
  const iVagas = findCol(header, ['vagas']);
  const iDestaque = findCol(header, ['destaque', 'descricao', 'descrição']);
  const iTipo = findCol(header, ['tipo']);
  const iBairro = findCol(header, ['bairro']);
  for (const r of dataRows(catalog)) {
    const cod = (r[iCod] || '').trim();
    if (!cod) continue;
    const vagas = iVagas >= 0 ? Number(r[iVagas]) || 0 : 0;
    const tipo = iTipo >= 0 ? r[iTipo] || '' : '';
    const bairro = iBairro >= 0 ? r[iBairro] || '' : '';
    map.set(cod, {
      finalidade: iFin >= 0 ? (r[iFin] || '').toLowerCase() : '',
      quartos: iQuartos >= 0 ? r[iQuartos] || '' : '',
      garagem: iVagas >= 0 ? (vagas > 0 ? `sim (${vagas})` : 'não') : '',
      descricao: [tipo, bairro].filter(Boolean).join(' · ') + (iDestaque >= 0 && r[iDestaque] ? ' — ' + r[iDestaque] : ''),
    });
  }
  return map;
}

export function computeKpis(
  client: ClientCfg,
  log: string[][],
  bookings: string[][],
  sessions: string[][],
  catalog: string[][] = []
): Kpis {
  const logHeader = log[0] ?? [];
  const rows = dataRows(log);

  const iPhone = findCol(logHeader, ['telefone', 'jid', 'contato']);
  const iDate = findCol(logHeader, ['data', 'data_hora', 'timestamp']);
  const iEsc = findCol(logHeader, ['escalacao', 'escalação']);
  const iMsg = findCol(logHeader, ['mensagem', 'resposta']);
  const iName = findCol(logHeader, ['nome']);

  const atendimentos = rows.length;

  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 30);
  let atendimentos30d = 0;
  let ultima: Date | null = null;
  const phones = new Set<string>();
  let escalacoes = 0;

  for (const r of rows) {
    if (iPhone >= 0 && r[iPhone]) phones.add(r[iPhone].trim());
    if (iEsc >= 0 && (r[iEsc] || '').trim().toUpperCase() === 'SIM') escalacoes++;
    if (iDate >= 0) {
      const d = parseDate(r[iDate]);
      if (d) {
        if (d >= cutoff) atendimentos30d++;
        if (!ultima || d > ultima) ultima = d;
      }
    }
  }

  const bookingRows = dataRows(bookings);
  const agendamentos = bookingRows.length;
  const sessoes = dataRows(sessions).length;

  const bHeader = bookings[0] ?? [];
  const iBNome = findCol(bHeader, ['nome']);
  const iBTelefone = findCol(bHeader, ['telefone', 'jid', 'contato']);
  const iBServico = findCol(bHeader, ['servico', 'serviço', 'procedimento', 'codigo_imovel', 'assunto', 'area', 'área', 'tipo']);
  const iBData = findCol(bHeader, ['data']);
  const iBHora = findCol(bHeader, ['hora', 'periodo', 'período']);
  const iBStatus = findCol(bHeader, ['status']);
  const nomePorTelefone = buildNomePorTelefone(sessions);
  const catalogMap = buildCatalogMap(catalog);

  // Histórico do MÊS CORRENTE inteiro (não só os últimos N) — cliente não precisa
  // pedir relatório por mensagem, o site já mostra tudo que caiu no mês atual.
  const agora = new Date();
  const mesAtual = agora.getMonth();
  const anoAtual = agora.getFullYear();

  const bookingRowsComData = bookingRows.map((r) => ({
    r,
    d: iBData >= 0 ? parseFlexibleDate(r[iBData]) : null,
  }));
  const doMes = bookingRowsComData.filter(
    ({ d }) => d === null || (d.getMonth() === mesAtual && d.getFullYear() === anoAtual)
  );
  // Mais recentes primeiro: com data válida ordenadas por data desc, sem data válida no fim (ordem original invertida).
  const comData = doMes.filter((x) => x.d !== null).sort((a, b) => (b.d as Date).getTime() - (a.d as Date).getTime());
  const semData = doMes.filter((x) => x.d === null).reverse();

  const proximosAgendamentos: BookingRow[] = [...comData, ...semData].map(({ r }) => {
    const telefone = iBTelefone >= 0 ? normPhone(r[iBTelefone]) : '';
    const nomeDireto = iBNome >= 0 ? (r[iBNome] || '').trim() : '';
    const servico = iBServico >= 0 ? r[iBServico] || '' : '';
    const item = catalogMap.get(servico.trim());
    return {
      data: iBData >= 0 ? r[iBData] || '' : '',
      hora: iBHora >= 0 ? r[iBHora] || '' : '',
      nome: nomeDireto || nomePorTelefone.get(telefone) || '',
      telefone,
      servico,
      status: iBStatus >= 0 ? r[iBStatus] || '' : '',
      finalidade: item ? (item.finalidade === 'locacao' ? 'aluguel' : item.finalidade === 'venda' ? 'compra' : item.finalidade) : '',
      quartos: item?.quartos || '',
      garagem: item?.garagem || '',
      descricao: item?.descricao || '',
    };
  });

  // Estimativa configurável (avgTicket em clients.json) — o painel deixa claro que é estimativa.
  const roiEstimado =
    client.monthlyFee > 0
      ? Math.round(((agendamentos * client.avgTicket) / client.monthlyFee) * 10) / 10
      : 0;

  const recentes: RecentRow[] = rows.slice(-3).reverse().map((r) => ({
    data: iDate >= 0 ? r[iDate] || '' : '',
    nome: iName >= 0 ? r[iName] || '' : '',
    mensagem: ((iMsg >= 0 ? r[iMsg] : '') || '').slice(0, 110),
  }));

  return {
    atendimentos,
    atendimentos30d,
    contatosUnicos: phones.size,
    agendamentos,
    sessoes,
    escalacoes,
    roiEstimado,
    ultimaAtividade: ultima
      ? ultima.toLocaleDateString('pt-BR')
      : 'sem registro',
    recentes,
    proximosAgendamentos,
  };
}
