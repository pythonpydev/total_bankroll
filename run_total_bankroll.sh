#!/bin/bash

# make it executable:
# chmod +x /home/ed/MEGA/total_bankroll/run_total_bankroll.sh

# run_total_bankroll.sh in /home/ed/MEGA/total_bankroll/

# Example seed in development:
# cd ~/MEGA/total_bankroll
# ./run_total_bankroll.sh seed

# Run the app in development:
# ./run_total_bankroll.sh run

# In development if the articles model changed
# ./run_total_bankroll.sh migrate
# ./run_total_bankroll.sh upgrade

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
