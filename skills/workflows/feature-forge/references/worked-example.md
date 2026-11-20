# Worked example (fictional)

A completed sheet, shortened. The company, repos and paths are invented; the shape is what matters. Replace every value with your own from the stage 0 interview.

## Situation

Acme Boards sells team plans for a whiteboard app. Three repos must agree on how a team's subscription state is stored and read:

- `api` (backend functions and database rules) owns every privileged write.
- `web` (marketing site and checkout entry) starts the purchase.
- `app` (the product) only reads the team's plan and enforces limits.

The provider is a hosted-checkout payments service, decided before planning started. An earlier provider-agnostic plan exists with four issue files.

## Resolved values

| Token | Value |
|---|---|
| `<PLAN_ROOT>` | `/home/dev/acme/plans/team-billing` |
| `<PRIOR_PLAN>` | `/home/dev/acme/plans/team-billing/map.md` |
| `<ISSUE_FILES>` | `/home/dev/acme/plans/team-billing/issues/01-plan-shape.md` … `04-limits.md` |
| `<PROVIDER>` | the payments provider (hosted checkout, signed webhooks) |
| `<REPO_CORE>` | `/home/dev/acme/api` |
| `<REPO_ENTRY>` | `/home/dev/acme/web` |
| `<REPO_MANAGE>` | `/home/dev/acme/web` (billing page; same repo as entry here) |
| `<REPO_CONSUME>` | `/home/dev/acme/app` |
| `<ENTITY>` | Team |
| `<CONSTRAINTS>` | The mobile build of `app` may not show prices or link to web checkout (app store rules) |

Repo roles collapsed from four to three because entry and management live in the same repo.

## Skill availability

| Skill | Claude Code | Codex | Used in stage |
|---|---|---|---|
| `research` | yes | yes | 2 |
| `codebase-design` | yes | yes | 3 |
| `grilling` | yes | yes | 4 |
| `to-tickets` | yes | no: fallback, tickets by hand | 5 |
| design tool | yes | no: screenshots and wireframes | 6 |
| `create-verification-skill` | yes | yes | 8 |
| `blast-radius` | yes | yes | 10 |

## Stage outputs (abridged)

1. **Frame.** Issue 01 still valid; issue 02 (proration rules) answered by the provider's own proration; issue 03 needs revision because the provider's portal now handles card updates; issue 04 still valid. One standing decision invalidated: "we store card fingerprints" is dropped, the provider holds them.
2. **Provider facts** in `<PLAN_ROOT>/research/provider.md`: seven subscription states, webhook retries for 3 days with no ordering guarantee, a metadata field that carries the team ID through checkout, signature scheme documented with a timestamp tolerance.
3. **Contract** in `<PLAN_ROOT>/contract.md`: one `teams/{id}/billing` record is truth; internal enum `trialing | active | past_due | canceled`; two provider states (`incomplete`, `paused`) have no clean mapping and are named as such; idempotency key is the provider's event ID stored with the processed result; `app` reads billing through one server endpoint and caches for 60 seconds.
4. **Grilling** found one gap: a refund issued directly in the provider dashboard had no owning repo. Resolved: `api` handles the refund event and moves the team to `canceled` at period end.
5. **Tickets:** six vertical slices, three in `api`, two in `web`, one in `app`, each naming its contract section and evidence.
6. **Design:** checkout entry, billing page, past-due banner, over-limit state in `app`. Mobile build shows plan status without prices.
7. **Approval:** explicit sign-off on version 3 of the artboards.
8. **Harness** in `api`: a script that fires the same event twice, two events out of order, and one with a bad signature, and prints the billing record before and after each.
9. **Build:** one delegate per repo; `api` on the strongest model tier.
10. **Blast radius:** the enum mapping and the 60-second cache were traced; the cache was proven safe by running the harness while flipping a team to `past_due`.
11. **Security review:** webhook signature verified with the tolerance; no provider secret in `web` or `app` bundles; billing fields not writable from either client.
12. **Close out:** review and simplify per repo.
