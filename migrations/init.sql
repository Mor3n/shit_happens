CREATE TABLE IF NOT EXISTS confessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    text TEXT,
    hashtags TEXT,
    reactions TEXT,
    timestamp TEXT,
    keywords TEXT,
    emotion TEXT
);

CREATE TABLE IF NOT EXISTS stats (
    tag TEXT,
    count INTEGER
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT
);
