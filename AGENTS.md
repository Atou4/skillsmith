# skillsmith

A marketplace of agent skill packs, one plugin per pack. Read `SCOPE.md` and `CONTRIBUTING.md` before adding anything.

## Layout

- Skills live in `skills/<pack>/<skill-name>/SKILL.md`, exactly two levels down. Packs today: `meta` (plugin `skillsmith`), `ui-ux` (third-party, vendored unmodified), `workflows`, `mobile`, `devops`. Stack skills go in `frontend`, `backend`, `mobile`, `infra` or `devops` (see `SCOPE.md`), created with their first skill; never nest a pack inside a pack.
- Each pack has `skills/<pack>/.claude-plugin/plugin.json` listing all its skills, a square `icon.png` beside it (`assets/brand/icon-512.png`), and an entry in `.claude-plugin/marketplace.json` with the same name and version.
- Create packs and skills with `scripts/scaffold.py`; it keeps the manifests in sync.
- Vendored skills are pinned in `vendor.json` and credited in `THIRD_PARTY_NOTICES.md`. Never edit one here; refresh it from upstream with the `skill-update-check` skill.
- `.agents/skills/verify-skillsmith/` is a dev-only skill (`metadata.internal: true`); `.claude/skills/` and `.cursor/skills/` link to it. Any `SKILL.md` outside `skills/` must carry that flag, or installers offer it to users.

## Authoring rules

- `name` equals the folder name. Description under 1024 characters, written as what it does and when to use it.
- Workflow first: numbered steps the agent can check, ending in a verification step.
- Skills that read or change the user's machine say what they will not do (delete, overwrite, send data) and what they ask first.
- No personal data: no home-directory paths, names, emails, project names, or employer details. Use `~` and placeholders.
- Per-user state never lives inside a skill folder. Use `~/.<skill-name>/`.
- Third-party skills are untrusted. Describe vetting by reading and grepping, never by running their scripts.

## Validate before committing

Full end-to-end check (every pack's plugin install, CLI discovery, audit fixture, vendored copies): `.agents/skills/verify-skillsmith/scripts/verify.sh all`.

Quick check:

```bash
uv run --with pyyaml python scripts/validate-skills.py
```

Docs-only changes need no other checks. Run `python3 -I skills/meta/skill-audit/scripts/audit.py` after changing the audit script and read the output.
