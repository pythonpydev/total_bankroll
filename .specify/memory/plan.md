# StakeEasy.net Architecture & Technology Stack Plan

**Document Version:** 1.0.0  
**Created:** 2025-11-05  
**Status:** Active  
**Type:** Architecture Decision Record (ADR) Collection

---

## Executive Summary

This document provides a comprehensive analysis of StakeEasy.net's technology stack and architecture, critiques current choices, and proposes improvements aligned with the project's constitution and operational requirements.

**Current State:** Flask monolith with MySQL backend, deployed on PythonAnywhere  
**Assessment:** Generally solid for MVP, but with identifiable scaling and maintainability concerns  
**Recommendation:** Incremental modernization with focus on maintainability and performance

---

## Table of Contents

1. [Current Architecture Overview](#1-current-architecture-overview)
2. [Technology Stack Analysis](#2-technology-stack-analysis)
3. [Architecture Critique](#3-architecture-critique)
4. [Proposed Improvements](#4-proposed-improvements)
5. [Migration Roadmap](#5-migration-roadmap)
6. [Decision Records](#6-decision-records)

---

## 1. Current Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Browser   │  │   Mobile   │  │   Future   │            │
│  │  (Desktop) │  │  (Safari,  │  │   Native   │            │
│  │            │  │   Chrome)  │  │    Apps    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Vite Build Output (Static)              │   │
│  │  - Bundled JavaScript (ES6+)                         │   │
│  │  - Minified CSS (Bootstrap + Custom)                 │   │
│  │  - Optimized Images                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Jinja2 Templates (Server)               │   │
│  │  - SSR HTML generation                               │   │
│  │  - Template inheritance                              │   │
│  │  - Auto-escaping for XSS prevention                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                Flask Application                      │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │         17+ Blueprint Modules               │  │   │
│  │  │  (auth, sites, assets, charts, tools, etc.)    │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │         Flask Extensions                        │  │   │
│  │  │  - Security-Too (Auth)                         │  │   │
│  │  │  - SQLAlchemy (ORM)                            │  │   │
│  │  │  - WTF (Forms/CSRF)                            │  │   │
│  │  │  - Limiter (Rate Limiting)                     │  │   │
│  │  │  - Mail (Email)                                │  │   │
│  │  │  - Dance (OAuth)                               │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  RecommendationEngine  │  CurrencyConverter          │   │
│  │  AchievementTracker    │  DataUtils                  │   │
│  │  (Currently mixed with route handlers)               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SQLAlchemy ORM Models                   │   │
│  │  - 15+ model classes                                 │   │
│  │  - Relationship definitions                          │   │
│  │  - Query construction                                │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Flask-Migrate (Alembic)                 │   │
│  │  - Schema versioning                                 │   │
│  │  - Migration scripts (17+ versions)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       PERSISTENCE LAYER                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    MySQL 8.0+                        │   │
│  │  - InnoDB engine                                     │   │
│  │  - 15+ tables                                        │   │
│  │  - Foreign key constraints                           │   │
│  │  - Indexes on relationships                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ExchangeRate │  │    Gmail     │  │   Google/    │      │
│  │     API      │  │     SMTP     │  │   Facebook   │      │
│  │              │  │              │  │    OAuth     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Deployment Architecture

**Current: PythonAnywhere Single Server**
```
┌─────────────────────────────────────────────────────────────┐
│                   PythonAnywhere Platform                    │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Web Worker                          │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │    WSGI Server (Gunicorn assumed)               │  │  │
│  │  │    └── Flask Application Instance               │  │  │
│  │  │        └── SQLAlchemy Connection Pool           │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              MySQL Database Service                   │  │
│  │  (pythonpydev.mysql.pythonanywhere-services.com)     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              File System (Static Assets)              │  │
│  │  /home/pythonpydev/total_bankroll/                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Limitations:**
- Single point of failure
- No horizontal scaling
- Shared resources (CPU, memory)
- Limited control over infrastructure
- No caching layer
- No background job processing

### 1.3 Data Flow Patterns

**Request/Response Flow**
```
User Action (Browser)
    │
    ├─► [1] Form Submission (POST) with CSRF token
    │       │
    │       ├─► [2] Flask Route Handler (Blueprint)
    │       │       │
    │       │       ├─► [3] Form Validation (WTForms)
    │       │       │       │
    │       │       │       ├─► [4] Business Logic Execution
    │       │       │       │       │
    │       │       │       │       ├─► [5] Database Query (SQLAlchemy)
    │       │       │       │       │       │
    │       │       │       │       │       └─► MySQL Read/Write
    │       │       │       │       │
    │       │       │       │       ├─► [6] External API Call (if needed)
    │       │       │       │       │       │
    │       │       │       │       │       └─► Currency/OAuth Service
    │       │       │       │       │
    │       │       │       │       └─► [7] Achievement Check
    │       │       │       │
    │       │       │       └─► [8] Template Rendering (Jinja2)
    │       │       │
    │       │       └─► [9] HTTP Response (HTML + Headers)
    │       │
    │       └─► [10] Browser Renders Page
    │
    └─► [Alternative] AJAX Request (JSON)
            │
            └─► Similar flow but returns JSON response
```

---

## 2. Technology Stack Analysis

### 2.1 Backend Framework: Flask

#### Current Implementation
```python
# App Factory Pattern
from flask import Flask
from .extensions import db, mail, limiter, csrf

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Extension initialization
    db.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    
    # Blueprint registration (17+ blueprints)
    app.register_blueprint(home_bp)
    # ... more blueprints
    
    return app
```

#### Strengths
✅ **Lightweight & Flexible:** Perfect for rapid development  
✅ **Mature Ecosystem:** Extensive plugin support  
✅ **Well-Documented:** Strong community resources  
✅ **Pythonic:** Clean, readable code  
✅ **Low Learning Curve:** Easy onboarding for developers  

#### Weaknesses
❌ **No Built-in Structure:** Requires discipline for organization  
❌ **Manual Wiring:** Extensions must be explicitly configured  
❌ **Scaling Challenges:** Not designed for microservices out-of-the-box  
❌ **Async Support:** Limited native async/await support (Flask 2.0+)  

#### Critique
**Assessment: ✅ APPROPRIATE for current scale**

Flask is an excellent choice for this application's requirements:
- User base likely <10,000 concurrent users
- Request/response pattern dominant (not event-driven)
- Team familiar with Python ecosystem
- Rapid iteration needed for feature development

**Concern:** The 17+ blueprint modules suggest some organizational debt. The mixing of `frontend/` and `routes/` directories indicates architectural inconsistency.

#### Alternative Considerations

**FastAPI** (Python)
- **Pros:** Native async, automatic OpenAPI docs, better performance, modern type hints
- **Cons:** Less mature ecosystem for traditional web apps, requires migration effort
- **Verdict:** Consider for API-heavy features or microservices extraction

**Django** (Python)
- **Pros:** Batteries included, built-in admin, better structure enforcement
- **Cons:** More opinionated, heavier framework, admin panel underutilized
- **Verdict:** Not recommended; Flask's flexibility better suits this project

**Recommendation:** **Keep Flask** but refactor route organization and extract business logic into service layer.

---

### 2.2 Database: MySQL

#### Current Implementation
```
Database: MySQL 8.0+
Engine: InnoDB (assumed)
Schema: 15+ tables with foreign key constraints
ORM: SQLAlchemy 2.0+
Migrations: Flask-Migrate (Alembic)
```

#### Strengths
✅ **ACID Compliance:** Strong transactional guarantees  
✅ **Mature & Stable:** Battle-tested in production  
✅ **Good Performance:** Efficient for relational data  
✅ **Wide Support:** Available on most hosting platforms  
✅ **Cost-Effective:** Free tier on PythonAnywhere  

#### Weaknesses
❌ **JSON Handling:** Limited JSON query capabilities vs PostgreSQL  
❌ **Full-Text Search:** Basic compared to PostgreSQL or Elasticsearch  
❌ **Scaling Reads:** Requires read replicas for horizontal scaling  
❌ **Geographic Distribution:** Complex for multi-region deployments  

#### Critique
**Assessment: ⚠️ ADEQUATE with caveats**

MySQL works well for the current schema, which is primarily relational. However:

**Concerns:**
1. **Article Content:** Storing markdown and HTML separately is redundant. PostgreSQL's JSONB would allow richer metadata storage.
2. **Currency Rates:** Time-series data might benefit from specialized storage (TimescaleDB, InfluxDB).
3. **No Caching Layer:** All reads hit the database directly, causing performance bottlenecks.

#### Schema Quality Analysis

**Well-Designed:**
- Proper foreign key relationships
- Appropriate use of `Numeric(10,2)` for currency
- DateTime with UTC timezone awareness
- Cascade deletes for user data cleanup

**Areas for Improvement:**
- **Missing Indexes:** No evidence of composite indexes on `(user_id, recorded_at)` for history tables
- **Denormalization Opportunity:** Total bankroll could be cached to avoid repeated aggregations
- **Audit Trail:** No soft deletes or audit logging for financial transactions

#### Alternative Considerations

**PostgreSQL**
- **Pros:** Superior JSON support, better full-text search, extensibility (PostGIS, TimescaleDB)
- **Cons:** Slightly more resource-intensive, migration complexity
- **Verdict:** ⭐ **Recommended for future migration**

**PythonAnywhere Constraint:** Check if PostgreSQL is available/affordable on current hosting tier.

**MongoDB** (NoSQL)
- **Pros:** Flexible schema, good for document-centric data
- **Cons:** Not suitable for financial transactions, relationship complexity
- **Verdict:** ❌ Not appropriate for this use case

**Recommendation:** 
1. **Short-term:** Add Redis caching layer in front of MySQL
2. **Medium-term:** Migrate to PostgreSQL (6-12 months)
3. **Long-term:** Consider read replicas if scaling demands increase

---

### 2.3 ORM: SQLAlchemy

#### Current Implementation
```python
# Model Example
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    sites = db.relationship('Sites', backref='user', lazy='dynamic')
    deposits = db.relationship('Deposits', backref='user', lazy='dynamic')
```

#### Strengths
✅ **Type Safety:** Models provide clear data contracts  
✅ **Relationship Management:** Automatic joins and lazy/eager loading  
✅ **Migration Support:** Flask-Migrate integration for schema versioning  
✅ **Query Flexibility:** Can drop to raw SQL when needed  
✅ **Security:** Prevents SQL injection through parameterization  

#### Weaknesses
❌ **Performance Overhead:** Slight performance cost vs raw SQL  
❌ **Learning Curve:** Complex querying can be non-intuitive  
❌ **N+1 Queries:** Easy to accidentally cause performance issues  
❌ **Debugging:** Error messages can be cryptic  

#### Critique
**Assessment: ✅ EXCELLENT choice**

SQLAlchemy is industry-standard for Python ORMs and the implementation shows good practices:
- Proper use of `lambda: datetime.now(UTC)` for timezone-aware defaults
- Appropriate relationship definitions with `lazy='dynamic'` for large collections
- Migration scripts properly versioned (17+ migrations found)

**Observed Issues:**
1. **Mixed lazy loading:** Some relationships use `lazy='dynamic'`, others `lazy=True`, and some `lazy='subquery'`. Needs consistency.
2. **Missing indexes:** No explicit indexes defined in models (may exist in migrations).
3. **No query optimization patterns:** No evidence of using `joinedload()` or `selectinload()` to prevent N+1 queries.

#### Recommendations
1. **Add Query Optimization:** Use `lazy='select'` with explicit eager loading where needed
2. **Document Lazy Loading Strategy:** Add comments explaining when to use each strategy
3. **Implement Repository Pattern:** Abstract database queries from route handlers

```python
# Proposed Repository Pattern
class UserRepository:
    @staticmethod
    def get_user_with_sites(user_id):
        return db.session.query(User)\
            .options(joinedload(User.sites))\
            .filter(User.id == user_id)\
            .one_or_none()
```

---

### 2.4 Authentication: Flask-Security-Too

#### Current Implementation
```python
from flask_security import Security, SQLAlchemyUserDatastore

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_blueprint=False)
```

#### Configuration
- Password hashing: Argon2
- Email confirmation required
- Password reset via email
- 2FA support (TOTP)
- OAuth via Flask-Dance (Google, Facebook)

#### Strengths
✅ **Comprehensive:** Handles registration, login, reset, 2FA out-of-the-box  
✅ **Security Hardened:** Uses Argon2, proper token generation  
✅ **Customizable:** Can disable/enable features as needed  
✅ **Email Integration:** Built-in email templates  

#### Weaknesses
❌ **Heavy Dependency:** Large dependency tree  
❌ **Limited Customization:** Templates and flows somewhat rigid  
❌ **Documentation:** Can be sparse for advanced use cases  
❌ **OAuth Integration:** Requires separate Flask-Dance, adding complexity  

#### Critique
**Assessment: ✅ GOOD choice with reservations**

Flask-Security-Too is a solid choice for rapid development, but it's showing its age:

**Concerns:**
1. **OAuth Complexity:** Using both Flask-Security-Too AND Flask-Dance creates confusion. The code has `register_blueprint=False` suggesting custom auth flows.
2. **Maintenance:** Flask-Security-Too has less active maintenance than alternatives.
3. **Modern Auth Patterns:** Doesn't support modern patterns like WebAuthn, passkeys, or social login via OIDC.

#### Alternative Considerations

**Authlib** (with Flask-Login)
- **Pros:** Modern OAuth/OIDC support, actively maintained, lighter weight
- **Cons:** More manual work for user management
- **Verdict:** ⭐ **Recommended for new projects**

**Flask-User**
- **Pros:** Simpler, more flexible
- **Cons:** Less feature-complete
- **Verdict:** ❌ Not worth switching

**Recommendation:** 
1. **Short-term:** Document custom auth flows clearly
2. **Medium-term:** Migrate to Authlib + Flask-Login (when OAuth needs expand)
3. **Add:** Social login analytics to track which OAuth providers are used

---

### 2.5 Frontend Stack

#### Current Implementation

**Build Tool:** Vite 7.x
```json
// package.json
{
  "devDependencies": {
    "vite": "^7.1.12"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
```

**Styling:** Bootstrap 5.x + Custom CSS
**JavaScript:** Vanilla JS (ES6+) with modular utilities
**Templating:** Jinja2 (server-side rendering)

#### Strengths
✅ **Fast Development:** Vite provides instant HMR  
✅ **Modern Tooling:** ES6+ support, tree-shaking  
✅ **Progressive Enhancement:** Works without JavaScript  
✅ **Lightweight:** No heavy framework overhead  
✅ **SEO-Friendly:** Server-side rendering for content  

#### Weaknesses
❌ **No State Management:** Page-level state only  
❌ **Code Duplication:** Chart logic repeated across pages  
❌ **Limited Interactivity:** Full page reloads for most actions  
❌ **Type Safety:** No TypeScript for JavaScript code  
❌ **Testing:** No frontend test suite evident  

#### Critique
**Assessment: ⚠️ ADEQUATE but showing strain**

The current frontend approach is appropriate for a server-rendered app, but there are signs it's being pushed beyond its design:

**Observed Issues:**
1. **JavaScript Organization:** Single `main.js` file suggests growing complexity
2. **AJAX Patterns:** Likely using jQuery or fetch with inconsistent error handling
3. **Chart Libraries:** Loading heavy libraries (Chart.js?) without code splitting
4. **Mobile Experience:** No evidence of PWA features or offline support

**Missing Capabilities:**
- Real-time updates (e.g., bankroll changes)
- Optimistic UI updates
- Client-side validation with server sync
- Drag-and-drop for reordering sites/assets

#### Alternative Considerations

**Current Approach (Enhanced)**
- **Add:** Alpine.js for reactivity (~15KB)
- **Add:** HTMX for AJAX without JavaScript
- **Add:** TypeScript for utilities
- **Keep:** Jinja2 for initial render

**React/Vue SPA**
- **Pros:** Rich interactivity, component reuse, large ecosystem
- **Cons:** Complexity, SEO challenges, requires API backend
- **Verdict:** ❌ Overkill for current needs

**Hybrid (Recommended)**
```
Pages with Little Interaction → Server-Rendered (Jinja2)
    - Legal pages
    - Static content
    - Article listings

Pages with Rich Interaction → Island Architecture (Preact/Alpine)
    - Dashboard (charts)
    - Recommendation tool
    - Goal tracking
```

**Recommendation:**
1. **Add Alpine.js** for reactive components without build step
2. **Add HTMX** for seamless AJAX interactions
3. **Migrate to TypeScript** for utility functions (gradual)
4. **Implement code splitting** in Vite for chart libraries

---

### 2.6 Email Infrastructure: Flask-Mail / Flask-Mailman

#### Current Implementation
```python
# Dual email libraries detected
from flask_mailman import Mail  # In extensions.py
from flask_mail import ...      # In requirements.txt
```

**Configuration:**
- SMTP: Gmail
- TLS: Enabled
- Port: 587

#### Critique
**Assessment: ⚠️ CONFUSION - Two email libraries present**

This is a **red flag**. The project has BOTH Flask-Mail and Flask-Mailman in requirements:
```
Flask-Mail==0.10.0
Flask-Mailman==1.1.1
```

**Issues:**
1. **Conflicting Libraries:** These are alternatives, not complements
2. **Unclear Intent:** Code imports Flask-Mailman but Flask-Mail is installed
3. **Gmail SMTP:** Not ideal for transactional email at scale

**Gmail SMTP Limitations:**
- Rate limits (~500 emails/day for free accounts)
- Deliverability issues (may hit spam filters)
- No email analytics
- Manual credential management

#### Recommendations

**Immediate:**
1. **Choose One Library:** Remove either Flask-Mail or Flask-Mailman
2. **Recommendation:** Keep Flask-Mailman (more actively maintained)

**Short-term:**
1. **Add Email Queue:** Implement Celery for async email sending
2. **Add Retry Logic:** Handle transient SMTP failures

**Medium-term:**
1. **Migrate to Transactional Email Service:**
   - **SendGrid:** 100 free emails/day, good API
   - **Mailgun:** 5,000 free emails/month, better deliverability
   - **AWS SES:** Pay-per-use, excellent deliverability
   - **Resend:** Developer-friendly, generous free tier

**Recommended Migration Path:**
```python
# Step 1: Abstract email sending
class EmailService:
    def send_confirmation_email(self, user):
        pass  # Implementation agnostic

# Step 2: Implement adapters
class GmailAdapter(EmailService):
    pass

class SendGridAdapter(EmailService):
    pass

# Step 3: Configure via environment
email_service = SendGridAdapter() if PROD else GmailAdapter()
```

---

### 2.7 Rate Limiting: Flask-Limiter

#### Current Implementation
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

#### Strengths
✅ **Easy to Use:** Decorator-based API  
✅ **Flexible:** Per-route or global limits  
✅ **Storage Backends:** Supports Redis, Memcached, in-memory  

#### Weaknesses
❌ **In-Memory Default:** Doesn't scale horizontally  
❌ **IP-Based:** Can be bypassed with proxies  
❌ **No Dashboard:** Can't visualize rate limit hits  

#### Critique
**Assessment: ⚠️ FUNCTIONAL but limited**

**Concerns:**
1. **Current Storage:** Likely using in-memory storage (default), which doesn't persist across restarts
2. **Proxy Handling:** PythonAnywhere likely uses a proxy; `get_remote_address` may return proxy IP, not user IP
3. **No Rate Limit Headers:** Users can't see their remaining quota

#### Recommendations

**Immediate:**
```python
# Check if behind proxy
limiter = Limiter(
    key_func=lambda: request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
)
```

**Short-term:**
1. **Add Redis backend:**
```python
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)
```

2. **Add Rate Limit Headers:**
```python
@limiter.limit("5 per minute")
def login():
    # Flask-Limiter automatically adds X-RateLimit-* headers
    pass
```

**Medium-term:**
1. **User-Based Rate Limits:** Rate limit by `user_id` for authenticated routes
2. **Rate Limit Dashboard:** Add monitoring for rate limit violations

---

### 2.8 Asset Management: Vite

#### Current Implementation
```javascript
// vite.config.js (empty file)
```

**Issue:** The Vite configuration file exists but is empty, suggesting:
1. Default configuration is being used
2. Build process may not be optimized
3. Missing manifest generation for cache busting

#### Critique
**Assessment: ⚠️ INCOMPLETE setup**

**Required Vite Configuration:**
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    manifest: true,
    outDir: 'src/total_bankroll/static/assets',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/total_bankroll/frontend/main.js'),
      },
    },
  },
  server: {
    port: 5173,
    origin: 'http://localhost:5173',
  },
});
```

**Missing Features:**
- Asset manifest for production
- Source maps for debugging
- Proper entry point configuration
- HMR proxy for development

#### Recommendations

1. **Complete Vite Setup:** Implement proper configuration
2. **Development Mode:** Integrate Vite dev server with Flask
3. **Production Build:** Generate manifest.json for asset paths
4. **Cache Strategy:** Configure long-term caching with fingerprinting

---

### 2.9 Testing Infrastructure

#### Current State
```python
# pyproject.toml
[project.optional-dependencies]
test = ["pytest"]
```

**Evidence Found:**
- Pytest configured in pyproject.toml
- `tests/` directory exists
- GitHub Actions workflow: `.github/workflows/python-ci.yml`

**Missing:**
- Coverage reporting tool (pytest-cov)
- Frontend tests (Jest, Vitest)
- Integration test examples
- Test database setup
- Fixture factories

#### Critique
**Assessment: ⚠️ FOUNDATION exists but underutilized**

**Concerns:**
1. **Test Coverage Unknown:** No coverage reports in CI
2. **No Mocking Strategy:** External services (email, currency API) likely not mocked
3. **Database Tests:** Unclear if tests use real database or mocks
4. **No E2E Tests:** Missing Selenium/Playwright for critical user flows

#### Recommendations

**Testing Stack Upgrade:**
```toml
[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",      # Coverage reporting
    "pytest-flask>=1.2",    # Flask-specific fixtures
    "pytest-mock>=3.10",    # Mocking utilities
    "factory-boy>=3.2",     # Test data factories
    "faker>=18.0",          # Fake data generation
    "responses>=0.23",      # Mock HTTP requests
]
```

**Test Organization:**
```
tests/
├── conftest.py              # Shared fixtures
├── factories.py             # Factory Boy factories
├── unit/
│   ├── test_models.py
│   ├── test_recommendations.py
│   └── test_currency.py
├── integration/
│   ├── test_auth_flow.py
│   └── test_bankroll_crud.py
└── e2e/
    └── test_critical_paths.py
```

**CI/CD Enhancement:**
```yaml
# .github/workflows/python-ci.yml
- name: Run tests with coverage
  run: |
    pytest tests/ \
      --cov=src/total_bankroll \
      --cov-report=xml \
      --cov-report=html \
      --cov-fail-under=80
```

---

## 3. Architecture Critique

### 3.1 Layering & Separation of Concerns

#### Current Structure Issues

**Problem 1: Business Logic in Route Handlers**
```python
# Current: routes/poker_sites.py (conceptual example)
@poker_sites_bp.route('/sites', methods=['POST'])
def add_site():
    # Form validation
    # Business logic (calculate totals, check limits)
    # Database operations
    # Email notification
    # Achievement check
    # Response rendering
    pass
```

**Impact:**
- Hard to test (coupled to Flask request context)
- Business logic duplication across routes
- Difficult to reuse in CLI commands or background jobs

**Recommendation:** Extract to service layer
```python
# Proposed: services/bankroll_service.py
class BankrollService:
    def __init__(self, db_session):
        self.db = db_session
    
    def add_site(self, user_id: int, site_data: dict) -> Site:
        """Business logic for adding a site"""
        # Validation
        # Database operations
        # Achievement checks
        return site
    
    def calculate_total_bankroll(self, user_id: int) -> Decimal:
        """Calculate user's total bankroll across all sources"""
        pass

# Usage in route
@poker_sites_bp.route('/sites', methods=['POST'])
def add_site():
    service = BankrollService(db.session)
    site = service.add_site(current_user.id, form.data)
    return render_template('site_created.html', site=site)
```

---

**Problem 2: Inconsistent Route Organization**

Current structure has both `routes/` and `frontend/` directories with overlapping responsibilities:
```
src/total_bankroll/
├── frontend/
│   └── main.js         # JavaScript entry point
├── routes/
│   ├── __init__.py
│   ├── about.py
│   ├── auth.py
│   └── ... (28+ files)
```

**Confusion:** Are these separate concerns or organizational mistakes?

**Recommendation:** Consolidate
```
src/total_bankroll/
├── routes/              # All route handlers
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── login.py
│   │   └── register.py
│   ├── bankroll/
│   │   ├── __init__.py
│   │   ├── sites.py
│   │   └── assets.py
│   └── tools/
│       ├── __init__.py
│       └── calculators.py
├── services/            # Business logic
│   ├── __init__.py
│   ├── bankroll.py
│   └── recommendations.py
├── repositories/        # Database access
│   ├── __init__.py
│   └── user.py
└── assets/              # Frontend source
    ├── js/
    └── css/
```

---

**Problem 3: God Object - The User Model**

The `User` model has 7+ relationships:
```python
class User(db.Model):
    sites = db.relationship('Sites')
    assets = db.relationship('Assets')
    deposits = db.relationship('Deposits')
    drawings = db.relationship('Drawings')
    site_history = db.relationship('SiteHistory')
    asset_history = db.relationship('AssetHistory')
    goals = db.relationship('Goal')
    # ... more
```

**Impact:**
- Eager loading of User can trigger massive query
- Hard to reason about data access patterns
- Performance issues when querying users

**Recommendation:** Use repository pattern with explicit loading
```python
class UserRepository:
    @staticmethod
    def get_user_with_bankroll_data(user_id):
        return db.session.query(User)\
            .options(
                joinedload(User.sites),
                joinedload(User.assets)
            )\
            .filter(User.id == user_id)\
            .one()
    
    @staticmethod
    def get_user_with_history(user_id):
        # Different query for different needs
        pass
```

---

### 3.2 Performance Concerns

#### Identified Issues

**Issue 1: No Caching Layer**
- Every dashboard load calculates total bankroll from scratch
- Currency rates fetched from database on every request
- Article lists regenerated on every page load

**Impact:** 
- Slow page loads
- Unnecessary database load
- Poor user experience on mobile

**Recommendation:** Implement Redis caching
```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300, key_prefix='user_bankroll_%s' % current_user.id)
def get_total_bankroll(user_id):
    # Expensive calculation
    pass
```

---

**Issue 2: N+1 Query Problem**

Likely present in dashboard rendering:
```python
# Problematic code (conceptual)
user = User.query.get(current_user.id)
for site in user.sites:  # Triggers query per site
    print(site.history.latest())  # Another query per site!
```

**Fix:** Eager loading
```python
user = User.query\
    .options(
        joinedload(User.sites)
            .joinedload(Sites.history)
    )\
    .get(current_user.id)
```

---

**Issue 3: No Database Connection Pooling Configuration**

SQLAlchemy uses connection pooling by default, but current config doesn't specify:
- Pool size
- Pool timeout
- Pool recycle time

**Recommendation:**
```python
# config.py
class ProductionConfig(Config):
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,  # Checks connection before using
        'max_overflow': 20,
    }
```

---

**Issue 4: No Background Job Processing**

Blocking operations in request handlers:
- Sending emails
- Updating currency rates
- Checking achievements

**Recommendation:** Add Celery
```python
from celery import Celery

celery = Celery(
    app.name,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery.task
def send_confirmation_email(user_id):
    # Async email sending
    pass

# In route handler
send_confirmation_email.delay(user.id)
```

---

### 3.3 Security Architecture

#### Strengths
✅ CSRF protection enabled globally  
✅ Argon2 password hashing  
✅ Email confirmation required  
✅ Rate limiting on auth endpoints  
✅ SQL injection prevented via ORM  

#### Concerns

**Concern 1: Session Management**
- No evidence of session fixation protection
- Unclear if sessions invalidated on logout
- No session timeout configuration visible

**Recommendation:**
```python
# config.py
PERMANENT_SESSION_LIFETIME = timedelta(days=30)
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# On login
session.permanent = True
session.regenerate()  # Prevent session fixation
```

---

**Concern 2: Secrets Management**

Current: All secrets in `.env` file
```
SECRET_KEY=...
GOOGLE_CLIENT_SECRET=...
DB_PASS_PROD=...
```

**Issues:**
- Single point of failure
- No secrets rotation strategy
- No audit trail for secret access

**Recommendation (Future):**
- Use AWS Secrets Manager / HashiCorp Vault
- Implement secret rotation for database passwords
- Use environment-specific secrets (dev, staging, prod)

---

**Concern 3: Input Validation**

Relying solely on WTForms for validation:
```python
# Current pattern
if form.validate_on_submit():
    # Process data
```

**Missing:**
- Business-level validation
- Cross-field validation
- Async validation (e.g., checking if username available)

**Recommendation:**
```python
# Layered validation
class AddSiteService:
    def validate_and_add_site(self, user_id, data):
        # 1. Schema validation (WTForms)
        # 2. Business rules (user hasn't exceeded site limit)
        # 3. Domain validation (site name not profane)
        pass
```

---

**Concern 4: No Security Headers Middleware**

Security headers defined but not comprehensively:
```python
# Missing from current implementation
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response
```

**Recommendation:** Use Flask-Talisman
```python
from flask_talisman import Talisman

Talisman(app, 
    force_https=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'"],
    }
)
```

---

### 3.4 Observability & Monitoring

#### Current State
**Logging:**
```python
import logging
logger = logging.getLogger(__name__)
```

**Issues:**
- Basic logging to `app.log` file
- No structured logging
- No centralized log aggregation
- No alerting on errors

**Missing:**
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- User analytics
- Database query performance monitoring

#### Recommendations

**Level 1: Structured Logging**
```python
import structlog

logger = structlog.get_logger()

logger.info("user_login", 
    user_id=user.id, 
    ip_address=request.remote_addr,
    user_agent=request.user_agent.string
)
```

**Level 2: Error Tracking**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
)
```

**Level 3: APM (Future)**
- New Relic / Datadog / Elastic APM
- Track slow database queries
- Monitor endpoint response times
- Alert on error rate spikes

---

## 4. Proposed Improvements

### 4.1 Immediate Wins (0-2 weeks)

#### 1. Fix Email Library Confusion
**Task:** Remove duplicate email library  
**Effort:** 1 hour  
**Impact:** High (removes ambiguity)

```bash
pip uninstall Flask-Mail
# Update requirements.in
# Flask-Mailman==1.1.1  # Keep this one
pip-compile requirements.in
```

#### 2. Complete Vite Configuration
**Task:** Implement proper Vite setup  
**Effort:** 4 hours  
**Impact:** Medium (better dev experience)

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    manifest: true,
    outDir: 'src/total_bankroll/static/assets',
    rollupOptions: {
      input: resolve(__dirname, 'src/total_bankroll/frontend/main.js'),
    },
  },
});
```

#### 3. Add Database Indexes
**Task:** Optimize common queries  
**Effort:** 2 hours  
**Impact:** High (performance improvement)

```python
# Create migration
flask db migrate -m "Add composite indexes for performance"

# In migration
op.create_index(
    'ix_site_history_user_recorded',
    'site_history',
    ['user_id', 'recorded_at']
)
```

#### 4. Fix Rate Limiter for Proxy
**Task:** Correct IP detection behind proxy  
**Effort:** 1 hour  
**Impact:** High (security)

```python
def get_real_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]

limiter = Limiter(key_func=get_real_ip)
```

#### 5. Add Security Headers
**Task:** Install and configure Flask-Talisman  
**Effort:** 2 hours  
**Impact:** High (security hardening)

---

### 4.2 Short-Term Improvements (1-3 months)

#### 1. Implement Service Layer
**Task:** Extract business logic from routes  
**Effort:** 20 hours  
**Impact:** High (maintainability)

**Benefits:**
- Testable business logic
- Reusable across CLI, API, background jobs
- Clearer separation of concerns

**Approach:**
```
Week 1: Create services/ directory structure
Week 2: Extract bankroll calculation logic
Week 3: Extract recommendation engine
Week 4: Refactor routes to use services
```

#### 2. Add Redis Caching
**Task:** Implement caching layer  
**Effort:** 12 hours  
**Impact:** High (performance)

**Implementation:**
```python
# 1. Add redis to requirements
# 2. Configure Flask-Caching
# 3. Cache expensive operations:
#    - Total bankroll calculation
#    - Currency rates
#    - Article listings
```

**Deployment:**
- PythonAnywhere: Check Redis availability
- Alternative: Use in-memory caching (limited scalability)

#### 3. Background Job Queue
**Task:** Add Celery for async tasks  
**Effort:** 16 hours  
**Impact:** High (performance, reliability)

**Tasks to Move to Background:**
- Email sending
- Currency rate updates (daily cron)
- Achievement checks
- Report generation (future)

**Challenges:**
- PythonAnywhere: Check if Celery workers supported
- May require worker dyno on different host

#### 4. Test Suite Enhancement
**Task:** Comprehensive test coverage  
**Effort:** 24 hours  
**Impact:** High (quality assurance)

**Goals:**
- 80%+ coverage on business logic
- Integration tests for critical flows
- Mock external services
- CI fails on coverage drop

#### 5. Frontend Modernization (Phase 1)
**Task:** Add Alpine.js and HTMX  
**Effort:** 16 hours  
**Impact:** Medium (UX improvement)

**Targets:**
- Dashboard charts (Alpine.js)
- Form submissions (HTMX)
- Modal dialogs (Alpine.js)
- Drag-and-drop reordering (Sortable.js)

---

### 4.3 Medium-Term Improvements (3-6 months)

#### 1. Database Migration to PostgreSQL
**Task:** Migrate from MySQL to PostgreSQL  
**Effort:** 40 hours  
**Impact:** High (future-proofing)

**Justification:**
- Superior JSON support for article metadata
- Better full-text search for articles
- More extensible (PostGIS for future geo features)
- Better performance for complex queries

**Migration Plan:**
```
Phase 1: Setup PostgreSQL on staging
Phase 2: Data migration script
Phase 3: Test all features on staging
Phase 4: Production migration (scheduled maintenance)
Phase 5: MySQL deprecation after 2 weeks
```

**Risk Mitigation:**
- Keep MySQL backup for 30 days
- Gradual rollout (canary deployment if possible)

#### 2. API Layer Introduction
**Task:** Build RESTful API for mobile/3rd-party  
**Effort:** 60 hours  
**Impact:** High (future mobile app)

**Scope:**
```
/api/v1/
├── /auth/              # JWT authentication
├── /bankroll/          # Sites, assets, totals
├── /transactions/      # Deposits, withdrawals
├── /tools/             # Calculators
└── /articles/          # Content access
```

**Technology:**
- Flask-RESTX (API auto-documentation)
- JWT authentication (Flask-JWT-Extended)
- Rate limiting per API key
- Versioned endpoints

#### 3. Monitoring & Observability
**Task:** Production-grade monitoring  
**Effort:** 24 hours  
**Impact:** High (operational excellence)

**Components:**
1. **Error Tracking:** Sentry
2. **Structured Logging:** Structlog + CloudWatch/ELK
3. **Uptime Monitoring:** UptimeRobot / Pingdom
4. **Performance:** New Relic / Scout APM

#### 4. Progressive Web App (PWA)
**Task:** Add PWA capabilities  
**Effort:** 32 hours  
**Impact:** Medium (mobile UX)

**Features:**
- Offline mode (view cached data)
- Add to home screen
- Push notifications (goal milestones)
- Background sync for transactions

---

### 4.4 Long-Term Vision (6-12 months)

#### 1. Microservices Extraction (Optional)
**Consideration:** Extract high-load or isolated features

**Candidates:**
- **Recommendation Engine:** Stateless, compute-heavy
- **Currency Service:** External dependency, cacheable
- **Email Service:** Already isolated, move to queue worker

**Architecture:**
```
┌─────────────┐
│   Web App   │  (Flask monolith - UI, Auth, Core CRUD)
└──────┬──────┘
       │
       ├──► [Recommendation Service] (FastAPI)
       ├──► [Currency Service] (Go/FastAPI)
       └──► [Email Worker] (Celery)
```

**When to Consider:**
- User base >10,000 active users
- Specific performance bottlenecks identified
- Team size >5 developers

#### 2. Database Read Replicas
**Task:** Horizontal read scaling  
**Effort:** 16 hours  
**Impact:** High (if traffic demands)

**Use Cases:**
- Dashboard queries → Read replica
- Write operations → Primary
- Analytics queries → Dedicated replica

#### 3. CDN for Static Assets
**Task:** Distribute static assets globally  
**Effort:** 8 hours  
**Impact:** High (global users)

**Options:**
- CloudFlare (free tier)
- AWS CloudFront
- Fastly

**Benefits:**
- Faster asset loading
- Reduced server bandwidth
- DDoS protection (via CloudFlare)

---

## 5. Migration Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Fix immediate issues and stabilize architecture

| Task | Effort | Priority |
|------|--------|----------|
| Fix email library duplication | 1h | P0 |
| Complete Vite configuration | 4h | P1 |
| Add database indexes | 2h | P0 |
| Fix rate limiter IP detection | 1h | P0 |
| Add security headers (Talisman) | 2h | P1 |
| **Total** | **10h** | |

**Deliverables:**
- Single email library (Flask-Mailman)
- Proper Vite build pipeline
- Faster queries
- Correct rate limiting
- Security hardening

---

### Phase 2: Service Layer Refactoring (Weeks 3-6)
**Goal:** Separate business logic from presentation

| Task | Effort | Priority |
|------|--------|----------|
| Create services/ directory structure | 4h | P1 |
| Extract BankrollService | 8h | P1 |
| Extract RecommendationService | 6h | P1 |
| Extract AchievementService | 6h | P2 |
| Update tests for services | 8h | P1 |
| **Total** | **32h** | |

**Deliverables:**
- Clean separation of concerns
- Testable business logic
- Documented service interfaces

---

### Phase 3: Performance & Reliability (Weeks 7-10)
**Goal:** Add caching and background processing

| Task | Effort | Priority |
|------|--------|----------|
| Add Redis to infrastructure | 4h | P1 |
| Implement Flask-Caching | 6h | P1 |
| Set up Celery for background jobs | 10h | P1 |
| Move email sending to Celery | 4h | P1 |
| Add currency update cron job | 2h | P2 |
| Comprehensive test coverage | 24h | P1 |
| **Total** | **50h** | |

**Deliverables:**
- Faster page loads (caching)
- Non-blocking email sending
- Automated currency updates
- 80%+ test coverage

---

### Phase 4: Frontend Modernization (Weeks 11-14)
**Goal:** Improve interactivity without full rewrite

| Task | Effort | Priority |
|------|--------|----------|
| Add Alpine.js to project | 2h | P1 |
| Refactor dashboard with Alpine | 8h | P1 |
| Add HTMX for form submissions | 6h | P2 |
| Implement drag-and-drop reordering | 6h | P2 |
| Add loading states and optimistic UI | 4h | P2 |
| **Total** | **26h** | |

**Deliverables:**
- Reactive dashboard
- Seamless form interactions
- Drag-and-drop site/asset ordering

---

### Phase 5: Database Migration (Weeks 15-18)
**Goal:** Migrate to PostgreSQL

| Task | Effort | Priority |
|------|--------|----------|
| Set up PostgreSQL on staging | 4h | P1 |
| Write migration script | 12h | P1 |
| Test all features on PostgreSQL | 16h | P1 |
| Production migration execution | 4h | P1 |
| Monitoring and rollback plan | 4h | P1 |
| **Total** | **40h** | |

**Deliverables:**
- PostgreSQL as primary database
- Improved JSON query capabilities
- Better full-text search

---

### Phase 6: API & Mobile Prep (Weeks 19-24)
**Goal:** Build API for future mobile app

| Task | Effort | Priority |
|------|--------|----------|
| Design API schema | 8h | P2 |
| Implement Flask-RESTX | 12h | P2 |
| Add JWT authentication | 8h | P2 |
| Document API with Swagger | 4h | P2 |
| API rate limiting | 4h | P2 |
| API integration tests | 8h | P2 |
| **Total** | **44h** | |

**Deliverables:**
- RESTful API (v1)
- API documentation
- JWT-based authentication

---

### Phase 7: Observability (Weeks 25-28)
**Goal:** Production monitoring and alerting

| Task | Effort | Priority |
|------|--------|----------|
| Integrate Sentry for error tracking | 4h | P1 |
| Set up structured logging | 8h | P1 |
| Add application metrics | 6h | P2 |
| Configure uptime monitoring | 2h | P1 |
| Create alerting rules | 4h | P1 |
| **Total** | **24h** | |

**Deliverables:**
- Real-time error tracking
- Structured logs for debugging
- Uptime and performance monitoring

---

## 6. Decision Records

### ADR-001: Keep Flask as Core Framework
**Date:** 2025-11-05  
**Status:** Accepted

**Context:** Considering whether to migrate to FastAPI or Django

**Decision:** Continue with Flask

**Rationale:**
- Current team familiar with Flask
- Application is primarily request/response (not event-driven)
- Flask ecosystem mature and stable
- Migration cost not justified by benefits

**Consequences:**
- Continue investing in Flask best practices
- Monitor async needs for future reconsideration

---

### ADR-002: Migrate to PostgreSQL
**Date:** 2025-11-05  
**Status:** Proposed

**Context:** MySQL adequate but limiting for future features

**Decision:** Migrate to PostgreSQL in 6 months

**Rationale:**
- Superior JSON support for article metadata
- Better full-text search capabilities
- More extensible for future needs
- Industry standard for modern web apps

**Consequences:**
- Migration effort required (~40 hours)
- Need to verify PythonAnywhere PostgreSQL support
- Potential cost increase

**Alternatives Considered:**
- Stay with MySQL: Limited future flexibility
- Move to MongoDB: Not suitable for financial data

---

### ADR-003: Add Redis for Caching
**Date:** 2025-11-05  
**Status:** Accepted

**Context:** Performance issues from repeated calculations

**Decision:** Introduce Redis caching layer

**Rationale:**
- Significant performance gains for dashboard
- Required for distributed rate limiting
- Enables future session storage
- Industry-standard caching solution

**Consequences:**
- Additional infrastructure dependency
- Need to handle cache invalidation
- Monitoring required for cache hit rates

---

### ADR-004: Service Layer Extraction
**Date:** 2025-11-05  
**Status:** Accepted

**Context:** Business logic mixed with route handlers

**Decision:** Extract business logic into service layer

**Rationale:**
- Improves testability
- Enables code reuse (CLI, API, background jobs)
- Clearer separation of concerns
- Aligns with constitution principles

**Consequences:**
- Refactoring effort required (~32 hours)
- Learning curve for new pattern
- More files to maintain

---

### ADR-005: Progressive Enhancement for Frontend
**Date:** 2025-11-05  
**Status:** Accepted

**Context:** Need richer interactivity without full SPA rewrite

**Decision:** Use Alpine.js + HTMX for progressive enhancement

**Rationale:**
- Maintains SSR benefits (SEO, performance)
- Adds interactivity incrementally
- Small bundle size (~50KB total)
- Minimal learning curve

**Consequences:**
- Two new libraries to learn
- Template complexity increases slightly
- JavaScript required for enhanced features

**Alternatives Considered:**
- Full React/Vue SPA: Overkill, loses SSR benefits
- Pure Vanilla JS: More code to maintain
- Stay with current approach: Limited UX improvements

---

### ADR-006: Consolidate to Flask-Mailman
**Date:** 2025-11-05  
**Status:** Accepted

**Context:** Two email libraries present (Flask-Mail, Flask-Mailman)

**Decision:** Remove Flask-Mail, keep Flask-Mailman

**Rationale:**
- Flask-Mailman more actively maintained
- Django-inspired API (better documented)
- Elimates confusion and duplication

**Consequences:**
- Verify no code uses Flask-Mail APIs
- Update requirements.txt

---

### ADR-007: Celery for Background Jobs
**Date:** 2025-11-05  
**Status:** Proposed

**Context:** Blocking operations in request handlers

**Decision:** Introduce Celery with Redis broker

**Rationale:**
- Non-blocking email sending
- Enables scheduled tasks (currency updates)
- Industry-standard task queue
- Scalable solution

**Consequences:**
- Additional complexity (worker processes)
- Need to verify PythonAnywhere worker support
- May require separate hosting for workers

**Risks:**
- PythonAnywhere limitations for background workers
- May need to migrate hosting

---

### ADR-008: Monorepo Structure
**Date:** 2025-11-05  
**Status:** Accepted

**Context:** Considering monorepo vs separate repos for services

**Decision:** Maintain monorepo for now

**Rationale:**
- Simplified deployment
- Easier refactoring across boundaries
- Small team benefits from single codebase

**Consequences:**
- Must maintain clear module boundaries
- Reconsider if team grows >5 developers

---

## 7. Production Deployment Strategy

### 7.1 Current Deployment Process Issues

#### Identified Problems

**Problem 1: No Rollback Strategy**
- Current process: `git pull` → `flask db upgrade` → reload
- If migration fails: Application broken, no automatic recovery
- If code has bugs: Manual intervention required

**Problem 2: Downtime During Deployment**
- PythonAnywhere reload causes ~5-30 seconds of downtime
- Database migrations run while app is still serving traffic
- No health checks before switching to new code

**Problem 3: Environment Mismatch**
- Development uses Python 3.x (version unknown)
- Production PythonAnywhere may use different Python version
- Package versions can drift between environments
- No verification step before deployment

**Problem 4: No Deployment Checklist**
- Manual process prone to missed steps
- No verification that `.env` variables match production needs
- No check for breaking changes in dependencies

---

### 7.2 Recommended Zero-Downtime Deployment Process

#### Phase 1: Pre-Deployment (Local Environment)

**Step 1: Development & Testing**
```bash
# 1. Make code changes in development
cd /home/ed/MEGA/total_bankroll

# 2. Run local tests
pytest tests/ --cov=src/total_bankroll --cov-fail-under=80

# 3. Run linter
flake8 src/

# 4. Test application manually
flask run
# Open browser, test critical paths:
# - Login
# - Add deposit/withdrawal
# - View dashboard
# - Use one tool
```

**Step 2: Database Migration (if needed)**
```bash
# Only if models changed
flask db migrate -m "Descriptive message of what changed"

# Review the generated migration file
# Check: migrations/versions/XXXXX_description.py

# Verify migration is reversible
# Look for both upgrade() and downgrade() functions

# Test migration locally
flask db upgrade

# Test the application still works
flask run

# Test rollback capability
flask db downgrade
flask db upgrade  # Re-apply for commit
```

**Step 3: Dependency Check**
```bash
# If requirements.in changed
pip-compile requirements.in

# Check for security vulnerabilities
pip-audit

# Verify no critical vulnerabilities before deployment
```

**Step 4: Static Asset Build**
```bash
# Build production assets
npm run build

# Verify build output exists
ls -la src/total_bankroll/static/assets/

# Commit built assets (if not .gitignored)
git add src/total_bankroll/static/assets/
```

**Step 5: Commit & Push**
```bash
# Commit all changes including migration scripts
git add .
git status  # Review what's being committed

git commit -m "feat(feature): Descriptive commit message

- List of changes
- Database migration included (if applicable)
- Breaking changes (if any)

Closes #issue_number"

# Push to GitHub
git push origin main

# Wait for CI/CD to pass
# Check: https://github.com/pythonpydev/total_bankroll/actions
```

---

#### Phase 2: Production Deployment (PythonAnywhere)

**Step 1: Pre-Deployment Backup**
```bash
# SSH into PythonAnywhere or use Bash console
# Navigate to project directory
cd ~/total_bankroll

# 1. Backup database
mysqldump -u pythonpydev -p pythonpydev$bankroll \
  > ~/backups/bankroll_$(date +%Y%m%d_%H%M%S).sql

# 2. Backup code (optional but recommended)
tar -czf ~/backups/total_bankroll_$(date +%Y%m%d_%H%M%S).tar.gz \
  ~/total_bankroll

# 3. Note current git commit for rollback
git rev-parse HEAD > ~/backups/last_deployed_commit.txt
```

**Step 2: Pull New Code**
```bash
# Activate virtual environment
workon bankroll_venv

# Check current state
git status
git log -1  # Show last deployed commit

# Fetch changes
git fetch origin main

# Check what's about to be deployed
git log HEAD..origin/main --oneline

# Pull new code
git pull origin main

# Verify correct code is checked out
git log -1
```

**Step 3: Update Dependencies**
```bash
# Check if requirements.txt changed
git diff HEAD@{1} HEAD -- requirements.txt

# If changed, update packages
pip install --upgrade -r requirements.txt

# Verify no conflicts
pip check

# Record installed packages for debugging
pip freeze > ~/backups/pip_freeze_$(date +%Y%m%d_%H%M%S).txt
```

**Step 4: Database Migration (Critical Step)**
```bash
# Set Flask app
export FLASK_APP="src/total_bankroll"

# Check current database version
flask db current

# Check pending migrations
flask db history | head -20

# DRY RUN: Review migration SQL (if possible)
# For critical migrations, test on staging first

# Apply migrations
flask db upgrade

# Verify migration succeeded
flask db current

# If migration failed:
#   1. Check error message
#   2. DO NOT reload app
#   3. Roll back: flask db downgrade
#   4. Fix issue, re-deploy
```

**Step 5: Verification (Before Reload)**
```bash
# Run smoke tests (if available)
# pytest tests/smoke/ --production

# Check configuration
python -c "from src.total_bankroll import create_app; app = create_app('production'); print('Config OK')"

# Verify database connectivity
python -c "
from src.total_bankroll import create_app
from src.total_bankroll.models import db
app = create_app('production')
with app.app_context():
    db.session.execute('SELECT 1')
    print('Database OK')
"
```

**Step 6: Reload Application**
```bash
# Via PythonAnywhere Web UI:
# 1. Go to Web tab
# 2. Click the "Reload" button for stakeeasy.net
# 3. Note the time of reload

# OR via API (if PythonAnywhere API token configured)
# curl -X POST https://www.pythonanywhere.com/api/v0/user/pythonpydev/webapps/stakeeasy.net/reload/ \
#   -H "Authorization: Token YOUR_API_TOKEN"
```

**Step 7: Post-Deployment Verification**
```bash
# 1. Check error logs immediately
tail -f ~/logs/error.log

# 2. Test critical user paths (within 5 minutes)
# - Homepage loads
# - Login works
# - Dashboard displays
# - Database queries work
# - No 500 errors

# 3. Monitor for 30 minutes
# Check error logs every 5 minutes

# 4. If errors detected: ROLLBACK (see section 7.3)
```

---

### 7.3 Emergency Rollback Procedure

If deployment causes issues, follow this rollback procedure:

**Step 1: Immediate Response**
```bash
# Navigate to project
cd ~/total_bankroll

# Check current commit
git log -1

# Find last known good commit
cat ~/backups/last_deployed_commit.txt

# Rollback code
LAST_GOOD_COMMIT=$(cat ~/backups/last_deployed_commit.txt)
git reset --hard $LAST_GOOD_COMMIT
```

**Step 2: Database Rollback (if migration applied)**
```bash
# Activate environment
workon bankroll_venv
export FLASK_APP="src/total_bankroll"

# Check current migration
flask db current

# Roll back one migration
flask db downgrade

# Verify rollback
flask db current

# If multiple migrations applied, repeat downgrade
```

**Step 3: Restore Dependencies**
```bash
# Find last good pip freeze file
ls -lt ~/backups/pip_freeze_*.txt | head -1

# Restore packages
LAST_PIP_FREEZE=$(ls -t ~/backups/pip_freeze_*.txt | head -1)
pip install -r $LAST_PIP_FREEZE
```

**Step 4: Reload Application**
```bash
# Via PythonAnywhere Web UI: Click "Reload"
# Test immediately to confirm stability
```

**Step 5: Database Restore (Last Resort)**
```bash
# Only if database is corrupted and rollback failed
# Find latest backup
ls -lt ~/backups/bankroll_*.sql | head -1

# Restore database
BACKUP_FILE=$(ls -t ~/backups/bankroll_*.sql | head -1)
mysql -u pythonpydev -p pythonpydev$bankroll < $BACKUP_FILE

# Reload application
```

---

### 7.4 Improved Deployment Checklist

Create this checklist as `.github/deployment_checklist.md`:

```markdown
# Production Deployment Checklist

## Pre-Deployment (Local)

### Code Quality
- [ ] All tests passing (`pytest tests/`)
- [ ] Linting passes (`flake8 src/`)
- [ ] No security vulnerabilities (`pip-audit`)
- [ ] Code reviewed (if team >1)

### Database Changes
- [ ] Migration script generated (`flask db migrate`)
- [ ] Migration tested locally
- [ ] Migration reviewed for safety
- [ ] Migration has downgrade() function
- [ ] No data loss in migration

### Dependencies
- [ ] requirements.txt updated (if needed)
- [ ] No conflicting package versions
- [ ] All packages available on PyPI

### Static Assets
- [ ] `npm run build` successful
- [ ] Built assets committed (or .gitignored and rebuilt on server)

### Documentation
- [ ] CHANGELOG.md updated
- [ ] Breaking changes documented
- [ ] Environment variable changes noted

### Testing
- [ ] Smoke test on local
- [ ] Critical user paths tested manually
- [ ] Performance acceptable locally

### Version Control
- [ ] All changes committed
- [ ] Descriptive commit message
- [ ] Pushed to GitHub
- [ ] CI/CD passing

---

## Deployment (PythonAnywhere)

### Backup
- [ ] Database backup created
- [ ] Code backup created (optional)
- [ ] Current commit hash saved

### Pull Code
- [ ] Virtual environment activated
- [ ] Current state verified
- [ ] Changes reviewed (`git log HEAD..origin/main`)
- [ ] Code pulled successfully

### Dependencies
- [ ] requirements.txt changes checked
- [ ] Packages updated (if needed)
- [ ] No package conflicts

### Database Migration
- [ ] Flask app exported
- [ ] Current migration version noted
- [ ] Migration applied (`flask db upgrade`)
- [ ] Migration success verified

### Pre-Reload Verification
- [ ] Config loads without error
- [ ] Database connectivity verified
- [ ] No syntax errors in Python code

### Reload
- [ ] Application reloaded via Web UI
- [ ] Reload timestamp noted

---

## Post-Deployment

### Immediate Verification (0-5 minutes)
- [ ] Homepage loads
- [ ] Login works
- [ ] Dashboard displays
- [ ] No 500 errors in logs

### Short-Term Monitoring (5-30 minutes)
- [ ] Error logs checked (every 5 min)
- [ ] Critical features tested
- [ ] Performance acceptable
- [ ] No user reports of issues

### Long-Term Monitoring (30min - 24hrs)
- [ ] Error rate normal
- [ ] Database performance normal
- [ ] No memory leaks
- [ ] User activity normal

---

## Rollback (If Issues)

### Immediate Actions
- [ ] Issue severity assessed
- [ ] Rollback decision made
- [ ] Code reverted (`git reset`)
- [ ] Database downgraded (`flask db downgrade`)
- [ ] Application reloaded

### Post-Rollback
- [ ] Issue documented
- [ ] Rollback verified
- [ ] Users notified (if needed)
- [ ] Fix planned for next deployment
```

---

### 7.5 Preventing Environment Mismatch

#### Problem: Dev/Prod Inconsistencies

**Solution 1: Environment Parity Check Script**

Create `scripts/check_env_parity.py`:

```python
#!/usr/bin/env python3
"""
Check for environment parity between development and production.
Run this before deployment to catch potential issues.
"""
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure Python version matches production."""
    current = sys.version_info
    required = (3, 9)  # Update to match PythonAnywhere Python version
    
    if current[:2] != required:
        print(f"❌ Python version mismatch!")
        print(f"   Current: {current.major}.{current.minor}")
        print(f"   Required: {required[0]}.{required[1]}")
        return False
    else:
        print(f"✅ Python version OK: {current.major}.{current.minor}")
        return True

def check_env_file():
    """Check .env file has production variables."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file missing!")
        return False
    
    required_vars = [
        "FLASK_ENV",
        "SECRET_KEY",
        "DB_HOST_PROD",
        "DB_NAME_PROD",
        "DB_USER_PROD",
        "DB_PASS_PROD",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
    ]
    
    env_content = env_path.read_text()
    missing = []
    
    for var in required_vars:
        if var not in env_content:
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("✅ All required environment variables present")
        return True

def check_database_migrations():
    """Ensure no uncommitted migrations."""
    result = subprocess.run(
        ["git", "status", "--porcelain", "migrations/"],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print("❌ Uncommitted migration files detected!")
        print(result.stdout)
        return False
    else:
        print("✅ All migrations committed")
        return True

def check_static_assets():
    """Verify Vite build completed."""
    assets_dir = Path("src/total_bankroll/static/assets")
    
    if not assets_dir.exists():
        print("❌ Static assets directory missing!")
        print("   Run: npm run build")
        return False
    
    if not list(assets_dir.glob("*.js")):
        print("⚠️  No JavaScript assets found. Run: npm run build")
        return False
    
    print("✅ Static assets present")
    return True

def main():
    """Run all checks."""
    print("=" * 60)
    print("Environment Parity Check")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_env_file(),
        check_database_migrations(),
        check_static_assets(),
    ]
    
    print("=" * 60)
    
    if all(checks):
        print("✅ All checks passed! Safe to deploy.")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
# Before deployment
python scripts/check_env_parity.py
```

---

**Solution 2: Pin Python Version**

Update `pyproject.toml`:

```toml
[project]
requires-python = ">=3.9,<3.12"  # Match PythonAnywhere version
```

Update `.python-version` (for pyenv users):

```
3.9.18
```

---

**Solution 3: Production Requirements Verification**

Create `scripts/verify_prod_requirements.sh`:

```bash
#!/bin/bash
# Verify all production requirements can be installed
set -e

echo "Testing production requirements installation..."

# Create temporary virtual environment
python3 -m venv /tmp/prod_test_env
source /tmp/prod_test_env/bin/activate

# Try installing requirements
pip install --upgrade pip
pip install -r requirements.txt

# Run basic import test
python -c "
from src.total_bankroll import create_app
app = create_app('production')
print('✅ Production requirements valid')
"

# Cleanup
deactivate
rm -rf /tmp/prod_test_env

echo "✅ All production requirements verified"
```

---

### 7.6 Automated Deployment Script (Advanced)

Create `scripts/deploy.sh` for semi-automated deployment:

```bash
#!/bin/bash
# Automated deployment script for PythonAnywhere
# Usage: ./scripts/deploy.sh [--skip-backup] [--dry-run]

set -e  # Exit on error

# Configuration
PROJECT_DIR="$HOME/total_bankroll"
BACKUP_DIR="$HOME/backups"
VENV_NAME="bankroll_venv"
DB_NAME="pythonpydev\$bankroll"
DB_USER="pythonpydev"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_BACKUP=false
DRY_RUN=false

for arg in "$@"; do
  case $arg in
    --skip-backup)
      SKIP_BACKUP=true
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
  esac
done

# Helper functions
log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

confirm() {
  read -p "$1 (y/n) " -n 1 -r
  echo
  [[ $REPLY =~ ^[Yy]$ ]]
}

# Step 1: Pre-flight checks
log_info "Running pre-flight checks..."

if [ ! -d "$PROJECT_DIR" ]; then
  log_error "Project directory not found: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

if [ "$DRY_RUN" = true ]; then
  log_warn "DRY RUN MODE - No changes will be made"
fi

# Step 2: Backup
if [ "$SKIP_BACKUP" = false ]; then
  log_info "Creating backup..."
  
  mkdir -p "$BACKUP_DIR"
  
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  BACKUP_SQL="$BACKUP_DIR/bankroll_$TIMESTAMP.sql"
  
  if [ "$DRY_RUN" = false ]; then
    mysqldump -u "$DB_USER" -p "$DB_NAME" > "$BACKUP_SQL"
    log_info "Database backed up to: $BACKUP_SQL"
    
    # Save current commit
    git rev-parse HEAD > "$BACKUP_DIR/last_deployed_commit.txt"
  else
    log_info "[DRY RUN] Would backup database to: $BACKUP_SQL"
  fi
else
  log_warn "Skipping backup (--skip-backup flag set)"
fi

# Step 3: Pull code
log_info "Fetching latest code..."

git fetch origin main

log_info "Changes to be deployed:"
git log HEAD..origin/main --oneline

if ! confirm "Continue with deployment?"; then
  log_warn "Deployment cancelled by user"
  exit 0
fi

if [ "$DRY_RUN" = false ]; then
  git pull origin main
else
  log_info "[DRY RUN] Would pull code from origin/main"
fi

# Step 4: Update dependencies
log_info "Checking for dependency changes..."

if git diff HEAD@{1} HEAD -- requirements.txt | grep -q '^[+-]'; then
  log_info "Dependencies changed, updating..."
  
  if [ "$DRY_RUN" = false ]; then
    source "$HOME/.virtualenvs/$VENV_NAME/bin/activate"
    pip install --upgrade -r requirements.txt
  else
    log_info "[DRY RUN] Would update pip packages"
  fi
else
  log_info "No dependency changes detected"
fi

# Step 5: Database migrations
log_info "Checking for database migrations..."

if [ "$DRY_RUN" = false ]; then
  source "$HOME/.virtualenvs/$VENV_NAME/bin/activate"
  export FLASK_APP="src/total_bankroll"
  
  PENDING_MIGRATIONS=$(flask db history | grep -c "->")
  
  if [ "$PENDING_MIGRATIONS" -gt 0 ]; then
    log_info "Applying database migrations..."
    flask db upgrade
  else
    log_info "No pending migrations"
  fi
else
  log_info "[DRY RUN] Would check and apply migrations"
fi

# Step 6: Reload application
log_info "Reloading application..."

if [ "$DRY_RUN" = false ]; then
  # Manual reload required via Web UI
  log_warn "Manual action required:"
  log_warn "1. Go to PythonAnywhere Web tab"
  log_warn "2. Click 'Reload' button"
  log_warn ""
  log_warn "Press Enter after reloading..."
  read
else
  log_info "[DRY RUN] Would reload application"
fi

# Step 7: Post-deployment verification
log_info "Deployment complete!"
log_info "Verify the following:"
log_info "1. Homepage loads: https://stakeeasy.net"
log_info "2. Login works"
log_info "3. Check error logs: tail -f ~/logs/error.log"
log_info ""
log_info "Monitor for 30 minutes before marking as stable"

if [ "$SKIP_BACKUP" = false ]; then
  log_info "Backup location: $BACKUP_SQL"
  log_info "To rollback: git reset --hard \$(cat $BACKUP_DIR/last_deployed_commit.txt)"
fi

exit 0
```

**Usage:**
```bash
# Standard deployment with backup
./scripts/deploy.sh

# Dry run to see what would happen
./scripts/deploy.sh --dry-run

# Skip backup (not recommended)
./scripts/deploy.sh --skip-backup
```

---

### 7.7 Monitoring & Alerting

**Set up basic monitoring to catch deployment issues:**

**Option 1: UptimeRobot (Free)**
1. Create account at uptimerobot.com
2. Add monitor for https://stakeeasy.net
3. Set check interval to 5 minutes
4. Configure email alerts on downtime

**Option 2: PythonAnywhere Task for Health Check**
Create `scripts/health_check.py`:

```python
#!/usr/bin/env python3
"""
Health check script to verify application is running.
Schedule this as a PythonAnywhere task to run every 5 minutes.
"""
import requests
import sys
from datetime import datetime

def check_health():
    try:
        response = requests.get("https://stakeeasy.net", timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {datetime.now()}: Site healthy (200 OK)")
            return 0
        else:
            print(f"⚠️ {datetime.now()}: Site returned {response.status_code}")
            return 1
    except requests.exceptions.RequestException as e:
        print(f"❌ {datetime.now()}: Site unreachable - {e}")
        return 2

if __name__ == "__main__":
    sys.exit(check_health())
```

Schedule in PythonAnywhere:
```
Schedule: */5 * * * *  (every 5 minutes)
Command: /home/pythonpydev/.virtualenvs/bankroll_venv/bin/python /home/pythonpydev/total_bankroll/scripts/health_check.py
```

---

## Conclusion

StakeEasy.net's current architecture is **fundamentally sound** for an MVP, but exhibits signs of technical debt that will impede future growth. The proposed improvements focus on:

1. **Immediate stabilization** (fix email library, security headers)
2. **Architectural cleanup** (service layer, route organization)
3. **Performance optimization** (caching, background jobs)
4. **Future-proofing** (PostgreSQL, API layer)
5. **Deployment safety** (zero-downtime, rollback procedures)

**Key Success Metrics:**
- Page load time <2 seconds (currently unknown)
- Test coverage >80% (currently unknown)
- Zero security vulnerabilities (currently compliant)
- Developer onboarding <1 day (improved by service layer)
- **Deployment success rate >95%** (new metric)
- **Zero downtime deployments** (new goal)

**Critical Path:**
Phase 1 → Phase 2 → Phase 3 → Phase 5

Phases 4, 6, 7 can proceed in parallel once Phase 3 completes.

**Estimated Timeline:** 28 weeks (7 months) for complete implementation  
**Estimated Effort:** ~256 hours of focused development

---

**Document Approval**

This architecture plan should be reviewed quarterly and updated as the application scales and requirements evolve.

**Next Steps:**
1. Review this plan with stakeholders
2. Implement deployment checklist and scripts (Week 1)
3. Prioritize immediate wins (Phase 1)
4. Begin service layer extraction (Phase 2)
5. Establish monitoring baseline before optimizations

---

*End of Architecture Plan*
