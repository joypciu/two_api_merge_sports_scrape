#!/usr/bin/env python3
"""
Analyze ISCJXXQGMB API response to find additional data fields we can collect
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import requests
import json
from datetime import datetime

def analyze_iscjxxqgmb_raw_data():
    """Analyze raw ISCJXXQGMB API response to find additional data fields"""

    print("ANALYZING ISCJXXQGMB API RAW DATA")
    print("=" * 60)

    # Make direct API call to get raw data
    url = "https://iscjxxqgmb.com/api/v3/user/line/list"
    params = {'lc[]': 1, 'ss': 'all', 'l': 3, 'ltr': 0}  # Get 3 soccer matches
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://iscjxxqgmb.com/',
        'Origin': 'https://iscjxxqgmb.com'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        print(f"API Response Status: {response.status_code}")
        print(f"Top Level Keys: {list(data.keys())}")
    
        if 'lines_hierarchy' in data and data['lines_hierarchy']:
            hierarchy = data['lines_hierarchy'][0]
            print(f"\nHierarchy Keys: {list(hierarchy.keys())}")
    
            if 'line_category_dto_collection' in hierarchy:
                categories = hierarchy['line_category_dto_collection']
                print(f"Number of Categories: {len(categories)}")
    
                if categories:
                    category = categories[0]
                    print(f"Category Keys: {list(category.keys())}")
                    print(f"Category Code: {category.get('code')}")
    
                    if 'line_supercategory_dto_collection' in category:
                        supercategories = category['line_supercategory_dto_collection']
                        print(f"Number of Supercategories: {len(supercategories)}")
    
                        if supercategories:
                            supercategory = supercategories[0]
                            print(f"Supercategory Keys: {list(supercategory.keys())}")
    
                            if 'line_subcategory_dto_collection' in supercategory:
                                subcategories = supercategory['line_subcategory_dto_collection']
                                print(f"Number of Subcategories: {len(subcategories)}")
    
                                if subcategories:
                                    subcategory = subcategories[0]
                                    print(f"Subcategory Keys: {list(subcategory.keys())}")
    
                                    if 'line_dto_collection' in subcategory:
                                        lines = subcategory['line_dto_collection']
                                        print(f"Number of Lines: {len(lines)}")
    
                                        # Analyze first match in detail
                                        if lines:
                                            analyze_first_match(lines[0])

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def analyze_first_match(line):
    """Analyze the first match in detail to find all available data fields"""

    print("\n" + "=" * 60)
    print("DETAILED MATCH ANALYSIS")
    print("=" * 60)

    print(f"Line Keys: {list(line.keys())}")

    # Analyze match data
    if 'match' in line:
        match = line['match']
        print(f"\nMATCH DATA KEYS: {list(match.keys())}")

        # Basic match info
        print(f"Match ID: {match.get('id')}")
        print(f"Title: {match.get('title')}")
        print(f"Begin At: {match.get('begin_at')} ({datetime.fromtimestamp(match.get('begin_at', 0)).strftime('%Y-%m-%d %H:%M:%S') if match.get('begin_at') else 'N/A'})")
        print(f"In Top: {match.get('in_top')}")
        print(f"Match Time: {match.get('match_time')}")
        print(f"Score: {match.get('score')}")
        print(f"Match In Campaign: {match.get('match_in_campaign')}")
        print(f"Set Number: {match.get('set_number')}")

        # Analyze statistics
        if 'stat' in match:
            stat = match['stat']
            print(f"\nSTATISTICS KEYS: {list(stat.keys())}")
            print(f"Stat Data: {stat}")

            # Check for sport-specific stats
            sport_specific_keys = ['segment_scores', 'stoppage_time', 'half_time', 'sets_score', 'overtime_score',
                                 'first_half_extra_time_score', 'second_half_extra_time_score', 'sport',
                                 'yellow_cards', 'red_cards', 'corners', 'regular_time_score', 'after_penalties_score']
            found_sport_stats = [key for key in sport_specific_keys if key in stat]
            if found_sport_stats:
                print(f"SPORT-SPECIFIC STATS FOUND: {found_sport_stats}")

        # Analyze team data
        for team_key in ['team1', 'team2']:
            if team_key in match:
                team = match[team_key]
                print(f"\n{team_key.upper()} KEYS: {list(team.keys())}")
                print(f"{team_key.upper()} DATA: {team}")

        # Analyze additional match fields
        additional_fields = ['set_scores', 'widgets']
        for field in additional_fields:
            if field in match:
                print(f"\n{field.upper()} KEYS: {list(match[field].keys()) if isinstance(match[field], dict) else 'Not Dict'}")
                print(f"{field.upper()} DATA: {match[field]}")

    # Analyze outcomes (betting markets)
    if 'outcomes' in line:
        outcomes = line['outcomes']
        print(f"\nOUTCOMES COUNT: {len(outcomes)}")

        if outcomes:
            print(f"FIRST OUTCOME KEYS: {list(outcomes[0].keys())}")
            print(f"FIRST OUTCOME: {outcomes[0]}")

            # Analyze different outcome types
            outcome_types = {}
            for outcome in outcomes:
                alias = outcome.get('alias', 'unknown')
                if alias not in outcome_types:
                    outcome_types[alias] = []
                outcome_types[alias].append(outcome.get('odd'))

            print(f"OUTCOME TYPES FOUND: {list(outcome_types.keys())}")
            print(f"SAMPLE ODDS BY TYPE: { {k: v[:3] for k, v in outcome_types.items()} }")

    # Analyze line metadata
    line_metadata = ['id', 'status', 'top', 'is_outright', 'is_cyber', 'in_favorites']
    print("\nLINE METADATA:")
    for key in line_metadata:
        if key in line:
            print(f"   {key}: {line[key]}")

def analyze_additional_endpoints():
    """Check for additional ISCJXXQGMB endpoints that might provide more data"""

    print("\n" + "=" * 60)
    print("CHECKING ADDITIONAL ISCJXXQGMB ENDPOINTS")
    print("=" * 60)

    endpoints_to_check = [
        'api/v1/allsports/sports',
        'api/v1/leagues',
        'api/v1/teams',
        'api/v1/events',
        'api/v1/statistics'
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://iscjxxqgmb.com/',
        'Origin': 'https://iscjxxqgmb.com'
    }

    for endpoint in endpoints_to_check:
        try:
            url = f"https://iscjxxqgmb.com/{endpoint}"
            response = requests.get(url, headers=headers, timeout=5)

            print(f"\n{endpoint}")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Type: List with {len(data)} items")
                        if data and len(data) > 0:
                            print(f"   Sample Keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not Dict'}")
                    elif isinstance(data, dict):
                        print(f"   Type: Dict with keys: {list(data.keys())}")
                    else:
                        print(f"   Type: {type(data)}")
                except:
                    print(f"   Content: {response.text[:100]}...")
            else:
                print(f"   Error: {response.status_code}")

        except Exception as e:
            print(f"   Exception: {str(e)[:50]}...")

if __name__ == "__main__":
    analyze_iscjxxqgmb_raw_data()
    analyze_additional_endpoints()