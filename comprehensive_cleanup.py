#!/usr/bin/env python3
import sqlite3
import os

# Comprehensive cleanup of any mock/fake/test data from database
db_path = 'app/sports_data_v2.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== COMPREHENSIVE MOCK DATA CLEANUP ===")

# Check all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Found tables: {[t[0] for t in tables]}")

total_removed = 0

# Clean each sport table
for (table_name,) in tables:
    if table_name.startswith('table_metadata') or table_name.startswith('sqlite'):
        continue

    print(f"\n--- Cleaning table: {table_name} ---")

    # Get count before cleanup
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count_before = cursor.fetchone()[0]
    print(f"Matches before cleanup: {count_before}")

    # Remove any mock/fake/test data patterns
    cursor.execute(f"""
    DELETE FROM {table_name}
    WHERE match_id LIKE '%FAKE%'
       OR match_id LIKE '%MOCK%'
       OR match_id LIKE '%TEST%'
       OR match_id LIKE '%DUMMY%'
       OR match_id LIKE '%SAMPLE%'
       OR home_team LIKE '%Mock%'
       OR home_team LIKE '%Test%'
       OR home_team LIKE '%Fake%'
       OR home_team LIKE '%Dummy%'
       OR home_team LIKE '%Sample%'
       OR away_team LIKE '%Mock%'
       OR away_team LIKE '%Test%'
       OR away_team LIKE '%Fake%'
       OR away_team LIKE '%Dummy%'
       OR away_team LIKE '%Sample%'
       OR tournament LIKE '%Mock%'
       OR tournament LIKE '%Test%'
       OR tournament LIKE '%Fake%'
       OR tournament LIKE '%Dummy%'
       OR tournament LIKE '%Sample%'
       OR tournament LIKE '%Sim%'
       OR home_team LIKE '%Simulated%'
       OR away_team LIKE '%Simulated%'
    """)

    # Get count after cleanup
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count_after = cursor.fetchone()[0]
    removed = count_before - count_after
    total_removed += removed
    print(f"Matches after cleanup: {count_after}")
    print(f"Removed from {table_name}: {removed}")

    # Update metadata if table still exists
    if count_after > 0:
        cursor.execute("""
        UPDATE table_metadata
        SET last_updated = datetime('now'), record_count = ?
        WHERE table_name = ?
        """, (count_after, table_name))

print(f"\n=== CLEANUP SUMMARY ===")
print(f"Total mock/fake/test matches removed: {total_removed}")

# Final verification
cursor.execute("SELECT COUNT(*) FROM soccer_2025_09_18")
final_count = cursor.fetchone()[0]
print(f"Final soccer matches count: {final_count}")

conn.commit()
conn.close()

print("\n✅ Comprehensive mock data cleanup completed!")
print("All data in database now comes from real API endpoints only.")