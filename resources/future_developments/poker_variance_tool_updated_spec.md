
# Poker Variance Simulator: Enhanced Requirements Specification (StakeEasy.net Edition)

> **Version:** 2.0 | **Target Platform:** StakeEasy.net (Flask + Chart.js)
> **Purpose:** A powerful, interactive, poker-focused variance simulator with PLO emphasis, downswing analytics, bankroll guidance, and shareable results.

---

## 1. Overview

The **Poker Variance Simulator** is a flagship tool for StakeEasy.net, designed to help players—especially in high-variance games like PLO—visualize the impact of statistical variance on their bankroll. Users input performance metrics (winrate, SD, hands), and the tool delivers:

- 20 Monte Carlo bankroll paths
- Confidence intervals (70% & 95%)
- Downswing frequency & duration
- Risk of ruin + bankroll recommendations
- Exportable charts & shareable results

This enhanced version **differentiates from competitors** (e.g., Primedope) with **interactive downswing tracking**, **game-specific presets**, **real-time UX**, and **deep integration** with StakeEasy.net content.

---

## 2. Data Inputs (User-Provided Parameters)

| Field | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| **Winrate (BB/100)** | Float | Yes | `2.5` | True long-term winrate. |
| **Standard Deviation (BB/100)** | Float | Yes | `140.0` | Volatility. **Presets auto-fill this.** |
| **Number of Hands** | Integer | Yes | `100000` | Sample size for simulation. |
| **Observed Winrate (BB/100)** | Float | Optional | `None` | Actual results for probability analysis. |
| **Game Type Preset** | Dropdown | Optional | `PLO 6-Max` | Auto-fills Winrate & SD. Options below. |
| **Current Bankroll (BB)** | Float | Optional | `None` | For risk of ruin & survival analysis. |

### Game Type Presets (Dropdown Options)
```json
{
  "NLHE Full Ring Beginner": {"wr": 1.0, "sd": 70},
  "NLHE 6-Max Regular": {"wr": 3.0, "sd": 100},
  "PLO Full Ring": {"wr": 2.0, "sd": 130},
  "PLO 6-Max (Default)": {"wr": 2.5, "sd": 140},
  "PLO High Stakes": {"wr": 5.0, "sd": 160},
  "MTT Regular": {"wr": 15.0, "sd": 250}
}
```

> **UX Note:** Selecting a preset auto-fills Winrate & SD. Tooltips show: _"PLO 6-Max: High variance, expect 100-160 BB/100 SD"_

---

## 3. Processes (Backend Calculations & Simulation)

### 3.1 Input Validation (Flask + WTForms + JS)
- Real-time JS validation on input
- Prevent negative values, non-numeric entries
- On submit: AJAX POST → JSON response (no full reload)

### 3.2 Core Statistical Calculations
```python
expected_bb = (winrate / 100) * hands
total_sd = sd * sqrt(hands / 100)

ci_70 = expected_bb ± 1.04 * total_sd
ci_95 = expected_bb ± 1.96 * total_sd

prob_loss = norm.cdf(0, loc=expected_bb, scale=total_sd)
```

### 3.3 Observed Winrate Probability (if provided)
```python
observed_bb = (observed_wr / 100) * hands
z = (observed_bb - expected_bb) / total_sd
p_above = 1 - norm.cdf(z, loc=0, scale=1)
```

### 3.4 Risk of Ruin & Bankroll Recommendation
```python
# <5% Risk of Ruin (Kelly-style approximation)
ror_bankroll = -(sd**2 / (2 * winrate)) * log(0.05)

# Survival Rate with User Bankroll
if user_bankroll:
    survival_rate = 1 - exp(-2 * user_bankroll * winrate / sd**2)
```

### 3.5 Monte Carlo Simulation (20 Paths)
- For each path: simulate per-hand result ~ N(winrate/100, sd/√100)
- Store `(hand, bb)` for all 20 paths
- Generate **EV line**: straight from (0,0) to (hands, expected_bb)

### 3.6 Downswing Analysis (100M-Hand Simulation)
- Run **one long simulation** (100M hands)
- Track:
  - Max downswing (BB)
  - Downswing duration (hands)
  - % time in downswing of X+ BB
  - % time in downswing of Y+ hands
- Output: **Frequency Table** + **Duration Table**

---

## 4. Outputs (Results Presented to User)

### 4.1 Interactive Variance Graph (Chart.js)
- **X:** Hands (0 to N)
- **Y:** Winnings (BB)
- **Series:**
  - 20 semi-transparent colored lines (simulated paths)
  - **Dashed green EV line**
  - Light/dark green **70%/95% CI bands**
- **Interactivity:**
  - Hover tooltips: `Hand X | +Y BB | Zth percentile`
  - Zoom/pan (Chart.js zoom plugin)
  - Toggle legend (hide paths, CI, EV)

### 4.2 Downswing Explorer (Second Tab/Chart)
- **Single long-run path** (100k to 10M hands)
- **Red shaded area**: Current downswing from peak
- **Slider**: Adjust visible hand range
- **Live Stats Panel**:
  - Current downswing: `-X BB`
  - Duration: `Y hands`
  - Max downswing: `Z BB`

### 4.3 Variance in Numbers (Table)
| Metric | Value |
|-------|-------|
| Expected Winnings | `X,XXX BB` (`Y.YY BB/100`) |
| Standard Deviation | `X,XXX BB` (`SD BB/100`) |
| 70% Confidence Interval | `±X,XXX BB` |
| 95% Confidence Interval | `±X,XXX BB` |
| Probability of Loss | `XX.X%` |
| P(≥ Observed WR) | `XX.X%` *(if provided)* |
| Minimum Bankroll (<5% ROR) | `X,XXX BB` |
| Survival Rate (Your Bankroll) | `XX.X%` *(if provided)* |

### 4.4 Downswing Frequency & Duration Tables
```text
Downswings of 1,000+ BB: 31.77% of time
Downswings of 5,000+ BB: 8.21% of time
...
Downswings >50,000 hands: 15.81% of time
```

### 4.5 Export & Share
- **Buttons:**
  - `Export Chart as PNG`
  - `Download CSV (All Paths)`
  - `Copy Shareable Link` → `/variance?wr=2.5&sd=140&hands=100000`
- **Embedded Image** for forums (via html2canvas)

---

## 5. Frontend Enhancements (HTML/CSS/JS)

- **Responsive Design**: Mobile-first, charts stack vertically
- **Real-Time Validation**: Inline errors, green checkmarks
- **Tooltips**: Hover over inputs → "Why SD matters in PLO"
- **Educational Modals**: "What is a downswing?" with animations
- **Dark Mode Toggle**: Matches StakeEasy.net theme
- **PLO Branding**: Default preset = PLO 6-Max, banner: _"Built for Pot-Limit Omaha Players"_

---

## 6. Backend Enhancements (Flask)

- **Blueprint**: `tools/variance_simulator.py`
- **AJAX Route**: `POST /api/variance` → returns JSON
- **Caching**: `Flask-Caching` for common inputs (e.g., 100k hands, PLO preset)
- **CSV Export**: Stream simulation data
- **Shareable URLs**: Encode params in query string
- **User Integration** (Future): Pull stats from logged-in user profile

---

## 7. Project Implementation Steps

| Step | Task | Tools |
|------|------|-------|
| 1 | Create Flask Blueprint + `/tools/variance-simulator` route | Python, Flask |
| 2 | Design HTML template with form, tabs, canvas | Jinja2, Bootstrap |
| 3 | Implement input validation (JS + WTForms) | JavaScript, WTForms |
| 4 | Add Game Presets + real-time field population | JS event listeners |
| 5 | Build core stats + Monte Carlo (20 paths) | NumPy, SciPy |
| 6 | Add 100M-hand downswing simulation | NumPy (vectorized) |
| 7 | Render main graph with Chart.js + interactivity | Chart.js + zoom plugin |
| 8 | Build Downswing Explorer tab + slider | Chart.js + noUiSlider |
| 9 | Add Export PNG/CSV + Shareable Link | html2canvas, Flask response |
| 10 | Integrate with site nav + add to Tools page | HTML edit |
| 11 | Test edge cases (negative WR, 1M+ hands) | Pytest |
| 12 | Launch + promote via PLO article | Marketing |

---

## 8. Differentiation from Primedope

| Feature | Primedope | **StakeEasy.net (Yours)** |
|-------|---------|---------------------------|
| Game Presets | No | Yes (PLO-focused) |
| Downswing Slider | Yes | Interactive + Live Stats |
| Bankroll Survival % | No | Yes |
| Export/Share | No | Yes |
| Real-Time Validation | No | Yes |
| Mobile Responsive | Basic | Yes |
| Educational Tooltips | No | Yes |
| Site Integration | No | Yes (user stats, articles) |

---

## 9. Future-Proof Extensions

- [ ] **User Dashboard**: Save simulations, track real results
- [ ] **Tilt Risk Score**: Based on downswing duration
- [ ] **PLO Hand History Upload**: Auto-extract WR/SD
- [ ] **MTT Mode**: ROI-based variance with prize pool chop

---

**Built for StakeEasy.net — Where PLO Players Master Variance.**

---
