# Agente Análise de Documento — Serviço #6

## Modelo: Claude Sonnet 4.6 (claude-sonnet-4-6)

Serviço standalone de análise de PDFs/documentos enviados via WhatsApp.
Pode ser usado isolado (demo) ou integrado ao chatbot da advocacia.

---

## Prompt do Sistema (nó "Analisar Documento")

```
Analise o documento jurídico enviado e forneça um resumo estruturado.

Organize sua resposta em:

*📋 TIPO DE DOCUMENTO*
Informe: contrato, petição, sentença, notificação, escritura, procuração, etc.

*👥 PARTES ENVOLVIDAS*
Liste cada parte com nome e papel (ex: Contratante, Contratado, Autor, Réu, etc.)

*📅 DATAS E PRAZOS*
Liste TODAS as datas importantes e o que representam. Destaque prazos próximos.

*💰 VALORES*
Se houver valores financeiros, liste-os claramente.

*⚠️ PONTOS DE ATENÇÃO*
Até 5 pontos que merecem atenção especial: obrigações, penalidades, cláusulas restritivas, riscos.

*📝 RESUMO EXECUTIVO*
3 a 5 linhas explicando do que se trata o documento de forma simples.

---
⚖️ Esta é uma análise informativa automatizada. Para orientação jurídica sobre o documento, consulte um advogado.
```

---

## Fluxo técnico n8n

```
Webhook / Trigger
  → Normalizar (detectar documentMessage + mimetype=pdf)
  → Baixar PDF via Evolution API
      POST /chat/getBase64FromMediaMessage/{instance}
      Body: {"key": {messageKey}}
      Retorna: {"base64": "...", "mimetype": "application/pdf"}
  → Montar Request Claude (Code node)
      messages: [{
        role: "user",
        content: [
          {type: "document", source: {type: "base64", media_type: "application/pdf", data: base64}},
          {type: "text", text: prompt_analise}
        ]
      }]
  → HTTP Request → Anthropic API
      model: claude-sonnet-4-6
      max_tokens: 1500
  → Parsear resposta (content[0].text)
  → Enviar WhatsApp (Evolution sendText)
```

---

## Erros tratados

| Situação | Resposta |
|---|---|
| Arquivo não é PDF | "Só consigo analisar arquivos PDF. Pode enviar nesse formato?" |
| PDF muito grande (>20MB) | "Arquivo muito grande. Tente dividir em partes menores ou enviar as páginas principais." |
| PDF protegido/criptografado | "Este PDF está protegido com senha. Pode me enviar uma versão sem senha?" |
| Erro na API | "Não consegui processar o documento agora. Tente novamente em instantes." |

---

## Tempo estimado

- PDF simples (1-5 páginas): ~4-8 segundos
- PDF longo (20-50 páginas): ~15-25 segundos
- Aviso automático enviado se demorar mais de 8s: "Analisando seu documento... aguarde um momento."
