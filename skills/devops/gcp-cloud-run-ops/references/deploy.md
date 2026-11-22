# Deploy, shift, roll back

Examples use an invented project `acme-shop-staging` / `acme-shop-production`, region
`europe-west1`, services `acme-shop-<env>-worker` and `acme-shop-<env>-api` and image `shop-api`.
Replace them with the values from step 1 of the skill. If the repo has its own deploy script, use
it and only borrow the checks below.

## Once per machine

```bash
gcloud auth login
gcloud auth configure-docker europe-west1-docker.pkg.dev
```

## 1. Record the rollback target

```bash
for s in worker api; do gcloud run services describe acme-shop-production-$s \
  --project acme-shop-production --region europe-west1 --format='yaml(status.traffic)'; done
```

Note the `revisionName` with `percent: 100` for each service. The first entry of the list is not
always it: a tagged 0% revision can come first.

## 2. Build and push, get the digest

```bash
SHA=$(git rev-parse HEAD)
REPO=europe-west1-docker.pkg.dev/acme-shop-production/containers
docker build --platform linux/amd64 -t $REPO/shop-api:$SHA .   # Cloud Run runs amd64
docker push $REPO/shop-api:$SHA
DIGEST=$(gcloud artifacts docker images describe $REPO/shop-api:$SHA --format='value(image_summary.digest)')
echo $DIGEST    # sha256:<64 hex>
```

## 3. Migrations (only if the release has them)

Run them before the deploy, with the project's migration tool and the database URL read inside a
subshell. They must be backward compatible (add, do not rename or drop), because the old revision
keeps serving until the shift and is the rollback target after it.

## 4. Create revisions without traffic

Deploy in dependency order (a service others call goes first). `--no-traffic` creates the revision
and runs its startup probe while users stay on the old one. It changes only the image; other
settings are kept.

```bash
for s in worker api; do
  gcloud run deploy acme-shop-production-$s --project acme-shop-production --region europe-west1 \
    --image $REPO/shop-api@$DIGEST --no-traffic --quiet
done
```

If a revision fails its startup probe the command fails and nothing changed for users. Read that
revision's logs (diagnose.md) and fix; never shift traffic to it by hand.

`--no-traffic` is refused on the very first deploy of a new service: that one gets 100% directly.

## 5. Optional: smoke-test the candidate before users see it

```bash
gcloud run services update-traffic acme-shop-staging-api --project acme-shop-staging \
  --region europe-west1 --update-tags candidate=LATEST
# URL: https://candidate---<service-url-host>  (add an identity token if the service is private)
curl -s -H "Authorization: Bearer $(gcloud auth print-identity-token)" https://candidate---.../health
```

This needs ingress that allows the `run.app` URL; with load-balancer-only ingress, smoke-test on
staging instead. The next step clears the tag.

## 6. Shift traffic and clear tags (production: ask first)

```bash
for s in worker api; do
  gcloud run services update-traffic acme-shop-production-$s --project acme-shop-production \
    --region europe-west1 --to-latest --clear-tags --quiet
done
```

`--to-latest` also undoes an earlier pin from a rollback or `--no-traffic` deploy, so future deploys
route normally. Gradual alternative: `--to-revisions NEW_REVISION=10`, watch errors and latency,
then the command above.

## 7. Verify

```bash
python3 -I <skill>/scripts/verify_deploy.py --project acme-shop-production --region europe-west1 \
  --services acme-shop-production-worker,acme-shop-production-api \
  --health-url https://api.example.com/health
```

Must exit 0. ERROR lines right after a shift can come from the old revision draining: read them.

## Roll back

```bash
gcloud run services update-traffic acme-shop-production-api --project acme-shop-production \
  --region europe-west1 --to-revisions REVISION_FROM_STEP_1=100 --quiet
```

Do it for every service of the release, in reverse dependency order, then run step 7. Seconds, no
build. The database does not roll back. The service is now pinned to that revision until a later
deploy shifts with `--to-latest`.

## Record

Commit, image digest, new revisions, rollback targets and time, wherever the team keeps releases
(changelog, release notes, git tag). Keep raw deploy output out of the repository if it contains
URLs or identities you do not want published.
