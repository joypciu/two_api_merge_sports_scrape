#!/usr/bin/env python3
import sqlite3
import os

# Clean up fake data from database
db_path = 'app/sports_data_v2.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Before cleanup:")
cursor.execute("SELECT COUNT(*) FROM soccer_2025_09_18")
total_before = cursor.fetchone()[0]
print(f"Total matches: {total_before}")

# Delete fake matches
cursor.execute("""
DELETE FROM soccer_2025_09_18
WHERE match_id LIKE '%FAKE%'
   OR home_team LIKE '%Simulated%'
   OR away_team LIKE '%Test%'
   OR tournament LIKE '%Sim%'
   OR home_team LIKE '%Mock%'
   OR away_team LIKE '%Mock%'
""")

# Update metadata
cursor.execute("SELECT COUNT(*) FROM soccer_2025_09_18")
new_count = cursor.fetchone()[0]

cursor.execute("""
UPDATE table_metadata
SET last_updated = datetime('now'), record_count = ?
WHERE table_name = 'soccer_2025_09_18'
""", (new_count,))

conn.commit()

print("After cleanup:")
print(f"Total matches: {new_count}")
print(f"Removed {total_before - new_count} fake matches")

conn.close()
print("✅ Fake data cleanup completed!")