# Troubleshooting

If users are hurt right now, roll back first ([deploy.md](deploy.md#roll-back)), then investigate.
Note the time, service and revision. Every check below is read-only.

| Symptom | Likely cause | Check | Fix |
|---|---|---|---|
| Deploy fails creating a revision | Container not listening on `0.0.0.0:$PORT`, start slower than the startup probe allows, crash at boot, unreadable secret, image built for arm64 | `gcloud run revisions describe REV --format='yaml(status.conditions)'`, then that revision's ERROR logs | Users are unaffected. Fix and redeploy; build with `--platform linux/amd64` |
| Health fails after the shift | New revision unhealthy (database, secret, configuration) | ERROR logs of the new revision vs the old | Roll back, then investigate |
| HTTP 503 under load | `max_instances` reached | 5xx recipe; request rate vs usual | Raise the maximum only within downstream limits (database connections = instances x pool size); ask |
| HTTP 500 "no available instance" in a burst | Burst outran cold starts (`min` 0) | `container/instance_count`, startup times | A warm minimum, or faster startup |
| Slow first request after a quiet period | Cold start | Startup recipe; `min_instances` | `min_instances` 1 (costs one idle instance), or speed up startup (lazy initialisation, smaller image, startup CPU boost) |
| Revision will not start after a secret change | Runtime service account cannot read the secret, or wrong name/version | Revision conditions and logs | Grant `secretmanager.secretAccessor` on that secret (through IaC if managed there) |
| Old secret value still in use | Instances read secrets at start | When the serving revision started | Deploy a new revision (the same digest is fine) |
| Bill higher than traffic explains | Tagged revision holding minimum instances; unused reserved IP; LB minimum; instance-based billing | `cloudrun_snapshot.py` findings | Clear tags (ask in production); see the SKU table in diagnose.md |
| Many 4xx on odd paths | Internet scanners | Top paths in the snapshot | Nothing, unless they hit real routes; then Cloud Armor |
| `run.app` URL refuses requests | Ingress set to internal or load-balancer only | `services describe ... ingress` | By design: use the load balancer or domain |
| Permission denied running a command | Your account lacks a role | The error names the permission | Ask the project admin; do not route around it |
| Scheduler job failing | Target error, or the invoker identity lacks `run.invoker` | Scheduler recipe, target service logs | Fix the cause; jobs retry on their schedule |

## Never

- Shift traffic to a revision that failed its startup probe.
- Print or paste a secret value or a database URL with credentials.
- Change Terraform-managed settings with `gcloud run services update`.
- Delete revisions, images or secret versions as part of a fix; disable or route away instead.
