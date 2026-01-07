"""Database utilities for Asana simulation."""
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for Asana simulation."""
    
    def __init__(self, db_path: str = "output/asana_simulation.sqlite"):
        self.db_path = db_path
        self.conn = None
        
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def connect(self):
        """Establish database connection."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")
        
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def initialize_schema(self, schema_path: str = "schema.sql", drop_existing: bool = False):
        """Initialize database schema from SQL file."""
        if drop_existing:
            # Drop all existing tables
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
            self.conn.commit()
            logger.info("Dropped existing tables")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        self.conn.executescript(schema_sql)
        self.conn.commit()
        logger.info("Database schema initialized")
        
    def insert_batch(self, table: str, records: List[Dict[str, Any]]):
        """Insert multiple records into a table."""
        if not records:
            return
            
        columns = records[0].keys()
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        values = [tuple(record[col] for col in columns) for record in records]
        
        cursor = self.conn.cursor()
        cursor.executemany(sql, values)
        self.conn.commit()
        
        logger.info(f"Inserted {len(records)} records into {table}")
        
    def insert_one(self, table: str, record: Dict[str, Any]):
        """Insert a single record into a table."""
        self.insert_batch(table, [record])
        
    def query(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a query and return results."""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
        
    def get_count(self, table: str) -> int:
        """Get count of records in a table."""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]
        
    def table_exists(self, table: str) -> bool:
        """Check if a table exists."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        return cursor.fetchone() is not None