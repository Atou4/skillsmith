# CLI discovery

A user runs the `skills` CLI against the repo and is offered exactly the skills the repo defines, nothing missing and no placeholders.

## Sub-features

- `cli-list` lists every skill folder under `skills/`.
- `cli-no-extras` offers no template, test or verification skill.
- `cli-readonly` leaves the user's skill folders and lock file untouched in list mode.

## How to get to it (user POV)

- Run `npx skills add Atou4/skillsmith --list` to preview, or without `--list` to install.
- Verification runs `npx skills add <repo path> --list` only.

## Driving it with verify.sh

Preconditions:

- Network access for `npx` to fetch the CLI.
- `verify.sh doctor` passes.

- **Discover.** Run `verify.sh discover`. It extracts the skill names from the CLI output into `artifacts/<RUN_ID>/skills-list.txt` and compares them with the folder names under `skills/`.
- **Read-only.** The same run records the entry counts of `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills` and the modification time of `~/.agents/.skill-lock.json` before and after, and fails if they differ. End state: `PASS: discover: CLI lists exactly the <n> repo skills; no skill folder or lock file changed`.

## Gotchas

- The CLI silently skips a skill whose frontmatter is not valid YAML. An unquoted `: ` in a `description` caused `skill-sync` to be missing from `--list` while the plugin route showed it. Diff the sets; do not trust a count.
- The CLI scans the whole repo for `SKILL.md`, not only `skills/`. A `SKILL.md` in `template/` was once listed as an installable skill; the template is now `SKILL.md.template`. If a new folder shows up in the list, look for a stray `SKILL.md`.
- Never run `npx skills add` without `--list`, or `npx skills update` in any form, during verification.
- This verification skill lives under `.agents/skills/` (linked from `.claude/skills/` and `.cursor/skills/`). The `skills` CLI scans `.agents/skills/` and `.claude/skills/` (it did not scan `.cursor/`), so without `metadata: internal: true` in its frontmatter users would be offered it. Keep that flag. If the verifier ever appears in the list, `verify.sh discover` fails because the CLI's set no longer equals `skills/`.
