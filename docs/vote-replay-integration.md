# Vote-Replay Integration: PR #53

This pack integrates the existing vote-replay work instead of
rebuilding it. The existing work is PR #53 in postfiatd:

- Title: "Test amendment vote replay with reordered validations"
- Branch: `test/amendment-vote-replay-order`, head `4f718711`
- Status (GitHub API, re-checked 2026-11-20): open, not merged,
  0 reviews, mergeable, mergeable_state unstable, last updated
  2026-11-13T23:18:29Z
- Files changed: `.github/workflows/pr-check.yml`,
  `src/test/app/AmendmentTable_test.cpp` (+435/−13 across 2 files,
  2 commits). No production consensus code is changed.

## What PR #53 does

From the PR body (quoted, GitHub API 2026-11-20):

> Adds a repeatable regression test proving amendment-vote outcomes do
> not depend on the order in which validator validations are supplied,
> and updates three existing boundary tests to postfiatd's 67%
> majority threshold.

> `testVoteReplayOrderIndependent` (in `AmendmentTable_test.cpp`)
> replays the same fixed validator votes in three validation orders
> (creation order, reversed, left-rotation by 5), twice per order, on
> a fresh table each time, and asserts identical vote actions and
> majority/enabled states at the threshold (week 2) and after the
> majority hold time (weeks 4-5). Each round also records a canonical
> state trace and its SHA-256, asserted equal across all runs.

> Two amendments are exercised: 13/16 yes-votes (a majority under
> both the postfiatd and upstream rules) and 11/16 yes-votes (a
> majority only under postfiatd's 67% rule).

Boundary-test updates in the PR:

- `testDetectMajority`: majority first at 11/16 (fix-ON) instead of
  13/16; enable at week 13 instead of 15. Pre-fix expectations
  unchanged.
- `testLostMajority`: majority lost when yes-votes drop to 10/16
  (fix-ON) instead of 12/16.
- `testChangedUNL`: with 10 validators, 8 yes-votes are already a
  majority under 67%, so the no-majority blocks use 4 dissenters
  (6 yes-votes) instead of 2.

The PR also adds the `ripple.app.AmendmentTable` suite to the
PR-check workflow so the test executes in CI.

## What this pack adds (and does not rebuild)

This pack does **not** re-implement the C++ test. It adds:

1. `scripts/vote_order_replay.py` — a small, runnable Python model
   of the same invariant over the documented `AmendmentTable` logic
   (`computeThreshold`, `passes`, `doVoting`). Same vote sets
   (13/16 and 11/16), same three orders × two reps, same canonical
   state-trace SHA-256 comparison. An auditor can run it without
   building postfiatd. The C++ test remains the authoritative check;
   the model is the portable one.
2. `scripts/threshold_arithmetic.py` — re-derives the PR's boundary
   values (11/16, 13/16, 10/16, 12/16, 6 vs 8 of 10) from the
   threshold formula, and extends them to N = 1..200.
3. `docs/worked-audit-postfiatd-67pct.md` finding F-03 — records that
   no replay test exists in the tree today, because the PR is still
   open/unmerged.
4. Checklist control G-13 — requires a replay test in-tree and in CI,
   which is exactly what PR #53 delivers once merged.

## What the model cannot prove (honest limits)

- The Python model mirrors the *documented* logic; it is not the
  C++ code. A bug in the C++ implementation that the documentation
  does not describe would not show up here.
- The model uses fixed, synthetic vote sets. It does not run the
  real `AmendmentTable` state machine, the real flag-ledger timing,
  or real validator keys.
- The model's "enable at week 4" step compresses the PR's
  weeks 4–5 hold check into a single round; the hold duration (2
  weeks) is verified separately in `scripts/majority_clock.py`.

## Status note

As of 2026-11-20 the PR is still open with 0 reviews. The worked
audit scores G-13 FAIL until it (or an equivalent test) is merged.
Nothing in this pack depends on the PR merging — the model scripts
stand on their own — but the in-tree gap is real and recorded.
