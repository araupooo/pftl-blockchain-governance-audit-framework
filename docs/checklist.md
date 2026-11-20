# Governance-Audit Checklist

A reusable checklist for auditing blockchain governance. Each control has
an ID, a statement, the evidence an auditor must produce, and the
detection check that decides PASS / FAIL. Score with
`docs/scoring-rubric.md` — as counts per control, never as a single
numeric rating.

Sources for the controls: the XRPL/postfiatd protocol rules verified in
`scripts/` (see `SOURCES.md`), the framework syntheses in §6 of the
research base (Tech-Audit.org checklist, Blockready 7-layer DAO health
framework, EEA DeFi Risk Guidelines / Galaxy SeC FiT PrO, ChainScore
proposal-audit architecture), and the incident catalogue
(`docs/failure-mode-catalogue.md`). No canonical governance-audit
standard exists; this checklist is a synthesis, and each control traces
to a protocol rule or a documented incident.

## A. Proposal lifecycle

### G-01 — Written proposal record
Every governance change has a written record — author, rationale, exact
diff, risk note — published before voting starts.
Evidence: the proposal document or pull-request body.
Detection check: a change with no written rationale is FAIL. (Worked
audit finding F-01: postfiatd's 67% threshold has no in-repo rationale.)

### G-02 — Public discussion window
The proposal is discussed in a public forum for a stated minimum window
before voting opens.
Evidence: forum thread / discussion links with dates.
Detection check: voting opened with no public discussion window is FAIL.

### G-03 — Delay between vote close and execution
A timelock or hold separates the vote from execution, and its length is
stated. (XRPL/postfiatd: the two-week majority hold,
`SystemParameters.h:88`.)
Evidence: the hold/timelock parameter in code or config.
Detection check: no stated delay is FAIL.

### G-04 — Retirement / removal path
Passed changes have a documented removal path (veto, retirement, or a
reversing change). (XRPL: amendments can be vetoed before enabling;
XLS-11d retires amendments after 2 years enabled on Mainnet.)
Evidence: the retirement mechanism in docs or code.
Detection check: no removal path is FAIL.

## B. Voting power and quorum

### G-05 — Voting power snapshotted before proposal creation
Voting power is measured at a snapshot taken before the proposal
exists, so voting power cannot be acquired after seeing the proposal.
Evidence: snapshot block/ledger and the rule that enforces it.
Detection check: voting power acquirable after proposal creation is
FAIL. (Beanstalk 2022, Neutron 2026.)

### G-06 — Acquisition-cost check
The cost to acquire a deciding share of votes is measured and
published alongside the proposal.
Evidence: acquisition-cost computation with market data and date.
Detection check: a deciding share acquirable for less than the value
at stake, with no mitigation, is FAIL. (Neutron: ~$20,200 bought the
vote.)

### G-07 — Threshold arithmetic re-derived from code
The quorum/threshold is recomputed from the code that implements it,
never copied from prose docs. Boundary cases (threshold, ±1 validator)
are tested at each plausible validator-set size.
Evidence: `scripts/threshold_arithmetic.py` output.
Detection check: a threshold figure that cannot be re-derived from code
is FAIL. (XRPL rounding bug: 28/36 = 77.78% activated pre-fix.)

### G-08 — Vote-concentration / swing-vote analysis
The analysis names who holds the deciding votes: which single operator
or coalition can swing the outcome.
Evidence: vote-share table by operator.
Detection check: no concentration analysis is FAIL. (XRPL Jan 2020:
Ripple's own validators swung two amendments.)

### G-09 — Voter-class distribution
Support is recorded by voter class (large vs small validators /
stakers), not just as a single percentage.
Evidence: support breakdown by class.
Detection check: a pass/fail reported without the class breakdown is
FAIL. (Solana SIMD-228: 67.5% of small validators against, 65.8% of
large validators in favor.)

## C. Validator-set changes

### G-10 — Validator-set changes take effect at defined boundaries
Set changes apply only at defined points (e.g. flag ledgers), never
mid-window.
Evidence: the boundary rule in code or docs.
Detection check: a set change that can take effect mid-window is FAIL.

### G-11 — UNL overlap measured against the worst-case bound
Pairwise UNL overlap is measured and compared with the worst-case bound
(>90% per Chase & MacBrough 2018), not the original ~20% belief.
Evidence: overlap measurement over the actual UNL set.
Detection check: overlap below the worst-case bound with no mitigation
is FAIL.

### G-12 — Negative UNL cap and quorum floor verified
Negative UNL listings never exceed 25% of the UNL
(`NegativeUNLVote.h:78`), the quorum never drops below 60% of total
validators, and the halt condition (8+ of 35 offline stops progress)
is documented.
Evidence: `scripts/quorum_arithmetic.py` output.
Detection check: any of the three invariants violated is FAIL.

## D. Vote ordering / replay

### G-13 — Order-independence replay test exists
The same votes, replayed in permuted order, produce identical
outcomes. The test exists in the tree and runs in CI.
Evidence: the replay test + CI run, or `scripts/vote_order_replay.py`.
Detection check: no replay test is FAIL. (postfiatd: none in-tree;
PR #53 adds it, still open/unmerged.)

### G-14 — Duplicate validations count once
A validator's duplicate validation in one window is counted once.
Evidence: dedup rule in code + a replay check.
Detection check: a duplicate changing the count is FAIL.

### G-15 — Stale votes ignored; latest vote wins
Validations from a previous flag window are ignored, and when a
validator changes its vote between windows only the latest counts.
Evidence: replay checks for both cases.
Detection check: a stale vote affecting the outcome is FAIL.

### G-16 — Threshold boundaries tested at each UNL size
For each plausible validator-set size, the cases threshold−1,
threshold, threshold+1 are tested.
Evidence: boundary table (`scripts/threshold_arithmetic.py`).
Detection check: an untested boundary size is FAIL.

## E. Decision traceability

### G-17 — Every decision links to votes, threshold, and activation
Each governance decision has a trace: the votes cast, the threshold
computation, and the activation record.
Evidence: the decision record with links.
Detection check: a decision that cannot be traced to its votes is
FAIL. (Worked audit finding F-02: README states 80%, code does 67%.)

### G-18 — Majority-clock behavior documented
The rule for what resets the majority hold, and the cost of a
transient dip, are documented and computed.
Evidence: `scripts/majority_clock.py` output.
Detection check: no dip-cost analysis for a live amendment is FAIL.
(XRPL Oct 2026: a ~2-hour dip cost 12 days.)

### G-19 — Emergency paths have parity with the ordinary path
Any emergency/fast execution path applies the same (or stricter)
checks as the ordinary path — same snapshot, same threshold, same
delay logic.
Evidence: the emergency path's checks, side by side with the ordinary
path's.
Detection check: an emergency path with weaker checks is FAIL.
(Beanstalk: `emergencyCommit()` divided by current weight.)

## F. Execution controls

### G-20 — Aggregation rule stated for parameter changes
For each parameter change, the aggregation rule is stated (median vs
majority) and the bar is explicit. (XRPL fee voting: median of trusted
preferences; a >50% shift flips it — measured at 18/35.)
Evidence: the rule + the flip point.
Detection check: a parameter change with an unstated aggregation rule
is FAIL.

### G-21 — Social-layer decisions have a written record
Decisions taken off-chain (forums, coin votes, miner signalling,
irregular state changes) have a written decision record that the
on-chain execution links to.
Evidence: the off-chain decision record.
Detection check: an irregular state change with no written record is
FAIL. (Ethereum DAO fork 2016.)

## G. Key custody and operator governance

### G-22 — Validator key custody documented
Where validator keys live, who can copy them, and the off-boarding
procedure are documented.
Evidence: custody document.
Detection check: no custody document is FAIL. (Blockdaemon 2026: keys
copied from a corporate device during off-boarding.)

### G-23 — Withdrawal / vote authority separated
Withdrawal authority and vote authority are separated from day-to-day
operational keys wherever the protocol allows.
Evidence: authority assignment record.
Detection check: a single key holding both is FAIL where separation
is possible.

### G-24 — Vote-recording extensions are gated and bounded
Vote-recording extensions (e.g. `ttVALIDATOR_VOTE` pseudo-transactions)
are rejected unless their amendment is enabled, cannot be forged by
non-validators, dedupe per validator, and prune old records so state
stays bounded.
Evidence: `scripts/validator_vote_tracker.py` output + the gating code
(`Change.cpp:96-101`, `features.macro:45-46`).
Detection check: any of gating / dedup / pruning failing is FAIL.
