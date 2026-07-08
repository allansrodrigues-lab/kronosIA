# Briefing — Kronos Intelligence
> Gerado em 19/06/2026. Cole este arquivo no início de uma nova conversa com o Claude para dar contexto completo do projeto.

## O que é

**Kronos Intelligence** é uma agência de automação com IA para pequenos negócios, operada solo por **Allan Rodrigues** (allansrodrigues@gmail.com). Stack única para todos os serviços: **n8n + Claude (Anthropic) + Evolution API (WhatsApp) + Google Sheets**, rodando num VPS Hostinger (2.24.101.180, Ubuntu 24.04, Docker + Traefik).

**Objetivo do Allan:** construir renda recorrente da Kronos suficiente para virar nômade digital — prioriza recorrência e operação remota sobre crescimento agressivo.

**Momento atual:** o trabalho freelancer local de Allan secou — a Kronos passou de "projeto paralelo" para única fonte de renda. Prioridade total agora é **vender**.

## Modelo de negócio: 6 serviços, mesma stack

| # | Serviço | Status |
|---|---|---|
| 1 | Chatbot de Atendimento 24h (agenda, tira dúvida, qualifica lead) | ✅ Pronto |
| 2 | Resumo de Áudio do WhatsApp (transcrição + resumo) | ✅ Pronto |
| 3 | Relatório Automático semanal (faturamento, pico, insights) | ✅ Pronto |
| 4 | Conteúdo Recorrente (posts prontos pra redes sociais) | ✅ Pronto |
| 5 | Triagem de E-mail (prioriza, resume, rascunha resposta) | ✅ Pronto |
| 6 | Leitura de Documentos/PDF (contratos, processos) | ✅ Pronto |

Princípio de arquitetura: **código faz conta, IA faz narrativa/insight** — números nunca são calculados pela IA, sempre por código determinístico.

## Nichos atendidos (segmentos da landing page)

1. **Clínicas & Consultórios** (odonto, estética) — protótipo "Aurora" (recepção) + "Bia" (agendamento) + "Clara" (atendimento) + "Diana" (pós-venda)
2. **Advocacia** — protótipo "Léa" (triagem de casos + leitura de PDF jurídico). Regra de venda: **nunca usar a palavra "chatbot"** — sempre "assistente inteligente" / "agente de IA" / "secretária digital inteligente".
3. **Empresas de Serviços** (genérico — pizzarias, salões, academias etc.) — demo "Bella Massa" (pizzaria fictícia, baseada num protótipo real que não fechou contrato)

## Planos comerciais

| Plano | Mensalidade | Implantação | Público |
|---|---|---|---|
| Essencial | R$ 397/mês | R$ 800 | Consultório individual |
| Profissional | R$ 697/mês | R$ 1.500 | Negócio com 2-5 profissionais |
| Completo | R$ 1.197/mês | R$ 2.500 | Operação completa |
| Advocacia (específico) | R$ 790/mês | R$ 1.990 | Escritórios de advocacia |

## Infraestrutura técnica

- **VPS:** Hostinger 2.24.101.180 (`srv1674538`), SSH `~/.ssh/vps_key` ou `kronos_vps`
- **n8n:** `n8n.kronosintelligence.com.br`, SQLite, MCP local conectado
- **Evolution API v2.3.7:** instância `clinica01` (chip único — "Central de Demos", troca de nicho via chavinha `/pizzaria` `/odonto` `/aurora` `/advocacia` `/conteudo` `/triagem` `/pdf` etc.)
- **LLM:** Claude Haiku (classificação de intent) + Claude Sonnet 4.6 (respostas dos agentes especialistas)
- **CRM:** Google Sheets — regra-mãe: cada CLIENTE real tem instância + planilha própria (nunca compartilhar base); CRM interno de prospecção fica na conta do Allan
- **Monitoramento:** Error Handler centralizado + Self-Healing Monitor (digest a cada 30min) em todos os workflows
- **Landing page:** `kronosintelligence.com.br` (arquivo `07_Recursos/index.html`, deploy via push GitHub + SSH no VPS)

## Status comercial (19/06/2026)

- **Landing page:** tag de conversão Google Ads instalada (aguardando IDs reais), CTA do hero vai direto pro WhatsApp, headline troca dinamicamente por grupo de anúncio (`?ag=chatbot|atendimento|agendamento`), e-mail oficial `ceo@kronosintelligence.com.br` (com encaminhamento ativo pro Gmail do Allan)
- **Google Ads:** conta suspensa, contestação enviada em 18/06, aguardando aprovação (1-3 dias úteis)
- **Banners Display:** estratégia é usar Anúncios Responsivos (Google gera os tamanhos automaticamente a partir do PNG 300×250) — não depende de Canva Pro
- **Prospecção ativa (19/06):** 52 contatos de escritórios de advocacia em Campinas (`05_Comercial/lista_advocacia_campinas.md` + aba `Prospeccao_Advocacia` no CRM) + ~130 contatos de clínicas odonto/estética (`05_Comercial/contatos_clinicas.vcf`) — disparo do dia em andamento
- **Tráfego pago:** decisão é Google Search apenas por agora (Meta/Instagram Ads e YouTube ficam pra quando a marca tiver mais tração)
- **Conteúdo próprio:** workflow `kronos-conteudo-proprio` gera posts prontos pro Instagram da Kronos — só disparo manual (schedule automático foi desativado a pedido do Allan, assim como o da Triagem de E-mail)

## Decisões estratégicas fixas (não reabrir sem motivo novo)

- **Lean:** não investir em infra paga (proxy residencial, Canva Pro, Google One, upgrades) antes de fechar o 1º cliente pagante
- **Sem mensagens automáticas não solicitadas:** nenhum workflow deve mandar WhatsApp pro Allan sem ele pedir (preferência confirmada 19/06)
- **CRM por cliente:** cada cliente fechado tem instância Evolution própria + planilha própria — nunca compartilhar
- **Identidade visual:** minimalista, navy (#020c2a), monograma "iK" — logos sempre via Canva, nunca desenhados à mão
- **Linguagem de venda advocacia:** nunca "chatbot"

## Onde encontrar mais detalhes

- `CLAUDE.md` — arquitetura técnica, troubleshooting, convenções de workflow
- `05_Comercial/` — listas de prospecção, propostas, plano de Google Ads (fora do git, gitignored)
- `12_Advocacia/`, `09_Pizzaria_SantaAna/`, `08_Clinica_Odonto/` — material por nicho
- Skills disponíveis: `/kronos-deploy`, `/kronos-workflow`, `/n8n-debug`, `/kronos-agente`, `/kronos-mcp`, `/kronos-monitor`, `/kronos-central-demos`, `/kronos-advocacia`
