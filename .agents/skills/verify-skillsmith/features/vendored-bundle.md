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

- **License and notices (offline).** `scripts/validate-skills.py` fails if any `vendor.json` entry lacks a `LICENSE` file or a `THIRD_PARTY_NOTICES.md` row naming the skill and its pinned commit.
- **Unmodified (network).** Run `verify.sh vendor`. It hashes every local file as a git blob and compares with upstream's tree at the pinned commit. End state: `PASS: vendor: <n> vendored skills byte-identical to their pinned upstream`. A modified, missing or extra file (other than `LICENSE`) fails with the file names in `artifacts/<RUN_ID>/vendor.txt`.
- **Install.** `verify.sh install` and `verify.sh discover` both list `better-motion`, `better-ui`, `emil-design-eng` and `ui-ux-pro-max`; the `ui-ux` plugin registers exactly those four.

## Gotchas

- Upstream moves often. On 2026-11-20 `better-ui` lost its motion guidance to a new `better-motion` skill; refreshing one without the other would have dropped content. Read upstream commit titles before refreshing.
- `ui-ux-pro-max` is about 3.7 MB. Its CSV data contains generic example paths such as `/Users/me/Desktop`; do not flag them as personal leaks.
- Refresh a vendored skill from upstream and update the notices table together; never edit the copy.
- The upstream repo for `ui-ux-pro-max` keeps the skill at `.claude/skills/ui-ux-pro-max`, not `skills/`.
