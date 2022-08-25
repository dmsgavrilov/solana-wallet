import os

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:123@localhost:5432")

SOLANA_API_URL = os.getenv("SOLANA_API_URL", "https://api.devnet.solana.com")
SOLANA_WEBSOCKET_URL = os.getenv("SOLANA_WEBSOCKET_URL", "wss://api.devnet.solana.com")
