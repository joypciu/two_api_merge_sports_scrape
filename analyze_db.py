#!/usr/bin/env python3
"""
Analyze database to identify columns with null/empty values
"""
import sqlite3
import os

def analyze_database():
    db_path = 'sports_data_v2.db'
    if not os.path.exists(db_path):
        print("Database file not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("Database Analysis:")
    print("=" * 50)

    for table in tables:
        table_name = table[0]
        print(f"\n{table_name}:")

        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"  Columns: {len(columns)}")

        # Get record count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Records: {count}")

        if count > 0:
            print("  Column analysis:")

            # Analyze each column
            for col in columns:
                col_name = col[1]
                col_type = col[2]

                # Count null/empty values
                if col_type.upper() in ['TEXT', 'VARCHAR', 'CHAR']:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL OR {col_name} = ''")
                elif col_type.upper() in ['INTEGER', 'REAL', 'NUMERIC']:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL OR {col_name} = 0")
                else:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")

                null_count = cursor.fetchone()[0]
                null_percentage = (null_count / count) * 100 if count > 0 else 0

                status = "ALWAYS NULL/EMPTY" if null_percentage == 100 else f"{null_percentage:.1f}% null/empty"
                print(f"    {col_name}: {status}")

    conn.close()

if __name__ == '__main__':
    analyze_database()