# Deploy do painel no VPS — 2 blocos pra colar

O deploy é em 2 passos porque os **segredos não estão no git** (repo público): a chave do
service account e o `users.json` vão direto do PC do Allan pro VPS via scp.

## Passo 1 — no PC do Allan (Git Bash): enviar os segredos (só na 1ª vez)

```bash
cp ~/.ssh/vps_key /tmp/vk && chmod 600 /tmp/vk
ssh -o IdentitiesOnly=yes -i /tmp/vk root@2.24.101.180 'mkdir -p /opt/kronos-painel/secrets'
scp -o IdentitiesOnly=yes -i /tmp/vk "C:/Users/Usuario/Downloads/kronos-ia-498605-3c56d6eafae9.json" root@2.24.101.180:/opt/kronos-painel/secrets/sa.json
scp -o IdentitiesOnly=yes -i /tmp/vk "C:/Users/Usuario/OneDrive/Documentos/Claude/Projects/teste Automação/14_Kronos_SaaS/app/users.json" root@2.24.101.180:/opt/kronos-painel/secrets/users.json
rm -f /tmp/vk
```

## Passo 2 — no VPS (Browser Terminal da Hostinger, ou no mesmo ssh): rodar o deploy

```bash
curl -s https://raw.githubusercontent.com/allansrodrigues-lab/kronosIA/main/14_Kronos_SaaS/deploy/deploy.sh | tr -d '\r' | bash
```
(o `tr -d '\r'` blinda contra quebra de linha do Windows, mesmo se o git escorregar)

Ao final: `DEPLOY_PAINEL_OK`. O painel fica em **http://2.24.101.180:4600** (com a tela de login).

## Atualizar depois (novas fatias)
Só repetir o **Passo 2** — ele re-clona o repo, recompila e resobe o container.
(Se mudar senha/usuário: regenerar `users.json` local e repetir o scp dele antes.)

## Notas
- ⚠️ Se `http://IP:4600` não abrir, liberar a porta 4600 no firewall do painel da Hostinger (VPS → Firewall).
- 🔒 Por enquanto é HTTP direto na porta (demo com login). Passo futuro (fatia 5): subdomínio
  `painel.kronosintelligence.com.br` + SSL via Traefik (precisa criar o DNS e conferir o nome real
  da rede Traefik com `docker network ls` — nunca assumir).
- O container roda `node:20-alpine` com o código montado em volume — sem imagem própria pra manter simples.
