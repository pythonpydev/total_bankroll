#!/bin/bash

# make it executable:
# chmod +x /path/to/rtb.sh

# --- Environment Selection ---
# Configuration
DEV_BASE_DIR="/home/ed/MEGA/total_bankroll"
DEV_VENV_DIR="$DEV_BASE_DIR/.venv"
PROD_BASE_DIR="/home/pythonpydev/total_bankroll"
PROD_VENV_DIR="/home/pythonpydev/.virtualenvs/bankroll_venv"

# Argument Parsing
COMMAND_ARG=""
ENV_FLAG=""

# Parse command and optional --prod flag
if [ "$#" -gt 0 ]; then
    COMMAND_ARG="$1"
    if [ "$#" -gt 1 ]; then
        ENV_FLAG="$2"
    fi
fi

# Determine Environment and Command
ENV=""
COMMAND=""
FLASK_ENV=""
BASE_DIR=""
VENV_DIR=""

# If a command argument is provided, bypass menus
if [ -n "$COMMAND_ARG" ]; then
    COMMAND="$COMMAND_ARG"
    if [ "$ENV_FLAG" = "--prod" ]; then
        ENV="prod"
        BASE_DIR="$PROD_BASE_DIR"
        VENV_DIR="$PROD_VENV_DIR"
        FLASK_ENV="production"
    elif [ -n "$ENV_FLAG" ]; then # Invalid flag
        echo "Error: Invalid flag '$ENV_FLAG'. Use '--prod' for production environment."
        echo "Usage: $0 {run|seed|purge-articles|convert-articles|migrate|upgrade} [--prod]"
        exit 1
    else # Default to dev if no --prod flag
        ENV="dev"
        BASE_DIR="$DEV_BASE_DIR"
        VENV_DIR="$DEV_VENV_DIR"
        FLASK_ENV="development"
    fi
else # No command argument, show menus
    # --- Environment Selection Menu ---
    echo "Select environment:"
    echo "1. Development (dev)"
    echo "2. Production (prod)"
    echo "3. Exit"
    read -p "Enter choice (1-3): " env_choice

    case "$env_choice" in
        1)
            ENV="dev"
            BASE_DIR="$DEV_BASE_DIR"
            VENV_DIR="$DEV_VENV_DIR"
            FLASK_ENV="development"
            ;;
        2)
            ENV="prod"
            BASE_DIR="$PROD_BASE_DIR"
            VENV_DIR="$PROD_VENV_DIR"
            FLASK_ENV="production"
            ;;
        3)
            echo "Exiting."
            exit 0
            ;;
        *)
            echo "Invalid environment choice. Exiting."
            exit 1
            ;;
    esac

    # --- Command Selection Menu ---
    echo ""
    echo "Select command for $ENV environment:"
    echo "1. Run Flask app (run)"
    echo "2. Seed articles (seed)"
    echo "3. Purge articles (purge-articles)"
    echo "4. Convert articles (convert-articles)"
    echo "5. Generate database migration (migrate)"
    echo "6. Apply database migrations (upgrade)"
    echo "7. Exit"
    read -p "Enter choice (1-7): " cmd_choice

    case "$cmd_choice" in
        1) COMMAND="run" ;;
        2) COMMAND="seed" ;;
        3) COMMAND="purge-articles" ;;
        4) COMMAND="convert-articles" ;;
        5) COMMAND="migrate" ;;
        6) COMMAND="upgrade" ;;
        7)
            echo "Exiting."
            exit 0
            ;;
        *)
            echo "Invalid command choice. Exiting."
            exit 1
            ;;
    esac
fi

# --- Validate Command ---
ALLOWED_COMMANDS=("run" "seed" "purge-articles" "convert-articles" "migrate" "upgrade")
COMMAND_VALID=false
for cmd in "${ALLOWED_COMMANDS[@]}"; do
    if [ "$COMMAND" = "$cmd" ]; then
        COMMAND_VALID=true
        break
    fi
done

if [ "$COMMAND_VALID" = false ]; then
    echo "Error: Invalid command '$COMMAND'."
    echo "Usage: $0 {run|seed|purge-articles|convert-articles|migrate|upgrade} [--prod]"
    exit 1
fi

# --- Common Setup (using determined variables) ---
# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Base directory '$BASE_DIR' does not exist. Exiting."
    exit 1
fi

# Set environment variables
export FLASK_ENV="$FLASK_ENV" # Set by menu or --prod flag
export FLASK_APP="total_bankroll:create_app"
export PYTHONPATH="$BASE_DIR/src:$PYTHONPATH"

# Activate virtual environment
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Error: Virtual environment activation script not found at $VENV_DIR/bin/activate. Exiting."
    exit 1
fi
source "$VENV_DIR/bin/activate"

# Change to project directory
cd "$BASE_DIR" || {
    echo "Error: Could not change to project directory '$BASE_DIR'. Exiting."
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