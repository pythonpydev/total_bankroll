### Pot Limit Omaha (PLO) Preflop Ranges in a 6-Max Table

In Pot Limit Omaha, starting hands are evaluated based on factors like high card strength, connectedness (for straights), suitedness (for flushes), and pair potential (for sets/full houses). There are 270,725 unique starting hands, so listing every single playable hand explicitly is impractical and not standard in poker strategy. Instead, ranges are described categorically with notations for suitedness (ds = double-suited, ss = single-suited, r = rainbow/no suits matching) and hand structures (e.g., gaps in connectedness: 0g = no gaps like 9876, 1g = one gap like 9875, 2g = two gaps like 9874; Broadway cards like A-K-Q-J-T; mid cards like 9-6).

The ranges below are for **raising first in (RFI)**—i.e., opening the pot when it's folded to you in that position—based on solver-derived data from reputable sources like Upswing Poker. These are conservative to balanced ranges suitable for mid-stakes 6-max PLO cash games (e.g., $1/2 or higher, 100BB stacks). They assume a standard 6-max setup: UTG (first to act), HJ (next, aka middle position), CO (cutoff), BTN (button), SB (small blind), BB (big blind).

- **Total RFI %**: The overall percentage of hands you open-raise from that position.
- For SB: When folded to you, use a looser range than BTN due to positional disadvantage postflop, but tighten vs. aggressive BBs. (No direct RFI for BB since if folded to BB, the pot is won preflop.)
- Adjustments: These are baselines; tighten in tough games or vs. frequent 3-betters, loosen vs. passive players. For BB, focus on defending (calling/3-betting) vs. opens, not opening.
- Sources: Compiled from solver-based guides (e.g., Upswing Poker preflop charts, PokerVIP hand charts, PLO Genius blog, and forum discussions). Percentages indicate the proportion of hands in that subcategory to raise (e.g., 100% ds means raise all double-suited versions).

#### Pairs (Hands with at Least One Pair)

These include premium pairs like AAxx down to low pairs. Raise higher % of suited versions for flush potential.

| Position | Total RFI %                                                                                                   | AA                       | KK                     | QQ                     | JJ                     | TT                     | 99-66                 | 55-22                |
| -------- | ------------------------------------------------------------------------------------------------------------- | ------------------------ | ---------------------- | ---------------------- | ---------------------- | ---------------------- | --------------------- | -------------------- |
| UTG      | 17.9%                                                                                                         | 100% ds, 100% ss, 100% r | 100% ds, 78% ss, 35% r | 87% ds, 43% ss, 24% r  | 76% ds, 34% ss, 15% r  | 57% ds, 33% ss, 10% r  | 49% ds, 14% ss, 2% r  | 23% ds, 6% ss, 1% r  |
| HJ       | 21.8%                                                                                                         | 100% ds, 100% ss, 100% r | 100% ds, 90% ss, 55% r | 93% ds, 61% ss, 31% r  | 83% ds, 43% ss, 20% r  | 71% ds, 36% ss, 17% r  | 57% ds, 20% ss, 3% r  | 32% ds, 7% ss, 1% r  |
| CO       | 30.0%                                                                                                         | 100% ds, 100% ss, 100% r | 100% ds, 97% ss, 88% r | 100% ds, 77% ss, 46% r | 93% ds, 65% ss, 32% r  | 84% ds, 59% ss, 27% r  | 68% ds, 32% ss, 6% r  | 45% ds, 10% ss, 1% r |
| BTN      | 47.2%                                                                                                         | 100% ds, 100% ss, 100% r | 100% ds, 99% ss, 96% r | 100% ds, 98% ss, 86% r | 100% ds, 92% ss, 66% r | 100% ds, 83% ss, 63% r | 90% ds, 58% ss, 19% r | 76% ds, 28% ss, 3% r |
| SB       | ~35-40% (looser than CO, but < BTN; adjust for BB aggression)                                                 | 100% ds, 100% ss, 100% r | 100% ds, 95% ss, 80% r | 100% ds, 85% ss, 60% r | 95% ds, 75% ss, 45% r  | 90% ds, 70% ss, 40% r  | 75% ds, 40% ss, 10% r | 60% ds, 20% ss, 2% r |
| BB       | N/A (defend vs. opens: call/3-bet ~25-35% total hands; e.g., 3-bet premium like AAKKds, call medium rundowns) | N/A                      | N/A                    | N/A                    | N/A                    | N/A                    | N/A                   | N/A                  |

#### Non-Pairs (Wraps, Rundowns, and High-Card Hands)

These are unpaired hands, categorized by gaps (0g/1g/2g for connectedness) and Ace-high vs. others. Prioritize ds for nut flush draws, connected for straights.

| Position | 0g (e.g., JT98)                                                                      | 1g (e.g., JT97)        | 2g (e.g., JT96)        | A[K-T][K-T] (e.g., AKQJ) | A[9-6][9-6] (e.g., A987) | A[5-2][5-2] (e.g., A543) | Other A (e.g., AT76)  | Other (e.g., KQ98)   |
| -------- | ------------------------------------------------------------------------------------ | ---------------------- | ---------------------- | ------------------------ | ------------------------ | ------------------------ | --------------------- | -------------------- |
| UTG      | 90% ds, 71% ss, 20% r                                                                | 93% ds, 49% ss, 11% r  | 58% ds, 16% ss, 4% r   | 100% ds, 64% ss, 0% r    | 72% ds, 25% ss, 0% r     | 49% ds, 7% ss, 0% r      | 69% ds, 2% ss, 0% r   | 20% ds, 1% ss, 0% r  |
| HJ       | 90% ds, 78% ss, 30% r                                                                | 93% ds, 55% ss, 15% r  | 61% ds, 19% ss, 8% r   | 100% ds, 77% ss, 6% r    | 76% ds, 36% ss, 0% r     | 57% ds, 10% ss, 0% r     | 81% ds, 10% ss, 0% r  | 25% ds, 1% ss, 0% r  |
| CO       | 90% ds, 80% ss, 30% r                                                                | 93% ds, 65% ss, 22% r  | 67% ds, 27% ss, 13% r  | 100% ds, 99% ss, 33% r   | 90% ds, 49% ss, 2% r     | 76% ds, 20% ss, 0% r     | 95% ds, 30% ss, 0% r  | 36% ds, 6% ss, 0% r  |
| BTN      | 97% ds, 80% ss, 40% r                                                                | 94% ds, 81% ss, 41% r  | 72% ds, 48% ss, 29% r  | 100% ds, 100% ss, 100% r | 100% ds, 73% ss, 35% r   | 93% ds, 43% ss, 2% r     | 100% ds, 77% ss, 6% r | 60% ds, 20% ss, 3% r |
| SB       | ~95% ds, 75% ss, 35% r (loosen r versions slightly vs. passive BB)                   | ~90% ds, 70% ss, 30% r | ~65% ds, 40% ss, 20% r | 100% ds, 95% ss, 70% r   | 95% ds, 60% ss, 20% r    | 85% ds, 35% ss, 1% r     | 95% ds, 60% ss, 3% r  | 50% ds, 15% ss, 2% r |
| BB       | N/A (defend: call ~80% ds/ss 0g-1g, 3-bet premium like AKQJds; fold weak r versions) | N/A                    | N/A                    | N/A                      | N/A                      | N/A                      | N/A                   | N/A                  |

#### Additional Hand Examples and Guidelines

To make this more explicit, here are examples of specific hands within these ranges (focusing on top-tier ones; weaker ones follow similar patterns but with lower % inclusion):

- **Premium (Playable from All Positions)**: AAKKds (e.g., A♠A♥K♠K♥), AAJTds (A♠A♥J♠T♥), JT98ds (J♠T♥9♠8♥), KQJTds.
- **UTG-Specific Additions**: Tight; focus on nutty hands like AAxx any suits, AKQJds, 9876ds. Avoid weak danglers (unconnected low cards).
- **HJ Additions**: Include more mid pairs like QQxx ss, A987ds, KJT9ss.
- **CO Additions**: Add mid rundowns like T987ss, 8765ds, suited Aces like AQT9ss.
- **BTN Additions**: Loosen to include rainbow broadways like KQJTr, low pairs like 7766ss, gappers like KT97ds, even some multi-gappers like QT86ds.
- **SB Additions**: Similar to CO but add speculative ss hands like 9876ss, A765ss if BB folds often.
- **BB Defending (vs. Open)**: Call with connected ds/ss hands (e.g., 80% of 0g-1g), 3-bet premiums (top 5-10%: AAKK, JT98ds). Fold rainbow low cards.

These ranges represent ~16-48% of hands depending on position, aligning with GTO solvers. For BB, since opening isn't applicable, the focus is on defense (call/3-bet ~30% vs. BTN open). Always adjust based on table dynamics—e.g., open wider on BTN vs. tight blinds. If you need visualizations or equity calculations for specific hands, provide more details!
