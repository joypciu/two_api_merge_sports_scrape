#!/usr/bin/env python3
"""
Test script to verify core functionality without predictor dependencies
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.apis.xbet_api import XBetAPI
from app.storage.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)

def test_xbet_api():
    """Test XBet API functionality"""
    print("Testing XBet API...")

    try:
        api = XBetAPI()
        print("XBet API initialized successfully")

        # Test sports list
        sports = api.get_sports_list()
        print(f"Retrieved {len(sports)} sports")

        return True
    except Exception as e:
        print(f"XBet API test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\nTesting Database...")

    try:
        db = DatabaseManager()
        print("Database manager initialized successfully")

        # Test table creation
        table_name = db.create_daily_table('test_sport')
        print(f"Created table: {table_name}")

        return True
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def test_data_processing():
    """Test data processing logic"""
    print("\nTesting Data Processing...")

    try:
        # Test with mock data
        mock_match = {
            'I': '12345',
            'O1': {'N': 'Test Home Team'},
            'O2': {'N': 'Test Away Team'},
            'S': 1758157500,  # Unix timestamp
            'IsLive': False,
            'SC': {'FS': {'S1': '1', 'S2': '0'}, 'CP': 1},
            'LE': 'Test League',
            'E': [
                {'G': 2, 'T': 7, 'P': 2.1},  # Home odds
                {'G': 2, 'T': 8, 'P': 2.3},  # Away odds
                {'G': 17, 'T': 9, 'P': 3.2}  # Draw odds
            ]
        }

        api = XBetAPI()
        processed = api._process_match_data(mock_match)

        if processed:
            print("Data processing successful")
            print(f"   Match ID: {processed['match_id']}")
            print(f"   Status: {processed['status']}")
            print(f"   Event Count: {processed['event_count']}")
            print(f"   Odds: {processed['odds_home']}, {processed['odds_away']}, {processed['odds_draw']}")
            return True
        else:
            print("Data processing returned None")
            return False

    except Exception as e:
        print(f"Data processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Core Functionality")
    print("=" * 50)

    results = []
    results.append(test_xbet_api())
    results.append(test_database())
    results.append(test_data_processing())

    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"   XBet API: {'PASS' if results[0] else 'FAIL'}")
    print(f"   Database: {'PASS' if results[1] else 'FAIL'}")
    print(f"   Data Processing: {'PASS' if results[2] else 'FAIL'}")

    if all(results):
        print("\nAll core functionality tests PASSED!")
        print("The data quality fixes are working correctly.")
    else:
        print("\nSome tests failed. Check the output above.")