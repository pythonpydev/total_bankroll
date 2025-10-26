Why Did the Previous Issues Happen?
You are correct. The issues were caused by changes to the database schema (the structure of your tables) and the difficulty of keeping three things perfectly synchronized:

Your application code (e.g., models.py).
Your local development database.
Your production database on PythonAnywhere.
When these fall out of sync, the migration tool (Flask-Migrate) gets confused, leading to the errors you saw. The key to avoiding this is a consistent, repeatable workflow.

The Reliable Deployment Procedure
Here is a step-by-step procedure you can follow every time you need to make a database change. This workflow ensures that you verify everything locally before touching your live production server, which is standard practice in software engineering.

Phase 1: On Your Local Development Machine
This is where you do all your work and testing.

Step 1: Make Your Code Changes This is what you're already doing. For example, you would add the display_order column to the Assets model in src/total_bankroll/models.py.

Step 2: Generate the Migration Script In your local terminal, run the migrate command. This tells Flask-Migrate to compare your updated models.py file with your local database and generate a new Python script in the migrations/versions/ folder that contains the necessary SQL commands.

bash
flask db migrate -m "A short, descriptive message for the change"
# Example:
# flask db migrate -m "Add display_order to Assets model"
Step 3: Apply the Migration Locally Run the upgrade command. This executes the script you just generated against your local database, applying the changes.

bash
flask db upgrade
Step 4: Test Your Application Locally Start your local Flask server (flask run) and thoroughly test the application. Make sure the new feature works as expected and that you haven't accidentally broken anything else. This is the most important step for preventing issues on your live site.

Step 5: Commit Everything to Git Once you are confident that everything works locally, commit both your application code changes and the new migration script to your git repository.

bash
 Show full code block
# Stage all your changes (including the new migration file)
git add .

# Commit them with a descriptive message
git commit -m "Add reordering feature for Assets page"

# Push the commit to your remote repository (e.g., GitHub)
git push
Phase 2: On the PythonAnywhere Production Server
Now that your new feature is tested and your code is in the repository, you can safely deploy it to production.

Step 1: Pull the Latest Code In your PythonAnywhere Bash console, navigate to your project directory and pull the changes you just pushed. This will bring down your new application code and, crucially, the new migration script.

bash
cd ~/total_bankroll
git pull
Step 2: Activate Environment and Set Variables Prepare your console session to run the Flask commands.

bash
workon bankroll_venv
export FLASK_APP="src/total_bankroll"
Step 3: Apply the Migration to the Production Database This is the key step on the server. Run the exact same upgrade command you ran locally. It will execute the same migration script you just pulled from git, but this time against your live production database.

bash
flask db upgrade
Because you have already tested this exact script on your local machine, the chance of it failing here is extremely low.

Step 4: Reload Your Web App The final step is to make your live application use the new code and database schema.

Go to the "Web" tab on your PythonAnywhere dashboard.
Click the big green "Reload www.stakeeasy.net" button.
Your new feature is now live! By following this procedure, you create a reliable and safe "pipeline" from development to production, minimizing the risk of database errors on your live site.
