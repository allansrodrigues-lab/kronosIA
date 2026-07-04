# Deploy do painel no VPS — 2 blocos pra colar

O painel fica em **https://kronosintelligence.com.br/painel** — no domínio real, com o
mesmo certificado SSL do site principal, sem precisar de subdomínio/DNS novo (é um
subcaminho roteado pelo Traefik que já existe no VPS).

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

## Passo 2 — rodar/atualizar o deploy

⚠️ **NÃO usar `curl raw.githubusercontent.com/.../deploy.sh | bash`** — esse domínio
cacheia o arquivo por vários minutos mesmo depois de um `git push` novo (já causou 2
bugs: um CRLF e um fix de prioridade do Traefik que "não pegava"). Sempre clonar o
repo e rodar o script a partir do clone:

```bash
cp ~/.ssh/vps_key /tmp/vk && chmod 600 /tmp/vk
ssh -o IdentitiesOnly=yes -i /tmp/vk root@2.24.101.180 'rm -rf /tmp/kd && git clone --depth 1 https://github.com/allansrodrigues-lab/kronosIA.git /tmp/kd && bash /tmp/kd/14_Kronos_SaaS/deploy/deploy.sh && rm -rf /tmp/kd'
rm -f /tmp/vk
```

Ao final: `DEPLOY_PAINEL_OK`. Testar: **https://kronosintelligence.com.br/painel**

## Como funciona por baixo (pra quando precisar debugar)
- O container `kronos-painel` roda **sem porta publicada ao host** — só é alcançável
  via Traefik, que já roteia o site principal. Ele entra na mesma rede docker
  (`kronos-site_default`) e ganha labels de Traefik dizendo "responda por
  `kronosintelligence.com.br/painel`, reaproveite o certificado SSL que já existe,
  e me dê PRIORIDADE ALTA" (sem isso, o router do site principal — mais genérico —
  ganha e devolve 404).
- O middleware `stripprefix` tira o `/painel` antes de mandar pro container, então o
  app dentro dele nem sabe que existe prefixo — ele serve tudo normal em `/`.
- O front (`index.html`/`login.html`) usa `<base href="/painel/">` pra todos os links
  e chamadas de API funcionarem certo atrás desse subcaminho.

## Atualizar depois (novas fatias)
Só repetir o **Passo 2** — ele re-clona o repo, recompila e resobe o container.
(Se mudar senha/usuário: regenerar `users.json` local e repetir o scp dele antes.)

## Notas
- Meu (Claude) SSH direto pra produção é bloqueado pelo classificador de segurança do
  Claude Code **na maioria das vezes** — quando isso acontecer, é só o Allan colar o
  mesmo bloco no próprio Git Bash.
- Testar `localhost:4600` direto (sem passar pelo Traefik) vai dar tela em branco/404
  de assets — isso é esperado, porque o front assume o prefixo `/painel`. Testar
  sempre pela URL de produção, ou só a API via curl localmente.
