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
- All financial values should be stored on the database in the original currency
the record was added in.
- Total on all site, total assets, total withdrawals, total deposits, total
bankroll and total profits should be shown in USD $.
- Make available reports on historical data
    - poker sites charts
        - line chart with historical amounts in $ for each poker site
        - bar chart with historical amounts in $ for each poker site
        - pie chart with only the latest amounts in $ for each poker site
        - polar area chart with only the latest amounts in $ for each poker site
        - radar chart with only the latest amounts in $ for each poker site
        - scatter chart with historical amounts in $ for each poker site
    - asset charts
        - line chart with historical amounts in $ for each asset
        - bar chart with historical amounts in $ for each asset
        - pie chart with only the latest amounts in $ for each asset
        - polar area chart with only the latest amounts in $ for each asset
        - radar chart with only the latest amounts in $ for each asset
        - scatter chart with historical amounts in $ for each asset
    - bankroll chart
        - line chart with historical amounts in $ for total bankroll
        - bar chart with historical amounts in $ for total bankroll
    - profit chart
        - line chart with historical amounts in $ for total profit
        - bar chart with historical amounts in $ for total profit
    - withdrawals chart
        - line chart with cumulative amounts over time in $ for withdrawals
        - bar chart with historical amounts in $ for withdrawals
    - deposits chart
        - line chart with cumulative deposit amounts over time in $ for deposits
        - bar chart with historical amounts in $ for deposits
- Users should have to log into the site before being able to access it fully.


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
user.

## Database

- Use MySQL to implement the database

### Database Schema

```sql
-- phpMyAdmin SQL Dump
-- version 5.2.1deb3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 20, 2025 at 02:21 PM
-- Server version: 8.0.43-0ubuntu0.24.04.1
-- PHP Version: 8.3.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `bankroll`
--

-- --------------------------------------------------------

--
-- Table structure for table `assets`
--

CREATE TABLE `assets` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `last_updated` datetime NOT NULL,
  `currency` varchar(255) NOT NULL DEFAULT 'Dollar',
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `asset_history`
--

CREATE TABLE `asset_history` (
  `id` int NOT NULL,
  `asset_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `currency` varchar(255) NOT NULL,
  `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `currency`
--

CREATE TABLE `currency` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `rate` decimal(10,6) NOT NULL,
  `code` varchar(3) NOT NULL,
  `symbol` varchar(5) NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `deposits`
--

CREATE TABLE `deposits` (
  `id` int NOT NULL,
  `date` datetime NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `deposited_at` decimal(10,2) NOT NULL,
  `last_updated` datetime NOT NULL,
  `currency` varchar(255) NOT NULL DEFAULT 'Dollar',
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `drawings`
--

CREATE TABLE `drawings` (
  `id` int NOT NULL,
  `date` datetime NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `withdrawn_at` decimal(10,2) NOT NULL,
  `last_updated` datetime NOT NULL,
  `currency` varchar(255) NOT NULL DEFAULT 'Dollar',
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `oauth`
--

CREATE TABLE `oauth` (
  `id` int NOT NULL,
  `provider` varchar(50) NOT NULL,
  `provider_user_id` varchar(255) NOT NULL,
  `token` text NOT NULL,
  `user_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sites`
--

CREATE TABLE `sites` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `last_updated` datetime NOT NULL,
  `currency` varchar(255) NOT NULL DEFAULT 'Dollar',
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `site_history`
--

CREATE TABLE `site_history` (
  `id` int NOT NULL,
  `site_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `currency` varchar(255) NOT NULL,
  `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login_at` timestamp NULL DEFAULT NULL,
  `fs_uniquifier` varchar(255) NOT NULL,
  `is_confirmed` tinyint(1) NOT NULL DEFAULT '0',
  `confirmed_on` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `assets`
--
ALTER TABLE `assets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `asset_history`
--
ALTER TABLE `asset_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `asset_id` (`asset_id`);

--
-- Indexes for table `currency`
--
ALTER TABLE `currency`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `deposits`
--
ALTER TABLE `deposits`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `drawings`
--
ALTER TABLE `drawings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `oauth`
--
ALTER TABLE `oauth`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `sites`
--
ALTER TABLE `sites`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `site_history`
--
ALTER TABLE `site_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `site_id` (`site_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `fs_uniquifier` (`fs_uniquifier`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `assets`
--
ALTER TABLE `assets`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `asset_history`
--
ALTER TABLE `asset_history`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `currency`
--
ALTER TABLE `currency`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `deposits`
--
ALTER TABLE `deposits`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `drawings`
--
ALTER TABLE `drawings`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `oauth`
--
ALTER TABLE `oauth`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sites`
--
ALTER TABLE `sites`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `site_history`
--
ALTER TABLE `site_history`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `assets`
--
ALTER TABLE `assets`
  ADD CONSTRAINT `assets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `asset_history`
--
ALTER TABLE `asset_history`
  ADD CONSTRAINT `asset_history_ibfk_1` FOREIGN KEY (`asset_id`) REFERENCES `assets` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `deposits`
--
ALTER TABLE `deposits`
  ADD CONSTRAINT `deposits_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `drawings`
--
ALTER TABLE `drawings`
  ADD CONSTRAINT `drawings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `oauth`
--
ALTER TABLE `oauth`
  ADD CONSTRAINT `oauth_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `sites`
--
ALTER TABLE `sites`
  ADD CONSTRAINT `sites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `site_history`
--
ALTER TABLE `site_history`
  ADD CONSTRAINT `site_history_ibfk_1` FOREIGN KEY (`site_id`) REFERENCES `sites` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
```


## File locations

- Source code is located in /home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/src/total_bankroll/

### Project folder structure

```
/home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/
├── _clone/
├── .aider.tags.cache.v4
├── .git/
├── .github/
├── .pytest_cache/
├── .venv/
├── info/
├── resources/
├── src/
├── tests/
├── .env
├── .flake8
├── .gitignore
├── bankroll.sql
├── env.txt
├── GEMINI.md
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
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



## Analysis of Project

### Strengths:

   1. Clear Purpose and Requirements: Well-defined application goals and
      functional needs.
   2. Modular Design (Blueprints): Effective use of Flask Blueprints for
      organized code.
   3. Consistent UI Layout: base.html ensures a uniform user interface.
   4. Separation of Concerns (Static Assets): Static files are logically
      separated for efficient serving.
   5. Automated Testing: pytest integration indicates a focus on code
      quality.
   6. Continuous Integration (GitHub Actions): Automated testing via GitHub
      Actions promotes robust development.
   7. Database Schema Defined: Clear database structure for data management.
   8. Currency Conversion Handling: Supports multiple currencies with USD
      conversion for totals.
   9. Detailed Running Instructions: Comprehensive setup and execution guide
      in GEMINI.md.
   10. Comprehensive Charting Requirements: Detailed visualization needs for
        enhanced user insights.

### Areas for Improvement:

   1. Configuration Management: SECRET_KEY should be persistently stored,
      not randomly generated. [COMPLETED]
   2. Database Migrations: Implement a tool like Alembic for structured
      schema evolution.
   3. Database Connection Handling: Optimize get_db to reuse connections
      within the application context.
   4. Frontend Asset Management: Utilize tools (Webpack/Parcel) for
      bundling and minification.
   5. API Exposure: Consider a RESTful API for more interactive frontends.
   6. Error Handling (User Experience): Improve error feedback with
      user-friendly pages or flash messages.
   7. Input Validation (Server-Side): Enhance server-side validation for
      increased robustness.
   8. Logging: Implement a structured logging system for better debugging
      and monitoring.
   9. Dependency Management: Pin exact versions in requirements.txt for
      consistency.
   10. User Authentication/Authorization: Crucial security feature for a
       financial application.

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