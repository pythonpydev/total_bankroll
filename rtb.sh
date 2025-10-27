#!/bin/bash

# make it executable:
# chmod +x /path/to/run_total_bankroll.sh

# Example usage:
# ./run_total_bankroll.sh dev run
# ./run_total_bankroll.sh prod seed

# Check if environment argument is provided
if [ -z "$1" ]; then
    echo "Error: Environment argument (dev or prod) is required."
    echo "Usage: $0 {dev|prod} {run|run-dev|seed|purge-articles|convert-articles|migrate|upgrade}"
    exit 1
fi

# Set environment-specific configurations
case "$1" in
    "dev")
        BASE_DIR="/home/ed/MEGA/total_bankroll"
        VENV_DIR="$BASE_DIR/.venv"
        FLASK_ENV="development"
        ;;
    "prod")
        BASE_DIR="/home/pythonpydev/total_bankroll"
        VENV_DIR="/home/pythonpydev/.virtualenvs/bankroll_venv"
        FLASK_ENV="production"
        ;;
    *)
        echo "Error: Invalid environment. Use 'dev' or 'prod'."
        echo "Usage: $0 {dev|prod} {run|run-dev|seed|purge-articles|convert-articles|migrate|upgrade}"
        exit 1
        ;;
esac

# Shift arguments to process the command
shift

# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Directory $BASE_DIR does not exist."
    exit 1
fi

# Set environment variables
export FLASK_ENV="$FLASK_ENV"
export FLASK_APP="total_bankroll:create_app"
export PYTHONPATH="$BASE_DIR/src:$PYTHONPATH"

# Activate virtual environment
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
echo "Environment: $FLASK_ENV"
echo "Environment variables:"
printenv | grep -E 'FLASK_ENV|FLASK_APP|PYTHONPATH'
echo "Python version:"
python --version
echo "Flask version:"
pip show flask

# Check command-line argument
case "$1" in
    "run")
        if [ "$FLASK_ENV" = "production" ]; then
            echo "Running Flask app with Gunicorn (production mode)..."
            gunicorn -w 2 -b 0.0.0.0:8000 "total_bankroll:create_app()"
        else
            echo "Running Flask app (development mode)..."
            flask run
        fi
        ;;
    "run-dev")
        if [ "$FLASK_ENV" = "production" ]; then
            echo "Error: 'run-dev' is only available in development environment."
            exit 1
        fi
        echo "Running Flask app in development mode..."
        export FLASK_ENV=development
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
        echo "Usage: $0 {dev|prod} {run|run-dev|seed|purge-articles|convert-articles|migrate|upgrade}"
        echo "  run: Start the Flask app (Gunicorn for prod, flask run for dev)"
        echo "  run-dev: Start the Flask app in development mode (dev only)"
        echo "  seed: Run seed_articles.py"
        echo "  purge-articles: Delete all articles from the database"
        echo "  convert-articles: Convert article markdown to HTML"
        echo "  migrate: Generate database migration"
        echo "  upgrade: Apply database migrations"
        exit 1
        ;;
esac
