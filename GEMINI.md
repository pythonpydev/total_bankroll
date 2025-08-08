# Total Bankroll Application

## Purpose

Keeps a track of total poker bankroll, including funds on each site, cash and other assets.

## Requirements

- Store amount of money on each poker site
- Some poker sites use different currencies.
- Add up total amount of money on each poker site
- Store amount of money saved in each asset type
- Add up total amount of non-poker assets
- Store each withdrawal transaction
- Add up total amount of withdrawals
- Store each deposit transaction
- Add up total amount of deposits.
- When withdrawals are made, as well as the date and time of the transaction,
the current net worth also needs to be recorded.
- Calculate total net worth
- Total net worth = money on poker sites + assets
- Calculate total bankroll
- Total bankroll = total net worth + deposits - withdrawals
- Calculate total profit 
- Total profit = total net worth - deposits + withdrawals
- Users cannot withdraw more money than their net worth
- Keep a history of all values saved over time
- Display latest changes in poker site funds, assets (current value - previous)
- All financial values should be stored on the database in US dollars $.
- Make available reports on historical data

## Interface

- A python flask web application, using HTML forms to input data.
- Use bootstrap to format the web pages.
- Use this example theme /home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/resources/
- The menu bar at the top should have the following links: Bankroll, Poker Sites, Assets, Withdrawal, Deposit, Currencies, About
- When entering values monetary values for poker sites and assets, there should 
be a drop down box for the currency. 
- Currencies should be selected from a drop down box.  The default currency is 
US dollars $.
- Use numeric up down boxes to obtain numeric values to improve validation.
- Display positive changes in poker site funds and assets as light green, and 
negative amounts as light red.
- When displaying a list of currencies in a drop down box, the default should 
US dollars, the second highest option the UK pound and the third highest option
the Euro.  After that, display the currencies in alphabetical order.

## Database

- Use SQLite to implement the database

### Database Schema

CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS drawings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    withdrawn_at REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    deposited_at REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS currency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rate REAL NOT NULL,
    code TEXT NOT NULL,
    symbol TEXT NOT NULL
);

## File locations

- Source code is located in /home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/src/total_bankroll/
