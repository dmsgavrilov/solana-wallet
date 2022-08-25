CREATE TABLE IF NOT EXISTS users  (
    id serial PRIMARY KEY,
    username VARCHAR(32) NOT NULL UNIQUE,
    public_key VARCHAR(64) NOT NULL,
    secret_key bytea NOT NULL
);


CREATE TABLE IF NOT EXISTS transactions  (
    id serial PRIMARY KEY,
    transaction_sig VARCHAR(128) NOT NULL UNIQUE,
    fee DECIMAL(10, 9),
    amount DECIMAL(10, 9),
    status VARCHAR(16),
    blocktime TIMESTAMP,
    sender_id INTEGER REFERENCES users ON DELETE CASCADE,
    receiver_id INTEGER REFERENCES users ON DELETE CASCADE
);
