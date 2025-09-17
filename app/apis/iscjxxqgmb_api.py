"""
ISCJXXQGMB API integration - Comprehensive sports data collection
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import logging
import time
import random
import requests
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from ratelimit import limits, sleep_and_retry

from .base_api import BaseAPI


class ISCJXXQGMBAPI(BaseAPI):
    """ISCJXXQGMB API integration with comprehensive functionality"""

    def __init__(self):
        super().__init__(
            base_url="https://iscjxxqgmb.com/api",
            rate_limit=50,  # Conservative rate limiting
            timeout=30
        )

        # Sports mapping (ID -> name)
        self.sports_map = {
            1: 'soccer', 45: 'cricket', 7: 'basketball', 3: 'tennis',
            13: 'volleyball', 19: 'baseball', 17: 'handball', 5: 'ice_hockey',
            21: 'futsal', 57: 'table_tennis', 161: 'kabaddi', 211: 'padel_tennis',
            144: 'basketball_3x3', 23: 'martial_arts', 9: 'boxing',
            215: 'bare_knuckle_boxing', 197: 't_basket', 201: 't_kick',
            35: 'american_football', 51: 'aussie_rules', 31: 'snooker',
            27: 'chess', 39: 'darts', 15: 'formula_1', 61: 'floorball',
            169: 'gaelic_football', 49: 'rugby', 181: 'lacrosse',
            69: 'water_polo', 73: 'bandy', 189: 'ski_jumping',
            191: 'horse_racing', 193: 'dog_racing', 195: 'chariot_racing',
            75: 'counter_strike', 11: 'esports', 77: 'league_of_legends',
            154: 'valorant'
        }

        # Reverse mapping (name -> ID)
        self.sports_ids = {v: k for k, v in self.sports_map.items()}

        # Live status mappings for different sports
        self.live_statuses = {
            'soccer': {'1st_half', '2nd_half', 'extra_time', 'break', 'in_play', 'live'},
            'cricket': {'live', 'in_play', 'break', 'innings', 'bowling', 'batting', '1st_innings', '2nd_innings'},
            'basketball': {'1st_quarter', '2nd_quarter', '3rd_quarter', '4th_quarter', 'overtime', 'in_play', 'live'},
            'tennis': {'set_1', 'set_2', 'set_3', 'set_4', 'set_5', 'in_play', 'live'},
            'volleyball': {'set_1', 'set_2', 'set_3', 'set_4', 'set_5', 'in_play', 'live'},
            'baseball': {'inning_1', 'inning_2', 'inning_3', 'inning_4', 'inning_5', 'inning_6', 'inning_7', 'inning_8', 'inning_9', 'extra_innings', 'in_play', 'live'},
            'handball': {'1st_half', '2nd_half', 'extra_time', 'in_play', 'live'},
            'ice_hockey': {'1st_period', '2nd_period', '3rd_period', 'overtime', 'shootout', 'in_play', 'live'},
            'futsal': {'1st_half', '2nd_half', 'extra_time', 'in_play', 'live'},
            'table_tennis': {'set_1', 'set_2', 'set_3', 'set_4', 'set_5', 'in_play', 'live'},
            'kabaddi': {'1st_half', '2nd_half', 'in_play', 'live'},
            'padel_tennis': {'set_1', 'set_2', 'set_3', 'set_4', 'set_5', 'in_play', 'live'},
            'basketball_3x3': {'1st_half', '2nd_half', 'overtime', 'in_play', 'live'},
            'martial_arts': {'round_1', 'round_2', 'round_3', 'in_play', 'live'},
            'boxing': {'round_1', 'round_2', 'round_3', 'in_play', 'live'},
            'bare_knuckle_boxing': {'round_1', 'round_2', 'round_3', 'in_play', 'live'},
            't_basket': {'1st_quarter', '2nd_quarter', '3rd_quarter', '4th_quarter', 'in_play', 'live'},
            't_kick': {'round_1', 'round_2', 'round_3', 'in_play', 'live'},
            'american_football': {'1st_quarter', '2nd_quarter', '3rd_quarter', '4th_quarter', 'overtime', 'in_play', 'live'},
            'aussie_rules': {'1st_quarter', '2nd_quarter', '3rd_quarter', '4th_quarter', 'in_play', 'live'},
            'snooker': {'frame_1', 'frame_2', 'in_play', 'live'},
            'chess': {'move_1', 'move_2', 'in_play', 'live'},
            'darts': {'leg_1', 'leg_2', 'set_1', 'set_2', 'in_play', 'live'},
            'formula_1': {'race', 'qualifying', 'in_play', 'live'},
            'floorball': {'1st_period', '2nd_period', '3rd_period', 'in_play', 'live'},
            'gaelic_football': {'1st_half', '2nd_half', 'in_play', 'live'},
            'rugby': {'1st_half', '2nd_half', 'in_play', 'live'},
            'lacrosse': {'1st_quarter', '2nd_quarter', '3rd_quarter', '4th_quarter', 'in_play', 'live'},
            'water_polo': {'1st_quarter', '2nd_quarter', '3rd_quarter', '4th_quarter', 'in_play', 'live'},
            'bandy': {'1st_half', '2nd_half', 'in_play', 'live'},
            'ski_jumping': {'jump_1', 'jump_2', 'in_play', 'live'},
            'horse_racing': {'race', 'in_play', 'live'},
            'dog_racing': {'race', 'in_play', 'live'},
            'chariot_racing': {'race', 'in_play', 'live'},
            'counter_strike': {'round_1', 'round_2', 'in_play', 'live'},
            'esports': {'game_1', 'game_2', 'in_play', 'live'},
            'league_of_legends': {'game_1', 'game_2', 'in_play', 'live'},
            'valorant': {'round_1', 'round_2', 'in_play', 'live'},
        }

        self.sports_cache = {}
        self.cache_expiry = 300  # 5 minutes

    @sleep_and_retry
    @limits(calls=50, period=60)
    def _make_request(self, endpoint: str, params: Optional[Dict] = None,
                      method: str = 'GET', **kwargs) -> Optional[Dict]:
        """Make HTTP request with rate limiting and error handling"""
        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"
            ]),
            "Accept": "application/json",
            "Referer": "https://iscjxxqgmb.com/",
            "Origin": "https://iscjxxqgmb.com"
        }

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout, **kwargs)
            else:
                response = requests.request(method.upper(), url, json=params, headers=headers, timeout=self.timeout, **kwargs)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
            return None
        except ValueError as e:
            logging.error(f"JSON parsing failed for {url}: {e}")
            return None

    def get_sports_list(self) -> List[Dict]:
        """Get comprehensive list of available sports"""
        try:
            data = self._make_request("v1/allsports/sports", {"ss": "all"})

            if data and isinstance(data, list):
                sports = []
                for sport in data:
                    sport_id = sport.get('id')
                    sport_name = self.sports_map.get(sport_id, sport.get('code', 'unknown'))

                    sports.append({
                        'id': sport_id,
                        'name': sport_name,
                        'title': sport.get('title', ''),
                        'code': sport.get('code', ''),
                        'count_pregame': sport.get('count_pregame', 0),
                        'count_live': sport.get('count_live', 0),
                        'total_matches': sport.get('count_pregame', 0) + sport.get('count_live', 0)
                    })

                logging.info(f"✅ ISCJXXQGMB: Found {len(sports)} sports")
                return sports

        except Exception as e:
            logging.error(f"Failed to get sports list: {e}")

        return []

    def get_live_matches(self, sport_id: str, count: int = 250) -> List[Dict]:
        """Get live matches for a specific sport"""
        try:
            # Convert sport name to ID if needed
            if not sport_id.isdigit():
                sport_id_num = self.sports_ids.get(sport_id, sport_id)
            else:
                sport_id_num = int(sport_id)

            data = self._make_request("v3/user/line/list", {
                'lc[]': sport_id_num,
                'ss': 'all',
                'l': count,
                'ltr': 0
            })

            if data and "lines_hierarchy" in data:
                sport_name = self.sports_map.get(int(sport_id_num), 'unknown')
                matches = self._parse_matches(data, 'all', sport_name)

                # Filter for live matches only
                live_matches = [match for match in matches if match.get('type') == 'live']

                logging.info(f"✅ ISCJXXQGMB: Retrieved {len(live_matches)} live matches for sport {sport_id}")
                return live_matches

        except Exception as e:
            logging.error(f"Failed to get live matches for sport {sport_id}: {e}")

        return []

    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get detailed match information"""
        try:
            data = self._make_request(f"v1/lines/{match_id}.json")
            if data:
                return self._process_match_details(data)
        except Exception as e:
            logging.error(f"Failed to get match details for {match_id}: {e}")
        return None

    def get_odds(self, match_id: str) -> Optional[Dict]:
        """Get betting odds for a match"""
        try:
            details = self.get_match_details(match_id)
            if details and 'odds' in details:
                return details['odds']
        except Exception as e:
            logging.error(f"Failed to get odds for {match_id}: {e}")
        return None

    def _parse_matches(self, data, ss_type, sport):
        """Parse matches from API response"""
        parsed_data = []
        if not data or "lines_hierarchy" not in data:
            return parsed_data

        current_time = datetime.now().isoformat()
        current_timestamp = datetime.now().timestamp()
        current_date = datetime.now().date()
        max_date = current_date + timedelta(days=7)

        for hierarchy in data["lines_hierarchy"]:
            for category in hierarchy.get("line_category_dto_collection", []):
                code = (category.get("code") or "").lower().replace("-", "_")
                if code not in {sport, 'football' if sport == 'soccer' else sport}:
                    continue

                for supercategory in category.get("line_supercategory_dto_collection", []):
                    for subcategory in supercategory.get("line_subcategory_dto_collection", []):
                        for line in subcategory.get("line_dto_collection", []):
                            lid = line.get("id")
                            if not lid:
                                continue

                            match = line.get("match", {})
                            stat = match.get("stat", {}) or {}
                            begin_at = match.get("begin_at") or 0

                            if isinstance(begin_at, (int, float)) and begin_at > 1e12:
                                begin_at = int(begin_at / 1000)

                            status = self._safe_get_status(stat)
                            is_live = False
                            if status:
                                is_live = status.lower() in [s.lower() for s in self.live_statuses.get(sport, set())]

                            entry_type = 'live' if is_live else 'pregame' if begin_at > current_timestamp else ss_type

                            if ss_type == 'all' and not is_live and begin_at > current_timestamp:
                                try:
                                    match_date = datetime.fromtimestamp(begin_at).date()
                                    if not (current_date <= match_date <= max_date):
                                        continue
                                except Exception as e:
                                    continue

                            entry = {
                                "timestamp": current_time,
                                "sport": sport,
                                "type": entry_type,
                                "line_id": lid,
                                "match_id": match.get("id"),
                                "title": match.get("title"),
                                "begin_at": datetime.fromtimestamp(begin_at).strftime("%Y-%m-%d %H:%M:%S") if begin_at else None,
                                "home_team": match.get("team1", {}).get("title"),
                                "away_team": match.get("team2", {}).get("title"),
                                "home_team_id": match.get("team1", {}).get("id"),
                                "away_team_id": match.get("team2", {}).get("id"),
                            }

                            if is_live:
                                entry["match_time"] = stat.get("time") or None
                                entry["status"] = status
                                entry["score"] = stat.get("score")
                                if sport in ["soccer", "futsal", "handball", "gaelic_football", "rugby", "bandy"]:
                                    entry.update({"half_time": stat.get("half_time")})
                                elif sport == "cricket":
                                    entry.update({
                                        "overs": stat.get("overs"),
                                        "wickets": stat.get("wickets"),
                                        "runs": stat.get("runs") or stat.get("score"),
                                    })
                                elif sport in ["basketball", "basketball_3x3", "t_basket", "american_football", "aussie_rules", "lacrosse", "water_polo"]:
                                    entry.update({"quarter": stat.get("quarter")})
                                elif sport in ["tennis", "table_tennis", "padel_tennis", "volleyball"]:
                                    entry.update({"set_number": stat.get("set_number"), "games": stat.get("games")})
                                elif sport == "baseball":
                                    entry.update({"inning": stat.get("inning")})
                                elif sport == "ice_hockey":
                                    entry.update({"period": stat.get("period")})
                                elif sport == "floorball":
                                    entry.update({"period": stat.get("period")})
                                elif sport in ["martial_arts", "boxing", "bare_knuckle_boxing", "t_kick"]:
                                    entry.update({"round": stat.get("round")})
                                elif sport == "snooker":
                                    entry.update({"frame": stat.get("frame")})
                                elif sport == "darts":
                                    entry.update({"leg": stat.get("leg"), "set_number": stat.get("set_number")})
                                elif sport == "chess":
                                    entry.update({"move": stat.get("move")})
                                elif sport in ["counter_strike", "esports", "league_of_legends", "valorant"]:
                                    entry.update({"round": stat.get("round") or stat.get("game")})

                            basic_outcomes = self._extract_basic_outcomes(line, sport)
                            entry.update(basic_outcomes)

                            if entry.get("title"):
                                parsed_data.append(entry)

        return parsed_data

    def _safe_get_status(self, stat):
        """Safely get status from stat object"""
        if not stat:
            return None
        return stat.get("status") or stat.get("state") or stat.get("match_status")

    def _extract_basic_outcomes(self, line, sport):
        """Extract basic betting outcomes"""
        outcomes = {o.get("alias"): o.get("odd") for o in line.get("outcomes", []) if o.get("odd") and o.get("status") == 100}
        titles = {o.get("alias"): o.get("title") for o in line.get("outcomes", [])}

        basic = {
            "odds_home": outcomes.get("1"),
            "odds_away": outcomes.get("2"),
            "total_over_odds": outcomes.get("total_over"),
            "total_under_odds": outcomes.get("total_under"),
            "handicap_1_odds": outcomes.get("fora_one"),
            "handicap_2_odds": outcomes.get("fora_two"),
            "total_title": titles.get("total_title"),
            "handicap_title": titles.get("fora_title"),
        }

        if sport in ["soccer", "futsal", "handball", "ice_hockey", "volleyball", "floorball", "bandy", "gaelic_football", "rugby"]:
            basic["odds_draw"] = outcomes.get("x")

        return basic

    def _process_match_details(self, data):
        """Process detailed match information"""
        processed = {
            'odds': {},
            'statistics': {},
            'events': []
        }

        try:
            if data and "outcomes" in data:
                # Extract all available odds
                for outcome in data.get("outcomes", []):
                    if outcome.get("odd") and outcome.get("status") == 100:
                        alias = outcome.get("alias", "")
                        title = outcome.get("title", "")
                        odd_value = outcome.get("odd")

                        processed['odds'][alias] = {
                            'title': title,
                            'odds': odd_value
                        }

        except Exception as e:
            logging.error(f"Error processing match details: {e}")

        return processed

    def _process_match_data(self, match_data: Dict) -> Optional[Dict]:
        """Process raw ISCJXXQGMB match data into standardized format"""
        try:
            return {
                'match_id': str(match_data.get('line_id', '')),
                'home_team': match_data.get('home_team', ''),
                'away_team': match_data.get('away_team', ''),
                'score': match_data.get('score', ''),
                'period': match_data.get('match_time', ''),
                'tournament': match_data.get('title', ''),
                'sport_id': str(match_data.get('sport', '')),
                'is_live': match_data.get('type') == 'live',
                'start_time': match_data.get('begin_at', 0),
                'raw_data': match_data
            }
        except Exception as e:
            logging.error(f"Error processing match data: {e}")
            return None

    def get_request_stats(self) -> Dict:
        """Enhanced stats for ISCJXXQGMB API"""
        base_stats = super().get_request_stats()
        base_stats.update({
            'sports_cached': len(self.sports_cache),
            'sports_supported': len(self.sports_map),
            'api_status': 'active'
        })
        return base_stats