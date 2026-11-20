# Plugin install

A Claude Code or Codex user adds the skillsmith marketplace and installs one or more pack plugins (`skillsmith`, `ui-ux`, `workflows`), and each registers exactly its pack's skills at the version in its `plugin.json`.

## Sub-features

- `plugin-add` adds the repo as a marketplace.
- `plugin-install` installs each `<pack>@skillsmith` at user scope.
- `plugin-version` installs the version declared in each pack's `.claude-plugin/plugin.json`.
- `plugin-skills` registers exactly the skills under `skills/<pack>/`; together, every skill under `skills/`.
- `plugin-codex` the same marketplace installs in Codex with `codex plugin marketplace add` and `codex plugin add`.

## How to get to it (user POV)

- Run `claude plugin marketplace add Atou4/skillsmith`, then `claude plugin install <pack>@skillsmith` per pack.
- Codex: `codex plugin marketplace add Atou4/skillsmith`, then `codex plugin add <pack>@skillsmith`.
- Verification uses the local path in place of `Atou4/skillsmith`, so uncommitted work is tested.

## Driving it with verify.sh

Preconditions:

- `verify.sh doctor` passes.
- `CLAUDE_CONFIG_DIR` is the helper's throwaway directory (the helper sets it).

- **Install.** Run `verify.sh install`. The output contains `Successfully added marketplace: skillsmith` and `Successfully installed plugin: skillsmith@skillsmith`.
- **Version.** The same run checks each `<pack> <version>` header from `claude plugin details` against `marketplace.json`, and `Read from: <repo path>` in `artifacts/<RUN_ID>/install.txt`.
- **Skills.** The run compares the union of `Skills (n)` lines with the folders under `skills/`. End state: `PASS: install: plugins <names>; <n> skills registered from the working tree`.
- **Codex (manual).** With `CODEX_HOME` set to a throwaway directory: `codex plugin marketplace add <repo path>`, `codex plugin add <pack>@skillsmith` per pack, then list `SKILL.md` files under `$CODEX_HOME/plugins/cache/skillsmith/<pack>/<version>/`. Each pack's cache holds only its own skills.

## Gotchas

- Without the isolated `CLAUDE_CONFIG_DIR`, the install lands in the user's real config. The helper refuses `~/.claude`; a hand-typed command does not.
- The plugin is copied into the isolated cache at install time. Edits made afterwards do not appear. Use a new `RUN_ID`.
- If you bump the version, installs of the old version in other configs do not update until the version differs.
- Claude's loader accepted a skill with invalid YAML frontmatter that the CLI rejected. A pass here does not prove `cli-discovery`.
