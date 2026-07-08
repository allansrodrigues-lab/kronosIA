# CRM Adapter — Camada adaptadora de CRM (Schalletti / nicho Imobiliária)

> **Conceito:** o bot NUNCA fala direto com o Sheets ou com um CRM — fala com este sub-workflow.
> Trocar de CRM = trocar UMA variável de ambiente (`CRM_PROVIDER`), zero mudança nos agentes.
> É a "tomada com adaptador": o aparelho (bot) não muda, só o plugue.
> Decisão do Allan (03/07): deixar os **3 conectores pré-montados** (Vista, Jetimob, Kenlo) já no protótipo.

---

## Nome no n8n

```
[Imobiliária] - CRM Adapter (v1.0)
```

Sub-workflow chamado via **Execute Workflow** por todos os fluxos do nicho.
⚠️ Lembrete de plataforma: Execute Workflow exige o sub-workflow **publicado**.

## Contrato de entrada/saída

Entrada (JSON):
```json
{
  "operacao": "get_imoveis | upsert_lead | log_interacao | registrar_visita | atualizar_status",
  "payload": { }
}
```

| Operação | Payload | Retorno |
|---|---|---|
| `get_imoveis` | `{ finalidade, faixa_max?, regiao?, quartos? }` | lista de imóveis (formato canônico abaixo) |
| `upsert_lead` | `{ jid, nome?, finalidade?, regiao?, faixa_preco?, quartos?, extras? }` | `{ lead_id }` |
| `log_interacao` | `{ jid, mensagem, direcao, intent }` | `{ ok }` |
| `registrar_visita` | `{ jid, codigo_imovel, data, periodo, corretor? }` | `{ visita_id }` |
| `atualizar_status` | `{ jid, status }` | `{ ok }` |

**Formato canônico de imóvel** (todo conector converte para isto — os agentes só conhecem este formato):
```json
{
  "codigo": "SCH-001",
  "finalidade": "venda | locacao",
  "tipo": "apartamento | casa | studio | cobertura | comercial",
  "bairro": "Cambuí",
  "quartos": 2, "suites": 1, "vagas": 1, "area_m2": 74,
  "preco": 690000, "condominio": 850,
  "destaque": "Varanda gourmet, andar alto, sol da manhã",
  "status": "disponivel",
  "fotos": []
}
```

## Estrutura do workflow

```
Execute Workflow Trigger
   └─ Switch: {{ $env.CRM_PROVIDER || 'sheets' }}
        ├─ sheets   → nodes Google Sheets (ATIVO — protótipo/demo)
        ├─ vista    → HTTP Request Vista CRM      (pré-montado, desativado)
        ├─ jetimob  → HTTP Request Jetimob        (pré-montado, desativado)
        └─ kenlo    → HTTP Request Kenlo          (pré-montado, desativado)
              └─ Code node "Normalizar p/ formato canônico" (um por conector)
                    └─ Retorno único
```

## Variáveis de ambiente (Settings → Variables)

```
CRM_PROVIDER      = sheets | vista | jetimob | kenlo   (padrão: sheets)
VISTA_API_KEY     = (chave do cliente; sandbox grátis p/ desenvolvimento)
VISTA_BASE_URL    = http://<conta-do-cliente>-rest.vistahost.com.br
JETIMOB_TOKEN     = (token do plano do cliente com acesso à API)
KENLO_TOKEN       = (após homologação como parceiro oficial)
```

---

## Ramo 1 — `sheets` (ATIVO no protótipo)

Planilha **CRM Imobiliária Schalletti** (própria do nicho — regra-mãe: base isolada por cliente).

| Aba | Colunas |
|---|---|
| `Carteira_Imoveis` | codigo, finalidade, tipo, bairro, quartos, suites, vagas, area_m2, preco, condominio, destaque, status |
| `Leads_Imobiliaria` | jid, nome, finalidade, regiao, faixa_preco, quartos, extras, status, data_contato, ultima_interacao |
| `Sessoes_Imobiliaria` | jid, nome, finalidade, regiao, faixa_preco, quartos, extras, imoveis_enviados, imovel_interesse, status, historico, data_contato |
| `Visitas` | visita_id, jid, codigo_imovel, data, periodo, corretor, status, lembrete_enviado |
| `Log_Interacoes` | timestamp, jid, direcao, intent, mensagem |

- `get_imoveis`: ler `Carteira_Imoveis` + Code node filtra por finalidade/faixa/região/quartos e `status = disponivel`
- Demais operações: append/update nas abas correspondentes

## Ramo 2 — `vista` (pré-montado, desativado)

- **Docs:** https://www.vistasoft.com.br/api/ — REST JSON, **sandbox com chave de teste grátis** (dá pra desenvolver sem pagar)
- **Auth:** chave na query string (`?key={{ $env.VISTA_API_KEY }}`)
- `get_imoveis` → `GET {{VISTA_BASE_URL}}/imoveis/listar` com param `pesquisa` (JSON: fields + filter por categoria/valor/dormitórios) — conferir nomes exatos dos campos na doc ao ativar
- `upsert_lead` → endpoint de clientes (`/clientes/*`) — mapear jid→telefone
- Code node converte o retorno Vista → formato canônico

## Ramo 3 — `jetimob` (pré-montado, desativado)

- **Docs:** https://jetimob.docs.apiary.io/ — exige plano com acesso à API
- **Auth:** token na URL do webservice (`https://api.jetimob.com/webservice/{{ $env.JETIMOB_TOKEN }}`)
- `get_imoveis` → endpoint de imóveis do webservice; `upsert_lead` → API de leads
- Code node converte retorno → formato canônico

## Ramo 4 — `kenlo` (pré-montado, desativado)

- **Docs/acesso:** https://plataforma.kenlo.com.br/integre-conosco — ⚠️ exige **homologação como parceiro oficial** (processo de validação; iniciar quando houver cliente Kenlo no funil)
- **Auth:** token Bearer (definir na homologação)
- Até a homologação, o node fica como stub documentado (HTTP Request com URL/headers placeholder)

---

## Regras de montagem

1. Ramos vista/jetimob/kenlo ficam com os nodes **desativados** (disable) — não quebram o workflow e servem de documentação viva.
2. TODO conector termina num **Code node de normalização** → formato canônico. Os agentes nunca veem formato de CRM.
3. **Error Trigger** → Error Handler central (`X29vC9p5WB38iZFI`).
4. Fallback: se `CRM_PROVIDER` inválido ou ramo falhar → cair no ramo `sheets` + alerta no log (bot nunca fica mudo por causa de CRM fora do ar).
5. Ao ativar um conector real: preencher env vars → habilitar nodes do ramo → rodar test harness do nicho → só então trocar `CRM_PROVIDER`.

## Argumento de venda embutido 💰

"Já integramos com Vista, Jetimob e Kenlo" — os conectores pré-montados viram slide/linha de proposta.
Com o sandbox grátis da Vista, dá pra validar o conector de verdade antes do primeiro cliente, custo zero.
