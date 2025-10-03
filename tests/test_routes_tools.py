from flask import url_for
from total_bankroll.models import User


def test_tools_page_unauthenticated(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/tools' page is requested by an unauthenticated user
    THEN check that the user is redirected to the login page
    """
    response = client.get(url_for('tools.tools_page'))
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_tools_page_authenticated(client, new_user):
    """
    GIVEN a Flask application configured for testing and an authenticated user
    WHEN the '/tools' page is requested
    THEN check that the page is rendered successfully
    """
    with client:
        client.post(url_for('auth.login'), data={
            'email': new_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        response = client.get(url_for('tools.tools_page'))

    assert response.status_code == 200
    assert b"Available Tools" in response.data
    assert b"Cash Game Stakes" in response.data
    assert b"Tournament Stakes" in response.data
    assert b"SPR Calculator" in response.data


def test_poker_stakes_page_authenticated(client, new_user):
    """
    GIVEN a Flask application and an authenticated user
    WHEN the '/poker_stakes' page is requested
    THEN check that the page is rendered successfully
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'})
        response = client.get(url_for('tools.poker_stakes_page'))
    assert response.status_code == 200
    assert b"Cash Game Stakes Recommendations" in response.data


def test_tournament_stakes_page_authenticated(client, new_user):
    """
    GIVEN a Flask application and an authenticated user
    WHEN the '/tournament_stakes' page is requested
    THEN check that the page is rendered successfully
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'})
        response = client.get(url_for('tools.tournament_stakes_page'))
    assert response.status_code == 200
    assert b"Tournament Stakes Recommendations" in response.data


def test_spr_calculator_page_authenticated(client, new_user):
    """
    GIVEN a Flask application and an authenticated user
    WHEN the '/tools/spr-calculator' page is requested
    THEN check that the page is rendered successfully
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.get(url_for('tools.spr_calculator_page'))
    assert response.status_code == 200
    assert b"Stack-to-Pot Ratio (SPR) Calculator" in response.data


def test_spr_calculator_valid_submission(client, new_user):
    """
    GIVEN a Flask application and an authenticated user
    WHEN a valid form is submitted to the SPR calculator
    THEN check that the correct SPR is calculated and displayed
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.post(url_for('tools.spr_calculator_page'), data={
            'effective_stack': '100',
            'pot_size': '10'
        }, follow_redirects=True)

    assert response.status_code == 200
    # Check for the calculated SPR of 10.00 (100 / 10)
    assert b'10.00' in response.data


def test_spr_calculator_invalid_submission(client, new_user):
    """
    GIVEN a Flask application and an authenticated user
    WHEN an invalid form is submitted to the SPR calculator (e.g., pot size of 0)
    THEN check that an error message is flashed
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.post(url_for('tools.spr_calculator_page'), data={
            'effective_stack': '100',
            'pot_size': '0'
        }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Pot size must be greater than zero." in response.data


def test_bankroll_goals_page_unauthenticated(client):
    """
    GIVEN a Flask application
    WHEN the '/tools/bankroll-goals' page is requested by an unauthenticated user
    THEN check that the user is redirected to the login page
    """
    response = client.get(url_for('tools.bankroll_goals_page'))
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_bankroll_goals_page_authenticated_get(client, new_user):
    """
    GIVEN a Flask application and an authenticated user
    WHEN the '/tools/bankroll-goals' page is requested
    THEN check that the page is rendered successfully
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.get(url_for('tools.bankroll_goals_page'))
    assert response.status_code == 200
    assert b"Bankroll Goals Calculator" in response.data


def test_bankroll_goals_page_valid_submission(client, new_user):
    """
    GIVEN a Flask application and an authenticated user
    WHEN a valid form is submitted to the Bankroll Goals calculator
    THEN check that the correct time projection is calculated and displayed
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        # For a new user, current_bankroll is 0. Target=1000, Monthly=100 -> 10 months.
        response = client.post(url_for('tools.bankroll_goals_page'), data={
            'target_bankroll': '1000',
            'monthly_profit': '100'
        }, follow_redirects=True)

    assert response.status_code == 200
    assert b"it will take you approximately 10 months" in response.data
    assert b"accumulate an additional $1,000.00" in response.data

def test_bankroll_goals_page_required_profit_submission(client, new_user):
    """
    GIVEN a Flask application and an authenticated user
    WHEN a valid form is submitted to calculate required profit
    THEN check that the correct monthly profit is calculated and displayed
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        # For a new user, current_bankroll is 0. Target=1200, Timeframe=12 months -> 100/month.
        response = client.post(url_for('tools.bankroll_goals_page'), data={
            'calculation_mode': 'profit',
            'target_bankroll': '1200',
            'timeframe_months': '12'
        }, follow_redirects=True)

    assert response.status_code == 200
    assert b"you will need to achieve an average monthly profit of $100.00" in response.data


def test_bankroll_goals_page_already_at_goal(client, new_user):
    """
    GIVEN a Flask application and an authenticated user with a bankroll
    WHEN a form is submitted with a target bankroll less than the current bankroll
    THEN check that the "Congratulations" message is displayed
    """
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        # For a new user, current_bankroll is 0. Target=0 should trigger the message.
        response = client.post(url_for('tools.bankroll_goals_page'), data={
            'calculation_mode': 'time',
            'target_bankroll': '0',
            'monthly_profit': '100'
        }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Congratulations! Your current bankroll" in response.data