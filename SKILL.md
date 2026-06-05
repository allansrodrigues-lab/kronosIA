<!--
Skill: agent-customization for "teste Automação" workspace
Generated: 2026-06-02
Purpose: capture and reuse the project's conversation-to-skill workflow
-->

# Skill: Project Workflow Extraction & Agent Customization

## Summary
This skill captures a repeatable process for converting a multi-step conversation, decision logic, and quality checks into a workspace-scoped `SKILL.md` that informs Copilot/agents about the project's conventions and automation workflows.

## When to use
- You have a documented or interactive conversation describing a development, automation, or review workflow and want a reusable skill for agents.
- You need a consistent template for agent customization files (`SKILL.md`, `.prompt.md`, `.agent.md`, or `copilot-instructions.md`).

## Inputs
- Conversation history (chat transcript or notes)
- Project files and workspace structure
- Desired output scope: `workspace-scoped` (default) or `personal`

## Outputs
- A `SKILL.md` saved at workspace root containing:
  - step-by-step workflow
  - decision points / branching logic
  - quality criteria and completion checks
  - example prompts and usage notes
  - an iteration checklist for refinement

## Step-by-step process
1. Collect context: scan the workspace and conversation for explicit steps, files, and recurring patterns.
2. Identify goals: extract desired outcomes and acceptance criteria from the discussion.
3. Enumerate steps: write a linear or conditional step list that an agent can follow.
4. Capture decision points: for each step, list conditions that change the next action.
5. Define quality criteria: what constitutes “done” at each phase (tests, docs, lint, manual checks).
6. Draft the `SKILL.md` using the template below and save it to workspace root.
7. Present the draft to the user and request clarifications on ambiguous steps.
8. Iterate until acceptance, then suggest related customization files to add (prompts, agents, tests).

## Decision points and branching logic
- For each step include short conditional rules, e.g.:
  - If tests fail → run `fix-tests` step, then re-run tests.
  - If external credentials missing → prompt user for secret storage action.
  - If stakeholder approval required → pause and create approval checklist.

## Quality criteria / Completion checks
- Each task should include at least one measurable check: unit tests passing, new docs added, no lint errors, or reviewer sign-off.
- Mark a workflow step complete only after its checks pass.

## Example prompts to use this skill
- "Create a `SKILL.md` from the last 3 messages and save it workspace-scoped."
- "Extract the deployment checklist from the conversation and add it to `SKILL.md`."
- "Update the skill: add a decision branch for missing API keys."

## Ambiguities / Questions (to prompt user)
- Do you want this skill to be workspace-scoped (shared) or personal (private)?
- Which files should the agent read first when extracting context? (e.g., `README.md`, `01_briefing_projeto.md`)
- What are your concrete 'done' criteria for automation flows (tests, signoffs, monitoring)?

## Iteration plan
1. Save this draft to `SKILL.md` (workspace root).
2. Ask user the three ambiguity questions above.
3. Update the skill with answers and add example prompt templates tailored to the project.
4. Optionally generate companion files: `copilot-instructions.md` and an example `.prompt.md` for common tasks.

## Related customizations to create next
- `copilot-instructions.md` with persona + tone + safety rules.
- `AGENTS.md` listing agent responsibilities and invocation patterns.
- Example `workflow` prompts and a small test harness that validates the steps.

---
Created by agent on user request. Reply with answers to the Ambiguities section to finalize the skill.
