# skillsmith

Meta skills for managing agent skills. They help you decide which skills to trust, install them cleanly for more than one agent, keep track of what you have, and run a project through the right skill at each phase.

Works with Claude Code and Codex.

## The skills

| Skill | Use it when |
|---|---|
| [`skill-vetter`](skills/meta/skill-vetter/SKILL.md) | You found a skill or pack and want to know if it is safe and worth installing. Produces a one-line verdict you can log. |
| [`skill-pack-installer`](skills/meta/skill-pack-installer/SKILL.md) | You want a pack installed for Claude Code and Codex without overwriting skills you wrote, and verified afterwards. |
| [`skill-audit`](skills/meta/skill-audit/SKILL.md) | You want to see broken links, duplicates, drift between agents and malformed skills. Read-only. |
| [`skill-sync`](skills/meta/skill-sync/SKILL.md) | `skill-audit` found problems and you want them fixed: relink skills missing from an agent, remove dead links, reconcile duplicates. Proposes every change and asks first. |
| [`project-factory`](skills/meta/project-factory/SKILL.md) | You are running a project end to end and want each phase (research, brand, UX, metrics, narrative, QA) routed to the best installed skill, with a living state file so work resumes cleanly. |

### UI/UX bundle (third-party, included unmodified)

| Skill | By | Use it when |
|---|---|---|
| [`ui-ux-pro-max`](skills/ui-ux/ui-ux-pro-max/SKILL.md) | Next Level Builder | You need design direction: styles, palettes, type pairings, UX guidelines across web and mobile stacks. |
| [`emil-design-eng`](skills/ui-ux/emil-design-eng/SKILL.md) | Emil Kowalski | You are polishing interface details: animation decisions, component feel. |
| [`better-ui`](skills/ui-ux/better-ui/SKILL.md) | Jakub Krehel | You want a detail pass: border radius, optical alignment, surface depth, icons, hit areas. |

These are other people's work under MIT licenses, with licenses and sources recorded in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). `project-factory` routes its UX phase to them.

## Install

Claude Code, as a plugin:

```bash
claude plugin marketplace add Atou4/skillsmith
claude plugin install skillsmith@skillsmith
```

Any agent, via the skills CLI:

```bash
npx skills add Atou4/skillsmith --global --agent claude-code codex --skill '*' --yes
```

Pick one route per agent. Installing both gives you every skill twice. Restart the session afterwards; new skills load at startup.

## How they fit together

```
find a pack -> skill-vetter -> skill-pack-installer -> skill-audit -> skill-sync
                                                           |
                       project-factory routes work to what is installed
```

`project-factory` keeps your projects in `~/.project-factory/`, outside the skill folder, so updating the plugin never touches your work.

## Principles

- **Read before run.** Third-party skills are untrusted instructions. Vet them by reading, never by executing.
- **Never overwrite user work.** A real directory in a skills folder is yours; installers skip it.
- **Verify, don't assume.** An exit code is not an installation.
- **Read-only audits.** Reporting and fixing are separate steps; you approve the fix.

## Develop

```bash
python3 scripts/validate-skills.py
```

Checks frontmatter, that each `name` matches its folder, description length, that `plugin.json` lists every skill, and that no personal paths leaked in. New skills start from [`template/SKILL.md.template`](template/SKILL.md.template). See [`AGENTS.md`](AGENTS.md) and [`SCOPE.md`](SCOPE.md).

## License

MIT
