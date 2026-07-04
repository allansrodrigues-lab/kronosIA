#!/bin/bash
# Deploy do painel SaaS da Kronos no VPS — roda DENTRO do VPS (Browser Terminal ou SSH).
# Pré-requisito: /opt/kronos-painel/secrets/ com sa.json e users.json (enviados via scp do PC do Allan).
# Roda como container Docker (node:20-alpine), porta 4600, sem depender do Traefik.
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

echo ">> (re)subindo o container do painel..."
docker rm -f kronos-painel 2>/dev/null || true
docker run -d --name kronos-painel --restart unless-stopped \
  -p 4600:4600 \
  -e KRONOS_SA_PATH=/secrets/sa.json \
  -v /opt/kronos-painel/app:/app \
  -v /opt/kronos-painel/secrets:/secrets:ro \
  -w /app \
  node:20-alpine node dist/server.js

sleep 3
docker logs --tail 5 kronos-painel
echo "DEPLOY_PAINEL_OK — acesse http://SEU_IP:4600"
