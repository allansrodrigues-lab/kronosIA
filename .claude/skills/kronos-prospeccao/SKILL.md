---
name: kronos-prospeccao
description: Coleta diária de dados de prospecção da Kronos — levanta contatos reais (clínicas, advocacia, parecer científico) por região de SP via pesquisa web, classifica porte (renomado/pequeno) e status de contato, e lança no CRM (Google Sheets). Use sempre que o Allan disser "bora prospectar", "coletar dados", "próximos contatos", "levanta mais X", "mais Y de tal cidade/nicho", "atualiza o mapa", ou quando for hora da rotina diária de coleta. NÃO dispara mensagem — só prepara o CRM pro Allan disparar no WhatsApp e salvar no chip.
---

# Coleta de dados de prospecção (Kronos)

Operação **orgânica, região por região**, 3 nichos juntos todo dia (decisão Allan 20/06/2026).
Rotina **DIÁRIA** — token só queima em prospecção/conversa até entrar cliente, então pode usar à vontade aqui; o Allan acompanha "como vai ficando". Ver memórias [[operacao-prospeccao-organica]], [[material-prospeccao-demos]], [[proximos-passos]].

⚠️ **Regra de ouro: contato REAL, nunca inventado.** Todo nome/telefone/e-mail vem de pesquisa web verificável. Se não achou contato, lança o nome com status "Sem contato (buscar)" — não chuta número.

⚙️ **Regra de operação (Allan 12/07/2026): varredura → lança DIRETO, sem perguntar onde.** Toda vez que fizer a varredura (busca web OU processar uma base CNPJ que o Allan fornecer), já atualiza o CRM na hora — contatos na aba do nicho + mensagem na aba `Mensagens` (se for nicho ainda sem mensagem lá). **Não** parar pra perguntar layout, estrutura ou "onde jogar" — a estrutura abaixo já está decidida e é definitiva. Perguntar só escopo quando ambíguo (qual nicho/região/quantos), nunca a arrumação. Objetivo: o Allan não procurar nem reconfirmar nada — abre a aba do nicho → contato; abre `Mensagens` → texto.

## CRM (Google Sheets via MCP `mcp__google-sheets__*`)
Spreadsheet: `1ZlDFYkgx6aXUM0ayj1e1_K6uX0cruo7VuCcmg1_w5ps`

| Nicho | Aba | Início dos dados |
|---|---|---|
| Clínicas (odonto/estética/dermato) | `Prospeccao` | linha 3 (nota na linha 1; header na linha 2) |
| Parecer Científico | `Prospeccao_Parecer` | linha 2 (header na linha 1; nota em N1) |
| Advocacia | `Prospeccao_Advocacia` | linha 2 (header na linha 1; nota em N1) |
| Imobiliária | `Prospeccao_Imobiliaria` | linha 3 (nota na linha 1; header na linha 2) |
| Energia Solar | `Prospeccao_Solar` | linha 3 (nota na linha 1; header na linha 2) |
| Arquitetura | `Prospeccao_Arquitetura` | linha 3 (nota na linha 1; header na linha 2) |
| Clínica Médica | `Prospeccao_Clinica_Medica` | linha 3 (nota na linha 1; header na linha 2) |

**Aba `Mensagens`** (central única, criada 12/07): mensagem de abordagem WhatsApp + e-mail de TODOS os 7 nichos + Universal. Colunas `Nicho | Persona/Bot | Canal | Assunto (e-mail) | Mensagem | Observacoes`. É de lá que sai o texto pra disparar — a nota no topo de cada aba de nicho aponta pra ela. Nicho novo sem mensagem lá → escrever no mesmo tom antes de abordar.

**Colunas (12):** `Nome | Cidade | Segmento/Especialidade | WhatsApp | Email | Endereco | Teste_WhatsApp | Status | Data_Abordagem | Data_Followup | Proposta_Enviada | Observacoes`

**Convenção da coluna `Observacoes`** (sempre preencher):
`Porte: Renomada/Pequena · Contato: confirmado / checar antes / Sem contato (buscar)`
- **Renomada** = rede/franquia, "& Associados", múltiplos sócios, full service, e-mail institucional. **Pequena** = profissional solo/consultório.
- **confirmado** = tem WhatsApp celular (9 dígitos). **checar antes** = só fixo, ou número não confirmado como WhatsApp. **Sem contato** = nome levantado, contato a buscar.
- `Status` padrão de linha nova = `Novo`.

## Públicos por nicho
- **Clínicas:** odontológicas (implante/orto), estética/harmonização, dermatologia. Renomados = OdontoCompany, Sorridents, DentalKids, Royal Face, Botoclinic, Damaface, clínicas tradicionais.
- **Parecer Científico** (serviço de nicho — quem decide/recomenda por base técnica): nutricionistas, nutrólogos, dermato/tricologia, endocrino, medicina ortomolecular/longevidade/integrativa, medicina do esporte, fisio esportiva. NÃO ofertar pra comércio/varejo. Ver [[servico-parecer-cientifico]].
- **Advocacia:** escritórios da região. Em Campinas rende mais pequeno/médio (renomados de verdade = bancas de SP, Onda 2). Ver [[advocacia-kronos]].

## Método (eficiente em tokens)
1. **Buscas de LISTA, não 1 por contato.** Query que expõe contato: `<nicho> <cidade> <bairro> whatsapp telefone "(19) 9"`. Cada busca rende ~5-6 nomes. Varia bairros (Cambuí, Centro, Taquaral, Barão Geraldo, Nova Campinas, Castelo) e subnichos pra não repetir resultados.
2. **Antes de lançar, conferir duplicata** na aba (`get_sheet_data` ou `find_in_spreadsheet`).
3. **Lançar em lote** com `batch_update_cells` (range explícito, ex: `A33:L42`) — mais barato que add_rows um a um.
4. **Gargalo conhecido:** WhatsApp sai fácil, **e-mail é o difícil**. Padrão validado 21/06: **advocacia/profissional com site institucional rende WhatsApp + e-mail juntos** (buscar `<nome> <cidade> whatsapp telefone contato <dominio>`); **clínica pequena/consultório quase nunca publica e-mail** (só WhatsApp/Instagram) — não gastar busca caçando e-mail deles, o canal é WhatsApp (que já serve ao chip/tráfego pago). E-mail de clínica só vale a pena nos renomados/médicos com site.
5. **Meta por região:** 50 por nicho = 25 renomados + 25 pequenos. Aceitar desvio quando a realidade da cidade não permite (ex.: Campinas advocacia deu 18/34) — registrar, não forçar/inventar.

## Base CNPJ que o Allan fornece (método rápido — Onda 2 em diante)
O Allan pode entregar uma planilha "empresas" exportada da **base CNPJ da Receita** (ex: `1IhJdDojRpAdPt6hjFfwK7sYlG1WlEb6-FWFaf350FxA`), já filtrada por região/bairro, com CNPJ, Razão/Fantasia, Telefones, E-mail, endereço e **CNAE**. Fluxo: **ler → classificar por CNAE → distribuir nas abas + jogar direto no CRM** (sem perguntar). Mapa CNAE → nicho:
- `6911701` Serviços advocatícios → `Prospeccao_Advocacia`
- `8630504` Atividade odontológica → `Prospeccao` (clínicas)
- `8630501/8630502/8630503` Atividade médica ambulatorial → `Prospeccao_Clinica_Medica` (cirurgia plástica/estética = ticket alto)
- `7111100` Serviços de arquitetura → `Prospeccao_Arquitetura`
- `6821801/6822600/6810201` imóveis → `Prospeccao_Imobiliaria`
- Descartar fora de nicho: elétrica (`4321500`), geração de energia, limpeza, laboratório de outra praça, holdings patrimoniais, linhas com dados mascarados (`XXXX`).

⚠️ **Armadilha da base CNPJ:** telefone/e-mail costuma ser do **contador que abriu a empresa**, não do negócio. Sinais: e-mail com `contabil`/`conta`/`societario`/`admjudicial`/Contabilizei, ou DDD de outro estado que não bate com a praça. Nesses casos, marcar `Contato: checar antes (contato do contador)` — nunca "confirmado". Telefone `999999999`/`988888888` = placeholder → WhatsApp vazio + "checar antes". Guardar o CNPJ na `Observacoes`. Telefone celular = 9 dígitos começando com 9 (o fixo tem 8). Ver [[dados-publicos-prospeccao-nicho]].

## Atualizar o mapa ("atualiza o mapa")
`07_Recursos/mapa_prospeccao.html` — contorno real de SP, 9 ondas. Editar o array `regions` (campo `c` = contagem da região; `st`: `go` em andamento / `next` próxima / `plan` planejada / `done` concluída). Abre no celular; regenerável a qualquer momento.

## Saída pro Allan / tráfego pago
- O Allan **dispara o WhatsApp um a um** (anexando a demo do nicho — `demo_<nicho>.png`, skill `kronos-demo-whatsapp`) e **salva cada contato no chip do celular** — esses contatos viram **público personalizado (custom audience) do tráfego pago**. Por isso volume de contato salvo importa, não só os que respondem. Ver [[contatos-chip-trafego-pago]] e [[trafego-pago-estrategia]].
- E-mail: eu deixo os **rascunhos prontos no Gmail** com a mesma demo anexada.
- Mensagens por nicho prontas em `05_Comercial/` (LOCAL, gitignored — **não commitar**). Tom caloroso, assinadas "Allan Rodrigues — Fundador da Kronos" + site.

## Ordem das ondas
1) Campinas (RMC) → 2) Capital + Grande SP → 3) Vale do Paraíba → 4) Baixada Santista → 5) Ribeirão Preto → 6) Sorocaba → 7) Rio Preto → 8) Bauru → 9) Oeste. Esgotar os 3 nichos da região antes de abrir a próxima.
