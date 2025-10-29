# total_bankroll also known as StakeEasy.net Application - Gemini Overview

## Project Overview

This project is a Flask-based web application, **StakeEasy.net**, designed to help poker players track their bankroll. It allows users to:

* Manage funds across different poker sites and other assets (e.g., cash).
* Record deposit and withdrawal transactions.
* Calculate overall bankroll and profit totals.
* Handle multiple currencies by converting all values to a base currency (USD) for consistent tracking.
* Visualize bankroll distribution with charts.
* Incorporate various tools for poker players (mainly for pot limit omaha)
* Repository of poker articles (again mainly for pot limit omaha)

## Technology Stack

* **Backend:** Flask
* **Database:** MySQL (using SQLAlchemy ORM)
* **Database Migrations:** Flask-Migrate (with Alembic)
* **Authentication:** Flask-Security-Too (for user registration, login, and password management), Flask-Dance (for OAuth with Google and Facebook)
* **Frontend:** HTML, Bootstrap, Jinja2, javascript
* **Configuration:** Centralized `config.py` with environment-specific settings, loading sensitive data from a `.env` file using `python-dotenv`.
* **Deployment:** Hosted on PythonAnywhere, served via WSGI.

## Database Schema

The application uses SQLAlchemy to define the database models. The key models are:

| Table              | Description                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------------- |
| **users**          | Stores user information, including email, password hash, and confirmation status.            |
| **oauth**          | Stores OAuth information for users who sign in with Google or Facebook.                      |
| **sites**          | Represents online poker sites or other locations where funds are held.                       |
| **assets**         | Represents non-site assets, such as cash or cryptocurrency.                                  |
| **deposits**       | Records deposit transactions made by the user.                                               |
| **drawings**       | Records withdrawal (drawing) transactions made by the user.                                  |
| **site_history**   | Tracks the historical balance of each site over time.                                        |
| **asset_history**  | Tracks the historical value of each asset over time.                                         |
| **currency**       | Stores currency information, including exchange rates relative to a base currency (USD).     |
| **cash_stakes**    | Stores information about cash game stakes.                                                   |
| **articles**       | Stores poker articles, including title, content, and author, for the PLO content repository. |
| **topics**         | Stores topics for articles.                                                                  |
| **article_topics** | A many-to-many association table linking articles to topics.                                 |

*Note: The core application tables (`assets`, `asset_history`, `currency`, `deposits`, `drawings`, `sites`, `site_history`) were originally defined in raw SQL. The project has been migrated to use SQLAlchemy for all models, ensuring a consistent and robust way to manage the database schema via Flask-Migrate.*

## Development Environment Project Structure

```
/home/ed/MEGA/total_bankroll/
├── .env
├── .flake8
├── .gitignore
├── GEMINI.md
├── package.json
├── LICENSE
├── README.md
├── requirements.in
├── requirements.txt
├── vite.config.js
├── wsgi.py
├── .github/
│   └── workflows/
│       └── python-ci.yml
├── migrations/
│   └── versions/
│       ├── ... (Alembic migration scripts)
├── src/
│   └── total_bankroll/
│       ├── __init__.py
│       ├── app.log
│       ├── commands.py
│       ├── config.py
│       ├── currency.py
│       ├── data_utils.py
│       ├── extensions.py
│       ├── models.py
│       ├── vite_asset_helper.py
│       ├── oauth.py
│       ├── recommendations.py
│       ├── seed_articles.py
│       ├── utils.py
│       ├── data/
│       │   └── recommendation_logic.json
│       ├── routes/
│       │   ├── ... (numerous route files)
│       ├── frontend/
│       │   ├── __init__.py
│       │   ├── about.py
│       │   ├── add_deposit.py
│       │   ├── add_withdrawal.py
│       │   ├── algo.py
│       │   ├── articles.py
│       │   ├── assets.py
│       │   ├── auth.py
│       │   ├── charts.py
│       │   ├── common.py
│       │   ├── currency_update.py
│       │   ├── deposit.py
│       │   ├── hand_eval.py
│       │   ├── help.py
│       │   ├── home.py
│       │   ├── hud_player_type_guide.html
│       │   ├── import_db.py
│       │   ├── legal.py
│       │   ├── plo_equity_vs_random.py
│       │   ├── poker_sites.py
│       │   ├── regenerate_hand_strength_json.py
│       │   ├── reset_db.py
│       │   ├── settings.py
│       │   ├── tools.py
│       │   └── withdrawal.py
│       ├── static/
│       │   ├── assets/
│       │   ├── css/
│       │   │   └── _styles.css
│       │   ├── images/
│       │   └── js/
│       │       ├── card_utils.js
│       │       ├── chart_utils.js
│       │       └── scripts.js
│       └── templates/
│           ├── __init__.py
│           ├── articles/
│           ├── auth/
│           ├── bankroll/
│           ├── charts/
│           ├── confirmations/
│           ├── core/
│           ├── info/
│           ├── legal/
│           ├── partials/
│           ├── quiz/
│           ├── settings/
│           └── tools/
└── tests/
    └── ... (Pytest test files)
```

## Production Environment Project Structure

- The structure for the Production Environment is the same as for the Development Environment except that the top level path is /home/pythonpydev/total_bankroll

## Difference between Production and Development

### Database Configuration

- MySQL username for development is root, MySQL username for production is pythonpydev

- Production database name is pythonpydev$bankroll

- Development database name is bankroll.

- The differences are set out in the .env file:
  
  - **Development Database Credentials**
  
  - DEV_DBHOST="localhost"
    DEV_DB_NAME="bankroll"
    DEV_DB_USER="root"

- **Production Database Credentials**

- DB_HOST_PROD="pythonpydev.mysql.pythonanywhere-services.com"
  DB_NAME_PROD="pythonpydev$bankroll"
  DB_USER_PROD="pythonpydev"

- In the development environment in .env, FLASK_ENV=development whereas in the production environment FLASK_ENV=production

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

## # Deployment Workflow for Database Changes

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

## Core Application Logic

This section details the business logic behind some of the application's key features.

### Tournament Stake Recommendations

The logic for calculating tournament stake recommendations is handled by the `get_tournament_recommendation_data` method in `src/total_bankroll/recommendations.py`. It follows these steps:

1. **Calculate the "Ideal" Average Buy-in**:
   
   * First, it determines a "buy-in multiple" based on the user's selections (Game Type, Skill Level, Risk Tolerance). This multiple, which represents how many buy-ins a user should have in their bankroll (e.g., 100 for aggressive, 200 for conservative), is calculated from rules defined in `src/total_bankroll/data/recommendation_logic.json`.
   * It then calculates the user's ideal average buy-in by dividing their total bankroll by this multiple: `ideal_buy_in = total_bankroll / buy_in_multiple`.

2. **Find the Closest Standard Stake**:
   
   * The system compares the "ideal" buy-in against a list of standard tournament buy-ins available on poker sites.
   * It iterates backward from the highest stake to find the first one that is less than or equal to the user's ideal average buy-in. This becomes the "recommended stake".

3. **Generate "Move Up" and "Move Down" Messages**:
   
   * **Move Up**: The system calculates the bankroll required to play the next highest stake (e.g., $11 if the recommended is $5.50). It then informs the user exactly how much more money they need to accumulate to safely play at that level.
   * **Move Down**: To help with risk management, the system calculates the minimum bankroll required for the *current* recommended stake. It then shows the user how much they can afford to lose before they should drop down to the next lowest stake to protect their bankroll.

4. **Handle Edge Cases**:
   
   * If a user's bankroll is too small for even the lowest available stakes, the system provides a clear explanation and calculates the amount needed to start playing, giving the user their first concrete goal.

In summary, the tournament recommendation engine provides a holistic view: it tells you what you can play **today**, what you need to do to **move up**, and how much you can risk before you need to **move down**.

### Cash Game Stake Recommendations

The logic for cash game recommendations is handled by the `get_cash_game_recommendation_data` method in `src/total_bankroll/recommendations.py`. It's designed to find the highest stake a user can comfortably play while providing clear guidance on bankroll progression.

1. **Calculate a Personalized "Buy-in Multiple"**:
   
   * The function first calls `_calculate_weighted_range` to get a personalized `buy_in_multiple` based on the user's selections. For cash games, this multiple represents the number of maximum buy-ins a user should have in their bankroll (e.g., 75).

2. **Find the Highest Playable Stake**:
   
   * It iterates *backwards* through the list of available cash game stakes (from highest to lowest).
   * For each stake, it calculates the required bankroll: `required_bankroll = max_buy_in * buy_in_multiple`.
   * The first stake it finds where the user's `total_bankroll` is greater than or equal to the `required_bankroll` is set as the recommended stake. Because the loop is backwards, this is guaranteed to be the highest stake they are properly bankrolled for.

3. **Generate "Move Up" and "Move Down" Messages**:
   
   * **Move Up**: If the recommended stake isn't the highest available, the system calculates the bankroll needed for the next stake up and tells the user how much more they need to accumulate.
   * **Move Down (Stop-Loss)**: This is a key risk management feature. It calculates a "stop-loss" threshold for the current recommended stake, based on the stake's *minimum* buy-in (`move_down_threshold = buy_in_multiple * current_min_buy_in`). It then tells the user the exact amount they can lose before they should move down to the next lowest stake to protect their bankroll.

4. **Handle Edge Cases**:
   
   * If the user's bankroll is too small for even the lowest available stakes, the system sets the recommendation to "Below Smallest Stakes" and provides a clear explanation of how much more money is needed to start playing.

### The `_calculate_weighted_range` Function

The `_calculate_weighted_range` function in `src/total_bankroll/recommendations.py` is the intelligent core of the recommendation engine. It creates a personalized bankroll rule for a user by blending their preferences, rather than just applying a single, rigid rule.

#### How It Works

The function's logic is driven by `src/total_bankroll/data/recommendation_logic.json`, which defines two key things:

1. **`weights`**: The importance of each user selection (e.g., `risk_tolerance` has a higher weight than `game_environment`).
2. **`ranges`**: The base "rules" for each selection (e.g., a conservative tournament player should have 100-200 buy-ins).

The calculation follows these steps:

1. **Initialize Sums**: It starts with `total_weight`, `weighted_low_sum`, and `weighted_high_sum` at zero.
2. **Iterate Through Selections**: For each user preference (like "Conservative" risk tolerance), it retrieves the corresponding weight and range from the JSON file.
3. **Calculate Weighted Sums**: It multiplies the low and high ends of the range by the selection's weight and adds them to the running totals.
4. **Calculate Final Averages**: After processing all selections, it divides the `weighted_low_sum` and `weighted_high_sum` by the `total_weight` to get a final, custom range (e.g., 98 to 192 buy-ins).
5. **Calculate Average Multiple**: It finds the midpoint of this new custom range (e.g., 145). This single number is what the cash game and tournament recommendation functions use to calculate the required bankroll for a given stake.

This process creates a nuanced, personalized bankroll management rule based on a user's specific context, making the application's advice far more relevant and useful.

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

# Possible New Features

### User Experience & Interface (UI/UX)

1. **The Ultimate Dashboard:** If a user could only see one page, what would it be? Design a new, more interactive dashboard that gives a complete, at-a-glance summary of a player's entire poker world: current bankroll, recent performance, upcoming goals, and a key strategy tip for the day.
2. **Gamify the Grind:** How can you make tracking a bankroll feel less like a chore and more like a game? Brainstorm a system of achievements, badges, or streaks for consistent tracking, reaching new bankroll milestones, or studying articles.
3. **Mobile-First Data Entry:** Redesign the forms for adding a new session, deposit, or withdrawal specifically for a mobile device. How can you make it possible to log a session in under 30 seconds from a phone?
4. **Personalized Themes:** Implement a "dark mode" and potentially other color themes. Allow users to customize the look and feel of their dashboard to make it their own.

### Core Feature Enhancements

5. **Advanced Session Tracking:** Go beyond simple deposits and drawings. Create a dedicated "Session" model where users can track individual playing sessions, including date, duration, game type (e.g., NLHE Cash, PLO MTT), stakes, location/site, and profit/loss. This would unlock much deeper analysis.
6. **Smarter Charts:** The current charts are great, but what's next? Add new charting options like "Profit by Game Type," "Hourly Rate Over Time," or "Performance by Day of the Week." Allow users to compare different time periods on the same graph.
7. **Goal Setting & Tracking:** Add a "Goals" feature. Let users set specific, measurable targets like "Reach a $10,000 bankroll by December" or "Play 100 tournaments this month." Visualize their progress towards these goals on the dashboard.
8. **Tagging & Filtering:** Implement a tagging system for all transactions and sessions. Users could add tags like `#studying`, `#shot-taking`, `#live`, or `#deep-run`. This would allow for powerful filtering and analysis of their results based on context.

### New Poker Tools & Features

9. **Hand History Reviewer:** Create a tool where users can paste a hand history from a poker site. The tool could parse the hand, display it visually, and allow the user to add notes or even share it with a unique link for discussion.
10. **Variance Simulator:** Build a tool that takes a user's estimated win rate and standard deviation and runs a simulation to show the wild swings a bankroll can take. This is an incredibly powerful tool for teaching the reality of variance.
11. **ICM Calculator:** For your tournament players, add an "Independent Chip Model (ICM)" calculator to help them make correct decisions in the late stages of a tournament, especially when it comes to final table deals.
12. **Live Poker Tracker:** Develop a simple "live session" mode. When a user starts playing a live game, they can hit a "Start" button. The app would track the duration, and they could quickly add their buy-ins and cash-out amount at the end to automatically calculate their results and hourly rate.

### Content & Community

13. **Interactive Quizzes:** Turn your strategy articles into interactive learning experiences. At the end of an article on SPR, for example, present the user with a few quiz scenarios to test their understanding.
14. **User-Generated Content:** How could you allow trusted users to contribute? Perhaps a simple forum, a comment section on articles for discussion, or even a way for users to submit their own hands for public review.
15. **The Mental Game:** The technical side of poker is covered, but what about the psychological side? Create a new content section dedicated to the "Mental Game," with articles and tools related to tilt control, motivation, focus, and dealing with downswings.