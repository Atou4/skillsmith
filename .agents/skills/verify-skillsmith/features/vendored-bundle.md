# Vendored UI/UX bundle

The three third-party UI/UX skills ship unmodified with their upstream licenses, credited in the notices file, so redistribution stays compliant.

## Sub-features

- `bundle-license` each vendored skill folder contains an upstream `LICENSE`.
- `bundle-notices` each vendored skill has a row in `THIRD_PARTY_NOTICES.md` with source, author and pinned commit.
- `bundle-unmodified` the folder matches the pinned upstream commit.

## How to get to it (user POV)

- Open `skills/ui-ux/<skill>/` and `THIRD_PARTY_NOTICES.md`.
- Install the bundle with the rest of the plugin; the skills appear alongside the meta skills.

## Driving it with verify.sh

Preconditions:

- `verify.sh doctor` passes.
- Network access and `gh` for the unmodified check.

- **License and notices (offline).** For each folder under `skills/ui-ux/`, run `test -f skills/ui-ux/<skill>/LICENSE` and `grep -c '`<skill>`' THIRD_PARTY_NOTICES.md`. Each file exists and each skill appears once.
- **Unmodified (network).** Clone the upstream repo at the pinned commit from the notices table into a scratch directory, then run `diff -r <upstream skill folder> skills/ui-ux/<skill>`. The only difference allowed is the added `LICENSE` file.
- **Install.** `verify.sh install` and `verify.sh discover` both list `better-ui`, `emil-design-eng` and `ui-ux-pro-max`.

## Gotchas

- `verify.sh` does not automate the license, notices or unmodified checks yet; they are manual commands.
- `ui-ux-pro-max` is about 3.7 MB. Its CSV data contains generic example paths such as `/Users/me/Desktop`; do not flag them as personal leaks.
- Refresh a vendored skill from upstream and update the notices table together; never edit the copy.
- The upstream repo for `ui-ux-pro-max` keeps the skill at `.claude/skills/ui-ux-pro-max`, not `skills/`.
