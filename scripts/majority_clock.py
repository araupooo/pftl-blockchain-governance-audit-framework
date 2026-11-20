#!/usr/bin/env python3
"""Majority-clock fragility test (check T-04).

Rule (xrpl.org Amendments docs, accessed 2026-11-20; postfiatd
SystemParameters.h:88, defaultAmendmentMajorityTime = weeks{2}):
an amendment must hold a majority continuously for two weeks; if support
drops below the threshold, the amendment is temporarily rejected and the
two-week period restarts. In code: doVoting emits tfLostMajority when
validators lose the majority (AmendmentTable.cpp:914) and the recorded
majority time is cleared, so the hold restarts from zero.

Worked example — fixCleanup3_4_0, Oct 2026 (reported timeline; the dates
below are as reported by CoinStats 2026-10-22 / Odaily 2026-10-25, citing
XRPLWin amendment-tracking data — secondary reporting, NOT directly
queried; labelled as reported wherever used):
  majority first reached  2026-10-09  -> no-dip activation 2026-10-23
  support dipped to 26/35 (74.29% < 80%) on 2026-10-21 for ~2 hours
  clock reset -> earliest activation 2026-11-04 (reported 14:46 UTC)
  delay vs no-dip activation: 12 days.

No network, no private data, no randomness. Deterministic output.
"""

import sys
from datetime import date, timedelta

HOLD = timedelta(days=14)
THRESHOLD_UPSTREAM = 0.80


def majority_clock(support_series, threshold):
    """support_series: list of (date, support_fraction) at flag ledgers.
    Returns (activation_date or None, reset_dates). The clock starts on
    the first date support >= threshold and resets whenever support
    drops below threshold."""
    majority_since = None
    resets = []
    for day, support in support_series:
        if support >= threshold:
            if majority_since is None:
                majority_since = day
            elif day - majority_since >= HOLD:
                return day, resets
        else:
            if majority_since is not None:
                resets.append(day)
            majority_since = None
    return None, resets


def main():
    failures = []

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + (f" -- {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    print("== majority_clock: two-week hold and dip-reset rule ==")
    print("hold: 14 days; upstream threshold: 80%")
    print()

    # --- general rule: a one-flag-ledger dip resets the clock ----------
    series = [
        (date(2026, 10, 9), 0.857),   # 30/35: majority gained
        (date(2026, 10, 16), 0.857),  # still holding, day 7
        (date(2026, 10, 21), 0.743),  # 26/35: dip below 80% for ~2 hours
        (date(2026, 10, 21), 0.857),  # support back the same day: clock restarts here
        (date(2026, 11, 4), 0.857),   # 14 days after restart
    ]
    activation, resets = majority_clock(series, THRESHOLD_UPSTREAM)
    check("RULE: a mid-hold dip resets the majority clock",
          resets == [date(2026, 10, 21)], f"resets={resets}")
    check("RULE: activation is 14 days after the restart, not after first gain",
          activation == date(2026, 11, 4), f"activation={activation}")

    no_dip = [
        (date(2026, 10, 9), 0.857),
        (date(2026, 10, 16), 0.857),
        (date(2026, 10, 23), 0.857),
    ]
    activation2, resets2 = majority_clock(no_dip, THRESHOLD_UPSTREAM)
    check("RULE: without a dip, activation is 14 days after first majority",
          activation2 == date(2026, 10, 23) and resets2 == [],
          f"activation={activation2}")

    # --- worked example: fixCleanup3_4_0 (reported timeline) -----------
    print()
    print("-- worked example: fixCleanup3_4_0 (REPORTED timeline, see header) --")
    dip_support = 26 / 35
    print(f"dip support: 26/35 = {dip_support:.2%} (< 80% threshold)")
    check("EXAMPLE: 26/35 is below the 80% threshold",
          dip_support < THRESHOLD_UPSTREAM)
    first_gain = date(2026, 10, 9)
    dip_day = date(2026, 10, 21)
    no_dip_activation = first_gain + HOLD
    reset_activation = dip_day + HOLD
    delay = (reset_activation - no_dip_activation).days
    print(f"majority first gained : {first_gain} -> no-dip activation {no_dip_activation}")
    print(f"dip on {dip_day} (26/35 for ~2 hours, reported) -> clock resets")
    print(f"re-derived activation : {reset_activation} (reported: 2026-11-04 14:46 UTC)")
    print(f"delay caused by the dip: {delay} days")
    check("EXAMPLE: re-derived activation date matches the reported 2026-11-04",
          reset_activation == date(2026, 11, 4))
    check("EXAMPLE: a ~2-hour dip costs 12 days of activation delay",
          delay == 12)

    # --- a dip AFTER activation is irrelevant (amendment already enabled)
    print()
    print("-- boundary: dip after the hold completes changes nothing --")
    series3 = [
        (date(2026, 10, 9), 0.857),
        (date(2026, 10, 23), 0.857),  # activated here (14 days held)
        (date(2026, 10, 24), 0.743),  # dip after activation
    ]
    act3, _ = majority_clock(series3, THRESHOLD_UPSTREAM)
    check("BOUNDARY: dip one day after activation does not un-enable",
          act3 == date(2026, 10, 23), f"activation={act3}")

    print()
    if failures:
        print(f"CLOCK RESULT: {len(failures)} CHECK(S) FAILED: {failures}")
        return 1
    print("CLOCK RESULT: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
