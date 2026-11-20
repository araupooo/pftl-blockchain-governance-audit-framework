# Scoring Rubric

## How to score

Score each of the 24 controls in `docs/checklist.md` as one of:

| Verdict | Meaning |
|---|---|
| PASS | The control holds, with evidence attached (script output or cited primary source). |
| FAIL | The control does not hold, with the failing evidence attached. |
| NOT-EVALUATED | The audit did not examine this control (state why: out of scope, no data available, or not applicable to this governance design). A NOT-EVALUATED is not a PASS — it is an explicit gap in coverage. |

## Aggregation

Report the aggregate as counts, never as a single numeric rating:

- `PASS x / 24`, `FAIL y / 24`, `NOT-EVALUATED z / 24`, with x + y + z = 24.
- List every FAIL with its finding ID, severity, and evidence.
- List every NOT-EVALUATED with its reason.

A single number would hide which controls failed. Two audits with the
same score can have opposite risk profiles; the control-by-control
table is the result.

## Severity (for FAILs only)

| Severity | Meaning |
|---|---|
| Critical | The failure lets a governance decision pass, or value move, without the intended checks. Fix before the next vote. |
| Major | The failure weakens a governance check or misleads operators about what the check is. Fix before relying on the control. |
| Minor | The failure is a documentation or process gap with no direct path to a wrong decision. Fix in the next pass. |

## Worked-audit score (postfiatd 67% threshold change)

Applied in `docs/worked-audit-postfiatd-67pct.md`. Result:

- PASS 10 / 24: G-03, G-07, G-10, G-12, G-14, G-15, G-16, G-18, G-20, G-24
- FAIL 3 / 24: G-01 (finding F-01, Major), G-13 (finding F-03, Major), G-17 (finding F-02, Major)
- NOT-EVALUATED 11 / 24: G-02, G-04, G-05, G-06, G-08, G-09, G-11, G-19, G-21, G-22, G-23 — each with its reason in the worked audit.

No Critical FAILs. Three Major FAILs, all three about the same change:
the threshold was lowered without a written rationale (G-01), the
docs still describe the old threshold (G-17), and no replay test guards
the ordering invariant (G-13). The mechanism itself — threshold
arithmetic, majority clock, quorum rules, vote tracking — verifies
cleanly where it was checked.
