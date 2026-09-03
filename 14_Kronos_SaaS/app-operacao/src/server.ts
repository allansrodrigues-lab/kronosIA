// Painel Kronos Operação — Agente Estoque/Fornecedores (autopeças). Porta 4700.
// Login e isolamento por cliente reaproveitados do painel de atendimento (14_Kronos_SaaS/app/src/auth.ts,
// copiado sem alteração). O que muda é a fonte de dado: SQLite por loja em vez de Google Sheets.
import express from 'express';
import * as fs from 'fs';
import * as path from 'path';
import { ClientCfg, OperacaoKpis, computeOperacaoKpis } from './estoque';
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

function resolvePaths(c: ClientCfg): ClientCfg {
  return {
    ...c,
    dbPath: path.join(ROOT, c.dbPath),
    fornecedoresPath: path.join(ROOT, c.fornecedoresPath),
  };
}

interface ClientOut {
  id: string;
  name: string;
  niche: string;
  icon: string;
  plan: string;
  monthlyFee: number;
  status: string;
  kpis: OperacaoKpis;
}

interface Overview {
  atualizadoEm: string;
  totals: { mrr: number; ativos: number; totalRuptura: number; totalCapitalParado: number } | null;
  clients: ClientOut[];
}

let cache: { at: number; data: Overview } | null = null;
const CACHE_MS = 60_000;

function buildOverview(): Overview {
  const clients: ClientOut[] = cfg.clients.map((c) => {
    const full = resolvePaths(c);
    const kpis = computeOperacaoKpis(full);
    return {
      id: c.id,
      name: c.name,
      niche: c.niche,
      icon: c.icon,
      plan: c.plan,
      monthlyFee: c.monthlyFee,
      status: c.status,
      kpis,
    };
  });

  const ativos = clients.filter((c) => c.status === 'ativo' || c.status === 'piloto');
  return {
    atualizadoEm: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
    totals: {
      mrr: ativos.reduce((s, c) => s + c.monthlyFee, 0),
      ativos: ativos.length,
      totalRuptura: clients.reduce((s, c) => s + c.kpis.ruptura.length, 0),
      totalCapitalParado: clients.reduce((s, c) => s + c.kpis.totalCapitalParado, 0),
    },
    clients,
  };
}

const app = express();
app.use(express.json());
app.use(express.static(path.join(ROOT, 'public')));

const COOKIE = 'kop_sess';
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

app.get('/api/overview', (req, res) => {
  const s = getSession(req);
  if (!s) return res.status(401).json({ error: 'não autenticado' });
  try {
    if (!cache || Date.now() - cache.at > CACHE_MS) {
      cache = { at: Date.now(), data: buildOverview() };
    }
    if (s.role === 'admin') return res.json(cache.data);
    // Cliente: só o próprio painel — sem MRR nem dado dos outros (isolamento por cliente vale na tela também).
    const mine = cache.data.clients.filter((c) => c.id === s.clientId);
    res.json({ atualizadoEm: cache.data.atualizadoEm, totals: null, clients: mine });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    res.status(500).json({ error: msg });
  }
});

app.get('/api/health', (_req, res) => res.json({ ok: true }));

const PORT = Number(process.env.PORT) || 4700;
app.listen(PORT, () => {
  console.log(`Kronos Operação painel rodando em http://localhost:${PORT}`);
});
