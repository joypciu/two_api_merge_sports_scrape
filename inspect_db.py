import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('app/sports_data_v2.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"- {table[0]}")

print("\n" + "="*50)

# Check recent tables
recent_tables = ['soccer_2025_09_17', 'basketball_2025_09_17', 'cricket_2025_09_17']

for table_name in recent_tables:
    print(f"\nTable: {table_name}")
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Records: {count}")

        if count > 0:
            # Get sample records
            cursor.execute(f"SELECT match_id, home_team, away_team, data_source, is_live, score FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            print("Sample records:")
            for row in rows:
                print(f"  {row}")
    except sqlite3.Error as e:
        print(f"Error querying table: {e}")

conn.close()