// Cálculo dos KPIs do Agente Estoque/Fornecedores a partir do SQLite da loja.
// Porta pra TypeScript a mesma lógica validada em 20_AutoPecas/mvp/agente_estoque.py
// (rodado e conferido manualmente antes desse painel existir).
import { DatabaseSync } from 'node:sqlite';
import * as fs from 'fs';

export interface ClientCfg {
  id: string;
  name: string;
  niche: string;
  icon: string;
  plan: string;
  monthlyFee: number;
  status: string;
  dbPath: string;
  fornecedoresPath: string;
  diasCapitalParado: number;
}

export interface Produto {
  id: number;
  nome: string;
  categoria: string;
  sku: string;
  quantidade_atual: number;
  estoque_minimo: number;
  preco_custo: number;
  preco_venda: number;
  ultima_venda: string;
  fornecedor_principal: string;
}

export interface FornecedorOpcao {
  tipo: 'principal' | 'alternativo';
  fornecedor: string;
  preco: number;
  prazo_dias: number;
  categoria_peca: string;
}

export interface RupturaItem extends Produto {
  fornecedores: FornecedorOpcao[];
}

export interface ParadoItem extends Produto {
  dias_parado: number;
  valor_parado: number;
}

export interface OperacaoKpis {
  totalProdutos: number;
  ruptura: RupturaItem[];
  parados: ParadoItem[];
  totalCapitalParado: number;
  atualizadoEm: string;
}

function carregarProdutos(dbPath: string): Produto[] {
  const db = new DatabaseSync(dbPath, { readOnly: true });
  try {
    const rows = db.prepare('SELECT * FROM produtos').all() as unknown as Produto[];
    return rows;
  } finally {
    db.close();
  }
}

function diasEntre(iso: string): number {
  const ultima = new Date(iso + 'T00:00:00');
  const hoje = new Date();
  const ms = hoje.getTime() - ultima.getTime();
  return Math.floor(ms / (1000 * 60 * 60 * 24));
}

export function computeOperacaoKpis(client: ClientCfg): OperacaoKpis {
  const produtos = carregarProdutos(client.dbPath);
  const catalogo: Record<string, FornecedorOpcao[]> = fs.existsSync(client.fornecedoresPath)
    ? JSON.parse(fs.readFileSync(client.fornecedoresPath, 'utf-8'))
    : {};

  const ruptura: RupturaItem[] = produtos
    .filter((p) => p.quantidade_atual <= p.estoque_minimo)
    .map((p) => ({ ...p, fornecedores: catalogo[p.sku] ?? [] }));

  const parados: ParadoItem[] = produtos
    .filter((p) => p.quantidade_atual > 0 && diasEntre(p.ultima_venda) >= client.diasCapitalParado)
    .map((p) => {
      const dias_parado = diasEntre(p.ultima_venda);
      return { ...p, dias_parado, valor_parado: p.quantidade_atual * p.preco_custo };
    });

  return {
    totalProdutos: produtos.length,
    ruptura,
    parados,
    totalCapitalParado: parados.reduce((s, p) => s + p.valor_parado, 0),
    atualizadoEm: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
  };
}
