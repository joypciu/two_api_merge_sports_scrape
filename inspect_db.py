import sqlite3
import json

def inspect_database():
    conn = sqlite3.connect('sports_data_v2.db')
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("=== DATABASE INSPECTION ===")
    print(f"Tables found: {[t[0] for t in tables]}")

    for table_name, in tables:
        print(f"\n=== TABLE: {table_name} ===")

        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Columns ({len(columns)}):")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")

        # Get record count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Records: {count}")

        if count > 0:
            # Sample some records to see data structure
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_rows = cursor.fetchall()
            print("Sample data:")
            for i, row in enumerate(sample_rows):
                print(f"  Row {i+1}: {row}")

    conn.close()

if __name__ == "__main__":
    inspect_database()