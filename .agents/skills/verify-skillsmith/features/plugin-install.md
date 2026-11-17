# Plugin install

A Claude Code user adds the skillsmith marketplace and installs the plugin, and all of the repo's skills become available at the version in `plugin.json`.

## Sub-features

- `plugin-add` adds the repo as a marketplace.
- `plugin-install` installs `skillsmith@skillsmith` at user scope.
- `plugin-version` installs the version declared in `.claude-plugin/plugin.json`.
- `plugin-skills` registers exactly the skills under `skills/`.

## How to get to it (user POV)

- Run `claude plugin marketplace add Atou4/skillsmith`, then `claude plugin install skillsmith@skillsmith`.
- Verification uses the local path in place of `Atou4/skillsmith`, so uncommitted work is tested.

## Driving it with verify.sh

Preconditions:

- `verify.sh doctor` passes.
- `CLAUDE_CONFIG_DIR` is the helper's throwaway directory (the helper sets it).

- **Install.** Run `verify.sh install`. The output contains `Successfully added marketplace: skillsmith` and `Successfully installed plugin: skillsmith@skillsmith`.
- **Version.** The same run checks `Version: <plugin.json version>` and `Read from: <repo path>` in `artifacts/<RUN_ID>/install.txt`.
- **Skills.** The run compares the `Skills (n)` line from `claude plugin details skillsmith` with the folders under `skills/`. End state: `PASS: install: version <x>, <n> skills registered from the working tree`.

## Gotchas

- Without the isolated `CLAUDE_CONFIG_DIR`, the install lands in the user's real config. The helper refuses `~/.claude`; a hand-typed command does not.
- The plugin is copied into the isolated cache at install time. Edits made afterwards do not appear. Use a new `RUN_ID`.
- If you bump the version, installs of the old version in other configs do not update until the version differs.
- Claude's loader accepted a skill with invalid YAML frontmatter that the CLI rejected. A pass here does not prove `cli-discovery`.
