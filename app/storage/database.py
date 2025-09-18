"""
Improved database manager with day-by-day table structure
Eliminates null columns and provides efficient data storage
"""
import sqlite3
import logging
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

class DatabaseManager:
    """Manages day-by-day table structure for efficient data storage"""

    def __init__(self, db_path: str = 'sports_data_v2.db'):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database with metadata tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create metadata table for tracking table information
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS table_metadata (
                    table_name TEXT PRIMARY KEY,
                    sport TEXT,
                    date_created DATE,
                    last_updated DATETIME,
                    record_count INTEGER DEFAULT 0
                )
            ''')

            # Create index for faster metadata queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metadata_sport_date
                ON table_metadata (sport, date_created)
            ''')

            conn.commit()

    def get_table_name(self, sport: str, target_date: Optional[date] = None) -> str:
        """Generate table name for sport and date"""
        if target_date is None:
            target_date = date.today()

        return f"{sport}_{target_date.strftime('%Y_%m_%d')}"

    def create_daily_table(self, sport: str, target_date: Optional[date] = None) -> str:
        """Create optimized daily table for a sport with expanded fields"""
        table_name = self.get_table_name(sport, target_date)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if table exists and drop it if schema might be wrong
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone():
                logging.info(f"INFO: Dropping existing table {table_name} to ensure correct schema")
                cursor.execute(f"DROP TABLE {table_name}")

        # Optimized schema - only essential columns (20 total)
        schema = f'''
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                score TEXT,
                status TEXT,
                period INTEGER DEFAULT 1,
                tournament TEXT,
                sport TEXT NOT NULL,

                -- Odds data (nullable but structured)
                odds_home REAL,
                odds_away REAL,
                odds_draw REAL,

                -- Match statistics
                event_count INTEGER DEFAULT 0,
                start_time INTEGER,

                -- Team information (only IDs)
                home_team_id INTEGER,
                away_team_id INTEGER,

                -- Essential match metadata
                stoppage_time BOOLEAN DEFAULT 0,
                half_time BOOLEAN DEFAULT 0,

                -- Metadata
                data_source TEXT DEFAULT 'iscjxxqgmb'
            )
        '''

        # Create indexes separately for SQLite compatibility
        index_sql = f'''
            CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp ON {table_name} (timestamp);
            CREATE INDEX IF NOT EXISTS idx_{table_name}_teams ON {table_name} (home_team, away_team);
            CREATE INDEX IF NOT EXISTS idx_{table_name}_status ON {table_name} (status);
            CREATE INDEX IF NOT EXISTS idx_{table_name}_match_id ON {table_name} (match_id);
        '''

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(schema)

            # Create indexes separately
            for index_stmt in index_sql.strip().split(';'):
                if index_stmt.strip():
                    cursor.execute(index_stmt.strip())

            # Update metadata
            cursor.execute('''
                INSERT OR REPLACE INTO table_metadata
                (table_name, sport, date_created, last_updated, record_count)
                VALUES (?, ?, ?, ?, COALESCE((SELECT record_count FROM table_metadata WHERE table_name = ?), 0))
            ''', (table_name, sport, date.today(), datetime.now(), table_name))

            conn.commit()

        logging.info(f"SUCCESS: Created/verified table: {table_name}")
        return table_name

    def insert_match_data(self, sport: str, matches: List[Dict], target_date: Optional[date] = None) -> int:
        """Insert match data into appropriate daily table"""
        if not matches:
            return 0

        table_name = self.create_daily_table(sport, target_date)

        inserted_count = 0

        with self.get_connection() as conn:
            cursor = conn.cursor()

            for match in matches:
                try:
                    # Clean and validate data
                    match_data = self._clean_match_data(match)
    
                    # Debug: Log event_count for first few matches
                    if inserted_count < 5 and match_data.get('event_count', 0) > 0:
                        logging.info(f"DB Insert: Match {match_data['match_id']} has event_count: {match_data['event_count']}")

                    # Insert or update match data with optimized fields (18 columns including sport)
                    values = (
                        match_data['match_id'],
                        match_data['home_team'],
                        match_data['away_team'],
                        match_data['score'],
                        match_data['status'],
                        match_data['period'],
                        match_data['tournament'],
                        sport,
                        match_data['odds_home'],
                        match_data['odds_away'],
                        match_data['odds_draw'],
                        match_data['event_count'],
                        match_data['start_time'],
                        match_data['data_source'],
                        # Team information (only IDs)
                        match_data.get('home_team_id'),
                        match_data.get('away_team_id'),
                        # Essential match metadata
                        match_data.get('stoppage_time', False),
                        match_data.get('half_time', False)
                    )

                    # Verify the values count matches columns before insertion
                    expected_columns = 18
                    if len(values) != expected_columns:
                        logging.error(f"Column count mismatch: expected {expected_columns}, got {len(values)}")
                        continue

                    cursor.execute(f'''
                        INSERT OR REPLACE INTO {table_name}
                        (match_id, home_team, away_team, score, status, period, tournament, sport,
                         odds_home, odds_away, odds_draw, event_count, start_time, data_source,
                         home_team_id, away_team_id, stoppage_time, half_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', values)

                    inserted_count += 1

                except Exception as e:
                    logging.error(f"Failed to insert match {match.get('match_id', 'unknown')}: {e}")
                    continue

            # Update metadata with new count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            new_count = cursor.fetchone()[0]

            cursor.execute('''
                UPDATE table_metadata
                SET last_updated = ?, record_count = ?
                WHERE table_name = ?
            ''', (datetime.now(), new_count, table_name))

            conn.commit()

        logging.info(f"SUCCESS: Inserted {inserted_count} matches into {table_name}")
        return inserted_count

    def _clean_match_data(self, match: Dict) -> Dict:
        """Clean and validate match data with optimized fields (18 columns), providing defaults for missing fields"""
        # Validate status field
        status = match.get('status', 'pregame')
        if status not in ['pregame', 'live']:
            status = 'pregame'  # Default to pregame for unknown statuses

        # Create a completely new dictionary with ONLY the fields that exist in the optimized database schema (18 columns)
        # This ensures no extra fields from the API response are included and matches the optimized schema
        cleaned_data = {
            # Core match data (columns 1-14)
            'match_id': str(match.get('match_id', '')),
            'home_team': match.get('home_team', '').strip(),
            'away_team': match.get('away_team', '').strip(),
            'score': match.get('score', ''),
            'status': status,
            'period': int(match.get('period', 1)),
            'tournament': match.get('tournament', ''),
            'sport': match.get('sport', ''),  # This will be set by the calling function
            'odds_home': match.get('odds_home'),
            'odds_away': match.get('odds_away'),
            'odds_draw': match.get('odds_draw'),
            'event_count': int(match.get('event_count', 0)),
            'start_time': match.get('start_time', 0),
            'data_source': match.get('data_source', 'iscjxxqgmb'),

            # Team information (columns 15-16) - only IDs, removed logos
            'home_team_id': match.get('home_team_id'),
            'away_team_id': match.get('away_team_id'),

            # Essential match metadata (columns 17-18) - kept only essential ones
            'stoppage_time': bool(match.get('stoppage_time', False)),
            'half_time': bool(match.get('half_time', False))
        }

        return cleaned_data

    def get_matches_by_date(self, sport: str, target_date: date) -> List[Dict]:
        """Get all matches for a specific sport and date"""
        table_name = self.get_table_name(sport, target_date)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                return []

            cursor.execute(f"SELECT * FROM {table_name} ORDER BY timestamp DESC")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            return [dict(zip(columns, row)) for row in rows]

    def get_recent_matches(self, sport: str, days: int = 7) -> List[Dict]:
        """Get recent matches across multiple days"""
        all_matches = []

        for i in range(days):
            target_date = date.today() - timedelta(days=i)
            matches = self.get_matches_by_date(sport, target_date)
            all_matches.extend(matches)

        return all_matches

    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        stats = {
            'total_tables': 0,
            'total_records': 0,
            'sports_covered': set(),
            'date_range': {'oldest': None, 'newest': None}
        }

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get table metadata
            cursor.execute("SELECT * FROM table_metadata ORDER BY date_created")
            metadata_rows = cursor.fetchall()

            if metadata_rows:
                stats['total_tables'] = len(metadata_rows)

                for row in metadata_rows:
                    table_name, sport, date_created, last_updated, record_count = row
                    stats['total_records'] += record_count or 0
                    stats['sports_covered'].add(sport)

                    if stats['date_range']['oldest'] is None or date_created < stats['date_range']['oldest']:
                        stats['date_range']['oldest'] = date_created
                    if stats['date_range']['newest'] is None or date_created > stats['date_range']['newest']:
                        stats['date_range']['newest'] = date_created

        stats['sports_covered'] = list(stats['sports_covered'])
        return stats

    def cleanup_old_data(self, retention_days: int = 90):
        """Remove tables older than retention period"""
        cutoff_date = date.today() - timedelta(days=retention_days)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Find old tables
            cursor.execute("SELECT table_name FROM table_metadata WHERE date_created < ?", (cutoff_date,))
            old_tables = cursor.fetchall()

            for (table_name,) in old_tables:
                try:
                    cursor.execute(f"DROP TABLE {table_name}")
                    cursor.execute("DELETE FROM table_metadata WHERE table_name = ?", (table_name,))
                    logging.info(f"CLEANUP: Dropped old table: {table_name}")
                except Exception as e:
                    logging.error(f"Failed to drop table {table_name}: {e}")

            conn.commit()

    def migrate_table_schema(self, table_name: str):
        """Migrate existing table to new schema (replace is_live and confidence with event_count)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                # Check if table exists and has old schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]

                if 'is_live' in column_names and 'confidence' in column_names:
                    logging.info(f"🔄 Migrating table {table_name} to new schema...")

                    # Create temporary table with new schema
                    temp_table = f"{table_name}_temp_migration"
                    new_schema = f'''
                        CREATE TABLE {temp_table} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            match_id TEXT UNIQUE NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            home_team TEXT NOT NULL,
                            away_team TEXT NOT NULL,
                            score TEXT,
                            status TEXT,
                            period INTEGER DEFAULT 1,
                            tournament TEXT,
                            sport TEXT NOT NULL,
                            odds_home REAL,
                            odds_away REAL,
                            odds_draw REAL,
                            event_count INTEGER DEFAULT 0,
                            start_time INTEGER,
                            data_source TEXT DEFAULT '1xbet'
                        )
                    '''

                    cursor.execute(new_schema)

                    # Copy data from old table to new table, converting status values
                    cursor.execute(f'''
                        INSERT INTO {temp_table}
                        (id, match_id, timestamp, home_team, away_team, score, status, period,
                         tournament, sport, odds_home, odds_away, odds_draw, event_count,
                         start_time, data_source)
                        SELECT id, match_id, timestamp, home_team, away_team, score,
                               CASE
                                   WHEN status = 'scheduled' THEN 'pregame'
                                   WHEN status IN ('pregame', 'live') THEN status
                                   ELSE 'pregame'
                               END as status,
                               period, tournament, sport, odds_home, odds_away, odds_draw, 0,
                               start_time, data_source
                        FROM {table_name}
                    ''')

                    # Drop old table and rename new table
                    cursor.execute(f"DROP TABLE {table_name}")
                    cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")

                    # Recreate indexes
                    index_sql = f'''
                        CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp ON {table_name} (timestamp);
                        CREATE INDEX IF NOT EXISTS idx_{table_name}_teams ON {table_name} (home_team, away_team);
                        CREATE INDEX IF NOT EXISTS idx_{table_name}_status ON {table_name} (status);
                        CREATE INDEX IF NOT EXISTS idx_{table_name}_match_id ON {table_name} (match_id);
                    '''
                    for index_stmt in index_sql.strip().split(';'):
                        if index_stmt.strip():
                            cursor.execute(index_stmt.strip())

                    conn.commit()
                    logging.info(f"✅ Successfully migrated table {table_name}")
                else:
                    logging.info(f"ℹ️ Table {table_name} already has new schema or doesn't exist")

            except Exception as e:
                logging.error(f"❌ Failed to migrate table {table_name}: {e}")
                conn.rollback()

    def migrate_all_tables(self):
        """Migrate all existing tables to new schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get all sport tables (excluding metadata tables)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_%'")
            tables = cursor.fetchall()

            for (table_name,) in tables:
                if not table_name.startswith('table_metadata') and not table_name.startswith('sqlite'):
                    self.migrate_table_schema(table_name)

    def optimize_database(self):
        """Optimize database performance"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Run optimization commands
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")

            logging.info("SUCCESS: Database optimized")