# Third-party notices

The skills in `skills/ui-ux/` were written by other people and are included here unmodified under their MIT licenses. Each skill folder carries its upstream `LICENSE` file. Credit and ownership stay with the original authors; update from the source, not from this copy.

| Skill | Author | Source | Pinned commit | Copied |
|---|---|---|---|---|
| `emil-design-eng` | Emil Kowalski | https://github.com/emilkowalski/skills (`skills/emil-design-eng`) | `64eb3de` | 2026-11-17 |
| `better-ui` | Jakub Krehel | https://github.com/jakubkrehel/skills (`skills/better-ui`) | `6c21201` | 2026-11-17 |
| `ui-ux-pro-max` | Next Level Builder | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (`.claude/skills/ui-ux-pro-max`) | `e59ff37` | 2026-11-17 |

Vetting notes (read-through and grep, not a security audit): `emil-design-eng` and `better-ui` contain Markdown only (`better-ui` also has an `agents/openai.yaml`). `ui-ux-pro-max` contains Python scripts and CSV data, about 3.7 MB; no network calls were found in the scripts, `subprocess` appears only in its tests, and one script reads the `COLORTERM` environment variable. Scripts were read, not run.

If an author asks for removal or a newer version is published, remove or refresh the folder and update this table.
