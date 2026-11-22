# Changelog

## 0.5.0 (2026-11-22)

- New `mobile` pack, the first stack pack, with `flutter-performance` and `flutter-security` from hoangnguyen0403/agent-skills-standard (MIT), vendored unmodified and pinned at `c679e00`. Install with `mobile@skillsmith`.

## 0.4.1 (2026-11-20)

- Logo and icon: every pack now ships a square `icon.png`, the README has a header logo, and `assets/brand/` holds the logo, icon and social preview image.
- Validator requires a 512 to 2048 px square PNG icon per pack; `scaffold.py pack` copies it.
- Pack groups for stack skills defined in `SCOPE.md`: `frontend`, `backend`, `mobile`, `infra`, `devops` (each created with its first skill).

## 0.4.0 (2026-11-20)

- New `platform-pipeline` in the `workflows` pack: PRD, artboards, a hard approval gate, visual research, then a build verified in the running app; Platform init once, then a Feature cycle per feature. Generalized from a personal version: dependency table with sources and fallbacks, project state in `docs/platform-pipeline.md`, no self-invoking build-discipline skill, the post-approval autonomy rule defined in the skill (still stops for destructive or outward-facing actions), and a routing note between it and `feature-forge`.
- CI runs only when checked files change; SkillSpector only when `vendor.json` changes or by hand.

## 0.3.0 (2026-11-20)

**Breaking for plugin users:** the single `skillsmith` plugin is now three packs. `skillsmith@skillsmith` contains only the meta skills; install `ui-ux@skillsmith` and `workflows@skillsmith` for the rest.

- One plugin per pack, so each user loads only the skills they install. Works with Claude Code and Codex plugin installs.
- New `skill-update-check` (meta): reports which CLI-installed or vendored skills changed upstream, with the commits, and proves vendored copies are byte-identical to their pins.
- New `workflows` pack with `feature-forge`, generalized: dependency table with sources and fallbacks, no self-invoking build-discipline skill, an invented worked example.
- `ui-ux` refreshed from upstream; `better-motion` added, because upstream moved motion guidance out of `better-ui`.
- `project-factory` is agent-neutral and routes through a user-owned `~/.project-factory/ROUTING.md` (template included) instead of a hard-coded table of skills the repo does not ship.
- Validator enforces the pack layout, plugin and marketplace consistency, vendored licenses and notices, hidden dev-only skills, and rejects unfinished template skills.
- `scripts/scaffold.py` creates packs and skills with manifests in sync.
- CI checks the skills CLI route, the audit fixture and vendored copies; a weekly job opens an issue when upstream skills change; a report-only SkillSpector scan runs on skill changes.
- `CONTRIBUTING.md`, this changelog.

## 0.2.2 (2026-11-17)

- Fixed `skill-sync` frontmatter: an unquoted `: ` made it invisible to the skills CLI.
- Strict YAML frontmatter validation; dev-only `verify-skillsmith` verification skill.

## 0.2.1 (2026-11-17)

- `skill-vetter`: optional SkillSpector static scan stage.

## 0.2.0 (2026-11-17)

- `skill-sync`; CI validation workflow.

## 0.1.0 (2026-11-17)

- Initial meta skills (`project-factory`, `skill-pack-installer`, `skill-vetter`, `skill-audit`) and the UI/UX bundle.
