#!/usr/bin/env bash
# Verification helper for the skillsmith repo.
#
# Usage: scripts/verify.sh <doctor|static|install|discover|audit-fixture|vendor|clean|all>
#
# - Every Claude Code command runs with CLAUDE_CONFIG_DIR pointing at a throwaway
#   directory, so your real ~/.claude is never modified.
# - Evidence is written to artifacts/<RUN_ID>/ next to this skill and survives `clean`.
# - Set RUN_ID to reuse a run across subcommands. Default: a timestamp.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$SKILL_DIR/../../.." && pwd)"
RUN_ID="${RUN_ID:-$(date +%Y%m%d-%H%M%S)}"
ART="$SKILL_DIR/artifacts/$RUN_ID"
ISO="${VERIFY_TMP:-${TMPDIR:-/tmp}}/verify-skillsmith-$RUN_ID"
mkdir -p "$ART" "$ISO/claude"
export CLAUDE_CONFIG_DIR="$ISO/claude"   # every claude command below uses a throwaway config
[ "$CLAUDE_CONFIG_DIR" != "$HOME/.claude" ] || { echo "refusing to use the real config dir" >&2; exit 1; }

fail() { echo "FAIL: $*" | tee -a "$ART/failures.txt" >&2; exit 1; }
ok()   { echo "PASS: $*" | tee -a "$ART/summary.txt"; }

repo_skill_names() { find "$REPO/skills" -name SKILL.md -exec dirname {} \; | xargs -n1 basename | sort; }
market_plugins()   { python3 -c "import json; print(' '.join(p['name'] for p in json.load(open('$REPO/.claude-plugin/marketplace.json'))['plugins']))"; }
plugin_version()   { python3 -c "import json; print({p['name']:p['version'] for p in json.load(open('$REPO/.claude-plugin/marketplace.json'))['plugins']}['$1'])"; }
dir_counts()       { for d in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills"; do printf '%s ' "$(ls -A "$d" 2>/dev/null | wc -l | tr -d ' ')"; done; }
lock_mtime()       { f="$HOME/.agents/.skill-lock.json"; [ -f "$f" ] && (stat -f %m "$f" 2>/dev/null || stat -c %Y "$f") || echo none; }

doctor() {
  { echo "repo: $REPO"; echo "run: $RUN_ID"; echo "claude: $(claude --version 2>&1 | head -1)"; echo "python3: $(python3 --version)"
    echo "uv: $(command -v uv || echo MISSING)"; echo "npx: $(command -v npx || echo MISSING)"
    echo "plugins: $(for p in $(market_plugins); do printf '%s@%s ' "$p" "$(plugin_version "$p")"; done)"; echo "skills in repo: $(repo_skill_names | tr '\n' ' ')"
    echo "git dirty files: $(git -C "$REPO" status --short | wc -l | tr -d ' ')"; } | tee "$ART/doctor.txt"
  [ -f "$REPO/.claude-plugin/marketplace.json" ] || fail "no marketplace.json under $REPO"
  command -v claude >/dev/null || fail "claude CLI not found"
  command -v npx >/dev/null || fail "npx not found"
  ok "doctor"
}

static() {
  if command -v uv >/dev/null; then runner=(uv run --quiet --with pyyaml python); else runner=(python3); fi
  (cd "$REPO" && "${runner[@]}" scripts/validate-skills.py) > "$ART/validate-skills.txt" 2>&1 || { cat "$ART/validate-skills.txt"; fail "validate-skills.py"; }
  grep -q '^OK:' "$ART/validate-skills.txt" || fail "validator did not print OK"
  (cd "$REPO" && claude plugin validate .) > "$ART/plugin-validate.txt" 2>&1 || { cat "$ART/plugin-validate.txt"; fail "claude plugin validate"; }
  grep -q 'Validation passed' "$ART/plugin-validate.txt" || fail "plugin validate did not pass"
  ok "static: $(cat "$ART/validate-skills.txt"); claude plugin validate passed"
}

install() {
  claude plugin marketplace add "$REPO" > "$ART/install.txt" 2>&1 || { cat "$ART/install.txt"; fail "marketplace add"; }
  for p in $(market_plugins); do
    { claude plugin install "$p@skillsmith"; claude plugin details "$p"; } >> "$ART/install.txt" 2>&1 || { cat "$ART/install.txt"; fail "install $p"; }
    grep -qE "^$p $(plugin_version "$p")$" "$ART/install.txt" || fail "plugin $p is not at version $(plugin_version "$p")"
  done
  claude plugin list >> "$ART/install.txt" 2>&1
  grep -q "Read from: $REPO" "$ART/install.txt" || fail "plugins were not read from $REPO"
  got="$(grep -E '^ *Skills \(' "$ART/install.txt" | sed -E 's/^ *Skills \([0-9]+\) *//' | tr ',' '\n' | sed 's/ //g' | sort)"
  [ "$got" = "$(repo_skill_names)" ] || { diff <(echo "$got") <(repo_skill_names) || true; fail "installed skills differ from repo skills"; }
  ok "install: plugins $(market_plugins | tr ' ' ','); $(echo "$got" | wc -l | tr -d ' ') skills registered from the working tree"
}

discover() {
  before="$(dir_counts)/$(lock_mtime)"
  (cd "$ISO" 2>/dev/null || cd /tmp; npx --yes skills add "$REPO" --list) > "$ART/skills-list-raw.txt" 2>&1 || { tail -5 "$ART/skills-list-raw.txt"; fail "npx skills --list"; }
  after="$(dir_counts)/$(lock_mtime)"
  [ "$before" = "$after" ] || fail "--list changed skill folders or lock file ($before -> $after)"
  grep -E '^│    [a-z]' "$ART/skills-list-raw.txt" | sed 's/│ *//' | sort > "$ART/skills-list.txt"
  [ "$(cat "$ART/skills-list.txt")" = "$(repo_skill_names)" ] || { diff "$ART/skills-list.txt" <(repo_skill_names) || true; fail "CLI discovers a different set than the repo defines"; }
  ok "discover: CLI lists exactly the $(wc -l < "$ART/skills-list.txt" | tr -d ' ') repo skills; no skill folder or lock file changed"
}

audit_fixture() {
  F="$ISO/fixture"; rm -rf "$F"; mkdir -p "$F/good" "$F/badname" "$F/nomd"
  printf -- '---\nname: good\ndescription: ok\n---\n' > "$F/good/SKILL.md"
  printf -- '---\nname: other\ndescription: ok\n---\n' > "$F/badname/SKILL.md"
  ln -s "$F/does-not-exist" "$F/dead"
  python3 -I "$REPO/skills/meta/skill-audit/scripts/audit.py" "$F" > "$ART/audit-fixture.txt" 2>&1 || fail "audit.py crashed"
  grep -q '| Broken symlinks | 1 |' "$ART/audit-fixture.txt" || fail "audit missed the broken symlink"
  grep -q '| Malformed | 2 |' "$ART/audit-fixture.txt"       || fail "audit missed the name mismatch or the missing SKILL.md"
  grep -q "name 'other' differs from folder" "$ART/audit-fixture.txt" || fail "audit did not name the mismatch"
  ok "audit-fixture: 1 broken symlink and 2 malformed skills found in a known-bad fixture"
}

vendor() {
  python3 -I "$REPO/skills/meta/skill-update-check/scripts/check_updates.py" --vendor "$REPO/vendor.json" --verify-local > "$ART/vendor.txt" 2>&1
  rc=$?
  [ $rc -ne 2 ] || { cat "$ART/vendor.txt"; fail "a vendored copy differs from its pinned upstream"; }
  grep -q "identical to" "$ART/vendor.txt" || { cat "$ART/vendor.txt"; fail "vendor check produced no result (network or rate limit?)"; }
  ok "vendor: $(grep -c 'identical to' "$ART/vendor.txt" | tr -d ' ') vendored skills byte-identical to their pinned upstream; upstream status: $(grep -E '^\| (changed|up to date) ' "$ART/vendor.txt" | tr -d '|' | xargs)"
}

clean() {
  claude plugin marketplace remove skillsmith >/dev/null 2>&1 || true
  rm -rf "$ISO"
  echo "cleaned $ISO (evidence kept in $ART)"
}

case "${1:-}" in
  doctor) doctor ;; static) static ;; install) install ;; discover) discover ;;
  audit-fixture) audit_fixture ;; vendor) vendor ;; clean) clean ;;
  all) trap clean EXIT; doctor; static; install; discover; audit_fixture; vendor; echo "ALL PASSED. Evidence: $ART" ;;
  *) echo "usage: $0 <doctor|static|install|discover|audit-fixture|vendor|clean|all>" >&2; exit 2 ;;
esac
