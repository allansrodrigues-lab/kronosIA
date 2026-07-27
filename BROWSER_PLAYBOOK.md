# BROWSER_PLAYBOOK.md

Procedimento operacional padrão para qualquer tarefa de navegador no projeto Kronos.

**Por que existe:** automação de navegador é a ferramenta mais usada aqui e a maior fonte de
retrabalho. Cada regra abaixo veio de uma falha real registrada na memória do projeto — não de
boa prática genérica. Quem seguir isto não repete o erro que já custou sessão.

Carregar antes de qualquer tarefa de navegador. O subagente `web-operator` já segue este arquivo.

---

## 1. As quatro regras de ouro

### 1.1 Reaproveitar a aba aberta — nunca re-navegar

Antes de qualquer `navigate`, rodar `tabs_context` e ver se a URL já está aberta. Se estiver,
usar o `tabId` existente.

Re-navegar para `web.whatsapp.com` derruba a sessão e força reconexão lenta; já custou uma
mensagem reenviada. Vale para qualquer site com sessão pesada (WhatsApp, LinkedIn, Canva).

Exceção única: a página está comprovadamente em estado quebrado (erro fatal, DOM vazio).

### 1.2 Verificar login antes de assumir que precisa de login

Nunca concluir "esse site pede autenticação" a partir da URL ou de memória. Abrir a aba e ler
a página. LinkedIn, Catho, Gupy, Workana, 99Freelas, Casa dos Dados e WhatsApp Web **já estão
logados** no Chrome do Allan.

Presumir login derrubou uma varredura inteira do LinkedIn, que teve de ser refeita.

### 1.3 Salvar valores de formulário em disco ANTES de submeter

Antes de clicar em salvar/enviar num formulário que teve dado digitado, gravar os campos num
JSON de rascunho:

```
<scratchpad>/form_<site>_<AAAAMMDD-HHMM>.json
{"url": "...", "campos": {"valor": "1.800,00", "descricao": "..."}, "salvo_em": "..."}
```

Um reload já apagou proposta preenchida à mão. Com o JSON, um reload custa um repreenchimento
automático em vez de reescrever tudo.

**Corolário:** NUNCA recarregar ou sair de página onde o Allan digitou algo sem confirmar com
ele antes.

### 1.4 Screenshot travou → cair para texto, não repetir

`Page.captureScreenshot timed out` (30s de CDP) acontece de forma esporádica.

- **Primeira falha:** repetir só a *captura* — não a ação anterior. O front-end quase sempre já
  aplicou a mudança; foi a captura que falhou.
- **Segunda falha:** parar de tentar screenshot. Usar `get_page_text` ou `read_page`.
- `zoom` às vezes devolve **conteúdo obsoleto sem erro nenhum**. Se o recorte não bate com o que
  deveria estar ali, não confiar: tirar screenshot cheio para recalibrar.

Regra geral: screenshot é para quando o *layout em si* importa. Para verificar conteúdo,
`get_page_text` é mais rápido e nunca trava.

---

## 2. Modos de falha catalogados

### 2.1 Clique e seleção

| Sintoma | Procedimento |
|---|---|
| Clique por coordenada erra o alvo (seleciona texto errado) | Clicar por `ref` do `read_page`, nunca por coordenada quando houver `ref`. Reler a página logo antes do clique importante — refs envelhecem. |
| Botão "Salvar" clicado e nada acontece | Confirmar com `read_network_requests` se saiu PUT/POST real. A UI não dá feedback de erro quando o clique não registra. |
| Lista/dropdown não aparece no `find` nem no `read_page` | São `<li>` sem role ARIA. Usar `javascript_tool` → `document.querySelectorAll('li')`, achar por texto exato, `scrollIntoView({block:'center'})`, aí clicar. |
| Campo de busca não abre sugestão | Pode haver dois campos equivalentes na página. No Workana, o do topo ("Selecione suas 3 habilidades") é morto; o da seção "Habilidades" mais abaixo funciona. Procurar o segundo campo antes de declarar quebrado. |

### 2.2 Entrada de texto

| Sintoma | Procedimento |
|---|---|
| JSON digitado em editor de código sai corrompido | **Nunca** `type` em CodeMirror/Monaco — o auto-fechamento de brackets corrompe. Montar em arquivo UTF-8 → `Get-Content -Raw -Encoding UTF8 arq \| Set-Clipboard` → clicar, Ctrl+A, Ctrl+V. |
| `form_input` falha com "Element type DIV is not a supported form input" | É `contenteditable`. Clicar + Ctrl+A + `type`. |
| `type` longo (~1500+ chars) dá timeout de CDP | **O texto entrou completo.** NÃO repetir — repetir duplica. Dar `wait` e conferir. |
| Campo monetário BRL vira valor absurdo (R$500.018,00) | A máscara reprocessa dígito a dígito. Usar o native setter: `HTMLInputElement.prototype.value` + `dispatchEvent(new Event('input',{bubbles:true}))` com o valor já formatado. |
| `input[type=date]` resiste à digitação | Setar via JS com valor ISO + dispatch de `input`/`change`. |

### 2.3 Arquivos e navegação

| Sintoma | Procedimento |
|---|---|
| Upload de foto/arquivo | **Não é possível** pelas ferramentas disponíveis — `file_upload` só aceita anexos da própria sessão, rejeita OneDrive e pasta do projeto. Deixar o arquivo em pasta fácil e passar o caminho completo para o Allan subir. |
| `navigate` com `file://` | Ele prefixa `https://`. Não dá para abrir arquivo local no Chrome; usar `Read` para mostrar imagem no chat. |
| Reddit / Twitter-X | Bloqueados pela política do Browser pane. Não insistir, não é bug. |

### 2.4 Muros de plataforma (checar ANTES de produzir trabalho)

| Plataforma | Verificação obrigatória primeiro |
|---|---|
| **Workana** | Perfil em moderação manual? Se sim, envio de proposta está bloqueado — **não redigir proposta ainda**. Já se queimou sessão em retry contra o paywall. Existe upsell de revisão expressa (BRL 59,90) — **nunca pagar sem autorização**. Cuidado: e-mail "bem-vindo" ≠ perfil aprovado. |
| **LinkedIn** | URL de busca precisa de `geoId` explícito, senão volta genérica/global. Modal "Disponível para" trava com renderer freeze — pedir ao Allan 1 clique em vez de insistir. |
| **Casa dos Dados** | "Pesquisar" é grátis; **"Gerar Arquivo" gasta crédito pago** (1 linha = 1 crédito, restam ~50). Preencher "Total de Linhas" para limitar gasto. **Nunca exportar sem o Allan autorizar.** |
| **WhatsApp Web** | Status do CRM não é confiável sozinho. Confirmar contato limpo abrindo `https://wa.me/<E.164>` → "Continuar para o WhatsApp Web": chat vazio = limpo; com histórico = pular; alerta "não está no WhatsApp" = número inválido. |

---

## 3. Regras de segurança que o navegador não relaxa

- **Nunca disparar mensagem** de número não declarado liberado pelo Allan. Varredura é leitura;
  envio é ação separada que exige confirmação explícita dele.
- **Nunca clicar em ação irreversível** (enviar, publicar, excluir, pagar, exportar pago) sem
  confirmação na conversa.
- **Deixar em branco** campos de pretensão salarial, CPF, dados bancários e documentos pessoais
  — são do Allan.
- **Nunca criar conta** nem digitar senha.

---

## 4. Determinismo e observabilidade

- **Nunca calcular data/dia da semana de cabeça.** Rodar `date +%A`. Uma rodada de prospecção
  travou por errar o dia, viu lista vazia e desistiu em 8 segundos sem log.
- **Toda rodada longa grava checkpoint** conforme avança, para que um travamento seja
  diagnosticável depois em vez de sumir em silêncio.
- **Toda tarefa termina com resultado estruturado** (seção 5) — inclusive quando falha.

---

## 5. Formato de resultado obrigatório

Toda operação de navegador reporta assim, uma entrada por ação:

```json
{
  "action": "o que foi tentado, em uma frase",
  "status": "sucesso | falha | bloqueado | parcial",
  "evidence": "prova concreta — string lida da página, requisição vista, contagem, URL final",
  "blocker_reason": "null quando status=sucesso; caso contrário a causa real"
}
```

Regras do campo `evidence`: precisa ser algo **lido de volta** depois da ação, não a intenção da
ação. "Cliquei em salvar" não é evidência. "PUT /profile/description → 200" é. "Página recarregada
mostra 'R$ 1.800,00'" é.

`status: "bloqueado"` é resultado legítimo e final — muro de plataforma não é falha da automação
e não deve virar loop de retry.
