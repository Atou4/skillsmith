#!/usr/bin/env python3
"""Read-only snapshot of a Cloud Run project: what runs, what it costs to keep running, who calls it.

Usage:
  cloudrun_snapshot.py --project PROJECT --region REGION [--days 7] [--service-prefix PREFIX]

Prints services (scaling, ingress, traffic and tags), per-revision instance counts,
requests by status class, billable instance-hours, fixed-cost resources (load balancer
rules, reserved IPs, Cloud NAT), Cloud Scheduler jobs and the most-hit 4xx/5xx paths.
Ends with WARN findings. It never changes anything and never reads secrets.
Needs: gcloud (authenticated), python3. Exit 0 = report printed, 2 = could not read.
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

FINDINGS = []


def warn(msg):
    FINDINGS.append(msg)


def gcloud_json(args):
    try:
        out = subprocess.run(["gcloud"] + args + ["--format=json"], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    if out.returncode != 0:
        return None, out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "gcloud failed"
    try:
        return json.loads(out.stdout or "[]"), None
    except json.JSONDecodeError:
        return None, "unparseable gcloud output"


def token():
    out = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        print("cannot get an access token: run `gcloud auth login`", file=sys.stderr)
        sys.exit(2)
    return out.stdout.strip()


class Monitoring:
    def __init__(self, project):
        self.project = project
        self.tok = token()

    def series(self, metric_filter, start, end, period_s, aligner, group_by, reducer="REDUCE_SUM"):
        params = [
            ("filter", metric_filter),
            ("interval.startTime", start.strftime("%Y-%m-%dT%H:%M:%SZ")),
            ("interval.endTime", end.strftime("%Y-%m-%dT%H:%M:%SZ")),
            ("aggregation.alignmentPeriod", "%ds" % period_s),
            ("aggregation.perSeriesAligner", aligner),
            ("aggregation.crossSeriesReducer", reducer),
        ] + [("aggregation.groupByFields", g) for g in group_by]
        out, page = [], None
        while True:
            q = params + ([("pageToken", page)] if page else [])
            url = "https://monitoring.googleapis.com/v3/projects/%s/timeSeries?%s" % (
                self.project, urllib.parse.urlencode(q))
            req = urllib.request.Request(url, headers={
                "Authorization": "Bearer " + self.tok, "x-goog-user-project": self.project})
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.load(resp)
            except urllib.error.HTTPError as exc:
                raise RuntimeError("Monitoring API %s: %s" % (exc.code, exc.read()[:200]))
            out.extend(data.get("timeSeries", []))
            page = data.get("nextPageToken")
            if not page:
                return out


def value(point):
    v = point["value"]
    for k in ("doubleValue", "int64Value"):
        if k in v:
            return float(v[k])
    return 0.0


def labels(ts):
    d = dict(ts.get("resource", {}).get("labels", {}))
    d.update(ts.get("metric", {}).get("labels", {}))
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", required=True)
    ap.add_argument("--region", required=True)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--service-prefix", default="")
    a = ap.parse_args()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    since = now - timedelta(days=a.days)
    hours = a.days * 24
    print("Cloud Run snapshot  project=%s region=%s  window=%dd (to %s)\n" % (a.project, a.region, a.days, now.isoformat()))

    services, err = gcloud_json(["run", "services", "list", "--project", a.project, "--region", a.region])
    if services is None:
        print("cannot list services: " + err, file=sys.stderr)
        return 2
    services = [s for s in services if s["metadata"]["name"].startswith(a.service_prefix)]
    names = [s["metadata"]["name"] for s in services]

    # 1. Services, scaling and traffic.
    print("== Services ==")
    for s in services:
        tmpl = s["spec"]["template"]["metadata"].get("annotations", {})
        ann = s["metadata"].get("annotations", {})
        mn = tmpl.get("autoscaling.knative.dev/minScale", "0")
        mx = tmpl.get("autoscaling.knative.dev/maxScale", "?")
        cpu_always = tmpl.get("run.googleapis.com/cpu-throttling") == "false"
        spec = s["spec"]["template"]["spec"]
        lim = spec["containers"][0].get("resources", {}).get("limits", {})
        print("%s  min=%s max=%s concurrency=%s cpu=%s mem=%s billing=%s ingress=%s" % (
            s["metadata"]["name"], mn, mx, spec.get("containerConcurrency", "?"), lim.get("cpu", "?"),
            lim.get("memory", "?"), "instance-based" if cpu_always else "request-based",
            ann.get("run.googleapis.com/ingress", "?")))
        for t in s["status"].get("traffic", []):
            pct = t.get("percent", 0)
            rev = t.get("revisionName", "LATEST")
            tag = t.get("tag")
            print("    traffic %3s%%  %s%s" % (pct, rev, ("  tag=" + tag) if tag else ""))
            if tag:
                warn("%s: revision %s carries tag '%s' (%s%% traffic). A tagged revision keeps its own "
                     "min instances warm and billed; remove it with `gcloud run services update-traffic %s "
                     "--remove-tags %s --project %s --region %s` once it is no longer needed."
                     % (s["metadata"]["name"], rev, tag, pct, s["metadata"]["name"], tag, a.project, a.region))
        if s["status"].get("latestCreatedRevisionName") != s["status"].get("latestReadyRevisionName"):
            warn("%s: latest created revision %s is not ready (latest ready: %s). A deploy failed its startup."
                 % (s["metadata"]["name"], s["status"].get("latestCreatedRevisionName"),
                    s["status"].get("latestReadyRevisionName")))
    print()

    mon = Monitoring(a.project)
    svc_filter = lambda m: 'metric.type="run.googleapis.com/%s" AND resource.type="cloud_run_revision"' % m

    # 2. Instances held right now, per revision (last 30 minutes).
    print("== Instances per revision (mean, last 30 min) ==")
    try:
        ts = mon.series(svc_filter("container/instance_count"), now - timedelta(minutes=30), now, 1800,
                        "ALIGN_MEAN", ["resource.label.service_name", "resource.label.revision_name", "metric.label.state"])
        per_rev = {}
        for t in ts:
            l = labels(t)
            if l.get("service_name") not in names:
                continue
            key = (l["service_name"], l["revision_name"])
            per_rev.setdefault(key, {})[l.get("state", "?")] = sum(value(p) for p in t["points"]) / max(len(t["points"]), 1)
        serving = {}
        for s in services:
            for t in s["status"].get("traffic", []):
                serving[(s["metadata"]["name"], t.get("revisionName"))] = t.get("percent", 0)
        for (svc, rev), st in sorted(per_rev.items()):
            total = sum(st.values())
            if total < 0.05:
                continue
            pct = serving.get((svc, rev), 0)
            print("%s  %s  active=%.2f idle=%.2f  traffic=%s%%" % (svc, rev, st.get("active", 0), st.get("idle", 0), pct))
            if pct == 0 and total >= 0.5:
                warn("%s: revision %s gets 0%% traffic but holds %.1f instance(s). It is billed; usually a stale tag."
                     % (svc, rev, total))
    except RuntimeError as exc:
        print("  unavailable: %s" % exc)
    print()

    # 3. Requests and billable time over the window.
    print("== Requests by status class, last %dd ==" % a.days)
    req = Counter()
    try:
        for t in mon.series(svc_filter("request_count"), since, now, 3600, "ALIGN_DELTA",
                            ["resource.label.service_name", "metric.label.response_code_class"]):
            l = labels(t)
            if l.get("service_name") in names:
                req[(l["service_name"], l.get("response_code_class", "?"))] += sum(value(p) for p in t["points"])
        for svc in names:
            row = {k[1]: int(v) for k, v in req.items() if k[0] == svc}
            tot = sum(row.values())
            print("%s  total=%d  %s  (~%d/day)" % (svc, tot, "  ".join("%s=%d" % kv for kv in sorted(row.items())), tot / a.days))
            if tot and row.get("4xx", 0) / tot > 0.5:
                warn("%s: %d%% of requests are 4xx. Check the top paths below: often internet scanners, "
                     "sometimes a broken client." % (svc, 100 * row.get("4xx", 0) / tot))
            if tot and row.get("5xx", 0) / tot > 0.01:
                warn("%s: 5xx rate %.1f%% over %dd." % (svc, 100.0 * row.get("5xx", 0) / tot, a.days))
    except RuntimeError as exc:
        print("  unavailable: %s" % exc)
    print()
    print("== Billable instance time, last %dd ==" % a.days)
    try:
        bill = Counter()
        for t in mon.series(svc_filter("container/billable_instance_time"), since, now, 3600, "ALIGN_DELTA",
                            ["resource.label.service_name"]):
            l = labels(t)
            if l.get("service_name") in names:
                bill[l["service_name"]] += sum(value(p) for p in t["points"]) / 3600.0
        for svc in names:
            h = bill.get(svc, 0.0)
            reqs = sum(v for k, v in req.items() if k[0] == svc)
            print("%s  %.1f instance-hours  = %.2f instances on average" % (svc, h, h / hours))
            mn = next((int(s["spec"]["template"]["metadata"].get("annotations", {}).get(
                "autoscaling.knative.dev/minScale", "0")) for s in services if s["metadata"]["name"] == svc), 0)
            if h / hours > mn + 0.5 and reqs / max(hours, 1) < 100:
                warn("%s: averages %.1f billed instances with min=%d at under 100 requests/hour. "
                     "Look for tagged or extra revisions holding instances." % (svc, h / hours, mn))
    except RuntimeError as exc:
        print("  unavailable: %s" % exc)
    print()

    # 4. Fixed-cost resources that bill whatever the traffic.
    print("== Fixed-cost resources ==")
    rules, err = gcloud_json(["compute", "forwarding-rules", "list", "--project", a.project])
    if rules is None:
        print("  forwarding rules: unavailable (%s)" % err)
    else:
        print("  load balancer forwarding rules: %d %s" % (len(rules), [r["name"] for r in rules]))
        if rules:
            warn("%d forwarding rule(s): a global external load balancer bills a fixed hourly minimum "
                 "(about EUR 16/month for up to 5 rules) whatever the traffic." % len(rules))
    addrs, err = gcloud_json(["compute", "addresses", "list", "--project", a.project])
    if addrs is not None:
        print("  reserved IP addresses: %s" % [(x["name"], x.get("status")) for x in addrs])
        for x in addrs:
            if x.get("status") == "RESERVED":
                warn("address %s is reserved but unused: unused static IPs are billed." % x["name"])
    routers, err = gcloud_json(["compute", "routers", "list", "--project", a.project])
    if routers:
        nat = [r["name"] for r in routers if r.get("nats")]
        print("  Cloud NAT routers: %s" % nat)
        if nat:
            warn("Cloud NAT gateway(s) %s bill hourly." % nat)
    jobs, err = gcloud_json(["scheduler", "jobs", "list", "--project", a.project, "--location", a.region])
    if jobs is not None:
        print("  Cloud Scheduler jobs (%d; 3 free per billing account):" % len(jobs))
        for j in jobs:
            print("    %-45s %-14s %s" % (j["name"].split("/")[-1], j.get("schedule"), j.get("state")))
    print()

    # 5. Who gets errors: most-hit 4xx/5xx paths in the last 24h (sample).
    print("== Top 4xx/5xx paths, last 24h (sample of 1000) ==")
    svc_clause = " OR ".join('resource.labels.service_name="%s"' % n for n in names) or "true"
    flt = ('resource.type="cloud_run_revision" AND (%s) AND httpRequest.status>=400' % svc_clause)
    logs, err = gcloud_json(["logging", "read", flt, "--project", a.project, "--freshness=1d", "--limit=1000"])
    if logs is None:
        print("  unavailable: %s" % err)
    else:
        c = Counter()
        for e in logs:
            h = e.get("httpRequest", {})
            path = urllib.parse.urlsplit(h.get("requestUrl", "")).path
            path = re.sub(r"[0-9a-f]{8}-[0-9a-f-]{27}|\b\d{3,}\b", "<id>", path)
            c[(h.get("status"), h.get("requestMethod"), path)] += 1
        for (st, m, p), n in c.most_common(12):
            print("  %4d  %s %s %s" % (n, st, m, p))
    print()

    print("== Findings ==")
    if not FINDINGS:
        print("none")
    for f in FINDINGS:
        print("WARN " + f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
