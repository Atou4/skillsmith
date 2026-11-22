# Diagnose: cost, traffic, errors

Read-only. Start with the snapshot; use the recipes for what it does not cover.

```bash
python3 -I <skill>/scripts/cloudrun_snapshot.py --project PROJECT --region REGION --days 7
```

## Reading the snapshot

| Section | Healthy | Look closer when |
|---|---|---|
| Services | one traffic line per service at 100%, no `tag=` | a tag, or several traffic lines nobody planned |
| Instances per revision | the serving revision holds about `min` instances when idle | a 0%-traffic revision holds instances (stale tag) |
| Requests | 2xx dominant | 4xx above 50% (scanners or a broken client), 5xx above 1% |
| Billable instance time | average close to `min` at low traffic | average well above `min` with little traffic |
| Fixed-cost | only resources you meant to have | an IP `RESERVED` but unused, a NAT gateway nobody needs |
| Top paths | scanner noise (`/.env`, `/wp-login.php`, `*credentials*.json`) all 404 | a real route in the top 4xx/5xx |

Scanners probing a public IP are normal and cheap. They matter only if they reach real routes or
grow in volume; then consider a Cloud Armor policy.

## Billing SKUs (Billing > Reports, group by SKU, filter to the project)

| SKU (names vary slightly by region tier) | Driven by | Lever |
|---|---|---|
| Services Min Instance CPU / Memory (request-based billing) | idle warm instances: `min_instances`, and any tagged revision with its own minimum | clear stale tags; choose `min` deliberately |
| Services CPU / Memory (request-based billing) | time spent serving requests | traffic, latency of slow endpoints |
| Services CPU / Memory (instance-based billing) | every second an instance is up | switch to request-based if the service does no background work |
| Cloud Load Balancer Forwarding Rule Minimum Global | a global external load balancer (fixed hourly minimum) | none while you need the LB |
| Network Internet Data Transfer Out | response bytes | compression, caching |
| Secret version replica storage | enabled secret versions | disable versions after rotation |
| Artifact Registry Storage | stored images | a cleanup policy for old digests |
| Cloud Scheduler Jobs | jobs beyond the free allowance per billing account | merge or drop unneeded jobs |

Monthly cost of one idle warm instance is roughly `idle_cpu_rate x vCPU x 2.6M s + idle_mem_rate x
GiB x 2.6M s`; take the rates from the Cloud Run pricing page for your region tier, or divide a
billing line by its usage. Money needs the Billing report (billing-account access); the snapshot
shows the drivers. Ask the user for the report if you cannot read it.

## Log recipes

```bash
# Errors of one service / one revision
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE" AND severity>=ERROR' --project PROJECT --freshness=1h --limit=20
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.revision_name="REVISION" AND severity>=ERROR' --project PROJECT --freshness=1h
# 5xx with path and latency
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE" AND httpRequest.status>=500' --project PROJECT --freshness=1d --format='value(timestamp,httpRequest.status,httpRequest.requestUrl,httpRequest.latency)'
# Slow requests
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE" AND httpRequest.latency>"2s"' --project PROJECT --freshness=1d --format='value(timestamp,httpRequest.latency,httpRequest.requestUrl)'
# Startup probe results (cold-start time = attempts x period)
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE" AND textPayload:"STARTUP" AND textPayload:"succeeded"' --project PROJECT --freshness=7d --limit=10 --format='value(timestamp,textPayload)'
# Cloud Scheduler failures
gcloud logging read 'resource.type="cloud_scheduler_job" AND severity>=ERROR' --project PROJECT --freshness=1d
# Who changed Cloud Run, and when (admin activity audit log)
gcloud logging read 'logName:"cloudaudit.googleapis.com%2Factivity" AND protoPayload.serviceName="run.googleapis.com"' --project PROJECT --freshness=7d --format='value(timestamp,protoPayload.authenticationInfo.principalEmail,protoPayload.methodName,protoPayload.resourceName)'
```

## Metrics beyond the snapshot

Cloud Monitoring API: `GET https://monitoring.googleapis.com/v3/projects/PROJECT/timeSeries`, bearer
token from `gcloud auth print-access-token`, header `x-goog-user-project: PROJECT`
(`cloudrun_snapshot.py` is a worked example). Metric types under `run.googleapis.com/`:
`request_count`, `request_latencies`, `container/instance_count` (label `state`: active, idle),
`container/billable_instance_time`, `container/startup_latencies`, `container/cpu/utilizations`,
`container/memory/utilizations`. Use `ALIGN_DELTA` for counters, `ALIGN_MEAN` or
`ALIGN_PERCENTILE_95` for gauges and distributions. For standing alerts, use the
`cloud-run-alert-configuration` skill and keep them in infrastructure-as-code.
