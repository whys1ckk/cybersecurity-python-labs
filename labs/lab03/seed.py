import json
import logging
import sqlite3
from contextlib import closing
from pathlib import Path
from labs.lab03.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database() -> None:
    """Заповнити базу початковими даними з JSON в одній транзакції."""
    initialize_database()
    if not SEED_PATH.exists():
        logger.error("Файл seed.json не знайдено.")
        return

    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    
    with closing(get_connection()) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] > 0:
                logger.info("База вже містить дані. Заповнення пропущено.")
                return

            with connection:
                for cat in data.get("categories", []):
                    connection.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (cat["id"], cat["name"])
                    )
                for rec in data.get("records", []):
                    connection.execute(
                        """INSERT INTO records (code, title, category_id, value, status)
                           VALUES (?, ?, ?, ?, ?)""",
                        (rec["code"], rec["title"], rec["category_id"], rec["value"], rec["status"])
                    )
            logger.info("Початкові дані успішно додано до бази.")
        except sqlite3.Error as e:
            logger.error("Помилка під час заповнення бази даних: %s", e)
            raise

if __name__ == "__main__":
    seed_database()