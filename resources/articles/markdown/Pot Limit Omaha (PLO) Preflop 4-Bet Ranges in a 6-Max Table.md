### Pot Limit Omaha (PLO) Preflop 4-Bet Ranges in a 6-Max Table

In Pot Limit Omaha (PLO), a **4-bet** is a re-re-raise (raising after a 3-bet) in response to an initial raise and a 3-bet. Given the high variance and close equities in PLO, 4-bet ranges are highly polarized, focusing on **premium value hands** (for getting stacks in preflop) and occasional **bluffs** (with blockers and nut potential for fold equity). These ranges are context-dependent, varying by position, stack sizes (assuming 100BB standard), the opener’s range, the 3-bettor’s tendencies, and whether you’re in position (IP) or out of position (OOP). With 270,725 unique starting hands, listing every 4-bet hand is impractical, so ranges are categorized by structure (pairs, rundowns, suitedness: ds = double-suited, ss = single-suited, r = rainbow) with percentages indicating the proportion of that subcategory to 4-bet.

These ranges are solver-inspired for mid-stakes 6-max cash games, drawn from strategy discussions on forums like TwoPlusTwo, articles from Upswing Poker and PokerVIP, and general GTO principles (e.g., MonkerSolver/PIO insights, though specific charts are often proprietary). Total 4-bet percentages are tight (typically 1-3% of hands), as 4-betting commits a large portion of the stack, especially OOP, and is often for value to build the pot or go all-in preflop. Adjustments are critical: tighten vs. nitty 3-bettors, loosen vs. aggressive ones with wider 3-bet ranges.

- **Total 4-Bet %**: Percentage of hands to 4-bet vs. a typical 3-bet (e.g., vs. BTN 3-bet from BB). OOP (e.g., BB) 4-bets are value-heavy (~80-90% value, 10-20% bluffs); IP (e.g., BTN) can include more bluffs (~60-70% value, 30-40% bluffs).
- **Value Hands**: Premium AAxx, high ds rundowns, and connected broadways with nut potential (e.g., AAKKds, JT98ds).
- **Bluffs**: A-high ds hands with blockers (e.g., A543ds, AKxxds) to deny nut flush/straight equity, used more IP or vs. loose 3-bettors.
- **Sizing**: Pot-sized (~3-3.5x the 3-bet) to commit stacks or maximize fold equity. With shallow SPR post-4-bet, prepare to get it in.
- **UTG**: Rarely 4-bets, as it’s first to act (only possible if UTG opens, faces a 3-bet, then 4-bets; extremely tight due to multiway risk).

Below are 4-bet ranges for a 6-max table (UTG, HJ, CO, BTN, SB, BB), assuming a standard scenario (e.g., CO opens, BTN 3-bets, SB/BB 4-bets, or BTN opens, BB 3-bets, CO 4-bets). Percentages are approximate, reflecting how often to 4-bet within each hand category.

#### Pairs (Hands with at Least One Pair)

Focus on AAxx for value (nut sets, redraws) and high pairs with strong side cards. Low pairs rarely 4-bet unless ds and connected.

| Position | Total 4-Bet % (vs. Typical 3-Bet) | AA                     | KK                    | QQ                   | JJ                   | TT-99               | 88-66               | 55-22 |
| -------- | --------------------------------- | ---------------------- | --------------------- | -------------------- | -------------------- | ------------------- | ------------------- | ----- |
| UTG      | ~0.5-1% (vs. any 3-bet, rare)     | 100% ds, 80% ss, 50% r | 50% ds, 20% ss, 0% r  | 20% ds, 0% ss, 0% r  | 0%                   | 0%                  | 0%                  | 0%    |
| HJ       | ~1-1.5% (vs. MP/CO/BTN/SB)        | 100% ds, 85% ss, 60% r | 60% ds, 25% ss, 0% r  | 30% ds, 10% ss, 0% r | 10% ds, 0% ss, 0% r  | 0%                  | 0%                  | 0%    |
| CO       | ~1.5-2% (vs. BTN/SB/BB)           | 100% ds, 90% ss, 70% r | 70% ds, 30% ss, 10% r | 40% ds, 15% ss, 0% r | 20% ds, 0% ss, 0% r  | 10% ds, 0% ss, 0% r | 0%                  | 0%    |
| BTN      | ~2-3% (vs. SB/BB)                 | 100% ds, 95% ss, 80% r | 80% ds, 40% ss, 15% r | 50% ds, 20% ss, 5% r | 30% ds, 10% ss, 0% r | 20% ds, 5% ss, 0% r | 10% ds, 0% ss, 0% r | 0%    |
| SB       | ~1-1.5% (vs. any)                 | 100% ds, 90% ss, 60% r | 60% ds, 25% ss, 0% r  | 30% ds, 10% ss, 0% r | 10% ds, 0% ss, 0% r  | 0%                  | 0%                  | 0%    |
| BB       | ~1-2% (vs. any)                   | 100% ds, 85% ss, 50% r | 50% ds, 20% ss, 0% r  | 20% ds, 0% ss, 0% r  | 0%                   | 0%                  | 0%                  | 0%    |

#### Non-Pairs (Wraps, Rundowns, and High-Card Hands)

High ds rundowns for nut straights/flushes; bluffs with A-high ds for blockers. 0g = no gaps (e.g., JT98), 1g = one gap (e.g., JT97), 2g = two gaps (e.g., JT96). A-high prioritized for nut potential.

| Position | 0g (e.g., JT98)       | 1g (e.g., JT97)      | 2g (e.g., JT96)      | A[K-T][K-T] (e.g., AKQJ) | A[9-6][9-6] (e.g., A987) | A[5-2][5-2] (e.g., A543) | Other A (e.g., AT76) | Other (e.g., KQ98)   |
| -------- | --------------------- | -------------------- | -------------------- | ------------------------ | ------------------------ | ------------------------ | -------------------- | -------------------- |
| UTG      | 50% ds, 20% ss, 0% r  | 40% ds, 10% ss, 0% r | 20% ds, 0% ss, 0% r  | 70% ds, 30% ss, 0% r     | 40% ds, 10% ss, 0% r     | 30% ds, 0% ss, 0% r      | 30% ds, 0% ss, 0% r  | 10% ds, 0% ss, 0% r  |
| HJ       | 60% ds, 25% ss, 0% r  | 50% ds, 15% ss, 0% r | 30% ds, 5% ss, 0% r  | 80% ds, 40% ss, 10% r    | 50% ds, 15% ss, 0% r     | 40% ds, 5% ss, 0% r      | 40% ds, 5% ss, 0% r  | 20% ds, 0% ss, 0% r  |
| CO       | 70% ds, 30% ss, 5% r  | 60% ds, 20% ss, 0% r | 40% ds, 10% ss, 0% r | 90% ds, 50% ss, 15% r    | 60% ds, 20% ss, 0% r     | 50% ds, 10% ss, 0% r     | 50% ds, 10% ss, 0% r | 30% ds, 5% ss, 0% r  |
| BTN      | 80% ds, 40% ss, 10% r | 70% ds, 30% ss, 5% r | 50% ds, 15% ss, 0% r | 100% ds, 60% ss, 20% r   | 70% ds, 30% ss, 5% r     | 60% ds, 15% ss, 0% r     | 60% ds, 15% ss, 0% r | 40% ds, 10% ss, 0% r |
| SB       | 60% ds, 25% ss, 0% r  | 50% ds, 15% ss, 0% r | 30% ds, 5% ss, 0% r  | 80% ds, 40% ss, 10% r    | 50% ds, 15% ss, 0% r     | 40% ds, 5% ss, 0% r      | 40% ds, 5% ss, 0% r  | 20% ds, 0% ss, 0% r  |
| BB       | 50% ds, 20% ss, 0% r  | 40% ds, 10% ss, 0% r | 20% ds, 0% ss, 0% r  | 70% ds, 30% ss, 0% r     | 40% ds, 10% ss, 0% r     | 30% ds, 0% ss, 0% r      | 30% ds, 0% ss, 0% r  | 10% ds, 0% ss, 0% r  |

#### Additional Hand Examples and Guidelines

To be explicit, here are specific hand examples within these ranges, focusing on value and bluff categories. These are not exhaustive but reflect common 4-bet spots based on solver insights and strategy discussions. Emphasize ds for nut flush/straight potential, AAxx for set value, and blockers for bluffs. Avoid weak ss/r unless IP vs. loose 3-bettors.

- **Premium Value (4-Bet from All Positions vs. Any 3-Bet)**:
  
  - **AAxx**: A♠A♥K♠K♥ (AAKKds), A♠A♥J♠T♥ (AAJTds), A♠A♥Q♠J♣ (AAQJds), A♠A♥K♦Q♣ (AAxx r with broadways).
  - **High Rundowns**: AKQJds (A♠K♥Q♠J♥), JT98ds (J♠T♥9♠8♥), KQJTds (K♠Q♥J♠T♥), QQATds (Q♠Q♦A♥T♥).
  - **High Pairs**: KKA4ds (K♠K♦A♥4♥), QQKJds (Q♠Q♥K♠J♥).

- **UTG/HJ (vs. Any 3-Bet, e.g., CO/BTN)**: Ultra-tight due to multiway risk and OOP. 4-bet AAxx ds/ss (e.g., A♠A♥K♠Q♥, A♠A♥J♦T♣), top ds rundowns like AKQJds, JT98ds. Bluffs rare: A543ds (wheel potential) vs. loose 3-bettors only.

- **CO Additions (vs. BTN/SB/BB 3-Bet)**: Add KKxx ds with connectors (K♠K♥Q♠J♥), ds one-gappers like KJ98ds, AAKQss (A♠A♣K♥Q♥). Bluffs: AT98ds, A543ds for nut blockers.

- **BTN Additions (vs. SB/BB 3-Bet)**: Widest IP range; include AAxx r (A♠A♥K♦J♣), ds mid pairs like JJT9ds, ss premiums like AKQJss, one-gappers J987ds. Bluffs: A-high ds like AT76ds, AKxxds (A♠K♥T♣9♦), wheel A543ds for fold equity.

- **SB Additions (vs. Any 3-Bet)**: Tight OOP; focus on AAxx ds/ss, high ds rundowns (AKQJds, JT98ds), KKxx ds with connectors. Bluffs: A543ds, AT98ds vs. loose BTN 3-bets.

- **BB Additions (vs. Any 3-Bet)**: Tightest OOP; AAxx ds/ss (A♠A♥K♠Q♥, A♠A♥J♦T♣), high ds rundowns (JT98ds, KQJTds). Bluffs: A543ds, AKxxds vs. aggressive 3-bettors (e.g., BTN vs. tight CO open).

#### Key Considerations

- **Total Range**: ~1-3% of hands (50-100 combos). Value-heavy OOP (BB/SB: ~80% value, e.g., AAxx, AKQJds); balanced IP (BTN: ~60% value, 40% bluffs like A543ds, ATxxds).
- **Adjustments**: Vs. tight 3-bettors (e.g., BB 3-bet vs. BTN), 4-bet only premiums (AAxx, JT98ds). Vs. loose 3-bettors (e.g., BTN 3-bet vs. CO), add bluffs (A543ds, AKxxds). Tighten multiway or with short stacks (~50BB, favor value).
- **Facing a 4-Bet**: Call ~10-15% (AAxx, AKQJds), 5-bet ~1% (AAKKds, AAJTds). Fold weaker hands due to pot commitment.
- **Board Coverage**: Prioritize ds for nut flushes, connected cards for straights, AA for sets. Bluffs need blockers (A-high) and playability.

These ranges align with GTO solvers like MonkerSolver, but adjust dynamically based on 3-bettor’s range and table tendencies. For specific matchups (e.g., CO vs. BTN 3-bet), provide details for tailored ranges!
