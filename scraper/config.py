# config.py
import os

# Lista de páginas a monitorear (edítala)
PAGES = [
    "https://probuilds.net/",
    "https://probuilds.net/champions"
]

DATABASE_URL = os.getenv("DATABASE_URL")  # postgres://user:pass@host:port/db
