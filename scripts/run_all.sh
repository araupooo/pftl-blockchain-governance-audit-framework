#!/usr/bin/env bash
# Run every governance-audit check and capture unedited logs.
# Usage: bash scripts/run_all.sh
# Writes one log per script into outputs/ and prints a summary.
# Exit code: non-zero if any script fails.
set -u

cd "$(dirname "$0")/.." || exit 1
mkdir -p outputs
rm -f outputs/*.log

run() {
    local name="$1"; shift
    echo "--- $name ---"
    if "$@" > "outputs/$name.log" 2>&1; then
        echo "$name: PASS (log: outputs/$name.log)"
    else
        echo "$name: FAIL (log: outputs/$name.log)"
        echo "FAILURES=$name" >> outputs/.failures
    fi
    cat "outputs/$name.log"
    echo
}

rm -f outputs/.failures

run threshold_arithmetic python3 scripts/threshold_arithmetic.py
run vote_order_replay python3 scripts/vote_order_replay.py
run doc_code_consistency bash scripts/doc_code_consistency.sh
run majority_clock python3 scripts/majority_clock.py
run quorum_arithmetic python3 scripts/quorum_arithmetic.py
run validator_vote_tracker python3 scripts/validator_vote_tracker.py
run incident_replay python3 scripts/incident_replay.py

echo "=== SUMMARY ==="
if [ -f outputs/.failures ]; then
    echo "FAILURES:"
    cat outputs/.failures
    rm -f outputs/.failures
    echo "RUN_ALL RESULT: FAILED"
    exit 1
fi
echo "threshold_arithmetic, vote_order_replay, doc_code_consistency,"
echo "majority_clock, quorum_arithmetic, validator_vote_tracker,"
echo "incident_replay: all completed."
echo "RUN_ALL RESULT: ALL CHECKS PASSED"
exit 0
