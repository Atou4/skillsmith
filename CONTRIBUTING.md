# Contributing

Read [`SCOPE.md`](SCOPE.md) first. Then pick the case below.

## Add a skill to an existing pack

```bash
python3 scripts/scaffold.py skill <pack-folder> <skill-name>
```

This copies `template/SKILL.md.template` and lists the skill in the pack's `plugin.json`. Then write the skill:

- `name` equals the folder name, kebab-case, unique across the whole repo (the skills CLI installs by name).
- The `description` says what the skill does and when to use it, with the phrases a user would type. It must be valid YAML: quote it if it contains `: `. Under 1024 characters.
- Numbered steps the agent can check, ending in a verification step. Say what the skill will not do and what it asks first.
- No personal data: no home-directory paths, names, emails, real project or employer details. Examples use invented names.
- Per-user state lives in `~/.<skill-name>/`, never inside the skill folder; plugin updates replace the folder.
- Skills that depend on other skills list them with a source and a fallback for when they are missing.

## Add a pack

Packs are grouped by what the reader does, so a developer installs `mobile` or `devops` rather than one plugin per framework. The groups are listed in [`SCOPE.md`](SCOPE.md): `frontend`, `backend`, `mobile`, `infra`, `devops`, plus `meta`, `ui-ux` and `workflows`. Use an existing group; add a new one only when none fits, and only with its first finished skill.

```bash
python3 scripts/scaffold.py pack <pack-folder> --description "<one sentence>" [--plugin-name <name>] [--category <category>]
```

This creates `skills/<pack-folder>/.claude-plugin/plugin.json` and `icon.png`, and adds the pack to `.claude-plugin/marketplace.json`.

- Skills sit exactly two levels down (`skills/<pack>/<skill>/`) so every install route finds them, including plain `npx skills add`. Do not nest packs inside packs.
- Skill names are unique across the whole repo and start with the technology, because one pack covers several: `flutter-performance`, `gcp-cloud-run`, `react-server-components`.
- Split a pack only when its skills serve different readers; never make one pack per skill.

## Add a third-party skill

Only with a license that allows redistribution (MIT, Apache-2.0, BSD). Otherwise link to it from a README instead.

1. Vet it with the `skill-vetter` skill and record the result in `THIRD_PARTY_NOTICES.md`.
2. Copy the upstream folder unmodified to `skills/<pack>/<skill>/` and add the upstream `LICENSE` file.
3. Add an entry to `vendor.json` with the full pinned commit, and a row to `THIRD_PARTY_NOTICES.md`.
4. List the skill in the pack's `plugin.json`.

Never edit a vendored skill. Refresh it from upstream with the `skill-update-check` skill.

## Before you open a pull request

```bash
uv run --with pyyaml python scripts/validate-skills.py      # or: pip install pyyaml && python3 scripts/validate-skills.py
.agents/skills/verify-skillsmith/scripts/verify.sh all      # needs the claude CLI and npx
```

CI is kept small. `validate` (about 30 seconds) runs only when skills, scripts, manifests or vendored files change, never for docs-only commits. The SkillSpector scan (about 9 minutes) runs only when `vendor.json` changes or by hand from the Actions tab. The upstream check runs once a week for a few seconds. Every job has a timeout, superseded runs are cancelled, and reports are kept for 7 days. Run `verify.sh all` locally before pushing rather than relying on CI.

## Releases

Bump the version in every pack's `plugin.json` and in `marketplace.json` together (the validator checks they match), add a `CHANGELOG.md` entry, tag `vX.Y.Z`, and publish a GitHub release. Plugin installs update only when the version changes.
