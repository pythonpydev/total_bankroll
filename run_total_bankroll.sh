#!/bin/bash
# run_prod_total_bankroll.sh in /home/pythonpydev/total_bankroll/

# Set base directory
BASE_DIR="/home/pythonpydev/total_bankroll"

# Set environment variables
export FLASK_ENV=production
export FLASK_APP=total_bankroll:create_app

# Activate virtual environment
if command -v workon >/dev/null 2>&1; then
    workon bankroll_venv || {
        echo "Error: Failed to activate virtualenv with workon bankroll_venv"
        exit 1
    }
else
    source /home/pythonpydev/.virtualenvs/bankroll_venv/bin/activate || {
        echo "Error: Failed to source virtualenv at /home/pythonpydev/.virtualenvs/bankroll_venv/bin/activate"
        exit 1
    }
fi

# Change to project directory
cd "$BASE_DIR"

# Check command-line argument
case "$1" in
    "run")
        echo "Running Flask app..."
        flask run
        ;;
    "seed")
        echo "Running seed_articles.py..."
        python src/total_bankroll/seed_articles.py
        ;;
    "migrate")
        echo "Generating database migration..."
        flask db migrate
        ;;
    "upgrade")
        echo "Applying database migrations..."
        flask db upgrade
        ;;
    *)
        echo "Usage: $0 {run|seed|migrate|upgrade}"
        echo "  run: Start the Flask app"
        echo "  seed: Run seed_articles.py"
        echo "  migrate: Generate database migration"
        echo "  upgrade: Apply database migrations"
        exit 1
        ;;
esac
