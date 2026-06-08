# Google Sheets — Setup Completo do CRM

> Este é o banco de dados de toda a automação.
> Um arquivo Google Sheets por cliente. Cada aba tem uma função específica.

---

## Passo 1 — Criar a planilha

1. Acesse [sheets.new](https://sheets.new) (cria planilha em branco direto)
2. Renomeie para: **`CRM — [Nome da Clínica]`**
3. Copie o **ID da planilha** da URL:
   ```
   docs.google.com/spreadsheets/d/  1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms  /edit
                                    ↑ este é o ID — copie e guarde
   ```
4. Este ID vai para a variável `GOOGLE_SHEETS_CRM_ID` no n8n

---

## Passo 2 — Criar as 8 abas

Na parte inferior da tela, clique no `+` para cada aba nova.
Renomeie cada uma exatamente como abaixo (sem espaço extra, sem acento diferente).

| # | Nome da aba | Para que serve |
|---|---|---|
| 1 | `Log_Interacoes` | Log geral de todas as mensagens recebidas (Workflow 01) |
| 2 | `Sessoes_Ativas` | Histórico de conversa multi-turn (Bia + Clara) |
| 3 | `Slots_Disponiveis` | Agenda da clínica — horários disponíveis para agendamento |
| 4 | `Agendamentos` | CRM de agendamentos confirmados |
| 5 | `Log_Agendamentos` | Log de ações da Bia (criar, cancelar, remarcar) |
| 6 | `Log_Lembretes` | Log de lembretes 24h enviados |
| 7 | `Clientes` | Base de clientes (opcional no MVP — útil para histórico) |
| 8 | `Config` | Configurações da clínica (personalização por cliente) |

> **Dica:** a aba 1 que já existe ("Página1") pode ser renomeada para `Log_Interacoes`.

---

## Passo 3 — Criar as colunas de cada aba

Copie cada tabela abaixo e cole na **linha 1** da aba correspondente.
As colunas devem estar exatamente nesses nomes — os workflows leem por nome.

---

### Aba 1 — `Log_Interacoes`

Cole na linha 1, a partir da célula A1:

```
Data	Telefone	Nome	Mensagem	Intent	Resposta	Escalacao
```

| Coluna | Tipo | Exemplo |
|---|---|---|
| Data | Texto | 03/06/2026 10:32 |
| Telefone | Texto | 5511999990000 |
| Nome | Texto | Maria Silva |
| Mensagem | Texto | Quero agendar uma limpeza |
| Intent | Texto | AGENDAR |
| Resposta | Texto | Que ótimo! Já vou abrir a agenda... |
| Escalacao | Texto | NAO |

---

### Aba 2 — `Sessoes_Ativas`

```
ID	Telefone	Agente	Fase	Historico	Dado_Temp	Criado_Em	Atualizado_Em	Status
```

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID | Texto | SES-001 *(preenchido pelo workflow)* |
| Telefone | Texto | 5511999990000 |
| Agente | Texto | BIA ou CLARA |
| Fase | Texto | aguardar_resposta |
| Historico | Texto longo | `[{"role":"user","content":"..."}]` |
| Dado_Temp | Texto | `{"procedimento":"Limpeza de Pele"}` |
| Criado_Em | Texto | 03/06/2026 10:32 |
| Atualizado_Em | Texto | 03/06/2026 10:33 |
| Status | Texto | ativo ou encerrado |

> Esta aba é escrita automaticamente pelos workflows. Não precisa preencher manualmente.

---

### Aba 3 — `Slots_Disponiveis`

```
ID	Data	Hora	Profissional	Procedimento_Tipo	Status	Reservado_Para	Agendamento_ID
```

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID | Texto | S001 |
| Data | Texto | 2026-06-05 *(formato YYYY-MM-DD)* |
| Hora | Texto | 14:00 |
| Profissional | Texto | Dra. Marina |
| Procedimento_Tipo | Texto | Qualquer ou nome específico |
| Status | Texto | disponivel |
| Reservado_Para | Texto | *(vazio — preenchido ao reservar)* |
| Agendamento_ID | Texto | *(vazio — preenchido ao reservar)* |

**Preencha com os horários reais da clínica.** Exemplo de bloco semanal:

| ID | Data | Hora | Profissional | Procedimento_Tipo | Status |
|---|---|---|---|---|---|
| S001 | 2026-06-05 | 09:00 | Dra. Marina | Qualquer | disponivel |
| S002 | 2026-06-05 | 10:00 | Dra. Marina | Qualquer | disponivel |
| S003 | 2026-06-05 | 11:00 | Dra. Marina | Qualquer | disponivel |
| S004 | 2026-06-05 | 14:00 | Dra. Julia | Qualquer | disponivel |
| S005 | 2026-06-05 | 15:00 | Dra. Julia | Qualquer | disponivel |
| S006 | 2026-06-06 | 09:00 | Dra. Marina | Qualquer | disponivel |

> **"Qualquer"** em Procedimento_Tipo significa que qualquer procedimento pode ser agendado neste slot.
> Se quiser restringir (ex: Botox só com Dra. Marina), use o nome exato do procedimento.

> **Dica de gestão:** preencha os slots das próximas 2-4 semanas. Uma vez por semana, adicione novos slots.
> Futuramente isso pode ser sincronizado com o Google Calendar automaticamente.

---

### Aba 4 — `Agendamentos`

```
ID	Telefone	Nome	Procedimento	Data	Hora	Profissional	Status	Criado_Em	Observacoes	Lembrete_Enviado	Confirmado_Pelo_Cliente
```

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID | Texto | AGD-1748908800000 *(gerado pelo workflow)* |
| Telefone | Texto | 5511999990000 |
| Nome | Texto | Maria Silva |
| Procedimento | Texto | Limpeza de Pele Profunda |
| Data | Texto | 2026-06-05 |
| Hora | Texto | 14:00 |
| Profissional | Texto | Dra. Marina |
| Status | Texto | confirmado / cancelado / remarcado / no_show |
| Criado_Em | Texto | 03/06/2026 10:35 |
| Observacoes | Texto | *(opcional)* |
| Lembrete_Enviado | Texto | SIM ou *(vazio)* |
| Confirmado_Pelo_Cliente | Texto | SIM / NAO ou *(vazio)* |

---

### Aba 5 — `Log_Agendamentos`

```
Data_Hora	Telefone	Nome	Acao	Procedimento	Detalhes
```

| Coluna | Tipo | Exemplo |
|---|---|---|
| Data_Hora | Texto | 03/06/2026 10:35 |
| Telefone | Texto | 5511999990000 |
| Nome | Texto | Maria Silva |
| Acao | Texto | criar_agendamento / cancelar_agendamento |
| Procedimento | Texto | Limpeza de Pele Profunda |
| Detalhes | Texto | S001 2026-06-05 14:00 |

---

### Aba 6 — `Log_Lembretes`

```
Data_Hora	Telefone	Nome	Procedimento	Data_Agendamento	Hora_Agendamento	Status
```

| Coluna | Tipo | Exemplo |
|---|---|---|
| Data_Hora | Texto | 03/06/2026 09:00 |
| Telefone | Texto | 5511999990000 |
| Nome | Texto | Maria Silva |
| Procedimento | Texto | Limpeza de Pele Profunda |
| Data_Agendamento | Texto | 2026-06-04 |
| Hora_Agendamento | Texto | 14:00 |
| Status | Texto | enviado |

---

### Aba 7 — `Clientes` *(opcional no MVP)*

```
Telefone	Nome	Email	Data_Cadastro	Total_Agendamentos	Ultimo_Procedimento	Ultima_Visita	Observacoes
```

> Preencha manualmente ou deixe para a fase 2.
> No MVP, o nome do cliente vem direto do WhatsApp (pushName) a cada mensagem.

---

### Aba 8 — `Config` *(personalização por cliente)*

Esta aba centraliza o que muda de clínica para clínica.
Os workflows podem ler daqui no futuro — por ora é referência visual para você na hora de configurar.

Cole exatamente assim (coluna A = chave, coluna B = valor):

| A (Chave) | B (Valor) |
|---|---|
| nome_clinica | Clínica Bella Estética |
| nome_agente_recepcionista | Aurora |
| nome_agente_agendamento | Bia |
| nome_agente_atendimento | Clara |
| whatsapp_instancia | clinica |
| horario_seg_sex | 9h às 19h |
| horario_sabado | 9h às 14h |
| endereco | Av. Exemplo, 123 — Bairro, Cidade/UF |
| profissional_principal | Dra. Marina |
| avaliacao_gratuita | Sim — 30 min |
| cancelamento_politica | Gratuito até 4h antes; após isso 50% retido |
| pagamento_pix_desconto | 5% |
| pagamento_parcelamento | Até 3x sem juros |
| anthropic_model_classificador | claude-haiku-4-5-20251001 |
| anthropic_model_agentes | claude-sonnet-4-6 |

---

## Passo 4 — Fixar linha de cabeçalho

Em todas as abas:
1. Clique no número da **linha 1** (seleciona a linha toda)
2. Menu **Exibir → Congelar → 1 linha**

Isso garante que o cabeçalho fique fixo ao rolar a planilha.

---

## Passo 5 — Formatar colunas de Status (opcional mas recomendado)

Na aba `Agendamentos`, coluna `Status`:
1. Selecione a coluna H inteira
2. Menu **Dados → Validação de dados**
3. Critério: **Lista de itens**
4. Valores: `confirmado,cancelado,remarcado,no_show`

Idem para coluna `Lembrete_Enviado`:
- Valores: `SIM`

---

## Passo 6 — Compartilhar com a conta de serviço do Google (para o n8n)

O n8n acessa o Sheets via OAuth2. Para configurar:

1. No n8n → **Settings → Credentials → Add Credential**
2. Tipo: **Google Sheets OAuth2**
3. Siga o fluxo de autorização — vai pedir para logar com a conta Google que tem acesso à planilha
4. Após autorizar, o n8n terá acesso a todas as planilhas dessa conta

> **Dica:** use uma conta Google dedicada por cliente (ex: `automacao@nomedalcinica.com.br`)
> para separar os dados e facilitar a transferência se o cliente assumir a gestão no futuro.

---

## Checklist final

- [ ] Planilha criada e renomeada com o nome da clínica
- [ ] ID da planilha anotado (para `GOOGLE_SHEETS_CRM_ID`)
- [ ] 8 abas criadas com os nomes exatos
- [ ] Colunas coladas na linha 1 de cada aba
- [ ] Aba `Slots_Disponiveis` preenchida com pelo menos 10 slots (próximas 2 semanas)
- [ ] Aba `Config` preenchida com os dados da clínica
- [ ] Linha 1 congelada em todas as abas
- [ ] Credencial Google Sheets configurada no n8n

---

## O que muda para cada novo cliente

| Item | Ação |
|---|---|
| Planilha | Criar nova (duplicar esta como template) |
| `GOOGLE_SHEETS_CRM_ID` | Trocar para o ID da nova planilha |
| Aba `Config` | Preencher com dados da nova clínica |
| Aba `Slots_Disponiveis` | Preencher com a agenda real da clínica |
| Variáveis n8n | Trocar EVO_INSTANCE, EVO_BASE_URL, EVO_API_KEY |
| Prompt da Clara | Atualizar procedimentos, preços e políticas no Code node |
| Prompt da Bia | Atualizar instruções pré-procedimento no Code node |

> **Atalho:** duplique a planilha deste cliente como template para o próximo.
> No Google Drive → botão direito na planilha → "Fazer uma cópia".
> Limpe as abas de dados (Log, Sessoes, Agendamentos) e atualize a aba Config.

---

## Template de planilha pré-preenchida

Para criar um template reutilizável:

1. Configure esta planilha completa para um cliente fictício ("Clínica Demo")
2. Salve como `_TEMPLATE_CRM_Clinica`
3. A cada novo cliente: **Fazer uma cópia** → renomear → atualizar `Config` e `Slots`
4. Tempo para configurar um novo cliente: **~20 minutos**
