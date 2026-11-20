# Third-party notices

The skills in `skills/ui-ux/` were written by other people and are included here unmodified under their MIT licenses. Each skill folder carries its upstream `LICENSE` file. Credit and ownership stay with the original authors; update from the source, not from this copy.

Machine-readable pins live in `vendor.json`. `scripts/validate-skills.py` checks that every entry there has a `LICENSE` and a row here; the `skill-update-check` skill and the weekly upstream workflow compare the pins with upstream.

| Skill | Author | Source | Pinned commit | Copied |
|---|---|---|---|---|
| `better-motion` | Jakub Krehel | https://github.com/jakubkrehel/skills (`skills/better-motion`) | `672ae44` | 2026-11-20 |
| `better-ui` | Jakub Krehel | https://github.com/jakubkrehel/skills (`skills/better-ui`) | `672ae44` | 2026-11-20 |
| `emil-design-eng` | Emil Kowalski | https://github.com/emilkowalski/skills (`skills/emil-design-eng`) | `64eb3de` | 2026-11-17 |
| `ui-ux-pro-max` | Next Level Builder | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (`.claude/skills/ui-ux-pro-max`) | `2de1134` | 2026-11-20 |

Vetting notes (read-through and grep, not a security audit):

- `emil-design-eng`, `better-ui` and `better-motion` contain Markdown only, plus an `agents/openai.yaml` display file in the Krehel skills.
- `ui-ux-pro-max` contains Python scripts and CSV data, about 3.7 MB. No network calls were found in the scripts; `subprocess` appears only in its tests; URLs in `scripts/validate_data.py` are data checked against an allowlist of publishers, not fetched. One script reads the `COLORTERM` environment variable. Scripts were read, not run.
- On 2026-11-20 upstream moved motion guidance out of `better-ui` into the new `better-motion`; both are included so no content was lost in the refresh.

If an author asks for removal or a newer version is published, remove or refresh the folder, update `vendor.json`, and update this table.
