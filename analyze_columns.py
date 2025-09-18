#!/usr/bin/env python3
"""
Analyze database columns to identify those that are consistently null/empty
"""
import sqlite3
import os

def analyze_columns():
    db_path = 'sports_data_v2.db'
    if not os.path.exists(db_path):
        print("Database file not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all sport tables (exclude metadata tables)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_%' AND name NOT LIKE 'table_metadata%' AND name NOT LIKE 'sqlite%'")
    tables = cursor.fetchall()

    print("Column Analysis Across All Sport Tables:")
    print("=" * 60)

    # Dictionary to track null/empty percentages across all tables
    column_stats = {}

    for table in tables:
        table_name = table[0]
        print(f"\nAnalyzing {table_name}:")

        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

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
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL OR {col_name} = '' OR {col_name} = 'None'")
                elif col_type.upper() in ['INTEGER', 'REAL', 'NUMERIC']:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL OR {col_name} = 0")
                elif col_type.upper() == 'BOOLEAN':
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL OR {col_name} = 0 OR {col_name} = 'False'")
                else:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")

                null_count = cursor.fetchone()[0]
                null_percentage = (null_count / count) * 100 if count > 0 else 0

                # Track stats across tables
                if col_name not in column_stats:
                    column_stats[col_name] = []
                column_stats[col_name].append(null_percentage)

                status = "ALWAYS NULL/EMPTY" if null_percentage == 100 else f"{null_percentage:.1f}% null/empty"
                print(f"    {col_name}: {status}")

    # Summary analysis
    print("\n" + "=" * 60)
    print("SUMMARY: Columns that are ALWAYS null/empty across ALL tables:")
    print("=" * 60)

    always_null_columns = []
    for col_name, percentages in column_stats.items():
        if all(p == 100.0 for p in percentages):
            always_null_columns.append(col_name)
            print(f"  - {col_name}")

    print(f"\nTotal columns that are always null/empty: {len(always_null_columns)}")

    print("\n" + "=" * 60)
    print("RECOMMENDATION: Drop these columns to optimize database:")
    print("=" * 60)

    for col in always_null_columns:
        print(f"  ALTER TABLE table_name DROP COLUMN {col};")

    print(f"\nEstimated space savings: ~{len(always_null_columns)} columns per table")

    conn.close()

    return always_null_columns

if __name__ == '__main__':
    analyze_columns()