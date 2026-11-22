# Scope

skillsmith is a marketplace of skill packs. Each pack is one plugin that users install separately.

## In scope

- **`skills/meta/` (plugin `skillsmith`)**: skills about skills. Finding, vetting, installing, auditing, syncing, update-checking and routing. Written and supported by the maintainer.
- **`skills/workflows/` (plugin `workflows`)**: multi-step engineering workflows that coordinate other skills, such as integrating a service across several repos.
- **Stack packs**: skills for one framework, language, cloud or infrastructure area, either written by the maintainer or vendored under the third-party rules below. They are grouped by what the reader is doing, one pack per group:

  | Pack | What goes in it | Example skills |
  |---|---|---|
  | `frontend` | Browser UI code and its tooling | `react-...`, `nextjs-...`, `tailwind-...` |
  | `backend` | Server code, APIs and databases | `node-...`, `python-...`, `postgres-...` |
  | `mobile` | Phone and tablet apps | `flutter-...`, `react-native-...`, `swiftui-...` |
  | `infra` | Cloud services and provisioning | `gcp-...`, `aws-...`, `firebase-...`, `terraform-...` |
  | `devops` | Build, ship and run: pipelines, containers, observability | `github-actions-...`, `docker-...`, `kubernetes-...` |

  A skill goes where its reader works, not where its technology is from: a Flutter CI pipeline is `devops`, Flutter widget performance is `mobile`. A pack is published when its first skill is finished (see Growing). `mobile` is published; `devops` exists only as an empty reserved folder (`skills/devops/.gitkeep`) with no plugin; `frontend`, `backend` and `infra` do not exist yet.
- **Third-party packs** (for example `skills/ui-ux/`): skills by other authors, included unmodified so they install together. Only licenses that allow redistribution (MIT, Apache-2.0, BSD); each keeps its upstream `LICENSE`, is pinned in `vendor.json` and credited in `THIRD_PARTY_NOTICES.md`.

## Out of scope

- Third-party skills without a license that allows redistribution. Link to the source instead.
- Edited copies of third-party skills. Vendored skills are refreshed from upstream, never changed here.
- Anything tied to one person's project, employer or private data. Examples use invented names and paths.
- One-off prompts that are not repeatable workflows.

## Growing

Add a pack only when there is at least one finished skill for it; empty placeholder packs are not published. Each addition goes through `scripts/scaffold.py` and passes `scripts/validate-skills.py`. See [`CONTRIBUTING.md`](CONTRIBUTING.md).
