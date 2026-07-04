// Painel SaaS da Kronos — fatia 2: servidor que lê os KPIs reais do CRM (Google Sheets)
// e serve o painel (visão cliente + visão Kronos). Porta 4600.
import express from 'express';
import * as fs from 'fs';
import * as path from 'path';
import { batchGet } from './sheets';
import { ClientCfg, Kpis, computeKpis } from './kpis';
import {
  Session,
  loadUsers,
  parseCookies,
  signSession,
  verifyPassword,
  verifySessionToken,
} from './auth';

const ROOT = path.join(__dirname, '..');
const cfg: { clients: ClientCfg[] } = JSON.parse(
  fs.readFileSync(path.join(ROOT, 'clients.json'), 'utf-8')
);

// Largura de leitura por tipo de aba (Sessoes tem histórico gigante na col E — não buscar).
const RANGE_BY_KIND: Record<string, string> = {
  log: 'A1:G5000',
  bookings: 'A1:H5000',
  sessions: 'A1:D5000',
  leads: 'A1:H5000',
};

interface ClientOut {
  id: string;
  name: string;
  niche: string;
  icon: string;
  plan: string;
  monthlyFee: number;
  avgTicketLabel: string;
  status: string;
  services: ClientCfg['services'];
  kpis: Kpis;
}

interface Overview {
  atualizadoEm: string;
  totals: {
    mrr: number;
    ativos: number;
    suspensos: number;
    atendimentos30d: number;
    agendamentos: number;
  };
  clients: ClientOut[];
}

let cache: { at: number; data: Overview } | null = null;
const CACHE_MS = 60_000;

async function buildOverview(): Promise<Overview> {
  // Agrupa por planilha → 1 batchGet por spreadsheet (metade das chamadas, os 2 primeiros clientes dividem o mesmo CRM).
  const bySheet = new Map<string, { client: ClientCfg; kinds: string[] }[]>();
  for (const c of cfg.clients) {
    const kinds = Object.keys(c.tabs).filter((k) => RANGE_BY_KIND[k]);
    const list = bySheet.get(c.spreadsheetId) ?? [];
    list.push({ client: c, kinds });
    bySheet.set(c.spreadsheetId, list);
  }

  const dataByClient = new Map<string, Record<string, string[][]>>();
  for (const [sid, entries] of bySheet) {
    const ranges: string[] = [];
    const owners: { clientId: string; kind: string }[] = [];
    for (const e of entries) {
      for (const kind of e.kinds) {
        ranges.push(`${e.client.tabs[kind]}!${RANGE_BY_KIND[kind]}`);
        owners.push({ clientId: e.client.id, kind });
      }
    }
    const results = await batchGet(sid, ranges);
    results.forEach((values, i) => {
      const o = owners[i];
      const bag = dataByClient.get(o.clientId) ?? {};
      bag[o.kind] = values;
      dataByClient.set(o.clientId, bag);
    });
  }

  const clients: ClientOut[] = cfg.clients.map((c) => {
    const bag = dataByClient.get(c.id) ?? {};
    const kpis = computeKpis(c, bag.log ?? [], bag.bookings ?? [], bag.sessions ?? []);
    return {
      id: c.id,
      name: c.name,
      niche: c.niche,
      icon: c.icon,
      plan: c.plan,
      monthlyFee: c.monthlyFee,
      avgTicketLabel: c.avgTicketLabel,
      status: c.status,
      services: c.services,
      kpis,
    };
  });

  const ativos = clients.filter((c) => c.status === 'ativo');
  return {
    atualizadoEm: new Date().toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    }),
    totals: {
      mrr: ativos.reduce((s, c) => s + c.monthlyFee, 0),
      ativos: ativos.length,
      suspensos: clients.filter((c) => c.status === 'suspenso').length,
      atendimentos30d: clients.reduce((s, c) => s + c.kpis.atendimentos30d, 0),
      agendamentos: clients.reduce((s, c) => s + c.kpis.agendamentos, 0),
    },
    clients,
  };
}

const app = express();
app.use(express.json());
app.use(express.static(path.join(ROOT, 'public')));

const COOKIE = 'ksess';
const SESSION_MS = 7 * 24 * 60 * 60 * 1000; // 7 dias

function getSession(req: express.Request): Session | null {
  return verifySessionToken(parseCookies(req.headers.cookie)[COOKIE]);
}

app.post('/api/login', (req, res) => {
  const { user, pass } = (req.body ?? {}) as { user?: string; pass?: string };
  const u = loadUsers().find((x) => x.user === (user || '').trim().toLowerCase());
  if (!u || !pass || !verifyPassword(pass, u.salt, u.hash)) {
    return res.status(401).json({ error: 'Usuário ou senha inválidos' });
  }
  const sess: Session = {
    u: u.user,
    name: u.name,
    role: u.role,
    clientId: u.clientId,
    exp: Date.now() + SESSION_MS,
  };
  res.setHeader(
    'Set-Cookie',
    `${COOKIE}=${signSession(sess)}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${SESSION_MS / 1000}`
  );
  res.json({ ok: true, role: u.role, name: u.name });
});

app.post('/api/logout', (_req, res) => {
  res.setHeader('Set-Cookie', `${COOKIE}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0`);
  res.json({ ok: true });
});

app.get('/api/me', (req, res) => {
  const s = getSession(req);
  if (!s) return res.status(401).json({ error: 'não autenticado' });
  res.json({ user: s.u, name: s.name, role: s.role, clientId: s.clientId });
});

app.get('/api/overview', async (req, res) => {
  const s = getSession(req);
  if (!s) return res.status(401).json({ error: 'não autenticado' });
  try {
    if (!cache || Date.now() - cache.at > CACHE_MS) {
      cache = { at: Date.now(), data: await buildOverview() };
    }
    if (s.role === 'admin') return res.json(cache.data);
    // Cliente: só o próprio painel — sem MRR nem lista dos outros (base blindada por cliente).
    const mine = cache.data.clients.filter((c) => c.id === s.clientId);
    res.json({ atualizadoEm: cache.data.atualizadoEm, totals: null, clients: mine });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    res.status(500).json({ error: msg });
  }
});

app.get('/api/health', (_req, res) => res.json({ ok: true }));

const PORT = Number(process.env.PORT) || 4600;
app.listen(PORT, () => {
  console.log(`Kronos SaaS painel rodando em http://localhost:${PORT}`);
});
