#!/usr/bin/env python3
"""Read-only post-deploy check for Cloud Run services. Exit 0 = all PASS, 1 = a FAIL, 2 = could not read.

Usage:
  verify_deploy.py --project PROJECT --region REGION --services api,work [--health-url URL] [--minutes 15]

Checks, per service: Ready condition, latest created revision is the latest ready one (no failed
startup), 100% of traffic on that revision, no traffic tags left behind, and error-level log entries
in the last N minutes. Optionally GETs a health URL and expects HTTP 200. Changes nothing.
"""
import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request

results = []


def check(ok, msg):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + msg)


def gcloud_json(args):
    out = subprocess.run(["gcloud"] + args + ["--format=json"], capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "gcloud failed")
    return json.loads(out.stdout or "null")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", required=True)
    ap.add_argument("--region", required=True)
    ap.add_argument("--services", required=True, help="comma-separated Cloud Run service names")
    ap.add_argument("--health-url")
    ap.add_argument("--minutes", type=int, default=15)
    a = ap.parse_args()

    for svc in [s.strip() for s in a.services.split(",") if s.strip()]:
        try:
            d = gcloud_json(["run", "services", "describe", svc, "--project", a.project, "--region", a.region])
        except RuntimeError as exc:
            print("cannot read %s: %s" % (svc, exc), file=sys.stderr)
            return 2
        st = d["status"]
        ready = next((c for c in st.get("conditions", []) if c.get("type") == "Ready"), {})
        check(ready.get("status") == "True", "%s: service Ready (%s)" % (svc, ready.get("message", ready.get("status"))))
        created, latest = st.get("latestCreatedRevisionName"), st.get("latestReadyRevisionName")
        check(created == latest, "%s: latest created revision %s is ready (latest ready: %s)" % (svc, created, latest))
        traffic = st.get("traffic", [])
        full = [t for t in traffic if t.get("percent") == 100]
        on_latest = bool(full) and (full[0].get("revisionName") == latest or full[0].get("latestRevision"))
        check(on_latest, "%s: 100%% of traffic on %s (traffic: %s)" % (
            svc, latest, ", ".join("%s=%s%%" % (t.get("revisionName", "LATEST"), t.get("percent", 0)) for t in traffic)))
        tags = ["%s=%s" % (t["tag"], t.get("revisionName")) for t in traffic if t.get("tag")]
        check(not tags, "%s: no traffic tags left behind%s" % (svc, (" (found: %s)" % ", ".join(tags)) if tags else ""))
        flt = ('resource.type="cloud_run_revision" AND resource.labels.service_name="%s" AND severity>=ERROR' % svc)
        try:
            logs = gcloud_json(["logging", "read", flt, "--project", a.project,
                                "--freshness=%dm" % a.minutes, "--limit=20"]) or []
        except RuntimeError as exc:
            print("cannot read logs for %s: %s" % (svc, exc), file=sys.stderr)
            return 2
        check(not logs, "%s: no ERROR log entries in the last %d min (%d found)" % (svc, a.minutes, len(logs)))
        for e in logs[:3]:
            msg = e.get("textPayload") or json.dumps(e.get("jsonPayload", {}))[:400]
            print("     %s %s" % (e.get("timestamp", "")[:19], " ".join(str(msg).split())[:160]))

    if a.health_url:
        try:
            with urllib.request.urlopen(urllib.request.Request(a.health_url, method="GET"), timeout=30) as r:
                code = r.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except (urllib.error.URLError, OSError) as exc:
            code = str(exc)
        check(code == 200, "health %s -> %s" % (a.health_url, code))

    ok = all(results)
    print("\n%s: %d checks, %d failed" % ("OK" if ok else "NOT OK", len(results), results.count(False)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
