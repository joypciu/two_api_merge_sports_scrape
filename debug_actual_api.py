#!/usr/bin/env python3
"""
Debug script to examine actual API responses from both 1xBet and ISCJXXQGMB
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import requests
from datetime import datetime

def debug_1xbet_raw():
    """Debug raw 1xBet API response"""
    print("=" * 60)
    print("RAW 1xBET API RESPONSE")
    print("=" * 60)

    try:
        url = "https://1xlite-86981.world/service-api/LiveFeed/GetSportsShortZip"
        params = {
            'lng': 'en',
            'gr': 1258,
            'country': 19,
            'virtualSports': 'true',
            'groupChamps': 'true'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://1xlite-86981.world/',
            'Origin': 'https://1xlite-86981.world'
        }

        print(f"URL: {url}")
        print(f"Params: {params}")

        response = requests.get(url, params=params, headers=headers, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")

                if isinstance(data, dict):
                    print(f"Top Level Keys: {list(data.keys())}")

                    if 'Value' in data:
                        value = data['Value']
                        print(f"Value Type: {type(value)}")
                        if isinstance(value, list) and len(value) > 0:
                            print(f"Number of matches: {len(value)}")
                            match = value[0]
                            print(f"First match keys: {list(match.keys())}")
                            print(f"First match ID: {match.get('I')}")
                            print(f"First match start time (S): {match.get('S')}")
                            print(f"First match IsLive: {match.get('IsLive')}")

                            if 'E' in match:
                                events = match['E']
                                print(f"Events count: {len(events)}")
                                if len(events) > 0:
                                    event = events[0]
                                    print(f"First event keys: {list(event.keys())}")
                                    print(f"First event G: {event.get('G')}, T: {event.get('T')}, P: {event.get('P')}")
                            else:
                                print("No 'E' field in match")

                print(f"Raw response (first 500 chars): {str(data)[:500]}")

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw text (first 500 chars): {response.text[:500]}")
        else:
            print(f"Error response: {response.text}")

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

def debug_iscjxxqgmb_raw():
    """Debug raw ISCJXXQGMB API response"""
    print("\n" + "=" * 60)
    print("RAW ISCJXXQGMB API RESPONSE")
    print("=" * 60)

    try:
        url = "https://iscjxxqgmb.com/api/v3/user/line/list"
        params = {
            'lc[]': 1,  # soccer
            'ss': 'all',
            'l': 2,
            'ltr': 0
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://iscjxxqgmb.com/',
            'Origin': 'https://iscjxxqgmb.com'
        }

        print(f"URL: {url}")
        print(f"Params: {params}")

        response = requests.get(url, params=params, headers=headers, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")

                if isinstance(data, dict):
                    print(f"Top Level Keys: {list(data.keys())}")

                    if 'lines_hierarchy' in data:
                        hierarchy = data['lines_hierarchy']
                        print(f"Lines hierarchy count: {len(hierarchy)}")

                        if len(hierarchy) > 0:
                            h = hierarchy[0]
                            print(f"First hierarchy keys: {list(h.keys())}")

                            if 'line_category_dto_collection' in h:
                                categories = h['line_category_dto_collection']
                                print(f"Categories count: {len(categories)}")

                                if len(categories) > 0:
                                    cat = categories[0]
                                    print(f"First category keys: {list(cat.keys())}")

                                    if 'line_supercategory_dto_collection' in cat:
                                        supercats = cat['line_supercategory_dto_collection']
                                        print(f"Supercategories count: {len(supercats)}")

                                        if len(supercats) > 0:
                                            super_cat = supercats[0]
                                            print(f"First supercategory keys: {list(super_cat.keys())}")

                                            if 'line_subcategory_dto_collection' in super_cat:
                                                subcats = super_cat['line_subcategory_dto_collection']
                                                print(f"Subcategories count: {len(subcats)}")

                                                if len(subcats) > 0:
                                                    sub_cat = subcats[0]
                                                    print(f"First subcategory keys: {list(sub_cat.keys())}")

                                                    if 'line_dto_collection' in sub_cat:
                                                        lines = sub_cat['line_dto_collection']
                                                        print(f"Lines count: {len(lines)}")

                                                        if len(lines) > 0:
                                                            line = lines[0]
                                                            print(f"First line keys: {list(line.keys())}")

                                                            if 'match' in line:
                                                                match = line['match']
                                                                print(f"Match keys: {list(match.keys())}")
                                                                print(f"Match ID: {match.get('id')}")
                                                                print(f"Match begin_at: {match.get('begin_at')}")

                                                                if 'stat' in match:
                                                                    stat = match['stat']
                                                                    print(f"Stat keys: {list(stat.keys()) if stat else 'None'}")
                                                                    print(f"Stat status: {stat.get('status') if stat else 'N/A'}")

                print(f"Raw response (first 500 chars): {str(data)[:500]}")

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw text (first 500 chars): {response.text[:500]}")
        else:
            print(f"Error response: {response.text}")

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_1xbet_raw()
    debug_iscjxxqgmb_raw()