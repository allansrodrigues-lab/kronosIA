# Kronos — Runbook de Onboarding de Cliente

Tempo estimado: **30–45 min** para o primeiro cliente, **15–20 min** a partir do segundo.

---

## Pré-requisitos (verificar antes de começar)

- [ ] Contrato/proposta assinados
- [ ] Número WhatsApp do cliente em mãos (será deslogado do app pessoal)
- [ ] Acesso ao Google Sheets do cliente (ou criar planilha nova)
- [ ] SSH no VPS: `ssh -i ~/.ssh/kronos_vps root@2.24.101.180`
- [ ] Proxy residencial ativo (se VPS tiver o IP bloqueado pelo WA) — ver nota abaixo

> **Sobre proxy:** O IP do datacenter Hostinger é bloqueado pelo WhatsApp no momento de vincular o QR. Solução: comprar proxy residencial estático (~US$2–5/mês em IPRoyal ou Proxy-Cheap) e configurar na instância Evolution **antes** de escanear o QR. Após vincular, o proxy pode ser removido — a sessão fica ativa pelo VPS normalmente.

---

## Passo 1 — Criar a planilha CRM do cliente

1. Abrir o Google Sheets **na conta do cliente** (não na conta da Kronos)
2. Duplicar o template: `1ZlDFYkgx6aXUM0ayj1e1_K6uX0cruo7VuCcmg1_w5ps`
   - Arquivo → Fazer uma cópia → nomear `CRM - [Nome do Cliente]`
3. Anotar o ID da nova planilha (parte da URL: `docs.google.com/spreadsheets/d/**ID**/`)
4. Compartilhar com a conta de serviço Google usada pelo n8n (verificar credencial no n8n)

---

## Passo 2 — Preencher o arquivo de config

Copiar `07_Recursos/config_template.json`, renomear para `[slug].json` e preencher:

```json
{
  "slug":         "clinica02",
  "nome":         "Clínica Dra. Carla Estética",
  "nicho":        "estetica",
  "persona_nome": "Ana",
  "numero_wa":    "5519999999999",
  "sheets_id":    "1ABC...",
  "webhook_path": "clinica02-wa"
}
```

Regras do slug:
- Lowercase, sem espaços, sem acento
- Único — não pode existir outro cliente com o mesmo slug
- Exemplos: `clinica02`, `dra_carla`, `odonto_campinas`

---

## Passo 3 — Rodar o pipeline de onboarding

```bash
# 1. Copiar config para o VPS
scp -i ~/.ssh/kronos_vps clinica02.json root@2.24.101.180:/docker/

# 2. Dry-run primeiro (simula sem alterar nada)
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "python3 /docker/onboard-cliente.py /docker/clinica02.json --dry-run"

# 3. Se dry-run OK, rodar de verdade
ssh -i ~/.ssh/kronos_vps root@2.24.101.180 \
  "python3 /docker/onboard-cliente.py /docker/clinica02.json"
```

O script faz automaticamente:
- ✅ Cria instância Evolution API (`slug`)
- ✅ Clona os workflows n8n para o cliente (com nome `slug-*`)
- ✅ Corrige referências de sub-workflow no orquestrador
- ✅ Configura webhook Evolution → n8n
- ✅ Ativa todos os workflows
- ✅ Smoke test (POST de teste no webhook)
- ✅ Relatório final com IDs e próximos passos

---

## Passo 4 — Vincular o WhatsApp

> ⚠️ Fazer isso COM o cliente presente (ou com acesso ao WhatsApp dele)

```bash
# No VPS — gera QR code em base64
curl -H "apikey: kronos-evo-key-2024" \
  http://localhost:8080/instance/connect/clinica02
```

Copiar o campo `qrcode.base64`, abrir num conversor base64→PNG e escanear com o WhatsApp do cliente.

**Se der erro de IP bloqueado:**
1. Configurar proxy residencial na instância Evolution
2. Retentar o connect
3. Após vincular, remover o proxy

---

## Passo 5 — Configurar o Google Calendar (para agendamento)

1. No n8n: abrir o workflow `clinica02-02-agendamento-bia` (ou equivalente)
2. Localizar o nó Google Calendar → trocar credencial para a conta do cliente
3. Verificar o Calendar ID (normalmente o e-mail do cliente)
4. Salvar e republicar o workflow

---

## Passo 6 — Personalizar o agente (se necessário)

Se o cliente precisar de nome de agente diferente (`Ana`, `Bia`, `Léa`):
1. Abrir o workflow `clinica02-01-orquestrador-*`
2. Localizar o nó `Montar Prompt Haiku` → editar o nome da agente no prompt
3. Fazer o mesmo nos sub-workflows de agendamento/atendimento
4. Publicar (Ctrl+S → Publish) — reinício do container não é necessário para mudanças de prompt

---

## Passo 7 — Teste final ao vivo

Usar o número da Kronos (5519971266736) para testar:

```
Enviar: "Quero agendar uma consulta"
Esperado: saudação da agente + pergunta de nome/data
```

> ⚠️ Nunca testar número-com-bot contra número-com-bot (causa loop de mensagens).

Cenários mínimos a testar:
- [ ] "Quero agendar" → Bia assume o fluxo de agendamento
- [ ] "Qual o preço?" → Clara responde com valores
- [ ] "Quero reclamar" → escala para equipe humana
- [ ] Mensagem picada em 2 partes → bot agrupa e responde uma vez só

---

## Passo 8 — Registrar no CRM de prospecção

1. Abrir Google Sheets → aba `Prospeccao`
2. Atualizar o status do cliente para `ONBOARDED`
3. Registrar: data de onboarding, slug, workflow IDs, número WA, sheets_id

---

## Checklist de entrega ao cliente

- [ ] Bot respondendo no WhatsApp
- [ ] Agendamentos criando eventos no Google Calendar
- [ ] Planilha CRM registrando atendimentos
- [ ] Lembrete D-1 configurado e testado
- [ ] Cliente sabe que o número vai ficar "logado" no bot (não no app pessoal)
- [ ] Acesso ao painel de monitoramento compartilhado (opcional)

---

## Troubleshooting rápido

| Sintoma | Verificar |
|---|---|
| Bot não responde | Evolution conectado? `GET /instance/connectionState/slug` |
| Resposta dupla | Buffering ativo no orquestrador? Delay configurado? |
| Erro 401 Anthropic | `$env.ANTHROPIC_API_KEY` resolvendo? Auto-tradução do Chrome? |
| Agendamento não cria evento | Credencial Google Calendar atualizada? Calendar ID correto? |
| Workflow inativo | n8n → abrir workflow → botão verde (Active) ligado? |

---

## Referências

- Script de onboarding: `07_Recursos/onboard-cliente.py`
- Config template: `07_Recursos/config_template.json`
- Test harness: `ssh root@VPS "python3 /docker/test-harness/run_tests.py"`
- Error handler n8n: `X29vC9p5WB38iZFI`
- Monitor: `ADmfpDIilh48WwV3` (digest a cada 30min no WhatsApp)
