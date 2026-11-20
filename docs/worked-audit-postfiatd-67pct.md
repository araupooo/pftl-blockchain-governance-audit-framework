# Worked Audit: postfiatd's 67% Amendment Threshold

**Scope:** postfiatd, main HEAD `0085a1ff` (2026-10-10), as checked out
and pinned. The audited change: the post-fix amendment majority
threshold is 67/100 instead of the XRPL-standard 80/100.

**Method:** the framework in `docs/checklist.md`, applied control by
control. Every measured claim traces to a runnable script and its
unedited log (`outputs/`) or to a pinned source line (verified by
`grep -n` on the local checkout of `0085a1ff`). Claims are labelled
[FAKTA] (verified, source + date), [ESTIMASI] (modelled/reported
number), [ANALISIS] (interpretation).

**Result:** PASS 10 / 24, FAIL 3 / 24, NOT-EVALUATED 11 / 24 (see
`docs/scoring-rubric.md`). No Critical FAILs; three Major FAILs.

## The change, as found

[FAKTA] `include/xrpl/protocol/SystemParameters.h:83-85` (pinned
commit `0085a1ff`, verified 2026-11-20):

```cpp
constexpr std::ratio<204, 256> preFixAmendmentMajorityCalcThreshold;
constexpr std::ratio<67, 100> postFixAmendmentMajorityCalcThreshold;
```

[FAKTA] Upstream rippled master (fetched 2026-11-20) uses
`constexpr std::ratio<80, 100> kAmendmentMajorityCalcThreshold;`
(`SystemParameters.h:76`). The 80% figure is independently confirmed
by the xrpl.org amendments documentation.

[FAKTA] `docs/AmendmentDevelopment.md:72` states the 67% rule:
"Once 67% of trusted validators vote yes for 2 weeks, the amendment
activates", and line 91: "activates automatically when 67% threshold
is reached".

[FAKTA] The voting logic itself is unchanged from upstream: PR #53's
body (GitHub API, 2026-11-20) states production
`src/xrpld/app/misc/detail/AmendmentTable.cpp` and `AmendmentTable.h`
"are byte-identical to xrplf/rippled 2.5.0 (commit
1e01cd34f7a216092ed779f291b43324c167167a); `doVoting` has zero
divergence. The divergence is the post-fix majority threshold."
The two-week hold is unchanged (`SystemParameters.h:88`:
`defaultAmendmentMajorityTime = std::chrono::weeks{2}`).

## Measured consequences

[FAKTA] Re-derived in `scripts/threshold_arithmetic.py`
(`outputs/threshold_arithmetic.log`, ALL CHECKS PASSED):

| Trusted validators (N) | postfiatd 67% (min yes) | upstream 80% (min yes) | Gap |
|---:|---:|---:|---:|
| 10 | 7 | 9 | 2 |
| 16 | 11 | 13 | 2 |
| 35 (default UNL) | 24 (68.57%) | 29 (82.86%) | 5 |
| 100 | 68 | 81 | 13 |

[FAKTA] Over N = 1..200, the postfiatd rule never activates below 67%
(minimum fraction 0.6701) and the upstream rule never below 80%
(minimum 0.8010). The postfiatd bar is weaker than upstream for every
N, strictly weaker for N >= 4 except N = 6 (small-N ties: N = 1, 2, 3
require unanimity under both rules; N = 6 needs 5/6 under both).

[FAKTA] The PR #53 boundary values re-derive exactly: 11/16 is the
first majority under 67%; 13/16 under 80%; majority is lost at 10/16
(67%) and 12/16 (80%); with 10 validators, 6 yes-votes is no majority
and 8 yes-votes is a majority under 67%.

[ANALISIS] 67% sits just above the 2/3 BFT boundary. The margin
between "governance supermajority" and "minimum consensus quorum"
effectively disappears: a coalition that can stall consensus (just
over 1/3) is only a few validators short of passing a rule change.
Whether that is a deliberate design choice is not documented anywhere
in the repo — see F-01.

## Findings

### F-01 — No written rationale for lowering the threshold (Major)
- Controls: G-01 (FAIL).
- [FAKTA] No design document, ADR, or pull-request body in the repo
  justifies 67%. The threshold constant changed; the reason did not
  travel with it. PR #53's body documents the *consequences* of 67%
  (boundary-test updates) but not the *reason* for 67%.
- [ANALISIS] A governance bar is a security parameter. Changing it
  without a written rationale means no reviewer can tell a deliberate
  choice from an error, and no future auditor can tell whether the
  value is still right.
- Fix: publish a short rationale (threat model, why 67% and not 80%
  or 75%, who approved it) and link it from
  `docs/AmendmentDevelopment.md`.

### F-02 — Docs state 80%, code implements 67% (Major)
- Controls: G-17 (FAIL).
- [FAKTA] `src/xrpld/app/misc/README.md:70-71`: "An Amendment must
  receive at least an 80% approval rate from validating nodes for a
  period of two weeks before being accepted." Line 85: "If the
  Amendment holds an 80% majority for a two week period, nodes will
  begin including the transaction to enable it". Line 94: "If 80%
  support is achieved, they will introduce a pseudo-transaction to
  track the amendment's majority status in the ledger."
- [FAKTA] The code implements 67% (`SystemParameters.h:85`).
  Detected by `scripts/doc_code_consistency.sh`
  (`outputs/doc_code_consistency.log`: "CHECK RESULT: DRIFT DETECTED").
- [ANALISIS] An operator following the README would expect 13/16
  yes-votes to be the minimum for a majority; the code accepts 11/16.
  The drift is in the oldest, most-read governance doc in the tree.
- Fix: update the README to 67% (or restore 80% in code, with the
  F-01 rationale either way) and add the doc-vs-code check to CI.

### F-03 — No vote-ordering / replay test in the tree (Major)
- Controls: G-13 (FAIL).
- [FAKTA] `grep -i replay src/test/app/AmendmentTable_test.cpp`
  returns nothing in `0085a1ff`. The outcome of an amendment vote is
  supposed to depend only on the *set* of trusted validations in the
  flag-ledger window, not their arrival order — but no test in the
  tree proves it.
- [FAKTA] PR #53 (open, 0 reviews, mergeable, last updated
  2026-11-13T23:18:29Z, re-checked 2026-11-20) adds
  `testVoteReplayOrderIndependent` and updates three boundary tests
  to 67%. It is the existing work; this pack integrates it rather
  than rebuilding it (see `docs/vote-replay-integration.md`).
- [FAKTA] The Python model in `scripts/vote_order_replay.py`
  replays the same votes in 3 orders × 2 reps: week-2 canonical
  trace `4929839647ee28978157de0c2a0eb98b90925aeee94ba28f8fc81c2fc9c8a968`
  and week-4 trace
  `105bb981d691228ef5ef2ea8e5632e57bd3c2116e89a39aa5679e99718652195` are
  identical across all runs. Duplicates count once, stale-window
  votes are ignored, and a vote flip (V10 yes→no) drops amendment B
  to 10/16 with no majority.
- Fix: merge PR #53 (or an equivalent replay test) and run the
  `ripple.app.AmendmentTable` suite in CI, as the PR's workflow
  change does.

### F-04 — Majority-clock fragility is unmonitored (observation)
- Controls: G-18 (PASS — mechanism verified; monitoring is the gap).
- [FAKTA] The clock rule works as specified
  (`scripts/majority_clock.py`, ALL CHECKS PASSED): a dip below
  threshold resets the two-week hold.
- [ESTIMASI] Worked example from reported data (CoinStats 2026-10-22
  / Odaily 2026-10-25, citing XRPLWin; secondary reporting, not
  directly queried): `fixCleanup3_4_0` first reached majority
  2026-10-09, support dipped to 26/35 (74.29%) for ~2 hours on
  2026-10-21, and the re-derived activation moved from 2026-10-23 to
  2026-11-04 — a 12-day delay from a 2-hour dip.
- [ANALISIS] The framework's G-18 check should run continuously
  against live amendments: how close has each one come to losing
  majority, and what would a transient dip cost.

### F-05 — ValidatorVoteTracker: gating and pruning verified; dedup model only (observation)
- Controls: G-24 (PASS), G-14/G-15 (PASS by model).
- [FAKTA] `ttVALIDATOR_VOTE` is rejected with `temDISABLED` unless
  `featurePF_ValidatorVoteTracking` is enabled
  (`src/xrpld/app/tx/detail/Change.cpp:96-101`); the feature is
  `DefaultNo` (`features.macro:45-46`); votes carry the validation
  hash as proof (`RCLValidations.cpp:197-216`); duplicates are
  skipped per ledger (`ValidatorVoteTracker.cpp:83`); old records are
  pruned to the last 10 ledgers (`ValidatorVoteTracker.cpp`,
  cleanup: "Keep votes for the last 10 ledgers").
- [FAKTA] Modelled in `scripts/validator_vote_tracker.py`
  (ALL CHECKS PASSED): same batch in 3 orders yields the same 4
  transactions and identical canonical trace; a second `doVoting`
  for the same ledger generates 0 new transactions; disabled
  amendment yields `temDISABLED` and 0 transactions; after ledgers
  1..25 only ledgers 16..25 are retained.
- Note: this is a model of the documented rules, not the C++ code.
  The authoritative check is the C++ suite.

### F-06 — Fee-vote median flips at 18/35, not at a supermajority (observation)
- Controls: G-20 (PASS).
- [FAKTA] Fee settings follow the median of trusted validators'
  preferences (xrpl.org fee-voting docs). Reference fee 10 drops;
  reserves 1 / 0.2 XRP since 2024-12-02.
- [FAKTA] Measured in `scripts/quorum_arithmetic.py`: 17/35
  validators preferring 0 drops leaves the median at 10; 18/35
  (51.4%) flips the median to 0. The bar for changing fees is a
  bare majority, not a supermajority — and the docs themselves flag
  the DoS exposure if low requirements are adopted by >50%.
- [ANALISIS] Fee voting is the one governance lever where a bare
  majority suffices. An audit should state the flip point (18/35)
  next to the amendment threshold (24/35), so the two bars are never
  confused.

## Control scores (detail)

PASS: G-03 (two-week hold is the delay, `SystemParameters.h:88`),
G-07 (threshold re-derived, `threshold_arithmetic.py`), G-10
(validator-set changes at flag ledgers, `doVoting` flow),
G-12 (Negative UNL cap 25% / floor 60% / halt at 8 of 35,
`quorum_arithmetic.py`), G-14 (dedup, `vote_order_replay.py`),
G-15 (stale votes ignored, latest wins, `vote_order_replay.py`),
G-16 (boundaries N=1..200 + PR #53 values, `threshold_arithmetic.py`),
G-18 (clock rule + re-derived fixCleanup3_4_0 timeline,
`majority_clock.py`), G-20 (fee median + 18/35 flip point,
`quorum_arithmetic.py`), G-24 (gating, dedup, pruning,
`validator_vote_tracker.py`).

FAIL: G-01 (F-01), G-13 (F-03), G-17 (F-02).

NOT-EVALUATED: G-02 (no public proposal forum record found for this
change), G-04 (retirement path not examined), G-05/G-06 (validator
votes are not liquid/acquirable tokens — snapshot and acquisition-cost
checks do not apply the same way), G-08/G-09 (postfiatd validator
concentration and voter-class distribution not measured — no public
validator list examined), G-11 (UNL overlap not measured — no UNL set
published for postfiatd examined), G-19 (no emergency execution path
in the amendment mechanism examined), G-21 (no social-layer decision
examined for this change), G-22/G-23 (validator key custody not
examined).
