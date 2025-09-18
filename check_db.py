#!/usr/bin/env python3
import sqlite3
import os

# Check database content
db_path = 'app/sports_data_v2.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

# Check soccer table
cursor.execute("SELECT COUNT(*) FROM soccer_2025_09_18")
total_count = cursor.fetchone()[0]
print(f"Total matches in soccer_2025_09_18: {total_count}")

# Check matches with event_count > 0
cursor.execute("SELECT COUNT(*) FROM soccer_2025_09_18 WHERE event_count > 0")
non_zero_count = cursor.fetchone()[0]
print(f"Matches with event_count > 0: {non_zero_count}")

# Show some examples
cursor.execute("SELECT match_id, event_count FROM soccer_2025_09_18 WHERE event_count > 0 LIMIT 5")
results = cursor.fetchall()
print("Examples:")
for match_id, event_count in results:
    print(f"  {match_id}: {event_count}")

# Show event_count distribution
cursor.execute("SELECT event_count, COUNT(*) FROM soccer_2025_09_18 GROUP BY event_count ORDER BY event_count")
distribution = cursor.fetchall()
print("Event count distribution:")
for event_count, count in distribution:
    print(f"  {event_count}: {count} matches")

conn.close()