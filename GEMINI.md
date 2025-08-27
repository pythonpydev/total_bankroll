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

1.  **SQL Injection in Raw SQL:** The application uses raw SQL in the `bankroll.sql` file to define the schema. While the application itself uses SQLAlchemy, which protects against SQL injection, any future raw SQL queries added to the application could be vulnerable if not properly parameterized. **Recommendation:** Migrate all table definitions to SQLAlchemy models to ensure a consistent and secure way of interacting with the database.

2.  **Cross-Site Scripting (XSS):** Jinja2, the templating engine used by Flask, automatically escapes data by default, which helps to prevent XSS attacks. However, it's important to be careful not to disable this feature (e.g., by using the `|safe` filter) unless absolutely necessary. **Recommendation:** Review all templates to ensure that the `|safe` filter is only used on trusted data.

3.  **Dependency Vulnerabilities:** The `requirements.txt` file does not pin dependencies to specific versions. This means that `pip install -r requirements.txt` could install a newer version of a library with a known vulnerability. **Recommendation:** Use a tool like `pip-tools` to compile a `requirements.txt` file with pinned versions, and regularly scan for vulnerabilities using a tool like `pip-audit`.

4.  **Error Handling:** The application currently runs in debug mode in development, which can leak sensitive information in error messages. While this is fine for development, it's important to ensure that debug mode is disabled in production. **Recommendation:** Double-check that `FLASK_ENV` is set to `production` in the PythonAnywhere environment to disable debug mode.

5.  **Clickjacking:** The application does not currently have a Content Security Policy (CSP) or the `X-Frame-Options` header set. This could make it vulnerable to clickjacking attacks. **Recommendation:** Implement a strict CSP and set the `X-Frame-Options` header to `DENY` or `SAMEORIGIN`.

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
