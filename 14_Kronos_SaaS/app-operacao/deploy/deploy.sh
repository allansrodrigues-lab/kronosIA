#!/bin/bash
# Deploy do painel Kronos Operação no VPS — roda DENTRO do VPS (Browser Terminal ou SSH).
# Pré-requisito: /opt/kronos-operacao/secrets/users.json (enviado via scp do PC do Allan).
# Sobe como container Docker (node:22-alpine — precisa 22+ pro node:sqlite nativo) SEM
# expor porta ao host — fica atrás do Traefik já existente, publicado em
# https://kronosintelligence.com.br/operacao (mesmo certificado letsencrypt do site
# principal, mesma rede kronos-site_default). Mesmo padrão do painel de atendimento
# (14_Kronos_SaaS/deploy/deploy.sh) — só não precisa de sa.json porque não lê Google Sheets.
set -e

mkdir -p /opt/kronos-operacao && cd /opt/kronos-operacao

if [ ! -f secrets/users.json ]; then
  echo "ERRO: envie antes o segredo via scp:"
  echo "  /opt/kronos-operacao/secrets/users.json (usuários do painel)"
  exit 1
fi

echo ">> baixando código do GitHub..."
rm -rf repo && git clone --depth 1 https://github.com/allansrodrigues-lab/kronosIA.git repo
rm -rf app && cp -r repo/14_Kronos_SaaS/app-operacao app && rm -rf repo
cp secrets/users.json app/users.json

echo ">> instalando dependências e compilando TypeScript (dentro de container node)..."
docker run --rm -v /opt/kronos-operacao/app:/app -w /app node:22-alpine sh -c "npm ci && npx tsc"

echo ">> (re)subindo o container do painel, atrás do Traefik (sem porta exposta)..."
docker rm -f kronos-operacao 2>/dev/null || true
docker run -d --name kronos-operacao --restart unless-stopped \
  --network kronos-site_default \
  -v /opt/kronos-operacao/app:/app \
  -w /app \
  --label "traefik.enable=true" \
  --label "traefik.http.routers.kronos-operacao.rule=Host(\`kronosintelligence.com.br\`) && PathPrefix(\`/operacao\`)" \
  --label "traefik.http.routers.kronos-operacao.entrypoints=websecure" \
  --label "traefik.http.routers.kronos-operacao.tls.certresolver=letsencrypt" \
  --label "traefik.http.routers.kronos-operacao.priority=1000" \
  --label "traefik.http.routers.kronos-operacao.middlewares=kronos-operacao-strip" \
  --label "traefik.http.middlewares.kronos-operacao-strip.stripprefix.prefixes=/operacao" \
  --label "traefik.http.services.kronos-operacao.loadbalancer.server.port=4700" \
  node:22-alpine node dist/server.js

sleep 3
docker logs --tail 5 kronos-operacao
echo "DEPLOY_OPERACAO_OK — https://kronosintelligence.com.br/operacao"
