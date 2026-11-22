# Third-party notices

The skills in `skills/ui-ux/` and the Flutter skills in `skills/mobile/` were written by other people and are included here unmodified under their MIT licenses. Each skill folder carries its upstream `LICENSE` file. Credit and ownership stay with the original authors; update from the source, not from this copy.

Machine-readable pins live in `vendor.json`. `scripts/validate-skills.py` checks that every entry there has a `LICENSE` and a row here; the `skill-update-check` skill and the weekly upstream workflow compare the pins with upstream.

| Skill | Author | Source | Pinned commit | Copied |
|---|---|---|---|---|
| `better-motion` | Jakub Krehel | https://github.com/jakubkrehel/skills (`skills/better-motion`) | `672ae44` | 2026-11-20 |
| `better-ui` | Jakub Krehel | https://github.com/jakubkrehel/skills (`skills/better-ui`) | `672ae44` | 2026-11-20 |
| `emil-design-eng` | Emil Kowalski | https://github.com/emilkowalski/skills (`skills/emil-design-eng`) | `64eb3de` | 2026-11-17 |
| `ui-ux-pro-max` | Next Level Builder | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (`.claude/skills/ui-ux-pro-max`) | `2de1134` | 2026-11-20 |
| `flutter-error-handling` | Hoang Nguyen | https://github.com/hoangnguyen0403/agent-skills-standard (`skills/flutter/flutter-error-handling`) | `c679e00` | 2026-11-22 |
| `flutter-performance` | Hoang Nguyen | https://github.com/hoangnguyen0403/agent-skills-standard (`skills/flutter/flutter-performance`) | `c679e00` | 2026-11-22 |
| `flutter-security` | Hoang Nguyen | https://github.com/hoangnguyen0403/agent-skills-standard (`skills/flutter/flutter-security`) | `c679e00` | 2026-11-22 |
| `flutter-testing` | Hoang Nguyen | https://github.com/hoangnguyen0403/agent-skills-standard (`skills/flutter/flutter-testing`) | `c679e00` | 2026-11-22 |

Vetting notes (read-through and grep, not a security audit):

- `emil-design-eng`, `better-ui` and `better-motion` contain Markdown only, plus an `agents/openai.yaml` display file in the Krehel skills.
- `ui-ux-pro-max` contains Python scripts and CSV data, about 3.7 MB. No network calls were found in the scripts; `subprocess` appears only in its tests; URLs in `scripts/validate_data.py` are data checked against an allowlist of publishers, not fetched. One script reads the `COLORTERM` environment variable. Scripts were read, not run.
- `flutter-performance`, `flutter-security`, `flutter-testing` and `flutter-error-handling` contain Markdown and an `evals/evals.json` test file; no scripts, no network calls, no secrets (the only credential-like text is a placeholder test password in a `patrol test` example). Read in full on 2026-11-22. Upstream rough edges, left as they are because vendored skills are never edited: `flutter-security` links a `secure-storage-impl.md` and a `common/security-standards` topic that upstream does not ship; all four assume a BLoC architecture; `flutter-testing` links to `../../common/common-tdd/` and `../../common/common-mobile-visual-testing/` files and `flutter-error-handling` to a `consumption.md`, none of which upstream ships with the skill; `flutter-testing` and `flutter-error-handling` rely on project helpers that you must supply or replace (`TestWrapper`, `BaseRobot`, `IntegrationAuthHelper`, `AppLogger`, `AppException`) and on `dartz`, `freezed`, `get_it`, `bloc_test`, `mocktail` and `patrol`; the example certificate fingerprint is a placeholder and SHA-1.
- On 2026-11-20 upstream moved motion guidance out of `better-ui` into the new `better-motion`; both are included so no content was lost in the refresh.

If an author asks for removal or a newer version is published, remove or refresh the folder, update `vendor.json`, and update this table.
