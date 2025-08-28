# Total Bankroll Application - Gemini Overview

## Project Overview

This project is a Flask-based web application designed to help users track their poker bankroll. It allows users to manage funds across different poker sites, track assets, and record deposits and withdrawals. The application supports multiple currencies and provides data visualization through charts.

## Technology Stack

*   **Backend:** Flask
*   **Database:** MySQL (using SQLAlchemy ORM)
*   **Authentication:** Flask-Security-Too (for user registration, login, and password management), Flask-Dance (for OAuth with Google and Facebook)
*   **Frontend:** HTML, Bootstrap, Jinja2
*   **Environment Management:** python-dotenv

## Hosting Environment

*   **Local Development:**
    *   **OS:** Linux Mint
    *   **Database:** Local MySQL instance named `bankroll`.
    *   **Configuration:** Managed via a `.env` file in the project root.
*   **Production:**
    *   **Provider:** PythonAnywhere
    *   **URL:** [pythonpydev.pythonanywhere.com](https://pythonpydev.pythonanywhere.com/)
    *   **Database:** Hosted MySQL database on PythonAnywhere.

## Database Schema

The application uses SQLAlchemy to define the database models. The key models are:

*   **`User`**: Stores user information, including email, password hash, and confirmation status. Inherits from `flask_security.UserMixin`.
*   **`OAuth`**: Stores OAuth information for users who sign in with Google or Facebook.

*Note: The other tables (`assets`, `asset_history`, `currency`, `deposits`, `drawings`, `sites`, `site_history`) are defined directly in the `bankroll.sql` file and are not managed by SQLAlchemy models. This is a potential area for improvement; using SQLAlchemy for all tables would provide a more consistent and robust way to manage the database schema.*

## Security Configuration

The application has a number of security features in place:

*   **Password Hashing:** Passwords are hashed using `argon2`, which is a strong, modern hashing algorithm.
*   **CSRF Protection:** `Flask-WTF` is used to provide CSRF protection on all forms.
*   **Environment Variables:** Sensitive information, such as secret keys and database credentials, is stored in a `.env` file and not hardcoded in the source code.
*   **Configuration Management:** The application uses separate configurations for development and production, which prevents production credentials from being used in the development environment.
*   **Email Confirmation:** New users are required to confirm their email address before they can log in.
*   **Password Reset:** Users can securely reset their password via a token-based email link.

## Potential Security Flaws & Recommendations

While the application has a good security foundation, there are several areas that could be improved:

1.  **SQL Injection in Raw SQL:** This vulnerability has been addressed by migrating all database table definitions and interactions to SQLAlchemy ORM, managed by Flask-Migrate. This ensures that all database operations are properly parameterized, significantly reducing the risk of SQL injection.

2.  **Cross-Site Scripting (XSS):** Jinja2, the templating engine used by Flask, automatically escapes data by default, which helps to prevent XSS attacks. A review of the application's templates (`src/total_bankroll/templates/`) found no instances where the `|safe` filter was explicitly used, indicating that auto-escaping is consistently applied for application-rendered data. This mitigates the risk of XSS through this vector.

3.  **Dependency Vulnerabilities:** This has been addressed. The `requirements.txt` file now pins dependencies to specific versions using `pip-tools` (generated from `requirements.in`). Regular vulnerability scanning can be performed using `pip-audit`. A recent scan found no known vulnerabilities.

4.  **Error Handling:** The application currently runs in debug mode in development, which can leak sensitive information in error messages. While this is fine for development, it's important to ensure that debug mode is disabled in production. **Recommendation:** Double-check that `FLASK_ENV` is set to `production` in the PythonAnywhere environment to disable debug mode.

5.  **Clickjacking:** The `X-Frame-Options` header has been set to `SAMEORIGIN` in `src/total_bankroll/__init__.py`. This helps mitigate clickjacking attacks by preventing the site from being embedded in iframes on other origins. Further enhancement could include implementing a Content Security Policy (CSP).

## GitHub Issues

- Google Gemini CLI should check the list of issues on github at the start of each session and update the list below if necessay.  Instructions for this are shown below.

*   [#15: Reformat site template so that there is a central container with two columns either side that could be used for advertising, news feed, additional buttons etc.](https://github.com/pythonpydev/total_bankroll/issues/15)
*   [#14: Cross-Site Scripting (XSS)](https://github.com/pythonpydev/total_bankroll/issues/14)
*   [#13: SQL Injection in Raw SQL](https://github.com/pythonpydev/total_bankroll/issues/13)
*   [#12: Error Handling](https://github.com/pythonpydev/total_bankroll/issues/12)
*   [#11: Dependency Vulnerabilities](https://github.com/pythonpydev/total_bankroll/issues/11)
*   [#10: Clickjacking](https://github.com/pythonpydev/total_bankroll/issues/10)
*   [#9: On poker sites and assets, original amount should be first deposited amount. could have recent change and overall change too?](https://github.com/pythonpydev/total_bankroll/issues/9)
*   [#8: Look at buying URL](https://github.com/pythonpydev/total_bankroll/issues/8)
*   [#7: Add table for cash game blinds](https://github.com/pythonpydev/total_bankroll/issues/7)
*   [#6: Add recommended stakes for cash and tournament based on bankroll](https://github.com/pythonpydev/total_bankroll/issues/6)
*   [#5: Add buy me a coffee link](https://github.com/pythonpydev/total_bankroll/issues/5)
*   [#2: Solid fill colours for chart keys](https://github.com/pythonpydev/total_bankroll/issues/2)

## Access Github Issues Lists

To retrieve a list of GitHub issues for this project, you can use the GitHub CLI (`gh`).

**Command:**
```bash
gh issue list -R pythonpydev/total_bankroll
```

**Project's GitHub URL:**
https://github.com/pythonpydev/total_bankroll

# Cash-Game Stakes (Typical)

Typical buy-in ranges (often 40bb minimum — 100bb maximum). Values shown in USD.

| ID | Small Blind | Big Blind | Minimum Buy-In | Maximum Buy-In |
|----|-------------|-----------|----------------|----------------|
| 1  | $0.01 | $0.02 | $0.80  | $2.00   |
| 2  | $0.02 | $0.05 | $2.00  | $5.00   |
| 3  | $0.05 | $0.10 | $4.00  | $10.00  |
| 4  | $0.10 | $0.25 | $10.00 | $25.00  |
| 5  | $0.25 | $0.50 | $20.00 | $50.00  |
| 6  | $0.50 | $1.00 | $40.00 | $100.00 |
| 7  | $1.00 | $2.00 | $80.00 | $200.00 |
| 8  | $2.00 | $5.00 | $200.00 | $500.00 |
| 9  | $5.00 | $10.00 | $400.00 | $1,000.00 |
| 10 | $10.00 | $20.00 | $800.00 | $2,000.00 |
| 11 | $25.00 | $50.00 | $2,000.00 | $5,000.00 |
| 12 | $50.00 | $100.00 | $4,000.00 | $10,000.00 |
| 13 | $100.00 | $200.00 | $8,000.00 | $20,000.00 |

**Notes:**  
- These are typical ranges used on PokerStars' cash-game (no-limit Hold'em) tables; actual availability and buy-in limits vary by region, table type, and traffic.  
- Many tables use a 40bb–100bb standard (shown above). Some deep-stack tables allow higher maximums (e.g., up to 250bb).
