#!/usr/bin/env python3
"""Create a new pack (bucket + plugin) or a new skill, keeping every manifest in sync.

  scripts/scaffold.py pack <bucket> --description "..." [--plugin-name NAME] [--category CAT]
  scripts/scaffold.py skill <bucket> <skill-name>

`pack` creates skills/<bucket>/.claude-plugin/plugin.json and adds the plugin to
.claude-plugin/marketplace.json at the marketplace's current version.
`skill` copies template/SKILL.md.template to skills/<bucket>/<skill-name>/SKILL.md and lists it in
the bucket's plugin.json. Run scripts/validate-skills.py afterwards. Stdlib only; never overwrites.
"""
import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKET = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def dump(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def pack(a):
    if not NAME.match(a.bucket):
        die("bucket must be kebab-case, for example 'flutter' or 'gcp'")
    name = a.plugin_name or a.bucket
    pdir = os.path.join(ROOT, "skills", a.bucket, ".claude-plugin")
    if os.path.exists(pdir):
        die(f"skills/{a.bucket} already has a plugin")
    market = json.load(open(MARKET))
    if any(p["name"] == name for p in market["plugins"]):
        die(f"a plugin named '{name}' already exists")
    version = market["plugins"][0].get("version", "0.1.0") if market["plugins"] else "0.1.0"
    os.makedirs(pdir)
    plugin = {
        "name": name, "version": version,
        "description": a.description,
        "author": market["owner"], "homepage": "https://github.com/Atou4/skillsmith",
        "repository": "https://github.com/Atou4/skillsmith", "license": "MIT",
        "keywords": [a.bucket], "skills": [],
    }
    dump(os.path.join(pdir, "plugin.json"), plugin)
    shutil.copyfile(os.path.join(ROOT, "assets", "brand", "icon-512.png"), os.path.join(pdir, "icon.png"))
    market["plugins"].append({"name": name, "source": f"./skills/{a.bucket}", "description": a.description,
                              "version": version, "category": a.category, "keywords": [a.bucket]})
    dump(MARKET, market)
    print(f"created pack '{name}' at skills/{a.bucket} (version {version}); add skills with: scripts/scaffold.py skill {a.bucket} <name>")


def skill(a):
    if not NAME.match(a.skill):
        die("skill name must be kebab-case")
    pj_path = os.path.join(ROOT, "skills", a.bucket, ".claude-plugin", "plugin.json")
    if not os.path.isfile(pj_path):
        die(f"no pack at skills/{a.bucket}; create it first with: scripts/scaffold.py pack {a.bucket} --description ...")
    sdir = os.path.join(ROOT, "skills", a.bucket, a.skill)
    if os.path.exists(sdir):
        die(f"skills/{a.bucket}/{a.skill} already exists")
    for dirpath, _, files in os.walk(os.path.join(ROOT, "skills")):
        if os.path.basename(dirpath) == a.skill and "SKILL.md" in files:
            die(f"a skill named '{a.skill}' already exists at {os.path.relpath(dirpath, ROOT)}")
    os.makedirs(sdir)
    tpl = open(os.path.join(ROOT, "template", "SKILL.md.template")).read()
    open(os.path.join(sdir, "SKILL.md"), "w").write(tpl.replace("replace-with-folder-name", a.skill))
    pj = json.load(open(pj_path))
    pj["skills"] = sorted(set(pj.get("skills", [])) | {f"./{a.skill}"})
    dump(pj_path, pj)
    print(f"created skills/{a.bucket}/{a.skill}/SKILL.md from the template and listed it in the pack; now write the skill")


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = ap.add_subparsers(dest="cmd", required=True)
p = sub.add_parser("pack"); p.add_argument("bucket"); p.add_argument("--description", required=True)
p.add_argument("--plugin-name"); p.add_argument("--category", default="engineering"); p.set_defaults(fn=pack)
s = sub.add_parser("skill"); s.add_argument("bucket"); s.add_argument("skill"); s.set_defaults(fn=skill)
args = ap.parse_args()
args.fn(args)
