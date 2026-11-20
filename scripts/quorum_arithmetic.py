#!/usr/bin/env python3
"""Validator voting-power and quorum arithmetic (check T-05).

Sources (all accessed 2026-11-20):
  xrpl.org UNL docs: "Initially, it was believed that 60% overlap between
      two servers' UNLs was enough... further research showed that in the
      worst case scenario, 90% overlap was required to prevent a fork."
  Chase & MacBrough, "Analysis of the XRP Ledger Consensus Protocol"
      (arXiv:1802.07242, 21 Feb 2018): whitepaper bound ~20%; independent
      analysis suggested >40%; corrected bound roughly >90% of the UNL
      under a more general fault model; Cobalt lowers it to >60%.
  xrpl.org Negative UNL docs: standard quorum 80% of trusted validators;
      "To prevent the network from fragmenting, the quorum has a hard
      minimum of 60% of total validators." "As of 2024-06-25, there are
      a total of 35 validators on the default UNLs, so the network would
      stop making forward progress if 8 or more of them were offline."
  postfiatd NegativeUNLVote.h:76-78: "We only want to put 25% of the UNL
      on the NegativeUNL." / negativeUNLMaxListed = 0.25
  xrpl.org Fee Voting docs: "The network automatically adjusts the fee
      settings to the median of trusted validators' preferences."
      Reference fee 10 drops; account reserve 1 XRP; owner reserve
      0.2 XRP (lowered 2024-12-02 from 10 / 2 XRP). "Insufficient
      requirements, if adopted by a consensus of trusted validators
      (>50%), could expose the XRP Ledger peer-to-peer network to
      denial-of-service attacks."

The Negative-UNL adjusted-quorum formula below is a MODEL built from
those documented rules (labelled as such); the static 80%-of-trusted
rule and the 60% floor are the documented invariants it must satisfy.

No network, no private data, no randomness. Deterministic output.
"""

import math
import statistics
import sys

UNL_SIZE = 35  # default UNLs as of 2024-06-25 (xrpl.org Negative UNL docs)


def static_quorum(total):
    """Standard quorum: 80% of trusted validators (ceiling)."""
    return math.ceil(0.80 * total)


def negative_unl_cap(total):
    """NegativeUNLVote.h:78 — at most 25% of the UNL may be listed."""
    return math.floor(0.25 * total)


def quorum_floor(total):
    """Hard minimum quorum: 60% of total validators."""
    return math.ceil(0.60 * total)


def adjusted_quorum(total, listed):
    """MODEL: with `listed` validators on the Negative UNL, the quorum is
    80% of the remaining trusted set, but never below the 60% floor."""
    remaining = total - listed
    return max(quorum_floor(total), math.ceil(0.80 * remaining))


def fee_median(preferences):
    """Fee voting: the network adopts the median of trusted preferences."""
    return statistics.median(preferences)


def main():
    failures = []

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + (f" -- {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    print("== quorum_arithmetic: UNL overlap, Negative UNL, fee-vote median ==")
    print(f"default UNL size: {UNL_SIZE} validators")
    print()

    # --- UNL overlap bounds (documented, revised twice) -----------------
    print("-- UNL overlap bounds (Chase & MacBrough 2018; xrpl.org UNL docs) --")
    print("whitepaper bound      : ~20% overlap")
    print("independent analysis  : >40% overlap")
    print("corrected worst case  : >90% overlap of the UNL")
    print("Cobalt (sibling proto): >60% overlap")
    check("OVERLAP: worst-case bound (>90%) is stricter than the 60% belief",
          0.90 > 0.60)
    check("OVERLAP: worst-case bound exceeds the whitepaper bound by 70 points",
          0.90 - 0.20 == 0.70)

    # --- Negative UNL invariants -----------------------------------------
    print()
    print("-- Negative UNL (UNL=35) --")
    cap = negative_unl_cap(UNL_SIZE)
    floor = quorum_floor(UNL_SIZE)
    sq = static_quorum(UNL_SIZE)
    print(f"Negative UNL cap (25% of UNL) : {cap} validators")
    print(f"quorum floor (60% of total)   : {floor} validators")
    print(f"static quorum (80% of 35)     : {sq} validators")
    check("NEGUNL: cap is 8 validators (floor of 25% of 35)", cap == 8)
    check("NEGUNL: quorum floor is 21 validators (ceil of 60% of 35)", floor == 21)
    check("NEGUNL: static quorum is 28 validators (ceil of 80% of 35)", sq == 28)
    for listed in range(0, cap + 1):
        aq = adjusted_quorum(UNL_SIZE, listed)
        check(f"NEGUNL: adjusted quorum with {listed} listed never below floor 21",
              aq >= floor, f"adjusted quorum={aq}")
    check("NEGUNL: adjusted quorum falls as listings grow (28 -> 22 at cap)",
          adjusted_quorum(UNL_SIZE, 0) == 28
          and adjusted_quorum(UNL_SIZE, cap) == 22)

    # --- halt condition: 8+ offline stops progress (static rule) --------
    print()
    print("-- halt condition (static 80%-of-trusted rule) --")
    for offline in (7, 8, 9):
        remaining = UNL_SIZE - offline
        halts = remaining < sq
        print(f"offline={offline}: remaining={remaining}, quorum={sq} -> "
              f"{'HALT' if halts else 'progress'}")
    check("HALT: 7 offline (28 remain) still meets the 28 quorum",
          UNL_SIZE - 7 >= sq)
    check("HALT: 8 offline (27 remain) cannot meet the 28 quorum -> stops",
          UNL_SIZE - 8 < sq)
    print("note: Negative UNL listings can restore progress once they "
          "propagate (listings change slowly by design); the static-rule "
          "halt above is the documented '8 or more offline' statement.")

    # --- fee-vote median --------------------------------------------------
    print()
    print("-- fee voting: median of trusted preferences --")
    prefs = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
             10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
             10, 10, 10, 10, 10]
    check("FEE: unanimous 10-drop preferences -> median 10 drops",
          fee_median(prefs) == 10)
    # 17 of 35 validators prefer 0 (free): median is still 10, no change.
    prefs_low_minority = [0] * 17 + [10] * 18
    check("FEE: 17/35 preferring 0 drops still leaves median at 10 drops",
          fee_median(prefs_low_minority) == 10,
          f"median={fee_median(prefs_low_minority)}")
    # 18 of 35 (51.4%, just over half) prefer 0: median flips to 0 -> DoS exposure flag.
    prefs_low_majority = [0] * 18 + [10] * 17
    med = fee_median(prefs_low_majority)
    check("FEE: 18/35 (>50%) preferring 0 drops flips the median to 0",
          med == 0, f"median={med}")
    print(f"FLAG: median {med} drops with >50% low-fee votes -> "
          f"DoS exposure per xrpl.org fee-voting docs (reserves 1 / 0.2 XRP, "
          f"reference fee 10 drops, since 2024-12-02)")

    print()
    if failures:
        print(f"QUORUM RESULT: {len(failures)} CHECK(S) FAILED: {failures}")
        return 1
    print("QUORUM RESULT: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
