#!/usr/bin/env python3
"""
Test script to verify database insertion fix
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from storage.database import DatabaseManager

def test_database_insertion():
    """Test that database insertion works with the fixed schema"""
    print("=== TESTING DATABASE INSERTION FIX ===")

    # Create database manager
    db_manager = DatabaseManager('test_sports_data.db')

    # Sample match data similar to what APIs return
    sample_matches = [
        {
            'match_id': 'test_match_1',
            'home_team': 'Manchester City',
            'away_team': 'Arsenal',
            'score': '2:1',
            'status': 'live',
            'period': 2,
            'tournament': 'Premier League',
            'odds_home': 1.85,
            'odds_away': 3.20,
            'odds_draw': 3.50,
            'event_count': 15,
            'start_time': 1638360000,
            'data_source': 'test',
            'home_team_id': 123,
            'away_team_id': 456,
            'stoppage_time': False,
            'half_time': True
        },
        {
            'match_id': 'test_match_2',
            'home_team': 'Barcelona',
            'away_team': 'Real Madrid',
            'score': '0:0',
            'status': 'pregame',
            'period': 1,
            'tournament': 'La Liga',
            'odds_home': 2.10,
            'odds_away': 2.80,
            'odds_draw': 3.20,
            'event_count': 8,
            'start_time': 1638370000,
            'data_source': 'test',
            'home_team_id': 789,
            'away_team_id': 101,
            'stoppage_time': False,
            'half_time': False
        }
    ]

    # Test insertion
    try:
        inserted = db_manager.insert_match_data('soccer', sample_matches)
        print(f"SUCCESS: Inserted {inserted} matches")

        # Verify data was inserted
        matches = db_manager.get_matches_by_date('soccer', db_manager.get_table_name('soccer').split('_')[-1])
        print(f"VERIFIED: Retrieved {len(matches)} matches from database")

        for match in matches:
            print(f"  - {match['home_team']} vs {match['away_team']}: {match['score']}")

        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_database_insertion()
    sys.exit(0 if success else 1)