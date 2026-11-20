# Claim-to-Evidence Index

Every substantive claim in this pack maps to a runnable script and its
unedited log, or to a cited primary source. Labels: [FAKTA] verified
fact with source + date; [ESTIMASI] modelled/reported number;
[ANALISIS] interpretation.

## Threshold and majority arithmetic

| # | Claim | Evidence |
|---|---|---|
| C-01 | [FAKTA] postfiatd post-fix threshold is 67/100 (`SystemParameters.h:85`, `0085a1ff`) | `outputs/doc_code_consistency.log`; `outputs/threshold_arithmetic.log` |
| C-02 | [FAKTA] Upstream rippled master threshold is 80/100 (`SystemParameters.h:76`, fetched 2026-11-20) | SOURCES.md #9; `outputs/threshold_arithmetic.log` (upstream rule) |
| C-03 | [FAKTA] 11/16 first majority under 67%; 13/16 under 80%; lost at 10/16 and 12/16; N=10: 6 no / 8 yes under 67% | `outputs/threshold_arithmetic.log` (PR53 checks); PR #53 body, SOURCES.md #10 |
| C-04 | [FAKTA] Pre-fix, 28/36 = 77.78% could activate (rounding bug) | `outputs/threshold_arithmetic.log` (BUG checks); xrpl.org Known Amendments, SOURCES.md #5 |
| C-05 | [FAKTA] Postfiatd rule never activates below 67% (min 0.6701), upstream never below 80% (min 0.8010), N=1..200 | `outputs/threshold_arithmetic.log` (POSTFIX checks) |
| C-06 | [FAKTA] At N=35: postfiatd needs 24 (68.57%), upstream 29 (82.86%), gap 5 validators | `outputs/threshold_arithmetic.log` (UNL35 checks) |
| C-07 | [FAKTA] Small-N ties are exactly N=1,2,3 (unanimity) and N=6 (5/6) | `outputs/threshold_arithmetic.log` (DIVERGENCE checks) |

## Vote ordering / replay

| # | Claim | Evidence |
|---|---|---|
| D-01 | [FAKTA] Same votes in 3 orders × 2 reps give identical canonical traces (week 2: `4929839647ee28978157de0c2a0eb98b90925aeee94ba28f8fc81c2fc9c8a968`; week 4: `105bb981d691228ef5ef2ea8e5632e57bd3c2116e89a39aa5679e99718652195`) | `outputs/vote_order_replay.log` |
| D-02 | [FAKTA] 13/16 passes under both rules; 11/16 passes only under 67% | `outputs/vote_order_replay.log` (BOUNDARY checks) |
| D-03 | [FAKTA] Duplicates count once; stale-window votes ignored; vote flip drops B to 10/16, no majority | `outputs/vote_order_replay.log` (DEDUP/STALE/VOTE-CHANGE checks) |
| D-04 | [FAKTA] Losing majority clears the recorded majority time (clock restarts) | `outputs/vote_order_replay.log` (CLOCK checks) |
| D-05 | [FAKTA] No replay test exists in postfiatd `0085a1ff` (`grep -i replay` on `AmendmentTable_test.cpp` returns nothing); PR #53 adds it, still open/unmerged as of 2026-11-20 | `docs/vote-replay-integration.md`; GitHub API, SOURCES.md #10 |

## Doc-vs-code drift

| # | Claim | Evidence |
|---|---|---|
| S-01 | [FAKTA] README (`src/xrpld/app/misc/README.md:70-71,85,94`) states 80%; code implements 67% | `outputs/doc_code_consistency.log` (DRIFT DETECTED) |
| S-02 | [FAKTA] `docs/AmendmentDevelopment.md:72,91` states 67%, consistent with code | `outputs/doc_code_consistency.log` |
| S-03 | [ANALISIS] A reader following the README expects 13/16 as the minimum; the code accepts 11/16 | F-02 in `docs/worked-audit-postfiatd-67pct.md` |

## Majority clock

| # | Claim | Evidence |
|---|---|---|
| K-01 | [FAKTA] A mid-hold dip resets the two-week clock; activation is 14 days after the restart | `outputs/majority_clock.log` (RULE checks) |
| K-02 | [ESTIMASI] fixCleanup3_4_0: dip to 26/35 (74.29%) on 2026-10-21 for ~2 hours; re-derived activation 2026-11-04; 12-day delay (reported timeline, CoinStats/Odaily citing XRPLWin) | `outputs/majority_clock.log` (EXAMPLE checks); SOURCES.md #21 |
| K-03 | [FAKTA] A dip after activation does not un-enable | `outputs/majority_clock.log` (BOUNDARY check) |

## Quorum and fee voting

| # | Claim | Evidence |
|---|---|---|
| Q-01 | [FAKTA] UNL overlap worst-case bound >90% (Chase & MacBrough 2018); whitepaper ~20%; independent analysis >40% | `outputs/quorum_arithmetic.log` (OVERLAP checks); SOURCES.md #7 |
| Q-02 | [FAKTA] Negative UNL cap 8 of 35 (25%); quorum floor 21 (60%); static quorum 28 (80%) | `outputs/quorum_arithmetic.log` (NEGUNL checks); `NegativeUNLVote.h:76-78` |
| Q-03 | [FAKTA] 8+ of 35 offline stops progress under the static 80% rule | `outputs/quorum_arithmetic.log` (HALT checks) |
| Q-04 | [FAKTA] Fee median flips at 18/35 preferring 0 drops (17/35 leaves it at 10) | `outputs/quorum_arithmetic.log` (FEE checks) |
| Q-05 | [FAKTA] Reserves 1 / 0.2 XRP, reference fee 10 drops, since 2024-12-02 | xrpl.org fee-voting docs, SOURCES.md #4 |

## Validator vote tracking

| # | Claim | Evidence |
|---|---|---|
| V-01 | [FAKTA] Same batch in 3 orders yields the same 4 transactions and identical canonical trace | `outputs/validator_vote_tracker.log` (DEDUP checks) |
| V-02 | [FAKTA] Second `doVoting` for the same ledger generates 0 new transactions | `outputs/validator_vote_tracker.log` (REPLAY check) |
| V-03 | [FAKTA] Disabled amendment yields `temDISABLED` and 0 transactions (`Change.cpp:96-101`) | `outputs/validator_vote_tracker.log` (GATE check) |
| V-04 | [FAKTA] After ledgers 1..25, only the last 10 are retained | `outputs/validator_vote_tracker.log` (PRUNE checks) |
| V-05 | [FAKTA] Generated transactions carry the validation hash as proof | `outputs/validator_vote_tracker.log` (PROOF check) |

## Incidents

| # | Claim | Evidence |
|---|---|---|
| I-01..I-08 | [FAKTA] The 8 catalogue incidents, each with its primary source, mechanism, detection check, and mapped control; verdicts CAUGHT 5 / AS-DESIGNED 2 / GAP 1 | `outputs/incident_replay.log`; `docs/failure-mode-catalogue.md` |

## Worked-audit verdict

| # | Claim | Evidence |
|---|---|---|
| W-01 | [FAKTA] Worked audit scores PASS 10 / 24, FAIL 3 / 24 (G-01, G-13, G-17), NOT-EVALUATED 11 / 24; no Critical FAILs | `docs/worked-audit-postfiatd-67pct.md`; `docs/scoring-rubric.md` |
| W-02 | [ANALISIS] 67% sits just above the 2/3 BFT boundary; the margin between governance supermajority and minimum consensus quorum effectively disappears | F-01 in `docs/worked-audit-postfiatd-67pct.md` |
