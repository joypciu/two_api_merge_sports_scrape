import requests
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import httpx
import asyncio
from concurrent.futures import ThreadPoolExecutor

class XBetApiClient:
    def __init__(self, base_url: str = "https://1xlite-86981.world"):
        self.base_url = base_url
        self.service_api_url = f"{base_url}/service-api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f'{base_url}/',
            'Origin': base_url
        })
    
    # async def fetch_matches(
    #     self,
    #     count: int = 10,
    #     language: str = "en",
    #     mode: int = 4,
    #     country: int = 19,
    #     top: bool = True,
    #     group: int = 925
    # ) -> Optional[Dict[str, Any]]:
    #     """Fetch matches from 1xbet API"""
        
    #     url = f"{self.base_url}/LineFeed/Get1x2_VZip"
    #     params = {
    #         "count": count,
    #         "lng": language,
    #         "mode": mode,
    #         "country": country,
    #         "top": str(top).lower(),
    #         "gr": group
    #     }
        
        # try:
        #     response = self.session.get(url, params=params, timeout=10)
        #     response.raise_for_status()
        #     return response.json()
        # except requests.exceptions.RequestException as e:
        #     print(f"Error fetching data: {e}")
        #     return None
        # except json.JSONDecodeError as e:
        #     print(f"Error parsing JSON: {e}")
        #     return None

    async def fetch_matches(
        self,
        sports: int = 1,  # default sport ID (soccer)
        count: int = 20,  # Reduced from 40 to match working params
        lng: str = "en",
        gr: int = 1258,
        mode: int = 4,
        country: int = 19,
        virtual_sports: bool = True,
        no_filter_block_event: bool = True
    ):
        url = f"{self.service_api_url}/LineFeed/Get1x2_VZip"
        params = {
            "sports": sports,
            "count": count,
            "lng": lng,
            "mode": mode,
            "country": country
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching 1xBet matches: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing 1xBet JSON: {e}")
            return None
    
    def save_response(self, data: Dict[str, Any], filename: Optional[str] = None):
        """Save API response to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/api_response_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filename

    async def fetch_match_details(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed information for a specific match"""
        url = f"{self.service_api_url}/LineFeed/GetGameZip"
        params = {
            "id": match_id,
            "lng": "en",
            "cfview": "0",
            "isSubGames": "true",
            "GroupEvents": "true",
            "countevents": "250",
            "grMode": "2"
        }
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching match details for {match_id}: {e}")
            return None

    async def fetch_tournament_info(self, tournament_id: str) -> Optional[Dict[str, Any]]:
        """Fetch tournament/league information"""
        url = f"{self.service_api_url}/LineFeed/GetChampsZip"
        params = {
            "sports": "1",
            "champs": tournament_id,
            "lng": "en",
            "gr": "1258"
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching tournament info for {tournament_id}: {e}")
            return None

    async def fetch_live_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Fetch live match statistics"""
        url = f"{self.service_api_url}/LineFeed/GetGameZip"
        params = {
            "id": match_id,
            "lng": "en",
            "cfview": "1",  # Live view
            "isSubGames": "true",
            "GroupEvents": "true"
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching live stats for {match_id}: {e}")
            return None

    async def fetch_team_info(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Fetch team information and statistics"""
        url = f"{self.service_api_url}/LineFeed/GetParticipantsZip"
        params = {
            "id": team_id,
            "lng": "en"
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching team info for {team_id}: {e}")
            return None

    async def fetch_odds_history(self, match_id: str, hours: int = 24) -> Optional[Dict[str, Any]]:
        """Fetch odds history for a match"""
        url = f"{self.service_api_url}/LineFeed/GetGameHistory"
        params = {
            "id": match_id,
            "hours": hours,
            "lng": "en"
        }
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching odds history for {match_id}: {e}")
            return None

    def fetch_sports_list(self) -> Optional[Dict[str, Any]]:
        """Fetch list of available sports"""
        url = f"{self.service_api_url}/LiveFeed/GetSportsShortZip"
        params = {
            "lng": "en",
            "gr": "1258",
            "country": "19",
            "virtualSports": "true",
            "groupChamps": "true"
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sports list: {e}")
            return None

    def extract_additional_match_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional match information from 1xBet API response"""
        additional_data = {}

        if not match_data:
            return additional_data

        # Handle both single match and list of matches
        if 'Value' in match_data:
            value = match_data['Value']
            if isinstance(value, list) and len(value) > 0:
                # It's a list of matches, take the first one
                game = value[0]
            elif isinstance(value, dict):
                # It's a single match object
                game = value
            else:
                return additional_data
        else:
            return additional_data

        # Extract tournament information
        if 'CI' in game:
            champ_info = game['CI']
            if isinstance(champ_info, dict):
                additional_data.update({
                    'tournament_name': champ_info.get('N', ''),
                    'tournament_id': champ_info.get('I', ''),
                    'tournament_country': champ_info.get('C', ''),
                    'season': champ_info.get('S', '')
                })

        # Extract team information
        if 'O1' in game:
            team1_info = game['O1']
            if isinstance(team1_info, dict):
                additional_data.update({
                    'home_team_full_name': team1_info.get('N', ''),
                    'home_team_logo': team1_info.get('I', ''),
                    'home_team_country': team1_info.get('C', '')
                })

        if 'O2' in game:
            team2_info = game['O2']
            if isinstance(team2_info, dict):
                additional_data.update({
                    'away_team_full_name': team2_info.get('N', ''),
                    'away_team_logo': team2_info.get('I', ''),
                    'away_team_country': team2_info.get('C', '')
                })

        # Extract match details
        if 'GE' in game:
            game_events = game['GE']
            if isinstance(game_events, dict):
                additional_data.update({
                    'match_stage': game_events.get('ST', ''),
                    'match_period': game_events.get('P', ''),
                    'match_time': game_events.get('T', ''),
                    'is_live': game_events.get('LI', False)
                })

        # Extract live statistics if available
        if 'SC' in game:
            scores = game['SC']
            if isinstance(scores, dict):
                if 'FS' in scores:  # Full Score
                    fs = scores['FS']
                    if isinstance(fs, dict):
                        additional_data.update({
                            'home_score': fs.get('S1', ''),
                            'away_score': fs.get('S2', ''),
                            'score_period': scores.get('CP', '')
                        })

                if 'PS' in scores:  # Period Scores
                    ps = scores['PS']
                    if isinstance(ps, list):
                        period_scores = []
                        for period in ps:
                            if isinstance(period, dict):
                                period_scores.append(f"{period.get('S1', '')}-{period.get('S2', '')}")
                        if period_scores:
                            additional_data['period_scores'] = ','.join(period_scores)

        # Extract additional odds
        if 'E' in game:
            events = game['E']
            if isinstance(events, list):
                for event in events:
                    if isinstance(event, dict) and event.get('G') == 1:  # Main outcomes
                        if event.get('T') == 1:  # 1x2
                            outcomes = event.get('P', [])
                            if isinstance(outcomes, list):
                                for outcome in outcomes:
                                    if isinstance(outcome, dict):
                                        if outcome.get('T') == 1:
                                            additional_data['home_win_odds'] = outcome.get('C', '')
                                        elif outcome.get('T') == 2:
                                            additional_data['away_win_odds'] = outcome.get('C', '')
                                        elif outcome.get('T') == 3:
                                            additional_data['draw_odds'] = outcome.get('C', '')

        return additional_data