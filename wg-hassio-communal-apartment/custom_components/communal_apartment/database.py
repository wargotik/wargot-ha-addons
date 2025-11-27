"""Database interface for Communal Apartment."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Payment types constants (ID -> system_name) - must match web_server.py
PAYMENT_TYPES = {
    1: "electricity",
    2: "gas",
    3: "water"
}


class CommunalApartmentDatabase:
    """Database interface for reading payment data."""

    def __init__(self, db_path: str) -> None:
        """Initialize database connection."""
        self.db_path = Path(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_payments(self) -> list[dict[str, Any]]:
        """Get all payments from database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT p.*
                FROM payments p
                ORDER BY p.payment_date DESC, p.created_at DESC
            """)

            rows = cursor.fetchall()
            conn.close()

            payments = []
            for row in rows:
                # Get payment_type_id and map to system_name
                payment_type_id = row["payment_type_id"]
                system_name = PAYMENT_TYPES.get(payment_type_id, "")
                payment_type_name = ""  # Will be translated in coordinator if needed
                
                # Get optional reading fields safely
                previous_reading = None
                try:
                    if row["previous_reading"] is not None:
                        previous_reading = float(row["previous_reading"])
                except (KeyError, TypeError, ValueError):
                    pass
                
                current_reading = None
                try:
                    if row["current_reading"] is not None:
                        current_reading = float(row["current_reading"])
                except (KeyError, TypeError, ValueError):
                    pass
                
                volume = None
                try:
                    if row["volume"] is not None:
                        volume = float(row["volume"])
                except (KeyError, TypeError, ValueError):
                    pass
                
                payments.append({
                    "id": row["id"],
                    "payment_type_id": payment_type_id,
                    "payment_type_name": payment_type_name,
                    "system_name": system_name,
                    "amount": float(row["amount"]) if row["amount"] else 0.0,
                    "payment_date": row["payment_date"],
                    "period": row["period"],
                    "receipt_number": row["receipt_number"],
                    "payment_method": row["payment_method"],
                    "notes": row["notes"],
                    "previous_reading": previous_reading,
                    "current_reading": current_reading,
                    "volume": volume,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })
            return payments
        except Exception as err:
            _LOGGER.error("Error getting payments: %s", err)
            return []

    def get_all_payment_types(self) -> list[dict[str, Any]]:
        """Get all payment types from constants (not from database)."""
        # Payment types are now stored in constants, not in database
        types = []
        for type_id, system_name in PAYMENT_TYPES.items():
            types.append({
                "id": type_id,
                "system_name": system_name,
                "name": system_name,  # Translation should be done in UI/coordinator
                "description": None,
                "is_active": True,
                "is_system": True,
                "created_at": None,
                "updated_at": None,
            })
        return types

