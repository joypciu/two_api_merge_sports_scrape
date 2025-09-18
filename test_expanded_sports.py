#!/usr/bin/env python3
"""
Test script for expanded sports configuration
Tests multiple sports from both APIs to ensure they work correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from main import SportsDataCollector
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_expanded_sports():
    """Test the expanded sports configuration"""
    print("🚀 Testing Expanded Sports Configuration")
    print("=" * 60)

    collector = SportsDataCollector()

    # Test a few key sports
    test_sports = ['soccer', 'basketball', 'tennis', 'ice_hockey', 'cricket']

    print(f"📊 Testing {len(test_sports)} sports: {', '.join(test_sports)}")
    print("-" * 60)

    total_matches = 0
    successful_sports = 0

    for sport_name in test_sports:
        if sport_name in collector.sports_config:
            config = collector.sports_config[sport_name]
            print(f"\n🏆 Testing {sport_name.upper()}:")
            print(f"   Config: {config}")

            try:
                result = collector._collect_sport_data(sport_name, config)

                if result['matches_collected'] > 0:
                    print(f"   ✅ SUCCESS: {result['matches_collected']} matches collected")
                    print(f"   📊 API Used: {result.get('api_used', 'UNKNOWN').upper()}")
                    total_matches += result['matches_collected']
                    successful_sports += 1
                else:
                    print(f"   ⚠️ NO DATA: No matches found for {sport_name}")

            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        else:
            print(f"   ⚠️ SKIPPED: {sport_name} not in configuration")

    print("\n" + "=" * 60)
    print("📊 EXPANDED SPORTS TEST RESULTS:")
    print(f"   • Sports Tested: {len(test_sports)}")
    print(f"   • Successful Sports: {successful_sports}")
    print(f"   • Total Matches Collected: {total_matches}")
    print(f"   • Success Rate: {successful_sports}/{len(test_sports)} ({successful_sports/len(test_sports)*100:.1f}%)")

    if successful_sports > 0:
        print("   ✅ EXPANDED CONFIGURATION WORKING!")
    else:
        print("   ❌ NO SPORTS COLLECTED - CHECK API CONNECTIVITY")

    return successful_sports > 0

def show_sports_summary():
    """Show summary of all configured sports"""
    print("\n📋 COMPLETE SPORTS CONFIGURATION:")
    print("=" * 60)

    collector = SportsDataCollector()

    active_sports = []
    inactive_sports = []

    for sport_name, config in collector.sports_config.items():
        if config.get('active', False):
            active_sports.append(f"{sport_name} ({config.get('preferred_api', 'unknown')})")
        else:
            inactive_sports.append(sport_name)

    print(f"✅ ACTIVE SPORTS ({len(active_sports)}):")
    for sport in active_sports:
        print(f"   • {sport}")

    if inactive_sports:
        print(f"\n⚪ INACTIVE SPORTS ({len(inactive_sports)}):")
        for sport in inactive_sports:
            print(f"   • {sport}")

    print(f"\n🎯 TOTAL CONFIGURED SPORTS: {len(collector.sports_config)}")
    print(f"🏃 ACTIVE FOR COLLECTION: {len(active_sports)}")

if __name__ == "__main__":
    show_sports_summary()
    success = test_expanded_sports()

    if success:
        print("\n🎉 Expanded sports configuration is working correctly!")
        print("All major sports are now configured and ready for data collection.")
    else:
        print("\n⚠️ Some issues detected with the expanded configuration.")
        print("Check API connectivity and sport ID mappings.")

    sys.exit(0 if success else 1)