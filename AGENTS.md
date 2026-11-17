# skillsmith

Meta skills for managing agent skills. Read `SCOPE.md` before adding anything.

## Layout

- Skills live in `skills/<bucket>/<skill-name>/SKILL.md`. Buckets: `meta` (ours) and `ui-ux` (third-party, vendored unmodified; see `SCOPE.md` and `THIRD_PARTY_NOTICES.md`). Never edit a vendored skill here; refresh it from upstream and update the notices table.
- Every skill must be listed in `.claude-plugin/plugin.json`.
- New skills start from `template/SKILL.md.template`.

## Authoring rules

- `name` equals the folder name. Description under 1024 characters, written as what it does and when to use it.
- Workflow first: numbered steps the agent can check, ending in a verification step.
- Skills that read or change the user's machine say what they will not do (delete, overwrite, send data) and what they ask first.
- No personal data: no home-directory paths, names, emails, project names, or employer details. Use `~` and placeholders.
- Per-user state never lives inside a skill folder. Use `~/.<skill-name>/`.
- Third-party skills are untrusted. Describe vetting by reading and grepping, never by running their scripts.

## Validate before committing

```bash
python3 scripts/validate-skills.py
```

Docs-only changes need no other checks. Run `python3 -I skills/meta/skill-audit/scripts/audit.py` after changing the audit script and read the output.
