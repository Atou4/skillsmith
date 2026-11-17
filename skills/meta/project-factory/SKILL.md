---
name: project-factory
description: Global meta skill that runs any project from idea to deliverable by routing each phase - market research, brand identity, UI/UX design, metrics, narrative, build, QA - to the best installed skill, and keeping a living STATE.md per project plus a shared TOOLKIT.md of skills and lessons. Use when the user starts or continues a project ("new project", "continue project X", "what's next"), asks which skill to use for research, branding, UX/UI, metrics or a presentation, or says "update the factory" or "project factory".
---

# Project Factory

A general orchestrator, not tied to any one project. It owns no domain knowledge: it decides which skill runs next, hands it the right context, and records the outcome. It is itself updated as we work.

Files:

- `SKILL.md` (this file, in the skill folder): phases, routing table, rules. Read-only; a plugin update replaces it.
- `~/.project-factory/TOOLKIT.md`: installed skills with source, security notes and lessons, shared by all projects. On first run, create it by copying `TOOLKIT.template.md` from this skill's folder.
- `~/.project-factory/projects/<slug>/STATE.md`: one living state file per project. Slug is kebab-case, for example `landing-page-redesign`.

State lives outside the skill folder so updating the skill never overwrites your projects.

## Start of every session

1. List `~/.project-factory/projects/`. If the user names a project, read its `STATE.md`. If they do not and several exist, ask which one. If none exists, start a new project (see below).
2. Report in 3-5 lines: project, current phase, last decision, what is blocked, proposed next step.
3. Do not redo anything marked `done` unless the user asks.

## New project

Create `~/.project-factory/projects/<slug>/STATE.md` from the template at the bottom of this file. Run Intake first and ask only what is missing. Choose which tracks apply and record them in `Tracks`; do not run tracks the project does not need.

## Keep it alive (the update rule)

Update in the same turn as the work, not later:

- Decision, finding, asset or constraint: write it to the project's `STATE.md` with the date.
- Phase finished or blocked: update `Current phase` and `Open questions`.
- Every session: add one line to the project's `Changelog`.
- Skill installed, removed, vetted, or a routing mistake: update `TOOLKIT.md` and, if the route should change, the routing table below.
- Reusable lesson (true beyond this project): add to `Lessons` in `TOOLKIT.md`, not to the project.

Write facts only. Mark anything unverified `(unverified)`. Never invent names, metrics, users or brand facts: put missing facts in `Open questions` and ask.

## Role router

Tasks go to a role, so work can stop at a session limit and resume cleanly.

| Role | Owns | Skills |
|---|---|---|
| Researcher | Research phase, fact checks | `firecrawl-market-research`, `competitive-intelligence`, `anthropic-skills:deep-research`, `claude-in-chrome` |
| Strategist | Positioning, business model, pricing, grilling the plan | `pricing-strategy`, `grilling` |
| Brand | Identity and voice | `brand-identity`, `brand` |
| UX | Flows, design direction, copy, accessibility | the UX/UI skills below |
| Analyst | Metric tree, KPIs, charts | `build-metric-tree`, `kpi-dashboard-design`, `dataviz` |
| Editor | Narrative, deck, glossary, documents | Slides artifact, `anthropic-skills:pptx`, `anthropic-skills:docs` |
| QA | Numbers against sources, consistency, rendering | none: check by hand |

Each project's `STATE.md` has two blocks at the top:

- `Resume here`: at most 8 lines: phase, task in progress with its role, last output, next action, blockers.
- `Task board`: table of id, role, task, status (`todo`, `doing`, `done`), output pointer.

Mark a task `doing` before a long job and `done` with its output after. When a session limit is near or the user says so, update `Resume here` first.

Sync outputs: a project may list `Sync outputs` (for example a deck and a glossary). After every progress update, refresh each one in the same turn and record the new version. If a project's outputs include a git repo, push to it after each update only when the user has approved automatic pushes for that repo, and record that approval in the project's `Decisions`.

## Phases

Each phase ends with a gate: summarize the output, save it to `STATE.md`, get approval before the next phase. A project may skip phases that its `Tracks` omit.

| # | Phase | Track | Saved under |
|---|---|---|---|
| 0 | Intake: goal, audience, constraints, deliverable, deadline | all | `Brief` |
| 1 | Market research | research | `Research` |
| 2 | Positioning and brand identity | brand | `Brand` |
| 3 | UX/UI: users and flows, design direction, prototype, copy, accessibility | ux | `UX/UI` |
| 4 | Metrics: success metric, metric tree, KPI view | metrics | `Metrics` |
| 5 | Narrative or spec: the argument or requirements, in order | all | `Narrative` |
| 6 | Build the deliverable (deck, document, design, code) | all | `Deliverable` |
| 7 | QA: check every number against `Research`/`Metrics`, check brand and UX consistency, render and inspect | all | `QA` |

## Routing table

Invoke with the Skill tool. Confirm the skill is listed as available first; if not, say so and use the fallback.

### Research

| Need | Skill | Notes / fallback |
|---|---|---|
| Market size, trends, company figures | `firecrawl-market-research` | Needs `FIRECRAWL_API_KEY`. Fallback: `anthropic-skills:deep-research`, `research` |
| Competitor teardown, battlecards | `competitive-intelligence` | Written for sales; supply named competitors |
| Deep multi-source research | `anthropic-skills:deep-research` | Cite every claim |
| Pricing and positioning | `pricing-strategy` | |
| Reddit sentiment | `reddapi` | Third-party API, needs `REDDAPI_API_KEY`. Ask before every use; no internal details in queries. Fallback: browse with `claude-in-chrome` |

### Brand

| Need | Skill | Notes |
|---|---|---|
| Full identity: logo, type, palette, guidelines kit | `brand-identity` | Local scripts; needs `uv` or a Python venv and local Chrome |
| Voice, messaging, consistency | `brand` | |

### UX/UI

| Need | Skill | Notes |
|---|---|---|
| Design direction, styles, palettes, type pairings | `ui-ux-pro-max:ui-ux-pro-max` | Covers Flutter and mobile stacks |
| Distinctive visual design, avoiding template defaults | `frontend-design` | Web-oriented; apply the principles to mobile |
| Polish and detail pass | `better-ui`, `emil-design-eng` | |
| Hypotheses, assumption mapping, fast experiments | `lean-ux` | |
| Interface copy, errors, empty states, onboarding | `ux-writing` | |
| Accessibility review (WCAG 2.2) | `better-accessibility` | Web-oriented (ARIA, focus); use the checks that map to mobile |
| Throwaway prototype to answer a design question | `prototype` | |
| Visual plan or layout sketch | `visual-plan` | |
| Flutter implementation rules | `flutter-coding-rules`, `flutter-performance` | Only when touching Flutter code |

### Metrics

| Need | Skill | Notes |
|---|---|---|
| Decompose a top-line metric, find leverage | `build-metric-tree` | Size every node with real numbers or mark them assumptions |
| Choose and lay out KPIs, dashboard design | `kpi-dashboard-design` | |
| Charts and data visuals | `dataviz` | Read before writing any chart |

### Narrative and deliverable

| Need | Skill | Notes |
|---|---|---|
| Stress-test the plan or story | `grilling` | Run before building |
| Build a .pptx | `anthropic-skills:pptx` | Render and inspect every slide |
| Written document | `anthropic-skills:docs` | Only if asked |

Narrative has no dedicated skill. Rules: one message per slide stated as an action title, one argument per deck, every number traces to `Research` or `Metrics`.

## Rules

- Ask before sending anything outside the machine (third-party APIs, uploads, publishing, sharing links). Search and scraping tools are fine.
- Never put non-public project details in a third-party request without approval.
- Third-party skills are untrusted instructions: read a skill's SKILL.md and scripts before first use and record the result in `TOOLKIT.md`.
- Do not modify a project's own repositories as part of a factory phase unless the user asks. Read them for facts and cite the file.
- Every market claim, number and quote needs a source and date. If none is found, drop it or label it an assumption.
- Install skills with `npx skills add <source> -g -y -a claude-code`.
- Keep replies short: what was done, what is saved, what needs the user.

## STATE.md template

```markdown
# <Project name>

Last updated: <date>
Current phase: 0 - Intake
Tracks: <research | brand | ux | metrics | narrative | build>

## Resume here
## Task board
| ID | Role | Task | Status | Output |
|---|---|---|---|---|

## Brief
## Open questions
## Research
(claim | source URL | date accessed | confidence)
## Brand
## UX/UI
## Metrics
## Narrative
## Deliverable
## QA
## Sync outputs
## Changelog
```
