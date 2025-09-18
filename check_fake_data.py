#!/usr/bin/env python3
import sqlite3
import os

# Check for fake data in database
db_path = 'app/sports_data_v2.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for fake matches
cursor.execute("""
SELECT match_id, home_team, away_team, tournament
FROM soccer_2025_09_18
WHERE match_id LIKE '%FAKE%'
   OR home_team LIKE '%Simulated%'
   OR away_team LIKE '%Test%'
   OR tournament LIKE '%Sim%'
   OR home_team LIKE '%Mock%'
   OR away_team LIKE '%Mock%'
""")

fake_results = cursor.fetchall()
print(f"Fake/mock matches found: {len(fake_results)}")
for row in fake_results:
    print(f"  {row}")

# Check total matches
cursor.execute("SELECT COUNT(*) FROM soccer_2025_09_18")
total = cursor.fetchone()[0]
print(f"Total matches in database: {total}")

conn.close()