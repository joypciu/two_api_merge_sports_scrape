#!/usr/bin/env python3
"""
Dynamic API Discovery & Health Check System
Comprehensive analysis of 1xBet, TheSportsDB, and iscjxxqgmb APIs
Discovers endpoints, analyzes data structures, and provides detailed insights
"""
import requests
import time
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_discovery.log'),
        logging.StreamHandler()
    ]
)

class DynamicAPIDiscovery:
    """Dynamic API discovery and comprehensive analysis system"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        # Known API configurations with potential endpoints
        self.api_configs = {
            '1xbet': {
                'name': '1xBet',
                'base_url': 'https://1xlite-86981.world/service-api',
                'known_endpoints': {
                    'sports_list': {
                        'path': '/LiveFeed/GetSportsShortZip',
                        'params': {'lng': 'en', 'gr': 1258, 'country': 19, 'virtualSports': 'true', 'groupChamps': 'true'},
                        'description': 'Complete sports catalog with IDs'
                    },
                    'live_matches': {
                        'path': '/LiveFeed/Get1x2_VZip',
                        'params': {'count': 100, 'lng': 'en', 'gr': 1258, 'mode': 4, 'country': 19, 'virtualSports': 'true', 'noFilterBlockEvent': 'true'},
                        'description': 'Live match data across all sports'
                    },
                    'top_games': {
                        'path': '/LiveFeed/GetTopGamesStatZip',
                        'params': {'lng': 'en'},
                        'description': 'Popular games and statistics'
                    },
                    'express_games': {
                        'path': '/main-line-feed/v1/expressDay',
                        'params': {'cfView': 3, 'country': 19, 'gr': 1258, 'lng': 'en', 'ref': 1},
                        'description': 'Express betting options'
                    }
                },
                'rate_limit': 45,
                'timeout': 30
            },
            'thesportsdb': {
                'name': 'TheSportsDB',
                'base_url': 'https://www.thesportsdb.com/api/v1/json',
                'known_endpoints': {
                    'daily_events': {
                        'path': '/eventsday.php',
                        'params': {'d': date.today().strftime('%Y-%m-%d'), 's': 'Soccer'},
                        'description': 'Daily events by sport and date'
                    },
                    'team_lookup': {
                        'path': '/lookupteam.php',
                        'params': {'id': '133604'},  # Manchester City
                        'description': 'Team information lookup'
                    },
                    'league_lookup': {
                        'path': '/lookupleague.php',
                        'params': {'id': '4328'},  # Premier League
                        'description': 'League information lookup'
                    },
                    'player_lookup': {
                        'path': '/lookupplayer.php',
                        'params': {'id': '34145937'},  # Sample player
                        'description': 'Player information lookup'
                    }
                },
                'rate_limit': 1,
                'timeout': 15
            },
            'iscj': {
                'name': 'iscjxxqgmb',
                'base_url': 'https://iscjxxqgmb.com/api',
                'known_endpoints': {
                    'match_list': {
                        'path': '/v3/user/line/list',
                        'params': {'lc[]': '1', 'ss': 'all', 'l': '50', 'ltr': '0'},
                        'description': 'Match listings with betting lines'
                    },
                    'match_details': {
                        'path': '/v1/lines/',
                        'params': {},  # Dynamic - needs match ID
                        'description': 'Detailed match information',
                        'requires_id': True
                    },
                    'sports_list': {
                        'path': '/v1/sports',
                        'params': {},
                        'description': 'Available sports catalog'
                    },
                    'live_matches': {
                        'path': '/v1/live',
                        'params': {},
                        'description': 'Currently live matches'
                    }
                },
                'rate_limit': 30,
                'timeout': 20
            }
        }

        self.discovery_results = {}

    def discover_all_apis(self) -> Dict:
        """Discover and analyze all configured APIs"""
        print("🚀 STARTING DYNAMIC API DISCOVERY")
        print("="*100)

        self.discovery_results = {
            'timestamp': datetime.now().isoformat(),
            'session_id': f"discovery_{int(time.time())}",
            'apis': {},
            'overall_summary': {}
        }

        for api_key, config in self.api_configs.items():
            print(f"\n🔍 DISCOVERING: {config['name']} API")
            print("-" * 80)

            api_result = self.discover_api(api_key, config)
            self.discovery_results['apis'][api_key] = api_result

            # Rate limiting between APIs
            if api_key != list(self.api_configs.keys())[-1]:
                time.sleep(2)

        # Generate overall summary
        self.discovery_results['overall_summary'] = self.generate_overall_summary()

        self.print_comprehensive_summary()
        return self.discovery_results

    def discover_api(self, api_key: str, config: Dict) -> Dict:
        """Discover and analyze a specific API"""
        result = {
            'name': config['name'],
            'base_url': config['base_url'],
            'endpoints_discovered': {},
            'working_endpoints': 0,
            'total_endpoints_tested': 0,
            'sports_coverage': {},
            'data_types_available': set(),
            'performance_metrics': {},
            'status': 'unknown',
            'error_summary': []
        }

        print(f"📊 Testing {len(config['known_endpoints'])} known endpoints...")

        for endpoint_name, endpoint_config in config['known_endpoints'].items():
            result['total_endpoints_tested'] += 1

            print(f"\n🔗 Testing: {endpoint_name}")
            print(f"   Description: {endpoint_config['description']}")

            endpoint_result = self.test_endpoint(api_key, config, endpoint_name, endpoint_config)

            result['endpoints_discovered'][endpoint_name] = endpoint_result

            if endpoint_result['status'] == 'success':
                result['working_endpoints'] += 1

                # Analyze data if successful
                if 'data_analysis' in endpoint_result:
                    analysis = endpoint_result['data_analysis']

                    # Collect sports coverage
                    if 'sports_count' in analysis:
                        result['sports_coverage'][endpoint_name] = analysis['sports_count']

                    # Collect data types
                    if 'data_types' in analysis:
                        result['data_types_available'].update(analysis['data_types'])

            # Rate limiting
            if config['rate_limit'] < 10:  # Slow APIs
                time.sleep(1)

        # Calculate performance metrics
        result['performance_metrics'] = {
            'success_rate': result['working_endpoints'] / result['total_endpoints_tested'] if result['total_endpoints_tested'] > 0 else 0,
            'total_sports_discovered': sum(result['sports_coverage'].values()),
            'data_types_count': len(result['data_types_available']),
            'average_response_time': sum(
                endpoint.get('response_time', 0)
                for endpoint in result['endpoints_discovered'].values()
                if endpoint.get('status') == 'success'
            ) / max(result['working_endpoints'], 1)
        }

        # Determine overall status
        success_rate = result['performance_metrics']['success_rate']
        if success_rate == 1.0:
            result['status'] = 'excellent'
        elif success_rate >= 0.75:
            result['status'] = 'good'
        elif success_rate >= 0.5:
            result['status'] = 'fair'
        elif success_rate > 0:
            result['status'] = 'poor'
        else:
            result['status'] = 'critical'

        print(f"\n🎯 {config['name']} Discovery Complete:")
        print(f"   Status: {result['status'].upper()}")
        print(f"   Working Endpoints: {result['working_endpoints']}/{result['total_endpoints_tested']}")
        print(f"   Sports Discovered: {result['performance_metrics']['total_sports_discovered']}")
        print(f"   Data Types: {result['performance_metrics']['data_types_count']}")

        return result

    def test_endpoint(self, api_key: str, config: Dict, endpoint_name: str, endpoint_config: Dict) -> Dict:
        """Test a specific endpoint"""
        result = {
            'name': endpoint_name,
            'description': endpoint_config['description'],
            'status': 'unknown',
            'response_time': 0,
            'http_status': None,
            'data_size': 0,
            'error_message': None,
            'data_analysis': {}
        }

        try:
            # Build URL
            url = f"{config['base_url']}{endpoint_config['path']}"

            # Add query parameters if any
            if endpoint_config.get('params'):
                if api_key == 'iscj' and endpoint_name == 'match_details' and endpoint_config.get('requires_id'):
                    # Skip match details without ID
                    result['status'] = 'skipped'
                    result['error_message'] = 'Requires dynamic match ID'
                    print("   ⏭️ SKIPPED: Requires match ID from previous endpoint")
                    return result

                url += '?' + urlencode(endpoint_config['params'], doseq=True)

            print(f"   URL: {url[:80]}{'...' if len(url) > 80 else ''}")

            start_time = time.time()

            # Make request
            response = self.session.get(
                url,
                timeout=config['timeout']
            )

            result['response_time'] = time.time() - start_time
            result['http_status'] = response.status_code
            result['data_size'] = len(response.text)

            print(f"   Status: {response.status_code} | Time: {result['response_time']:.2f}s | Size: {result['data_size']} bytes")

            if response.status_code == 200:
                try:
                    # Try to parse as JSON
                    data = response.json()
                    result['status'] = 'success'
                    result['content_type'] = 'json'

                    # Analyze the data structure
                    result['data_analysis'] = self.analyze_response_data(api_key, endpoint_name, data)

                    print("   ✅ SUCCESS: Valid JSON response")
                    if result['data_analysis']:
                        key_info = list(result['data_analysis'].keys())[:3]
                        print(f"   📊 Analysis: {', '.join(key_info)}")

                except json.JSONDecodeError:
                    result['status'] = 'partial'
                    result['content_type'] = 'text'
                    result['error_message'] = 'Non-JSON response'
                    print("   ⚠️ PARTIAL: Non-JSON response")
            else:
                result['status'] = 'error'
                result['error_message'] = f'HTTP {response.status_code}: {response.reason}'
                print(f"   ❌ ERROR: HTTP {response.status_code}")

        except requests.exceptions.Timeout:
            result['status'] = 'error'
            result['error_message'] = f'Timeout after {config["timeout"]}s'
            print(f"   ⏰ TIMEOUT: {config['timeout']}s")

        except requests.exceptions.ConnectionError as e:
            result['status'] = 'error'
            result['error_message'] = f'Connection error: {str(e)}'
            print(f"   🌐 CONNECTION ERROR: {str(e)}")

        except Exception as e:
            result['status'] = 'error'
            result['error_message'] = str(e)
            print(f"   💥 EXCEPTION: {str(e)}")

        return result

    def analyze_response_data(self, api_key: str, endpoint_name: str, data: Any) -> Dict:
        """Analyze the structure and content of API response data"""
        analysis = {}

        if not isinstance(data, dict):
            return analysis

        # Generic analysis for all APIs
        analysis.update(self.generic_data_analysis(data))

        return analysis

    def analyze_1xbet_data(self, endpoint_name: str, data: Dict) -> Dict:
        """Analyze the structure and content of API response data"""
        analysis = {}

        if not isinstance(data, dict):
            return analysis

        # 1xBet specific analysis
        if api_key == '1xbet':
            analysis.update(self.analyze_1xbet_data(endpoint_name, data))

        # TheSportsDB specific analysis
        elif api_key == 'thesportsdb':
            analysis.update(self.analyze_thesportsdb_data(endpoint_name, data))

        # iscjxxqgmb specific analysis
        elif api_key == 'iscj':
            analysis.update(self.analyze_iscj_data(endpoint_name, data))

        # Generic analysis for all APIs
        analysis.update(self.generic_data_analysis(data))

        return analysis


    def analyze_thesportsdb_data(self, endpoint_name: str, data: Dict) -> Dict:
        """Analyze TheSportsDB specific data structures"""
        analysis = {}

        if endpoint_name == 'daily_events':
            if 'events' in data and isinstance(data['events'], list):
                events = data['events']
                analysis['events_count'] = len(events)

                if events:
                    # Analyze event structure
                    sample_event = events[0]
                    analysis['event_fields'] = list(sample_event.keys())

                    # Count events by league
                    leagues_count = {}
                    for event in events:
                        league = event.get('strLeague', 'Unknown')
                        leagues_count[league] = leagues_count.get(league, 0) + 1

                    analysis['leagues_count'] = len(leagues_count)
                    analysis['top_leagues'] = dict(
                        sorted(leagues_count.items(), key=lambda x: x[1], reverse=True)[:5]
                    )

        elif endpoint_name == 'team_lookup':
            if 'teams' in data and isinstance(data['teams'], list) and data['teams']:
                team = data['teams'][0]
                analysis['team_fields'] = list(team.keys())
                analysis['team_name'] = team.get('strTeam', 'Unknown')
                analysis['league'] = team.get('strLeague', 'Unknown')
                analysis['country'] = team.get('strCountry', 'Unknown')

        return analysis

    def analyze_iscj_data(self, endpoint_name: str, data: Dict) -> Dict:
        """Analyze iscjxxqgmb specific data structures"""
        analysis = {}

        if endpoint_name == 'match_list':
            if 'lines_hierarchy' in data and isinstance(data['lines_hierarchy'], list):
                hierarchy = data['lines_hierarchy']
                analysis['hierarchy_items_count'] = len(hierarchy)

                if hierarchy:
                    # Analyze hierarchy structure
                    sample_item = hierarchy[0]
                    analysis['hierarchy_fields'] = list(sample_item.keys())

                    # Look for sports/categories
                    if 'line_category_dto_collection' in sample_item:
                        categories = sample_item['line_category_dto_collection']
                        analysis['categories_count'] = len(categories) if isinstance(categories, list) else 0

                        if isinstance(categories, list) and categories:
                            sample_category = categories[0]
                            analysis['category_fields'] = list(sample_category.keys())

        return analysis

    def generic_data_analysis(self, data: Dict) -> Dict:
        """Generic analysis applicable to all APIs"""
        analysis = {}

        # Count top-level keys
        analysis['top_level_keys'] = list(data.keys())
        analysis['top_level_count'] = len(data)

        # Analyze data types in the response
        data_types = set()
        for key, value in data.items():
            if isinstance(value, list):
                data_types.add('array')
                if value and isinstance(value[0], dict):
                    data_types.add('array_of_objects')
            elif isinstance(value, dict):
                data_types.add('object')
            elif isinstance(value, str):
                data_types.add('string')
            elif isinstance(value, (int, float)):
                data_types.add('number')
            elif isinstance(value, bool):
                data_types.add('boolean')
            else:
                data_types.add('other')

        analysis['data_types'] = list(data_types)

        # Estimate data complexity
        total_items = 0
        max_depth = 0

        def count_items(obj, depth=0):
            nonlocal total_items, max_depth
            max_depth = max(max_depth, depth)

            if isinstance(obj, dict):
                total_items += len(obj)
                for value in obj.values():
                    count_items(value, depth + 1)
            elif isinstance(obj, list):
                total_items += len(obj)
                for item in obj:
                    count_items(item, depth + 1)

        count_items(data)
        analysis['total_data_items'] = total_items
        analysis['max_nesting_depth'] = max_depth

        return analysis

    def generate_overall_summary(self) -> Dict:
        """Generate overall summary across all APIs"""
        summary = {
            'total_apis': len(self.discovery_results['apis']),
            'working_apis': 0,
            'total_endpoints_tested': 0,
            'working_endpoints': 0,
            'total_sports_discovered': 0,
            'api_status_breakdown': {},
            'best_performing_api': None,
            'sports_coverage_comparison': {}
        }

        best_performance = 0

        for api_key, api_result in self.discovery_results['apis'].items():
            summary['total_endpoints_tested'] += api_result['total_endpoints_tested']
            summary['working_endpoints'] += api_result['working_endpoints']
            summary['total_sports_discovered'] += api_result['performance_metrics'].get('total_sports_discovered', 0)

            if api_result['status'] not in ['critical', 'poor']:
                summary['working_apis'] += 1

            # Track status breakdown
            status = api_result['status']
            summary['api_status_breakdown'][status] = summary['api_status_breakdown'].get(status, 0) + 1

            # Find best performing API
            success_rate = api_result['performance_metrics']['success_rate']
            if success_rate > best_performance:
                best_performance = success_rate
                summary['best_performing_api'] = api_key

            # Collect sports coverage
            if api_result['sports_coverage']:
                summary['sports_coverage_comparison'][api_result['name']] = api_result['sports_coverage']

        # Calculate overall success rate
        summary['overall_success_rate'] = summary['working_endpoints'] / summary['total_endpoints_tested'] if summary['total_endpoints_tested'] > 0 else 0

        return summary

    def print_comprehensive_summary(self):
        """Print comprehensive discovery summary"""
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE API DISCOVERY SUMMARY")
        print("="*100)

        summary = self.discovery_results['overall_summary']

        # Overall status
        status_emoji = {
            'excellent': '🟢', 'good': '🟡', 'fair': '🟠',
            'poor': '🔴', 'critical': '💀'
        }

        success_rate = summary['overall_success_rate']
        if success_rate == 1.0:
            overall_status = 'excellent'
        elif success_rate >= 0.75:
            overall_status = 'good'
        elif success_rate >= 0.5:
            overall_status = 'fair'
        elif success_rate > 0:
            overall_status = 'poor'
        else:
            overall_status = 'critical'

        print(f"🎯 Overall Status: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        print(f"   Success Rate: {success_rate:.1%}")
        print(f"   Working APIs: {summary['working_apis']}/{summary['total_apis']}")
        print(f"   Working Endpoints: {summary['working_endpoints']}/{summary['total_endpoints_tested']}")
        print(f"   Total Sports Discovered: {summary['total_sports_discovered']}")

        # API breakdown
        print(f"\n🔍 API BREAKDOWN:")
        for api_key, api_result in self.discovery_results['apis'].items():
            status_icon = '✅' if api_result['status'] in ['excellent', 'good'] else '⚠️' if api_result['status'] == 'fair' else '❌'
            print(f"   {status_icon} {api_result['name']}: {api_result['status'].upper()}")
            print(f"      Endpoints: {api_result['working_endpoints']}/{api_result['total_endpoints_tested']}")
            print(f"      Sports: {api_result['performance_metrics']['total_sports_discovered']}")
            print(f"      Data Types: {api_result['performance_metrics']['data_types_count']}")

        # Sports coverage comparison
        if summary['sports_coverage_comparison']:
            print(f"\n🏆 SPORTS COVERAGE COMPARISON:")
            for api_name, coverage in summary['sports_coverage_comparison'].items():
                total_sports = sum(coverage.values())
                print(f"   {api_name}: {total_sports} sports across {len(coverage)} endpoints")

        print(f"\n📅 Discovery completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)

    def save_discovery_results(self, filename: Optional[str] = None) -> str:
        """Save comprehensive discovery results"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"api_discovery_results_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.discovery_results, f, indent=2, default=str, ensure_ascii=False)

        print(f"💾 Discovery results saved to: {filename}")
        return filename

    def get_api_details(self, api_key: str) -> Dict:
        """Get detailed information about a specific API"""
        return self.discovery_results.get('apis', {}).get(api_key, {})

    def get_endpoint_details(self, api_key: str, endpoint_name: str) -> Dict:
        """Get detailed information about a specific endpoint"""
        api_data = self.get_api_details(api_key)
        return api_data.get('endpoints_discovered', {}).get(endpoint_name, {})

def main():
    """Main discovery function"""
    print("🚀 Dynamic API Discovery System")
    print("This tool will discover and analyze all available endpoints for each API")
    print("providing detailed insights into data structures and capabilities.\n")

    discoverer = DynamicAPIDiscovery()

    # Run comprehensive discovery
    results = discoverer.discover_all_apis()

    # Save results
    discoverer.save_discovery_results()

    print("\n🎉 Discovery Complete!")
    print("Use the results to understand what data is available from each API")
    print("and plan future endpoint additions based on the discovered capabilities.")

    return results

if __name__ == "__main__":
    main()