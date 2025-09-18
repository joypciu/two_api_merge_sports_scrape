#!/usr/bin/env python3
"""
Debug script to examine raw API responses from both 1xBet and ISCJXXQGMB
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import asyncio
from app.apis.xbet_api import XBetAPI
# from app.apis.iscjxxqgmb_api import ISCJXXQGMBAPI  # Commented out due to missing dependency
import logging

logging.basicConfig(level=logging.DEBUG)

async def debug_1xbet_response():
    """Debug 1xBet API response"""
    print("=" * 60)
    print("DEBUGGING 1xBET API RESPONSE")
    print("=" * 60)

    try:
        api = XBetAPI()
        matches_data = await api.client.fetch_matches(sports=1, count=2)

        if matches_data and matches_data.get('Success') and matches_data.get('Value'):
            print(f"Got {len(matches_data['Value'])} matches")

            for i, match in enumerate(matches_data['Value'][:2]):
                print(f"\nMATCH {i+1}: {match.get('I', 'unknown')}")
                print(f"   Home: {match.get('O1', {}).get('N', 'unknown') if isinstance(match.get('O1'), dict) else match.get('O1', 'unknown')}")
                print(f"   Away: {match.get('O2', {}).get('N', 'unknown') if isinstance(match.get('O2'), dict) else match.get('O2', 'unknown')}")
                print(f"   Start Time (S): {match.get('S', 'N/A')}")
                print(f"   Is Live (IsLive): {match.get('IsLive', 'N/A')}")
                print(f"   Score (SC): {match.get('SC', 'N/A')}")
                print(f"   Tournament (LE): {match.get('LE', 'N/A')}")

                # Events analysis
                if 'E' in match:
                    print(f"   Events Count: {len(match['E'])}")
                    for j, event in enumerate(match['E'][:5]):  # Show first 5 events
                        print(f"     Event {j}: G={event.get('G')}, T={event.get('T')}, P={event.get('P', 'N/A')}")
                else:
                    print("   Events: None")

                print(f"   Raw keys: {list(match.keys())}")
        else:
            print("No matches data received")

    except Exception as e:
        print(f"1xBet Error: {e}")
        import traceback
        traceback.print_exc()

def debug_iscjxxqgmb_response():
    """Debug ISCJXXQGMB API response"""
    print("\n" + "=" * 60)
    print("DEBUGGING ISCJXXQGMB API RESPONSE")
    print("=" * 60)

    try:
        api = ISCJXXQGMBAPI()
        matches = api.get_live_matches('1')

        if matches:
            print(f"Got {len(matches)} matches")

            for i, match in enumerate(matches[:2]):
                print(f"\nMATCH {i+1}: {match.get('match_id', 'unknown')}")
                print(f"   Home: {match.get('home_team', 'unknown')}")
                print(f"   Away: {match.get('away_team', 'unknown')}")
                print(f"   Start Time: {match.get('start_time', 'N/A')}")
                print(f"   Is Live: {match.get('is_live', 'N/A')}")
                print(f"   Status: {match.get('status', 'N/A')}")
                print(f"   Period: {match.get('period', 'N/A')}")
                print(f"   Score: {match.get('score', 'N/A')}")

                print(f"   Raw keys: {list(match.keys())}")
        else:
            print("No matches received")

    except Exception as e:
        print(f"ISCJXXQGMB Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await debug_1xbet_response()
    # debug_iscjxxqgmb_response()  # Commented out due to missing dependency

if __name__ == "__main__":
    asyncio.run(main())