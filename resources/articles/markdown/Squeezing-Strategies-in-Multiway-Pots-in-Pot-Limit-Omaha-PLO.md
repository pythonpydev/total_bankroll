### Squeezing Strategies in Multiway Pots in Pot Limit Omaha (PLO)

In Pot Limit Omaha (PLO), **squeezing** refers to 3-betting preflop after an initial raise and one or more callers, typically in a multiway pot scenario (three or more players likely to see the flop). The goal is to isolate the original raiser, fold out speculative callers, build the pot with premium hands, or gain fold equity with well-constructed bluffs. In 6-max PLO cash games (100BB stacks), squeezing is a powerful tool to exploit loose-passive tendencies, especially at mid-to-low stakes where players overcall with marginal hands. This guide provides detailed squeezing examples, ranges, and strategies, focusing on multiway scenarios, with concrete hand examples and a narrative for execution. It draws from solver-based insights and expert analyses, emphasizing position, hand selection, and opponent tendencies.

#### Key Factors in Squeezing Multiway Pots

Squeezing in multiway pots is riskier than heads-up due to diluted equities (~40-45% for premiums three-way vs. ~60% heads-up) and higher likelihood of facing calls or 4-bets. Key considerations include:

- **Position**: In position (IP, e.g., BTN/CO) is ideal for squeezing (~10-15% range) due to postflop control and fold equity; out of position (OOP, e.g., blinds) tightens to ~5-8% for value-heavy hands.
- **Hand Selection**: Polarized ranges—value (Tier 1-2: AAxx ds, AKQJds) for pot-building; bluffs (A-high ds with blockers, e.g., A543ds) for fold equity. Avoid marginal hands (e.g., mid pairs ss) that play poorly multiway.
- **Opponent Ranges**: Original raiser’s range (e.g., UTG ~18%, BTN ~47%) and callers’ wider ranges (~30-50%) inform equity. Loose callers justify bigger squeezes; tight ranges demand caution.
- **Bet Sizing**: Size large (~4-5x open or pot-sized, ~12-15BB) to maximize fold equity and deny callers’ odds. Smaller sizes (~3x) IP vs. passive tables.
- **Table Dynamics**: Squeeze more vs. loose-passive callers who fold to 3-bets; tighten vs. aggressive 4-bettors or sticky callers.
- **Stack-to-Pot Ratio (SPR)**: With 100BB, squeezing commits ~10-15% of stack, aiming for low SPR (~2-4) postflop to stack off with ~40%+ equity.

#### Squeezing Ranges and Examples

Below is a table of squeezing ranges for multiway pots (e.g., UTG opens, MP calls, you squeeze). Ranges are polarized: value (~60-70% of squeeze range) for stacks in, bluffs (~30-40% IP, ~10-20% OOP) with nut potential and blockers. Percentages indicate how often to squeeze within each hand category (ds = double-suited, ss = single-suited, r = rainbow; 0g = no gaps like JT98, 1g = one gap like JT97).

| Position                               | Total Squeeze % | Value Hands (Pairs)                                        | Value Hands (Non-Pairs)                                                | Bluff Hands                           | Example Scenarios                                                                                                                                                                                                          |
| -------------------------------------- | --------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **HJ (vs. UTG open + 1-2 callers)**    | ~6-8%           | AA: 100% ds, 80% ss, 40% r; KK: 60% ds, 20% ss; QQ: 30% ds | 0g ds (e.g., JT98ds): 70%; A[K-T][K-T]ds (e.g., AKQJds): 80%           | A-high ds (e.g., A543ds, AT98ds): 20% | **Hand**: A♠A♥K♠Q♥ (AAKQds). **Action**: UTG opens 3BB, MP calls, HJ squeezes to 13BB. **Why**: Value—~55% equity vs. ranges, builds pot. **Postflop**: C-bet dry boards (e.g., K72r); check wet (e.g., 789 two-tone) OOP. |
| **CO (vs. UTG/HJ open + 1-2 callers)** | ~8-10%          | AA: 100% ds, 85% ss, 50% r; KK: 70% ds, 30% ss; QQ: 40% ds | 0g ds: 80%; 1g ds (e.g., JT97ds): 60%; A[K-T][K-T]ds: 90%              | A-high ds: 30%; A[K-T]xx ds: 20%      | **Hand**: K♠Q♥J♠T♥ (KQJTds). **Action**: HJ opens 3BB, MP calls, CO squeezes to 12BB. **Why**: Value—nut straight + flush potential, ~50% three-way. **Postflop**: Bet wraps on coordinated boards; check-call dry.        |
| **BTN (vs. any open + 1-2 callers)**   | ~10-12%         | AA: 100% ds, 90% ss, 60% r; KK: 80% ds, 40% ss; QQ: 50% ds | 0g ds: 90%; 1g ds: 70%; 2g ds (e.g., JT96ds): 30%; A[K-T][K-T]ds: 100% | A-high ds: 40%; A[K-T]xx ds/ss: 30%   | **Hand**: A♠T♥9♠8♥ (AT98ds). **Action**: CO opens 3BB, HJ calls, BTN squeezes to 11BB. **Why**: Bluff—blocks nut flush/straights, fold equity IP. **Postflop**: C-bet wet boards for fold equity; fold to raises.          |
| **SB (vs. any open + 1-2 callers)**    | ~5-7%           | AA: 100% ds, 80% ss, 40% r; KK: 50% ds, 10% ss             | 0g ds: 70%; A[K-T][K-T]ds: 80%                                         | A-high ds: 10% (e.g., A543ds)         | **Hand**: A♠A♥J♠T♥ (AAJTds). **Action**: BTN opens 3BB, CO calls, SB squeezes to 14BB. **Why**: Value—strong equity (~50% multiway), OOP needs pot control. **Postflop**: Lead dry boards; check-call wet with redraws.    |
| **BB (vs. any open + 1-2 callers)**    | ~5-7%           | AA: 90% ds, 70% ss, 30% r; KK: 40% ds                      | 0g ds: 60%; A[K-T][K-T]ds: 70%                                         | A-high ds: 10% (e.g., A543ds)         | **Hand**: J♠T♥9♠8♥ (JT98ds). **Action**: UTG opens 3BB, MP calls, BB squeezes to 14BB. **Why**: Value—nut wrap + flush, ~45% equity. **Postflop**: Bet coordinated boards; check dry without redraws.                      |

#### Concrete Squeezing Examples

Below are specific multiway scenarios with hand examples, actions, and reasoning, tailored for 6-max PLO (100BB). These assume a $1/2 game ($200 stacks) for clarity.

1. **Scenario 1: BTN Squeeze (Value)**
   
   - **Setup**: UTG opens to $7, HJ calls, CO calls. BTN holds A♠A♥K♠K♥ (AAKKds).
   - **Action**: Squeeze to $30 (pot-sized). UTG calls, others fold.
   - **Why**: AAKKds has ~50% equity three-way vs. UTG (~18%) and callers (~30-40% ranges). Sizing maximizes fold equity, isolating UTG. Postflop: C-bet ~2/3-pot on dry boards (e.g., K72r, ~60% equity); check wet boards (e.g., 789 two-tone, ~40% equity) for pot control.
   - **Outcome**: Heads-up vs. UTG, low SPR (~3) favors stacking off with overpair + nut flush draw.

2. **Scenario 2: CO Squeeze (Bluff)**
   
   - **Setup**: HJ opens to $7, MP calls. CO holds A♠T♥9♠8♥ (AT98ds).
   - **Action**: Squeeze to $25. Both fold.
   - **Why**: AT98ds blocks nut flush/straights, has ~45% equity multiway, and fold equity IP vs. loose callers. Smaller size (~3.5x) balances risk. Postflop: C-bet wet boards (e.g., QT9) for fold equity; fold to raises without hits.
   - **Outcome**: Folds win pot outright; if called, play cautiously OOP with non-nut draws.

3. **Scenario 3: BB Squeeze (Value)**
   
   - **Setup**: BTN opens to $7, CO calls. BB holds J♠T♥9♠8♥ (JT98ds).
   - **Action**: Squeeze to $28. BTN calls, CO folds.
   - **Why**: JT98ds has ~45% equity vs. BTN’s wide range (~47%) and CO’s calling range (~35%). Large size denies odds to speculative hands. Postflop: Lead coordinated boards (e.g., 789) for value; check dry (e.g., K22) without redraws.
   - **Outcome**: Heads-up vs. BTN, play aggressively with wraps/flushes; fold to 4-bets without premiums.

4. **Scenario 4: SB Squeeze (Mixed)**
   
   - **Setup**: CO opens to $7, BTN calls. SB holds A♠K♥T♠9♦ (AKT9ds).
   - **Action**: Squeeze to $26. Both call.
   - **Why**: AKT9ds has ~45-50% equity multiway, with nut flush and broadway potential. Size targets loose callers. Postflop: Bet A-high or flushy boards; check-fold low-equity flops (e.g., 234r).
   - **Outcome**: Multiway pot, low SPR (~2); push with nut draws, fold without hits.

#### Narrative for Squeezing Multiway

Squeezing in multiway pots is about exploiting loose calls while building pots with premiums or stealing with fold equity. **IP Strategy**: On BTN/CO, squeeze ~10-12% (e.g., AAxx ds, JT98ds, A543ds as bluffs) vs. opens + 1-2 callers, using smaller sizes (~3-4x) vs. passive tables to balance risk. Postflop, c-bet polarized on favorable boards (dry for AAxx, wet for wraps); check marginal for pot control. **OOP Strategy**: In blinds, tighten to ~5-7% (mostly value like AAKKds, JT98ds), sizing large (~4-5x) to deny odds. Avoid marginal hands (e.g., QQxx ss) that flop poorly multiway. **Exploits**: Vs. loose-passive, squeeze wider (add A-high ds bluffs); vs. tight, stick to premiums to avoid 4-bets. If facing calls, play nut-heavy postflop—bet wraps/flushes, check-fold non-nuts. **Postflop**: Low SPR post-squeeze commits to ~40%+ equity; prioritize redraws (e.g., set + flush draw) multiway. Study solvers (e.g., MonkerSolver) for precise frequencies, but exploit by sizing up vs. callers.
