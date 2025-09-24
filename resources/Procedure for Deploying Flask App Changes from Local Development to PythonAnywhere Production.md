### Procedure for Deploying Flask App Changes from Local Development to PythonAnywhere Production

Follow this step-by-step guide to ensure a smooth deployment. This assumes your local setup uses Git for version control, your Flask app is configured to read sensitive settings (e.g., database URI, secret keys) from environment variables (via .env locally and config.py if needed), and you're using SQLAlchemy for ORM. PythonAnywhere handles configuration via a WSGI file and environment variables in the web app dashboard, so we'll align with that. If you haven't set up database migrations yet, I'll include guidance to use Alembic (a common tool with SQLAlchemy for handling schema changes safely).

#### Preparation on Your Local Development Machine

1. **Verify Your Local App Works**: Run your Flask app locally (`flask run` or equivalent) and test all recent changes, including API endpoints, database interactions, and any new features. Ensure there are no errors in your console or logs.

2. **Update Dependencies**: 
   
   - Install any new libraries you've used (e.g., `pip install some-new-package`).
   - Generate an updated `requirements.txt` file: Run `pip freeze > requirements.txt` in your project directory. This captures all installed packages. Review the file to remove any unnecessary or local-only entries (e.g., development tools like pytest if not needed in production).

3. **Handle Configuration Differences**:
   
   - Ensure your Flask app loads configs from environment variables (e.g., using `os.environ.get('DATABASE_URL')` in your code instead of hardcoding).
   - If you're using a `.env` file locally (with python-dotenv), add it to `.gitignore` to avoid committing secrets.
   - Update your `config.py` (if used) to be environment-agnostic, perhaps with classes like `DevelopmentConfig` and `ProductionConfig` that inherit from a base and override via env vars.
   - Do not commit sensitive data (e.g., production DB credentials) to Git. You'll set these on PythonAnywhere later.

4. **Set Up Database Migrations (If Not Already Done)**:
   
   - If you haven't, install Alembic: `pip install alembic` (and add to requirements.txt).
   - Initialize Alembic in your project: Run `alembic init migrations` (this creates a `migrations` folder).
   - Configure `alembic.ini` to point to your SQLAlchemy engine (e.g., set `sqlalchemy.url` to your local DB URI temporarily).
   - In `migrations/env.py`, import your models and set `target_metadata = Base.metadata` (assuming your models use a declarative base).
   - Generate a migration for your current schema changes: `alembic revision --autogenerate -m "Description of changes"`.
   - Apply it locally: `alembic upgrade head` and test.

5. **Apply and Test DB Changes Locally**:
   
   - If using Alembic, run `alembic upgrade head`.
   - If not using migrations, export schema changes as SQL scripts (e.g., using `mysqldump --no-data` to get structure diffs, or manually write ALTER TABLE statements). Test them on a local DB backup.

6. **Commit Changes to Git**:
   
   - Stage all files: `git add .` (or selectively add changed files).
   - Commit: `git commit -m "Detailed commit message describing changes"`.
   - Ensure `.gitignore` excludes `.env`, virtualenv folders, `__pycache__`, etc.

7. **Push to GitHub**:
   
   - Push your branch: `git push origin main` (or your branch name). Verify the push succeeds and view changes on GitHub.

#### Deployment on PythonAnywhere

8. **Log In to PythonAnywhere**:
   
   - Go to your PythonAnywhere dashboard (pythonanywhere.com) and log in.
   - If your app isn't set up yet, create a new web app via the "Web" tab, selecting Flask and your Python version.

9. **Pull Changes from GitHub**:
   
   - Open a Bash console (under the "Consoles" tab).
   - Navigate to your project directory (usually `/home/yourusername/yourprojectname`).
   - If not already cloned, clone your repo: `git clone https://github.com/yourusername/yourrepo.git`.
   - Pull updates: `git pull origin main` (resolve any merge conflicts if they arise).

10. **Install Updated Dependencies**:
    
    - In the Bash console, activate your virtualenv if using one (e.g., `workon myenv` or `source venv/bin/activate`).
    - Install requirements: `pip install -r requirements.txt`. Watch for errors (e.g., missing system dependencies; PythonAnywhere has most common ones pre-installed, but you may need to install extras like `mysqlclient` via `pip`).

11. **Update Production Configuration**:
    
    - Edit your WSGI file (found in `/var/www/yourusername_pythonanywhere_com_wsgi.py` or via the "Web" tab > "WSGI configuration file").
      - Ensure it points to your Flask app (e.g., `from yourapp import app as application`).
      - Set any app-specific configs here if needed, but prefer environment variables for secrets.
    - In the "Web" tab > "Environment variables" section, add production-specific vars (e.g., `DATABASE_URL` as `mysql://yourusername:password@yourusername.mysql.pythonanywhere-services.com/yourusername$yourdb`).
    - Reload the web app (button in the "Web" tab) to apply WSGI changes.

12. **Apply Database Changes to Production**:
    
    - **Using Alembic (Recommended)**:
      - In the Bash console, navigate to your project dir.
      - Update `alembic.ini` or use env vars to set `sqlalchemy.url` to your production DB URI (e.g., export it temporarily: `export SQLALCHEMY_DATABASE_URI='mysql://...'`).
      - Run `alembic upgrade head`. This applies schema changes safely without data loss.
    - **Manual Method (If No Migrations)**:
      - Open the MySQL console (under "Databases" tab).
      - Run your SQL scripts (e.g., ALTER TABLE statements) to update the schema. Be cautious: Back up your production DB first via the "Databases" tab > "Backup" or using `mysqldump` in Bash.
      - Test queries to ensure the structure matches development.

13. **Test the Production App**:
    
    - Reload the web app in the "Web" tab.
    - Visit your site URL (e.g., yourusername.pythonanywhere.com) in a browser.
    - Test key features, especially those involving DB changes or new libraries. Check error logs in the "Web" tab > "Log files" if issues arise.

14. **Handle Any Issues**:
    
    - If configs mismatch: Double-check env vars and WSGI file.
    - DB connection errors: Verify credentials in env vars and ensure SQLAlchemy is configured to use them.
    - Dependency issues: Re-run `pip install` or check PythonAnywhere's help for pre-installed packages.
    - Rollback if needed: `git checkout previous-commit-hash` in Bash, then reload the app.

15. **Final Verification and Monitoring**:
    
    - Monitor logs for a few hours post-deployment.
    - If everything works, consider setting up automated backups or error tracking (PythonAnywhere has basic logging; integrate Sentry or similar if needed).

This procedure minimizes risks like config leaks, unmet dependencies, or unsynced DB schemas. If your app grows, consider CI/CD tools like GitHub Actions for automated testing before pushing. If you encounter specific errors, provide details for troubleshooting.
