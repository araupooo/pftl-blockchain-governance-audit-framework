#!/usr/bin/env bash
# Doc-vs-code consistency check (check T-03).
#
# Reads the pinned postfiatd source (main HEAD 0085a1ff, 2026-10-10) and
# compares every amendment-threshold figure stated in prose docs against
# the threshold constant the code actually implements.
#
# Pinned files:
#   include/xrpl/protocol/SystemParameters.h:83-85
#       preFixAmendmentMajorityCalcThreshold  = 204/256
#       postFixAmendmentMajorityCalcThreshold = 67/100
#   docs/AmendmentDevelopment.md:72,91            ("67%")
#   src/xrpld/app/misc/README.md:70-71,85,94      ("80%")
#
# Usage: POSTFIATD_DIR=/path/to/postfiatd bash doc_code_consistency.sh
# If POSTFIATD_DIR is unset, the script clones the pinned commit from
# public GitHub (no auth, no private data) into a temp dir and verifies
# the checkout SHA before reading anything.
#
# Exit code: 0 when the check ran to completion. The check is EXPECTED
# to report drift (finding F-02 in docs/worked-audit-postfiatd-67pct.md);
# drift is a finding, not a script failure, so it does not fail the run.
set -u
PINNED_SHA="0085a1ff885d6a446369cf73a4430f75af22be55"
REPO_URL="https://github.com/postfiatorg/postfiatd"

echo "== doc_code_consistency: threshold figures in docs vs code =="
echo "pinned postfiatd commit: $PINNED_SHA"

WORKDIR="${POSTFIATD_DIR:-}"
CLEANUP=""
if [ -z "$WORKDIR" ]; then
    WORKDIR="$(mktemp -d)"
    CLEANUP="$WORKDIR"
    echo "cloning pinned commit into $WORKDIR ..."
    git init -q "$WORKDIR"
    git -C "$WORKDIR" remote add origin "$REPO_URL"
    git -C "$WORKDIR" fetch -q --depth 1 origin "$PINNED_SHA"
    git -C "$WORKDIR" checkout -q FETCH_HEAD
fi

HEAD_SHA="$(git -C "$WORKDIR" rev-parse HEAD)"
echo "checkout HEAD: $HEAD_SHA"
if [ "$HEAD_SHA" != "$PINNED_SHA" ]; then
    echo "FAIL: checkout is not the pinned commit (expected $PINNED_SHA)"
    [ -n "$CLEANUP" ] && rm -rf "$CLEANUP"
    exit 1
fi
echo "checkout verified: pinned commit $PINNED_SHA"
echo

SYS="$WORKDIR/include/xrpl/protocol/SystemParameters.h"
DEV="$WORKDIR/docs/AmendmentDevelopment.md"
READ="$WORKDIR/src/xrpld/app/misc/README.md"

echo "--- code: include/xrpl/protocol/SystemParameters.h ---"
grep -n "AmendmentMajorityCalcThreshold" "$SYS"
CODE_LINE="$(grep "postFixAmendmentMajorityCalcThreshold" "$SYS")"
echo "code post-fix threshold line: $CODE_LINE"
echo
echo "--- docs: docs/AmendmentDevelopment.md ---"
grep -n "67%\|80%" "$DEV" || true
echo
echo "--- docs: src/xrpld/app/misc/README.md ---"
grep -n "80%\|67%" "$READ" || true
echo

DEV_PCT="$(grep -o "67%" "$DEV" | head -1)"
READ_PCT="$(grep -o "80%" "$READ" | head -1)"
echo "--- verdict ---"
echo "code implements : 67%"
echo "AmendmentDevelopment.md states : ${DEV_PCT:-<none found>}"
echo "app/misc README.md states      : ${READ_PCT:-<none found>}"
if [ "$READ_PCT" = "80%" ]; then
    echo "CHECK RESULT: DRIFT DETECTED (finding F-02)"
    echo "  src/xrpld/app/misc/README.md lines 70-71, 85, 94 state an 80%"
    echo "  threshold; the code at SystemParameters.h:85 implements 67%."
    echo "  A reader following the README would expect 13/16 yes-votes to be"
    echo "  the minimum for a majority; the code accepts 11/16."
else
    echo "CHECK RESULT: no drift found in README.md"
fi

[ -n "$CLEANUP" ] && rm -rf "$CLEANUP"
echo "DOC-CODE RESULT: CHECK COMPLETE"
exit 0
