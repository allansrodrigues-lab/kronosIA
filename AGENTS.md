# AGENTS

Este repositório é um projeto de documentação e design de automações para uma clínica de estética.
Ele descreve fluxos n8n, agentes de IA, base de conhecimento e métricas — não há aplicação de código-fonte executável.

## Objetivo para agentes de IA
- Trate este projeto como documentação técnica de automação e não como um código-fonte tradicional.
- Use a estrutura de pastas e os arquivos Markdown como fonte primária de verdade.
- Mantenha o tom e a linguagem em português (pt-BR), alinhado ao conteúdo existente.

## Estrutura principal
- `README.md` — visão geral do projeto
- `01_Briefing/` — briefing, escopo, objetivos e stakeholders
- `02_Documentacao/` — arquitetura geral, integrações e glossário
- `03_Fluxos_Automacao/` — documentação dos fluxos n8n
- `04_Agentes_IA/` — agentes de IA, persona e orquestração
- `04_Agentes_IA/base_conhecimento/` — base de conhecimento usada pelos agentes
- `05_Checklist_Testes/` — planos de teste e casos de QA
- `06_Metricas/` — KPIs, dashboards e relatórios
- `07_Recursos/` — prompts, credenciais e recursos de suporte

## Convenções importantes
- Arquivos usam prefixos numéricos para manter ordenação lógica.
- Cada fluxo em `03_Fluxos_Automacao/` deve documentar: objetivo, gatilho, passos, integrações, tratamento de erros, métricas.
- Cada agente em `04_Agentes_IA/` deve documentar: persona, escopo, ferramentas, prompt base e exemplos.
- Atualizações de serviços, preços ou políticas devem refletir em `04_Agentes_IA/base_conhecimento/`.

## Diretrizes para escrever ou alterar conteúdo
- Prefira criar ou atualizar documentação em Markdown, não código executável.
- Quando possível, link direto para arquivos existentes em vez de reproduzir conteúdo.
- Não invente detalhes de arquitetura, integrações ou implementação que não estejam documentados.
- Se faltar informação sobre um fluxo ou agente, solicite esclarecimento do usuário antes de completar o conteúdo.
- Não procese este repositório como se fosse um projeto com build/test automático; não há comandos de compilação padrão.

## Quando for preciso ajudar com tarefas
- Para propostas de fluxo ou agentes, alinhe-se com os padrões existentes em `03_Fluxos_Automacao/README.md` e `04_Agentes_IA/README.md`.
- Para sugestões de melhorias, preserve a estrutura de pastas e a nomenclatura numérica.
- Para conteúdo de IA, respeite o princípio: especialização de agentes, voz única e handoff fluido.
