#!/usr/bin/env bash
# user-guide-maker engine — every step of building a guide. Run from the platform's repository.
#
#   run.sh init <platform> <test-to-clone> <test-to-populate>   set up docs/user-guide for this guide
#   run.sh preflight                       check the tools, the app and the sign-in
#   run.sh read                            read both tests (read-only) and work out the build plan
#   run.sh capture [--dry]                 build the Test to populate in the editor, screenshotting
#                                          every step (--dry: never saves; the default saves twice)
#   run.sh look                            the look-only screenshots (opens and cancels; never saves)
#   run.sh build                           build the deck, measure text in PowerPoint, rebuild,
#                                          render previews, validate
#   run.sh sheets [images dir]             contact sheets of the previews (or of any folder) for review
#
# The guide's folder is $GUIDE_DIR (default: ./docs/user-guide). `init` copies the platform
# profile into $GUIDE_DIR/build — edit those copies freely, `init` never overwrites them
# (pass --force to refresh) — and records the inputs in $GUIDE_DIR/build/guide.env.
#
# Overridable: GUIDE_DIR, TEMPLATE, WIN_WORK, NODE_EXE, CHROME_EXE, PYTHON, APP_URL.
set -euo pipefail

ENGINE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL="$(dirname "$ENGINE")"
PLUGIN_ROOT="$(cd "$SKILL/../.." && pwd)"
GUIDE_DIR="${GUIDE_DIR:-$PWD/docs/user-guide}"
BUILD="$GUIDE_DIR/build"
ENV_FILE="$BUILD/guide.env"
if [ -f "$ENV_FILE" ]; then set -a; . "$ENV_FILE"; set +a; fi
TEMPLATE="${TEMPLATE:-$PLUGIN_ROOT/src/Layout User Guide Template.pptx}"
PY="${PYTHON:-python3}"

die() { echo "ERROR: $*" >&2; exit 1; }
is_wsl() { grep -qi microsoft /proc/version 2>/dev/null; }
native() { if is_wsl; then wslpath -w "$1"; else echo "$1"; fi; }

win_temp() {       # Windows %TEMP% as a WSL path; WSL interop can fail now and then, so ask twice, two ways
  local t="" i
  for i in 1 2 3; do
    t="$(cd /mnt/c 2>/dev/null && cmd.exe /c 'echo %TEMP%' 2>/dev/null | tr -d '\r' | tail -1)"
    [ -z "$t" ] && t="$(powershell.exe -NoProfile -Command '$env:TEMP' 2>/dev/null | tr -d '\r' | tail -1)"
    case "$t" in [A-Za-z]:\\*) wslpath "$t"; return 0 ;; esac
    sleep 1
  done
  return 1
}
if [ -z "${WIN_WORK:-}" ]; then
  if is_wsl; then
    WIN_WORK="$(win_temp)/userguide-maker" || die "could not find the Windows temp folder (WSL interop): set WIN_WORK=/mnt/c/Users/<you>/AppData/Local/Temp/userguide-maker"
  else
    WIN_WORK="$HOME/.cache/userguide-maker"
  fi
fi
case "$WIN_WORK" in /*) ;; *) die "WIN_WORK must be an absolute path (got '$WIN_WORK')" ;; esac
if [ -z "${NODE_EXE:-}" ]; then
  if is_wsl && [ -x "/mnt/c/Program Files/nodejs/node.exe" ]; then NODE_EXE="/mnt/c/Program Files/nodejs/node.exe"; else NODE_EXE="$(command -v node || true)"; fi
fi
deck() { echo "$GUIDE_DIR/${GUIDE_TITLE:-User Guide}.pptx"; }
need_init() { [ -f "$ENV_FILE" ] || die "no guide set up here: run '$0 init <platform> <test-to-clone> <test-to-populate>' first (GUIDE_DIR=$GUIDE_DIR)"; }

# ---------------------------------------------------------------------------------- init
cmd_init() {
  local platform="${1:-}" clone="${2:-}" populate="${3:-}" force="${4:-}"
  [ -n "$platform" ] && [ -n "$clone" ] && [ -n "$populate" ] || die "usage: run.sh init <platform> <test-to-clone> <test-to-populate> [--force]"
  local prof="$SKILL/platforms/$platform"
  [ -d "$prof" ] || die "no profile for '$platform'. Profiles: $(ls "$SKILL/platforms" | tr '\n' ' '). See references/new-platform.md to add one."
  [ "$clone" != "$populate" ] || die "the Test to clone and the Test to populate must be different tests"
  mkdir -p "$BUILD" "$GUIDE_DIR/screenshots" "$GUIDE_DIR/previews"
  for f in "$prof"/*; do
    local b; b="$(basename "$f")"
    [ "$b" = "profile.env" ] && continue
    if [ ! -e "$BUILD/$b" ] || [ "$force" = "--force" ]; then cp "$f" "$BUILD/$b"; fi
  done
  { echo "# written by run.sh init on $(date +%F) — the inputs of this guide"
    echo "PLATFORM=$platform"
    echo "CLONE=$clone"
    echo "POPULATE=$populate"
    echo "GUIDE_VERSION=${GUIDE_VERSION:-1}"
    echo "WIN_WORK=\"$WIN_WORK\""
    cat "$prof/profile.env"
  } > "$ENV_FILE"
  if [ ! -f "$GUIDE_DIR/PROGRESS.md" ]; then
    sed -e "s/{{PLATFORM}}/$platform/g" -e "s/{{CLONE}}/$clone/g" -e "s/{{POPULATE}}/$populate/g" -e "s/{{DATE}}/$(date +%F)/g" \
      "$SKILL/references/progress-template.md" > "$GUIDE_DIR/PROGRESS.md"
  fi
  echo "set up $GUIDE_DIR for $platform: clone $clone -> populate $populate"
  echo "profile copied to $BUILD (edit there); next: $0 preflight"
}

# ---------------------------------------------------------------------------------- shared
prepare_work() {   # copy the engine and the guide's scripts where the browser's Node runs them
  mkdir -p "$WIN_WORK"
  if [ ! -d "$WIN_WORK/node_modules/playwright-core" ]; then
    local src; src="$(ls -d "$HOME"/.npm/_npx/*/node_modules/playwright-core 2>/dev/null | head -1 || true)"
    if [ -n "$src" ]; then mkdir -p "$WIN_WORK/node_modules" && cp -r "$src" "$WIN_WORK/node_modules/"
    else
      command -v npm >/dev/null || die "playwright-core is missing and npm is not available: install it with 'npm install --prefix \"$WIN_WORK\" playwright-core'"
      npm install --silent --no-save --prefix "$WIN_WORK" playwright-core >/dev/null
    fi
  fi
  echo '{ "private": true, "type": "commonjs" }' > "$WIN_WORK/package.json"
  cp "$ENGINE/browser.js" "$ENGINE/capture-lib.js" "$WIN_WORK/"
  cp "$BUILD"/*.js "$WIN_WORK/" 2>/dev/null || true
  [ -f "$BUILD/plan.json" ] && cp "$BUILD/plan.json" "$WIN_WORK/plan.json"
  return 0
}
write_run() {      # write_run <dry true|false>
  local shots="$WIN_WORK/shots-$POPULATE"
  mkdir -p "$shots"
  cat > "$WIN_WORK/run.json" <<JSON
{ "platform": "$PLATFORM", "app": "${APP_URL}", "clone": "$CLONE", "target": "$POPULATE",
  "shots": $(printf '%s' "$(native "$shots")" | "$PY" -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
  "work": $(printf '%s' "$(native "$WIN_WORK")" | "$PY" -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
  "plan": $(printf '%s' "$(native "$WIN_WORK/plan.json")" | "$PY" -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
  "dry": $1 }
JSON
  echo "$shots"
}
node_run() {       # WSL's interop sometimes fails to start a Windows program (UtilAcceptVsock): retry those
  local i err="$WIN_WORK/.stderr"
  for i in 1 2 3; do
    if (cd "$WIN_WORK" && "$NODE_EXE" "$@" 2> >(tee "$err" >&2)); then return 0; fi
    sleep 1
    grep -q "UtilAcceptVsock" "$err" 2>/dev/null || return 1
    echo "(WSL interop hiccup — starting it again)" >&2
  done
  return 1
}

# ---------------------------------------------------------------------------------- preflight
cmd_preflight() {
  need_init
  local ok=1
  echo "platform $PLATFORM · clone $CLONE · populate $POPULATE · app $APP_URL"
  [ -f "$TEMPLATE" ] && echo "ok   template: $TEMPLATE" || { echo "FAIL template not found: $TEMPLATE"; ok=0; }
  [ -n "$NODE_EXE" ] && [ -e "$NODE_EXE" ] && echo "ok   node: $NODE_EXE" || { echo "FAIL node not found (set NODE_EXE)"; ok=0; }
  "$PY" -c 'import lxml, PIL' 2>/dev/null && echo "ok   python: lxml + Pillow" || { echo "FAIL python needs lxml and Pillow: $PY -m pip install --user lxml pillow"; ok=0; }
  if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -Command "try { \$a = New-Object -ComObject PowerPoint.Application; 'ok   PowerPoint (render + measure)' } catch { 'WARN PowerPoint not available: previews fall back to LibreOffice, text is not measured' }" 2>/dev/null | tr -d '\r'
  else echo "WARN no powershell.exe: previews fall back to LibreOffice (soffice), text is not measured"; fi
  if curl -s -o /dev/null -m 8 -w '%{http_code}' "$APP_URL" | grep -qE '^(2|3)'; then echo "ok   app answers: $APP_URL"; else echo "FAIL app does not answer: $APP_URL"; ok=0; fi
  prepare_work >/dev/null && echo "ok   work folder: $WIN_WORK (browser profile, playwright-core)"
  [ -f "$WIN_WORK/.token" ] && echo "note a sign-in token is waiting in $WIN_WORK/.token (spent on the next run)"
  [ "$ok" = 1 ] && echo "preflight passed — next: $0 read" || die "preflight failed"
}

# ---------------------------------------------------------------------------------- read
cmd_read() {
  need_init
  if [ ! -f "$BUILD/${READ_SCRIPT:-read-test.js}" ]; then
    echo "this profile has no read-test.js: its reference data lives in build/capture-build.js."
    echo "Set those constants from the Test to clone ($CLONE) before capturing — see build/profile.md and references/new-platform.md."
    return 0
  fi
  prepare_work
  write_run false >/dev/null
  node_run "${READ_SCRIPT:-read-test.js}" "$(native "$WIN_WORK/run.json")" clone "$(native "$WIN_WORK/clone.json")"
  node_run "${READ_SCRIPT:-read-test.js}" "$(native "$WIN_WORK/run.json")" target "$(native "$WIN_WORK/target.json")"
  cp "$WIN_WORK/clone.json" "$BUILD/clone.json"; cp "$WIN_WORK/target.json" "$BUILD/target.json"
  if [ -f "$BUILD/${PLAN_SCRIPT:-plan.js}" ]; then
    local nodeh; nodeh="$(command -v node || echo "$NODE_EXE")"
    if [ "$nodeh" = "$NODE_EXE" ]; then
      node_run "${PLAN_SCRIPT:-plan.js}" "$(native "$WIN_WORK/clone.json")" "$(native "$WIN_WORK/target.json")" "$(native "$WIN_WORK/plan.json")"
      cp "$WIN_WORK/plan.json" "$BUILD/plan.json"
    else
      node "$BUILD/${PLAN_SCRIPT:-plan.js}" "$BUILD/clone.json" "$BUILD/target.json" "$BUILD/plan.json"
      cp "$BUILD/plan.json" "$WIN_WORK/plan.json"
    fi
  fi
  echo "read done: $BUILD/clone.json, target.json, plan.json — review the plan summary above"
}

# ---------------------------------------------------------------------------------- capture
copy_shots() {
  rm -f "$GUIDE_DIR/screenshots/"*.png
  cp "$1"/*.png "$1"/*.json "$GUIDE_DIR/screenshots/" 2>/dev/null || true
  echo "screenshots: $(ls "$GUIDE_DIR/screenshots/"*.png 2>/dev/null | wc -l) in $GUIDE_DIR/screenshots"
}
cmd_capture() {
  need_init; prepare_work
  if [ -f "$BUILD/${PLAN_SCRIPT:-plan.js}" ] && [ ! -f "$BUILD/plan.json" ]; then die "no plan: run '$0 read' first"; fi
  local dry=false; [ "${1:-}" = "--dry" ] && dry=true
  local shots; shots="$(write_run "$dry")"
  rm -rf "$shots" && mkdir -p "$shots"
  for s in ${CAPTURES:-capture-build.js}; do
    echo "== $s ($([ "$dry" = true ] && echo 'dry run: nothing is saved' || echo 'SAVES the Test to populate'))"
    node_run "$s" "$(native "$WIN_WORK/run.json")"
  done
  copy_shots "$shots"
}
cmd_look() {
  need_init; prepare_work
  local shots; shots="$(write_run false)"
  for s in ${LOOK_CAPTURES:-capture.js}; do
    echo "== $s (look-only)"
    node_run "$s" "$(native "$WIN_WORK/run.json")"
  done
  cp "$shots"/*.png "$shots"/*.json "$GUIDE_DIR/screenshots/" 2>/dev/null || true
  echo "screenshots: $(ls "$GUIDE_DIR/screenshots/"*.png | wc -l) in $GUIDE_DIR/screenshots"
}

# ---------------------------------------------------------------------------------- build
render() {   # render <json-out>: previews (+ text heights with PowerPoint)
  local out="$WIN_WORK/render"
  if command -v powershell.exe >/dev/null 2>&1; then
    cp "$(deck)" "$WIN_WORK/deck.pptx"; cp "$ENGINE/render-measure.ps1" "$WIN_WORK/"
    timeout 1800 powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(native "$WIN_WORK/render-measure.ps1")" \
      -Deck "$(native "$WIN_WORK/deck.pptx")" -OutDir "$(native "$out")" -Json "$(native "$WIN_WORK/$1")" | tr -d '\r' && return 0
    echo "WARN PowerPoint render failed; trying LibreOffice"
  fi
  command -v soffice >/dev/null || { echo "WARN no renderer: previews skipped"; return 1; }
  rm -rf "$out" && mkdir -p "$out"
  soffice --headless -env:UserInstallation=file:///tmp/ugm-lo --convert-to pdf --outdir "$out" "$(deck)" >/dev/null 2>&1
  pdftoppm -png -r 60 "$out"/*.pdf "$out/slide" && rm -f "$out"/*.pdf
  echo '{}' > "$WIN_WORK/$1"
}
find_validate() {
  find "$HOME/.claude" -path '*pptx/scripts/office/validate.py' 2>/dev/null | head -1
}
cmd_build() {
  need_init
  mkdir -p "$WIN_WORK"
  local d; d="$(deck)"
  local args=("$TEMPLATE" "$GUIDE_DIR/screenshots" "$d" "$BUILD/heights.json" "$BUILD")
  GUIDE_VERSION="${GUIDE_VERSION:-1}" "$PY" -E "$ENGINE/build.py" "${args[@]}"
  if render measure.json && [ -s "$WIN_WORK/measure.json" ] && [ "$(cat "$WIN_WORK/measure.json")" != "{}" ]; then
    "$PY" -E "$ENGINE/build.py" --heights-from "$WIN_WORK/measure.json" "$BUILD/manifest.json" "$BUILD/heights.json"
    "$PY" -E "$ENGINE/build.py" "${args[@]}"
    render measure-final.json || true
  fi
  if [ -d "$WIN_WORK/render" ]; then rm -f "$GUIDE_DIR/previews/"*.png; cp "$WIN_WORK/render/"*.png "$GUIDE_DIR/previews/" 2>/dev/null || true; fi
  local v; v="$(find_validate)"
  if [ -n "$v" ]; then PYTHONPATH="$ENGINE/shim" "$PY" -E "$v" "$d" --original "$TEMPLATE" | tail -5
  else echo "note: the pptx skill's validate.py was not found; the deck was not schema-checked"; fi
  echo "deck: $d"
}
cmd_sheets() {
  local src="${1:-$GUIDE_DIR/previews}" outdir="${TMPDIR:-/tmp}/userguide-sheets"
  mkdir -p "$outdir"; rm -f "$outdir"/sheet-*.jpg
  "$PY" "$ENGINE/sheet.py" "$src" "$outdir/sheet"
}

case "${1:-}" in
  init) shift; cmd_init "$@" ;;
  preflight) cmd_preflight ;;
  read) cmd_read ;;
  capture) shift; cmd_capture "$@" ;;
  look) cmd_look ;;
  build) cmd_build ;;
  sheets) shift; cmd_sheets "$@" ;;
  *) sed -n '2,20p' "$0"; exit 2 ;;
esac
