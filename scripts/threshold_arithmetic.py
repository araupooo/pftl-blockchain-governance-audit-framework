#!/usr/bin/env python3
"""Re-derive amendment-majority threshold arithmetic (check T-01).

Pinned sources (postfiatd main HEAD 0085a1ff, 2026-10-10):
  include/xrpl/protocol/SystemParameters.h:83-85
      preFixAmendmentMajorityCalcThreshold  = 204/256
      postFixAmendmentMajorityCalcThreshold = 67/100
  src/xrpld/app/misc/detail/AmendmentTable.cpp:326-341 (computeThreshold)
      threshold = max(1, floor(trusted * num / den))
  src/xrpld/app/misc/detail/AmendmentTable.cpp:360-376 (passes)
      pre-fix : votes >= threshold
      post-fix: votes >  threshold, except trusted == 1 (then >=)
Upstream rippled master (fetched 2026-11-20):
  include/xrpl/protocol/SystemParameters.h:76
      kAmendmentMajorityCalcThreshold = 80/100
PR #53 (postfiatorg/postfiatd, open, 0 reviews, 2026-11-20) boundary values
used as assertions: 11/16 first majority under postfiatd 67%; 13/16 under
upstream 80%; majority lost at 10/16 (postfiatd) / 12/16 (upstream);
10 validators: 6 yes = no majority, 8 yes = majority under 67%.

No network, no private data, no randomness. Deterministic output.
"""

import math
import sys

PRE_FIX = (204, 256)    # legacy ratio, ">=" comparison (the rounding bug)
POSTFIATD = (67, 100)   # postfiatd post-fix ratio, ">" comparison
UPSTREAM = (80, 100)    # upstream rippled post-fix ratio, ">" comparison


def threshold(trusted, ratio):
    num, den = ratio
    return max(1, (trusted * num) // den)


def min_yes_votes(trusted, ratio, strict):
    """Minimum yes-votes for a majority under the given rule."""
    t = threshold(trusted, ratio)
    if strict:
        # passes() uses strict ">" post-fix, except a single trusted
        # validator, where ">=" applies so a majority is reachable.
        return t if trusted == 1 else t + 1
    return t  # pre-fix ">="


def frac(n, d):
    return f"{n}/{d} = {100.0 * n / d:.2f}%"


def main():
    failures = []

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + (f" -- {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    print("== threshold_arithmetic: amendment-majority re-derivation ==")
    print("rules: pre-fix 204/256 with >= | postfiatd 67/100 with > | upstream 80/100 with >")
    print()

    # --- PR #53 boundary assertions -------------------------------------
    check("PR53: N=16 postfiatd first majority at 11 yes-votes",
          min_yes_votes(16, POSTFIATD, True) == 11,
          f"threshold={threshold(16, POSTFIATD)}, min_yes={min_yes_votes(16, POSTFIATD, True)}")
    check("PR53: N=16 upstream first majority at 13 yes-votes",
          min_yes_votes(16, UPSTREAM, True) == 13,
          f"threshold={threshold(16, UPSTREAM)}, min_yes={min_yes_votes(16, UPSTREAM, True)}")
    check("PR53: N=16 postfiatd majority lost at 10 yes-votes",
          not (10 > threshold(16, POSTFIATD)))
    check("PR53: N=16 upstream majority lost at 12 yes-votes",
          not (12 > threshold(16, UPSTREAM)))
    check("PR53: N=10 postfiatd 6 yes = NO majority",
          not (6 > threshold(10, POSTFIATD)),
          f"threshold={threshold(10, POSTFIATD)}")
    check("PR53: N=10 postfiatd 8 yes = majority",
          8 > threshold(10, POSTFIATD))
    check("PR53: N=10 postfiatd minimum majority is 7 yes-votes",
          min_yes_votes(10, POSTFIATD, True) == 7)

    # --- the pre-fix rounding bug ----------------------------------------
    # fixAmendmentMajorityCalc (enabled 2021-04-08, xrpl.org Known Amendments):
    # pre-fix, 28 of 36 validators (77.78%) could activate an amendment.
    check("BUG: pre-fix N=36 activates at 28 yes-votes (77.78% < 80%)",
          min_yes_votes(36, PRE_FIX, False) == 28,
          frac(28, 36))
    check("BUG: pre-fix minimum fraction over N=1..200 is below 80%",
          min(min_yes_votes(n, PRE_FIX, False) / n for n in range(1, 201)) < 0.80,
          f"min={min(min_yes_votes(n, PRE_FIX, False) / n for n in range(1, 201)):.4f}")

    # --- post-fix guarantees ---------------------------------------------
    post_min = min(min_yes_votes(n, POSTFIATD, True) / n for n in range(1, 201))
    up_min = min(min_yes_votes(n, UPSTREAM, True) / n for n in range(1, 201))
    check("POSTFIX: postfiatd 67% rule never activates below 67% (N=1..200)",
          post_min >= 0.67, f"min fraction={post_min:.4f}")
    check("POSTFIX: upstream 80% rule never activates below 80% (N=1..200)",
          up_min >= 0.80, f"min fraction={up_min:.4f}")
    check("DIVERGENCE: postfiatd bar is weaker than upstream for every N=1..200",
          all(min_yes_votes(n, POSTFIATD, True) <= min_yes_votes(n, UPSTREAM, True)
              for n in range(1, 201)))
    check("DIVERGENCE: postfiatd bar is strictly weaker than upstream for N>=4 except N=6",
          all(min_yes_votes(n, POSTFIATD, True) < min_yes_votes(n, UPSTREAM, True)
              for n in range(4, 201) if n != 6))
    check("DIVERGENCE: small-N ties are exactly N=1,2,3 (unanimity) and N=6 (5/6 both)",
          [n for n in range(1, 201)
           if min_yes_votes(n, POSTFIATD, True) == min_yes_votes(n, UPSTREAM, True)]
          == [1, 2, 3, 6])

    # --- default UNL size (35 validators, xrpl.org Negative UNL docs) ----
    for n in (35,):
        p = min_yes_votes(n, POSTFIATD, True)
        u = min_yes_votes(n, UPSTREAM, True)
        print(f"UNL N={n}: postfiatd needs {p} yes-votes ({frac(p, n)}); "
              f"upstream needs {u} yes-votes ({frac(u, n)}); gap={u - p} validators")
        check(f"UNL35: postfiatd needs 24 yes-votes of 35 (68.57%)", p == 24)
        check(f"UNL35: upstream needs 29 yes-votes of 35 (82.86%)", u == 29)

    print()
    print("== boundary table (N, pre-fix min, postfiatd min, upstream min) ==")
    print(f"{'N':>4} {'pre-fix':>8} {'postfiatd':>10} {'upstream':>9}")
    for n in (1, 2, 3, 4, 5, 10, 16, 35, 36, 100, 200):
        print(f"{n:>4} {min_yes_votes(n, PRE_FIX, False):>8} "
              f"{min_yes_votes(n, POSTFIATD, True):>10} {min_yes_votes(n, UPSTREAM, True):>9}")

    print()
    if failures:
        print(f"THRESHOLD RESULT: {len(failures)} CHECK(S) FAILED: {failures}")
        return 1
    print("THRESHOLD RESULT: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
