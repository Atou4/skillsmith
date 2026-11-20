#!/usr/bin/env python3
"""Read-only check: have installed or vendored skills changed upstream on GitHub?

Usage:
  check_updates.py --lock [PATH]       skills installed by the skills CLI (default ~/.agents/.skill-lock.json)
  check_updates.py --vendor PATH       a repo's vendor.json of copied third-party skills
Options:
  --verify-local       with --vendor: also prove each local copy is byte-identical to upstream at its
                       pinned commit (files the repo added, such as LICENSE, are allowed extras)
  --only NAME[,NAME]   check only these skills
  --fail-on-changes    exit 1 when anything changed (for CI)

Compares the git tree hash of each skill folder with the folder at the upstream default branch.
Sends only public repo names and paths to api.github.com. Uses GITHUB_TOKEN or GH_TOKEN when set
(recommended: GITHUB_TOKEN=$(gh auth token) to avoid the 60-requests-per-hour anonymous limit).
Never modifies files. Stdlib only.
"""
import argparse
import hashlib
import json
import os
import posixpath
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
_cache = {}


def get(path):
    if path in _cache:
        return _cache[path]
    req = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json", "User-Agent": "skill-update-check"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        data = {"_error": f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        data = {"_error": f"network: {e.reason}"}
    _cache[path] = data
    return data


def folder_tree(repo, folder, ref):
    """Git tree hash of `folder` in `repo` at `ref`, or (None, error)."""
    q = urllib.parse.quote
    if folder in ("", "."):
        c = get(f"/repos/{repo}/commits/{q(ref)}")
        return (c.get("commit", {}).get("tree", {}).get("sha"), c.get("_error")) if isinstance(c, dict) else (None, "bad response")
    parent, name = posixpath.split(folder)
    listing = get(f"/repos/{repo}/contents/{q(parent)}?ref={q(ref)}" if parent else f"/repos/{repo}/contents?ref={q(ref)}")
    if isinstance(listing, dict):
        return None, listing.get("_error", "not a directory")
    for entry in listing:
        if entry.get("name") == name and entry.get("type") == "dir":
            return entry.get("sha"), None
    return None, "folder not found upstream"


def commits_since(repo, folder, since_iso, exclude_sha=None, limit=5):
    q = urllib.parse.quote
    rows = get(f"/repos/{repo}/commits?path={q(folder)}&since={q(since_iso)}&per_page={limit + 1}")
    if not isinstance(rows, list):
        return []
    out = []
    for c in rows:
        if exclude_sha and c["sha"].startswith(exclude_sha[:7]):
            continue
        out.append(f"{c['sha'][:7]} {c['commit']['committer']['date'][:10]} {c['commit']['message'].splitlines()[0][:70]}")
    return out[:limit]


def check_lock(path, only):
    data = json.load(open(os.path.expanduser(path)))
    skills = data.get("skills", data)
    results = []
    for name, e in sorted(skills.items()):
        if only and name not in only:
            continue
        if e.get("sourceType") != "github" or not e.get("skillFolderHash"):
            results.append((name, e.get("source", "?"), "skipped", "not a GitHub install with a folder hash", []))
            continue
        folder = posixpath.dirname(e["skillPath"])
        head, err = folder_tree(e["source"], folder, "HEAD")
        if err:
            results.append((name, e["source"], "unknown", err, []))
        elif head == e["skillFolderHash"]:
            results.append((name, e["source"], "up to date", "", []))
        else:
            since = e.get("updatedAt") or e.get("installedAt") or "1970-01-01T00:00:00Z"
            results.append((name, e["source"], "changed", f"installed {since[:10]}", commits_since(e["source"], folder, since)))
    return results


def check_vendor(path, only):
    data = json.load(open(path))
    results = []
    for e in data["skills"]:
        name = e["skill"]
        if only and name not in only:
            continue
        pinned, err1 = folder_tree(e["repo"], e["path"], e["commit"])
        head, err2 = folder_tree(e["repo"], e["path"], "HEAD")
        if err1 or err2:
            results.append((name, e["repo"], "unknown", err1 or err2, []))
        elif pinned == head:
            results.append((name, e["repo"], "up to date", f"pin {e['commit'][:7]}", []))
        else:
            pin = get(f"/repos/{e['repo']}/commits/{e['commit']}")
            since = pin.get("commit", {}).get("committer", {}).get("date", "1970-01-01T00:00:00Z")
            results.append((name, e["repo"], "changed", f"pin {e['commit'][:7]}", commits_since(e["repo"], e["path"], since, e["commit"])))
    return results


def blob_sha(path):
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def verify_local(vendor_path, only, allowed_extra=("LICENSE",)):
    """Compare each vendored folder with upstream at its pinned commit, file by file (git blob hashes)."""
    base = os.path.dirname(os.path.abspath(vendor_path))
    problems = []
    for e in json.load(open(vendor_path))["skills"]:
        if only and e["skill"] not in only:
            continue
        local = os.path.join(base, "skills", e["bucket"], e["skill"])
        tree, err = folder_tree(e["repo"], e["path"], e["commit"])
        if err:
            problems.append(f"`{e['skill']}`: cannot read upstream at pin ({err})")
            continue
        listing = get(f"/repos/{e['repo']}/git/trees/{tree}?recursive=1")
        if not isinstance(listing, dict) or "tree" not in listing:
            problems.append(f"`{e['skill']}`: cannot list upstream tree")
            continue
        if listing.get("truncated"):
            problems.append(f"`{e['skill']}`: upstream tree too large to list in one call; check by hand")
        upstream = {x["path"]: x["sha"] for x in listing["tree"] if x["type"] == "blob"}
        mine = {}
        for dirpath, dirs, files in os.walk(local):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f == ".DS_Store":
                    continue
                full = os.path.join(dirpath, f)
                mine[os.path.relpath(full, local).replace(os.sep, "/")] = blob_sha(full)
        missing = sorted(set(upstream) - set(mine))
        extra = sorted(set(mine) - set(upstream) - set(allowed_extra))
        changed = sorted(p for p in set(upstream) & set(mine) if upstream[p] != mine[p])
        if missing or extra or changed:
            problems.append(f"`{e['skill']}`: {len(changed)} modified, {len(missing)} missing, {len(extra)} extra"
                            + "".join(f"\n  - modified {p}" for p in changed[:5])
                            + "".join(f"\n  - missing {p}" for p in missing[:5])
                            + "".join(f"\n  - extra {p}" for p in extra[:5]))
        else:
            print(f"- `{e['skill']}`: identical to {e['repo']}@{e['commit'][:7]} ({len(upstream)} files; LICENSE added)")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--lock", nargs="?", const="~/.agents/.skill-lock.json")
    g.add_argument("--vendor")
    ap.add_argument("--only", default="")
    ap.add_argument("--fail-on-changes", action="store_true")
    ap.add_argument("--verify-local", action="store_true")
    a = ap.parse_args()
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    results = check_lock(a.lock, only) if a.lock else check_vendor(a.vendor, only)

    counts = {}
    for r in results:
        counts[r[2]] = counts.get(r[2], 0) + 1
    print("# Skill update check\n")
    print(f"Source: {a.lock or a.vendor} | token: {'yes' if TOKEN else 'no (anonymous, 60 requests/hour)'}\n")
    print("| Status | Count |\n|---|---|")
    for k in ("changed", "up to date", "unknown", "skipped"):
        if counts.get(k):
            print(f"| {k} | {counts[k]} |")
    print()
    for status in ("changed", "unknown"):
        rows = [r for r in results if r[2] == status]
        if rows:
            print(f"## {status.capitalize()}\n")
            for name, repo, _, note, commits in rows:
                print(f"- `{name}` ({repo}) {note}")
                for c in commits:
                    print(f"  - {c}")
            print()
    if a.verify_local and a.vendor:
        print("## Local copies vs pinned upstream\n")
        problems = verify_local(a.vendor, only)
        for p in problems:
            print(f"- PROBLEM {p}")
        print()
        if problems:
            sys.exit(2)
    if a.fail_on_changes and counts.get("changed"):
        sys.exit(1)


if __name__ == "__main__":
    main()
