# Database on Development Environment vs Production Environment

The issue you're facing stems from how your application handles code versus database changes. Git effectively tracks and syncs your codebase (e.g., Python files, templates), which is why code modifications propagate smoothly from development to production via `git push` and `git pull`. However, databases are external to your codebase—they're separate MySQL instances (local in dev, hosted on PythonAnywhere in prod) with different connection details (usernames, database names, hosts), even though passwords are shared. Changes made directly to the development database (e.g., via a MySQL client, manual SQL queries, or even app-driven inserts/updates that alter schema or data) aren't captured in Git. As a result, pulling code doesn't automatically replicate those database changes to production.

### Why This Happens
- **Schema Changes**: If you alter tables, columns, indexes, etc., directly in the dev database (bypassing your app's models), these aren't versioned. Your app uses Flask-SQLAlchemy and Flask-Migrate (based on Alembic), which are designed to track schema changes through Python model definitions in `models.py`. Direct database tinkering bypasses this, leading to mismatches where prod doesn't get the updates.
- **Data Changes**: Inserted/updated data (e.g., new records in tables like users, deposits, or withdrawals) lives only in the dev database. Git doesn't track raw data, so it won't sync. If the data is user-generated or runtime-specific, it *shouldn't* be synced blindly anyway (to avoid overwriting prod data). But if it's seed/initial data (e.g., currencies, default settings), it can be managed via scripts.
- **Environment Separation**: Your `config.py` and `.env` files enforce separate databases, which is good for isolation (dev changes don't accidentally break prod). But this means manual replication is needed for DB consistency.
- **Potential Side Effects**: If schemas diverge, your app might crash in prod (e.g., querying a non-existent column) or produce inconsistent behavior. Data divergences could lead to missing records or duplicates.

### How to Prevent It
- **Treat Development as Source of Truth via Version Control**: Always channel database schema changes through your models and migrations. This way, changes are codified in Git-tracked files (e.g., migration scripts in `alembic/versions/` or equivalent—your app initializes `Migrate(app, db)` in `__init__.py`).
- **Avoid Direct Database Modifications**: Don't use tools like MySQL Workbench or raw SQL to alter the dev database. Instead, update your app's models and let migrations handle schema evolution.
- **Handle Data Separately**: For seed data, create repeatable scripts or Flask CLI commands (your app already has `commands.register_commands(app)`). For runtime data, accept that dev and prod will differ, or use dumps/imports sparingly (with backups).
- **Test Thoroughly**: After syncing, always test in prod to catch any discrepancies early.
- **Automation Tools**: Consider integrating CI/CD (e.g., GitHub Actions) to automate migration application on deploy, but that's advanced and not necessary yet.

### Procedure to Follow for Syncing Changes
Follow this step-by-step process whenever you make database-related changes in development. It assumes you're using Flask-Migrate for schema management (which your code supports). If you haven't initialized migrations yet, run `flask db init` in dev first to set up the `migrations/` folder.

#### 1. **Make Changes in Development**
   - Update your app's models (in `models.py`) for any schema changes (e.g., adding a column: `new_column = db.Column(db.String(255))`).
   - For data changes:
     - If it's seed/initial data, create a Flask CLI command (e.g., in `commands.py`) to insert it reproducibly, like your `init_currency_command`.
     - Avoid direct inserts; use the app's routes or admin interfaces if available.
   - Test locally: Run your app (`flask run` or via `__init__.py`) and verify changes.

#### 2. **Generate and Apply Migrations in Development**
   - In your dev terminal, navigate to the project root (`/path/to/total_bankroll/src`).
   - Ensure your `.env` is loaded (or use `env_development.txt` renamed to `.env`).
   - Run: `flask db migrate -m "Brief description of change"`
     This detects model changes and generates a migration script (e.g., in `migrations/versions/xxxx_brief_description.py`).
   - Review the script for accuracy (edit if needed, but rarely necessary).
   - Apply to dev DB: `flask db upgrade`
     This updates your local database schema.

#### 3. **Commit and Push Code Changes**
   - Stage all changes: `git add .` (includes updated models, migration scripts, etc.).
   - Commit: `git commit -m "Updated schema/data for [feature]; added migration"`
   - Push to GitHub: `git push origin main` (or your branch).

#### 4. **Pull Changes to Production**
   - Log into PythonAnywhere.
   - Open a Bash console (via the "Consoles" tab).
   - Navigate to your project directory: `cd /home/pythonpydev/total_bankroll/src`
   - Pull from GitHub: `git pull origin main`
   - Ensure your production `.env` is in place (based on `env_production.txt`, renamed to `.env` if needed).

#### 5. **Apply Migrations in Production**
   - In the same Bash console:
     - If using a virtualenv (check via `workon` or PythonAnywhere's virtualenv setup), activate it.
     - Set environment: `export FLASK_APP=total_bankroll` (if not already set).
     - Run: `flask db upgrade`
       This applies the new migration scripts to the prod database, replicating schema changes.
   - For data changes:
     - If using a seed command, run it (e.g., `flask init-currency` based on your `init_currency_command`).
     - If manual data replication is needed (rare—only for non-user data), export from dev and import to prod:
       - In dev: `mysqldump -u root -p"f3gWoQe7X7BFCm" --databases bankroll > dev_dump.sql`
       - Upload `dev_dump.sql` to PythonAnywhere (via Files tab).
       - In prod console: `mysql -u pythonpydev -p"f3gWoQe7X7BFCm" -h pythonpydev.mysql.pythonanywhere-services.com pythonpydev\$bankroll < dev_dump.sql`
         (Note: Escape the `$` in the DB name as `\$`; use cautiously to avoid overwriting prod data—backup first with `mysqldump`).

#### 6. **Reload the Application in Production**
   - In PythonAnywhere's "Web" tab, click "Reload" for your app to pick up changes.
   - Test: Access your site and verify the changes (e.g., new columns work, data is present if seeded).

#### 7. **Handle Rollbacks if Needed**
   - If issues arise, downgrade in prod: `flask db downgrade` (reverts the last migration).
   - Always backup databases before upgrades (use `mysqldump` as above).

By following this, your dev environment remains the source of truth, with all changes versioned in Git. If you're making frequent direct DB tweaks, refactor them into models/migrations to avoid future pain. If data syncing becomes a bigger issue, consider tools like database replication (advanced, not recommended for dev/prod separation) or staging environments. Let me know if you need code snippets for custom commands!
