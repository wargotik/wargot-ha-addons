"""Database module for storing sensors."""
import sqlite3
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_LOGGER = logging.getLogger(__name__)

DB_PATH = "/data/alarmme.db"


class SensorDatabase:
    """Database manager for sensors."""
    
    def __init__(self, db_path: str = DB_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists."""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Initialize database schema."""
        import time
        max_retries = 5
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # Add timeout to prevent database locked errors
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                cursor = conn.cursor()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    _LOGGER.warning(
                        "[database] Database is locked, retrying in %.1f seconds (attempt %d/%d)...",
                        retry_delay, attempt + 1, max_retries
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    _LOGGER.error("[database] Failed to connect to database after %d attempts: %s", attempt + 1, e)
                    raise
        
        try:
            
            # Create sensors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensors (
                    entity_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    device_class TEXT NOT NULL,
                    enabled_in_away_mode INTEGER DEFAULT 0,
                    enabled_in_night_mode INTEGER DEFAULT 0,
                    last_triggered_at TIMESTAMP,
                    area TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add last_triggered_at column if it doesn't exist (for existing databases)
            try:
                cursor.execute("ALTER TABLE sensors ADD COLUMN last_triggered_at TIMESTAMP")
            except sqlite3.OperationalError:
                # Column already exists, ignore
                pass
            
            # Add area column if it doesn't exist (for existing databases)
            try:
                cursor.execute("ALTER TABLE sensors ADD COLUMN area TEXT")
            except sqlite3.OperationalError:
                # Column already exists, ignore
                pass
            
            # Create index on device_class for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_device_class 
                ON sensors(device_class)
            """)
            
            conn.commit()
            conn.close()
            _LOGGER.info("[database] Database initialized successfully")
        except Exception as err:
            _LOGGER.error("[database] Error initializing database: %s", err, exc_info=True)
            raise
    
    def save_sensor(
        self, 
        entity_id: str, 
        name: str, 
        device_class: str,
        enabled_in_away_mode: bool = False,
        enabled_in_night_mode: bool = False,
        area: Optional[str] = None
    ) -> bool:
        """Save or update sensor in database."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO sensors 
                (entity_id, name, device_class, enabled_in_away_mode, enabled_in_night_mode, area, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                entity_id,
                name,
                device_class,
                1 if enabled_in_away_mode else 0,
                1 if enabled_in_night_mode else 0,
                area
            ))
            
            conn.commit()
            conn.close()
            _LOGGER.debug("[database] Saved sensor: %s (%s) - area: %s", name, entity_id, area)
            return True
        except Exception as err:
            _LOGGER.error("[database] Error saving sensor %s: %s", entity_id, err, exc_info=True)
            return False
    
    def get_sensor(self, entity_id: str) -> Optional[Dict]:
        """Get sensor from database by entity_id."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT entity_id, name, device_class, enabled_in_away_mode, enabled_in_night_mode, last_triggered_at, area
                FROM sensors
                WHERE entity_id = ?
            """, (entity_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "entity_id": row[0],
                    "name": row[1],
                    "device_class": row[2],
                    "enabled_in_away_mode": bool(row[3]),
                    "enabled_in_night_mode": bool(row[4]),
                    "last_triggered_at": row[5] if len(row) > 5 else None,
                    "area": row[6] if len(row) > 6 else None
                }
            return None
        except Exception as err:
            _LOGGER.error("[database] Error getting sensor %s: %s", entity_id, err, exc_info=True)
            return None
    
    def get_all_sensors(self) -> List[Dict]:
        """Get all sensors from database."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT entity_id, name, device_class, enabled_in_away_mode, enabled_in_night_mode, last_triggered_at, area
                FROM sensors
                ORDER BY name
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "entity_id": row[0],
                    "name": row[1],
                    "device_class": row[2],
                    "enabled_in_away_mode": bool(row[3]),
                    "enabled_in_night_mode": bool(row[4]),
                    "last_triggered_at": row[5] if len(row) > 5 else None,
                    "area": row[6] if len(row) > 6 else None
                }
                for row in rows
            ]
        except Exception as err:
            _LOGGER.error("[database] Error getting all sensors: %s", err, exc_info=True)
            return []
    
    def update_sensor_modes(
        self, 
        entity_id: str, 
        enabled_in_away_mode: Optional[bool] = None,
        enabled_in_night_mode: Optional[bool] = None
    ) -> bool:
        """Update sensor mode settings."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if enabled_in_away_mode is not None:
                updates.append("enabled_in_away_mode = ?")
                params.append(1 if enabled_in_away_mode else 0)
            
            if enabled_in_night_mode is not None:
                updates.append("enabled_in_night_mode = ?")
                params.append(1 if enabled_in_night_mode else 0)
            
            if not updates:
                conn.close()
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(entity_id)
            
            query = f"""
                UPDATE sensors 
                SET {', '.join(updates)}
                WHERE entity_id = ?
            """
            
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            
            _LOGGER.debug("[database] Updated sensor modes: %s", entity_id)
            return True
        except Exception as err:
            _LOGGER.error("[database] Error updating sensor modes %s: %s", entity_id, err, exc_info=True)
            return False
    
    def delete_sensor(self, entity_id: str) -> bool:
        """Delete sensor from database."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM sensors WHERE entity_id = ?", (entity_id,))
            conn.commit()
            conn.close()
            
            _LOGGER.debug("[database] Deleted sensor: %s", entity_id)
            return True
        except Exception as err:
            _LOGGER.error("[database] Error deleting sensor %s: %s", entity_id, err, exc_info=True)
            return False
    
    def is_sensor_saved(self, entity_id: str) -> bool:
        """Check if sensor is saved in database."""
        return self.get_sensor(entity_id) is not None
    
    def record_sensor_trigger(self, entity_id: str, last_changed: str = None) -> bool:
        """Record sensor trigger using last_changed timestamp from Home Assistant."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            # Use last_changed from HA if provided, otherwise use current timestamp
            if last_changed:
                cursor.execute("""
                    UPDATE sensors 
                    SET last_triggered_at = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE entity_id = ?
                """, (last_changed, entity_id))
            else:
                cursor.execute("""
                    UPDATE sensors 
                    SET last_triggered_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE entity_id = ?
                """, (entity_id,))
            
            conn.commit()
            conn.close()
            
            _LOGGER.debug("[database] Recorded sensor trigger: %s (last_changed: %s)", entity_id, last_changed)
            return True
        except Exception as err:
            _LOGGER.error("[database] Error recording sensor trigger %s: %s", entity_id, err, exc_info=True)
            return False

