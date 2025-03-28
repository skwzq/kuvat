CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    title TEXT,
    image BLOB,
    description TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users
);