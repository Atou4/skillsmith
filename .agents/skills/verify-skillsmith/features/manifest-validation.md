# Manifest validation

A contributor changes a skill or the plugin manifest and gets a clear failure for broken frontmatter, a name that does not match its folder, an unlisted skill, or a personal path, before it can be pushed or released.

## Sub-features

- `validate-frontmatter` checks `name`, `description` and the name-equals-folder rule.
- `validate-yaml` fails frontmatter that is not valid YAML (needs PyYAML).
- `validate-manifest` checks that `plugin.json` lists every skill and nothing missing.
- `validate-leaks` rejects home-directory paths and email addresses in SKILL.md files.
- `validate-ci` runs the same checks on every push and pull request.

## How to get to it (user POV)

- Run `python3 scripts/validate-skills.py` (or `uv run --with pyyaml python scripts/validate-skills.py`).
- Run `claude plugin validate .`.
- Push to `main` or open a pull request to trigger `.github/workflows/validate.yml`.

## Driving it with verify.sh

Preconditions:

- `verify.sh doctor` passes.

- **Positive.** Run `verify.sh static`. `artifacts/<RUN_ID>/validate-skills.txt` starts with `OK:` and `plugin-validate.txt` contains `Validation passed`. A missing-icon warning is expected and does not fail.
- **Negative (YAML).** Copy the repo to a scratch directory, put an unquoted `: ` inside one skill's `description`, and run `uv run --with pyyaml python scripts/validate-skills.py` there. It exits 1 and names the skill with `frontmatter is not valid YAML`.
- **Negative (manifest).** In the same scratch copy, remove one skill from `plugin.json`. The validator exits 1 with `plugin.json does not list skill`.
- **CI parity.** After pushing, `gh run list --repo Atou4/skillsmith --limit 1` shows `success` for the pushed commit.

## Gotchas

- Without PyYAML the validator skips the strict YAML check and can pass a skill the CLI will reject. Use `uv run --with pyyaml`; CI installs it explicitly.
- Do the negative tests in a scratch copy, never in the repo.
- The leak check matches the literal strings `/Users/` and `@gmail.com` in SKILL.md files only. It does not scan scripts or vendored data.
- `claude plugin validate` checks the plugin directory; it does not check that the `skills` CLI can parse each skill.
