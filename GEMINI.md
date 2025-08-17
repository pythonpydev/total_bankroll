# Total Bankroll Application

## Purpose

Keeps a track of total poker bankroll, including funds on each site, cash and other assets.

## Requirements

- Store amount of money on each poker site
- Some poker sites use different currencies.
- Add up total amount of money on each poker site
- Store amount of money saved in each asset type
- Add up total amount of non-poker assets
- Store each withdrawal transaction
- Add up total amount of withdrawals
- Store each deposit transaction
- Add up total amount of deposits.
- When withdrawals are made, as well as the date and time of the transaction,
the current total profit also needs to be recorded.
- Calculate total bankroll
- Total bankroll = money on poker sites + assets
- Calculate total profit
- Total profit = total bankroll - deposits + withdrawals
- Users cannot withdraw more money than their net worth
- Keep a history of all values saved over time
- Display latest changes in poker site funds, assets (current value - previous)
- All financial values should be stored on the database in US dollars $.
- Make available reports on historical data

## Interface

- A python flask web application, using HTML forms to input data.
- Use bootstrap to format the web pages.
- Use this example theme /home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/resources/
- The menu bar at the top should have the following links: Bankroll, Poker Sites, Assets, Withdrawal, Deposit, Currencies, About
- When entering values monetary values for poker sites and assets, there should
be a drop down box for the currency.
- Currencies should be selected from a drop down box.  The default currency is
US dollars $.
- Use numeric up down boxes to obtain numeric values to improve validation.
- Display positive changes in poker site funds and assets as light green, and
negative amounts as light red.
- When displaying a list of currencies in a drop down box, the default should
US dollars, the second highest option the UK pound and the third highest option
the Euro.  After that, display the currencies in alphabetical order.
- There should be a charts page which should have the following options for the
user:
    - Value of amount on poker sites over time
        - This should be a line graph showing the amount of money in $ on 
        different poker sites over time on the same axis.
    - Value of amount of assets over time
    - Value of bankroll over time
    - Profit over time
    - Value of withdrawals over time
    - Value of deposits over time

## Database

- Use MySQL to implement the database

### Database Schema

CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS drawings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    withdrawn_at REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    deposited_at REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS currency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rate REAL NOT NULL,
    code TEXT NOT NULL,
    symbol TEXT NOT NULL
);

## File locations

- Source code is located in /home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/src/total_bankroll/

### Project folder structure

```
/home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/
├── .aider.chat.history.md
├── .aider.input.history
├── .flake8
├── .gitignore
├── bankroll.db
├── GEMINI.md
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
├── .github/
│   └── workflows/
│       └── python-ci.yml
├── resources/
│   └── bootstrap/
│       └── index.html
├── src/
│   ├── __init__.py
│   └── total_bankroll/
│       ├── __init__.py
│       ├── app.py
│       ├── currency.py
│       ├── db.py
│       ├── schema_postgres.sql
│       ├── schema.sql
│       ├── site.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── add_asset.py
│       │   ├── add_deposit.py
│       │   ├── add_poker_site.py
│       │   ├── add_withdrawal.py
│       │   ├── assets.py
│       │   ├── deposit.py
│       │   ├── home.py
│       │   ├── poker_sites.py
│       │   ├── settings.py
│       │   ├── update_asset.py
│       │   ├── update_poker_site.py
│       │   └── withdrawal.py
│       ├── static/
│       │   ├── index.html
│       │   ├── assets/
│       │   │   ├── favicon.ico
│       │   │   └── img/
│       │   │       ├── bg-masthead.jpg
│       │   │       └── portfolio/
│       │   │           ├── fullsize/
│       │   │           │   ├── 1.jpg
│       │   │           │   ├── 2.jpg
│       │   │           │   ├── 3.jpg
│       │   │           │   ├── 4.jpg
│       │   │           │   ├── 5.jpg
│       │   │           │   └── 6.jpg
│       │   │           └── thumbnails/
│       │   │               ├── 1.jpg
│       │   │               ├── 2.jpg
│       │   │               ├── 3.jpg
│       │   │               ├── 4.jpg
│       │   │               ├── 5.jpg
│       │   │               └── 6.jpg
│       │   ├── css/
│       │   │   └── styles.css
│       │   └── js/
│       │       └── scripts.js
│       └── templates/
│           ├── about.html
│           ├── add_asset.html
│           ├── add_deposit.html
│           ├── add_site.html
│           ├── add_withdrawal.html
│           ├── assets.html
│           ├── base.html
│           ├── confirm_delete.html
│           ├── confirm_reset_database.html
│           ├── currencies.html
│           ├── deposit.html
│           ├── index.html
│           ├── poker_sites.html
│           ├── settings.html
│           ├── update_asset.html
│           ├── update_deposit.html
│           ├── update_site.html
│           ├── update_withdrawal.html
│           └── withdrawal.html
└── tests/
    ├── test_basic.py
    └── test_forms.py
```

### Explanation of file structure

The project is a standard Flask web application. The main application logic is in `src/total_bankroll/app.py`. This file also defines the routes and starts the Flask development server.

The `src/total_bankroll/routes` directory contains the blueprints for the different sections of the application. Each file in this directory corresponds to a feature of the application, such as adding a new poker site or viewing the list of assets. This is a good practice as it keeps the code organized and modular.

The `src/total_bankroll/templates` directory contains the HTML templates for the application. These templates are rendered by Flask and sent to the user's browser. The use of a `base.html` template is a good practice as it allows for a consistent layout across all pages.

The `src/total_bankroll/static` directory contains the static assets for the application, such as CSS, JavaScript, and images. These files are served directly by the web server and are not processed by Flask.

The `tests` directory contains the tests for the application. The tests are written using the `pytest` framework. This is a good practice as it helps to ensure the quality of the code.

The `resources` directory contains a bootstrap theme that is used as a base for the application's UI.

The project also has a `.github/workflows` directory, which contains a `python-ci.yml` file. This file defines a GitHub Actions workflow that runs the tests automatically whenever code is pushed to the repository. This is a great practice for continuous integration.

Overall, the project is well-structured and follows best practices for Flask application development.

Possible future refinements, efficiencies and refactoring:

*   **Configuration Management**: The secret key is generated randomly every time the app starts. This will invalidate sessions on every restart. It would be better to use a configuration file (e.g., `config.py` or environment variables) to store the secret key and other configuration values.
*   **Database Migrations**: The project uses SQL scripts to create the database schema. As the application evolves, managing database schema changes can become complex. Using a database migration tool like Alembic would help to manage schema changes in a more structured way.
*   **Blueprints Refactoring**: The `routes` directory is a good start, but as the application grows, it might be beneficial to group related routes into more specific blueprints. For example, all routes related to poker sites could be in a `poker_sites` blueprint, and all routes related to assets could be in an `assets` blueprint. This is already partially done, but could be more consistent.
*   **Frontend Asset Management**: The static assets are currently managed manually. Using a tool like Webpack or Parcel could help to bundle and minify the assets, which would improve the application's performance.
*   **API**: The application is a traditional web application that renders HTML on the server. As the application grows, it might be beneficial to expose a RESTful API that can be consumed by a frontend framework like React or Vue.js. This would allow for a more interactive user experience.
*   **Database Connection Handling**: The database connection is opened and closed in each route. It would be more efficient to use Flask's application context to manage the database connection. This is already done with `app.teardown_appcontext(close_db)`, but the connection is still opened manually in each route. The `get_db` function should handle the connection opening and reuse it if it's already open in the current context.
## Running the Application

To run the Flask application, follow these steps:

1.  **Navigate to the project's root directory** in your terminal:
    ```bash
    cd /home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/
    ```

2.  **Ensure Python Dependencies are Installed**:
    If you haven't already, install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**:
    The application uses environment variables for sensitive information and configuration. These are loaded from a `.env` file in the project root.

    *   **Create/Edit your `.env` file**: In the root of your project (`/home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/.env`), ensure it contains the following, replacing placeholder values with your actual credentials:

        ```
        # .env file for total_bankroll project

        FLASK_APP=total_bankroll.app
        FLASK_ENV=development

        # Flask Secret Key (for session management)
        SECRET_KEY="YOUR_FLASK_SECRET_KEY"

        # Exchange Rate API Key (from exchangerate-api.com)
        EXCHANGE_RATE_API_KEY="YOUR_EXCHANGERATE_API_KEY"

        # PostgreSQL Database Credentials
        DB_HOST="localhost"
        DB_NAME="bankroll"
        DB_USER="efb"
        DB_PASS="post123!"
        ```
        *   **Generating `SECRET_KEY`**: You can generate a strong, random `SECRET_KEY` by running `python -c "import os; print(os.urandom(24).hex())"` in your terminal and pasting the output.
        *   **`EXCHANGE_RATE_API_KEY`**: Obtain this from [https://www.exchangerate-api.com/](https://www.exchangerate-api.com/).

4.  **Set `PYTHONPATH` (Linux/macOS)**:
    This environment variable tells Python where to find your application's modules. You need to set this in your terminal session *before* running the app.

    ```bash
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src
    ```
    *   **Note**: This command needs to be run in each new terminal session. For persistence, you can add it to your shell's startup file (e.g., `~/.bashrc` or `~/.zshrc`).

5.  **Run the Flask Application**:
    From the project's root directory, execute the following command:

    ```bash
    python -m flask run
    ```

    This will start the Flask development server, typically accessible at `http://127.0.0.1:5000/`.
