# StakeEasy.net (total_bankroll) Project Constitution

## Mission Statement

StakeEasy.net is a Flask-based web application designed to empower poker players with professional-grade bankroll management tools, strategic insights, and educational content, primarily focused on Pot Limit Omaha.

## Core Principles

### 1. User-Centric Design
- Every feature must solve a real problem for poker players
- Data entry should be fast and friction-free (target: <30 seconds on mobile)
- The dashboard is the single source of truth for a player's poker world

### 2. Data Integrity & Security
- All user financial data must be protected with industry-standard security
- Database operations must use SQLAlchemy ORM (no raw SQL)
- Sensitive configuration must live in `.env` files, never in code
- Production credentials must never touch development environments

### 3. Progressive Enhancement
- Core functionality must work without JavaScript
- Enhanced features can require modern browsers
- Mobile experience is first-class, not an afterthought

### 4. Educational Value
- Strategy content should be actionable and practical
- Tools should teach concepts through interaction
- Variance and bankroll management are fundamental truths to be taught

## Technology Stack Commitments

### Backend
- **Framework:** Flask with SQLAlchemy ORM
- **Database:** MySQL with Flask-Migrate for all schema changes
- **Authentication:** Flask-Security-Too + Flask-Dance (OAuth)
- **Configuration:** Centralized `config.py` with environment-specific settings

### Frontend
- **Templates:** Jinja2 with automatic XSS escaping (no `|safe` without justification)
- **Styling:** Bootstrap for consistency and responsiveness
- **Assets:** Vite for bundling, with helper utilities for development

### Security
- Passwords hashed with argon2
- CSRF protection on all forms
- X-Frame-Options set to SAMEORIGIN
- Debug mode strictly disabled in production
- Regular dependency audits with pip-audit

## Development Workflow Standards

### Database Changes
1. **Local First:** All changes tested in development environment
2. **Migration Scripts:** Use `flask db migrate` for every schema change
3. **Test Before Commit:** Apply with `flask db upgrade` and verify functionality
4. **Git as Source of Truth:** Commit migration scripts with code changes
5. **Production Deploy:** Pull, upgrade, reload (in that order)

### Code Quality
- Dependencies pinned with pip-tools (requirements.in → requirements.txt)
- Linting with flake8 (config in `.flake8`)
- Tests with pytest (CI via GitHub Actions)
- Type hints encouraged but not mandated

### File Organization
```
src/total_bankroll/
├── models.py           # All database models (SQLAlchemy)
├── extensions.py       # Flask extension instances
├── config.py          # Environment-specific configuration
├── frontend/          # Route handlers (blueprints)
├── templates/         # Jinja2 HTML templates
├── static/            # CSS, JS, images
└── data/              # JSON configuration files
```

## Environment Separation

### Development
- Path: `/home/ed/MEGA/total_bankroll/`
- Database: `bankroll` (user: `root`)
- FLASK_ENV: `development`
- Debug mode: Enabled

### Production (PythonAnywhere)
- Path: `/home/pythonpydev/total_bankroll/`
- Database: `pythonpydev$bankroll` (user: `pythonpydev`)
- FLASK_ENV: `production`
- Debug mode: Disabled
- Served via WSGI

## Feature Development Guidelines

### Before Adding a Feature
1. **Ask:** Does this help a poker player manage their bankroll or improve their game?
2. **Design:** Sketch the user flow on paper or in comments
3. **Data Model:** Consider database impact before writing routes
4. **Mobile:** How will this work on a phone?

### Implementation Order
1. Database model changes (if needed)
2. Backend route handler
3. Template with basic functionality
4. JavaScript enhancement (progressive)
5. Tests (at minimum, smoke tests)
6. Documentation update

### What Requires Migration
- Model field changes (add, remove, rename)
- New tables or relationships
- Index additions or changes
- Constraint modifications

### What Doesn't Require Migration
- Route changes
- Template updates
- Static file modifications
- Configuration changes
- Pure business logic

## Content Standards

### Strategy Articles
- Must be practical and actionable
- PLO-focused but applicable to other games where relevant
- Include concrete examples
- Cite sources for mathematical concepts

### Tool Design
- Should teach while being useful
- Results should be explainable (show the math)
- Edge cases should be handled gracefully with helpful messages

## Prohibited Actions

### Security
- Never commit secrets to git
- Never use raw SQL for user input
- Never disable CSRF protection
- Never use `|safe` in templates without sanitization
- Never share production credentials in development

### Data
- Never delete user data without explicit confirmation
- Never mix production and development databases
- Never bypass migration system for schema changes

### Code
- Never hardcode site-specific values (use configuration)
- Never use `SELECT *` in production code
- Never ignore SQLAlchemy warnings

## Success Metrics

### User Experience
- Session logging in <30 seconds on mobile
- Dashboard loads in <2 seconds
- Zero data loss incidents
- <1% error rate on production

### Code Quality
- All tests passing before merge
- No high-severity vulnerabilities in dependencies
- Migration scripts succeed on first try
- Code review completed within 48 hours

### Content
- New poker tool shipped monthly
- Strategy article published bi-weekly
- User engagement with educational content growing

## Version Control

### Commit Standards
- Descriptive messages (not "fix" or "update")
- Migration scripts committed with related code
- No commented-out code in commits
- .env files never committed

### Branch Strategy
- `main` branch is production-ready
- Feature branches for new work
- Test before merging

## Documentation Requirements

### Code
- Complex algorithms need explanation comments
- Public functions should have docstrings
- Configuration options documented in `.env.example`

### Project
- GEMINI.md is the comprehensive guide
- README.md is the quick start
- This constitution is the decision framework

## Decision Framework

When faced with a technical decision, ask:
1. **Security:** Is this the most secure approach?
2. **User:** Does this make life easier for poker players?
3. **Maintainability:** Can someone else understand this in 6 months?
4. **Performance:** Will this scale to 10,000 users?
5. **Consistency:** Does this match our existing patterns?

## Evolution

This constitution is a living document. Changes should be:
- Discussed before implementation
- Reflected in code review standards
- Updated in this file
- Communicated to all contributors

Last Updated: 2025-11-05
