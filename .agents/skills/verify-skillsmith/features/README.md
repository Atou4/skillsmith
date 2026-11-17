# skillsmith verification map

This directory is the maintained source for verifying the user-facing behavior of skillsmith. Read this index, then use the feature file that matches your change as the recipe.

## Baseline preconditions

- Work from the repo root, `Atou4/skillsmith`, with a clean understanding of which files are uncommitted (`git status --short`). The install route reads the working tree.
- `claude`, `npx`, `python3` are on `PATH`. `uv` is preferred so PyYAML is available for strict frontmatter checks.
- Run through `.agents/skills/verify-skillsmith/scripts/verify.sh`, which isolates `CLAUDE_CONFIG_DIR`.
- Run `verify.sh doctor` and require the expected repo path, version and skill list.
- Never drive the user's real Claude config or install into their real skill folders.

## Driving conventions

- Treat every command as literal. Keep flags unchanged.
- Compare the set of skill names, not their count.
- Use `RUN_ID` to group a run's evidence.
- Cleanup removes the isolated config only. Do not remove `artifacts/`.

## Proof and skip reporting

- Proof for a step is its `PASS:` line in `artifacts/<RUN_ID>/summary.txt` plus the raw output file named in the feature.
- Record the feature ID with every artifact.
- Report an unreachable path with the attempted command and the unmet precondition.
- Do not report a skipped entry point as verified through a different path.

## Features

| Feature | File | Covers |
|---|---|---|
| `plugin-install` | [plugin-install.md](plugin-install.md) | Claude Code plugin install from the working tree |
| `cli-discovery` | [cli-discovery.md](cli-discovery.md) | `npx skills` finds exactly the repo's skills |
| `manifest-validation` | [manifest-validation.md](manifest-validation.md) | Validator, strict YAML, plugin manifest, CI parity |
| `skill-audit` | [skill-audit.md](skill-audit.md) | The audit script on a known-bad fixture |
| `vendored-bundle` | [vendored-bundle.md](vendored-bundle.md) | Third-party UI/UX skills keep licenses and notices |

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible behavior. It then uses exactly four H2 sections in this order: `Sub-features`, `How to get to it (user POV)`, `Driving it with verify.sh`, `Gotchas`.
