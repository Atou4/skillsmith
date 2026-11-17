#!/usr/bin/env python3
"""Validate every skill in this repo. Exit 1 on any problem. Stdlib only."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def err(msg):
    errors.append(msg)


skill_dirs = []
for dirpath, _dirs, files in os.walk(os.path.join(ROOT, "skills")):
    if "SKILL.md" in files:
        skill_dirs.append(dirpath)

for d in sorted(skill_dirs):
    rel = os.path.relpath(d, ROOT)
    text = open(os.path.join(d, "SKILL.md"), encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{rel}: no frontmatter")
        continue
    fm = {}
    key = None
    for line in m.group(1).splitlines():
        k = re.match(r"^(name|description):\s*(.*)$", line)
        if k:
            key = k.group(1)
            fm[key] = k.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fm[key] = (fm[key] + " " + line.strip()).strip()
        else:
            key = None
    if not fm.get("name"):
        err(f"{rel}: missing name")
    elif fm["name"] != os.path.basename(d):
        err(f"{rel}: name '{fm['name']}' != folder '{os.path.basename(d)}'")
    if not fm.get("description"):
        err(f"{rel}: missing description")
    elif len(fm["description"]) > 1024:
        err(f"{rel}: description over 1024 chars ({len(fm['description'])})")
    for bad in ("/Users/", "@gmail.com"):
        if bad in text:
            err(f"{rel}: contains personal string '{bad}'")

plugin = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json")))
listed = {os.path.normpath(p) for p in plugin.get("skills", [])}
actual = {os.path.normpath("./" + os.path.relpath(d, ROOT)) for d in skill_dirs}
for p in sorted(listed - actual):
    err(f"plugin.json lists missing skill: {p}")
for p in sorted(actual - listed):
    err(f"plugin.json does not list skill: {p}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(skill_dirs)} skills validated")
