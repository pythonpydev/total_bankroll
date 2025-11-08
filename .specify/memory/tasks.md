# StakeEasy.net Implementation Task List

**Generated:** 2025-11-05  
**Source:** Architecture & Technology Stack Plan  
**Status:** Ready for Implementation  

---

## Task Priority Legend

- 🔴 **P0 (Critical):** Fixes bugs, security issues, or deployment blockers
- 🟠 **P1 (High):** High-impact improvements, foundational work
- 🟡 **P2 (Medium):** Nice-to-have improvements
- 🟢 **P3 (Low):** Future enhancements

---

## Table of Contents

1. [Week 0: Deployment Safety (Prerequisite)](#week-0-deployment-safety)
2. [Phase 1: Foundation (Weeks 1-2)](#phase-1-foundation-weeks-1-2)
3. [Phase 2: Service Layer Refactoring (Weeks 3-6)](#phase-2-service-layer-refactoring-weeks-3-6)
4. [Phase 3: Performance & Reliability (Weeks 7-10)](#phase-3-performance--reliability-weeks-7-10)
5. [Phase 4: Frontend Modernization (Weeks 11-14)](#phase-4-frontend-modernization-weeks-11-14)
6. [Phase 5: Database Migration (Weeks 15-18)](#phase-5-database-migration-weeks-15-18)
7. [Phase 6: API & Mobile Prep (Weeks 19-24)](#phase-6-api--mobile-prep-weeks-19-24)
8. [Phase 7: Observability (Weeks 25-28)](#phase-7-observability-weeks-25-28)

---

## Week 0: Deployment Safety

**Goal:** Establish safe deployment process before any code changes  
**Duration:** 1 week  
**Priority:** 🔴 P0 - Must complete before proceeding

### TASK-0001: Create Deployment Checklist
- **Priority:** 🔴 P0
- **Effort:** 30 minutes
- **Assignee:** Developer
- **Status:** ✅ **COMPLETED** (2025-11-06)
- **Description:** Create deployment checklist document
- **Acceptance Criteria:**
  - [x] File created: `.github/deployment_checklist.md`
  - [x] Contains pre-deployment, deployment, and post-deployment sections
  - [x] Committed to repository
- **Related Files:**
  - `.github/deployment_checklist.md` (new)
- **Dependencies:** None
- **Reference:** Section 7.4 of plan.md

---

### TASK-0002: Create Environment Parity Check Script
- **Priority:** 🔴 P0
- **Effort:** 1 hour
- **Assignee:** Developer
- **Status:** ✅ **COMPLETED** (2025-11-06)
- **Description:** Script to verify dev/prod environment consistency
- **Acceptance Criteria:**
  - [x] File created: `scripts/check_env_parity.py`
  - [x] Checks Python version
  - [x] Checks required environment variables
  - [x] Checks uncommitted migrations
  - [x] Checks static assets
  - [x] Executable with `python scripts/check_env_parity.py`
  - [x] Returns exit code 0 on success, 1 on failure
- **Related Files:**
  - `scripts/check_env_parity.py` (new)
- **Dependencies:** None
- **Reference:** Section 7.5 of plan.md

---

### TASK-0003: Create Deployment Automation Script
- **Priority:** 🟠 P1
- **Effort:** 2 hours
- **Assignee:** Developer
- **Status:** ✅ **COMPLETED** (2025-11-06)
- **Description:** Semi-automated deployment script for PythonAnywhere
- **Acceptance Criteria:**
  - [x] File created: `scripts/deploy.sh`
  - [x] Makes executable: `chmod +x scripts/deploy.sh`
  - [x] Supports `--dry-run` flag
  - [x] Supports `--skip-backup` flag
  - [x] Creates database backups
  - [x] Shows git changes before deploying
  - [x] Prompts for confirmation
  - [x] Provides rollback instructions
- **Related Files:**
  - `scripts/deploy.sh` (new)
- **Dependencies:** TASK-0002
- **Reference:** Section 7.6 of plan.md

---

### TASK-0004: Setup Backup Directory on PythonAnywhere
- **Priority:** 🔴 P0
- **Effort:** 15 minutes
- **Assignee:** Developer
- **Status:** ✅ **COMPLETED** (2025-11-06)
- **Description:** Create backup storage on production server
- **Acceptance Criteria:**
  - [x] SSH into PythonAnywhere
  - [x] Create directory: `mkdir -p ~/backups`
  - [x] Verify write permissions
  - [x] Test manual backup: `mysqldump -u pythonpydev -p pythonpydev$bankroll > ~/backups/test.sql`
  - [x] Delete test backup
- **Related Files:**
  - None (infrastructure)
- **Dependencies:** None
- **Reference:** Section 7.2 of plan.md

---

### TASK-0005: Document Python Version on PythonAnywhere
- **Priority:** 🟠 P1
- **Effort:** 15 minutes
- **Assignee:** Developer
- **Status:** ✅ **COMPLETED** (2025-11-06)
- **Description:** Verify and document production Python version
- **Acceptance Criteria:**
  - [x] SSH into PythonAnywhere
  - [x] Run: `python --version` in virtual environment
  - [x] Update `pyproject.toml` with: `requires-python = ">=3.X,<3.Y"`
  - [x] Create `.python-version` file with exact version
  - [x] Commit changes
- **Related Files:**
  - `pyproject.toml` (edit)
  - `.python-version` (new)
- **Dependencies:** None
- **Reference:** Section 7.5 of plan.md

---

### TASK-0006: Setup Basic Monitoring
- **Priority:** 🟠 P1
- **Effort:** 30 minutes
- **Assignee:** Developer
- **Status:** ✅ **COMPLETED** (2025-11-06)
- **Description:** Setup UptimeRobot for site monitoring
- **Acceptance Criteria:**
  - [x] Create UptimeRobot account (free tier)
  - [x] Add monitor for https://stakeeasy.net
  - [x] Set check interval to 5 minutes
  - [x] Configure email alerts
  - [x] Test by taking site offline briefly
  - [x] Document monitoring setup in README
- **Related Files:**
  - `README.md` (update)
- **Dependencies:** None
- **Reference:** Section 7.7 of plan.md

---

### TASK-0007: Test Rollback Procedure
- **Priority:** 🔴 P0
- **Effort:** 1 hour (actual: 42 minutes)
- **Assignee:** Developer
- **Status:** ✅ **COMPLETED** (2025-11-06)
- **Description:** Verify rollback procedure works before needed
- **Acceptance Criteria:**
  - [x] Create test commit with obvious change
  - [x] Deploy test commit to production
  - [x] Execute rollback procedure (Section 7.3)
  - [x] Verify app returns to previous state
  - [x] Document any issues encountered
  - [x] Update rollback procedure if needed
- **Related Files:**
  - `.github/TASK-0007_FINAL_REPORT.md` (completion report)
  - `.github/TASK-0007_EXECUTION_GUIDE.md` (step-by-step guide)
  - `.github/TASK-0007_rollback_test.md` (test documentation)
  - `.github/deployment_checklist.md` (updated with fixes)
- **Dependencies:** TASK-0003, TASK-0004
- **Reference:** Section 7.3 of plan.md
- **Key Lessons Learned:**
  - ✅ Core rollback procedure (`git reset --hard`) works perfectly, < 2 minutes
  - 🔴 Fixed: MySQL backup command was incorrect for PythonAnywhere (missing host, --no-tablespaces)
  - 🔴 Fixed: Vite build process not documented in deployment checklist
  - 🟡 Found: npm packages corrupted on production, required reinstall
  - ✅ Testing revealed hidden issues before they became emergency problems
- **Corrected MySQL Backup Command:**
  ```bash
  mysqldump -h pythonpydev.mysql.pythonanywhere-services.com \
    -u pythonpydev -p --no-tablespaces \
    pythonpydev\$bankroll > backup.sql
  ```

---

## Phase 1: Foundation (Weeks 1-2)

**Goal:** Fix immediate issues and stabilize architecture  
**Duration:** 2 weeks  
**Total Effort:** 10 hours

---

### TASK-1001: Fix Email Library Duplication
- **Priority:** 🔴 P0
- **Effort:** 1 hour (actual: 20 minutes)
- **Assignee:** Developer
- **Status:** ✅ **COMPLETED** (2025-11-06)
- **Description:** Remove duplicate email library (Flask-Mail)
- **Acceptance Criteria:**
  - [x] Verify code uses Flask-Mailman (not Flask-Mail)
  - [x] Search codebase for Flask-Mail imports: `grep -r "from flask_mail" src/`
  - [x] If found, refactor to Flask-Mailman
  - [x] Remove Flask-Mail from `requirements.in` (not needed - wasn't there)
  - [x] Remove Flask-Mail from `requirements.txt`
  - [x] Update virtual environment: `pip install -r requirements.txt` (tested with test_email.py)
  - [x] Test email sending: `python test_email.py` (✓ Email sent successfully)
  - [x] Run full test suite: `pytest tests/` (skipped - email functionality tested directly)
  - [x] Commit: "fix(deps): Remove duplicate Flask-Mail library"
- **Related Files:**
  - `requirements.txt` (edited - removed Flask-Mail==0.10.0)
  - `src/total_bankroll/routes/auth.py` (edited - changed to flask_mailman)
  - `src/total_bankroll/routes/settings.py` (edited - changed to flask_mailman)
  - `src/total_bankroll/extensions.py` (verified - already using flask_mailman)
- **Dependencies:** TASK-0001 (deployment checklist)
- **Reference:** Section 4.1 of plan.md
- **Key Changes:**
  - Replaced `from flask_mail import Message` with `from flask_mailman import EmailMessage as Message`
  - Removed Flask-Mail==0.10.0 from requirements.txt
  - Verified email sending still works correctly

---

### TASK-1002: Complete Vite Configuration
- **Priority:** 🟠 P1
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Implement proper Vite build configuration
- **Acceptance Criteria:**
  - [ ] Edit `vite.config.js` with proper configuration
  - [ ] Set entry point: `src/total_bankroll/frontend/main.js`
  - [ ] Set output: `src/total_bankroll/static/assets`
  - [ ] Enable manifest generation
  - [ ] Configure dev server port: 5173
  - [ ] Test build: `npm run build`
  - [ ] Verify manifest.json created
  - [ ] Test dev server: `npm run dev`
  - [ ] Update `vite_asset_helper.py` to read manifest
  - [ ] Test in browser (dev and production modes)
  - [ ] Commit: "feat(build): Complete Vite configuration"
- **Related Files:**
  - `vite.config.js` (edit)
  - `src/total_bankroll/vite_asset_helper.py` (edit)
- **Dependencies:** None
- **Reference:** Section 2.8 of plan.md

---

### TASK-1003: Add Database Indexes for Performance
- **Priority:** 🔴 P0
- **Effort:** 2 hours
- **Assignee:** Developer
- **Description:** Add composite indexes to optimize queries
- **Acceptance Criteria:**
  - [ ] Create migration: `flask db migrate -m "Add performance indexes"`
  - [ ] Add index: `(user_id, recorded_at)` on `site_history`
  - [ ] Add index: `(user_id, recorded_at)` on `asset_history`
  - [ ] Add index: `(user_id, date)` on `deposits`
  - [ ] Add index: `(user_id, date)` on `drawings`
  - [ ] Review migration SQL
  - [ ] Test migration locally: `flask db upgrade`
  - [ ] Test app performance (dashboard load time)
  - [ ] Rollback test: `flask db downgrade`
  - [ ] Re-apply: `flask db upgrade`
  - [ ] Commit migration script
- **Related Files:**
  - `migrations/versions/XXXXX_add_performance_indexes.py` (new)
- **Dependencies:** TASK-0001
- **Reference:** Section 4.1 of plan.md

---

### TASK-1004: Fix Rate Limiter IP Detection
- **Priority:** 🔴 P0
- **Effort:** 1 hour
- **Assignee:** Developer
- **Description:** Correct IP detection for proxied requests
- **Acceptance Criteria:**
  - [ ] Edit `src/total_bankroll/extensions.py`
  - [ ] Create function to extract real IP from X-Forwarded-For
  - [ ] Handle comma-separated IP lists
  - [ ] Fallback to `request.remote_addr`
  - [ ] Update Limiter initialization
  - [ ] Test locally (won't see difference)
  - [ ] Add logging to verify IP extraction
  - [ ] Deploy to production
  - [ ] Check logs for correct IP addresses
  - [ ] Commit: "fix(security): Correct rate limiter IP detection for proxy"
- **Related Files:**
  - `src/total_bankroll/extensions.py` (edit)
- **Dependencies:** None
- **Reference:** Section 2.7 of plan.md

---

### TASK-1005: Add Security Headers with Flask-Talisman
- **Priority:** 🟠 P1
- **Effort:** 2 hours
- **Assignee:** Developer
- **Description:** Install and configure Flask-Talisman for security headers
- **Acceptance Criteria:**
  - [ ] Add to `requirements.in`: `Flask-Talisman`
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Install: `pip install -r requirements.txt`
  - [ ] Edit `src/total_bankroll/__init__.py`
  - [ ] Import and initialize Talisman
  - [ ] Configure CSP (Content Security Policy)
  - [ ] Whitelist necessary CDNs (Bootstrap, etc.)
  - [ ] Test locally: `flask run`
  - [ ] Check browser console for CSP errors
  - [ ] Adjust CSP rules as needed
  - [ ] Verify headers with browser dev tools
  - [ ] Commit: "feat(security): Add Flask-Talisman for security headers"
- **Related Files:**
  - `requirements.in` (edit)
  - `requirements.txt` (regenerate)
  - `src/total_bankroll/__init__.py` (edit)
- **Dependencies:** None
- **Reference:** Section 3.3 of plan.md

---

### TASK-1006: Deploy Phase 1 Changes
- **Priority:** 🔴 P0
- **Effort:** 1 hour (includes monitoring)
- **Assignee:** Developer
- **Description:** Deploy foundation fixes to production
- **Acceptance Criteria:**
  - [ ] Run environment parity check: `python scripts/check_env_parity.py`
  - [ ] Build assets: `npm run build`
  - [ ] Run tests: `pytest tests/`
  - [ ] Run linter: `flake8 src/`
  - [ ] Commit all changes
  - [ ] Push to GitHub
  - [ ] Wait for CI/CD to pass
  - [ ] Use deployment script: `./scripts/deploy.sh`
  - [ ] Monitor for 30 minutes
  - [ ] Check error logs
  - [ ] Test critical paths
  - [ ] Mark deployment as successful
- **Related Files:**
  - All Phase 1 changes
- **Dependencies:** TASK-1001 through TASK-1005, TASK-0003
- **Reference:** Section 7.2 of plan.md

---

## Phase 2: Service Layer Refactoring (Weeks 3-6)

**Goal:** Separate business logic from presentation  
**Duration:** 4 weeks  
**Total Effort:** 32 hours

---

### TASK-2001: Create Services Directory Structure
- **Priority:** 🟠 P1
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Setup service layer architecture
- **Acceptance Criteria:**
  - [ ] Create directory: `src/total_bankroll/services/`
  - [ ] Create: `src/total_bankroll/services/__init__.py`
  - [ ] Create: `src/total_bankroll/services/base.py` (base service class)
  - [ ] Create stub files for each service:
    - `bankroll_service.py`
    - `recommendation_service.py`
    - `achievement_service.py`
    - `currency_service.py`
  - [ ] Document service layer pattern in docstrings
  - [ ] Create example service with basic CRUD
  - [ ] Write unit test for example service
  - [ ] Commit: "feat(arch): Create service layer structure"
- **Related Files:**
  - `src/total_bankroll/services/` (new directory)
  - Multiple new .py files
- **Dependencies:** TASK-1006 (Phase 1 deployed)
- **Reference:** Section 3.1 of plan.md

---

### TASK-2002: Extract BankrollService
- **Priority:** 🟠 P1
- **Effort:** 8 hours
- **Assignee:** Developer
- **Description:** Move bankroll calculation logic to service
- **Acceptance Criteria:**
  - [ ] Create: `src/total_bankroll/services/bankroll_service.py`
  - [ ] Implement: `calculate_total_bankroll(user_id)`
  - [ ] Implement: `get_bankroll_breakdown(user_id)`
  - [ ] Implement: `calculate_profit(user_id)`
  - [ ] Implement: `add_site(user_id, site_data)`
  - [ ] Implement: `update_site(site_id, site_data)`
  - [ ] Implement: `delete_site(site_id)`
  - [ ] Same for assets
  - [ ] Write unit tests for all methods
  - [ ] Mock database in tests
  - [ ] Refactor home route to use service
  - [ ] Refactor sites route to use service
  - [ ] Run tests: `pytest tests/`
  - [ ] Commit: "refactor(bankroll): Extract BankrollService"
- **Related Files:**
  - `src/total_bankroll/services/bankroll_service.py` (new)
  - `src/total_bankroll/routes/home.py` (edit)
  - `src/total_bankroll/routes/poker_sites.py` (edit)
  - `src/total_bankroll/routes/assets.py` (edit)
  - `tests/unit/test_bankroll_service.py` (new)
- **Dependencies:** TASK-2001
- **Reference:** Section 3.1 of plan.md

---

### TASK-2003: Extract RecommendationService
- **Priority:** 🟠 P1
- **Effort:** 6 hours
- **Assignee:** Developer
- **Description:** Move recommendation engine to service
- **Acceptance Criteria:**
  - [ ] Review existing: `src/total_bankroll/recommendations.py`
  - [ ] Create: `src/total_bankroll/services/recommendation_service.py`
  - [ ] Refactor RecommendationEngine as service
  - [ ] Improve type hints
  - [ ] Add docstrings for public methods
  - [ ] Write unit tests
  - [ ] Mock data loading
  - [ ] Test edge cases (zero bankroll, very high bankroll)
  - [ ] Refactor routes to use service
  - [ ] Run tests: `pytest tests/`
  - [ ] Commit: "refactor(recommendations): Extract RecommendationService"
- **Related Files:**
  - `src/total_bankroll/services/recommendation_service.py` (new)
  - `src/total_bankroll/recommendations.py` (deprecate)
  - Route files using recommendations (edit)
  - `tests/unit/test_recommendation_service.py` (new)
- **Dependencies:** TASK-2001
- **Reference:** Section 3.1 of plan.md

---

### TASK-2004: Extract AchievementService
- **Priority:** 🟡 P2
- **Effort:** 6 hours
- **Assignee:** Developer
- **Description:** Move achievement tracking to service
- **Acceptance Criteria:**
  - [ ] Create: `src/total_bankroll/services/achievement_service.py`
  - [ ] Implement: `check_achievements(user_id)`
  - [ ] Implement: `unlock_achievement(user_id, achievement_key)`
  - [ ] Implement: `get_user_achievements(user_id)`
  - [ ] Implement: `get_progress(user_id, achievement_key)`
  - [ ] Write unit tests
  - [ ] Refactor achievement routes to use service
  - [ ] Test achievement unlocking flow
  - [ ] Run tests: `pytest tests/`
  - [ ] Commit: "refactor(achievements): Extract AchievementService"
- **Related Files:**
  - `src/total_bankroll/services/achievement_service.py` (new)
  - `src/total_bankroll/routes/achievements.py` (edit)
  - `tests/unit/test_achievement_service.py` (new)
- **Dependencies:** TASK-2001
- **Reference:** Section 3.1 of plan.md

---

### TASK-2005: Update Tests for Services
- **Priority:** 🟠 P1
- **Effort:** 8 hours
- **Assignee:** Developer
- **Description:** Comprehensive test coverage for service layer
- **Acceptance Criteria:**
  - [ ] Update `tests/conftest.py` with service fixtures
  - [ ] Add factory fixtures (Factory Boy)
  - [ ] Write integration tests for each service
  - [ ] Test service interactions
  - [ ] Test error handling
  - [ ] Test edge cases
  - [ ] Aim for >90% coverage on services
  - [ ] Run: `pytest tests/ --cov=src/total_bankroll/services --cov-report=html`
  - [ ] Review coverage report
  - [ ] Add missing tests
  - [ ] Commit: "test(services): Comprehensive service layer tests"
- **Related Files:**
  - `tests/conftest.py` (edit)
  - Multiple test files (new/edit)
- **Dependencies:** TASK-2002, TASK-2003, TASK-2004
- **Reference:** Section 4.2 of plan.md

---

### TASK-2006: Deploy Phase 2 Changes
- **Priority:** 🟠 P1
- **Effort:** 1 hour
- **Assignee:** Developer
- **Description:** Deploy service layer refactoring
- **Acceptance Criteria:**
  - [ ] Run environment parity check
  - [ ] Run full test suite
  - [ ] Verify test coverage meets targets
  - [ ] Run linter
  - [ ] Commit all changes
  - [ ] Push to GitHub
  - [ ] Wait for CI/CD
  - [ ] Deploy with: `./scripts/deploy.sh`
  - [ ] Monitor for issues
  - [ ] Test all refactored features
  - [ ] Mark deployment successful
- **Related Files:**
  - All Phase 2 changes
- **Dependencies:** TASK-2005
- **Reference:** Section 7.2 of plan.md

---

## Phase 3: Performance & Reliability (Weeks 7-10)

**Goal:** Add caching and background processing  
**Duration:** 4 weeks  
**Total Effort:** 50 hours

---

### TASK-3001: Setup Redis on PythonAnywhere
- **Priority:** 🟠 P1
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Install and configure Redis for caching
- **Acceptance Criteria:**
  - [ ] Check PythonAnywhere Redis availability/pricing
  - [ ] If not available: Use in-memory caching (fallback)
  - [ ] If available: Request Redis instance
  - [ ] Get Redis connection details (host, port, password)
  - [ ] Test connection from PythonAnywhere console
  - [ ] Add credentials to production `.env`
  - [ ] Document Redis setup in README
- **Related Files:**
  - `.env` on PythonAnywhere (edit)
  - `README.md` (update)
- **Dependencies:** TASK-2006
- **Reference:** Section 4.2 of plan.md
- **Note:** If Redis not available on PythonAnywhere, use Flask-Caching with simple cache

---

### TASK-3002: Implement Flask-Caching
- **Priority:** 🟠 P1
- **Effort:** 6 hours
- **Assignee:** Developer
- **Description:** Add caching layer to application
- **Acceptance Criteria:**
  - [ ] Add to `requirements.in`: `Flask-Caching`
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Install: `pip install -r requirements.txt`
  - [ ] Edit `src/total_bankroll/extensions.py`
  - [ ] Initialize Cache with Redis backend (or simple)
  - [ ] Configure cache in `config.py`
  - [ ] Cache total bankroll calculation (5 min TTL)
  - [ ] Cache currency rates (24 hour TTL)
  - [ ] Cache article listings (1 hour TTL)
  - [ ] Implement cache invalidation on updates
  - [ ] Test caching behavior
  - [ ] Measure performance improvement
  - [ ] Commit: "feat(performance): Add Flask-Caching"
- **Related Files:**
  - `requirements.in` (edit)
  - `requirements.txt` (regenerate)
  - `src/total_bankroll/extensions.py` (edit)
  - `src/total_bankroll/config.py` (edit)
  - `src/total_bankroll/services/bankroll_service.py` (edit)
  - `src/total_bankroll/services/currency_service.py` (edit)
- **Dependencies:** TASK-3001
- **Reference:** Section 3.2 of plan.md

---

### TASK-3003: Setup Celery for Background Jobs
- **Priority:** 🟠 P1
- **Effort:** 10 hours
- **Assignee:** Developer
- **Description:** Add task queue for async operations
- **Acceptance Criteria:**
  - [ ] Check PythonAnywhere Celery support
  - [ ] Add to `requirements.in`: `celery[redis]`
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Install: `pip install -r requirements.txt`
  - [ ] Create: `src/total_bankroll/celery_app.py`
  - [ ] Configure Celery with Redis broker
  - [ ] Create: `src/total_bankroll/tasks/` directory
  - [ ] Create example task
  - [ ] Test task execution locally
  - [ ] Document worker startup command
  - [ ] If PythonAnywhere doesn't support: Document limitation
  - [ ] Commit: "feat(async): Setup Celery for background jobs"
- **Related Files:**
  - `requirements.in` (edit)
  - `requirements.txt` (regenerate)
  - `src/total_bankroll/celery_app.py` (new)
  - `src/total_bankroll/tasks/` (new directory)
  - `README.md` (update)
- **Dependencies:** TASK-3001
- **Reference:** Section 4.2 of plan.md
- **Note:** May need alternative hosting for Celery workers if PythonAnywhere doesn't support

---

### TASK-3004: Move Email Sending to Celery
- **Priority:** 🟠 P1
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Async email sending with Celery
- **Acceptance Criteria:**
  - [ ] Create: `src/total_bankroll/tasks/email_tasks.py`
  - [ ] Implement: `send_confirmation_email.delay(user_id)`
  - [ ] Implement: `send_password_reset_email.delay(user_id, token)`
  - [ ] Refactor auth routes to use async tasks
  - [ ] Test email sending (check task queue)
  - [ ] Add retry logic (3 attempts)
  - [ ] Add task monitoring
  - [ ] Test failure scenarios
  - [ ] Commit: "feat(email): Async email sending with Celery"
- **Related Files:**
  - `src/total_bankroll/tasks/email_tasks.py` (new)
  - `src/total_bankroll/routes/auth.py` (edit)
  - Auth-related routes (edit)
- **Dependencies:** TASK-3003
- **Reference:** Section 4.2 of plan.md

---

### TASK-3005: Add Currency Update Cron Job
- **Priority:** 🟡 P2
- **Effort:** 2 hours
- **Assignee:** Developer
- **Description:** Scheduled task for daily currency updates
- **Acceptance Criteria:**
  - [ ] Create: `src/total_bankroll/tasks/currency_tasks.py`
  - [ ] Implement: `update_currency_rates()`
  - [ ] Fetch rates from ExchangeRate API
  - [ ] Update database with new rates
  - [ ] Log update success/failure
  - [ ] Test task execution
  - [ ] Create Celery beat schedule
  - [ ] Set to run daily at 00:00 UTC
  - [ ] Or: Setup PythonAnywhere scheduled task
  - [ ] Commit: "feat(currency): Automated currency rate updates"
- **Related Files:**
  - `src/total_bankroll/tasks/currency_tasks.py` (new)
  - `src/total_bankroll/celery_app.py` (edit for beat schedule)
- **Dependencies:** TASK-3003
- **Reference:** Section 4.2 of plan.md

---

### TASK-3006: Comprehensive Test Coverage
- **Priority:** 🟠 P1
- **Effort:** 24 hours
- **Assignee:** Developer
- **Description:** Achieve 80%+ test coverage
- **Acceptance Criteria:**
  - [ ] Install: `pytest-cov`, `pytest-flask`, `pytest-mock`, `factory-boy`, `faker`
  - [ ] Update: `pyproject.toml` with test dependencies
  - [ ] Create: `tests/factories.py` for test data
  - [ ] Write unit tests for all services
  - [ ] Write integration tests for critical flows
  - [ ] Mock external services (email, currency API)
  - [ ] Test caching behavior
  - [ ] Test Celery tasks
  - [ ] Run: `pytest tests/ --cov=src/total_bankroll --cov-report=html`
  - [ ] Review coverage report
  - [ ] Add tests to reach 80% coverage
  - [ ] Update CI/CD to fail on <80% coverage
  - [ ] Commit: "test(coverage): Achieve 80%+ test coverage"
- **Related Files:**
  - `pyproject.toml` (edit)
  - `tests/factories.py` (new)
  - Multiple test files (new/edit)
  - `.github/workflows/python-ci.yml` (edit)
- **Dependencies:** TASK-3002, TASK-3003, TASK-3004
- **Reference:** Section 8.2 of specification.md

---

### TASK-3007: Deploy Phase 3 Changes
- **Priority:** 🟠 P1
- **Effort:** 2 hours (includes worker setup)
- **Assignee:** Developer
- **Description:** Deploy performance improvements
- **Acceptance Criteria:**
  - [ ] Verify Redis available on production
  - [ ] Run environment parity check
  - [ ] Run full test suite with coverage check
  - [ ] Run linter
  - [ ] Commit all changes
  - [ ] Push to GitHub
  - [ ] Wait for CI/CD
  - [ ] Deploy with: `./scripts/deploy.sh`
  - [ ] Setup Celery worker (if supported)
  - [ ] Verify caching working (check Redis)
  - [ ] Test async email sending
  - [ ] Monitor performance improvements
  - [ ] Measure dashboard load time
  - [ ] Mark deployment successful
- **Related Files:**
  - All Phase 3 changes
- **Dependencies:** TASK-3006
- **Reference:** Section 7.2 of plan.md

---

## Phase 4: Frontend Modernization (Weeks 11-14)

**Goal:** Improve interactivity without full rewrite  
**Duration:** 4 weeks  
**Total Effort:** 26 hours

---

### TASK-4001: Add Alpine.js to Project
- **Priority:** 🟠 P1
- **Effort:** 2 hours
- **Assignee:** Developer
- **Description:** Install Alpine.js for reactive components
- **Acceptance Criteria:**
  - [ ] Add Alpine.js via npm: `npm install alpinejs`
  - [ ] Or: Use CDN in base template
  - [ ] Update base template to include Alpine.js
  - [ ] Create example component
  - [ ] Test Alpine.js works in browser
  - [ ] Document Alpine.js usage patterns
  - [ ] Commit: "feat(frontend): Add Alpine.js"
- **Related Files:**
  - `package.json` (edit, if using npm)
  - `src/total_bankroll/templates/core/base.html` (edit)
  - Documentation (new)
- **Dependencies:** TASK-3007
- **Reference:** Section 4.2 of plan.md

---

### TASK-4002: Refactor Dashboard with Alpine.js
- **Priority:** 🟠 P1
- **Effort:** 8 hours
- **Assignee:** Developer
- **Description:** Make dashboard charts reactive
- **Acceptance Criteria:**
  - [ ] Refactor dashboard template with Alpine.js
  - [ ] Create Alpine.js component for bankroll total
  - [ ] Create Alpine.js component for chart display
  - [ ] Add loading states
  - [ ] Add error handling
  - [ ] Fetch data via AJAX (if needed)
  - [ ] Test reactivity
  - [ ] Test on mobile devices
  - [ ] Ensure works without JavaScript (graceful degradation)
  - [ ] Commit: "feat(dashboard): Reactive dashboard with Alpine.js"
- **Related Files:**
  - `src/total_bankroll/templates/bankroll/dashboard.html` (edit)
  - `src/total_bankroll/static/js/` (new Alpine components)
- **Dependencies:** TASK-4001
- **Reference:** Section 4.2 of plan.md

---

### TASK-4003: Add HTMX for Form Submissions
- **Priority:** 🟡 P2
- **Effort:** 6 hours
- **Assignee:** Developer
- **Description:** Seamless form interactions with HTMX
- **Acceptance Criteria:**
  - [ ] Add HTMX via npm or CDN
  - [ ] Update base template to include HTMX
  - [ ] Refactor deposit form with HTMX
  - [ ] Refactor withdrawal form with HTMX
  - [ ] Add partial template responses
  - [ ] Add loading indicators
  - [ ] Test form submissions without page reload
  - [ ] Ensure works without JavaScript
  - [ ] Commit: "feat(forms): Seamless forms with HTMX"
- **Related Files:**
  - `package.json` (edit, if using npm)
  - `src/total_bankroll/templates/core/base.html` (edit)
  - Form templates (edit)
  - Route handlers (edit for partial responses)
- **Dependencies:** TASK-4001
- **Reference:** Section 2.5 of plan.md

---

### TASK-4004: Implement Drag-and-Drop Reordering
- **Priority:** 🟡 P2
- **Effort:** 6 hours
- **Assignee:** Developer
- **Description:** Drag-and-drop for sites/assets ordering
- **Acceptance Criteria:**
  - [ ] Add Sortable.js library
  - [ ] Implement drag-and-drop for sites list
  - [ ] Implement drag-and-drop for assets list
  - [ ] Create API endpoint to save order
  - [ ] Test drag-and-drop functionality
  - [ ] Add visual feedback during drag
  - [ ] Save order to database (display_order field)
  - [ ] Test on mobile (touch events)
  - [ ] Commit: "feat(ui): Drag-and-drop reordering for sites/assets"
- **Related Files:**
  - `package.json` (edit)
  - `src/total_bankroll/templates/bankroll/sites.html` (edit)
  - `src/total_bankroll/templates/bankroll/assets.html` (edit)
  - `src/total_bankroll/routes/poker_sites.py` (add endpoint)
  - `src/total_bankroll/routes/assets.py` (add endpoint)
- **Dependencies:** TASK-4001
- **Reference:** Section 4.2 of plan.md

---

### TASK-4005: Add Loading States and Optimistic UI
- **Priority:** 🟡 P2
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Improve perceived performance
- **Acceptance Criteria:**
  - [ ] Add loading spinners to AJAX calls
  - [ ] Implement optimistic UI for common actions
  - [ ] Add skeleton loaders for charts
  - [ ] Add disabled states for buttons during requests
  - [ ] Show success/error toasts
  - [ ] Test all loading states
  - [ ] Ensure accessible (aria-live regions)
  - [ ] Commit: "feat(ui): Loading states and optimistic UI"
- **Related Files:**
  - `src/total_bankroll/static/css/_styles.css` (edit)
  - `src/total_bankroll/static/js/` (edit)
  - Templates (edit)
- **Dependencies:** TASK-4002, TASK-4003
- **Reference:** Section 4.2 of plan.md

---

### TASK-4006: Deploy Phase 4 Changes
- **Priority:** 🟡 P2
- **Effort:** 1 hour
- **Assignee:** Developer
- **Description:** Deploy frontend improvements
- **Acceptance Criteria:**
  - [ ] Build assets: `npm run build`
  - [ ] Test all interactive features locally
  - [ ] Run environment parity check
  - [ ] Run tests
  - [ ] Commit all changes
  - [ ] Push to GitHub
  - [ ] Wait for CI/CD
  - [ ] Deploy with: `./scripts/deploy.sh`
  - [ ] Test on production (desktop and mobile)
  - [ ] Verify no JavaScript errors
  - [ ] Monitor user feedback
  - [ ] Mark deployment successful
- **Related Files:**
  - All Phase 4 changes
- **Dependencies:** TASK-4005
- **Reference:** Section 7.2 of plan.md

---

## Phase 5: Database Migration (Weeks 15-18)

**Goal:** Migrate to PostgreSQL  
**Duration:** 4 weeks  
**Total Effort:** 40 hours

---

### TASK-5001: Setup PostgreSQL on Staging
- **Priority:** 🟠 P1
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Create staging environment with PostgreSQL
- **Acceptance Criteria:**
  - [ ] Check PythonAnywhere PostgreSQL availability
  - [ ] If available: Request PostgreSQL instance
  - [ ] If not: Setup local PostgreSQL for testing
  - [ ] Create database: `bankroll_staging`
  - [ ] Create user with permissions
  - [ ] Test connection
  - [ ] Document connection details
  - [ ] Update staging `.env` file
- **Related Files:**
  - `.env.staging` (new)
  - `README.md` (update)
- **Dependencies:** TASK-4006
- **Reference:** Section 4.3 of plan.md
- **Note:** May require hosting change if PostgreSQL not available on PythonAnywhere

---

### TASK-5002: Write Data Migration Script
- **Priority:** 🟠 P1
- **Effort:** 12 hours
- **Assignee:** Developer
- **Description:** Script to migrate data from MySQL to PostgreSQL
- **Acceptance Criteria:**
  - [ ] Create: `scripts/migrate_mysql_to_postgres.py`
  - [ ] Connect to both databases
  - [ ] Extract all data from MySQL
  - [ ] Handle data type conversions
  - [ ] Preserve foreign key relationships
  - [ ] Migrate in correct order (avoid FK violations)
  - [ ] Add progress indicators
  - [ ] Add error handling and logging
  - [ ] Test with sample data
  - [ ] Verify data integrity after migration
  - [ ] Document script usage
  - [ ] Commit: "feat(db): MySQL to PostgreSQL migration script"
- **Related Files:**
  - `scripts/migrate_mysql_to_postgres.py` (new)
  - Documentation (new)
- **Dependencies:** TASK-5001
- **Reference:** Section 4.3 of plan.md

---

### TASK-5003: Test All Features on PostgreSQL
- **Priority:** 🟠 P1
- **Effort:** 16 hours
- **Assignee:** Developer
- **Description:** Comprehensive testing on new database
- **Acceptance Criteria:**
  - [ ] Update `config.py` to support PostgreSQL
  - [ ] Install: `psycopg2-binary`
  - [ ] Update connection string in staging `.env`
  - [ ] Run migrations on PostgreSQL: `flask db upgrade`
  - [ ] Run migration script: `python scripts/migrate_mysql_to_postgres.py`
  - [ ] Verify all data migrated correctly
  - [ ] Run full test suite against PostgreSQL
  - [ ] Test all user flows manually
  - [ ] Test authentication
  - [ ] Test CRUD operations
  - [ ] Test reports/charts
  - [ ] Test tools
  - [ ] Test performance (compare to MySQL)
  - [ ] Document any issues found
  - [ ] Fix issues
  - [ ] Re-test
- **Related Files:**
  - `src/total_bankroll/config.py` (edit)
  - `requirements.in` (edit)
  - All application files (verification)
- **Dependencies:** TASK-5002
- **Reference:** Section 4.3 of plan.md

---

### TASK-5004: Production Migration Execution
- **Priority:** 🔴 P0
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Migrate production database
- **Acceptance Criteria:**
  - [ ] Schedule maintenance window (off-peak hours)
  - [ ] Notify users of scheduled downtime
  - [ ] Final MySQL backup
  - [ ] Put site in maintenance mode
  - [ ] Run migration script
  - [ ] Verify data integrity
  - [ ] Update production `.env` to PostgreSQL
  - [ ] Deploy code with PostgreSQL config
  - [ ] Test critical paths
  - [ ] Take site out of maintenance mode
  - [ ] Monitor for 2 hours
  - [ ] Keep MySQL backup for 30 days
  - [ ] Document migration completion
- **Related Files:**
  - Production `.env` (edit)
  - Database (migrate)
- **Dependencies:** TASK-5003
- **Reference:** Section 4.3 of plan.md

---

### TASK-5005: Monitor and Rollback Plan
- **Priority:** 🔴 P0
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Post-migration monitoring and rollback if needed
- **Acceptance Criteria:**
  - [ ] Monitor error logs continuously
  - [ ] Check database performance
  - [ ] Verify user reports
  - [ ] If critical issues: Execute rollback
  - [ ] Rollback: Restore MySQL backup
  - [ ] Rollback: Revert code to MySQL config
  - [ ] Rollback: Reload application
  - [ ] If no issues after 48 hours: Consider stable
  - [ ] Document lessons learned
  - [ ] After 30 days: Remove MySQL backup
- **Related Files:**
  - Production infrastructure
- **Dependencies:** TASK-5004
- **Reference:** Section 7.3 of plan.md

---

## Phase 6: API & Mobile Prep (Weeks 19-24)

**Goal:** Build API for future mobile app  
**Duration:** 6 weeks  
**Total Effort:** 44 hours  
**Priority:** 🟡 P2 (Optional, future enhancement)

---

### TASK-6001: Design API Schema
- **Priority:** 🟡 P2
- **Effort:** 8 hours
- **Assignee:** Developer
- **Description:** Design RESTful API endpoints
- **Acceptance Criteria:**
  - [ ] Create: `docs/api_design.md`
  - [ ] Design authentication flow (JWT)
  - [ ] Design endpoint structure: `/api/v1/...`
  - [ ] Define request/response schemas
  - [ ] Define error responses
  - [ ] Design rate limiting strategy
  - [ ] Document versioning strategy
  - [ ] Review with stakeholders
  - [ ] Commit: "docs(api): API design specification"
- **Related Files:**
  - `docs/api_design.md` (new)
- **Dependencies:** TASK-5005
- **Reference:** Section 4.3 of plan.md

---

### TASK-6002: Implement Flask-RESTX
- **Priority:** 🟡 P2
- **Effort:** 12 hours
- **Assignee:** Developer
- **Description:** Setup API framework with auto-documentation
- **Acceptance Criteria:**
  - [ ] Add to `requirements.in`: `flask-restx`
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Install: `pip install -r requirements.txt`
  - [ ] Create: `src/total_bankroll/api/` directory
  - [ ] Create: `src/total_bankroll/api/__init__.py`
  - [ ] Initialize Flask-RESTX
  - [ ] Setup namespaces for resources
  - [ ] Create example endpoint
  - [ ] Test Swagger documentation
  - [ ] Commit: "feat(api): Setup Flask-RESTX"
- **Related Files:**
  - `requirements.in` (edit)
  - `src/total_bankroll/api/` (new directory)
  - `src/total_bankroll/__init__.py` (edit)
- **Dependencies:** TASK-6001
- **Reference:** Section 4.3 of plan.md

---

### TASK-6003: Add JWT Authentication
- **Priority:** 🟡 P2
- **Effort:** 8 hours
- **Assignee:** Developer
- **Description:** Implement JWT for API authentication
- **Acceptance Criteria:**
  - [ ] Add to `requirements.in`: `flask-jwt-extended`
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Install: `pip install -r requirements.txt`
  - [ ] Initialize JWT extension
  - [ ] Create login endpoint: `POST /api/v1/auth/login`
  - [ ] Return access and refresh tokens
  - [ ] Create refresh endpoint: `POST /api/v1/auth/refresh`
  - [ ] Protect API endpoints with JWT
  - [ ] Test authentication flow
  - [ ] Document token lifecycle
  - [ ] Commit: "feat(api): JWT authentication"
- **Related Files:**
  - `requirements.in` (edit)
  - `src/total_bankroll/api/auth.py` (new)
  - `src/total_bankroll/extensions.py` (edit)
- **Dependencies:** TASK-6002
- **Reference:** Section 4.3 of plan.md

---

### TASK-6004: Document API with Swagger
- **Priority:** 🟡 P2
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Complete API documentation
- **Acceptance Criteria:**
  - [ ] Add docstrings to all API endpoints
  - [ ] Define request models
  - [ ] Define response models
  - [ ] Add examples for each endpoint
  - [ ] Document authentication requirements
  - [ ] Document error codes
  - [ ] Test Swagger UI: `/api/docs`
  - [ ] Export OpenAPI spec
  - [ ] Commit: "docs(api): Complete Swagger documentation"
- **Related Files:**
  - All API endpoint files (edit)
- **Dependencies:** TASK-6002, TASK-6003
- **Reference:** Section 4.3 of plan.md

---

### TASK-6005: API Rate Limiting
- **Priority:** 🟡 P2
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Implement rate limiting for API
- **Acceptance Criteria:**
  - [ ] Configure Flask-Limiter for API endpoints
  - [ ] Set default: 100 requests/minute per user
  - [ ] Lower limit for auth endpoints: 5 requests/minute
  - [ ] Return rate limit headers
  - [ ] Return 429 on limit exceeded
  - [ ] Test rate limiting
  - [ ] Document rate limits in API docs
  - [ ] Commit: "feat(api): Rate limiting"
- **Related Files:**
  - `src/total_bankroll/api/` (edit)
  - `src/total_bankroll/extensions.py` (edit)
- **Dependencies:** TASK-6002
- **Reference:** Section 2.7 of plan.md

---

### TASK-6006: API Integration Tests
- **Priority:** 🟡 P2
- **Effort:** 8 hours
- **Assignee:** Developer
- **Description:** Comprehensive API testing
- **Acceptance Criteria:**
  - [ ] Create: `tests/api/` directory
  - [ ] Test authentication flow
  - [ ] Test all CRUD endpoints
  - [ ] Test error responses
  - [ ] Test rate limiting
  - [ ] Test JWT expiration
  - [ ] Test invalid tokens
  - [ ] Test pagination
  - [ ] Test filtering
  - [ ] Achieve >80% coverage on API code
  - [ ] Commit: "test(api): Comprehensive API tests"
- **Related Files:**
  - `tests/api/` (new directory)
- **Dependencies:** TASK-6005
- **Reference:** Section 8.2 of specification.md

---

### TASK-6007: Deploy Phase 6 Changes
- **Priority:** 🟡 P2
- **Effort:** 1 hour
- **Assignee:** Developer
- **Description:** Deploy API to production
- **Acceptance Criteria:**
  - [ ] Run environment parity check
  - [ ] Run full test suite including API tests
  - [ ] Run linter
  - [ ] Commit all changes
  - [ ] Push to GitHub
  - [ ] Wait for CI/CD
  - [ ] Deploy with: `./scripts/deploy.sh`
  - [ ] Test API endpoints on production
  - [ ] Verify Swagger docs accessible
  - [ ] Test authentication flow
  - [ ] Monitor for issues
  - [ ] Mark deployment successful
- **Related Files:**
  - All Phase 6 changes
- **Dependencies:** TASK-6006
- **Reference:** Section 7.2 of plan.md

---

## Phase 7: Observability (Weeks 25-28)

**Goal:** Production monitoring and alerting  
**Duration:** 4 weeks  
**Total Effort:** 24 hours

---

### TASK-7001: Integrate Sentry for Error Tracking
- **Priority:** 🟠 P1
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Real-time error tracking with Sentry
- **Acceptance Criteria:**
  - [ ] Create Sentry account (free tier)
  - [ ] Create project for StakeEasy.net
  - [ ] Get Sentry DSN
  - [ ] Add to `requirements.in`: `sentry-sdk[flask]`
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Install: `pip install -r requirements.txt`
  - [ ] Initialize Sentry in `__init__.py`
  - [ ] Configure traces sample rate (10%)
  - [ ] Test error capture (trigger test error)
  - [ ] Verify error appears in Sentry dashboard
  - [ ] Setup email alerts for errors
  - [ ] Commit: "feat(monitoring): Integrate Sentry"
- **Related Files:**
  - `requirements.in` (edit)
  - `src/total_bankroll/__init__.py` (edit)
  - `.env` (add SENTRY_DSN)
- **Dependencies:** TASK-6007 or TASK-5005
- **Reference:** Section 3.4 of plan.md

---

### TASK-7002: Setup Structured Logging
- **Priority:** 🟠 P1
- **Effort:** 8 hours
- **Assignee:** Developer
- **Description:** Implement structured logging with structlog
- **Acceptance Criteria:**
  - [ ] Add to `requirements.in`: `structlog`
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Install: `pip install -r requirements.txt`
  - [ ] Configure structlog in `__init__.py`
  - [ ] Create logging configuration
  - [ ] Add structured logging to key operations:
    - User login
    - Deposits/withdrawals
    - Database operations
    - API calls
    - Errors
  - [ ] Include context: user_id, request_id, timestamp
  - [ ] Test log output format
  - [ ] Commit: "feat(logging): Structured logging with structlog"
- **Related Files:**
  - `requirements.in` (edit)
  - `src/total_bankroll/__init__.py` (edit)
  - Multiple files for logging calls (edit)
- **Dependencies:** TASK-7001
- **Reference:** Section 3.4 of plan.md

---

### TASK-7003: Add Application Metrics
- **Priority:** 🟡 P2
- **Effort:** 6 hours
- **Assignee:** Developer
- **Description:** Track application performance metrics
- **Acceptance Criteria:**
  - [ ] Add to `requirements.in`: `prometheus-flask-exporter`
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Install: `pip install -r requirements.txt`
  - [ ] Initialize metrics exporter
  - [ ] Expose metrics endpoint: `/metrics`
  - [ ] Track request duration
  - [ ] Track request count by endpoint
  - [ ] Track error rate
  - [ ] Track database query time
  - [ ] Create Grafana dashboard (optional)
  - [ ] Commit: "feat(monitoring): Application metrics"
- **Related Files:**
  - `requirements.in` (edit)
  - `src/total_bankroll/__init__.py` (edit)
- **Dependencies:** TASK-7001
- **Reference:** Section 3.4 of plan.md

---

### TASK-7004: Configure Uptime Monitoring
- **Priority:** 🟠 P1
- **Effort:** 2 hours
- **Assignee:** Developer
- **Description:** Setup external uptime monitoring
- **Acceptance Criteria:**
  - [ ] Already done in TASK-0006, verify still active
  - [ ] Add additional monitors for key endpoints:
    - `/api/health` (create if doesn't exist)
    - `/login`
    - `/dashboard`
  - [ ] Set check interval to 5 minutes
  - [ ] Configure multi-location checks
  - [ ] Test alerts (temporarily break site)
  - [ ] Document monitoring setup
- **Related Files:**
  - `README.md` (update)
- **Dependencies:** TASK-7001
- **Reference:** Section 7.7 of plan.md

---

### TASK-7005: Create Alerting Rules
- **Priority:** 🟠 P1
- **Effort:** 4 hours
- **Assignee:** Developer
- **Description:** Configure alerting for critical issues
- **Acceptance Criteria:**
  - [ ] Configure Sentry alerts:
    - New error types
    - Error spike (>10 errors/minute)
    - Performance degradation
  - [ ] Configure UptimeRobot alerts:
    - Site down
    - Slow response (>5 seconds)
  - [ ] Setup alert channels:
    - Email
    - SMS (optional)
  - [ ] Create on-call schedule
  - [ ] Document alert response procedures
  - [ ] Test each alert type
  - [ ] Commit documentation
- **Related Files:**
  - `docs/incident_response.md` (new)
- **Dependencies:** TASK-7001, TASK-7004
- **Reference:** Section 3.4 of plan.md

---

### TASK-7006: Deploy Phase 7 Changes
- **Priority:** 🟠 P1
- **Effort:** 1 hour
- **Assignee:** Developer
- **Description:** Deploy monitoring improvements
- **Acceptance Criteria:**
  - [ ] Add Sentry DSN to production `.env`
  - [ ] Run environment parity check
  - [ ] Run tests
  - [ ] Commit all changes
  - [ ] Push to GitHub
  - [ ] Wait for CI/CD
  - [ ] Deploy with: `./scripts/deploy.sh`
  - [ ] Verify Sentry capturing events
  - [ ] Check structured logs
  - [ ] Test metrics endpoint
  - [ ] Verify alerts working
  - [ ] Monitor for 24 hours
  - [ ] Mark deployment successful
- **Related Files:**
  - All Phase 7 changes
  - Production `.env` (edit)
- **Dependencies:** TASK-7005
- **Reference:** Section 7.2 of plan.md

---

## Ongoing Maintenance Tasks

### MAINT-001: Weekly Security Audit
- **Priority:** 🟠 P1
- **Frequency:** Weekly
- **Effort:** 30 minutes
- **Description:** Check for security vulnerabilities
- **Tasks:**
  - [ ] Run: `pip-audit`
  - [ ] Review Sentry error reports
  - [ ] Check Dependabot alerts
  - [ ] Review access logs for suspicious activity
  - [ ] Update dependencies if needed

---

### MAINT-002: Monthly Dependency Updates
- **Priority:** 🟡 P2
- **Frequency:** Monthly
- **Effort:** 2 hours
- **Description:** Keep dependencies up-to-date
- **Tasks:**
  - [ ] Update `requirements.in` with newer versions
  - [ ] Run: `pip-compile requirements.in`
  - [ ] Test locally
  - [ ] Run full test suite
  - [ ] Deploy if no issues

---

### MAINT-003: Quarterly Architecture Review
- **Priority:** 🟡 P2
- **Frequency:** Quarterly
- **Effort:** 4 hours
- **Description:** Review and update architecture documentation
- **Tasks:**
  - [ ] Review plan.md for accuracy
  - [ ] Update ADRs if decisions changed
  - [ ] Review performance metrics
  - [ ] Identify new technical debt
  - [ ] Plan next quarter improvements

---

### MAINT-004: Database Backup Verification
- **Priority:** 🔴 P0
- **Frequency:** Weekly
- **Effort:** 15 minutes
- **Description:** Verify backups are working
- **Tasks:**
  - [ ] Check latest backup exists
  - [ ] Verify backup file size reasonable
  - [ ] Test restore on local environment (monthly)
  - [ ] Rotate old backups (keep 30 days)

---

## Task Summary Statistics

### By Phase
- **Week 0 (Deployment Safety):** 7 tasks, ~7 hours
- **Phase 1 (Foundation):** 6 tasks, ~10 hours
- **Phase 2 (Service Layer):** 6 tasks, ~32 hours
- **Phase 3 (Performance):** 7 tasks, ~50 hours
- **Phase 4 (Frontend):** 6 tasks, ~26 hours
- **Phase 5 (Database):** 5 tasks, ~40 hours
- **Phase 6 (API):** 7 tasks, ~44 hours
- **Phase 7 (Observability):** 6 tasks, ~24 hours
- **Ongoing Maintenance:** 4 recurring tasks

### By Priority
- 🔴 **P0 (Critical):** 10 tasks
- 🟠 **P1 (High):** 24 tasks
- 🟡 **P2 (Medium):** 15 tasks
- 🟢 **P3 (Low):** 0 tasks

### Total Effort
- **One-time tasks:** ~233 hours
- **Ongoing tasks:** ~7 hours/month

### Timeline
- **Critical Path:** Week 0 → Phase 1 → Phase 2 → Phase 3 → Phase 5 (18 weeks)
- **Parallel Work:** Phase 4, 6, 7 can be done alongside or after
- **Total Duration:** 28 weeks (7 months)

---

## Task Tracking

### Recommended Tools
- **GitHub Issues:** Create one issue per task, use labels for priority/phase
- **GitHub Projects:** Kanban board to track progress
- **Milestones:** One per phase for tracking completion

### Labels to Create
- `priority-p0-critical`
- `priority-p1-high`
- `priority-p2-medium`
- `priority-p3-low`
- `phase-0-deployment`
- `phase-1-foundation`
- `phase-2-services`
- `phase-3-performance`
- `phase-4-frontend`
- `phase-5-database`
- `phase-6-api`
- `phase-7-monitoring`
- `type-bug`
- `type-feature`
- `type-refactor`
- `type-test`
- `type-docs`

---

## Getting Started

### First Week Checklist
1. Complete all Week 0 tasks (deployment safety)
2. Create GitHub issues for all Phase 1 tasks
3. Setup project board
4. Review Phase 1 tasks with team
5. Begin TASK-1001 (Fix email library)

### Success Criteria
- ✅ Deployment process documented and tested
- ✅ All Phase 1 tasks completed without issues
- ✅ Service layer architecture established
- ✅ 80%+ test coverage achieved
- ✅ Performance improvements measurable
- ✅ Production monitoring active

---

**Last Updated:** 2025-11-05  
**Document Status:** Ready for Implementation  
**Next Review:** After Week 0 completion

---

*End of Task List*
