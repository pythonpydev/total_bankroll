# StakeEasy.net Application - Gemini Overview

## Project Overview

This project is a Flask-based web application, **StakeEasy.net**, designed to help poker players track their bankroll. It allows users to:

* Manage funds across different poker sites and other assets (e.g., cash).
* Record deposit and withdrawal transactions.
* Calculate overall bankroll and profit totals.
* Handle multiple currencies by converting all values to a base currency (USD) for consistent tracking.
* Visualize bankroll distribution with charts.
* Incorporate the functionality of the spr project located at gh issue list -R pythonpydev/total_bankroll

## Technology Stack

* **Backend:** Flask
* **Database:** MySQL (using SQLAlchemy ORM)
* **Database Migrations:** Flask-Migrate (with Alembic)
* **Authentication:** Flask-Security-Too (for user registration, login, and password management), Flask-Dance (for OAuth with Google and Facebook)
* **Frontend:** HTML, Bootstrap, Jinja2
* **Configuration:** Centralized `config.py` with environment-specific settings, loading sensitive data from a `.env` file using `python-dotenv`.
* **Deployment:** Hosted on PythonAnywhere, served via WSGI.

## Database Schema

The application uses SQLAlchemy to define the database models. The key models are:

* **`User`**: Stores user information, including email, password hash, and confirmation status. Inherits from `flask_security.UserMixin`.
* **`OAuth`**: Stores OAuth information for users who sign in with Google or Facebook.

*Note: The core application tables (`assets`, `asset_history`, `currency`, `deposits`, `drawings`, `sites`, `site_history`) were originally defined in raw SQL. The project has been migrated to use SQLAlchemy for all models, ensuring a consistent and robust way to manage the database schema via Flask-Migrate.*

## Project Structure

```
/home/ed/MEGA/total_bankroll/
├── .env
├── .flake8
├── .gitignore
├── GEMINI.md
├── LICENSE
├── README.md
├── requirements.in
├── requirements.txt
├── wsgi.py
├── .github/
│   └── workflows/
│       └── python-ci.yml
├── migrations/
│   └── ... (Alembic migration scripts)
├── src/
│   └── total_bankroll/
│       ├── __init__.py
│       ├── config.py
│       ├── models.py
│       ├── routes/
│       │   └── ... (Blueprint route files)
│       ├── static/
│       │   ├── css/
│       │   ├── js/
│       │   └── assets/
│       └── templates/
│           └── ... (Jinja2 template files)
└── tests/
    └── ... (Pytest test files)
```

## Security Configuration

The application has a number of security features in place:

* **Password Hashing:** Passwords are hashed using `argon2`, which is a strong, modern hashing algorithm.
* **CSRF Protection:** `Flask-WTF` is used to provide CSRF protection on all forms.
* **Environment Variables:** Sensitive information, such as secret keys and database credentials, is stored in a `.env` file and not hardcoded in the source code.
* **Configuration Management:** The application uses separate configurations for development and production, which prevents production credentials from being used in the development environment.
* **Email Confirmation:** New users are required to confirm their email address before they can log in.
* **Password Reset:** Users can securely reset their password via a token-based email link.

## Potential Security Flaws & Recommendations

While the application has a good security foundation, there are several areas that could be improved:

1. **SQL Injection in Raw SQL:** This vulnerability has been addressed by migrating all database table definitions and interactions to SQLAlchemy ORM, managed by Flask-Migrate. This ensures that all database operations are properly parameterized, significantly reducing the risk of SQL injection.

2. **Cross-Site Scripting (XSS):** Jinja2, the templating engine used by Flask, automatically escapes data by default, which helps to prevent XSS attacks. A review of the application's templates (`src/total_bankroll/templates/`) found no instances where the `|safe` filter was explicitly used, indicating that auto-escaping is consistently applied for application-rendered data. This mitigates the risk of XSS through this vector.

3. **Dependency Vulnerabilities:** This has been addressed. The `requirements.txt` file now pins dependencies to specific versions using `pip-tools` (generated from `requirements.in`). Regular vulnerability scanning can be performed using `pip-audit`. A recent scan found no known vulnerabilities.

4. **Error Handling:** The application currently runs in debug mode in development, which can leak sensitive information in error messages. While this is fine for development, it's important to ensure that debug mode is disabled in production. **Recommendation:** Double-check that `FLASK_ENV` is set to `production` in the PythonAnywhere environment to disable debug mode.

5. **Clickjacking:** The `X-Frame-Options` header has been set to `SAMEORIGIN` in `src/total_bankroll/__init__.py`. This helps mitigate clickjacking attacks by preventing the site from being embedded in iframes on other origins. Further enhancement could include implementing a Content Security Policy (CSP).

## Access Github Issues Lists

To retrieve a list of GitHub issues for this project, you can use the GitHub CLI (`gh`).

**Command:**

```bash
gh issue list -R pythonpydev/total_bankroll
```

**Project's GitHub URL:**
https://github.com/pythonpydev/total_bankroll

# Deployment Workflow for Database Changes

To ensure that database schema changes are applied safely and consistently to both the local development environment and the production server on PythonAnywhere, follow this procedure for every change that affects the database models.

## Phase 1: On Your Local Development Machine

This is where all work and testing should be done first.

1. **Make Code Changes:** Modify your Python code as needed (e.g., add a column to a model in `src/total_bankroll/models.py`).

2. **Generate Migration Script:** In your local terminal, run the `migrate` command to create the database migration script.
   
   ```bash
   flask db migrate -m "A short, descriptive message for the change"
   ```

3. **Apply Migration Locally:** Run the `upgrade` command to apply the changes to your local database.
   
   ```bash
   flask db upgrade
   ```

4. **Test Locally:** Start your local server (`flask run`) and thoroughly test the application to ensure the new feature works and nothing else is broken.

5. **Commit to Git:** Once you are confident that everything works, commit all your changes (including the new migration script) to your git repository.
   
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   git push
   ```

## Phase 2: On the PythonAnywhere Production Server

After successfully testing and pushing your changes, you can deploy to the live server.

1. **Pull Latest Code:** In your **PythonAnywhere Bash console**, navigate to your project directory and pull the latest code.
   
   ```bash
   cd ~/total_bankroll
   git pull
   ```

2. **Activate Environment:** Prepare your console session.
   
   ```bash
   workon bankroll_venv
   export FLASK_APP="src/total_bankroll"
   ```

3. **Apply Migration to Production:** Run the same `upgrade` command to apply the changes to your live database.
   
   ```bash
   flask db upgrade
   ```

4. **Reload Web App:** Go to the **"Web"** tab on your PythonAnywhere dashboard and click the big green **"Reload"** button to make your changes live.

### Running the Application

To run the Flask application locally for development, follow these steps.

1. **Navigate to the project's root directory:** Open your terminal and change into the application's main folder.
   
   ```bash
   cd /home/ed/MEGA/total_bankroll/
   ```

2. **Install Python Dependencies (if you haven't already):** This command reads the `requirements.txt` file and installs all the necessary Python packages for the project.
   
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:** The application needs a `.env` file in the root directory (`/home/ed/MEGA/total_bankroll/.env`) to load configuration like secret keys and database credentials. If it doesn't exist, create it and add the following content, filling in your actual details:
   
   ```
   # .env file for total_bankroll project
   FLASK_ENV=development
   
   # A strong, random secret key for session management
   SECRET_KEY="YOUR_FLASK_SECRET_KEY"
   
   # Exchange Rate API Key (from exchangerate-api.com)
   EXCHANGE_RATE_API_KEY="YOUR_EXCHANGERATE_API_KEY"
   
   # MySQL Database Credentials
   DB_HOST="localhost"
   DB_NAME="bankroll"
   DB_USER="efb"
   DB_PASS="post123!"
   ```

4. **Run the Flask Application:** This command starts the development web server. The `FLASK_APP` variable is set within the `create_app` factory, so it does not need to be exported separately.
   
   ```bash
   flask run
   ```

After running the last command, you should see output indicating the server is running, and you'll be able to access it in your web browser, typically at `http://127.0.0.1:5000/`.

# Cash-Game Stakes (Typical)

Typical buy-in ranges (often 40bb minimum — 100bb maximum). Values shown in USD.

| ID  | Small Blind | Big Blind | Minimum Buy-In | Maximum Buy-In |
| --- | ----------- | --------- | -------------- | -------------- |
| 1   | $0.01       | $0.02     | $0.80          | $2.00          |
| 2   | $0.02       | $0.05     | $2.00          | $5.00          |
| 3   | $0.05       | $0.10     | $4.00          | $10.00         |
| 4   | $0.10       | $0.25     | $10.00         | $25.00         |
| 5   | $0.25       | $0.50     | $20.00         | $50.00         |
| 6   | $0.50       | $1.00     | $40.00         | $100.00        |
| 7   | $1.00       | $2.00     | $80.00         | $200.00        |
| 8   | $2.00       | $5.00     | $200.00        | $500.00        |
| 9   | $5.00       | $10.00    | $400.00        | $1,000.00      |
| 10  | $10.00      | $20.00    | $800.00        | $2,000.00      |
| 11  | $25.00      | $50.00    | $2,000.00      | $5,000.00      |
| 12  | $50.00      | $100.00   | $4,000.00      | $10,000.00     |
| 13  | $100.00     | $200.00   | $8,000.00      | $20,000.00     |

**Notes:**  

- These are typical ranges used on PokerStars' cash-game (no-limit Hold'em) tables; actual availability and buy-in limits vary by region, table type, and traffic.  
- Many tables use a 40bb–100bb standard (shown above). Some deep-stack tables allow higher maximums (e.g., up to 250bb).



# Pot Limit Omaha SPR Calculator

This file provides context and instructions for the Gemini CLI to assist in the
development of a Pot Limit Omaha (PLO) Stack-to-Pot Ratio (SPR) calculator.

## Project Location

/home/ed/MEGA/spr/

## Overview

The goal of this project is to create a website that assists poker player that
play four card Pot Limit Omaha (PLO) poker.

The site allows users to input their starting PLO hands, the size of the pot
etc. and allows players to guess what the Stack to Pot Ratio (SPR) is. The site
calculates the correct SPR for a given hand of PLO. The user will input the
effective stack size and the size of the pot, and the tool will output the SPR.

The site should also calculate how many pot sized bets a player could make
given the hero's stack size and the size of the pot and convert this into
actions: e.g. raise before the flop, bet pot on the flop, bet pot on the turn
and bet pot on the river.

The app will be able to evaluate a player's PLO hand on a given flop and
identify how many cards left in the deck will improve their hand (i.e. number
of outs). It will then be able to calculate the odds of improving as a
percentage, decimal and fraction or ration (e.g. 3 to 1 or 3/1).

The app will be able to evaluate the strengths of the hero's hand on a given
flop and also factor in any draws e.g. draws to a straight, flush, full house,
four of a kind or a straight flush.

Most of the information required for the project is located in tables.md
located in /home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/spr/docs/

The site will evaluate the equity of the hero's hand and their opponent's hand
and will determine what action the hero should take based on the information
contained party in decisions.html and also based on the information provided
in the text book
Advanced Pot-Limit Omaha_ Small Ball and Short-Handed Play ( PDFDrive ).pdf
which is located in
/home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/spr/docs/

The project is structured as a standard Python package with a `src` directory,
tests, and configuration files like `pyproject.toml`.

## Key Technologies

- Language: Python 3 (>=3.8)
- Dependency Management: `pip` with `requirements.txt`
- Testing: `pytest`
- Linting: `flake8`
- Formatting: `black`

## Core Logic

The core logic for the web application is implemented in `src/spr/app.py`. The
core calculation logic is implemented in `src/spr/algo.py`. [nb. both of these will change when the app is integrated into the total_bankroll app]

### PLO hand strength

The app uses the treys python package to evaluate the strength of PLO hands.

### Interface

The interface is defined in `src/spr/app.py` (however this will change when the app is integrated into total_bankroll) and uses Flask to implement a HTML
front end. JavaScript is also used throughout for front-end elements and
form validation etc.  These are all the same as the total_bankroll app making integration much easier.

## Development Guidelines

- All code should be written in Python 3 and conform to the project's existing
  style.
- Use `pytest` for testing. Test files are located in the `tests/` directory.
- Use `flake8` for linting and `black` for formatting.
- Dependencies are managed in `requirements.txt`.

## Example Usage

Users navigate to form.html, to input the hand details etc. and then click on
the submit button. The app will then display the hands as images of cards. The
user is given the opportunity to input their guess of the SPR. When they press
the Submit SPR Guess button the app displays the correct SPR. Users can also
click on the View Hand Evaluation button which will display the relative hand
strengths of the hero's and opponent's hand.

## To do

The following improvements need to be made to the website:

1. [x] Improve the Home page.
2. [x] Calculate pot-sized bets.
3. [x] Calculate outs.
4. [x] Calculate odds.
5. [ ] Calculate pot equities.
6. [x] Evaluate hand strength.
7. [ ] Determine the hero's next action.
8. [ ] Create a quiz.

### Anticipated difficulties of each task

1. **Improve the Home page:** This is a straightforward task. (Completed)
2. **Calculate pot-sized bets:** This is a relatively simple calculation. (Completed)
3. **Calculate outs:** This is a medium-complexity task that will require some logic to identify all possible improving cards. (Completed)
4. **Calculate odds:** This is a simple calculation once the number of outs is known. (Completed)
5. **Calculate pot equities:** This is a complex task, but as mentioned before, there are existing libraries and algorithms that can be used for this.
6. **Evaluate hand strength:** This is a medium-complexity task that will involve combining the absolute hand ranking with the number of outs. (Completed)
7. **Determine the hero's next action:** This is still the most challenging task. The tables.md file will be a great help, but it will still require careful
   implementation to translate the tables into a working decision-making engine.
8. **Create a quiz:** This is a large but well-defined task. The detailed requirements in the "To Do" list will make it much easier to implement.

## 
