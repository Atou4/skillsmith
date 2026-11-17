# Scope

## In scope

- **`skills/meta/`**: skills about skills. Finding, vetting, installing, auditing, routing and maintaining them, plus orchestration skills that decide which other skill runs next and keep resumable state. Written and supported by the maintainer.
- **`skills/ui-ux/`**: a separate bucket of third-party UI/UX skills, included unmodified so they install together with the meta skills. Only MIT-or-similarly-permissive skills, each keeping its upstream `LICENSE`, each listed in `THIRD_PARTY_NOTICES.md` with source and pinned commit.

## Out of scope

- Other domain skills (research, Flutter, marketing and so on) unless they are added as a clearly labelled third-party bucket under the same rules.
- Third-party skills without a license that allows redistribution. Link to the source instead.
- Anything tied to one person's project, employer or private data.

## Growing

A new bucket is added only for skills the maintainer wrote and can support, or for third-party skills that meet the rules above. Each addition updates `plugin.json` and passes `scripts/validate-skills.py`. Vendored skills are refreshed from upstream, never edited here.
