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

function dataRows(sheet: string[][]): string[][] {
  if (sheet.length <= 1) return [];
  return sheet.slice(1).filter((r) => r.some((c) => (c || '').trim() !== ''));
}

export function computeKpis(
  client: ClientCfg,
  log: string[][],
  bookings: string[][],
  sessions: string[][]
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

  const agendamentos = dataRows(bookings).length;
  const sessoes = dataRows(sessions).length;

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
  };
}
