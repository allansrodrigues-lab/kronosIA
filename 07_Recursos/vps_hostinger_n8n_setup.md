# Setup VPS Hostinger — n8n em Produção

> Ubuntu 22.04/24.04 + n8n + Nginx + SSL (Let's Encrypt)
> Ao final: n8n acessível em `https://n8n.seudominio.com.br` com HTTPS

---

## Antes de começar

Você precisa de:
- Acesso SSH ao VPS (IP + usuário root + senha ou chave SSH)
- Subdomínio criado apontando para o IP do VPS (ex: `n8n.seudominio.com.br`)
- O DNS do subdomínio já propagado (pode checar em [dnschecker.org](https://dnschecker.org))

---

## PARTE 1 — Acesso e preparo do servidor

### 1.1 — Conectar via SSH

No seu terminal (PowerShell ou CMD no Windows):

```bash
ssh root@IP_DO_SEU_VPS
```

Se usar chave SSH:
```bash
ssh -i caminho/para/chave.pem root@IP_DO_SEU_VPS
```

---

### 1.2 — Atualizar o sistema

```bash
apt update && apt upgrade -y
```

---

### 1.3 — Criar usuário dedicado para o n8n

```bash
adduser n8n
```

> Digite uma senha forte. Pode deixar os outros campos em branco (Enter).

Dar permissão sudo:
```bash
usermod -aG sudo n8n
```

---

### 1.4 — Configurar firewall

```bash
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
```

Confirme com `y` quando perguntar.

---

## PARTE 2 — Instalar Node.js e n8n

### 2.1 — Instalar Node.js 20 (LTS)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt install -y nodejs
```

Verificar versão:
```bash
node --version   # deve mostrar v20.x.x
npm --version    # deve mostrar 10.x.x
```

---

### 2.2 — Instalar n8n globalmente

```bash
npm install -g n8n
```

> Pode demorar 2-3 minutos.

Verificar:
```bash
n8n --version
```

---

### 2.3 — Criar pasta de dados do n8n

```bash
mkdir -p /home/n8n/.n8n
chown -R n8n:n8n /home/n8n/.n8n
```

---

## PARTE 3 — Configurar n8n como serviço (systemd)

### 3.1 — Criar o arquivo de serviço

```bash
nano /etc/systemd/system/n8n.service
```

Cole exatamente o conteúdo abaixo (substitua `SEU_SUBDOMINIO` pelo seu domínio real):

```ini
[Unit]
Description=n8n workflow automation
After=network.target

[Service]
Type=simple
User=n8n
WorkingDirectory=/home/n8n
Environment=N8N_HOST=SEU_SUBDOMINIO
Environment=N8N_PORT=5678
Environment=N8N_PROTOCOL=https
Environment=NODE_ENV=production
Environment=WEBHOOK_URL=https://SEU_SUBDOMINIO/
Environment=GENERIC_TIMEZONE=America/Sao_Paulo
Environment=N8N_LOG_LEVEL=info
Environment=N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
ExecStart=/usr/bin/n8n start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

> Salvar: **Ctrl+O → Enter → Ctrl+X**

---

### 3.2 — Ativar e iniciar o serviço

```bash
systemctl daemon-reload
systemctl enable n8n
systemctl start n8n
```

Verificar status:
```bash
systemctl status n8n
```

Deve mostrar **active (running)** em verde.

Ver logs em tempo real (opcional):
```bash
journalctl -u n8n -f
```

---

## PARTE 4 — Instalar e configurar Nginx

### 4.1 — Instalar Nginx

```bash
apt install -y nginx
```

---

### 4.2 — Criar configuração do site

```bash
nano /etc/nginx/sites-available/n8n
```

Cole o conteúdo abaixo (substitua `SEU_SUBDOMINIO` pelo domínio real):

```nginx
server {
    listen 80;
    server_name SEU_SUBDOMINIO;

    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        chunked_transfer_encoding on;
    }
}
```

> Salvar: **Ctrl+O → Enter → Ctrl+X**

---

### 4.3 — Ativar o site

```bash
ln -s /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

`nginx -t` deve mostrar: `syntax is ok` e `test is successful`

---

## PARTE 5 — SSL com Let's Encrypt (HTTPS)

### 5.1 — Instalar Certbot

```bash
apt install -y certbot python3-certbot-nginx
```

---

### 5.2 — Gerar o certificado

```bash
certbot --nginx -d SEU_SUBDOMINIO
```

Você vai responder:
1. E-mail para notificações: seu e-mail
2. Termos de serviço: `A` (agree)
3. Newsletter: `N`

O certbot vai modificar o nginx automaticamente para HTTPS.

---

### 5.3 — Verificar renovação automática

```bash
certbot renew --dry-run
```

Deve mostrar `Congratulations, all simulated renewals succeeded`.

---

## PARTE 6 — Primeiro acesso ao n8n

Abra no navegador: `https://SEU_SUBDOMINIO`

1. Você verá a tela de criação do primeiro usuário
2. Preencha:
   - Email: seu e-mail
   - Nome
   - Senha forte (guarde!)
3. Clique em **"Get started"**

---

## PARTE 7 — Configurar variáveis de ambiente no n8n

No n8n → menu lateral → **Settings → Variables**

Clique em **"Add Variable"** para cada uma:

| Nome | Valor |
|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` |
| `EVO_BASE_URL` | `https://evo.seudominio.com.br` |
| `EVO_API_KEY` | sua chave da Evolution API |
| `EVO_INSTANCE` | `clinica` (nome da instância) |
| `EVO_TEAM_NUMBER` | `5511999990000` (número da equipe para escalações) |
| `GOOGLE_SHEETS_CRM_ID` | ID da planilha (copiado no Passo 1 do setup do Sheets) |

---

## PARTE 8 — Importar os workflows

No n8n → menu lateral → **Workflows → Add Workflow → Import from File**

Importe nesta ordem:
1. `workflow_01_orquestrador.json`
2. `workflow_02_agendamento.json`
3. `workflow_03_atendimento.json`
4. `workflow_04_lembrete_24h.json`

Após importar cada um:
- Abra o workflow
- Verifique se os nodes de Google Sheets estão com a credencial configurada
- Ative o workflow (toggle verde no canto superior direito)

> **Atenção no Workflow 03:** após importar, abra o node "Chamar Bia" e selecione manualmente o workflow `02-agendamento-bia` — o JSON usa um ID de referência que precisa ser atualizado após o import.

---

## PARTE 9 — Configurar credencial Google Sheets

No n8n → **Settings → Credentials → Add Credential**

1. Busque: `Google Sheets OAuth2 API`
2. Clique em **"Sign in with Google"**
3. Autorize com a conta que tem acesso à planilha
4. Nomeie a credencial: **`Google Sheets — Clinica`**

> Este nome precisa ser exato — é o que está configurado nos nodes dos workflows.

---

## PARTE 10 — Testar tudo

### Teste do Workflow 01 (sem WhatsApp)

No terminal do seu computador (não no VPS):

```bash
curl -X POST https://SEU_SUBDOMINIO/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "TEST001"
      },
      "pushName": "Maria Teste",
      "message": { "conversation": "Quero agendar uma limpeza de pele" },
      "messageType": "conversation",
      "messageTimestamp": 1716825600
    }
  }'
```

No n8n → **Executions** → deve aparecer execução com `intent: AGENDAR`.

---

## Checklist de produção

- [ ] SSH funcionando no VPS
- [ ] Node.js 20 instalado
- [ ] n8n instalado e rodando como serviço systemd
- [ ] Nginx configurado como reverse proxy
- [ ] SSL ativo (HTTPS no subdomínio)
- [ ] n8n acessível em `https://SEU_SUBDOMINIO`
- [ ] Usuário admin criado no n8n
- [ ] 6 variáveis de ambiente configuradas
- [ ] Credencial Google Sheets configurada
- [ ] 4 workflows importados e ativos
- [ ] Teste curl retorna execução verde no n8n

---

## Comandos úteis de manutenção

```bash
# Ver status do n8n
systemctl status n8n

# Reiniciar n8n
systemctl restart n8n

# Ver logs em tempo real
journalctl -u n8n -f

# Atualizar n8n para nova versão
npm update -g n8n
systemctl restart n8n

# Ver uso de memória/CPU
htop
```

---

## Troubleshooting

| Problema | Solução |
|---|---|
| n8n não inicia | `journalctl -u n8n -f` para ver o erro |
| Nginx erro 502 | n8n não está rodando na porta 5678 — verifique `systemctl status n8n` |
| SSL não funciona | DNS ainda não propagou — aguarde até 48h ou use `dnschecker.org` |
| Webhook não recebe | Verifique se a URL do webhook está correta e o workflow está ativo |
| Erro de permissão no Sheets | Refaça o OAuth no n8n com a conta correta |
