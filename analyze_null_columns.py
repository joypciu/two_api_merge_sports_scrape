import sqlite3
import json
from collections import defaultdict

def analyze_null_columns():
    """Analyze which columns are always null or have low usage"""
    conn = sqlite3.connect('sports_data_v2.db')
    cursor = conn.cursor()

    # Get all sport tables (exclude metadata)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_%' AND name NOT LIKE 'table_metadata%' AND name NOT LIKE 'sqlite%'")
    tables = cursor.fetchall()

    print("=== NULL COLUMN ANALYSIS ===")

    column_stats = defaultdict(lambda: {'total': 0, 'null': 0, 'non_null': 0})

    for table_name, in tables:
        print(f"\nAnalyzing table: {table_name}")

        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        # Get sample data (if any exists)
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]

        if count == 0:
            print(f"  No data in table {table_name}")
            continue

        # Analyze each column for null values
        for col_name in column_names:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL OR {col_name} = ''")
            null_count = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NOT NULL AND {col_name} != ''")
            non_null_count = cursor.fetchone()[0]

            column_stats[col_name]['total'] += count
            column_stats[col_name]['null'] += null_count
            column_stats[col_name]['non_null'] += non_null_count

            null_percentage = (null_count / count * 100) if count > 0 else 0
            print(".1f")

    print("\n=== SUMMARY: Columns by null percentage ===")
    sorted_columns = sorted(column_stats.items(), key=lambda x: (x[1]['null'] / x[1]['total']) if x[1]['total'] > 0 else 0, reverse=True)

    for col_name, stats in sorted_columns:
        if stats['total'] > 0:
            null_pct = stats['null'] / stats['total'] * 100
            print(".1f")

    # Identify columns that are always null
    always_null = [col for col, stats in column_stats.items() if stats['total'] > 0 and stats['non_null'] == 0]
    print(f"\n=== COLUMNS ALWAYS NULL: {len(always_null)} ===")
    for col in always_null:
        print(f"  {col}")

    # Identify columns with high null percentage (>90%)
    high_null = [col for col, stats in column_stats.items() if stats['total'] > 0 and (stats['null'] / stats['total']) > 0.9]
    print(f"\n=== COLUMNS >90% NULL: {len(high_null)} ===")
    for col in high_null:
        null_pct = column_stats[col]['null'] / column_stats[col]['total'] * 100
        print(".1f")

    conn.close()

    return always_null, high_null

if __name__ == "__main__":
    analyze_null_columns()