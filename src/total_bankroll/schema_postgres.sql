CREATE TABLE IF NOT EXISTS sites (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS drawings (
    id SERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    withdrawn_at REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS deposits (
    id SERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    deposited_at REAL NOT NULL,
    last_updated TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'Dollar'
);

CREATE TABLE IF NOT EXISTS currency (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    rate REAL NOT NULL,
    code TEXT NOT NULL,
    symbol TEXT NOT NULL
);