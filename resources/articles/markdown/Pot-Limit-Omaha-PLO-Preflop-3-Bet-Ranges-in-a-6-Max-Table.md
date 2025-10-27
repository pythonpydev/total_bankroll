### Pot Limit Omaha (PLO) Preflop 3-Bet Ranges in a 6-Max Table

In Pot Limit Omaha, 3-betting (re-raising after an open-raise) is more situational than raising first in (RFI) because it depends on the opener's position, table dynamics, stack sizes (assuming 100BB standard), and whether you're in position (IP) or out of position (OOP). Hand equities run close in PLO, so 3-bet ranges are polarized: value hands (premiums for stacks off) and bluffs (blockers like A-high suited for fold equity). There are 270,725 unique starting hands, making it impossible to list every playable 3-bet hand exhaustively. Instead, ranges are categorized by structure (pairs, rundowns/gaps, suitedness: ds = double-suited, ss = single-suited, r = rainbow), with percentages indicating the proportion of that subcategory to 3-bet (e.g., 80% ds means 3-bet 80% of double-suited versions).

These ranges are solver-inspired approximations for mid-stakes 6-max cash games, compiled from forum discussions, strategy articles, and general GTO tools like MonkerSolver/PIO (though specific charts are often paywalled). Total 3-bet % varies: tighter OOP (e.g., blinds ~5-8%) vs. looser IP (e.g., BTN ~10-15%). Adjust for opener's range (wider vs. late opens) and opponents (loosen vs. weak callers, tighten vs. aggressive 4-betters). UTG can't 3-bet preflop as they're first to act.

- **Total 3-Bet %**: Overall percentage of hands to 3-bet vs. a standard open (e.g., vs. CO for BTN; vs. BTN for BB).
- Bluffs: Often ~30-50% of the range, focusing on A-wheel (A543ds) or A-blockers (Axx x ds) for nut potential and to deny equity.
- Sizing: OOP pot-sized (~3-3.5x open); IP smaller (~2.5-3x) for better SPR.
- BB/SB: Heavier on value OOP; add bluffs if opener folds often.

#### Pairs (Hands with at Least One Pair)

Premium pairs with good side cards/suitedness for value; low pairs rarely 3-bet unless ds with connectivity.

| Position | Total 3-Bet % (vs. Typical Open) | AA                      | KK                    | QQ                    | JJ                    | TT-99                | 88-66                | 55-22               |
| -------- | -------------------------------- | ----------------------- | --------------------- | --------------------- | --------------------- | -------------------- | -------------------- | ------------------- |
| UTG      | N/A                              | N/A                     | N/A                   | N/A                   | N/A                   | N/A                  | N/A                  | N/A                 |
| HJ       | ~6-8% (vs. UTG)                  | 100% ds, 90% ss, 50% r  | 80% ds, 50% ss, 20% r | 60% ds, 30% ss, 10% r | 40% ds, 20% ss, 0% r  | 30% ds, 10% ss, 0% r | 20% ds, 0% ss, 0% r  | 0%                  |
| CO       | ~8-10% (vs. UTG/HJ)              | 100% ds, 95% ss, 60% r  | 85% ds, 60% ss, 25% r | 70% ds, 40% ss, 15% r | 50% ds, 25% ss, 5% r  | 40% ds, 15% ss, 0% r | 25% ds, 5% ss, 0% r  | 10% ds, 0% ss, 0% r |
| BTN      | ~10-12% (vs. UTG/HJ/CO)          | 100% ds, 100% ss, 70% r | 90% ds, 70% ss, 30% r | 80% ds, 50% ss, 20% r | 60% ds, 30% ss, 10% r | 50% ds, 20% ss, 5% r | 30% ds, 10% ss, 0% r | 15% ds, 0% ss, 0% r |
| SB       | ~8-10% (vs. UTG/HJ/CO/BTN)       | 100% ds, 95% ss, 60% r  | 85% ds, 60% ss, 25% r | 70% ds, 40% ss, 15% r | 50% ds, 25% ss, 5% r  | 40% ds, 15% ss, 0% r | 25% ds, 5% ss, 0% r  | 10% ds, 0% ss, 0% r |
| BB       | ~5-7% (vs. any)                  | 100% ds, 90% ss, 50% r  | 80% ds, 50% ss, 20% r | 60% ds, 30% ss, 10% r | 40% ds, 20% ss, 0% r  | 30% ds, 10% ss, 0% r | 20% ds, 0% ss, 0% r  | 0%                  |

#### Non-Pairs (Wraps, Rundowns, and High-Card Hands)

Focus on high connected ds for nut straights/flushes; add gaps/bluffs IP. 0g = no gaps (e.g., JT98), 1g = one gap (e.g., JT97), 2g = two gaps (e.g., JT96). Prioritize A-high for blockers.

| Position | 0g (e.g., JT98)       | 1g (e.g., JT97)       | 2g (e.g., JT96)       | A[K-T][K-T] (e.g., AKQJ) | A[9-6][9-6] (e.g., A987) | A[5-2][5-2] (e.g., A543) | Other A (e.g., AT76) | Other (e.g., KQ98)   |
| -------- | --------------------- | --------------------- | --------------------- | ------------------------ | ------------------------ | ------------------------ | -------------------- | -------------------- |
| UTG      | N/A                   | N/A                   | N/A                   | N/A                      | N/A                      | N/A                      | N/A                  | N/A                  |
| HJ       | 80% ds, 40% ss, 10% r | 70% ds, 30% ss, 5% r  | 50% ds, 10% ss, 0% r  | 90% ds, 50% ss, 10% r    | 70% ds, 20% ss, 0% r     | 50% ds, 10% ss, 0% r     | 60% ds, 10% ss, 0% r | 30% ds, 5% ss, 0% r  |
| CO       | 85% ds, 50% ss, 15% r | 75% ds, 35% ss, 10% r | 55% ds, 15% ss, 5% r  | 95% ds, 60% ss, 15% r    | 75% ds, 25% ss, 5% r     | 55% ds, 15% ss, 0% r     | 65% ds, 15% ss, 0% r | 35% ds, 10% ss, 0% r |
| BTN      | 90% ds, 60% ss, 20% r | 80% ds, 40% ss, 15% r | 60% ds, 20% ss, 10% r | 100% ds, 70% ss, 20% r   | 80% ds, 30% ss, 10% r    | 60% ds, 20% ss, 5% r     | 70% ds, 20% ss, 5% r | 40% ds, 15% ss, 5% r |
| SB       | 85% ds, 50% ss, 15% r | 75% ds, 35% ss, 10% r | 55% ds, 15% ss, 5% r  | 95% ds, 60% ss, 15% r    | 75% ds, 25% ss, 5% r     | 55% ds, 15% ss, 0% r     | 65% ds, 15% ss, 0% r | 35% ds, 10% ss, 0% r |
| BB       | 80% ds, 40% ss, 10% r | 70% ds, 30% ss, 5% r  | 50% ds, 10% ss, 0% r  | 90% ds, 50% ss, 10% r    | 70% ds, 20% ss, 0% r     | 50% ds, 10% ss, 0% r     | 60% ds, 10% ss, 0% r | 30% ds, 5% ss, 0% r  |

#### Additional Hand Examples and Guidelines

To make this as explicit as possible, here are examples of specific hands within these ranges (focusing on value and bluff categories; adjust % based on exact vs. open scenario). These are not all-inclusive but represent common 3-bet spots from solver insights and discussions. Emphasize ds for board coverage, high cards for domination, and connectivity for playability. Avoid weak ss/r unless IP vs. weak open.

- **Premium Value (3-Bet from All Positions vs. Any Open)**: AAKKds (e.g., A♠A♥K♠K♥), AAJTds (A♠A♥J♠T♥), AKQJds (A♠K♥Q♠J♥), JT98ds (J♠T♥9♠8♥), KQJTds (K♠Q♥J♠T♥), QQATss (Q♠Q♦A♥T♥), KKA4ss (K♠K♦A♥4♥).
- **HJ-Specific (vs. UTG Open)**: Tight; AAxx any, KKxx ds, high ds rundowns like AKQJds, JT98ds. Bluff sparingly: A543ds.
- **CO Additions (vs. UTG/HJ)**: Add mid-high ds like QT97ds, JJxx ds with connectors, A987ds. Bluffs: AT76ds, AKxx ss with gaps.
- **BTN Additions (vs. Early Open)**: Loosen; include ss premiums like AA AKQTss, ds one-gappers J987ds, mid pairs 8877ds, QT97ds > JT97ss (better coverage). Bluffs: A-high ds like AT98ds, AT76ds, wheel A543ds.
- **SB Additions (vs. Late Open, e.g., BTN)**: Widest OOP; ds rundowns T987ds, ds one-gappers J987ds, ds broadways AKQTds, ds pairs 8877ds, A-high ds AT98ds/AT76ds, ss premiums QQATss/KKA4ss/AA AKQTss. Bluffs: Axx x ds with blockers.
- **BB Additions (vs. Any)**: Tightest; focus value like AAxx, high ds. Add bluffs if opener weak: A-wheel ds, low ds rundowns if connected.

These represent ~5-12% total hands, polarized (60-70% value, 30-40% bluffs IP; more value OOP). Use merged ranges vs. callers, polarized vs. folders. For exact solvers (e.g., Monker), ranges tighten at higher stakes. If facing a 3-bet, defend ~20-30% (call premiums, 4-bet AAxx).
