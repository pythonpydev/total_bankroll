#!/bin/bash

# make it executable:
# chmod +x /home/ed/MEGA/total_bankroll/run_total_bankroll.sh

# run_total_bankroll.sh in /home/ed/MEGA/total_bankroll/

# Example:
# cd ~/MEGA/total_bankroll
# ./run_total_bankroll.sh seed

# Run the app in development:
# ./run_total_bankroll.sh run

# Set base directory
BASE_DIR="/home/ed/MEGA/total_bankroll"

# Set environment variables
export FLASK_ENV=development
export FLASK_APP=total_bankroll:create_app

# Activate virtual environment
source "$BASE_DIR/.venv/bin/activate"

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
        echo "  run: Start the Flask app"
        echo "  seed: Run seed_articles.py"
        echo "  purge-articles: Delete all articles from the database"
        echo "  convert-articles: Convert article markdown to HTML"
        echo "  migrate: Generate database migration"
        echo "  upgrade: Apply database migrations"
        exit 1
        ;;
esac
