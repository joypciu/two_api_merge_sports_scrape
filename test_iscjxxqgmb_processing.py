#!/usr/bin/env python3
"""
Test ISCJXXQGMB API processing with actual data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from datetime import datetime
from app.apis.iscjxxqgmb_api import ISCJXXQGMBAPI

def test_iscjxxqgmb_processing():
    """Test ISCJXXQGMB data processing"""
    print("Testing ISCJXXQGMB Data Processing")
    print("=" * 50)

    # Make direct API call to get raw data
    url = "https://iscjxxqgmb.com/api/v3/user/line/list"
    params = {'lc[]': 1, 'ss': 'all', 'l': 2, 'ltr': 0}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://iscjxxqgmb.com/',
        'Origin': 'https://iscjxxqgmb.com'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        # Extract first match data
        hierarchy = data['lines_hierarchy'][0]
        category = hierarchy['line_category_dto_collection'][0]
        supercategory = category['line_supercategory_dto_collection'][0]
        subcategory = supercategory['line_subcategory_dto_collection'][0]
        line = subcategory['line_dto_collection'][0]
        match = line['match']

        print("Raw match data:")
        print(f"  ID: {match.get('id')}")
        print(f"  begin_at: {match.get('begin_at')} (type: {type(match.get('begin_at'))})")
        print(f"  stat.status: {match.get('stat', {}).get('status')}")

        # Test processing
        api = ISCJXXQGMBAPI()

        # Create mock match data as _parse_matches would create
        mock_match_data = {
            "line_id": line.get("id"),
            "match_id": match.get("id"),
            "title": match.get("title"),
            "begin_at": match.get("begin_at"),  # Keep as Unix timestamp
            "home_team": match.get("team1", {}).get("title"),
            "away_team": match.get("team2", {}).get("title"),
            "type": "live",  # Since stat.status is "2nd_half"
            "match_time": match.get("stat", {}).get("time"),
            "score": match.get("stat", {}).get("score"),
            "sport": "soccer",
            "outcomes": line.get("outcomes", []),
            "odds_home": None,  # Will be extracted
            "odds_away": None,
            "odds_draw": None,
            "raw_data": match  # Include raw match data for stat.status access
        }

        # Extract odds
        basic_outcomes = api._extract_basic_outcomes(line, "soccer")
        mock_match_data.update(basic_outcomes)

        print("\nMock match data for processing:")
        print(f"  line_id: {mock_match_data['line_id']}")
        print(f"  begin_at: {mock_match_data['begin_at']}")
        print(f"  type: {mock_match_data['type']}")
        print(f"  match_time: {mock_match_data['match_time']}")
        print(f"  outcomes count: {len(mock_match_data['outcomes'])}")
        print(f"  odds_home: {mock_match_data['odds_home']}")
        print(f"  odds_away: {mock_match_data['odds_away']}")
        print(f"  odds_draw: {mock_match_data['odds_draw']}")

        # Test _process_match_data
        processed = api._process_match_data(mock_match_data)

        if processed:
            print("\nProcessed match data:")
            print(f"  match_id: {processed['match_id']}")
            print(f"  status: {processed['status']}")
            print(f"  event_count: {processed['event_count']}")
            print(f"  start_time: {processed['start_time']} (human: {datetime.fromtimestamp(processed['start_time']).strftime('%Y-%m-%d %H:%M:%S') if processed['start_time'] else 'N/A'})")
            print(f"  period: {processed['period']}")
            print(f"  odds_home: {processed['odds_home']}")
            print(f"  odds_away: {processed['odds_away']}")
            print(f"  odds_draw: {processed['odds_draw']}")

            return True
        else:
            print("Processing returned None")
            return False

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_iscjxxqgmb_processing()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")