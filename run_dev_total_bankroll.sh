#!/bin/bash

# make it executable:
# chmod +x /home/ed/MEGA/total_bankroll/run_dev_total_bankroll.sh

# Example:
# cd /home/ed/MEGA/total_bankroll
# ./run_dev_total_bankroll.sh seed


# Set base directory
BASE_DIR="/home/ed/MEGA/total_bankroll"

# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Directory $BASE_DIR does not exist."
    exit 1
fi

# Set environment variables
export FLASK_ENV=development
export FLASK_APP=total_bankroll:create_app
export PYTHONPATH="$BASE_DIR/src:$PYTHONPATH"

# Activate virtual environment
VENV_DIR="$BASE_DIR/.venv"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR/bin/activate."
    exit 1
fi
source "$VENV_DIR/bin/activate"

# Change to project directory
cd "$BASE_DIR" || {
    echo "Error: Could not change to directory $BASE_DIR."
    exit 1
}

# Debug: Print environment variables and Python path
echo "Environment variables:"
printenv | grep -E 'FLASK_ENV|FLASK_APP|PYTHONPATH'
echo "Python version:"
python --version
echo "Flask version:"
pip show flask

# Check command-line argument
case "$1" in
    "run")
        echo "Running Flask app..."
        # Explicitly set host and port to ensure Werkzeug is used
        export FLASK_ENV=development
        export FLASK_RUN_HOST=127.0.0.1
        flask run --port=5000
        ;;
    "seed")
        echo "Running seed_articles.py..."
        python src/total_bankroll/seed_articles.py
        ;;
    "purge-articles")
        echo "Purging all articles from the database..."
        python src/total_bankroll/purge_articles.py
        ;;
    "convert-articles")
        echo "Converting all articles' markdown to HTML..."
        python src/total_bankroll/convert_articles.py
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
        echo "Usage: $0 {run|seed|purge-articles|convert-articles|migrate|upgrade}"
        echo "  run: Start the Flask app in development mode"
        echo "  seed: Run seed_articles.py"
        echo "  purge-articles: Delete all articles from the database"
        echo "  convert-articles: Convert article markdown to HTML"
        echo "  migrate: Generate database migration"
        echo "  upgrade: Apply database migrations"
        exit 1
        ;;
esac
