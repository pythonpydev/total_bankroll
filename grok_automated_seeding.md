To automate the seeding of the MySQL database on PythonAnywhere with articles from Markdown files in `/home/ed/MEGA/total_bankroll/resources/articles/markdown` using the provided `seed_articles.py` script, you can set up a scheduled task on PythonAnywhere. This ensures the script runs automatically at a specified interval (e.g., daily, weekly, or one-time) without manual intervention. Since you’ve already seeded the articles locally and encountered the `Table 'bankroll.article' doesn't exist` error on PythonAnywhere, I’ll assume the database schema issue has been resolved (as outlined previously) by applying migrations (`flask db upgrade`). Below, I’ll guide you through automating the seeding process, ensuring the `articles` table exists, and scheduling the task on PythonAnywhere.

---

### Prerequisites
1. **Database Schema**: The `articles` table must exist in the `ed$bankroll` database. If not, apply migrations (see Step 1 below).
2. **Markdown Files**: Ensure Markdown files are in `/home/ed/MEGA/total_bankroll/resources/articles/markdown` on PythonAnywhere.
3. **Dependencies**: All required packages (`flask`, `flask-sqlalchemy`, `flask-migrate`, `pymysql`, `markdown`, `bleach`, `beautifulsoup4`) are installed in the virtual environment.
4. **Script**: The `seed_articles.py` script (provided) is in `/home/ed/MEGA/total_bankroll/src/total_bankroll/` and works correctly when run manually.

---

### Step 1: Ensure Database Schema
The previous error (`Table 'bankroll.article' doesn't exist`) indicates the `articles` table is missing. Apply migrations to create it:

1. **Open a Bash Console** on PythonAnywhere:
   - Go to the “Consoles” tab and start a new Bash console.

2. **Activate Virtual Environment**:
   ```bash
   source /home/ed/MEGA/total_bankroll/.venv/bin/activate
   ```

3. **Navigate to Project Directory**:
   ```bash
   cd /home/ed/MEGA/total_bankroll/src/total_bankroll
   ```

4. **Apply Migrations**:
   ```bash
   flask db migrate -m "Add articles table"
   flask db upgrade
   ```

5. **Verify Table**:
   - Open a MySQL console (from the “Databases” tab):
     ```sql
     USE ed$bankroll;
     SHOW TABLES;
     ```
   - Confirm `articles` is listed. If not, check `config.py` for the correct `SQLALCHEMY_DATABASE_URI`:
     ```python
     class ProductionConfig:
         SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ed:<your-mysql-password>@ed.mysql.pythonanywhere-services.com/ed$bankroll'
         SQLALCHEMY_TRACK_MODIFICATIONS = False
     ```

---

### Step 2: Verify Markdown Files
Ensure the Markdown files are in `/home/ed/MEGA/total_bankroll/resources/articles/markdown`:
```bash
ls /home/ed/MEGA/total_bankroll/resources/articles/markdown
```
- If missing, upload them from your local machine:
  ```bash
  # From local machine
  scp -r resources/articles/markdown ed@ssh.pythonanywhere.com:/home/ed/MEGA/total_bankroll/resources/articles/
  ```
- Set permissions:
  ```bash
  chmod -R 644 /home/ed/MEGA/total_bankroll/resources/articles/markdown
  ```

---

### Step 3: Test `seed_articles.py` Manually
Before automating, test the script to ensure it works:
```bash
cd /home/ed/MEGA/total_bankroll/src/total_bankroll
source /home/ed/MEGA/total_bankroll/.venv/bin/activate
python3 seed_articles.py
```
- **Expected Output**: `Articles seeded successfully`.
- **If It Fails**:
  - Check for `Table 'bankroll.article' doesn't exist` (re-run migrations).
  - Verify the directory path in `seed_articles.py` (`resources/articles/markdown` is relative to the script’s directory).

---

### Step 4: Create a Scheduled Task on PythonAnywhere
PythonAnywhere allows scheduling tasks via the “Tasks” tab. Since `seed_articles.py` is designed to run in the Flask app context, we’ll create a wrapper script to handle the virtual environment and app context, then schedule it.

1. **Create a Wrapper Script**:
   Create `/home/ed/MEGA/total_bankroll/run_seed_articles.sh` to activate the virtual environment and run `seed_articles.py`:
   ```bash
   #!/bin/bash
   source /home/ed/MEGA/total_bankroll/.venv/bin/activate
   cd /home/ed/MEGA/total_bankroll/src/total_bankroll
   python3 seed_articles.py
   ```

   - Save the script:
     ```bash
     nano /home/ed/MEGA/total_bankroll/run_seed_articles.sh
     ```
     Paste the above content, save, and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).
   - Make it executable:
     ```bash
     chmod +x /home/ed/MEGA/total_bankroll/run_seed_articles.sh
     ```

2. **Test the Wrapper Script**:
   ```bash
   /home/ed/MEGA/total_bankroll/run_seed_articles.sh
   ```
   - Check for `Articles seeded successfully`. If it fails, debug as in Step 3.

3. **Schedule the Task**:
   - Go to PythonAnywhere’s “Tasks” tab.
   - Click “Add a new scheduled task”.
   - **Command**: `/home/ed/MEGA/total_bankroll/run_seed_articles.sh`
   - **Schedule**:
     - For one-time seeding, choose a near-future time (e.g., 10 minutes from now, like 17:15 BST on Oct 21, 2025).
     - For recurring seeding (e.g., to check for new Markdown files daily), set to “Daily” at a specific time (e.g., 00:00).
   - Save the task.

4. **Monitor Logs**:
   - After the task runs, check the log in the “Tasks” tab or at `/var/log/<your-username>.pythonanywhere.com.<task-id>.log`.
   - Look for `Articles seeded successfully` or errors.

---

### Step 5: Prevent Duplicate Articles
The current `seed_articles.py` creates a new `Article` for each Markdown file without checking for duplicates, which could result in multiple entries for the same file if run repeatedly. Modify `seed_articles.py` to skip existing articles based on `title` or `content_md`:

<xaiArtifact artifact_id="90502dbf-06c5-45c6-bfda-b466b8e4dc2a" artifact_version_id="a939d66c-092a-451e-98d6-935ccf463b51" title="seed_articles.py" contentType="text/python">
import os
from total_bankroll import create_app, db
from total_bankroll.models import Article
from datetime import datetime, UTC

def seed_articles(app, md_directory):
    with app.app_context():
        if not os.path.exists(md_directory):
            print(f"Error: Directory {md_directory} does not exist")
            return
        for filename in os.listdir(md_directory):
            if filename.endswith('.md'):
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    content_md = f.read()
                    title = filename.replace('.md', '').replace('-', ' ').title()
                    # Check if article already exists
                    existing_article = Article.query.filter_by(title=title).first()
                    if existing_article:
                        print(f"Skipping existing article: {title}")
                        continue
                    article = Article(
                        title=title,
                        content_md=content_md,
                        date_published=datetime.now(UTC)
                    )
                    db.session.add(article)
        db.session.commit()
        print("Articles seeded successfully")

if __name__ == '__main__':
    app = create_app(config_name='production')
    md_dir = 'resources/articles/markdown'
    seed_articles(app, md_dir)
</xaiArtifact>

- **Changes**:
  - Added check for existing articles using `Article.query.filter_by(title=title).first()`.
  - Skips seeding if an article with the same title exists to prevent duplicates.
- **Upload**:
  ```bash
  # From local machine
  scp seed_articles.py ed@ssh.pythonanywhere.com:/home/ed/MEGA/total_bankroll/src/total_bankroll/
  ```
  ```bash
  chmod 644 /home/ed/MEGA/total_bankroll/src/total_bankroll/seed_articles.py
  ```

---

### Step 6: Test Automation
1. **Run Manually First**:
   ```bash
   /home/ed/MEGA/total_bankroll/run_seed_articles.sh
   ```
2. **Check Database**:
   ```sql
   USE ed$bankroll;
   SELECT * FROM articles;
   ```
   Verify articles (e.g., “How to Use the Tags in PLO & What They Imply”) are present.
3. **Wait for Scheduled Task**:
   - If set to run soon, check the task log after the scheduled time.
   - Visit `https://<your-username>.pythonanywhere.com/strategy/articles/` to confirm articles render with styled tables and poker hands.
4. **Debug**:
   - **Table Not Found**: Re-run migrations.
   - **No Articles**: Check task log for errors (e.g., directory not found, database connection issues).
   - **Table Styling**: Ensure `_styles.css` includes table styles (as provided previously).

---

### Example Scheduled Task
Here’s the Task Schedule for a one-time run to seed articles:
```xaitask
{
  "name": "Seed Articles",
  "prompt": "Run the seed_articles.py script to populate the MySQL database with articles from /home/ed/MEGA/total_bankroll/resources/articles/markdown",
  "cadence": "once",
  "time_of_day": "17:15",
  "day_of_week": 1,
  "day_of_month": 1,
  "day_of_year": 1
}
```
- **Note**: PythonAnywhere’s task scheduler uses the command and time set in the “Tasks” tab, not this `xaitask` format. The above is for reference to confirm intent (one-time run at 17:15 BST).

---

### Why This Works
- The wrapper script ensures the virtual environment and correct directory are used.
- The updated `seed_articles.py` prevents duplicate entries.
- Migrations create the `articles` table, resolving the previous error.
- The scheduled task automates execution, and logs help debug issues.

---

### Next Steps
1. **Apply Migrations** (if not done):
   ```bash
   source /home/ed/MEGA/total_bankroll/.venv/bin/activate
   cd /home/ed/MEGA/total_bankroll/src/total_bankroll
   flask db migrate -m "Add articles table"
   flask db upgrade
   ```
2. **Upload Files**:
   - Upload updated `seed_articles.py`.
   - Ensure Markdown files are in `/home/ed/MEGA/total_bankroll/resources/articles/markdown`.
3. **Schedule Task**:
   - Set up `/home/ed/MEGA/total_bankroll/run_seed_articles.sh` in the “Tasks” tab.
4. **Test**:
   - Run the wrapper script manually.
   - Check `https://<your-username>.pythonanywhere.com/strategy/articles/`.
5. **Feedback**:
   - Share task logs or screenshots if issues arise.
   - Specify if you want recurring seeding (e.g., daily to check for new files) or additional automation.

Let me know if you need help with any step or encounter errors!
