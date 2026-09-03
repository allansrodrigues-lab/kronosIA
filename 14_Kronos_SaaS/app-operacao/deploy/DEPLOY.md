# Deploy do painel Kronos Operação no VPS — 2 blocos pra colar

O painel fica em **https://kronosintelligence.com.br/operacao** — mesmo domínio real,
mesmo certificado SSL do site principal, sem DNS novo (subcaminho roteado pelo Traefik
que já existe). Mesmo padrão do painel de atendimento (`14_Kronos_SaaS/deploy/`), só
mais simples: não lê Google Sheets, então não precisa de `sa.json`.

O deploy é em 2 passos porque `users.json` **não vai pro git** (repo público, tem hash
de senha) — vai direto do PC do Allan pro VPS via scp.

## Passo 1 — no PC do Allan (Git Bash): enviar o segredo (só na 1ª vez)

Peça pra mim (Claude) o conteúdo de `users.operacao.json` gerado nesta sessão (senhas
aleatórias de 16 caracteres, já com hash — nunca fica em texto puro em lugar nenhum do
código) e salve localmente antes de rodar:

```bash
cp ~/.ssh/vps_key /tmp/vk && chmod 600 /tmp/vk
ssh -o IdentitiesOnly=yes -i /tmp/vk root@2.24.101.180 'mkdir -p /opt/kronos-operacao/secrets'
scp -o IdentitiesOnly=yes -i /tmp/vk "CAMINHO/PRO/users.operacao.json" root@2.24.101.180:/opt/kronos-operacao/secrets/users.json
rm -f /tmp/vk
```

## Passo 2 — rodar/atualizar o deploy

⚠️ **NÃO usar `curl raw.githubusercontent.com/.../deploy.sh | bash`** — esse domínio
cacheia o arquivo por vários minutos (já causou bug no painel de atendimento). Sempre
clonar o repo e rodar o script a partir do clone:

```bash
cp ~/.ssh/vps_key /tmp/vk && chmod 600 /tmp/vk
ssh -o IdentitiesOnly=yes -i /tmp/vk root@2.24.101.180 'rm -rf /tmp/kd && git clone --depth 1 https://github.com/allansrodrigues-lab/kronosIA.git /tmp/kd && bash /tmp/kd/14_Kronos_SaaS/app-operacao/deploy/deploy.sh && rm -rf /tmp/kd'
rm -f /tmp/vk
```

Ao final: `DEPLOY_OPERACAO_OK`. Testar: **https://kronosintelligence.com.br/operacao**

## Como funciona por baixo

- Container `kronos-operacao` roda **sem porta publicada ao host** — só alcançável via
  Traefik. Entra na rede `kronos-site_default` (mesma do site principal e do painel de
  atendimento) e ganha labels dizendo "responda por
  `kronosintelligence.com.br/operacao`, reaproveite o certificado SSL, prioridade alta".
- Middleware `stripprefix` tira `/operacao` antes de mandar pro container — o app nem
  sabe que existe prefixo, serve tudo normal em `/` (por isso `<base href="/operacao/">`
  no HTML).
- Imagem é `node:22-alpine` (não `:20` como o painel de atendimento) — `node:sqlite` só
  existe a partir do Node 22.

## Atualizar depois (novas fatias, dado real de cliente)

Só repetir o **Passo 2** — re-clona o repo, recompila e resobe o container.
(Se trocar/adicionar usuário: gerar novo `users.json` e repetir o scp antes.)

## Notas

- Meu (Claude) SSH direto pra produção é bloqueado pelo classificador de segurança do
  Claude Code **na maioria das vezes** — quando isso acontecer, é só o Allan colar o
  mesmo bloco no próprio Git Bash. Essa sessão remota (nuvem) não tem `ssh`/`scp`
  instalado de jeito nenhum — os dois passos acima precisam rodar no PC/terminal local
  do Allan, não aqui.
- `data/ouro-verde.db` e `data/ouro-verde.fornecedores.json` **já vêm no repo** (dado
  fictício, sem problema estar público) — diferente do painel de atendimento, aqui só
  `users.json` é segredo.
