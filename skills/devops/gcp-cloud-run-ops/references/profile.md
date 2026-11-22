# Optional project profile: `.cloud-run-ops.json`

A small file at the repository root that records the values this skill otherwise has to discover.
It holds names only, never secrets. Commit it so every agent and teammate uses the same targets.

```json
{
  "environments": [
    {
      "name": "staging",
      "project": "acme-shop-staging",
      "region": "europe-west1",
      "services": ["acme-shop-staging-worker", "acme-shop-staging-api"],
      "health_url": "https://api-staging.example.com/health",
      "production": false
    },
    {
      "name": "production",
      "project": "acme-shop-production",
      "region": "europe-west1",
      "services": ["acme-shop-production-worker", "acme-shop-production-api"],
      "health_url": "https://api.example.com/health",
      "production": true
    }
  ],
  "deploy_command": "infra/scripts/deploy.sh {env} {digest} --shift-traffic",
  "notes": "Worker deploys before the API. Migrations: see docs/deployment.md."
}
```

| Field | Meaning |
|---|---|
| `services` | In deploy order: a service that others depend on comes first. |
| `health_url` | Reached through the public entry point (load balancer or domain), not the `run.app` URL when ingress is restricted. |
| `production` | `true` makes every mutating step wait for the user's explicit yes. |
| `deploy_command` | The repo's own deploy script, if any; the skill prefers it over the generic sequence. |
| `notes` | Project rules the agent must follow (migration order, extra gates). |

If Terraform declares the same values, Terraform wins: fix the profile in the same change.
