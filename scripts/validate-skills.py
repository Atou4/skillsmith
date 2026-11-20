#!/usr/bin/env python3
"""Validate the skillsmith repo layout, manifests and skills. Exit 1 on any problem.

Layout rules:
  skills/<bucket>/<skill>/SKILL.md                every skill sits exactly two levels down
  skills/<bucket>/.claude-plugin/plugin.json      one plugin per bucket, listing all its skills
  .claude-plugin/marketplace.json                 lists every bucket once, with matching name and version
  vendor.json + THIRD_PARTY_NOTICES.md            every vendored skill has a LICENSE and a notices row
  Any SKILL.md outside skills/ must set metadata.internal: true, or the skills CLI offers it to users.

Uses PyYAML for strict frontmatter parsing when available (CI installs it); falls back to a
line-based parse otherwise. Run: uv run --with pyyaml python scripts/validate-skills.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "node_modules", "artifacts", "__pycache__"}
LEAKS = ("/Users/", "@gmail.com")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
errors = []

try:
    import yaml
except ImportError:
    yaml = None


def err(msg):
    errors.append(msg)


def rel(p):
    return os.path.relpath(p, ROOT)


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{rel(path)}: no frontmatter")
        return None, text
    block = m.group(1)
    if yaml:
        try:
            data = yaml.safe_load(block)
            return (data if isinstance(data, dict) else {}), text
        except yaml.YAMLError as e:
            err(f"{rel(path)}: frontmatter is not valid YAML ({str(e).splitlines()[0]})")
            return None, text
    fm, key = {}, None
    for line in block.splitlines():
        k = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if k:
            key = k.group(1)
            fm[key] = k.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fm[key] = (str(fm[key]) + " " + line.strip()).strip()
    if "internal: true" in block:
        fm["metadata"] = {"internal": True}
    return fm, text


def load_json(path):
    try:
        return json.load(open(path))
    except (OSError, json.JSONDecodeError) as e:
        err(f"{rel(path)}: {e}")
        return None


# 1. Every SKILL.md in the repo: where it is, and whether installers can see it.
skills = {}  # (bucket, name) -> dir
for dirpath, dirs, files in os.walk(ROOT, followlinks=False):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not os.path.islink(os.path.join(dirpath, d))]
    if "SKILL.md" not in files:
        continue
    parts = rel(dirpath).split(os.sep)
    path = os.path.join(dirpath, "SKILL.md")
    if parts[0] == "skills":
        if len(parts) != 3:
            err(f"{rel(path)}: skills must sit at skills/<bucket>/<skill>/SKILL.md")
            continue
        skills[(parts[1], parts[2])] = dirpath
    else:
        fm, _ = frontmatter(path)
        if fm is not None and not (isinstance(fm.get("metadata"), dict) and fm["metadata"].get("internal") is True):
            err(f"{rel(path)}: SKILL.md outside skills/ must set 'metadata: internal: true' or installers will offer it")

# 2. Frontmatter and content of every published skill.
names = {}
for (bucket, name), d in sorted(skills.items()):
    fm, text = frontmatter(os.path.join(d, "SKILL.md"))
    r = rel(d)
    if name in names:
        err(f"{r}: skill name '{name}' also used in skills/{names[name]}/ (the skills CLI installs by name)")
    names[name] = bucket
    if fm is None:
        continue
    if not fm.get("name"):
        err(f"{r}: missing name")
    elif fm["name"] != name:
        err(f"{r}: name '{fm['name']}' != folder '{name}'")
    desc = str(fm.get("description") or "")
    if not desc:
        err(f"{r}: missing description")
    elif desc.startswith("One or two sentences. Say what the skill does"):
        err(f"{r}: description is still the template placeholder; write the skill before publishing")
    elif len(desc) > 1024:
        err(f"{r}: description over 1024 chars ({len(desc)})")
    for bad in LEAKS:
        if bad in text:
            err(f"{r}/SKILL.md: contains personal string '{bad}'")

# 3. One plugin per bucket, and the marketplace that lists them.
buckets = sorted({b for b, _ in skills} | {d for d in os.listdir(os.path.join(ROOT, "skills")) if os.path.isdir(os.path.join(ROOT, "skills", d))})
market = load_json(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) or {"plugins": []}
by_source = {os.path.normpath(p.get("source", "")): p for p in market.get("plugins", [])}
plugin_names = set()
for b in buckets:
    pj_path = os.path.join(ROOT, "skills", b, ".claude-plugin", "plugin.json")
    pj = load_json(pj_path)
    if pj is None:
        continue
    for field in ("name", "version", "description", "license"):
        if not pj.get(field):
            err(f"{rel(pj_path)}: missing {field}")
    if pj.get("version") and not SEMVER.match(pj["version"]):
        err(f"{rel(pj_path)}: version '{pj['version']}' is not MAJOR.MINOR.PATCH")
    if pj.get("name") in plugin_names:
        err(f"{rel(pj_path)}: plugin name '{pj['name']}' is used twice")
    plugin_names.add(pj.get("name"))
    listed = {os.path.normpath(os.path.join("skills", b, p)) for p in pj.get("skills", [])}
    actual = {os.path.normpath(os.path.join("skills", b, s)) for (bb, s) in skills if bb == b}
    for p in sorted(listed - actual):
        err(f"{rel(pj_path)} lists a missing skill: {p}")
    for p in sorted(actual - listed):
        err(f"{rel(pj_path)} does not list skill: {p}")
    entry = by_source.pop(os.path.normpath(f"skills/{b}"), None)
    if entry is None:
        err(f"marketplace.json has no plugin with source './skills/{b}'")
    else:
        if entry.get("name") != pj.get("name"):
            err(f"marketplace.json entry for skills/{b} is named '{entry.get('name')}', plugin.json says '{pj.get('name')}'")
        if entry.get("version") and entry.get("version") != pj.get("version"):
            err(f"marketplace.json version {entry.get('version')} != plugin.json {pj.get('version')} for skills/{b}")
for src in by_source:
    err(f"marketplace.json lists source '{src}' with no bucket behind it")

# 4. Vendored third-party skills: license, notices, and provenance stay together.
vendor = load_json(os.path.join(ROOT, "vendor.json")) or {"skills": []}
notices = open(os.path.join(ROOT, "THIRD_PARTY_NOTICES.md"), encoding="utf-8").read()
for e in vendor.get("skills", []):
    key = (e.get("bucket"), e.get("skill"))
    where = f"vendor.json entry '{e.get('skill')}'"
    if key not in skills:
        err(f"{where}: no skill at skills/{key[0]}/{key[1]}")
        continue
    if not os.path.isfile(os.path.join(skills[key], "LICENSE")):
        err(f"skills/{key[0]}/{key[1]}: vendored skill has no LICENSE file")
    if f"`{e['skill']}`" not in notices or e.get("commit", "")[:7] not in notices:
        err(f"{where}: THIRD_PARTY_NOTICES.md must name the skill and its pinned commit {e.get('commit', '')[:7]}")
    for field in ("author", "repo", "path", "commit", "license"):
        if not e.get(field):
            err(f"{where}: missing {field}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(skills)} skills in {len(buckets)} plugins validated" + ("" if yaml else " (no PyYAML: strict YAML check skipped)"))
