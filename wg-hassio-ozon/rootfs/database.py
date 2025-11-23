"""Database module for Ozon add-on using SQLite."""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

DB_FILE = "/data/ozon.db"


class Database:
    """SQLite database handler for Ozon add-on."""

    def __init__(self) -> None:
        """Initialize database connection."""
        self.db_path = Path(DB_FILE)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        return conn

    def _init_database(self) -> None:
        """Initialize database tables."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Create products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL UNIQUE,
                    name TEXT,
                    price REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Create pages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    product_id TEXT PRIMARY KEY,
                    html TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)

            # Create fetch_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fetch_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    html_length INTEGER,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)

            # Create price_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    price REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_url ON products(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_timestamp ON pages(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fetch_history_product ON fetch_history(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fetch_history_timestamp ON fetch_history(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)")

            conn.commit()
            conn.close()
            _LOGGER.info("Database initialized successfully")
        except Exception as err:
            _LOGGER.error("Error initializing database: %s", err)
            raise

    def get_all_products(self) -> list[dict[str, Any]]:
        """Get all products from database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()

            products = []
            for row in rows:
                products.append({
                    "id": row["id"],
                    "url": row["url"],
                    "name": row["name"] or f"Товар {row['id']}",
                    "price": row["price"] or 0
                })
            return products
        except Exception as err:
            _LOGGER.error("Error getting products: %s", err)
            return []

    def add_product(self, product_id: str, url: str, name: str | None = None, price: float = 0) -> bool:
        """Add product to database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO products (id, url, name, price, created_at, updated_at)
                VALUES (?, ?, ?, ?, 
                    COALESCE((SELECT created_at FROM products WHERE id = ?), ?),
                    ?)
            """, (product_id, url, name, price, product_id, now, now))

            conn.commit()
            conn.close()
            _LOGGER.info("Product added: %s", product_id)
            return True
        except sqlite3.IntegrityError as err:
            _LOGGER.error("Product already exists or constraint violation: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("Error adding product: %s", err)
            return False

    def product_exists(self, url: str) -> bool:
        """Check if product with URL already exists."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM products WHERE url = ?", (url,))
            result = cursor.fetchone()
            conn.close()
            return result["count"] > 0
        except Exception as err:
            _LOGGER.error("Error checking product existence: %s", err)
            return False

    def update_product(self, product_id: str, name: str | None = None, price: float | None = None) -> bool:
        """Update product information."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)

            old_price = None
            price_changed = False
            if price is not None:
                # Get old price before update
                cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
                old_row = cursor.fetchone()
                if old_row:
                    old_price = old_row["price"]
                    if old_price != price:
                        price_changed = True
                else:
                    # Product doesn't exist yet, but we'll add price history anyway
                    price_changed = True
                
                updates.append("price = ?")
                params.append(price)

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(product_id)

                cursor.execute(
                    f"UPDATE products SET {', '.join(updates)} WHERE id = ?",
                    params
                )

            conn.commit()
            conn.close()
            
            # Add to price history if price changed (after commit)
            if price_changed and price is not None:
                self.add_price_history(product_id, price)
            
            return True
        except Exception as err:
            _LOGGER.error("Error updating product: %s", err)
            return False

    def delete_product(self, product_id: str) -> bool:
        """Delete product, its page and history."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Delete history first
            cursor.execute("DELETE FROM fetch_history WHERE product_id = ?", (product_id,))
            # Delete price history
            cursor.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
            # Delete page
            cursor.execute("DELETE FROM pages WHERE product_id = ?", (product_id,))
            # Delete product
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as err:
            _LOGGER.error("Error deleting product: %s", err)
            return False

    def save_page(self, product_id: str, html: str) -> bool:
        """Save HTML page for product."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            timestamp = datetime.now().isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO pages (product_id, html, timestamp)
                VALUES (?, ?, ?)
            """, (product_id, html, timestamp))

            conn.commit()
            conn.close()
            _LOGGER.info("Page saved for product: %s", product_id)
            return True
        except Exception as err:
            _LOGGER.error("Error saving page: %s", err)
            return False

    def get_page(self, product_id: str) -> dict[str, Any] | None:
        """Get HTML page for product."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pages WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "product_id": row["product_id"],
                    "html": row["html"],
                    "timestamp": row["timestamp"]
                }
            return None
        except Exception as err:
            _LOGGER.error("Error getting page: %s", err)
            return None

    def get_all_pages(self) -> dict[str, dict[str, Any]]:
        """Get all pages from database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pages")
            rows = cursor.fetchall()
            conn.close()

            pages = {}
            for row in rows:
                pages[row["product_id"]] = {
                    "html": row["html"],
                    "timestamp": row["timestamp"]
                }
            return pages
        except Exception as err:
            _LOGGER.error("Error getting pages: %s", err)
            return {}

    def add_fetch_history(self, product_id: str, status: str, error_message: str | None = None, html_length: int | None = None) -> bool:
        """Add fetch history record."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            timestamp = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO fetch_history (product_id, timestamp, status, error_message, html_length)
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, timestamp, status, error_message, html_length))

            conn.commit()
            conn.close()
            _LOGGER.debug("Fetch history added for product: %s, status: %s", product_id, status)
            return True
        except Exception as err:
            _LOGGER.error("Error adding fetch history: %s", err)
            return False

    def get_last_fetch(self, product_id: str) -> dict[str, Any] | None:
        """Get last fetch history for product."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM fetch_history 
                WHERE product_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (product_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "id": row["id"],
                    "product_id": row["product_id"],
                    "timestamp": row["timestamp"],
                    "status": row["status"],
                    "error_message": row["error_message"],
                    "html_length": row["html_length"]
                }
            return None
        except Exception as err:
            _LOGGER.error("Error getting last fetch: %s", err)
            return None

    def get_fetch_history(self, product_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Get fetch history. If product_id is None, returns all history."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if product_id:
                cursor.execute("""
                    SELECT * FROM fetch_history 
                    WHERE product_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (product_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM fetch_history 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))

            rows = cursor.fetchall()
            conn.close()

            history = []
            for row in rows:
                history.append({
                    "id": row["id"],
                    "product_id": row["product_id"],
                    "timestamp": row["timestamp"],
                    "status": row["status"],
                    "error_message": row["error_message"],
                    "html_length": row["html_length"]
                })
            return history
        except Exception as err:
            _LOGGER.error("Error getting fetch history: %s", err)
            return []

