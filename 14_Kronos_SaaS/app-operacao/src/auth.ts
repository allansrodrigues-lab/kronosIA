// Autenticação da fatia 3 — zero dependência nova (crypto nativo do Node).
// Senha: scrypt (hash + salt). Sessão: payload assinado com HMAC num cookie HttpOnly.
// users.json fica FORA do git (repo é público); o segredo da sessão é gerado
// automaticamente no 1º boot (.secret, também gitignored).
import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';

const ROOT = path.join(__dirname, '..');
const SECRET_PATH = path.join(ROOT, '.secret');

function getSecret(): Buffer {
  if (!fs.existsSync(SECRET_PATH)) {
    fs.writeFileSync(SECRET_PATH, crypto.randomBytes(32).toString('hex'));
  }
  return Buffer.from(fs.readFileSync(SECRET_PATH, 'utf-8').trim(), 'hex');
}

export interface User {
  user: string;
  name: string;
  role: 'admin' | 'client';
  clientId?: string;
  salt: string;
  hash: string;
}

export function loadUsers(): User[] {
  const p = path.join(ROOT, 'users.json');
  if (!fs.existsSync(p)) return [];
  return JSON.parse(fs.readFileSync(p, 'utf-8')).users;
}

export function hashPassword(pass: string, salt?: string): { salt: string; hash: string } {
  const s = salt ?? crypto.randomBytes(16).toString('hex');
  const h = crypto.scryptSync(pass, s, 32).toString('hex');
  return { salt: s, hash: h };
}

export function verifyPassword(pass: string, salt: string, hash: string): boolean {
  const h = crypto.scryptSync(pass, salt, 32).toString('hex');
  return crypto.timingSafeEqual(Buffer.from(h, 'hex'), Buffer.from(hash, 'hex'));
}

export interface Session {
  u: string;
  name: string;
  role: 'admin' | 'client';
  clientId?: string;
  exp: number;
}

export function signSession(s: Session): string {
  const p = Buffer.from(JSON.stringify(s)).toString('base64url');
  const sig = crypto.createHmac('sha256', getSecret()).update(p).digest('base64url');
  return `${p}.${sig}`;
}

export function verifySessionToken(token: string | undefined): Session | null {
  if (!token) return null;
  const [p, sig] = token.split('.');
  if (!p || !sig) return null;
  const good = crypto.createHmac('sha256', getSecret()).update(p).digest('base64url');
  const a = Buffer.from(sig);
  const b = Buffer.from(good);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try {
    const s: Session = JSON.parse(Buffer.from(p, 'base64url').toString());
    if (!s.exp || s.exp < Date.now()) return null;
    return s;
  } catch {
    return null;
  }
}

export function parseCookies(header: string | undefined): Record<string, string> {
  const out: Record<string, string> = {};
  (header || '').split(';').forEach((kv) => {
    const i = kv.indexOf('=');
    if (i > 0) out[kv.slice(0, i).trim()] = decodeURIComponent(kv.slice(i + 1).trim());
  });
  return out;
}
