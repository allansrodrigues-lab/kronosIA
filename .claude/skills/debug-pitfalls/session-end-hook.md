# Hook de Captura de Pitfalls — Fim de Sessão

## O que fazer ao fim de qualquer sessão de debug

Antes de encerrar, responder mentalmente a estas perguntas. Se qualquer resposta for "sim", atualizar `debug-pitfalls/SKILL.md`:

1. **Houve um passo que "não pegou" mesmo após aplicar um fix?**
   → Novo pitfall de procedimento (ex: esqueceu restart, editou arquivo errado)

2. **Houve um erro que parecia ser X mas era Y?**
   → Novo pitfall de diagnóstico enganoso

3. **Houve uma diferença de comportamento entre ambientes** (VPS vs local, container vs host, bash vs PowerShell)?
   → Novo pitfall de ambiente

4. **Um comando que deveria funcionar falhou por uma dependência ausente?**
   → Registrar alternativa (ex: sem curl no n8n → usar Node)

## Formato para adicionar um novo pitfall

```markdown
## N. [Nome curto do pitfall]

**O que acontece:** [sintoma que levou ao diagnóstico errado]

**Detectar:**
\`\`\`bash
[comando de uma linha que confirma o problema]
\`\`\`

**Fix:** [o que fazer, em 1-3 linhas]

**Verificar:** [comando ou check que confirma que o fix funcionou]
```

## Não registrar

- Erros únicos específicos de um cliente (ex: "a planilha X tinha coluna errada")
- Problemas que já têm skill própria com cobertura completa
- Qualquer coisa que seja óbvia lendo o código
