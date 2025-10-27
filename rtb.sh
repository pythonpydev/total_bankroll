#!/bin/bash

# make it executable:
# chmod +x /path/to/rtb.sh

# --- Environment Selection ---
echo "Select environment:"
echo "1. Development (dev)"
echo "2. Production (prod)"
read -p "Enter choice (1 or 2): " env_choice

case "$env_choice" in
    1)
        ENV="dev"
        BASE_DIR="/home/ed/MEGA/total_bankroll"
        VENV_DIR="$BASE_DIR/.venv"
        FLASK_ENV="development"
        ;;
    2)
        ENV="prod"
        BASE_DIR="/home/pythonpydev/total_bankroll"
        VENV_DIR="/home/pythonpydev/.virtualenvs/bankroll_venv"
        FLASK_ENV="production"
        ;;
    *)
        echo "Invalid environment choice. Exiting."
        exit 1
        ;;
esac

# --- Command Selection ---
echo ""
echo "Select command for $ENV environment:"
echo "1. Run Flask app (run)"
echo "2. Run Flask app in development mode (run-dev) - Dev only"
echo "3. Seed articles (seed)"
echo "4. Purge articles (purge-articles)"
echo "5. Convert articles (convert-articles)"
echo "6. Generate database migration (migrate)"
echo "7. Apply database migrations (upgrade)"
read -p "Enter choice (1-7): " cmd_choice

COMMAND=""
case "$cmd_choice" in
    1) COMMAND="run" ;;
    2) COMMAND="run-dev" ;;
    3) COMMAND="seed" ;;
    4) COMMAND="purge-articles" ;;
    5) COMMAND="convert-articles" ;;
    6) COMMAND="migrate" ;;
    7) COMMAND="upgrade" ;;
    *)
        echo "Invalid command choice. Exiting."
        exit 1
        ;;
esac

# Check if run-dev is selected in production
if [ "$COMMAND" = "run-dev" ] && [ "$ENV" = "prod" ]; then
    echo "Error: 'run-dev' is only available in development environment. Exiting."
    exit 1
fi

# --- Common Setup ---
# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Directory $BASE_DIR does not exist. Exiting."
    exit 1
fi

# Set environment variables
export FLASK_ENV="$FLASK_ENV"
export FLASK_APP="total_bankroll:create_app"
export PYTHONPATH="$BASE_DIR/src:$PYTHONPATH"

# Activate virtual environment
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR/bin/activate. Exiting."
    exit 1
fi
source "$VENV_DIR/bin/activate"

# Change to project directory
cd "$BASE_DIR" || {
    echo "Error: Could not change to directory $BASE_DIR. Exiting."
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

# --- Execute Command ---
case "$COMMAND" in
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
        echo "Running Flask app in development mode..."
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
        echo "Unknown command. This should not happen. Exiting."
        exit 1
        ;;
esac