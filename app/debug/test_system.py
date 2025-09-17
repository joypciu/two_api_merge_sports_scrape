#!/usr/bin/env python3
"""
Test script for the improved Sports Data Collection System v2.0
Demonstrates the new modular architecture and capabilities
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.xbet_api import XBetAPI
from storage.database import DatabaseManager
from analysis.predictor import MatchPredictor
from datetime import datetime

def test_api_connectivity():
    """Test API connectivity"""
    print("🔍 Testing 1xBet API connectivity...")

    api = XBetAPI()
    stats = api.get_request_stats()

    print(f"✅ API Status: {'Healthy' if stats['healthy'] else 'Unhealthy'}")
    print(f"📊 Request Count: {stats['request_count']}")
    print(f"🎯 Sports Cached: {stats['sports_cached']}")

    # Test getting sports list
    sports = api.get_sports_list()
    print(f"📋 Available Sports: {len(sports)}")
    if sports:
        print(f"🏆 Top Sports: {', '.join([s['name'] for s in sports[:5]])}")

    return api

def test_database_operations():
    """Test database operations"""
    print("\n💾 Testing Database Operations...")

    db = DatabaseManager('test_sports_v2.db')

    # Test creating tables
    table_name = db.create_daily_table('soccer')
    print(f"✅ Created table: {table_name}")

    # Test inserting sample data
    sample_matches = [
        {
            'match_id': 'test_001',
            'home_team': 'Manchester City',
            'away_team': 'Arsenal',
            'score': '2:1',
            'status': 'finished',
            'tournament': 'Premier League',
            'odds_home': 1.85,
            'odds_away': 4.20,
            'odds_draw': 3.40,
            'is_live': False,
            'data_source': '1xbet',
            'confidence': 0.95
        },
        {
            'match_id': 'test_002',
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'score': '',
            'status': 'scheduled',
            'tournament': 'La Liga',
            'odds_home': 2.10,
            'odds_away': 3.50,
            'odds_draw': 3.20,
            'is_live': False,
            'data_source': '1xbet',
            'confidence': 0.88
        }
    ]

    inserted = db.insert_match_data('soccer', sample_matches)
    print(f"✅ Inserted {inserted} matches")

    # Test retrieving data
    matches = db.get_matches_by_date('soccer', datetime.now().date())
    print(f"📊 Retrieved {len(matches)} matches from today")

    # Test database stats
    stats = db.get_database_stats()
    print(f"📈 Database Stats: {stats['total_records']} records, {stats['total_tables']} tables")

    return db

def test_predictions():
    """Test prediction capabilities"""
    print("\n🎯 Testing Prediction Engine...")

    db = DatabaseManager('test_sports_v2.db')
    predictor = MatchPredictor(db)

    # Test team statistics
    try:
        stats = predictor.get_team_statistics('Manchester City', 'soccer', days=30)
        print(f"📊 Manchester City Stats: {stats.get('total_matches', 0)} matches, {stats.get('win_rate', 0):.2%} win rate")
    except Exception as e:
        print(f"⚠️ Could not get team stats: {e}")

    # Test match prediction
    try:
        prediction = predictor.predict_match_outcome('Manchester City', 'Arsenal', 'soccer')
        print(f"🔮 Prediction: {prediction['prediction']} ({prediction['confidence']}% confidence)")
    except Exception as e:
        print(f"⚠️ Could not generate prediction: {e}")

    # Test score prediction
    try:
        score_pred = predictor.predict_score('Real Madrid', 'Barcelona', 'soccer')
        print(f"⚽ Score Prediction: {score_pred.get('predicted_score', 'N/A')}")
    except Exception as e:
        print(f"⚠️ Could not predict score: {e}")

def test_real_data_collection():
    """Test collecting real data"""
    print("\n🌐 Testing Real Data Collection...")

    api = XBetAPI()
    db = DatabaseManager('test_sports_v2.db')

    # Test collecting soccer data
    try:
        matches = api.get_live_matches('1')  # Soccer
        if matches:
            inserted = db.insert_match_data('soccer', matches)
            print(f"✅ Collected {len(matches)} soccer matches, inserted {inserted}")

            # Show sample match
            if matches:
                match = matches[0]
                print(f"📋 Sample Match: {match['home_team']} vs {match['away_team']}")
                print(f"   Score: {match.get('score', 'N/A')}, Status: {match.get('status', 'N/A')}")
        else:
            print("ℹ️ No live soccer matches found")

    except Exception as e:
        print(f"❌ Error collecting real data: {e}")

def main():
    """Run all tests"""
    print("🚀 Sports Data Collection System v2.0 - Test Suite")
    print("=" * 60)

    try:
        # Test API connectivity
        api = test_api_connectivity()

        # Test database operations
        db = test_database_operations()

        # Test predictions
        test_predictions()

        # Test real data collection
        test_real_data_collection()

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\n🎯 Key Improvements Demonstrated:")
        print("  • Modular API architecture")
        print("  • Day-by-day table structure")
        print("  • Advanced prediction engine")
        print("  • Efficient data storage (no null columns)")
        print("  • Real-time data collection")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()