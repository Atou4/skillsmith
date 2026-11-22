<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark.svg">
    <img alt="skillsmith" src="assets/brand/logo-light.svg" width="420">
  </picture>
</p>

[![validate](https://github.com/Atou4/skillsmith/actions/workflows/validate.yml/badge.svg)](https://github.com/Atou4/skillsmith/actions/workflows/validate.yml)
[![release](https://img.shields.io/github/v/release/Atou4/skillsmith)](https://github.com/Atou4/skillsmith/releases)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Agent skills for Claude Code and Codex, organized as packs you install separately. Start with the meta pack: it vets skills before you install them, installs packs for several agents without overwriting your own, audits and syncs what you have, and tells you when upstream skills change.

## Packs

| Pack (plugin) | Skills | For |
|---|---|---|
| [`skillsmith`](skills/meta/) | 6 | Managing agent skills, and routing project work to the right skill |
| [`ui-ux`](skills/ui-ux/) | 4 | Design direction, polish, motion, interaction feel (third-party, unmodified) |
| [`workflows`](skills/workflows/) | 2 | Multi-step engineering workflows |
| [`mobile`](skills/mobile/) | 4 | Phone and tablet apps: Flutter performance, security, testing and error handling (third-party, unmodified) |

Each pack adds only its own skill descriptions to your sessions, so install the ones you use.

## Install

**Claude Code**

```bash
claude plugin marketplace add Atou4/skillsmith
claude plugin install skillsmith@skillsmith      # meta pack
claude plugin install ui-ux@skillsmith           # optional
claude plugin install workflows@skillsmith       # optional
claude plugin install mobile@skillsmith          # optional
```

**Codex**

```bash
codex plugin marketplace add Atou4/skillsmith
codex plugin add skillsmith@skillsmith
codex plugin add ui-ux@skillsmith
codex plugin add workflows@skillsmith
codex plugin add mobile@skillsmith
```

**Any agent, via the skills CLI**

```bash
npx skills add Atou4/skillsmith --list                                   # preview
npx skills add Atou4/skillsmith --global --agent claude-code codex --skill skill-vetter skill-audit --yes
```

Pick one route per agent; installing the same skill twice gives you duplicates. Restart the session afterwards.

## The skills

### `skillsmith`: meta

| Skill | Use it when |
|---|---|
| [`skill-vetter`](skills/meta/skill-vetter/SKILL.md) | You found a skill and want to know if it is safe and worth installing. Reads it, greps its scripts, optionally runs NVIDIA SkillSpector, and gives a one-line verdict. |
| [`skill-pack-installer`](skills/meta/skill-pack-installer/SKILL.md) | You want a skills repo installed for Claude Code and Codex, without overwriting skills you wrote, verified afterwards. |
| [`skill-audit`](skills/meta/skill-audit/SKILL.md) | You want a read-only report of broken links, duplicates, drift between agents and malformed skills. |
| [`skill-sync`](skills/meta/skill-sync/SKILL.md) | The audit found problems and you want them fixed, one approved change at a time. |
| [`skill-update-check`](skills/meta/skill-update-check/SKILL.md) | You want to know which installed or vendored skills changed upstream, and what changed. |
| [`project-factory`](skills/meta/project-factory/SKILL.md) | You are running a project end to end and want each phase routed to the right installed skill, with a state file so work resumes cleanly. |

```
find a skill -> skill-vetter -> skill-pack-installer -> skill-audit -> skill-sync
                                        skill-update-check, weekly or before a release
```

### `ui-ux`: third-party, included unmodified

| Skill | By | Use it when |
|---|---|---|
| [`ui-ux-pro-max`](skills/ui-ux/ui-ux-pro-max/SKILL.md) | Next Level Builder | You need design direction: styles, palettes, type pairings, UX guidelines across stacks. |
| [`better-ui`](skills/ui-ux/better-ui/SKILL.md) | Jakub Krehel | You want a detail pass: radius, optical alignment, surface depth, icons, hit areas. |
| [`better-motion`](skills/ui-ux/better-motion/SKILL.md) | Jakub Krehel | You are deciding what should animate, and need exact durations, easing and recipes. |
| [`emil-design-eng`](skills/ui-ux/emil-design-eng/SKILL.md) | Emil Kowalski | You are polishing a component's interactions and feel. |

Licenses, sources and pinned commits are in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). CI proves each copy is byte-identical to its pinned upstream commit, and a weekly job opens an issue when upstream moves.

### `workflows`

| Skill | Use it when |
|---|---|
| [`platform-pipeline`](skills/workflows/platform-pipeline/SKILL.md) | You are building a product from scratch, or adding the next feature to it. PRD, real artboards, a hard approval gate, visual research, then a build verified in the running app. |
| [`feature-forge`](skills/workflows/feature-forge/SKILL.md) | You are integrating an external service (payments, auth, messaging) across several repos you own. Pins the shared contract first, grills it against failure modes that cost money or trust, and builds the verification harness before the handler. |

### `mobile`: third-party, included unmodified

| Skill | By | Use it when |
|---|---|---|
| [`flutter-performance`](skills/mobile/flutter-performance/SKILL.md) | Hoang Nguyen | You are diagnosing jank, extra rebuilds or slow lists in a Flutter app. |
| [`flutter-security`](skills/mobile/flutter-security/SKILL.md) | Hoang Nguyen | You are storing tokens or PII, injecting secrets, pinning certificates or hardening a Flutter release build. |
| [`flutter-testing`](skills/mobile/flutter-testing/SKILL.md) | Hoang Nguyen | You are writing unit, widget and Patrol integration tests, with the robot pattern and widget keys. |
| [`flutter-error-handling`](skills/mobile/flutter-error-handling/SKILL.md) | Hoang Nguyen | You are turning exceptions into typed failures with `Either` in repositories and folding them in BLoCs. |

All four come from [agent-skills-standard](https://github.com/hoangnguyen0403/agent-skills-standard) (MIT). They assume a BLoC-style architecture and, in `flutter-testing` and `flutter-error-handling`, project helpers (`TestWrapper`, `AppLogger` and similar) that you supply or replace. More groups (`frontend`, `backend`, `infra`, `devops`) are added when their first skill is ready; see [`SCOPE.md`](SCOPE.md).

## Good skills we link to instead of copying

Some excellent skills have no redistributable license file, so they are not copied here. Install them from their own repos; `skill-vetter` first, as with any skill.

| Area | Skills | Install |
|---|---|---|
| Frontend (React, Next.js) | `react-best-practices`, `composition-patterns`, `react-view-transitions`, `web-design-guidelines` from [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | `npx skills add vercel-labs/agent-skills --list`, then pick with `--skill <name>` |
| Mobile (React Native, Expo) | `react-native-skills` from the same repo | same |
| Backend (Postgres, auth) | `supabase`, `supabase-postgres-best-practices` from [supabase/agent-skills](https://github.com/supabase/agent-skills) | `npx skills add supabase/agent-skills --list` |
| Infra (Firebase) | `firebase-*` skills from [firebase/agent-skills](https://github.com/firebase/agent-skills) | `npx skills add firebase/agent-skills --list` |

The `frontend`, `backend` and `infra` packs here will hold original or cleanly licensed skills when they exist; see [`SCOPE.md`](SCOPE.md).

## Example: `skill-update-check`

```
| Status | Count |
|---|---|
| changed | 2 |
| up to date | 1 |

## Changed

- `better-ui` (jakubkrehel/skills) pin 6c21201
  - 8d4b209 2026-11-18 Add better-motion skill
  - 19ab1fa 2026-11-17 Resolve contradictions and ambiguity found by cold reads and trials
- `ui-ux-pro-max` (nextlevelbuilder/ui-ux-pro-max-skill) pin e59ff37
  - ed766d3 2026-11-18 feat: add GIS web map and Earth observation product types (#582)
  - f984fcd 2026-11-18 feat: add web map UX guidelines (Maps category) (#581)
```

That is real output from this repo, three days after the UI/UX skills were first copied. The first commit moved content from `better-ui` into a new skill, which is why the skill reads commit titles before refreshing.

## Principles

- **Read before run.** Third-party skills are untrusted instructions. Vet them by reading, never by executing.
- **Never overwrite user work.** A real directory in a skills folder is yours; installers and sync skip it.
- **Verify, don't assume.** An exit code is not an installation. Both install routes are tested on every change.
- **Report, then fix.** Audits and update checks are read-only; you approve each change.

## Repository layout

```
.claude-plugin/marketplace.json   one entry per pack
skills/<pack>/
  .claude-plugin/plugin.json      the pack's plugin manifest
  <skill>/SKILL.md                one folder per skill
vendor.json                       pins for third-party skills
THIRD_PARTY_NOTICES.md            their licenses and sources
scripts/validate-skills.py        layout, manifests, frontmatter, notices
scripts/scaffold.py               create a pack or a skill with manifests in sync
.agents/skills/verify-skillsmith  dev-only end-to-end verification (hidden from installers)
```

## Contributing

New packs (Flutter, React, GCP and so on) and skills are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SCOPE.md`](SCOPE.md). Changes are listed in [`CHANGELOG.md`](CHANGELOG.md).

## License

MIT for this repository's own skills and scripts. Third-party skills keep their own licenses, listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
