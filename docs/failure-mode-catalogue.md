# Governance Failure-Mode Catalogue

Eight documented incidents, each with its primary source, the
mechanism, the observable detection check, and the framework control
it maps to. The mapping is executable: `scripts/incident_replay.py`
encodes all eight as test cases (verdict totals: CAUGHT 5,
AS-DESIGNED 2, GAP 1).

Claims are labelled [FAKTA] (verified, source + date), [ESTIMASI]
(modelled/reported number), [ANALISIS] (interpretation).

## XRPL-2026-clock — Amendment clock reset, Oct 2026

- [ESTIMASI] `fixCleanup3_4_0` first reached majority 9 Oct 2026,
  lost it 21 Oct when support dipped to 26 of 35 validators for
  ~2 hours, resetting the 14-day clock; earliest activation moved
  from 23 Oct to 4 Nov 2026, 14:46 UTC. Sources: CoinStats 2026-10-22,
  Odaily 2026-10-25, CoinMarketCap Academy — all citing XRPLWin
  amendment-tracking data (secondary reporting, not directly
  queried). The fix bundle addressed a token-minting permission bug
  (delegated burn permission could mint).
- Detection check (G-18): track each live amendment's support margin
  per flag ledger; alert when support comes within 2 validators of
  the threshold; compute the dip cost (14 days from the dip date).
- Verdict: AS-DESIGNED — the clock reset fired exactly as specified.
  The lesson is monitoring and cost, not a control failure.

## XRPL-2020-lost-majority — Amendments lost majority, Jan 2020

- [FAKTA] On 2019-01-11, `fixCheckThreading` and
  `fixPayChanRecipientOwnerDir` lost support of several validators,
  falling below the 80% threshold; they were no longer expected to
  become enabled 2020-01-18. Ripple's own validators voted against
  them temporarily "to give people more time to upgrade", because
  enabling would amendment-block everyone still on v1.3.1. Source:
  xrpl.org blog, 2020-01-13.
- Detection check (G-08): maintain a vote-share table by operator;
  flag any single operator whose votes decide the outcome.
- Verdict: CAUGHT — a concentration analysis would have flagged the
  swing votes before they were cast.

## XRPL-2021-rounding — Threshold rounding bug

- [FAKTA] Pre-`fixAmendmentMajorityCalc`, an amendment could
  activate with 28/36 = 77.8% support. `fixAmendmentMajorityCalc`
  (amendment ID
  `4F46DF03559967AC60F2EB272FEFE3928A7594A45FF774B87A7E540DB0F8F068`,
  enabled 2021-04-08) fixed it: "Without this amendment, the minimum
  threshold for amendment activation is any value that rounds to
  204/256 of trusted validators… With this amendment, the actual
  minimum number of validators needed is never less than 80%."
  Source: xrpl.org Known Amendments. Local code confirms the
  mechanism (`AmendmentTable.cpp:371-376`: `>=` before the fix,
  strictly `>` after, with a single-validator exception).
- Detection check (G-07): re-derive the threshold from code for
  N = 1..200 and assert the minimum fraction never drops below the
  stated bar (`scripts/threshold_arithmetic.py`).
- Verdict: CAUGHT — re-derivation flags 28/36 as below 80%.

## NEUTRON-2026 — Governance attack, Sep 2026

- [FAKTA] Primary source: Cosmos Hub Forum, "Neutron Governance
  Attack: Cosmos Hub Response and Recovery Update" (Cosmos Labs,
  updated 29 Sep 2026). "On September 22, 2026, a governance attack
  on Neutron drained liquidity from Astroport and other protocols…
  the attacker bridged… roughly 1.7M ATOM… to the Cosmos Hub. The
  Cosmos Hub itself was not exploited. No Hub user funds were
  affected." "Hub validators halted the network at height
  33,086,740… Roughly 24 hours later, they restarted on a patched
  Gaia binary (v28.3.0) that applied a single, one-time change at the
  halt height, moving 1,227,121 ATOM from the attacker's address into
  a 4-of-6 multisig."
- [FAKTA] Attack mechanics (corroborated by Unchained,
  CryptoBriefing, CoinPaprika): Neutron proposal 9, "AIATO: AI Agent
  Takeover", passed via the expedited 3-day track with ~82% of votes
  cast; the attacker spent ~$20,200 acquiring NTRN shortly before the
  vote; 11 messages handed admin control of Astroport and Drop
  contracts to the attacker; ~$9.4–9.5M in contract value exposed,
  ~20% drained before Neutron halted.
- Detection check (G-05, G-06): snapshot voting power before
  proposal creation; publish the acquisition cost of a deciding
  share next to the value at stake.
- Verdict: CAUGHT — both controls fail on the incident parameters.

## BEANSTALK-2022 — Flash-loan governance takeover, Apr 2022

- [FAKTA] "A flash loan exploit occurred on April 17, 2022 on
  Beanstalk Farms. Approximately $182 million was lost, with the
  attacker gaining $76 million as profit. The incident is due to the
  governance mechanism, in which the attacker used a flash loan to
  amplify the governance token amount and ultimately control the
  result to pass the proposal." (CertiK.) The attacker proposed
  BIP-18 (malicious) alongside a decoy BIP-19 ($250k Ukraine
  donation); borrowed ~$1B in a flash loan, converted to voting
  power (~67% "stalk"), and used `emergencyCommit()` — executable
  once a proposal was 1 day old with 2/3 support — to execute
  immediately. Elliptic confirms ~25,000 ETH (~$76M) stolen;
  protocol lost $182M; BEAN fell $1 → $0.10.
- Detection check (G-05, G-19): snapshot before proposal creation;
  the emergency path must divide by the weight at proposal end, not
  by current weight, and must meet the same threshold as the ordinary
  path.
- Verdict: CAUGHT — both controls fail on the incident parameters.

## SOLANA-SIMD228-2025 — Inflation vote failed, Mar 2025

- [FAKTA] SIMD-228 (dynamic, market-based SOL inflation) failed:
  ~74% of staked supply voted across 910 validators; 43.6% yes,
  27.4% no, 3.3% abstain of total stake — 61.4% of participating
  votes in favor vs the 66.67% required. Voting ran Mar 6–13/14,
  2025 (Epochs 753–755). Sources: Cointelegraph 2025-03-14, The
  Block via TradingView, FXStreet 2025-03-15.
- [FAKTA] Class split: 67.5% of validators with <100,000 SOL voted
  against; 65.8% of validators with >1,000,000 SOL voted in favor
  (ChainCatcher analysis of Dune data).
- Detection check (G-07, G-09): verify the threshold arithmetic
  (61.4% < 66.67% → correctly failed); record support by voter
  class.
- Verdict: AS-DESIGNED — a high-turnout vote can still fail on
  threshold design; the class split is the governance-health signal.

## ETH-DAO-2016 — Irregular state change by social consensus, Jul 2016

- [FAKTA] On 20 Jul 2016 at block 1,920,000, Ethereum hard-forked
  with an irregular state change moving ~12M ETH from DAO-related
  contracts into a WithdrawDAO recovery contract. The Ethereum
  Foundation's announcement reported ~85% of miners mining the fork;
  participants who rejected it continued as Ethereum Classic.
  Sources: Ethereum Foundation blog (20 Jul 2016) via ethereum.org
  history page and secondary summaries.
- Detection check (G-21): an irregular state change must link to a
  written off-chain decision record (forum thread, coin vote, miner
  signalling) — the audit trail covers the off-chain decision, not
  just on-chain votes.
- Verdict: GAP — no on-chain vote record exists to audit. The
  framework admits this: social-layer governance is a category the
  framework can describe but not verify from chain data alone.

## BLOCKDAEMON-2026 — Validator key compromise, Oct 2026

- [FAKTA] Primary source: Blockdaemon status page. "Between
  2026-10-26 19:03 UTC and 2026-10-27, an unauthorised party used
  private keys associated with five Blockdaemon-operated Solana
  mainnet validators (four live, one retired)… The withdraw
  authority on the five vote accounts was subsequently reassigned by
  the unauthorised party. Under Solana's authority model this cannot
  be reversed, so those vote accounts have been permanently retired."
  Key material was copied from a corporate device during an employee
  off-boarding in Dec 2025. Replacement validators live by
  2026-10-27 22:28 UTC.
- Detection check (G-23): withdrawal authority separated from
  operational keys; custody register naming where keys live and the
  off-boarding procedure.
- Verdict: CAUGHT — a custody control would have flagged keys
  sitting on a corporate device past off-boarding.
