# StakeEasy.net Technical Specification

**Version:** 1.0.0  
**Last Updated:** 2025-11-05  
**Status:** Active

## Executive Summary

StakeEasy.net is a Flask-based web application that provides poker players with professional-grade bankroll management, intelligent stake recommendations, poker tools, and educational content focused primarily on Pot Limit Omaha (PLO).

### Key Capabilities
- Multi-currency bankroll tracking across poker sites and assets
- Intelligent stake recommendations based on bankroll, skill, and risk tolerance
- Interactive poker tools (equity calculators, hand evaluators, SPR analysis)
- Educational article repository with tagging and progress tracking
- Achievement and goal-setting system for player motivation
- OAuth integration (Google, Facebook) alongside traditional authentication

---

## 1. System Architecture

### 1.1 Technology Stack

#### Backend
- **Framework:** Flask 3.x with Python 3.9+
- **ORM:** SQLAlchemy with Flask-Migrate (Alembic)
- **Database:** MySQL 8.0+
- **Authentication:** Flask-Security-Too (Argon2 password hashing)
- **OAuth:** Flask-Dance (Google, Facebook providers)
- **Email:** Flask-Mail with Gmail SMTP
- **Rate Limiting:** Flask-Limiter
- **Security:** Flask-WTF (CSRF), Flask-Principal (permissions)

#### Frontend
- **Templating:** Jinja2 with auto-escaping
- **Styling:** Bootstrap 5.x
- **Build Tool:** Vite 7.x for asset bundling
- **JavaScript:** Vanilla JS with modular utilities

#### Infrastructure
- **Development:** Local MySQL, Flask development server
- **Production:** PythonAnywhere with WSGI, MySQL-as-a-service
- **CI/CD:** GitHub Actions for Python linting and testing
- **Version Control:** Git with GitHub

### 1.2 Project Structure

```
/home/ed/MEGA/total_bankroll/           # Development root
├── .env                                 # Environment-specific configuration
├── .github/workflows/                   # CI/CD pipelines
├── migrations/                          # Alembic migration scripts
├── src/total_bankroll/                  # Application package
│   ├── __init__.py                     # App factory
│   ├── config.py                       # Configuration classes
│   ├── models.py                       # SQLAlchemy models
│   ├── extensions.py                   # Flask extension instances
│   ├── oauth.py                        # OAuth configuration
│   ├── commands.py                     # Flask CLI commands
│   ├── recommendations.py              # Stake recommendation engine
│   ├── currency.py                     # Currency conversion utilities
│   ├── data_utils.py                   # Data processing helpers
│   ├── utils.py                        # General utilities
│   ├── vite_asset_helper.py           # Asset URL generation
│   ├── data/                           # JSON configuration files
│   │   └── recommendation_logic.json   # Stake recommendation rules
│   ├── frontend/                       # Blueprint modules (routes)
│   │   └── main.js                     # Primary JavaScript entry
│   ├── routes/                         # Route definitions
│   ├── static/                         # Static assets
│   │   ├── assets/                     # Vite build output
│   │   ├── css/                        # Stylesheets
│   │   ├── images/                     # Images
│   │   └── js/                         # JavaScript utilities
│   └── templates/                      # Jinja2 templates
│       ├── articles/                   # Article views
│       ├── charts/                     # Chart/visualization views
│       ├── core/                       # Base layouts
│       ├── forms/                      # Form templates
│       ├── info/                       # Static information pages
│       ├── partials/                   # Reusable components
│       ├── quiz/                       # Interactive quiz templates
│       ├── security/                   # Auth-related views
│       └── tools/                      # Poker tool interfaces
├── tests/                              # Pytest test suite
├── scripts/                            # Utility scripts
├── requirements.in                     # Direct dependencies
├── requirements.txt                    # Pinned dependencies (pip-tools)
├── package.json                        # Node.js dependencies
├── vite.config.js                      # Vite configuration
└── wsgi.py                             # WSGI entry point
```

### 1.3 Environment Configuration

#### Development Environment
```
Path: /home/ed/MEGA/total_bankroll/
Database: bankroll (user: root, host: localhost)
FLASK_ENV: development
Debug Mode: Enabled
```

#### Production Environment (PythonAnywhere)
```
Path: /home/pythonpydev/total_bankroll/
Database: pythonpydev$bankroll (user: pythonpydev, remote host)
FLASK_ENV: production
Debug Mode: Disabled
Served via: WSGI
```

---

## 2. Data Models

### 2.1 Core Database Schema

#### User Management
- **users**: User accounts with email, hashed password, 2FA settings, activity tracking
- **roles**: User roles for permission management (future use)
- **oauth**: OAuth provider tokens and user associations

#### Bankroll Tracking
- **sites**: Poker sites/platforms where funds are held
- **assets**: Non-site assets (cash, cryptocurrency, etc.)
- **deposits**: Money added to bankroll
- **drawings**: Money withdrawn from bankroll
- **site_history**: Time-series balance snapshots for sites
- **asset_history**: Time-series value snapshots for assets
- **currency**: Exchange rates for multi-currency support

#### Poker Tools & Content
- **cash_stakes**: Standard cash game blind structures
- **articles**: Strategy articles with markdown source and HTML rendering
- **tags**: Article categorization tags
- **article_tags**: Many-to-many relationship between articles and tags

#### Gamification
- **goals**: User-defined bankroll or activity goals
- **achievements**: Available achievements (badges)
- **user_achievements**: Unlocked achievements per user
- **user_read_articles**: Reading progress tracking
- **user_tool_usage**: Tool usage tracking for achievements

### 2.2 Key Relationships

```
User (1) ──< (M) Sites
User (1) ──< (M) Assets
User (1) ──< (M) Deposits
User (1) ──< (M) Drawings
User (1) ──< (M) SiteHistory
User (1) ──< (M) AssetHistory
User (1) ──< (M) Goals
User (1) ──< (M) UserAchievements
User (1) ──< (M) Articles (as author)
User (M) ──< (M) Articles (via UserReadArticle)

Sites (1) ──< (M) SiteHistory
Assets (1) ──< (M) AssetHistory
Articles (M) ──< (M) Tags (via article_tags)
```

### 2.3 Currency Handling

All monetary amounts are stored with their currency code (ISO 4217). The `currency` table maintains exchange rates relative to USD (base currency). Conversions happen at display time using the `currency.py` utility module.

**Decimal Precision:** All monetary columns use `Numeric(10, 2)` for accurate financial calculations.

---

## 3. Core Features

### 3.1 Authentication & User Management

#### Registration Flow
1. User submits email and password
2. System generates confirmation token
3. Email sent with confirmation link
4. User clicks link, account activated
5. User redirected to dashboard

#### Authentication Methods
- **Email/Password:** Argon2-hashed passwords
- **OAuth:** Google and Facebook via Flask-Dance
- **2FA (Optional):** TOTP-based two-factor authentication

#### Security Features
- CSRF protection on all forms
- Rate limiting on authentication endpoints
- Session management with secure cookies
- X-Frame-Options: SAMEORIGIN header
- Password strength validation
- Email confirmation required for new accounts

### 3.2 Bankroll Management

#### Sites & Assets
- **Create/Edit/Delete:** Users manage poker sites and other assets
- **Display Ordering:** Custom ordering via drag-and-drop (stored in `display_order` field)
- **Multi-Currency:** Each site/asset can be denominated in different currencies

#### Deposits & Withdrawals
- **Quick Entry:** Mobile-optimized forms for fast data entry
- **Currency Conversion:** Automatic conversion to base currency for totals
- **History Tracking:** Automatic snapshots stored in `site_history` and `asset_history`

#### Dashboard Views
- **Current Balances:** Real-time total across all sites and assets
- **Total Deposits/Withdrawals:** Lifetime totals
- **Profit Calculation:** `(Current Bankroll) - (Total Deposits) + (Total Withdrawals)`
- **Visual Charts:** Pie charts for bankroll distribution, line charts for growth over time

### 3.3 Stake Recommendations

**Engine Location:** `src/total_bankroll/recommendations.py`

#### Tournament Recommendations
- **Input:** Total bankroll, game type, skill level, risk tolerance, game environment
- **Algorithm:**
  1. Calculate weighted buy-in multiple from user selections
  2. Compute ideal average buy-in: `bankroll / multiple`
  3. Find closest standard tournament stake ≤ ideal buy-in
  4. Generate move-up threshold (bankroll needed for next stake)
  5. Generate move-down threshold (minimum safe bankroll for current stake)

#### Cash Game Recommendations
- **Input:** Total bankroll, game type, skill level, risk tolerance, game environment
- **Algorithm:**
  1. Calculate weighted buy-in multiple (based on max buy-ins)
  2. Iterate stakes from highest to lowest
  3. Find highest stake where `bankroll ≥ (max_buy_in × multiple)`
  4. Generate move-up message (amount needed for next stake)
  5. Generate stop-loss threshold (minimum for current stake based on min buy-in)

#### Configuration
- **File:** `src/total_bankroll/data/recommendation_logic.json`
- **Structure:**
  - `weights`: Importance of each selection factor
  - `cash_game.ranges`: Buy-in multiples for each selection
  - `tournament.ranges`: Buy-in multiples for each selection

### 3.4 Poker Tools

#### Hand Evaluator
- **Input:** Poker hand description
- **Output:** Hand strength category, equity estimates
- **Use Case:** Quick assessment of starting hand strength

#### Equity Calculator (PLO vs Random)
- **Input:** PLO hand (4 cards)
- **Output:** Equity percentage against random hands
- **Technology:** Pre-computed lookup tables for performance

#### SPR Calculator
- **Input:** Stack size, pot size
- **Output:** Stack-to-Pot Ratio and strategic implications
- **Educational:** Includes explanations of SPR ranges

#### Variance Simulator
- **Input:** Win rate, standard deviation, sample size
- **Output:** Monte Carlo simulation showing bankroll swings
- **Purpose:** Teaching variance reality to players

### 3.5 Educational Content

#### Article System
- **Storage:** Markdown source in `content_md`, rendered HTML in `content_html`
- **Tagging:** Many-to-many relationship for categorization
- **Reading Progress:** Tracked in `user_read_articles` for achievements
- **Search & Filter:** By tag, date, or full-text search

#### Quiz System (Future)
- **Template Structure:** `templates/quiz/`
- **Purpose:** Interactive learning validation
- **Integration:** Tied to article content for testing comprehension

### 3.6 Gamification

#### Achievements
- **Categories:** Bankroll milestones, consistency, learning, tool usage
- **Tracking:** Automatic based on user activity
- **Display:** Badge icons with unlock timestamps

#### Goals
- **Types:** Bankroll targets, activity goals (sessions, articles read)
- **Status:** Active, completed, archived
- **Progress Visualization:** Percentage completion, time remaining

#### Streak Tracking
- **Metric:** Consecutive days of activity (login, logging, or reading)
- **Storage:** `users.streak_days` and `users.last_activity_date`
- **Reset Logic:** Automatically resets if >24 hours pass without activity

---

## 4. API Endpoints & Routes

### 4.1 Authentication Routes (`auth_bp`)
- `GET /login` - Login form
- `POST /login` - Authenticate user
- `GET /register` - Registration form
- `POST /register` - Create new account
- `GET /logout` - End user session
- `GET /confirm/<token>` - Email confirmation
- `GET /forgot-password` - Password reset request
- `POST /forgot-password` - Send reset email
- `GET /reset-password/<token>` - Password reset form
- `POST /reset-password/<token>` - Update password

### 4.2 OAuth Routes (`oauth.py`)
- `GET /login/google` - Initiate Google OAuth
- `GET /login/google/callback` - Google OAuth callback
- `GET /login/facebook` - Initiate Facebook OAuth
- `GET /login/facebook/callback` - Facebook OAuth callback

### 4.3 Core Application Routes
- `GET /` - Dashboard (home_bp)
- `GET /about` - About page (about_bp)
- `GET /help` - Help documentation (help_bp)
- `GET /legal/privacy` - Privacy policy (legal_bp)
- `GET /legal/terms` - Terms of service (legal_bp)

### 4.4 Bankroll Routes
- `GET /sites` - List poker sites (poker_sites_bp)
- `POST /sites` - Create new site
- `PUT /sites/<id>` - Update site
- `DELETE /sites/<id>` - Delete site
- `GET /assets` - List assets (assets_bp)
- `POST /assets` - Create new asset
- `PUT /assets/<id>` - Update asset
- `DELETE /assets/<id>` - Delete asset
- `GET /deposits` - Deposit history (deposit_bp)
- `GET /deposits/add` - Add deposit form (add_deposit_bp)
- `POST /deposits/add` - Submit deposit
- `GET /withdrawals` - Withdrawal history (withdrawal_bp)
- `GET /withdrawals/add` - Add withdrawal form (add_withdrawal_bp)
- `POST /withdrawals/add` - Submit withdrawal

### 4.5 Analytics Routes (`charts_bp`)
- `GET /charts/bankroll-over-time` - Time-series chart data
- `GET /charts/bankroll-distribution` - Pie chart data
- `GET /charts/profit-loss` - P&L visualization

### 4.6 Tools Routes (`tools_bp`, `hand_eval_bp`)
- `GET /tools` - Tools landing page
- `GET /tools/hand-evaluator` - Hand evaluation tool
- `POST /tools/hand-evaluator` - Evaluate hand
- `GET /tools/equity-calculator` - PLO equity calculator
- `POST /tools/equity-calculator` - Calculate equity
- `GET /tools/spr-calculator` - SPR analysis tool
- `POST /tools/spr-calculator` - Calculate SPR
- `GET /tools/variance-simulator` - Variance simulation
- `POST /tools/variance-simulator` - Run simulation

### 4.7 Content Routes (`articles_bp`)
- `GET /articles` - Article listing
- `GET /articles/<id>` - View article
- `GET /articles/tag/<tag>` - Filter by tag
- `POST /articles/<id>/mark-read` - Track reading progress

### 4.8 Gamification Routes (`goals_bp`, `achievements_bp`)
- `GET /goals` - User goals dashboard
- `POST /goals` - Create new goal
- `PUT /goals/<id>` - Update goal
- `DELETE /goals/<id>` - Archive goal
- `GET /achievements` - Achievement listing
- `GET /achievements/<id>` - Achievement details

### 4.9 Settings Routes (`settings_bp`)
- `GET /settings` - User settings page
- `POST /settings/profile` - Update profile
- `POST /settings/currency` - Change default currency
- `POST /settings/2fa/enable` - Enable 2FA
- `POST /settings/2fa/disable` - Disable 2FA

### 4.10 Common Utilities (`common_bp`)
- `GET /currency/update` - Manual currency rate refresh
- `POST /currency/convert` - Currency conversion endpoint

---

## 5. Business Logic

### 5.1 Recommendation Engine

**Weighted Range Calculation (`_calculate_weighted_range`)**

```python
# Pseudocode
total_weight = sum(weight for each selection)
weighted_low = sum(low_range * weight for each selection)
weighted_high = sum(high_range * weight for each selection)

avg_low = round(weighted_low / total_weight)
avg_high = round(weighted_high / total_weight)
avg_multiple = (avg_low + avg_high) / 2

return {
    "low": avg_low,
    "high": avg_high,
    "average_multiple": avg_multiple,
    "recommendation_string": f"{avg_low} to {avg_high} {unit}"
}
```

**Tournament Stake Selection**
```python
ideal_buy_in = total_bankroll / buy_in_multiple

# Find closest stake ≤ ideal_buy_in
for stake in reversed(tournament_stakes):
    if stake.buy_in <= ideal_buy_in:
        recommended_stake = stake
        break

# Calculate move-up threshold
next_stake = tournament_stakes[current_index + 1]
required_bankroll = next_stake.buy_in * buy_in_multiple
shortfall = required_bankroll - total_bankroll

# Calculate move-down threshold
min_bankroll = current_stake.buy_in * buy_in_multiple
buffer = total_bankroll - min_bankroll
```

**Cash Game Stake Selection**
```python
# Iterate from highest to lowest stake
for stake in reversed(cash_stakes):
    required_bankroll = stake.max_buy_in * buy_in_multiple
    if total_bankroll >= required_bankroll:
        recommended_stake = stake
        break

# Move-up calculation
next_stake = cash_stakes[current_index + 1]
required = next_stake.max_buy_in * buy_in_multiple
shortfall = required - total_bankroll

# Stop-loss calculation
move_down_threshold = current_stake.min_buy_in * buy_in_multiple
buffer = total_bankroll - move_down_threshold
```

### 5.2 Achievement Tracking

**Achievement Types & Triggers**

| Category | Example Achievement | Trigger Event |
|----------|---------------------|---------------|
| Bankroll | "First $1,000" | Bankroll reaches $1,000 |
| Consistency | "7-Day Streak" | 7 consecutive activity days |
| Learning | "Article Reader" | Read 10 articles |
| Tools | "Calculator Pro" | Use hand evaluator 50 times |

**Unlock Logic (Conceptual)**
```python
def check_achievements(user):
    achievements_to_unlock = []
    
    # Bankroll milestone check
    current_bankroll = calculate_total_bankroll(user)
    for achievement in get_bankroll_achievements():
        if current_bankroll >= achievement.target:
            if not user_has_achievement(user, achievement):
                achievements_to_unlock.append(achievement)
    
    # Streak check
    if user.streak_days >= 7:
        unlock_achievement(user, "7-day-streak")
    
    # Article reading check
    articles_read = count_user_read_articles(user)
    if articles_read >= 10:
        unlock_achievement(user, "article-reader")
    
    # Tool usage check
    tool_uses = count_tool_usage(user, "hand_evaluator")
    if tool_uses >= 50:
        unlock_achievement(user, "calculator-pro")
    
    return achievements_to_unlock
```

### 5.3 Currency Conversion

**Rate Storage**
- Base currency: USD (rate = 1.000000)
- All other rates stored relative to USD
- Updated daily via external API (ExchangeRate-API)

**Conversion Formula**
```python
def convert_to_base(amount, from_currency):
    """Convert any currency to USD"""
    rate = get_exchange_rate(from_currency)  # Rate to USD
    return amount * rate

def convert_from_base(amount, to_currency):
    """Convert USD to any currency"""
    rate = get_exchange_rate(to_currency)
    return amount / rate

def convert(amount, from_currency, to_currency):
    """Convert between any two currencies"""
    usd_amount = convert_to_base(amount, from_currency)
    return convert_from_base(usd_amount, to_currency)
```

### 5.4 Profit Calculation

```python
total_deposits = sum(all deposits in base currency)
total_withdrawals = sum(all withdrawals in base currency)
current_bankroll = sum(all sites + assets in base currency)

profit = current_bankroll - total_deposits + total_withdrawals
```

**Interpretation:**
- Positive: Player is ahead
- Negative: Player is down
- Zero: Break-even

---

## 6. Security Implementation

### 6.1 Authentication Security

**Password Requirements**
- Minimum 8 characters
- Must contain uppercase, lowercase, digit, and special character
- Hashed with Argon2 (time_cost=2, memory_cost=512, parallelism=2)

**Session Management**
- HTTPOnly cookies
- Secure flag in production
- SameSite=Lax
- Session timeout: 30 days (configurable)

**OAuth Security**
- State parameter verification
- Nonce validation
- Token encryption at rest
- Provider email verification required

### 6.2 CSRF Protection

- All forms include CSRF token
- Token validation on POST/PUT/DELETE requests
- Exemptions: OAuth callback endpoints (validated via state parameter)

### 6.3 SQL Injection Prevention

- All database queries use SQLAlchemy ORM
- Parameterized queries enforced
- No raw SQL with user input
- Query parameter binding for all dynamic values

### 6.4 XSS Prevention

- Jinja2 auto-escaping enabled globally
- `|safe` filter prohibited without explicit sanitization
- User-generated content (articles) sanitized with Bleach library
- Allowed HTML tags: p, br, strong, em, h1-h6, ul, ol, li, a, code, pre

### 6.5 Rate Limiting

**Endpoints with Limits**
- Login: 5 attempts per 15 minutes per IP
- Registration: 3 attempts per hour per IP
- Password reset: 3 attempts per hour per email
- API endpoints: 100 requests per minute per user

### 6.6 Data Protection

**Sensitive Data Handling**
- Environment variables for secrets (.env file)
- .env excluded from version control (.gitignore)
- Production credentials never in development
- Database backups encrypted at rest

**User Data Privacy**
- Email addresses hashed for lookup indexes
- No plaintext passwords stored
- OAuth tokens encrypted with app secret key
- User data deletion cascade (GDPR compliance ready)

### 6.7 Headers & Hardening

```python
# Security headers set in __init__.py
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## 7. Database Migration Workflow

### 7.1 Development Workflow

```bash
# 1. Make model changes in models.py
# 2. Generate migration script
flask db migrate -m "Add user_streak_tracking"

# 3. Review generated script in migrations/versions/
# 4. Apply migration to local database
flask db upgrade

# 5. Test application thoroughly
flask run

# 6. Commit migration script with code
git add migrations/versions/*.py
git commit -m "Add user streak tracking feature"
git push
```

### 7.2 Production Deployment

```bash
# On PythonAnywhere Bash console
cd ~/total_bankroll
git pull

# Activate virtual environment
workon bankroll_venv
export FLASK_APP="src/total_bankroll"

# Apply migrations
flask db upgrade

# Reload web app (via Web tab dashboard)
# Click the "Reload" button
```

### 7.3 Migration Best Practices

**Do:**
- Test migrations on local database first
- Include descriptive messages
- Review auto-generated scripts for accuracy
- Create data migrations for complex changes
- Backup production database before applying

**Don't:**
- Edit already-applied migration scripts
- Skip migration steps (always use `flask db migrate`)
- Manually modify schema in production
- Mix schema and data changes in same migration (unless necessary)

---

## 8. Testing Strategy

### 8.1 Test Structure

```
tests/
├── unit/                  # Unit tests for individual functions
│   ├── test_models.py
│   ├── test_recommendations.py
│   └── test_currency.py
├── integration/           # Integration tests for routes
│   ├── test_auth_flow.py
│   ├── test_bankroll_crud.py
│   └── test_tools.py
└── fixtures/              # Test data and fixtures
    └── conftest.py
```

### 8.2 Test Coverage Goals

- **Models:** 90%+ coverage
- **Business Logic:** 95%+ coverage (recommendations, currency, calculations)
- **Routes:** 80%+ coverage (happy paths + error handling)
- **Utils:** 85%+ coverage

### 8.3 CI/CD Pipeline

**GitHub Actions Workflow (`.github/workflows/python-ci.yml`)**
```yaml
name: Python CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Lint with flake8
        run: flake8 src/
      - name: Run tests
        run: pytest tests/ --cov=src/total_bankroll
```

### 8.4 Manual Testing Checklist

**Pre-Deployment**
- [ ] Registration and email confirmation
- [ ] Login with email/password
- [ ] OAuth login (Google, Facebook)
- [ ] Add/edit/delete site
- [ ] Add deposit and withdrawal
- [ ] View charts and dashboard totals
- [ ] Use all poker tools
- [ ] Read article and check progress tracking
- [ ] Create goal and verify display
- [ ] Change user settings
- [ ] Test on mobile device

---

## 9. Performance Considerations

### 9.1 Database Optimization

**Indexes**
- Primary keys on all tables
- Foreign key indexes for relationships
- Composite index on `(user_id, recorded_at)` for history tables
- Unique index on `users.email` and `users.fs_uniquifier`

**Query Optimization**
- Lazy loading for relationships (`lazy='dynamic'`)
- Eager loading for frequently accessed relationships (`.joinedload()`)
- Pagination for large result sets (articles, history)
- Database-level aggregations for totals

### 9.2 Caching Strategy

**Candidate Data for Caching**
- Currency exchange rates (24-hour TTL)
- Article listings (invalidate on publish/edit)
- Achievement definitions (static data)
- Cash stakes table (static data)

**Implementation** (Future)
- Flask-Caching with Redis backend
- Cache key strategy: `f"cache:{resource}:{user_id}:{param}"`

### 9.3 Frontend Optimization

**Asset Management**
- Vite for bundling and minification
- CSS/JS fingerprinting for cache busting
- Lazy loading for chart libraries
- Image optimization (WebP format, compression)

**Progressive Enhancement**
- Core functionality works without JavaScript
- Charts and dynamic features load asynchronously
- Mobile-first responsive design

---

## 10. Deployment & Operations

### 10.1 Environment Variables

**Required Variables (`.env`)**
```bash
# Environment
FLASK_ENV=development|production

# Security
SECRET_KEY=<random-string>
SECURITY_PASSWORD_SALT=<random-string>

# Database (Development)
DEV_DB_HOST=localhost
DEV_DB_NAME=bankroll
DEV_DB_USER=root
DEV_DB_PASS=<password>

# Database (Production)
DB_HOST_PROD=<pythonanywhere-mysql-host>
DB_NAME_PROD=pythonpydev$bankroll
DB_USER_PROD=pythonpydev
DB_PASS_PROD=<password>

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=<email>
MAIL_PASSWORD=<app-password>
MAIL_DEFAULT_SENDER=<email>

# OAuth
GOOGLE_CLIENT_ID=<google-oauth-client-id>
GOOGLE_CLIENT_SECRET=<google-oauth-secret>
FACEBOOK_CLIENT_ID=<facebook-app-id>
FACEBOOK_CLIENT_SECRET=<facebook-app-secret>

# External APIs
EXCHANGE_RATE_API_KEY=<exchangerate-api-key>
```

### 10.2 Production Deployment Process

1. **Code Changes**
   - Develop on local environment
   - Test thoroughly with `flask run`
   - Commit to Git

2. **Migration Preparation**
   - If models changed: `flask db migrate -m "message"`
   - Review generated migration script
   - Apply locally: `flask db upgrade`
   - Test application with new schema

3. **Push to Repository**
   ```bash
   git add .
   git commit -m "Descriptive message"
   git push origin main
   ```

4. **Deploy to PythonAnywhere**
   ```bash
   # SSH or Bash console
   cd ~/total_bankroll
   git pull
   workon bankroll_venv
   export FLASK_APP="src/total_bankroll"
   flask db upgrade
   # Reload via Web tab
   ```

5. **Verification**
   - Check error logs (`/var/log/`)
   - Test critical user flows
   - Monitor for errors in first hour

### 10.3 Monitoring & Logging

**Application Logging**
```python
# Configured in __init__.py
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Log Levels**
- ERROR: Application errors, exceptions
- WARNING: Deprecations, recoverable issues
- INFO: User actions, business events
- DEBUG: Detailed diagnostic information (dev only)

**Monitoring Checklist**
- Daily error log review
- Weekly database backup verification
- Monthly dependency vulnerability scan (`pip-audit`)
- Quarterly performance baseline comparison

### 10.4 Backup Strategy

**Database Backups**
- **Frequency:** Daily automated backups (PythonAnywhere)
- **Retention:** 30 days rolling
- **Manual Backup Before:**
  - Major migrations
  - Production deployments
  - Bulk data operations

**Backup Command (Manual)**
```bash
mysqldump -u pythonpydev -p pythonpydev$bankroll > backup_$(date +%Y%m%d).sql
```

**Restoration Process**
```bash
mysql -u pythonpydev -p pythonpydev$bankroll < backup_YYYYMMDD.sql
```

---

## 11. Future Enhancements

### 11.1 Planned Features (Prioritized)

**High Priority**
1. **Session Tracking** - Granular game session logging (date, duration, stakes, location, P&L)
2. **Advanced Analytics** - Profit by game type, hourly rate tracking, day-of-week analysis
3. **Goal Enhancements** - Progress bars, notifications on milestones, social sharing
4. **Mobile App** - Native iOS/Android app with offline support

**Medium Priority**
5. **Hand History Reviewer** - Parse and visualize hand histories with annotation
6. **ICM Calculator** - Tournament deal calculator with chip utility curves
7. **Live Session Mode** - Real-time tracking with timer and quick-entry interface
8. **Community Features** - Forums, hand discussion threads, user profiles

**Low Priority**
9. **API for Third-Party Apps** - RESTful API with OAuth2 authentication
10. **Advanced Charting** - Customizable multi-axis charts, export to Excel
11. **Poker Room Integration** - Direct API connections to poker sites (if available)

### 11.2 Technical Debt

**Refactoring Needs**
- Consolidate route modules (currently split between `frontend/` and `routes/`)
- Extract business logic from routes into service layer
- Implement repository pattern for database access
- Add comprehensive docstrings to all modules

**Infrastructure Improvements**
- Migrate to PostgreSQL for better JSON support (article metadata)
- Implement Redis caching layer
- Add Celery for background tasks (email sending, currency updates)
- Set up staging environment for pre-production testing

---

## 12. Compliance & Legal

### 12.1 Data Privacy (GDPR Ready)

**User Rights**
- Right to access: Export all user data via settings page
- Right to deletion: Cascade delete on account closure
- Right to rectification: Edit profile and data anytime
- Right to portability: JSON export of user data

**Data Retention**
- Active accounts: Indefinite
- Inactive accounts: 2 years before archival prompt
- Deleted accounts: 30-day soft delete before permanent removal

### 12.2 Legal Pages

**Required Pages** (Implemented in `legal_bp`)
- Privacy Policy (`/legal/privacy`)
- Terms of Service (`/legal/terms`)
- Cookie Policy (included in privacy policy)

**Disclaimers**
- Poker is gambling; users should play responsibly
- Application provides tools, not financial advice
- Exchange rates are estimates; verify with official sources

---

## 13. Developer Guidelines

### 13.1 Code Style

**Python**
- PEP 8 compliance (enforced by flake8)
- Line length: 100 characters
- Imports: Standard library, third-party, local (grouped)
- Type hints encouraged for public functions

**JavaScript**
- ES6+ syntax
- 2-space indentation
- Single quotes for strings
- Semicolons required

**HTML/Jinja2**
- 2-space indentation
- Semantic HTML5 elements
- Bootstrap utility classes preferred over custom CSS
- Template inheritance for consistency

### 13.2 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** feat, fix, docs, style, refactor, test, chore

**Example:**
```
feat(recommendations): Add move-down threshold for cash games

Implement stop-loss calculation that tells users the minimum
bankroll they should maintain for their current stake before
dropping down to protect their roll.

Closes #42
```

### 13.3 Pull Request Process

1. Create feature branch from `main`
2. Make changes with atomic commits
3. Write/update tests for new functionality
4. Run full test suite locally (`pytest`)
5. Update documentation if API changes
6. Submit PR with description of changes
7. Address code review feedback
8. Squash commits if requested
9. Merge after approval and CI pass

---

## 14. Appendices

### 14.1 Key Dependencies

**Python (requirements.txt)**
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-Security-Too==5.3.3
Flask-Dance==7.0.0
Flask-Mail==0.9.1
Flask-Limiter==3.5.0
Flask-WTF==1.2.1
SQLAlchemy==2.0.23
PyMySQL==1.1.0
python-dotenv==1.0.0
argon2-cffi==23.1.0
bleach==6.1.0
markdown==3.5.1
```

**Node.js (package.json)**
```json
{
  "devDependencies": {
    "vite": "^7.1.12"
  }
}
```

### 14.2 Database Connection Strings

**Development:**
```
mysql+pymysql://root:<password>@localhost/bankroll
```

**Production:**
```
mysql+pymysql://pythonpydev:<password>@pythonpydev.mysql.pythonanywhere-services.com/pythonpydev$bankroll
```

### 14.3 Useful Flask CLI Commands

```bash
# Database
flask db migrate -m "message"       # Generate migration
flask db upgrade                    # Apply migrations
flask db downgrade                  # Rollback migration
flask db current                    # Show current revision
flask db history                    # Show migration history

# Custom Commands (commands.py)
flask seed-articles                 # Populate article database
flask update-currency-rates         # Fetch latest exchange rates
flask create-admin                  # Create admin user (if implemented)
```

### 14.4 Contact & Support

**Development Team:** pythonpydev  
**Repository:** https://github.com/pythonpydev/total_bankroll  
**Production URL:** https://stakeeasy.net  
**Support Email:** support@stakeeasy.net (configured in MAIL_DEFAULT_SENDER)

---

## 15. Glossary

| Term | Definition |
|------|------------|
| **Bankroll** | Total poker funds across all sites and assets |
| **Buy-in Multiple** | Number of buy-ins recommended for a given stake (e.g., 100 for tournaments) |
| **SPR** | Stack-to-Pot Ratio; stack size divided by pot size |
| **ICM** | Independent Chip Model; tournament equity calculation |
| **PLO** | Pot Limit Omaha; poker variant (4-card hands) |
| **Equity** | Win probability of a hand vs. opponent range |
| **Variance** | Statistical spread of results around expected value |
| **Stop-Loss** | Minimum bankroll threshold before dropping stakes |
| **Shot-Taking** | Playing above recommended stakes (calculated risk) |
| **Rake** | House fee taken from poker pots |

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-05 | AI Assistant | Initial specification based on GEMINI.md and constitution |

**Approval**

This specification reflects the current state of StakeEasy.net (total_bankroll) as of November 2025. It should be reviewed and updated quarterly or whenever major features are added.

---

*End of Specification*
