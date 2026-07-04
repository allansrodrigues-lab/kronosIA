#!/bin/bash
# Deploy do painel SaaS da Kronos no VPS — roda DENTRO do VPS (Browser Terminal ou SSH).
# Pré-requisito: /opt/kronos-painel/secrets/ com sa.json e users.json (enviados via scp do PC do Allan).
# Sobe como container Docker (node:20-alpine) SEM expor porta ao host — fica atrás do
# Traefik já existente, publicado em https://kronosintelligence.com.br/painel (mesmo
# certificado letsencrypt do site principal, mesma rede kronos-site_default).
set -e

mkdir -p /opt/kronos-painel && cd /opt/kronos-painel

if [ ! -f secrets/sa.json ] || [ ! -f secrets/users.json ]; then
  echo "ERRO: envie antes os segredos via scp:"
  echo "  /opt/kronos-painel/secrets/sa.json   (chave do service account)"
  echo "  /opt/kronos-painel/secrets/users.json (usuários do painel)"
  exit 1
fi

echo ">> baixando código do GitHub..."
rm -rf repo && git clone --depth 1 https://github.com/allansrodrigues-lab/kronosIA.git repo
rm -rf app && cp -r repo/14_Kronos_SaaS/app app && rm -rf repo
cp secrets/users.json app/users.json

echo ">> instalando dependências e compilando TypeScript (dentro de container node)..."
docker run --rm -v /opt/kronos-painel/app:/app -w /app node:20-alpine sh -c "npm ci && npx tsc"

echo ">> (re)subindo o container do painel, atrás do Traefik (sem porta exposta)..."
docker rm -f kronos-painel 2>/dev/null || true
docker run -d --name kronos-painel --restart unless-stopped \
  --network kronos-site_default \
  -e KRONOS_SA_PATH=/secrets/sa.json \
  -v /opt/kronos-painel/app:/app \
  -v /opt/kronos-painel/secrets:/secrets:ro \
  -w /app \
  --label "traefik.enable=true" \
  --label "traefik.http.routers.kronos-painel.rule=Host(\`kronosintelligence.com.br\`) && PathPrefix(\`/painel\`)" \
  --label "traefik.http.routers.kronos-painel.entrypoints=websecure" \
  --label "traefik.http.routers.kronos-painel.tls.certresolver=letsencrypt" \
  --label "traefik.http.routers.kronos-painel.priority=1000" \
  --label "traefik.http.routers.kronos-painel.middlewares=kronos-painel-strip" \
  --label "traefik.http.middlewares.kronos-painel-strip.stripprefix.prefixes=/painel" \
  --label "traefik.http.services.kronos-painel.loadbalancer.server.port=4600" \
  node:20-alpine node dist/server.js

sleep 3
docker logs --tail 5 kronos-painel
echo "DEPLOY_PAINEL_OK — https://kronosintelligence.com.br/painel"
