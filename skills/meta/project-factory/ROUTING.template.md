# Project Factory routing

Copy this file to `~/.project-factory/ROUTING.md` on first run, then make it yours: delete rows for skills you will not install, add rows for skills you do. `project-factory` reads your copy, never this template.

Columns: **Skill** is the name your agent loads. **Source** is where to get it. **Ships with skillsmith** means it comes with one of this marketplace's plugins (plugin skills may be shown with a prefix, for example `ui-ux:better-ui`). **Notes** holds requirements and the fallback when the skill is missing.

Before routing to a skill, confirm it is available in the current agent. If it is not, say so and use the fallback. Vet third-party skills with `skill-vetter` before first use.

## Research

| Need | Skill | Source | Ships with skillsmith | Notes / fallback |
|---|---|---|---|---|
| Market size, trends, company figures | `firecrawl-market-research` | firecrawl/firecrawl-workflows | no | Needs `FIRECRAWL_API_KEY`. Fallback: `research` or the agent's own web research |
| Competitor teardown, battlecards | `competitive-intelligence` | anthropics/knowledge-work-plugins | no | Written for sales; supply named competitors |
| Multi-source research with citations | `research` | mattpocock/skills | no | Cite every claim |
| Reddit sentiment | `reddapi` | lignertys/reddit-research-skills | no | Third-party API, needs `REDDAPI_API_KEY`. Ask before every use. Fallback: read threads in a browser |

## Strategy

| Need | Skill | Source | Ships with skillsmith | Notes / fallback |
|---|---|---|---|---|
| Stress-test the plan | `grilling` | mattpocock/skills | no | Fallback: list the five ways the plan fails and answer each |
| Pricing and positioning | (your pricing skill) | | no | Fallback: price from competitors' published prices, with sources |

## Brand

| Need | Skill | Source | Ships with skillsmith | Notes / fallback |
|---|---|---|---|---|
| Full identity: logo, type, palette, guidelines | `brand-identity` | fatihaydost/brand-identity-skill | no | Local scripts; needs `uv` or a Python venv and Chrome |
| Voice, messaging, consistency | `brand` | nextlevelbuilder/ui-ux-pro-max-skill | no | |

## UX/UI

| Need | Skill | Source | Ships with skillsmith | Notes / fallback |
|---|---|---|---|---|
| Design direction, styles, palettes, type pairings | `ui-ux-pro-max` | nextlevelbuilder/ui-ux-pro-max-skill | yes (`ui-ux`) | Covers web and mobile stacks |
| Polish: radius, alignment, depth, icons, hit areas | `better-ui` | jakubkrehel/skills | yes (`ui-ux`) | |
| Motion: what to animate, durations, easing | `better-motion` | jakubkrehel/skills | yes (`ui-ux`) | |
| Interaction feel and component polish | `emil-design-eng` | emilkowalski/skills | yes (`ui-ux`) | |
| Distinctive visual design | `frontend-design` | anthropics/skills | no | Web-oriented |
| Accessibility review (WCAG 2.2) | `better-accessibility` | jakubkrehel/skills | no | Web-oriented; use the checks that map to mobile |
| Interface copy, errors, empty states | `ux-writing` | content-designer/ux-writing-skill | no | |
| Hypotheses, assumption mapping | `lean-ux` | wondelai/skills | no | |
| Throwaway prototype | `prototype` | mattpocock/skills | no | |

## Metrics

| Need | Skill | Source | Ships with skillsmith | Notes / fallback |
|---|---|---|---|---|
| Decompose a top-line metric | `build-metric-tree` | amplitude/builder-skills | no | Size nodes with real numbers or mark them assumptions |
| KPIs and dashboard layout | `kpi-dashboard-design` | wshobson/agents | no | |
| Charts | (your charting skill) | | no | Fallback: plain tables with sources |

## Build

| Need | Skill | Source | Ships with skillsmith | Notes / fallback |
|---|---|---|---|---|
| Integrate an external service across several repos | `feature-forge` | Atou4/skillsmith | yes (`workflows`) | Contract first, harness before build |
| Flutter implementation rules | `flutter-performance` | hoangnguyen0403/agent-skills-standard | no | Only when touching Flutter code |

## Narrative and deliverable

| Need | Skill | Source | Ships with skillsmith | Notes / fallback |
|---|---|---|---|---|
| Slide deck | (your deck skill) | | no | Render and inspect every slide |
| Written document | (your document skill) | | no | Only if asked |

Narrative rules, whatever the tool: one message per slide stated as an action title, one argument per deck, every number traces to `Research` or `Metrics`.
