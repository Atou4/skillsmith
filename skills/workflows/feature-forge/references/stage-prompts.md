# Stage prompt templates

Fill every placeholder from the stage 0 interview, then write the result
to `<PLAN_ROOT>/EXECUTION-STEPS.md`. Resolve all paths absolute. A sheet
with an unresolved placeholder is a draft.

## Placeholders

| Token | Meaning |
| --- | --- |
| `<PLAN_ROOT>` | Where the plan and its artifacts live |
| `<PRIOR_PLAN>` | Existing map/spec/plan file, if any |
| `<ISSUE_FILES>` | Absolute path per existing issue file, one per line |
| `<PROVIDER>` | The external service |
| `<REPO_CORE>` | Repo owning privileged mutations (functions, backend) |
| `<REPO_ENTRY>` | Repo where the user-facing flow starts |
| `<REPO_MANAGE>` | Repo where the result is administered |
| `<REPO_CONSUME>` | Repo that only reads the resulting state |
| `<ENTITY>` | The thing the integration attaches to (Workspace, Org, Team) |
| `<CONSTRAINTS>` | Store, regulatory, or residency rules that bind the design |

Repo roles are a starting shape, not a fixed count. Collapse or expand
them to match the actual system.

---

## Stage 1 — Frame against prior art

Skill: none (plain read). Optional: `why` for decision history.

```
Read these in full:
<PRIOR_PLAN>
<ISSUE_FILES>

The provider is now decided: <PROVIDER>. <one line on the commercial or
operational shape: billing period, where it is purchased, what stays
system of record>.

For each issue file tell me: (a) still valid as written, (b) needs
revision now the provider is known, or (c) already answered by the
<PROVIDER> decision. One line of reasoning each, as a table.

Then separately: list any standing decision in <PRIOR_PLAN> that
<PROVIDER> actually invalidates. Pay attention to anything assuming we
own responsibilities <PROVIDER> takes over, or vice versa.

Do not rewrite any file yet.
```

## Stage 2 — Provider facts

Skill: `research`

```
Use the research skill.

Subject: <PROVIDER> for <the specific use case>, with <system of record>
as source of truth and <REPO_CORE> owning all privileged mutations.

Primary sources only (<PROVIDER> docs, API reference, changelog), with
citations. Answer:

- Responsibility boundary. What <PROVIDER> owns versus what we own.
  What that removes from our scope versus the alternatives.
- Entry flow. Hosted versus embedded. What custom data can be attached
  to a request so a callback maps back to a <ENTITY>.
- Callbacks and webhooks. Exact event set for the lifecycle we care
  about. Signature verification scheme. Retry and redelivery behavior.
  Ordering guarantees. Whether events can arrive duplicated or out of
  order.
- Provider-side portal. What the user can self-serve there, and what
  needs our own UI.
- State model. The provider status enum and its exact transitions.
- Constraints. Test-mode fidelity, rate limits, API stability.

Write to: <PLAN_ROOT>/research/<provider>.md
```

## Stage 3 — The contract

Skill: `codebase-design`. Support: `domain-modeling`.

```
Use the codebase-design skill.

Design the seam between these repos for the <PROVIDER> integration.

  <REPO_ENTRY>    hosts the user-facing entry flow
  <REPO_CORE>     owns request creation, callback ingestion, state
                  transitions, reconciliation
  <REPO_MANAGE>   administers the result
  <REPO_CONSUME>  consumes resulting state only. Never initiates.
                  <CONSTRAINTS>

Ground in:
  <PRIOR_PLAN>  (standing decisions)
  <relevant issue files>
  <PLAN_ROOT>/research/<provider>.md

Decide and write, as one authoritative contract:

1. The document or table shape that is truth for a <ENTITY>'s state.
   Field names, types, which are provider-mirrored versus ours.
2. Our internal status enum, and the exact mapping from <PROVIDER>'s
   enum to ours. Name every state with no clean mapping.
3. How a request is bound to a <ENTITY> before <PROVIDER> knows about
   it, and how the callback resolves back to that <ENTITY> with no
   ambiguity.
4. The idempotency scheme for callback processing. What the key is,
   where it is stored, what happens on duplicate and out-of-order
   delivery.
5. How <REPO_MANAGE> and <REPO_CONSUME> read the resulting state.
   Server-authorized only. Specify read path, caching, staleness rules.
6. Per repo: what it owns and what it is forbidden from writing.

Output to: <PLAN_ROOT>/contract.md
```

## Stage 4 — Grill the contract

Skill: `grilling`

```
Use the grilling skill.

Target: <PLAN_ROOT>/contract.md

Grill hardest on failure modes that cost money or trust:

- Callback arrives twice. Arrives out of order. Never arrives despite
  the operation succeeding on <PROVIDER>'s side.
- User completes the flow, abandons before redirect, then appears on
  <REPO_CONSUME>.
- Renewal or retry fails. Credentials expire mid-term. A human acts
  directly in the <PROVIDER> dashboard, outside our flow. Reversal or
  dispute.
- Two actors act on the same <ENTITY> concurrently.
- A <ENTITY> drops to a lower tier while over that tier's limits. What
  happens to data already there.
- Someone replays a captured callback payload at our endpoint.
- Our write fails after <PROVIDER> has already committed.

For each, make me answer what the system does. Do not accept "we would
handle that" without a named state and a named owning repo.
```

## Stage 5 — Contract to issues

Skill: `to-tickets` (or `to-feature`)

```
Use the to-tickets skill.

Source: <PLAN_ROOT>/contract.md

Break it into independently-grabbable issues as vertical slices, one per
repo where possible. Each issue names: the repo absolute path, the
contract section it implements, its acceptance evidence, and what must
land before it. Sequence so each ends in something verifiable on its
own.
```

## Stage 6 — Design

Skill: `design`. Support: `prototype`.

```
Use the design skill.

Artboards for the <PROVIDER> integration:
- <REPO_ENTRY>: the entry flow and whatever precedes it
- <REPO_MANAGE>: management, history, and the over-limit / downgrade /
  failure states
- <REPO_CONSUME>: how the resulting state appears, with <CONSTRAINTS>

Reuse the existing design language in <REPO_ENTRY> and <REPO_MANAGE>
rather than introducing new primitives.
```

## Stage 7 — Approval gate

No skill. Hard stop. Explicit sign-off on the artboards before any repo
is touched.

## Stage 8 — Verification harness

Skill: `create-verification-skill`. Run from `<REPO_CORE>`.

```
Use the create-verification-skill skill.

Target repo: <REPO_CORE>

Critical capability: drive simulated <PROVIDER> callback events at our
handler and prove idempotent, correctly-ordered processing against real
local state.

Cover explicitly, not just the happy path:
- duplicate delivery of the same event
- out-of-order delivery
- signature or auth verification failure

Evidence must include the stored state before and after, not just a 200
response.
```

Repeat per repo as each gets built.

## Stage 9 — Build

Skill: none required. If the user asked for a build-discipline skill
(for example `poteto-mode`), invoke it first.

```
Spawn one delegate per repo against the approved contract at
<PLAN_ROOT>/contract.md

Model tiers:
  strongest -> <REPO_CORE>
               idempotency, state transitions, reconciliation, enum
               mapping
  standard  -> <REPO_ENTRY>, <REPO_MANAGE>, <REPO_CONSUME>

Each delegate gets: its repo absolute path, the contract sections it
owns, the sections it is forbidden from writing, and the verification
skill in its repo. Review every diff yourself. Do not accept a
delegate's own "done".
```

## Stage 10 — Blast-radius the seams

Skill: `blast-radius`

```
Use the blast-radius skill on <diff or file:line>.

Context: <PROVIDER> integration. <system of record> is truth. A wrong
state read silently grants or revokes authority across <REPO_CONSUME>
and <REPO_MANAGE>.

Find the one fact this is safe because of, and prove it by running real
code against <the local harness from stage 8>. Do not hand back a
writeup alone.
```

Run on, at minimum: the enum mapping, anything touching money, currency,
or precision, and the state read path.

## Stage 11 — Security review

Skill: `security-review`

```
Run a security review across all repos in play.

Check specifically:
- callback signature or token verification present and correct
- <PROVIDER> secrets absent from every client bundle
- no client-writable path to the fields carrying authority
- access rules audited against the ownership table in
  <PLAN_ROOT>/contract.md
```

## Stage 12 — Close out

Skills: `code-review`, `simplify`. Per repo.
