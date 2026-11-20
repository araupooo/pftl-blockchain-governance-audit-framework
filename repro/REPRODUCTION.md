# Reproduction

Reproduce the worked audit from a fresh clone with one documented
command. No private data, no credentials, no spending. One step
needs network: `scripts/doc_code_consistency.sh` clones the pinned
postfiatd commit from public GitHub (or set `POSTFIATD_DIR` to a
local checkout to skip the clone).

## One command

```bash
bash scripts/run_all.sh
```

## What it does

1. Runs the 7 checks in order: threshold arithmetic, vote-order
   replay, doc-vs-code consistency, majority clock, quorum
   arithmetic, validator vote tracking, incident replay.
2. Writes one unedited log per check into `outputs/`.
3. Prints a summary and exits 0 only if every check completed.

## Expected result

```
THRESHOLD RESULT: ALL CHECKS PASSED
REPLAY RESULT: ALL CHECKS PASSED
CHECK RESULT: DRIFT DETECTED (finding F-02)
DOC-CODE RESULT: CHECK COMPLETE
CLOCK RESULT: ALL CHECKS PASSED
QUORUM RESULT: ALL CHECKS PASSED
TRACKER RESULT: ALL CHECKS PASSED
INCIDENT RESULT: ALL CHECKS PASSED
RUN_ALL RESULT: ALL CHECKS PASSED
```

Note: "DRIFT DETECTED" is the doc-vs-code check working as designed
— it reports the finding (README states 80%, code implements 67%)
and the run still passes. The finding is F-02 in
`docs/worked-audit-postfiatd-67pct.md`.

## Spot values to confirm the run is real

- Threshold: N=35 needs 24 yes-votes under 67% vs 29 under 80%
  (gap 5 validators); N=16 needs 11 vs 13.
- Replay: week-2 canonical trace
  `4929839647ee28978157de0c2a0eb98b90925aeee94ba28f8fc81c2fc9c8a968`
  and week-4 trace
  `105bb981d691228ef5ef2ea8e5632e57bd3c2116e89a39aa5679e99718652195`,
  identical across 3 orders × 2 reps.
- Majority clock: re-derived fixCleanup3_4_0 activation 2026-11-04,
  12-day delay from a ~2-hour dip.
- Quorum: Negative UNL cap 8, quorum floor 21, static quorum 28,
  halt at 8 of 35 offline; fee median flips at 18/35.
- Tracker: 4 transactions per batch, dedup order-independent,
  `temDISABLED` when the amendment is off, last 10 ledgers retained.

## Requirements

- `python3` (3.8+), `bash`, `git`, `curl` (only for the pinned
  postfiatd clone inside `doc_code_consistency.sh`).
- No other dependencies. All scripts are deterministic: fixed
  inputs, no wall-clock dependence, no randomness.
