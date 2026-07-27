---
name: radar
description: Varredura diária de demanda — vagas remotas de IA/automação (LinkedIn, Catho, Gupy, Indeed) e projetos freelance (Workana, 99Freelas). Use quando o Allan disser "roda o radar", "tem vaga nova?", "varre as vagas", "/radar", ou na rotina diária. Devolve tabela de novidades com nota de aderência e grava em leads.md.
---

# Radar de demanda — vagas + freelance

Varredura diária em busca de (a) vagas remotas de IA/automação para o Allan e (b) projetos freelance que sirvam de bico **ou** de lead Kronos.

## Regras de navegador (obrigatórias)

Herdadas do `CLAUDE.md` — repetidas aqui porque essa skill é 100% browser:

- **Reaproveitar a aba já aberta.** Não re-navegar para URL que já está carregada.
- **Todos os sites já estão logados** (LinkedIn, Catho, Gupy, Workana, 99Freelas). Verificar a sessão existente antes de assumir que precisa de login — assumir login já fez pular o LinkedIn inteiro.
- **LinkedIn exige `geoId` explícito na URL de busca**, senão a busca volta genérica/global.
- **Workana: NÃO tentar enviar proposta enquanto o perfil estiver em moderação.** Checar a elegibilidade da conta *antes* de redigir qualquer coisa — já se queimaram sessões inteiras em retry contra paywall de moderação.
- **Screenshot travou ou timeout 2x → trocar para `get_page_text`/JS**, nunca insistir.
- Preferir `browser_batch` para sequências de interação.

## Fontes e filtros

| Fonte | O que buscar | Observação |
|---|---|---|
| LinkedIn | "automação", "n8n", "engenheiro de IA", "AI automation" — remoto | `geoId` do Brasil obrigatório na URL |
| Catho | mesmas palavras-chave, filtro home office | dropdowns às vezes só respondem a clique por coordenada |
| Gupy | vagas de IA/automação sem exigência de diploma | Allan não tem diploma — priorizar essas |
| Workana | projetos de automação/chatbot/n8n/integração | **só leitura** enquanto o perfil estiver em moderação |
| 99Freelas | idem | proposta liberada |

## Nota de aderência (0–10)

Somar: stack bate com n8n/WhatsApp/IA (+4) · remoto (+2) · não exige diploma (+2) · faixa ≥ R$5k ou projeto ≥ R$1,5k (+2). Abaixo de 6, não vale o tempo do Allan — listar mas marcar como baixa.

## Saída

Tabela única com: **Título · Fonte · Link · Faixa · Nota · Ação sugerida**.

Depois, anexar as linhas novas em `leads.md` (criar se não existir) com a data. **Só entra o que ainda não está lá** — deduplicar por link antes de gravar.

## Limites

- **Não enviar candidatura nem proposta sem o Allan mandar.** O radar prepara; ele decide o disparo.
- Campos de pretensão salarial, CPF e dados pessoais ficam **em branco** para ele preencher.
- Se uma fonte estiver bloqueada (moderação, captcha, sessão caída), registrar o motivo na saída e seguir para a próxima — não travar a rodada inteira em uma fonte.

## Relacionado

- `/kronos-prospeccao` — coleta de leads B2B para o CRM (nichos), rotina separada desta.
- Memórias: `radar-demanda-freelance-kronos`, `workana-99freelas-contas-allan` (status da moderação do perfil).
