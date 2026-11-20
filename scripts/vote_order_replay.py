#!/usr/bin/env python3
"""Vote-order replay test (check T-02) — integrates PR #53, does not rebuild it.

Integrates the existing vote-replay work: PR #53 (postfiatorg/postfiatd,
"Test amendment vote replay with reordered validations", open, 0 reviews,
2026-11-20) adds `testVoteReplayOrderIndependent` to
src/test/app/AmendmentTable_test.cpp. That C++ test replays the same fixed
validator votes in three orders (creation, reversed, left-rotation by 5),
twice per order, on a fresh table each time, asserting identical vote
actions and majority/enabled states plus equal canonical state-trace
SHA-256. This script is a small, runnable Python model of the same
invariant over the documented AmendmentTable logic:

  src/xrpld/app/misc/detail/AmendmentTable.cpp:326-341 (computeThreshold)
  src/xrpld/app/misc/detail/AmendmentTable.cpp:360-376 (passes: ">" post-fix)
  src/xrpld/app/misc/detail/AmendmentTable.cpp:851-918 (doVoting actions:
      tfGotMajority / tfLostMajority / enable after the 2-week hold)

The model is NOT the C++ code; it checks the invariant the C++ test
guards, so an auditor can run it without building postfiatd. The C++
test remains the authoritative check; see docs/vote-replay-integration.md.

Cases: two amendments over 16 validators, exactly as in PR #53 —
A: 13/16 yes (majority under both rules), B: 11/16 yes (majority only
under postfiatd's 67% rule). Plus duplicate/stale/vote-change cases.

No network, no private data, no randomness. Deterministic output.
Full SHA-256 values (64 hex chars) are printed, never truncated.
"""

import hashlib
import json
import sys

POSTFIATD = (67, 100)
UPSTREAM = (80, 100)
HOLD_WEEKS = 2  # defaultAmendmentMajorityTime = weeks{2}, SystemParameters.h:88


def threshold(trusted, ratio):
    num, den = ratio
    return max(1, (trusted * num) // den)


class AmendmentSet:
    """Minimal model of AmendmentTable::AmendmentSet + doVoting."""

    def __init__(self, ratio):
        self.ratio = ratio
        self.votes = {}          # amendment -> set of yes-voter ids
        self.trusted = 0         # trusted validations in the flag window
        self.majority_since = {}  # amendment -> week majority first seen
        self.enabled = set()

    def apply_validations(self, validations, window):
        """validations: list of (validator_id, amendment, yes, ledger_window).
        Only validations from the current flag window count; a validator's
        latest vote in the window wins; duplicates count once."""
        window_votes = {}
        for vid, amendment, yes, w in validations:
            if w != window:
                continue  # stale-window validation: ignored
            window_votes.setdefault(amendment, {})[vid] = yes
        self.votes = {a: {v for v, y in m.items() if y}
                      for a, m in window_votes.items()}
        # trusted = distinct validators whose validation arrived in-window
        self.trusted = len({vid for vid, _, _, w in validations if w == window})

    def passes(self, amendment):
        yes = len(self.votes.get(amendment, set()))
        t = threshold(self.trusted, self.ratio)
        if self.trusted == 1:
            return yes >= t
        return yes > t

    def do_voting(self, week, local_vote_up=True):
        """One flag-ledger round. Returns {amendment: action}."""
        actions = {}
        for amendment in sorted(self.votes):
            has_val = self.passes(amendment)
            has_ledger = amendment in self.majority_since
            if has_val and not has_ledger and local_vote_up:
                actions[amendment] = "tfGotMajority"
                self.majority_since[amendment] = week
            elif not has_val and has_ledger:
                actions[amendment] = "tfLostMajority"
                del self.majority_since[amendment]
            elif (has_ledger and local_vote_up
                    and self.majority_since[amendment] + HOLD_WEEKS <= week
                    and amendment not in self.enabled):
                actions[amendment] = "enable"
                self.enabled.add(amendment)
            else:
                actions[amendment] = "none"
        return actions

    def canonical_trace(self, week, actions):
        """Canonical state trace: sorted representation only, so arrival
        order cannot leak into it. SHA-256 over the JSON encoding."""
        state = {
            "week": week,
            "trusted": self.trusted,
            "threshold": threshold(self.trusted, self.ratio),
            "votes": {a: sorted(v) for a, v in sorted(self.votes.items())},
            "actions": {a: actions.get(a, "none") for a in sorted(self.votes)},
            "majority_since": {a: w for a, w in sorted(self.majority_since.items())},
            "enabled": sorted(self.enabled),
        }
        blob = json.dumps(state, sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()


VALIDATORS = [f"V{i:02d}" for i in range(16)]
# PR #53 fixed vote sets: A 13/16 yes, B 11/16 yes.
VOTES_A = set(VALIDATORS[:13])
VOTES_B = set(VALIDATORS[:11])


def build_validations(yes_set, order):
    """One validation per validator, in the given order. Yes-voters vote
    yes on both amendments; the rest vote no (a validation still counts
    toward the trusted set)."""
    vals = []
    for vid in order:
        vals.append((vid, "A", vid in VOTES_A, 0))
        vals.append((vid, "B", vid in VOTES_B, 0))
    return vals


def rotate_left(seq, k):
    return seq[k:] + seq[:k]


def main():
    failures = []

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + (f" -- {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    print("== vote_order_replay: PR #53 pattern, Python model ==")
    print("amendments: A 13/16 yes (majority under both rules), "
          "B 11/16 yes (majority only under postfiatd 67%)")
    print()

    orders = {
        "creation": VALIDATORS,
        "reversed": list(reversed(VALIDATORS)),
        "rotated-5": rotate_left(VALIDATORS, 5),
    }
    traces = {}
    for order_name, order in orders.items():
        for rep in (1, 2):
            table = AmendmentSet(POSTFIATD)
            table.apply_validations(build_validations(None, order), window=0)
            # week 2: threshold check; weeks 4-5: after the majority hold
            a2 = table.do_voting(week=2)
            t2 = table.canonical_trace(2, a2)
            a4 = table.do_voting(week=4)
            t4 = table.canonical_trace(4, a4)
            key = f"{order_name}/rep{rep}"
            traces[key] = (t2, t4)
            print(f"run {key}: week2 actions={a2} trace={t2}")
            print(f"run {key}: week4 actions={a4} trace={t4}")

    all_t2 = {t[0] for t in traces.values()}
    all_t4 = {t[1] for t in traces.values()}
    check("REPLAY: week-2 canonical trace identical across 3 orders x 2 reps",
          len(all_t2) == 1, f"distinct traces={len(all_t2)}")
    check("REPLAY: week-4 canonical trace identical across 3 orders x 2 reps",
          len(all_t4) == 1, f"distinct traces={len(all_t4)}")

    # Boundary assertions matching PR #53's two amendments.
    table = AmendmentSet(POSTFIATD)
    table.apply_validations(build_validations(None, VALIDATORS), window=0)
    check("BOUNDARY: A (13/16) passes under postfiatd 67%",
          table.passes("A"))
    check("BOUNDARY: B (11/16) passes under postfiatd 67%",
          table.passes("B"))
    table_up = AmendmentSet(UPSTREAM)
    table_up.apply_validations(build_validations(None, VALIDATORS), window=0)
    check("BOUNDARY: A (13/16) passes under upstream 80%",
          table_up.passes("A"))
    check("BOUNDARY: B (11/16) does NOT pass under upstream 80%",
          not table_up.passes("B"))

    # Duplicate validations count once.
    dup = build_validations(None, VALIDATORS)
    dup += [(VALIDATORS[0], "A", True, 0), (VALIDATORS[0], "A", True, 0),
            (VALIDATORS[1], "B", True, 0)]
    t_dup = AmendmentSet(POSTFIATD)
    t_dup.apply_validations(dup, window=0)
    check("DEDUP: duplicate validations for the same validator count once",
          len(t_dup.votes["A"]) == 13 and len(t_dup.votes["B"]) == 11
          and t_dup.trusted == 16,
          f"votes A={len(t_dup.votes['A'])} B={len(t_dup.votes['B'])} trusted={t_dup.trusted}")

    # Stale-window validations are ignored.
    stale = build_validations(None, VALIDATORS)
    stale += [(f"V{i:02d}", "A", True, -1) for i in range(16)]  # previous window
    t_stale = AmendmentSet(POSTFIATD)
    t_stale.apply_validations(stale, window=0)
    check("STALE: previous-flag-window validations are ignored",
          len(t_stale.votes["A"]) == 13 and t_stale.trusted == 16)

    # A validator changing its vote between flag ledgers: latest counts.
    changed = build_validations(None, VALIDATORS)
    t_chg = AmendmentSet(POSTFIATD)
    t_chg.apply_validations(changed, window=0)
    before = t_chg.passes("B")
    changed2 = [(v, a, (False if v == "V10" else y), 1)
                for (v, a, y, w) in build_validations(None, VALIDATORS)]
    t_chg.apply_validations(changed2, window=1)
    check("VOTE-CHANGE: V10 flipping yes->no drops B to 10/16, no majority",
          before and not t_chg.passes("B")
          and len(t_chg.votes["B"]) == 10,
          f"B yes-votes after flip={len(t_chg.votes['B'])}")

    # Majority clock: losing majority clears the recorded majority time.
    t_clk = AmendmentSet(POSTFIATD)
    t_clk.apply_validations(build_validations(None, VALIDATORS), window=0)
    t_clk.do_voting(week=2)
    check("CLOCK: majority recorded at week 2", t_clk.majority_since.get("B") == 2)
    t_clk.apply_validations(changed2, window=1)
    t_clk.do_voting(week=3)
    check("CLOCK: losing majority at week 3 clears the recorded time",
          "B" not in t_clk.majority_since)

    print()
    if failures:
        print(f"REPLAY RESULT: {len(failures)} CHECK(S) FAILED: {failures}")
        return 1
    print("REPLAY RESULT: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
