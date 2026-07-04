// Leitura do Google Sheets via service account (a mesma conta-robô que o n8n usa).
// A chave NUNCA vai pro git: o caminho vem de env var (KRONOS_SA_PATH) com um default local.
import { JWT } from 'google-auth-library';
import * as fs from 'fs';

const SA_PATH =
  process.env.KRONOS_SA_PATH ||
  'C:/Users/Usuario/Downloads/kronos-ia-498605-3c56d6eafae9.json';

let jwt: JWT | null = null;

function getClient(): JWT {
  if (!jwt) {
    const raw = JSON.parse(fs.readFileSync(SA_PATH, 'utf-8'));
    jwt = new JWT({
      email: raw.client_email,
      key: raw.private_key,
      scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
    });
  }
  return jwt;
}

export interface ValueRange {
  range: string;
  values?: string[][];
}

// Uma chamada só por planilha (batchGet) — economiza quota da API.
export async function batchGet(
  spreadsheetId: string,
  ranges: string[]
): Promise<string[][][]> {
  const client = getClient();
  const qs = ranges.map((r) => 'ranges=' + encodeURIComponent(r)).join('&');
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values:batchGet?${qs}`;
  const res = await client.request<{ valueRanges: ValueRange[] }>({ url });
  return res.data.valueRanges.map((vr) => vr.values ?? []);
}
