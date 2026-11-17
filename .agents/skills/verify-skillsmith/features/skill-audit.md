# Skill audit

A user runs the audit script and gets a read-only report of broken symlinks, malformed skills, duplicates and drift across their agent skill folders.

## Sub-features

- `audit-broken` reports a symlink whose target is gone.
- `audit-malformed` reports a missing SKILL.md, missing frontmatter fields, or a `name` that differs from the folder.
- `audit-readonly` changes nothing on disk.
- `audit-multiline` reads descriptions written over several lines or with block markers.

## How to get to it (user POV)

- Ask the agent to audit skills (the `skill-audit` skill), which runs `python3 -I skills/meta/skill-audit/scripts/audit.py`.
- Run the script directly, optionally with extra skill roots as arguments.

## Driving it with verify.sh

Preconditions:

- `verify.sh doctor` passes.
- Never point the fixture at the user's real skill folders; the helper builds its own.

- **Fixture.** Run `verify.sh audit-fixture`. It builds a root with one good skill, one skill whose `name` is `other`, an empty folder, and a symlink to a missing path, then runs the audit on it.
- **Expected.** `artifacts/<RUN_ID>/audit-fixture.txt` contains `| Broken symlinks | 1 |`, `| Malformed | 2 |`, and the line ``name 'other' differs from folder``. End state: `PASS: audit-fixture: 1 broken symlink and 2 malformed skills found in a known-bad fixture`.
- **Real machine (optional).** Run `python3 -I skills/meta/skill-audit/scripts/audit.py` with no arguments and read the counts. It only reads. Do not act on findings here; that is `skill-sync`.

## Gotchas

- The first version misread multi-line `description:` values as empty and reported false "malformed" skills. The fixture does not cover multi-line descriptions; if you change the parser, test against a real multi-line example (for example a skill whose description starts on the next line).
- "Missing in some roots" is noisy on a real machine because many skills are deliberately single-agent. It is a prompt to decide, not a defect.
- Run with `python3 -I` so a stray module in the working directory cannot be imported.
