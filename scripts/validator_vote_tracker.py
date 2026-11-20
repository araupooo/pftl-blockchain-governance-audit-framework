#!/usr/bin/env python3
"""ValidatorVoteTracker checks (check T-06) — model of the documented rules.

Pinned sources (postfiatd main HEAD 0085a1ff, 2026-10-10):
  src/xrpld/app/misc/ValidatorVoteTracker.h
      Vote{validatorKey, ledgerHash, ledgerSeq, validationHash, voteTime,
           exclusionAdd, exclusionRemove}; votesByLedger_ maps ledger
      sequence -> votes; processedValidators_ maps ledger -> validators
      already turned into transactions; cleanup() "to prevent memory
      growth"; isEnabled() gates on the amendment.
  src/xrpld/app/misc/ValidatorVoteTracker.cpp:59-83 (doVoting)
      returns early if the amendment is not enabled; generates one
      ttVALIDATOR_VOTE pseudo-transaction per unique validator;
      "Skip if we've already processed this validator for this ledger";
      "Skip duplicate validators in this batch".
  src/xrpld/app/misc/ValidatorVoteTracker.cpp:cleanup
      "Keep votes for the last 10 ledgers" (keepAfter = current - 10).
  src/xrpld/app/tx/detail/Change.cpp:96-101
      ttVALIDATOR_VOTE with PF_ValidatorVoteTracking disabled -> temDISABLED.
  src/xrpld/app/consensus/RCLValidations.cpp:197-216
      records the vote when a validation is processed, using the
      validation's signing hash as proof.
  include/xrpl/protocol/detail/features.macro:45-46
      PF_ValidatorVoteTracking and PF_AccountExclusion, both DefaultNo.

This is a model of those rules, not the C++ code. It checks the
invariants an auditor needs: dedup is order-independent, the gate
rejects when disabled, and vote records stay bounded.

No network, no private data, no randomness. Deterministic output.
Full SHA-256 values (64 hex chars) are printed, never truncated.
"""

import hashlib
import json
import sys

KEEP_LAST = 10  # ValidatorVoteTracker.cpp cleanup(): keep last 10 ledgers


class VoteTrackerModel:
    def __init__(self, amendment_enabled):
        self.enabled = amendment_enabled
        self.votes_by_ledger = {}       # ledgerSeq -> list of votes
        self.processed = {}             # ledgerSeq -> set of validators
        self.tx_log = []                # generated pseudo-transactions

    def record_vote(self, validator, ledger_seq, validation_hash):
        self.votes_by_ledger.setdefault(ledger_seq, []).append(
            (validator, validation_hash))

    def do_voting(self, current_seq):
        """Generate ttVALIDATOR_VOTE pseudo-transactions for the last
        closed ledger. Returns (txs_generated, status)."""
        if not self.enabled:
            return [], "temDISABLED"
        votes = self.votes_by_ledger.get(current_seq, [])
        processed = self.processed.setdefault(current_seq, set())
        unique = set()
        txs = []
        for validator, vhash in votes:
            if validator in processed:
                continue  # already processed for this ledger
            if validator in unique:
                continue  # duplicate in this batch
            unique.add(validator)
            processed.add(validator)
            txs.append({"ledger": current_seq + 1, "validator": validator,
                        "validationHash": vhash})
        self.tx_log.extend(txs)
        self.cleanup(current_seq)
        return txs, "tesSUCCESS"

    def cleanup(self, current_ledger):
        keep_after = current_ledger - KEEP_LAST if current_ledger > KEEP_LAST else 0
        for seq in [s for s in self.votes_by_ledger if s <= keep_after]:
            del self.votes_by_ledger[seq]
        for seq in [s for s in self.processed if s <= keep_after]:
            del self.processed[seq]

    def canonical_trace(self):
        """Canonical trace over the SORTED tx set, so arrival order cannot
        leak into it (same principle as vote_order_replay.py)."""
        ordered = sorted(self.tx_log,
                         key=lambda t: (t["ledger"], t["validator"]))
        blob = json.dumps(ordered, sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()


def main():
    failures = []

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + (f" -- {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    print("== validator_vote_tracker: dedup, gating, pruning ==")
    print()

    # --- dedup is order-independent --------------------------------------
    batch = [("V01", "h01"), ("V02", "h02"), ("V03", "h03"), ("V02", "h02"),
             ("V01", "h01"), ("V04", "h04"), ("V03", "h03")]
    traces = {}
    for order_name, seq in (("creation", batch),
                            ("reversed", list(reversed(batch))),
                            ("rotated-3", batch[3:] + batch[:3])):
        m = VoteTrackerModel(amendment_enabled=True)
        for v, h in seq:
            m.record_vote(v, 100, h)
        txs, status = m.do_voting(100)
        traces[order_name] = (len(txs), m.canonical_trace())
        print(f"order {order_name}: {len(txs)} txs, status={status}, "
              f"trace={traces[order_name][1]}")
    check("DEDUP: same batch in 3 orders yields 4 txs each (V01-V04 once)",
          all(t[0] == 4 for t in traces.values()))
    check("DEDUP: canonical tx trace identical across orders",
          len({t[1] for t in traces.values()}) == 1)

    # --- re-running doVoting for the same ledger generates nothing new ---
    m = VoteTrackerModel(amendment_enabled=True)
    for v, h in batch:
        m.record_vote(v, 100, h)
    first, _ = m.do_voting(100)
    second, _ = m.do_voting(100)
    check("REPLAY: second doVoting for the same ledger generates 0 new txs",
          len(first) == 4 and len(second) == 0,
          f"first={len(first)} second={len(second)}")

    # --- gating: disabled amendment rejects -------------------------------
    m_off = VoteTrackerModel(amendment_enabled=False)
    for v, h in batch:
        m_off.record_vote(v, 100, h)
    txs_off, status_off = m_off.do_voting(100)
    check("GATE: ttVALIDATOR_VOTE with amendment disabled -> temDISABLED, 0 txs",
          txs_off == [] and status_off == "temDISABLED",
          f"status={status_off} txs={len(txs_off)}")

    # --- pruning: only the last 10 ledgers are retained -------------------
    m_prune = VoteTrackerModel(amendment_enabled=True)
    for seq in range(1, 26):
        m_prune.record_vote("V01", seq, f"h{seq:02d}")
        m_prune.do_voting(seq)
    retained = sorted(m_prune.votes_by_ledger)
    check("PRUNE: after ledgers 1..25, only the last 10 are retained",
          retained == list(range(16, 26)), f"retained={retained}")
    check("PRUNE: retained vote count is bounded (10 ledgers x 1 vote)",
          sum(len(v) for v in m_prune.votes_by_ledger.values()) == 10)

    # --- validation hash travels with the vote as proof --------------------
    m_proof = VoteTrackerModel(amendment_enabled=True)
    m_proof.record_vote("V07", 200, "aabbccddeeff00112233445566778899"
                        "aabbccddeeff00112233445566778899")
    txs, _ = m_proof.do_voting(200)
    check("PROOF: generated tx carries the validation hash as proof",
          txs and txs[0]["validationHash"].startswith("aabbccdd"),
          f"tx={txs[0] if txs else None}")

    print()
    if failures:
        print(f"TRACKER RESULT: {len(failures)} CHECK(S) FAILED: {failures}")
        return 1
    print("TRACKER RESULT: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
