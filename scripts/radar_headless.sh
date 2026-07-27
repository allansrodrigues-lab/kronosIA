#!/usr/bin/env bash
#
# Radar de demanda em modo headless.
#
# Por que existe: a varredura diária de vagas/freelas é um pipeline determinístico
# com formato de saída fixo — não precisa queimar uma sessão interativa. Aqui ela
# roda via `claude -p`, grava tudo em leads.md e só chama o Allan se achar algo
# realmente bom (acima do limiar).
#
# Uso:
#   bash scripts/radar_headless.sh              # rodada normal
#   bash scripts/radar_headless.sh --dry-run    # mostra o que faria, sem gravar nem notificar
#   NOTA_MINIMA=8 bash scripts/radar_headless.sh
#
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEADS="$RAIZ/leads.md"
SAIDA_BRUTA="$(mktemp)"
trap 'rm -f "$SAIDA_BRUTA"' EXIT

# Nota de aderência mínima para valer um ping. Abaixo disso entra no leads.md
# silenciosamente e o Allan lê quando quiser.
NOTA_MINIMA="${NOTA_MINIMA:-7}"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

PROMPT=$(cat <<'FIM'
Rode a varredura diária do radar de demanda (skill /radar).

Fontes: LinkedIn, Catho, Gupy, Workana, 99Freelas.
Alvo: vagas remotas de IA/automação e projetos freelance de automação/chatbot/n8n.

REGRAS:
- Reaproveitar a aba já aberta; todos os sites já estão logados. Não re-navegar.
- LinkedIn exige geoId explícito na URL de busca.
- Workana: só leitura enquanto o perfil estiver em moderação. Não tentar enviar proposta.
- Verificação por get_page_text, não por screenshot. Se travar uma vez, trocar de abordagem.
- NÃO enviar candidatura nem proposta. Só levantar e pontuar.

Nota de aderência 0-10: stack bate com n8n/WhatsApp/IA (+4), remoto (+2),
não exige diploma (+2), faixa >= R$5k ou projeto >= R$1.5k (+2).

SAÍDA: uma linha por achado, exatamente neste formato pipe-delimitado, nada mais:
NOTA|TITULO|FONTE|LINK|FAIXA

Sem cabeçalho, sem markdown, sem comentário. Se não houver nada novo, não imprima nada.
FIM
)

echo "[radar] iniciando varredura ($(date '+%Y-%m-%d %H:%M'))" >&2

claude -p "$PROMPT" \
  --allowedTools "mcp__claude-in-chrome__navigate" \
                 "mcp__claude-in-chrome__get_page_text" \
                 "mcp__claude-in-chrome__read_page" \
                 "mcp__claude-in-chrome__find" \
                 "mcp__claude-in-chrome__browser_batch" \
                 "mcp__claude-in-chrome__tabs_context_mcp" \
                 "Write" \
  > "$SAIDA_BRUTA" 2>/dev/null || {
    echo "[radar] claude -p falhou; nada gravado" >&2
    exit 1
  }

# Fica só com linhas no formato esperado (NOTA|...), descartando qualquer
# prosa que o modelo tenha deixado escapar.
ACHADOS="$(grep -E '^[0-9]{1,2}\|' "$SAIDA_BRUTA" || true)"

if [ -z "$ACHADOS" ]; then
  echo "[radar] nenhum achado novo hoje." >&2
  exit 0
fi

TOTAL=$(printf '%s\n' "$ACHADOS" | wc -l | tr -d ' ')

# Deduplica pelo link contra o que já está no leads.md.
NOVOS=""
while IFS= read -r linha; do
  link=$(printf '%s' "$linha" | cut -d'|' -f4)
  if [ -f "$LEADS" ] && grep -qF "$link" "$LEADS"; then
    continue
  fi
  NOVOS="${NOVOS}${linha}"$'\n'
done <<< "$ACHADOS"

NOVOS=$(printf '%s' "$NOVOS" | sed '/^$/d')

if [ -z "$NOVOS" ]; then
  echo "[radar] $TOTAL achados, todos já registrados. Nada novo." >&2
  exit 0
fi

QTD_NOVOS=$(printf '%s\n' "$NOVOS" | wc -l | tr -d ' ')

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[radar] --dry-run: $QTD_NOVOS novos (nada gravado)" >&2
  printf '%s\n' "$NOVOS"
  exit 0
fi

# Grava tudo — inclusive o que está abaixo do limiar.
{
  echo ""
  echo "## $(date '+%Y-%m-%d')"
  echo ""
  echo "| Nota | Título | Fonte | Link | Faixa |"
  echo "|---|---|---|---|---|"
  printf '%s\n' "$NOVOS" | while IFS='|' read -r nota titulo fonte link faixa; do
    echo "| $nota | $titulo | $fonte | $link | $faixa |"
  done
} >> "$LEADS"

echo "[radar] $QTD_NOVOS novos gravados em leads.md" >&2

# Notifica só o que passa do limiar.
BONS=$(printf '%s\n' "$NOVOS" | awk -F'|' -v min="$NOTA_MINIMA" '$1 >= min')

if [ -z "$BONS" ]; then
  echo "[radar] nada acima de $NOTA_MINIMA — sem notificação." >&2
  exit 0
fi

QTD_BONS=$(printf '%s\n' "$BONS" | wc -l | tr -d ' ')
echo ""
echo "🎯 $QTD_BONS oportunidade(s) com nota >= $NOTA_MINIMA:"
echo ""
printf '%s\n' "$BONS" | while IFS='|' read -r nota titulo fonte link faixa; do
  echo "  [$nota] $titulo ($fonte) — $faixa"
  echo "        $link"
done
