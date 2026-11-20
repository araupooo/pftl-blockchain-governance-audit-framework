# Sources

Primary sources only, except where labelled secondary. All web
sources accessed 2026-11-20. Local code checked against the postfiatd
checkout at main HEAD `0085a1ff` (2026-10-10), verified by `grep -n`.

## Protocol rules (XRPL / postfiatd)

| # | Source | Location |
|---|---|---|
| 1 | XRPL Amendments docs | https://www.xrpl.build/docs/concepts/networks-and-servers/amendments |
| 2 | XRPL UNL docs | https://xrpl.org/docs/concepts/consensus-protocol/unl |
| 3 | XRPL Negative UNL docs | https://xrpl.org/docs/concepts/consensus-protocol/negative-unl |
| 4 | XRPL Fee Voting docs | https://xrpl.org/docs/concepts/consensus-protocol/fee-voting |
| 5 | XRPL Known Amendments | https://xrpl.org/resources/known-amendments |
| 6 | XRPL blog, amendments lost majority (2020-01-13) | https://xrpl.org/blog/2020/fixcheckthreading-fixpaychanrecipientownerdir-lost-majority |
| 7 | Chase & MacBrough, "Analysis of the XRP Ledger Consensus Protocol" (arXiv:1802.07242, 21 Feb 2018) | https://arxiv.org/pdf/1802.07242 |
| 8 | postfiatd `0085a1ff` (local checkout, pinned) | `include/xrpl/protocol/SystemParameters.h:83-88`; `src/xrpld/app/misc/detail/AmendmentTable.cpp:326-341,360-376,851-918,988`; `src/xrpld/app/misc/README.md:70-71,85,94,101`; `docs/AmendmentDevelopment.md:72,91`; `src/xrpld/app/misc/NegativeUNLVote.h:76-78`; `src/xrpld/app/misc/ValidatorVoteTracker.h`; `src/xrpld/app/misc/ValidatorVoteTracker.cpp:83`; `src/xrpld/app/tx/detail/Change.cpp:96-101`; `src/test/app/AmendmentTable_test.cpp:546-549`; `src/xrpld/core/Config.h:248`; `src/xrpld/app/main/Application.cpp:1288`; `src/xrpld/core/detail/Config.cpp:872`; `src/xrpld/app/consensus/RCLValidations.cpp:197-216`; `include/xrpl/protocol/detail/features.macro:45-46` |
| 9 | Upstream rippled master `SystemParameters.h` (fetched 2026-11-20) | https://raw.githubusercontent.com/ripple/rippled/master/include/xrpl/protocol/SystemParameters.h — line 76: `constexpr std::ratio<80, 100> kAmendmentMajorityCalcThreshold;` |
| 10 | PR #53 (GitHub API, 2026-11-20) | https://api.github.com/repos/postfiatorg/postfiatd/pulls/53 — open, 0 reviews, mergeable, head `4f718711`, base `0085a1ff`, updated 2026-11-13T23:18:29Z |

## Incidents

| # | Source | Location |
|---|---|---|
| 11 | Cosmos Hub Forum (Cosmos Labs), Neutron governance attack response (updated 29 Sep 2026) | https://forum.cosmos.network/t/neutron-governance-attack-cosmos-hub-response-and-recovery-update/17369 |
| 12 | CertiK, Beanstalk Farms exploit revisit | https://www.certik.com/blog/revisiting-beanstalk-farms-exploit |
| 13 | Elliptic, Beanstalk Farms | https://www.elliptic.co/insights/76-million-stolen-from-beanstalk-farms-defi-stablecoin-protocol/ |
| 14 | Cointelegraph, SIMD-228 (2025-03-14) | http://cointelegraph.com/news/solana-proposal-cut-inflation-rate-fails-to-pass |
| 15 | The Block via TradingView, SIMD-228 | https://www.tradingview.com/news/the_block:d5c307c02094b:0-solana-s-key-simd-228-proposal-fails-to-pass-validator-vote-token-emissions-unchanged/ |
| 16 | Blockdaemon status, Solana validator incident | https://status.blockdaemon.com/incidents/xqr8f96s6v8x |
| 17 | Ethereum Foundation blog (20 Jul 2016), DAO fork | via https://ethereum.org — block 1,920,000, ~12M ETH moved, ~85% of miners on the fork |
| 21 | fixCleanup3_4_0 timeline — SECONDARY reporting, labelled as reported wherever used | CoinStats 2026-10-22; Odaily 2026-10-25; CoinMarketCap Academy — all citing XRPLWin amendment-tracking data (not directly queried) |

## Framework syntheses (not standards)

| # | Source | Location |
|---|---|---|
| 18 | Tech-Audit.org, "Blockchain Governance Audit Checklist 2026" | http://Tech-Audit.org/blockchain-audit/blockchain-governance-audit-checklist/ |
| 19 | Blockready, "How to Evaluate a DAO: Governance-Health Framework" | https://www.blockready.com/blog/how-to-evaluate-a-dao |
| 20 | Blockchain-Council DeFi audit framework guide (EEA DeFi Risk Assessment Guidelines; Galaxy SeC FiT PrO) | https://www.blockchain-council.org/cryptocurrency/defi-protocol-crypto-audit-framework-liquidity-pools-oracles-governance/ |

## Not verified — do not cite as primary source

- Founder statement on mainnet governance (18 Sep 2026,
  #validator-ops, Discord): ordering undecided, leaning toward
  mainnet on postfiatl1v2 with inherited validator governance after
  a multi-million-dollar audit. Discord is not accessible from this
  environment and no public mirror was found. Carried as an
  unverified operator statement; not used as evidence anywhere in
  this pack.
- Upstream rippled threshold was checked against current master,
  not the exact commit postfiatd forked from. The 80% figure is
  independently confirmed by the xrpl.org docs (#1, #5), so the
  divergence finding stands.
