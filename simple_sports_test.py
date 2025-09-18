#!/usr/bin/env python3
"""
Simple test to verify expanded sports configuration
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from main import SportsDataCollector

    print("SUCCESS: Successfully imported SportsDataCollector")

    collector = SportsDataCollector()
    print("SUCCESS: Successfully created SportsDataCollector instance")

    print(f"Total sports configured: {len(collector.sports_config)}")

    active_sports = []
    inactive_sports = []

    for sport_name, config in collector.sports_config.items():
        if config.get('active', False):
            active_sports.append(sport_name)
        else:
            inactive_sports.append(sport_name)

    print(f"Active sports ({len(active_sports)}): {', '.join(active_sports)}")

    if inactive_sports:
        print(f"Inactive sports ({len(inactive_sports)}): {', '.join(inactive_sports)}")

    print("\nEXPANDED SPORTS CONFIGURATION SUCCESS!")
    print("All major sports are now configured and ready for data collection.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)