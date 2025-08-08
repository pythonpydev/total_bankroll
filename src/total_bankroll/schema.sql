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