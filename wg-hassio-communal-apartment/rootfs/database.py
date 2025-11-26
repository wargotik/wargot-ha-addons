"""Database module for Communal Apartment add-on using SQLite."""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

DB_FILE = "/data/communal_apartment.db"


class Database:
    """SQLite database handler for Communal Apartment add-on."""

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

            # Create payment_types table (справочник типов платежей)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    system_name TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_system INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Create payments table (таблица платежей)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_type_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date TEXT NOT NULL,
                    period TEXT NOT NULL,
                    receipt_number TEXT,
                    payment_method TEXT,
                    notes TEXT,
                    previous_reading REAL,
                    current_reading REAL,
                    volume REAL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (payment_type_id) REFERENCES payment_types(id)
                )
            """)
            
            # Add new columns to existing table if they don't exist (for migration)
            try:
                cursor.execute("ALTER TABLE payments ADD COLUMN previous_reading REAL")
            except sqlite3.OperationalError:
                pass  # Column already exists
            try:
                cursor.execute("ALTER TABLE payments ADD COLUMN current_reading REAL")
            except sqlite3.OperationalError:
                pass  # Column already exists
            try:
                cursor.execute("ALTER TABLE payments ADD COLUMN volume REAL")
            except sqlite3.OperationalError:
                pass  # Column already exists

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_type ON payments(payment_type_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_period ON payments(period)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_types_active ON payment_types(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_types_system ON payment_types(is_system)")

            conn.commit()
            conn.close()
            _LOGGER.info("Database initialized successfully")
        except Exception as err:
            _LOGGER.error("Error initializing database: %s", err)
            raise

    # ========== Payment Types Methods ==========

    def add_payment_type(self, name: str, system_name: str | None = None, description: str | None = None, 
                        is_active: bool = True, is_system: bool = False) -> int | None:
        """Add a new payment type. Returns the ID of the created type."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # If system_name is not provided, use name as system_name
            if system_name is None:
                system_name = name

            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO payment_types (system_name, name, description, is_active, is_system, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (system_name, name, description, 1 if is_active else 0, 1 if is_system else 0, now, now))

            payment_type_id = cursor.lastrowid
            conn.commit()
            conn.close()
            _LOGGER.info("Payment type added: %s (id: %s)", name, payment_type_id)
            return payment_type_id
        except sqlite3.IntegrityError as err:
            _LOGGER.error("Payment type already exists: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Error adding payment type: %s", err)
            return None

    def get_all_payment_types(self, active_only: bool = False) -> list[dict[str, Any]]:
        """Get all payment types."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if active_only:
                cursor.execute("SELECT * FROM payment_types WHERE is_active = 1 ORDER BY name")
            else:
                cursor.execute("SELECT * FROM payment_types ORDER BY name")

            rows = cursor.fetchall()
            conn.close()

            types = []
            for row in rows:
                types.append({
                    "id": row["id"],
                    "system_name": row["system_name"],
                    "name": row["name"],
                    "description": row["description"],
                    "is_active": bool(row["is_active"]),
                    "is_system": bool(row["is_system"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            return types
        except Exception as err:
            _LOGGER.error("Error getting payment types: %s", err)
            return []

    def get_payment_type(self, type_id: int) -> dict[str, Any] | None:
        """Get payment type by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM payment_types WHERE id = ?", (type_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "id": row["id"],
                    "system_name": row["system_name"],
                    "name": row["name"],
                    "description": row["description"],
                    "is_active": bool(row["is_active"]),
                    "is_system": bool(row["is_system"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
            return None
        except Exception as err:
            _LOGGER.error("Error getting payment type: %s", err)
            return None

    def update_payment_type(self, type_id: int, name: str | None = None, description: str | None = None, is_active: bool | None = None) -> bool:
        """Update payment type. System types can only have name, description and is_active updated."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if this is a system type
            cursor.execute("SELECT is_system FROM payment_types WHERE id = ?", (type_id,))
            row = cursor.fetchone()
            if not row:
                _LOGGER.warning("Payment type %s not found", type_id)
                conn.close()
                return False

            is_system = bool(row["is_system"])

            updates = []
            params = []

            # For system types, only allow updating name, description, and is_active
            # system_name and is_system cannot be changed
            if name is not None:
                updates.append("name = ?")
                params.append(name)

            if description is not None:
                updates.append("description = ?")
                params.append(description)

            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(type_id)

                cursor.execute(
                    f"UPDATE payment_types SET {', '.join(updates)} WHERE id = ?",
                    params
                )

            conn.commit()
            conn.close()
            return True
        except Exception as err:
            _LOGGER.error("Error updating payment type: %s", err)
            return False

    def delete_payment_type(self, type_id: int) -> bool:
        """Delete payment type (only if no payments reference it and it's not a system type)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if this is a system type
            cursor.execute("SELECT is_system FROM payment_types WHERE id = ?", (type_id,))
            row = cursor.fetchone()
            if not row:
                _LOGGER.warning("Payment type %s not found", type_id)
                conn.close()
                return False

            if bool(row["is_system"]):
                _LOGGER.warning("Cannot delete payment type %s: it is a system type", type_id)
                conn.close()
                return False

            # Check if there are payments using this type
            cursor.execute("SELECT COUNT(*) as count FROM payments WHERE payment_type_id = ?", (type_id,))
            result = cursor.fetchone()
            if result["count"] > 0:
                _LOGGER.warning("Cannot delete payment type %s: it has %s payments", type_id, result["count"])
                conn.close()
                return False

            cursor.execute("DELETE FROM payment_types WHERE id = ?", (type_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as err:
            _LOGGER.error("Error deleting payment type: %s", err)
            return False

    # ========== Payments Methods ==========

    def add_payment(self, payment_type_id: int, amount: float, payment_date: str, period: str,
                   receipt_number: str | None = None,
                   payment_method: str | None = None, notes: str | None = None,
                   previous_reading: float | None = None, current_reading: float | None = None,
                   volume: float | None = None) -> int | None:
        """Add a new payment. Returns the ID of the created payment."""
        try:
            _LOGGER.info("Saving payment to database: type_id=%s, amount=%s, date=%s, period=%s, "
                        "receipt_number=%s, payment_method=%s, previous_reading=%s, current_reading=%s, volume=%s",
                        payment_type_id, amount, payment_date, period, receipt_number, payment_method,
                        previous_reading, current_reading, volume)
            
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO payments (payment_type_id, amount, payment_date, period, receipt_number,
                                    payment_method, notes, previous_reading, current_reading, volume,
                                    created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (payment_type_id, amount, payment_date, period, receipt_number,
                  payment_method, notes, previous_reading, current_reading, volume, now, now))

            payment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            _LOGGER.info("Payment successfully saved to database: id=%s, type_id=%s, amount=%s, period=%s, "
                        "date=%s, volume=%s, readings=%s→%s",
                        payment_id, payment_type_id, amount, period, payment_date, volume,
                        previous_reading, current_reading)
            return payment_id
        except Exception as err:
            _LOGGER.error("Error saving payment to database: %s, type_id=%s, amount=%s, period=%s", 
                         err, payment_type_id, amount, period, exc_info=True)
            return None

    def get_all_payments(self, payment_type_id: int | None = None, period: str | None = None,
                        limit: int | None = None) -> list[dict[str, Any]]:
        """Get all payments with optional filters."""
        try:
            _LOGGER.info("Getting payments from database: payment_type_id=%s, period=%s, limit=%s", 
                        payment_type_id, period, limit)
            
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT p.*, pt.name as payment_type_name
                FROM payments p
                LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
                WHERE 1=1
            """
            params = []

            if payment_type_id is not None:
                query += " AND p.payment_type_id = ?"
                params.append(payment_type_id)

            if period is not None:
                query += " AND p.period = ?"
                params.append(period)

            query += " ORDER BY p.payment_date DESC, p.created_at DESC"

            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            _LOGGER.debug("Executing query: %s with params: %s", query, params)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            _LOGGER.info("Retrieved %d payments from database", len(rows))

            payments = []
            for row in rows:
                payment = {
                    "id": row["id"],
                    "payment_type_id": row["payment_type_id"],
                    "payment_type_name": row["payment_type_name"],
                    "amount": float(row["amount"]),
                    "payment_date": row["payment_date"],
                    "period": row["period"],
                    "receipt_number": row["receipt_number"],
                    "payment_method": row["payment_method"],
                    "notes": row["notes"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                
                # Add reading fields if they exist
                if row.get("previous_reading") is not None:
                    payment["previous_reading"] = float(row["previous_reading"])
                if row.get("current_reading") is not None:
                    payment["current_reading"] = float(row["current_reading"])
                if row.get("volume") is not None:
                    payment["volume"] = float(row["volume"])
                
                _LOGGER.debug("Payment: id=%s, type=%s, amount=%s, period=%s, volume=%s, readings=%s→%s",
                             payment["id"], payment["payment_type_name"], payment["amount"], 
                             payment["period"], payment.get("volume"), 
                             payment.get("previous_reading"), payment.get("current_reading"))
                
                payments.append(payment)
            
            _LOGGER.info("Returning %d payments", len(payments))
            return payments
        except Exception as err:
            _LOGGER.error("Error getting payments: %s", err)
            return []

    def get_payment(self, payment_id: int) -> dict[str, Any] | None:
        """Get payment by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, pt.name as payment_type_name
                FROM payments p
                LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
                WHERE p.id = ?
            """, (payment_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                payment = {
                    "id": row["id"],
                    "payment_type_id": row["payment_type_id"],
                    "payment_type_name": row["payment_type_name"],
                    "amount": float(row["amount"]),
                    "payment_date": row["payment_date"],
                    "period": row["period"],
                    "receipt_number": row["receipt_number"],
                    "payment_method": row["payment_method"],
                    "notes": row["notes"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                
                # Add reading fields if they exist
                if row.get("previous_reading") is not None:
                    payment["previous_reading"] = float(row["previous_reading"])
                if row.get("current_reading") is not None:
                    payment["current_reading"] = float(row["current_reading"])
                if row.get("volume") is not None:
                    payment["volume"] = float(row["volume"])
                
                return payment
            return None
        except Exception as err:
            _LOGGER.error("Error getting payment: %s", err)
            return None

    def update_payment(self, payment_id: int, payment_type_id: int | None = None, amount: float | None = None,
                      payment_date: str | None = None, period: str | None = None,
                      receipt_number: str | None = None,
                      payment_method: str | None = None, notes: str | None = None) -> bool:
        """Update payment."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            updates = []
            params = []

            if payment_type_id is not None:
                updates.append("payment_type_id = ?")
                params.append(payment_type_id)

            if amount is not None:
                updates.append("amount = ?")
                params.append(amount)

            if payment_date is not None:
                updates.append("payment_date = ?")
                params.append(payment_date)

            if period is not None:
                updates.append("period = ?")
                params.append(period)

            if receipt_number is not None:
                updates.append("receipt_number = ?")
                params.append(receipt_number)

            if payment_method is not None:
                updates.append("payment_method = ?")
                params.append(payment_method)

            if notes is not None:
                updates.append("notes = ?")
                params.append(notes)

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(payment_id)

                cursor.execute(
                    f"UPDATE payments SET {', '.join(updates)} WHERE id = ?",
                    params
                )

            conn.commit()
            conn.close()
            return True
        except Exception as err:
            _LOGGER.error("Error updating payment: %s", err)
            return False

    def delete_payment(self, payment_id: int) -> bool:
        """Delete payment."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as err:
            _LOGGER.error("Error deleting payment: %s", err)
            return False

    def get_payments_summary(self, period: str | None = None) -> dict[str, Any]:
        """Get summary statistics for payments."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "SELECT SUM(amount) as total, COUNT(*) as count FROM payments WHERE 1=1"
            params = []

            if period is not None:
                query += " AND period = ?"
                params.append(period)

            cursor.execute(query, params)
            row = cursor.fetchone()
            conn.close()

            return {
                "total_amount": float(row["total"]) if row["total"] else 0.0,
                "total_count": row["count"] if row["count"] else 0
            }
        except Exception as err:
            _LOGGER.error("Error getting payments summary: %s", err)
            return {"total_amount": 0.0, "total_count": 0}
