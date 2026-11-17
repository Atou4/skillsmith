#!/usr/bin/env python3
"""Read-only audit of installed agent skills. Prints a Markdown report. Stdlib only."""
import os
import re
import sys
from collections import defaultdict

HOME = os.path.expanduser("~")
DEFAULT_ROOTS = ["~/.claude/skills", "~/.codex/skills", "~/.agents/skills"]


def frontmatter(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read(8192)
    except OSError:
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm = {}
    key = None
    for line in m.group(1).splitlines():
        k = re.match(r"^(name|description):\s*(.*)$", line)
        if k:
            key = k.group(1)
            fm[key] = k.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fm[key] = (fm[key] + " " + line.strip()).strip()  # multi-line value
        else:
            key = None
    # folded/literal block markers carry no text on their own line
    for k, v in fm.items():
        fm[k] = re.sub(r"^[>|][+-]?\s*", "", v)
    return fm


def short(p):
    return p.replace(HOME, "~")


def main():
    roots = [os.path.expanduser(r) for r in (sys.argv[1:] or DEFAULT_ROOTS)]
    roots = [r for r in roots if os.path.isdir(r)]
    entries = {}  # root -> {name: info}
    for root in roots:
        entries[root] = {}
        for name in sorted(os.listdir(root)):
            if name.startswith("."):
                continue
            p = os.path.join(root, name)
            is_link = os.path.islink(p)
            target = os.path.realpath(p) if is_link else p
            entries[root][name] = {
                "path": p,
                "link": is_link,
                "target": target,
                "broken": is_link and not os.path.exists(p),
            }

    broken, malformed, managed = [], [], []
    by_name = defaultdict(dict)  # name -> {root: target}
    for root, items in entries.items():
        for name, info in items.items():
            by_name[name][root] = info
            if info["broken"]:
                broken.append((root, name, os.readlink(info["path"])))
                continue
            if not os.path.isdir(info["target"]):
                continue
            skill_md = os.path.join(info["target"], "SKILL.md")
            if not os.path.isfile(skill_md):
                malformed.append((root, name, "no SKILL.md"))
                continue
            fm = frontmatter(skill_md) or {}
            if not fm.get("name") or not fm.get("description"):
                malformed.append((root, name, "frontmatter missing name or description"))
            elif fm["name"].strip("\"'") != name:
                malformed.append((root, name, f"name '{fm['name']}' differs from folder"))
            if not info["link"]:
                managed.append((root, name))

    missing, drift = [], []
    for name, per_root in by_name.items():
        present = [r for r in per_root if not per_root[r]["broken"]]
        absent = [r for r in roots if r not in per_root]
        if absent and present:
            missing.append((name, [short(r) for r in absent]))
        targets = {per_root[r]["target"] for r in present}
        if len(targets) > 1:
            drift.append((name, {short(r): short(per_root[r]["target"]) for r in present}))

    total = sum(len(v) for v in entries.values())
    print("# Skill audit\n")
    print(f"Roots scanned: {', '.join(short(r) for r in roots)}")
    print(f"Entries: {total} | unique names: {len(by_name)}\n")
    print("| Finding | Count |\n|---|---|")
    print(f"| Broken symlinks | {len(broken)} |")
    print(f"| Malformed | {len(malformed)} |")
    print(f"| Duplicate name, different target | {len(drift)} |")
    print(f"| Missing in some roots | {len(missing)} |")
    print(f"| User-managed (real directories) | {len(managed)} |\n")

    def section(title, rows, fmt):
        if not rows:
            return
        print(f"## {title}\n")
        for r in rows:
            print(fmt(r))
        print()

    section("Broken symlinks", broken, lambda r: f"- `{r[1]}` in {short(r[0])} -> `{short(r[2])}`")
    section("Malformed", malformed, lambda r: f"- `{r[1]}` in {short(r[0])}: {r[2]}")
    section(
        "Duplicate name, different target",
        drift,
        lambda r: f"- `{r[0]}`: " + "; ".join(f"{k} -> {v}" for k, v in r[1].items()),
    )
    section("Missing in some roots", missing, lambda r: f"- `{r[0]}` absent from {', '.join(r[1])}")
    section("User-managed", managed, lambda r: f"- `{r[1]}` in {short(r[0])}")


if __name__ == "__main__":
    main()
