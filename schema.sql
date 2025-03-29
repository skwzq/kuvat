CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    data BLOB
    format TEXT
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    image_id INTEGER REFERENCES images,
    description TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users
);