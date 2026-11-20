# Blockchain Governance-Audit Framework

A reusable, public, inspectable framework for auditing blockchain
governance — proposal lifecycles, validator voting power and quorum
arithmetic, validator-set changes, vote ordering/replay, and decision
traceability — with runnable scripts, a worked audit, and a
primary-source-cited failure-mode catalogue.

## What is in here

- `docs/checklist.md` — 24 controls (G-01..G-24) in 7 domains, each
  with the evidence required and the detection check that decides
  PASS / FAIL.
- `docs/scoring-rubric.md` — score as counts per control (PASS /
  FAIL / NOT-EVALUATED), never as a single numeric rating. Includes
  the worked-audit score.
- `docs/worked-audit-postfiatd-67pct.md` — the framework applied to
  one real governance case from public records: postfiatd lowered
  its amendment threshold from 80% to 67% with no written rationale,
  while its README still states 80%. Score: PASS 10 / 24, FAIL 3 /
  24, NOT-EVALUATED 11 / 24. No Critical FAILs; three Major FAILs
  (F-01 no rationale, F-02 doc-vs-code drift, F-03 no replay test
  in-tree).
- `docs/failure-mode-catalogue.md` — 8 documented incidents
  (XRPL clock reset, XRPL lost majority, XRPL rounding bug, Neutron
  governance attack, Beanstalk flash-loan takeover, Solana SIMD-228,
  Ethereum DAO fork, Blockdaemon key compromise), each with a primary
  source, mechanism, detection check, and mapped control.
- `docs/vote-replay-integration.md` — how the existing vote-replay
  work (PR #53, still open/unmerged) is integrated rather than
  rebuilt, and the honest limits of the Python model.
- `docs/claims.md` — claim-to-evidence index: every substantive
  claim maps to a script log or a cited primary source.
- `scripts/` — 7 runnable checks (threshold arithmetic, vote-order
  replay, doc-vs-code consistency, majority clock, quorum arithmetic,
  validator vote tracking, incident replay) plus `run_all.sh`.
- `outputs/` — unedited logs from a full run of `run_all.sh`.
- `SOURCES.md` — primary-source index.

## Headline findings (worked audit)

- postfiatd implements a 67% amendment threshold
  (`SystemParameters.h:85`, commit `0085a1ff`) where upstream
  rippled uses 80%. At the default UNL size of 35, that is 24
  yes-votes instead of 29 — a gap of 5 validators.
- The tree's most-read governance doc still states 80%
  (`src/xrpld/app/misc/README.md:70-71,85,94`). An operator
  following it would expect 13/16 yes-votes as the minimum; the
  code accepts 11/16.
- No vote-ordering/replay test exists in the tree. PR #53 adds one;
  it is open with 0 reviews. The pack's Python model replays the
  PR's vote sets (13/16 and 11/16) in 3 orders × 2 reps with
  identical canonical traces.
- A ~2-hour dip below threshold costs 12 days of activation delay
  (re-derived from the reported fixCleanup3_4_0 timeline).
- Fee voting flips at 18/35 validators preferring 0 drops — a bare
  majority, not a supermajority.

## Quickstart

```bash
bash scripts/run_all.sh
```

Runs all 7 checks and writes unedited logs to `outputs/`. No network
except one step: `scripts/doc_code_consistency.sh` clones the pinned
postfiatd commit (`0085a1ff`) from public GitHub to read the exact
lines it audits (or set `POSTFIATD_DIR` to a local checkout). No
private data, no credentials, no spending.

Reproduce from a fresh clone with one command — see
`repro/REPRODUCTION.md`.

## Scope and limits

- The framework is a synthesis (Tech-Audit.org, Blockready,
  EEA DeFi Risk Guidelines / Galaxy SeC FiT PrO, ChainScore). No
  canonical governance-audit standard exists.
- The Python scripts model documented protocol logic; they are not
  the protocol code. The C++ test suite remains authoritative where
  it exists.
- The fixCleanup3_4_0 timeline is reported (secondary sources citing
  XRPLWin), not directly queried; it is labelled as reported wherever
  used.
- The worked audit covers one change (the 67% threshold) in one
  codebase at one pinned commit. Controls scored NOT-EVALUATED are
  explicit gaps in coverage, not passes.
