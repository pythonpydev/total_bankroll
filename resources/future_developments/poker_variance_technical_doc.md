# Poker Variance Simulator: Enhanced Technical Specification

**Version:** 2.0 | **Platform:** Flask + Chart.js | **Target:** StakeEasy.net

---

## 1. Inputs

| Field | Type | Req | Default | Notes |
|-------|------|-----|---------|-------|
| `winrate` | float | Y | `2.5` | BB/100 |
| `sd` | float | Y | `140.0` | BB/100 |
| `hands` | int | Y | `100000` | ≥1 |
| `observed_wr` | float | N | `None` | BB/100 |
| `bankroll` | float | N | `None` | BB |
| `preset` | str | N | `plo_6max` | Auto-fills `winrate`, `sd` |

**Presets (JSON):**
```json
{
  "plo_6max": {"winrate": 2.5, "sd": 140},
  "plo_fr": {"winrate": 2.0, "sd": 130},
  "nlhe_6max": {"winrate": 3.0, "sd": 100},
  "mtt": {"winrate": 15.0, "sd": 250}
}
```

---

## 2. Backend Logic (Flask `/api/variance`)

### 2.1 Validation
- WTForms + JS real-time
- `winrate > -50`, `sd > 0`, `hands ≥ 1`

### 2.2 Core Stats
```python
ev = (winrate / 100) * hands
total_sd = sd * (hands / 100)**0.5

ci_70 = ev ± 1.04 * total_sd
ci_95 = ev ± 1.96 * total_sd

p_loss = norm.cdf(0, ev, total_sd)
```

### 2.3 Observed Winrate
```python
if observed_wr:
    obs_bb = (observed_wr / 100) * hands
    z = (obs_bb - ev) / total_sd
    p_above = 1 - norm.cdf(z)
```

### 2.4 Risk of Ruin
```python
ror_bankroll = -(sd**2 / (2 * winrate)) * log(0.05)  # <5% ROR
if bankroll:
    survival = 1 - exp(-2 * bankroll * winrate / sd**2)
```

### 2.5 Monte Carlo (20 Paths)
- Per hand: `N(winrate/100, sd/√100)`
- Return list of `[[hand, bb], ...]` for 20 paths
- EV line: `[(0,0), (hands, ev)]`

### 2.6 Downswing Simulation (1 × 100M hands)
- Track: `max_dd`, `dd_duration`, `peak`
- Generate:
  - `% time in ≥X BB downswing` (X = 1k, 5k, 10k)
  - `% time in ≥Y hand downswing` (Y = 10k, 50k, 100k)

---

## 3. Outputs (JSON → Frontend)

```json
{
  "ev": 2500.0,
  "total_sd": 4427.2,
  "ci_70": [290.1, 4709.9],
  "ci_95": [-4170.3, 9170.3],
  "p_loss": 28.4,
  "p_above_observed": 12.1,
  "ror_bankroll": 18432,
  "survival_rate": 96.8,
  "paths": [[[...], [...]], ...],
  "ev_line": [[0,0], [100000,2500]],
  "downswing_freq": {"1000": 31.77, "5000": 8.21},
  "downswing_dur": {"50000": 15.81, "100000": 7.32}
}
```

---

## 4. Frontend (Chart.js)

### 4.1 Main Graph
- 20 `line` datasets (semi-transparent)
- 1 dashed green `ev_line`
- 2 filled bands: 70% (light), 95% (dark)
- Tooltip: `Hand X | +Y BB | Zth %ile`
- Zoom/pan enabled

### 4.2 Downswing Tab
- 1 long path (100k–10M hands)
- Red fill: `current_bb < peak`
- Slider: `input type="range"` → update visible range
- Live panel: `Downswing: -X BB | Duration: Y hands`

---

## 5. Export & Share

- **PNG**: `html2canvas(canvas)`
- **CSV**: `GET /api/variance/csv?params...`
- **Share URL**: `/variance?wr=2.5&sd=140&h=100k&obs=5`

---

## 6. Implementation Steps

| # | Task | Tech |
|---|------|------|
| 1 | Flask blueprint + `/api/variance` | Flask, WTForms |
| 2 | HTML form + presets + validation | JS, Bootstrap |
| 3 | Core stats + Monte Carlo | NumPy, SciPy |
| 4 | Downswing sim (100M) | NumPy vectorized |
| 5 | Chart.js: main + downswing tab | Chart.js + zoom |
| 6 | Export PNG/CSV + share URL | html2canvas, Flask |
| 7 | Caching + mobile CSS | Flask-Caching, media queries |
| 8 | Deploy + link from `/tools` | Jinja nav |
