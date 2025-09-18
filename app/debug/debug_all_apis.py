#!/usr/bin/env python3
"""
Comprehensive Debug and Testing System for All 3 APIs
Tests 1xBet, TheSportsDB, and iscjxxqgmb with detailed diagnostics
"""
import requests
import time
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_all_apis.log'),
        logging.StreamHandler()
    ]
)

class APIDebugger:
    """Comprehensive API debugging and testing system"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def debug_1xbet_api(self) -> Dict:
        """Debug 1xBet API with comprehensive testing"""
        print("\n" + "="*60)
        print("🔍 DEBUGGING 1xBET API")
        print("="*60)

        base_url = "https://1xlite-86981.world/service-api"
        results = {
            'api_name': '1xBet',
            'base_url': base_url,
            'tests': {},
            'overall_status': 'unknown'
        }

        # Test 1: Get Sports List
        print("\n📊 Test 1: Getting Sports List...")
        try:
            url = f"{base_url}/LiveFeed/GetSportsShortZip"
            params = {'lng': 'en', 'gr': 1258, 'country': 19, 'virtualSports': 'true', 'groupChamps': 'true'}

            start_time = time.time()
            response = self.session.get(url, params=params, timeout=30)
            response_time = time.time() - start_time

            print(f"   URL: {response.url}")
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {response_time:.2f}s")

            if response.status_code == 200:
                data = response.json()
                if 'Value' in data and isinstance(data['Value'], list):
                    sports_count = len(data['Value'])
                    print(f"   ✅ SUCCESS: Found {sports_count} sports")

                    # Show sample sports
                    sample_sports = data['Value'][:5]
                    print("   📋 Sample Sports:")
                    for sport in sample_sports:
                        sport_name = sport.get('C', 'Unknown')
                        sport_id = sport.get('I', 'N/A')
                        print(f"      • {sport_name} (ID: {sport_id})")

                    results['tests']['sports_list'] = {
                        'status': 'success',
                        'sports_count': sports_count,
                        'response_time': response_time,
                        'sample_data': sample_sports
                    }
                else:
                    print("   ❌ ERROR: Unexpected response format")
                    results['tests']['sports_list'] = {
                        'status': 'error',
                        'error': 'Unexpected response format',
                        'response_time': response_time
                    }
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                results['tests']['sports_list'] = {
                    'status': 'error',
                    'http_code': response.status_code,
                    'response_time': response_time
                }

        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results['tests']['sports_list'] = {
                'status': 'error',
                'exception': str(e)
            }

        # Test 2: Get Soccer Matches
        print("\n⚽ Test 2: Getting Soccer Matches...")
        try:
            url = f"{base_url}/LiveFeed/Get1x2_VZip"
            params = {'count': 20, 'lng': 'en', 'gr': 1258, 'mode': 4, 'country': 19, 'virtualSports': 'true', 'noFilterBlockEvent': 'true'}

            start_time = time.time()
            response = self.session.get(url, params=params, timeout=30)
            response_time = time.time() - start_time

            print(f"   URL: {response.url}")
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {response_time:.2f}s")

            if response.status_code == 200:
                data = response.json()
                if 'Value' in data and isinstance(data['Value'], list):
                    matches_count = len(data['Value'])
                    print(f"   ✅ SUCCESS: Found {matches_count} matches")

                    # Show sample matches
                    sample_matches = data['Value'][:3]
                    print("   📋 Sample Matches:")
                    for match in sample_matches:
                        home_team = match.get('O1', {}).get('N', 'Unknown') if isinstance(match.get('O1'), dict) else str(match.get('O1', 'Unknown'))
                        away_team = match.get('O2', {}).get('N', 'Unknown') if isinstance(match.get('O2'), dict) else str(match.get('O2', 'Unknown'))
                        print(f"      • {home_team} vs {away_team}")

                    results['tests']['soccer_matches'] = {
                        'status': 'success',
                        'matches_count': matches_count,
                        'response_time': response_time,
                        'sample_data': sample_matches
                    }
                else:
                    print("   ❌ ERROR: Unexpected response format")
                    results['tests']['soccer_matches'] = {
                        'status': 'error',
                        'error': 'Unexpected response format',
                        'response_time': response_time
                    }
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                results['tests']['soccer_matches'] = {
                    'status': 'error',
                    'http_code': response.status_code,
                    'response_time': response_time
                }

        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results['tests']['soccer_matches'] = {
                'status': 'error',
                'exception': str(e)
            }

        # Calculate overall status
        successful_tests = sum(1 for test in results['tests'].values() if test['status'] == 'success')
        total_tests = len(results['tests'])

        if successful_tests == total_tests:
            results['overall_status'] = 'healthy'
        elif successful_tests > 0:
            results['overall_status'] = 'partial'
        else:
            results['overall_status'] = 'unhealthy'

        print(f"\n🎯 1xBet API Status: {results['overall_status'].upper()}")
        print(f"   Tests Passed: {successful_tests}/{total_tests}")

        return results

    def debug_thesportsdb_api(self) -> Dict:
        """Debug TheSportsDB API"""
        print("\n" + "="*60)
        print("🔍 DEBUGGING THESPORTSDB API")
        print("="*60)

        base_url = "https://www.thesportsdb.com/api/v1/json"
        results = {
            'api_name': 'TheSportsDB',
            'base_url': base_url,
            'tests': {},
            'overall_status': 'unknown'
        }

        # Test 1: Get Daily Events
        print("\n📅 Test 1: Getting Daily Soccer Events...")
        try:
            today = date.today().strftime('%Y-%m-%d')
            url = f"{base_url}/eventsday.php?d={today}&s=Soccer"

            start_time = time.time()
            response = self.session.get(url, timeout=10)
            response_time = time.time() - start_time

            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {response_time:.2f}s")

            if response.status_code == 200:
                data = response.json()
                if 'events' in data and isinstance(data['events'], list):
                    events_count = len(data['events'])
                    print(f"   ✅ SUCCESS: Found {events_count} events")

                    # Show sample events
                    sample_events = data['events'][:2]
                    print("   📋 Sample Events:")
                    for event in sample_events:
                        home_team = event.get('strHomeTeam', 'Unknown')
                        away_team = event.get('strAwayTeam', 'Unknown')
                        league = event.get('strLeague', 'Unknown')
                        print(f"      • {home_team} vs {away_team} ({league})")

                    results['tests']['daily_events'] = {
                        'status': 'success',
                        'events_count': events_count,
                        'response_time': response_time,
                        'sample_data': sample_events
                    }
                else:
                    print("   ❌ ERROR: Unexpected response format")
                    results['tests']['daily_events'] = {
                        'status': 'error',
                        'error': 'Unexpected response format',
                        'response_time': response_time
                    }
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                results['tests']['daily_events'] = {
                    'status': 'error',
                    'http_code': response.status_code,
                    'response_time': response_time
                }

        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results['tests']['daily_events'] = {
                'status': 'error',
                'exception': str(e)
            }

        # Test 2: Get Team Lookup
        print("\n👥 Test 2: Getting Team Information...")
        try:
            url = f"{base_url}/lookupteam.php?id=133604"  # Manchester City

            start_time = time.time()
            response = self.session.get(url, timeout=10)
            response_time = time.time() - start_time

            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {response_time:.2f}s")

            if response.status_code == 200:
                data = response.json()
                if 'teams' in data and isinstance(data['teams'], list) and len(data['teams']) > 0:
                    team = data['teams'][0]
                    team_name = team.get('strTeam', 'Unknown')
                    league = team.get('strLeague', 'Unknown')
                    print(f"   ✅ SUCCESS: Found team '{team_name}' in {league}")

                    results['tests']['team_lookup'] = {
                        'status': 'success',
                        'team_name': team_name,
                        'league': league,
                        'response_time': response_time
                    }
                else:
                    print("   ❌ ERROR: Team not found or unexpected format")
                    results['tests']['team_lookup'] = {
                        'status': 'error',
                        'error': 'Team not found',
                        'response_time': response_time
                    }
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                results['tests']['team_lookup'] = {
                    'status': 'error',
                    'http_code': response.status_code,
                    'response_time': response_time
                }

        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results['tests']['team_lookup'] = {
                'status': 'error',
                'exception': str(e)
            }

        # Calculate overall status
        successful_tests = sum(1 for test in results['tests'].values() if test['status'] == 'success')
        total_tests = len(results['tests'])

        if successful_tests == total_tests:
            results['overall_status'] = 'healthy'
        elif successful_tests > 0:
            results['overall_status'] = 'partial'
        else:
            results['overall_status'] = 'unhealthy'

        print(f"\n🎯 TheSportsDB API Status: {results['overall_status'].upper()}")
        print(f"   Tests Passed: {successful_tests}/{total_tests}")

        return results

    def debug_iscj_api(self) -> Dict:
        """Debug iscjxxqgmb API"""
        print("\n" + "="*60)
        print("🔍 DEBUGGING ISCJXXQGMB API")
        print("="*60)

        base_url = "https://iscjxxqgmb.com/api"
        results = {
            'api_name': 'iscjxxqgmb',
            'base_url': base_url,
            'tests': {},
            'overall_status': 'unknown'
        }

        # Test 1: Get Match List
        print("\n📋 Test 1: Getting Match List...")
        try:
            url = f"{base_url}/v3/user/line/list"
            params = {'lc[]': '1', 'ss': 'all', 'l': '10', 'ltr': '0'}

            start_time = time.time()
            response = self.session.get(url, params=params, timeout=30)
            response_time = time.time() - start_time

            print(f"   URL: {response.url}")
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {response_time:.2f}s")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print("   ✅ SUCCESS: API responded with JSON")

                    # Check if we have expected structure
                    if 'lines_hierarchy' in data:
                        print("   📊 Found lines_hierarchy structure")
                        hierarchy_count = len(data['lines_hierarchy'])
                        print(f"   📋 Found {hierarchy_count} hierarchy items")

                        results['tests']['match_list'] = {
                            'status': 'success',
                            'hierarchy_count': hierarchy_count,
                            'response_time': response_time,
                            'has_lines_hierarchy': True
                        }
                    else:
                        print("   ⚠️ WARNING: No lines_hierarchy found")
                        results['tests']['match_list'] = {
                            'status': 'partial',
                            'response_time': response_time,
                            'has_lines_hierarchy': False,
                            'available_keys': list(data.keys()) if isinstance(data, dict) else 'not_dict'
                        }

                except json.JSONDecodeError:
                    print("   ❌ ERROR: Response is not valid JSON")
                    print(f"   📄 Content preview: {response.text[:200]}...")
                    results['tests']['match_list'] = {
                        'status': 'error',
                        'error': 'Invalid JSON response',
                        'response_time': response_time,
                        'content_preview': response.text[:200]
                    }
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                if response.status_code == 404:
                    print("   🚫 API endpoint not found (404)")
                elif response.status_code == 403:
                    print("   🚫 Access forbidden (403)")
                elif response.status_code >= 500:
                    print("   🚫 Server error (5xx)")

                results['tests']['match_list'] = {
                    'status': 'error',
                    'http_code': response.status_code,
                    'response_time': response_time
                }

        except requests.exceptions.Timeout:
            print("   ⏰ TIMEOUT: Request timed out")
            results['tests']['match_list'] = {
                'status': 'error',
                'error': 'Request timeout',
                'timeout_seconds': 30
            }
        except requests.exceptions.ConnectionError:
            print("   🌐 CONNECTION ERROR: Cannot connect to server")
            results['tests']['match_list'] = {
                'status': 'error',
                'error': 'Connection failed'
            }
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results['tests']['match_list'] = {
                'status': 'error',
                'exception': str(e)
            }

        # Test 2: Get Match Details (if first test succeeded)
        if results['tests'].get('match_list', {}).get('status') == 'success':
            print("\n📄 Test 2: Getting Match Details...")
            try:
                # Try to get a match ID from the previous response
                match_data = results['tests']['match_list'].get('sample_data', {})
                if match_data and 'id' in match_data:
                    match_id = match_data['id']
                    url = f"{base_url}/v1/lines/{match_id}.json"

                    start_time = time.time()
                    response = self.session.get(url, timeout=15)
                    response_time = time.time() - start_time

                    print(f"   URL: {url}")
                    print(f"   Status: {response.status_code}")
                    print(f"   Response Time: {response_time:.2f}s")

                    if response.status_code == 200:
                        print("   ✅ SUCCESS: Match details retrieved")
                        results['tests']['match_details'] = {
                            'status': 'success',
                            'response_time': response_time
                        }
                    else:
                        print(f"   ❌ HTTP ERROR: {response.status_code}")
                        results['tests']['match_details'] = {
                            'status': 'error',
                            'http_code': response.status_code,
                            'response_time': response_time
                        }
                else:
                    print("   ⏭️ SKIPPED: No match ID available for details test")
                    results['tests']['match_details'] = {
                        'status': 'skipped',
                        'reason': 'No match ID available'
                    }

            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
                results['tests']['match_details'] = {
                    'status': 'error',
                    'exception': str(e)
                }
        else:
            print("\n📄 Test 2: Getting Match Details... SKIPPED (previous test failed)")
            results['tests']['match_details'] = {
                'status': 'skipped',
                'reason': 'Previous test failed'
            }

        # Calculate overall status
        successful_tests = sum(1 for test in results['tests'].values()
                              if test['status'] in ['success', 'partial'])
        total_tests = len(results['tests'])

        if successful_tests == total_tests:
            results['overall_status'] = 'healthy'
        elif successful_tests > 0:
            results['overall_status'] = 'partial'
        else:
            results['overall_status'] = 'unhealthy'

        print(f"\n🎯 iscjxxqgmb API Status: {results['overall_status'].upper()}")
        print(f"   Tests Passed: {successful_tests}/{total_tests}")

        return results

    def run_all_debugs(self) -> Dict:
        """Run debugging for all 3 APIs"""
        print("🚀 STARTING COMPREHENSIVE API DEBUG SESSION")
        print("="*80)

        all_results = {
            'timestamp': datetime.now().isoformat(),
            'session_id': f"debug_{int(time.time())}",
            'apis': {}
        }

        # Debug each API
        all_results['apis']['1xbet'] = self.debug_1xbet_api()
        time.sleep(2)  # Rate limiting between APIs

        all_results['apis']['thesportsdb'] = self.debug_thesportsdb_api()
        time.sleep(1)  # Rate limiting

        all_results['apis']['iscj'] = self.debug_iscj_api()

        # Summary
        print("\n" + "="*80)
        print("📊 DEBUG SESSION SUMMARY")
        print("="*80)

        healthy_count = 0
        partial_count = 0
        unhealthy_count = 0

        for api_name, results in all_results['apis'].items():
            status = results['overall_status']
            if status == 'healthy':
                healthy_count += 1
                icon = '✅'
            elif status == 'partial':
                partial_count += 1
                icon = '⚠️'
            else:
                unhealthy_count += 1
                icon = '❌'

            print(f"{icon} {api_name.upper()}: {status.upper()}")

        print(f"\n🎯 Overall Status:")
        print(f"   ✅ Healthy APIs: {healthy_count}")
        print(f"   ⚠️ Partial APIs: {partial_count}")
        print(f"   ❌ Unhealthy APIs: {unhealthy_count}")
        print(f"   📅 Session Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Save results
        filename = f"api_debug_results_{all_results['session_id']}.json"
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)

        print(f"💾 Detailed results saved to: {filename}")

        return all_results

def main():
    """Main function"""
    debugger = APIDebugger()
    results = debugger.run_all_debugs()

    # Print key findings
    print("\n🔍 KEY FINDINGS:")
    for api_name, api_results in results['apis'].items():
        print(f"\n{api_name.upper()}:")
        for test_name, test_results in api_results['tests'].items():
            status = test_results['status']
            if status == 'success':
                print(f"   ✅ {test_name}: Working")
            elif status == 'partial':
                print(f"   ⚠️ {test_name}: Partial success")
            else:
                print(f"   ❌ {test_name}: Failed")

if __name__ == "__main__":
    main()