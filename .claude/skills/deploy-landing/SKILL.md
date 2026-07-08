---
name: deploy-landing
description: Faz deploy da landing page Kronos (07_Recursos/index.html) pro VPS, confirma que o CI/CD propagou e verifica SSL/Traefik. Se o GitHub Action não propagar, cai no fallback manual (scp/clone+copy direto no VPS). Use quando o usuário disser "deploy da landing", "sobe o site", "publica a landing", "/deploy-landing".
---

# Deploy Landing Page

Landing (`kronosintelligence.com.br`) roda em container Nginx no VPS Hostinger (`2.24.101.180`), montado como volume a partir de `/opt/kronos-site/`, atrás do Traefik (SSL via Let's Encrypt). O caminho normal é o CI/CD (`.github/workflows/deploy.yml`, dispara em push na branch `main` quando `07_Recursos/index.html` muda) — mas ele **não propaga de forma confiável**, então todo deploy precisa terminar com verificação e, se preciso, fallback manual.

## Passo 1 — Checar se há mudança pra publicar
```bash
git status --short 07_Recursos/index.html
git log -1 --format="%H %s" -- 07_Recursos/index.html
```
Se não houver diferença entre o commit local e o que já está no ar, avisar o usuário e pular pro Passo 3 (só verificar, sem redeploy).

## Passo 2 — Deploy
1. Se houver mudança não commitada, **parar e perguntar** antes de commitar/dar push (nunca commitar automaticamente sem o usuário pedir).
2. Se já está commitado na `main`, dar `git push` já dispara o Action. Acompanhar:
```bash
gh run list --workflow=deploy.yml --limit 1
gh run watch <run-id>
```
3. Aguardar o job "Deploy no VPS" terminar (steps: scp do index.html, sync de scripts, smoke test).

## Passo 3 — Verificar se propagou de verdade
```bash
curl -sI https://kronosintelligence.com.br | grep -Ei "http|content-length|last-modified"
```
Comparar `Content-Length` com `wc -c 07_Recursos/index.html` local. Se bater, propagou. Se não bater (ou o Action falhou/ficou pendente), ir pro fallback.

## Passo 4 — Fallback manual (Action não propagou)
Usar a chave `~/.ssh/kronos_vps` (root@2.24.101.180). Rodar o clone+copy direto no servidor (evita depender do runner do GitHub):
```bash
ssh -o BatchMode=yes -o IdentitiesOnly=yes -i ~/.ssh/kronos_vps root@2.24.101.180 \
  'cd /tmp && rm -rf kdeploy && git clone --depth 1 https://github.com/allansrodrigues-lab/kronosIA.git kdeploy \
   && cp kdeploy/07_Recursos/index.html /opt/kronos-site/index.html \
   && rm -rf kdeploy && echo DEPLOY_OK'
```
Se a chave der erro de permissão (644 em vez de 600 — comum quando ela mora em pasta sincronizada), copiar pra um caminho fora de sync e ajustar antes de reusar:
```bash
cp ~/.ssh/kronos_vps /tmp/vk && chmod 600 /tmp/vk
ssh -o IdentitiesOnly=yes -i /tmp/vk root@2.24.101.180 '...'
rm -f /tmp/vk
```
Se o SSH falhar por completo, o último recurso é colar o mesmo bloco `clone+copy` no **Browser Terminal** do painel Hostinger (VPS → Browser Terminal) e pedir pro usuário confirmar execução.

Repetir o Passo 3 depois do fallback pra confirmar que pegou.

## Passo 5 — Verificar SSL/Traefik
```bash
curl -vI https://kronosintelligence.com.br 2>&1 | grep -Ei "SSL certificate|subject:|expire"
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 'docker ps --filter name=traefik --format "{{.Names}} {{.Status}}"'
```
- Certificado deve estar válido e emitido pra `kronosintelligence.com.br` (Let's Encrypt, renovação automática pelo Traefik).
- Confirmar que o container Traefik está `Up` (nome real pode variar — nunca assumir `traefik`/`web`; conferir com `docker network ls` se for mexer em rede).
- Se o certificado estiver expirado ou o Traefik down, é um problema de infra separado — não tentar corrigir dentro desse fluxo de deploy sem avisar o usuário primeiro (ação de risco maior).

## Relatar ao final
Resumir pro usuário: se o deploy foi via CI ou fallback manual, o `Content-Length`/hash confirmando propagação, e o status do SSL/Traefik. Se algo não bateu, apontar o passo exato onde travou (não adivinhar causa-raiz sem checar o estado real, ver skill `debug-pitfalls`).
