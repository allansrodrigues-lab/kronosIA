# 12 — Advocacia (Demo Kronos) — Ferraz & Nogueira Advogados Associados

Nicho advocacia para a Kronos Intelligence. Escritório fictício da demo: **Ferraz & Nogueira Advogados Associados** (Campinas/SP) — mesmo padrão da Bella Massa na pizzaria.

## O que tem aqui

| Item | Descrição |
|---|---|
| `agentes/00_orquestrador_advocacia.md` | Classificação de intent + roteamento |
| `agentes/01_agente_triagem_lea.md` | Léa — atendimento, triagem de casos, agendamento |
| `agentes/02_agente_analise_pdf.md` | Serviço #6 — análise de PDF/documentos |
| `base_conhecimento/00_escritorio.md` | **Perfil do Ferraz & Nogueira** — identidade, endereço, equipe, horários |
| `base_conhecimento/01_areas_atuacao.md` | Áreas + advogado responsável por cada uma |
| `base_conhecimento/02_politicas.md` | Regras do bot (o que Léa nunca faz) |
| `base_conhecimento/03_tom_de_voz_lea.md` | Persona e tom profissional/empático |
| `workflows/` | JSONs exportados do n8n (quando pronto) |

## Workflows no n8n

| Nome | ID | Status |
|---|---|---|
| `DEMO-01-orquestrador-advocacia` | `QEawJtNsqlNGwrw0` | ✅ ATIVO — webhook `/webhook/whatsapp-advocacia-demo` |
| `DEMO-02-agente-lea` | `TZDQobW44zZwkjOB` | ✅ ATIVO — Sonnet 5, prompt Ferraz & Nogueira (02/07) |
| `kronos-analise-pdf` | `VFtnXxDmZYEf1saI` | ✅ ATIVO |

## Demo na chavinha

- **`/pdf`** (ou `/advocacia`) → troca perfil para "Análise de Documentos ⚖️"
- Qualquer PDF enviado em modo `/pdf` → vai para `kronos-analise-pdf`
- Resposta em ~8-20s dependendo do tamanho do documento

## Fluxo do Serviço #6 (Análise de PDF)

```
Cliente envia PDF no WhatsApp
  → Webhook whatsapp-pdf
  → Normalizar (detecta documentMessage)
  → É PDF? → SIM
      → Aviso "Analisando..." (para reduzir ansiedade)
      → Baixar PDF via Evolution API (getBase64FromMediaMessage)
      → Montar request com bloco document (base64, media_type=application/pdf)
      → Claude Sonnet 4.6 (max_tokens=1500)
      → Formatar análise
      → Enviar resposta WhatsApp
  → É PDF? → NÃO
      → "Só aceito PDF, pode reenviar?"
```

## Análise entregue ao cliente

1. **Tipo do documento** (contrato, petição, sentença, etc.)
2. **Partes envolvidas** (nomes + papéis)
3. **Datas e prazos** (todos, com ⚠️ para próximos)
4. **Valores financeiros**
5. **Pontos de atenção** (até 5: obrigações, penalidades, riscos)
6. **Resumo executivo** (3-5 linhas simples)
7. Rodapé: aviso de que é análise informativa, não consultoria jurídica

## Próximos passos (quando fechar cliente advocacia)

- [ ] Criar instância Evolution própria para o escritório
- [ ] Criar planilha CRM própria (aba `Triagem`)
- [ ] Montar workflow do orquestrador + Léa
- [ ] Personalizar áreas de atuação na base de conhecimento
- [ ] Testar com documentos reais do cliente
- [ ] Deploy no número de WhatsApp do escritório
