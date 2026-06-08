---
name: kronos-deploy
description: Deploy e configuração da infraestrutura Kronos Intelligence no VPS Hostinger. Use esta skill sempre que precisar: subir a landing page, configurar DNS, criar novo container Docker, configurar Traefik, adicionar novo cliente ao servidor, renovar SSL, ou qualquer tarefa de infraestrutura no VPS (IP 2.24.101.180, Ubuntu 24.04, Docker + Traefik). Também use quando o usuário mencionar "subir no servidor", "configurar domínio", "deploy", "VPS", "Hostinger", "container", "Nginx", ou "SSL".
---

# Kronos Deploy

## Contexto do servidor
- **VPS:** Hostinger KVM1 — Ubuntu 24.04, Docker + Traefik
- **IP:** 2.24.101.180
- **Usuário SSH:** root
- **Domínio principal:** kronosintelligence.com.br
- **Containers ativos:** Evolution API, n8n-xve0, Traefik
- **Arquivos da landing page:** `07_Recursos/index.html`

## Tarefas disponíveis

### 1. Deploy da landing page
1. Conectar ao VPS via SSH: `ssh root@2.24.101.180`
2. Criar diretório: `mkdir -p /opt/kronos-site`
3. Copiar `index.html` para `/opt/kronos-site/index.html`
4. Criar `docker-compose.yml` com Nginx + labels do Traefik:
```yaml
version: '3'
services:
  kronos-site:
    image: nginx:alpine
    volumes:
      - /opt/kronos-site:/usr/share/nginx/html:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.kronos.rule=Host(`kronosintelligence.com.br`)"
      - "traefik.http.routers.kronos.entrypoints=websecure"
      - "traefik.http.routers.kronos.tls.certresolver=letsencrypt"
    networks:
      - traefik_default
networks:
  traefik_default:
    external: true
```
5. Executar: `docker compose up -d`

### 2. Configurar DNS (Hostinger)
1. Acessar: hpanel.hostinger.com → Domínios → kronosintelligence.com.br → DNS
2. Adicionar registro:
   - Tipo: **A**
   - Nome: **@**
   - Valor: **2.24.101.180**
   - TTL: 3600
3. Adicionar registro www:
   - Tipo: **A**
   - Nome: **www**
   - Valor: **2.24.101.180**
4. Aguardar propagação (até 24h, normalmente 30min)

### 3. Adicionar novo cliente
1. Criar instância Evolution API para o WhatsApp do cliente
2. Criar workflow n8n dedicado (usar skill `kronos-workflow`)
3. Configurar variáveis do cliente no n8n
4. Testar fluxo completo antes de ativar

### 4. Verificar status
```bash
docker ps                          # containers ativos
docker logs kronos-site            # logs da landing page
curl -I https://kronosintelligence.com.br  # verificar SSL
```

## Divisão de responsabilidades (Kronos vs Cliente)
| Componente | Kronos controla | Cliente fornece |
|---|---|---|
| VPS + n8n | ✅ | — |
| Evolution API | ✅ | — |
| API Keys IA | ✅ | — |
| WhatsApp número | — | ✅ número deles |
| Google Calendar | — | ✅ conta deles |
| Google Sheets | — | ✅ conta deles |

## Observações importantes
- O Traefik gerencia SSL automaticamente via Let's Encrypt
- Todos os clientes rodam no mesmo VPS em containers separados
- Credenciais dos clientes ficam em variáveis de ambiente no n8n, nunca em código
- Backups: configurar snapshot semanal no painel Hostinger
