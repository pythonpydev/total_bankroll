# Mastering PLO Range Construction: Building Balanced and Exploitative Ranges

Pot-Limit Omaha (PLO) is a complex game where constructing effective ranges—both preflop and postflop—is critical for success due to the four-hole-card structure, which creates exponentially more hand combinations (270,725 vs. 1,326 in No-Limit Hold'em). A well-constructed range balances value hands, bluffs, and speculative draws to remain unexploitable while capitalizing on opponent leaks like over-calling or over-folding. Drawing from expert insights from sources like Upswing Poker and Phil Galfond’s Run It Once, this article explains how to build preflop and postflop ranges in PLO, adjust them for position and opponent tendencies, and exploit specific leaks at StakeEasy.net tables.

Whether you’re crafting a tight early-position range or a loose button range, understanding range construction will elevate your PLO game.

## Preflop Range Construction: Principles and Guidelines

PLO preflop ranges are wider than in NLHE due to closer hand equities (e.g., AAxx vs. trash is ~70:30, not 85:15). Key principles include:

- **Connectivity**: Favor hands with coordinated cards (e.g., T♠ 9♠ 8♣ 7♣) for straight/flush potential.
- **High Card Strength**: Prioritize aces and kings for nutted hands.
- **Suitedness**: Single- or double-suited hands (e.g., A♠ K♠ Q♥ J♣) boost flush equity.
- **Position**: Widen ranges in late position; tighten in early position.

### Example Preflop Ranges

Based on expert recommendations, here are starting ranges by position (assuming 100bb stacks, 6-max):

| Position | Range (~% of Hands) | Example Hands            | Notes                                                            |
| -------- | ------------------- | ------------------------ | ---------------------------------------------------------------- |
| UTG      | ~15-20%             | AAxx, AKQJds, T987ss     | Tight, nut-heavy (AA, double-suited rundowns). Avoid weak pairs. |
| MP       | ~25-30%             | A♠ K♠ Q♥ T♣, J♠ T♠ 9♣ 8♣ | Add strong single-suited, connected hands.                       |
| CO       | ~35-40%             | KQJ9ds, T987             | Wider, include speculative draws.                                |
| Button   | ~50-60%             | QJT8ss, KJxx             | Very wide, mix in suited connectors.                             |
| SB/BB    | ~40-50% (calling)   | A♥ Q♥ T♠ 9♣, 9876        | Defend wide vs. raises, prioritize draws.                        |

**Adjustments**:

- **Vs. Loose Players**: Tighten ranges (~10% UTG, ~30% Button) to exploit over-callers with nutted hands.
- **Vs. Tight Players**: Widen ranges (~25% UTG, ~70% Button) to steal blinds and exploit over-folding.
- **3-Betting**: 3-bet premium hands (AAxx double-suited, AKQJds) ~2-3% of hands, wider in position vs. loose openers.

**Tool Tip**: Use PLO Matrix or PokerRanger to visualize ranges and practice construction.

## Postflop Range Construction: Balancing Value and Bluffs

Postflop ranges in PLO must account for board texture, position, and opponent tendencies. Your range should include:

- **Value Hands**: Nuts (flushes, straights, sets), strong two-pairs.
- **Bluffs**: Missed draws with blockers (e.g., A♠ on flush board) or hands with low showdown value.
- **Semi-Bluffs**: Strong draws (wraps, nut flushes) with equity to improve.

### Flop Range Construction

- **Dry Boards (e.g., K♠ 8♣ 2♥)**: Narrow value range (sets, top pair good kicker), bluff with backdoor draws or blockers. C-bet ~40-50% of range vs. one opponent, less multi-way.
- **Wet Boards (e.g., 9♠ 7♦ 6♠)**: Wider value range (sets, wraps, flush draws), semi-bluff strong draws. C-bet ~30% heads-up, check multi-way to pot control.

### Turn and River Ranges

- **Turn**: Polarize with nuts or semi-bluffs (e.g., 13+ out draws). Check marginal hands to avoid bloating pots.
- **River**: Bet polarized (nuts or air with blockers). Bluff-to-value ratio depends on bet size (e.g., 1:1 for pot-sized bets).

**Example**: Board K♦ 7♠ 2♠-Q♥. In position:

- **Value**: K-K-x-x, Q-Q-x-x, K-Q-x-x.
- **Bluffs**: A♠ x x x (flush blocker), missed gutshots.
- **Ratio**: GTO ~1:1 for pot bet; adjust to 2:1 vs. over-folders.

## Exploiting Opponent Leaks in Range Construction

Adjust ranges based on opponent tendencies using HUD stats (e.g., PokerTracker) or live reads.

### 1. Vs. Over-Folders (Nits, Fold to C-Bet >60%)

- **Leak**: Fold too much to aggression, especially on wet boards or rivers.
- **Range Adjustment**:
  - **Preflop**: Widen open-raises (~70% Button) to steal blinds.
  - **Postflop**: C-bet wider (~60% flop, 50% turn), bluff rivers with blockers (e.g., A♠ on 9♠ 7♠ 2♣-Q♥-T♠). Skew to 2:1 bluff-to-value.
- **Example**: Vs. nit in MP, raise Q♥ J♥ T♣ 9♣ from Button, c-bet dry boards like K♣ 4♦ 2♠, barrel turn/river if checked.

### 2. Vs. Over-Callers (Stations, WTSD >35%)

- **Leak**: Call too wide with marginal hands or non-nut draws.
- **Range Adjustment**:
  - **Preflop**: Tighten ranges (~15% UTG, 40% Button) to play nut-heavy hands.
  - **Postflop**: Value bet wider (top pair, second pair on dry boards), minimize bluffs (~1:3 bluff-to-value). Check back semi-bluffs unless equity is nutted.
- **Example**: Vs. station, bet K♠ K♣ Q♥ J♣ on K♦ 8♣ 3♥ for three streets—they call with worse pairs.

### 3. Vs. Over-Aggressors (Maniacs, Agg Factor >3)

- **Leak**: Bluff too often, over-3-bet preflop.
- **Range Adjustment**:
  - **Preflop**: Call wider with speculative hands (e.g., 9♠ 8♠ 7♣ 6♣) to trap their bluffs.
  - **Postflop**: Check-call with medium strength (two-pair, draws), bet nuts for value. Use 1:4 bluff-to-value to exploit their aggression.
- **Example**: Call their 3-bet with A♥ Q♥ T♠ 9♣, check-call flop T♦ 7♠ 2♣, raise turn if draw hits.

### 4. Vs. Under-Bluffers (Tight-Aggressive Regs, Low Bluff Freq)

- **Leak**: Bluff too rarely, fold to river pressure.
- **Range Adjustment**:
  - **Preflop**: 3-bet wider to exploit their tight calling range.
  - **Postflop**: Bluff more on brick rivers (e.g., K♥ 7♣ 2♦-Q♠-4♣), skew to 3:1 bluff-to-value.
- **Example**: Bluff A♠ x x x on flush-completing river—they fold capped ranges.

## Common PLO Range Construction Mistakes and Fixes

1. **Too Wide Preflop in Early Position**:
   
   - **Mistake**: Playing 40% UTG hands (e.g., K♣ Q♦ T♥ 5♠) leads to dominated spots.
   - **Fix**: Tighten to ~15-20% (AAxx, strong rundowns). Use PLO Matrix for guidance.

2. **Over-Bluffing Multi-Way**:
   
   - **Mistake**: C-betting 60% in four-way pots—someone always calls.
   - **Fix**: Check marginal hands, c-bet ~30% multi-way with nuts or strong draws.

3. **Static Postflop Ranges**:
   
   - **Mistake**: Using same c-bet range on dry and wet boards.
   - **Fix**: Adjust by texture—c-bet wider on dry, semi-bluff wet.

4. **Ignoring Blockers**:
   
   - **Mistake**: Bluffing without blockers (e.g., no A♠ on flush board).
   - **Fix**: Include blockers (A♠, key straight cards) in bluff range.

## Practical Application at StakeEasy.net

1. **Build Preflop Charts**: Create UTG-to-Button charts (~15-60% hands) using PLO Matrix. Memorize 10-20 key hands per position.
2. **Track Opponent Stats**: Use PokerTracker to identify leaks (e.g., high WTSD for stations). Adjust ranges dynamically.
3. **Simulate Postflop**: Run flop/turn scenarios in PIOsolver to balance value and bluffs.
4. **Exploit Multi-Way**: Tighten ranges in multi-way pots, value bet vs. stations, bluff vs. nits.

## Example: Constructing a River Range

- **Board**: K♦ 7♠ 2♠-Q♥-T♠
- **Position**: Button, heads-up vs. nit (Fold to River Bet >60%).
- **Range**:
  - **Value**: Nut flush (A♠ x x x), straights (J-9-x-x), sets.
  - **Bluffs**: A♠ x x x (blocks flush), missed wraps (Q-J-9-x).
  - **Ratio**: 2:1 bluff-to-value (exploit nit’s over-folding).
- **Action**: Overbet $150 into $100 pot to maximize fold equity.

## Conclusion: Build Ranges, Win Pots

PLO range construction blends GTO balance with exploitative tweaks. Start with tight, nut-heavy preflop ranges, polarize postflop with value and semi-bluffs, and adjust based on opponent leaks. As Galfond notes, “Your range should tell a story—make it one opponents can’t read.” Practice on StakeEasy.net’s PLO tables, use solvers to refine ranges, and track stats to exploit leaks. Build smart ranges, and your bankroll will grow—good luck!
