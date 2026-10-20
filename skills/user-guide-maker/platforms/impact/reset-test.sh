#!/usr/bin/env bash
# Put the guide's demo test back to the blank state a new IMPACT component starts in,
# so the "from scratch" walkthrough can be re-captured. Touches ONLY the demo test
# (default SO2GKM679H, "Snack Shelf Test") and its own Recent Changes history.
#
# The blank state is backup/<CODE>-blank.json, exported right after the test was
# created through Api\SurveyController::store (the endpoint Fluent calls).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CODE="${DEMO_CODE:-SO2GKM679H}"
BLANK="$HERE/backup/$CODE-blank.json"
[ -f "$BLANK" ] || { echo "no blank snapshot at $BLANK"; exit 1; }
[ "$CODE" != "ABUVANIDYQ" ] || { echo "refusing to reset ABUVANIDYQ (the user's own test)"; exit 1; }

docker cp "$BLANK" impact:/tmp/guide-blank.json
docker exec -w /app impact php artisan tinker --execute='
$d = json_decode(file_get_contents("/tmp/guide-blank.json"), true);
$t = \App\Models\Test::where("code", $d["code"])->firstOrFail();
$t->images = $d["images"];
$t->global_settings = $d["global_settings"];
$t->instructions = $d["instructions"];
$t->result_settings = $d["result_settings"];
$t->save();
$n = \App\Models\RecentChange::where("test_id", $t->id)->delete();
echo "reset ".$t->code." (".$t->name."), cleared ".$n." history rows".PHP_EOL;
' 2>&1 | grep -E "reset|Exception|Error"
