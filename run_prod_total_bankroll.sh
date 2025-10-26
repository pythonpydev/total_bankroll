#!/bin/bash
export PYTHONPATH=/home/pythonpydev/total_bankroll/src:$PYTHONPATH
export FLASK_APP=total_bankroll:create_app
export FLASK_ENV=production

source /home/pythonpydev/.virtualenvs/bankroll_venv/bin/activate

echo "Environment variables:"
echo "PYTHONPATH=$PYTHONPATH"
echo "FLASK_APP=$FLASK_APP"
echo "FLASK_ENV=$FLASK_ENV"

echo "Python version:"
python --version

echo "Flask version:"
pip show flask

if [ "$1" = "run" ]; then
    echo "Starting Flask application..."
    gunicorn -w 1 -b 0.0.0.0:8000 wsgi:app
elif [ "$1" = "seed" ]; then
    echo "Running seed_articles.py..."
    python /home/pythonpydev/total_bankroll/src/total_bankroll/seed_articles.py
elif [ "$1" = "migrate" ]; then
    echo "Generating database migrations..."
    flask db migrate
elif [ "$1" = "upgrade" ]; then
    echo "Applying database migrations..."
    flask db upgrade
else
    echo "Usage: $0 {run|seed|migrate|upgrade}"
    exit 1
fi
