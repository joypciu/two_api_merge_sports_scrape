"""
1xBet API integration - Working excellently
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_api import BaseAPI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api_client import XBetApiClient  # Import existing working client

class XBetAPI(BaseAPI):
    """1xBet API integration with enhanced functionality"""

    def __init__(self):
        super().__init__(
            base_url="https://1xlite-86981.world/service-api",
            rate_limit=45,  # Slightly below limit for safety
            timeout=30
        )
        self.client = XBetApiClient()
        self.sports_cache = {}
        self.cache_expiry = 300  # 5 minutes

    def get_sports_list(self) -> List[Dict]:
        """Get comprehensive list of available sports"""
        try:
            data = self._make_request("LiveFeed/GetSportsShortZip", {
                'lng': 'en',
                'gr': 1258,
                'country': 19,
                'virtualSports': 'true',
                'groupChamps': 'true'
            })

            if data and 'Value' in data:
                sports = []
                for sport in data['Value']:
                    sports.append({
                        'id': sport.get('I'),
                        'name': sport.get('N'),
                        'category': sport.get('C'),
                        'count': sport.get('C1', 0)  # Number of matches
                    })
                logging.info(f"✅ 1xBet: Found {len(sports)} sports")
                return sports

        except Exception as e:
            logging.error(f"Failed to get sports list: {e}")

        return []

    def get_live_matches(self, sport_id: str, count: int = 250) -> List[Dict]:
        """Get live matches for a specific sport"""
        try:
            # Use the existing working async client
            matches_data = asyncio.run(self.client.fetch_matches(
                sports=int(sport_id),
                count=count
            ))

            if matches_data and matches_data.get('Success') and matches_data.get('Value'):
                matches = []
                for match in matches_data['Value']:
                    # Check if 'E' field exists for odds
                    if 'E' not in match:
                        logging.debug(f"Match {match.get('I', 'unknown')} has no 'E' field for odds")

                    processed_match = self._process_match_data(match)
                    if processed_match:
                        matches.append(processed_match)

                logging.info(f"SUCCESS: 1xBet: Retrieved {len(matches)} matches for sport {sport_id}")
                return matches

        except Exception as e:
            logging.error(f"Failed to get live matches for sport {sport_id}: {e}")

        return []

    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get detailed match information"""
        try:
            details = asyncio.run(self.client.fetch_match_details(match_id))
            if details:
                return self._process_match_details(details)
        except Exception as e:
            logging.error(f"Failed to get match details for {match_id}: {e}")
        return None

    def get_odds(self, match_id: str) -> Optional[Dict]:
        """Get betting odds for a match"""
        try:
            # Get detailed match data which includes odds
            details = self.get_match_details(match_id)
            if details and 'odds' in details:
                return details['odds']
        except Exception as e:
            logging.error(f"Failed to get odds for {match_id}: {e}")
        return None

    def _process_match_data(self, match_data: Dict) -> Optional[Dict]:
        """Process raw 1xBet match data into standardized format"""
        try:
            # Extract team names
            home_team = ""
            away_team = ""

            if 'O1' in match_data:
                if isinstance(match_data['O1'], dict):
                    home_team = match_data['O1'].get('N', '')
                elif isinstance(match_data['O1'], str):
                    home_team = match_data['O1']

            if 'O2' in match_data:
                if isinstance(match_data['O2'], dict):
                    away_team = match_data['O2'].get('N', '')
                elif isinstance(match_data['O2'], str):
                    away_team = match_data['O2']

            if not home_team or not away_team:
                return None

            # Extract score information
            score = ""
            period = 1
            if 'SC' in match_data and match_data['SC']:
                scores = match_data['SC']
                if 'FS' in scores:
                    home_score = scores['FS'].get('S1', '')
                    away_score = scores['FS'].get('S2', '')
                    if home_score and away_score:
                        score = f"{home_score}:{away_score}"

                if 'CP' in scores:
                    period = scores['CP']

            # Extract tournament info
            tournament = ""
            if 'LE' in match_data and match_data['LE']:
                tournament = match_data['LE']

            # Count events and extract odds
            event_count = 0
            odds_home = None
            odds_away = None
            odds_draw = None

            if 'E' in match_data:
                event_count = len(match_data['E'])
                for event in match_data['E']:
                    if event.get('G') == 1:  # Main odds
                        odds_data = self._extract_odds(event)
                        if odds_data.get('home_win') and not odds_home:
                            odds_home = odds_data.get('home_win')
                        if odds_data.get('away_win') and not odds_away:
                            odds_away = odds_data.get('away_win')
                        if odds_data.get('draw') and not odds_draw:
                            odds_draw = odds_data.get('draw')
                    elif event.get('G') == 2:  # Alternative odds location
                        odds_data = self._extract_odds(event)
                        if odds_data.get('home_win') and not odds_home:
                            odds_home = odds_data.get('home_win')
                        if odds_data.get('away_win') and not odds_away:
                            odds_away = odds_data.get('away_win')
                        if odds_data.get('draw') and not odds_draw:
                            odds_draw = odds_data.get('draw')
                    elif event.get('G') == 17:  # Check all G=17 events for odds
                        odds_data = self._extract_odds(event)
                        if odds_data.get('home_win') and not odds_home:
                            odds_home = odds_data.get('home_win')
                        if odds_data.get('away_win') and not odds_away:
                            odds_away = odds_data.get('away_win')
                        if odds_data.get('draw') and not odds_draw:
                            odds_draw = odds_data.get('draw')
                    elif event.get('G') in [15, 62]:  # Check other groups that might have odds
                        odds_data = self._extract_odds(event)
                        if odds_data.get('home_win') and not odds_home:
                            odds_home = odds_data.get('home_win')
                        if odds_data.get('away_win') and not odds_away:
                            odds_away = odds_data.get('away_win')
                        if odds_data.get('draw') and not odds_draw:
                            odds_draw = odds_data.get('draw')

            # Determine match status
            is_live = match_data.get('IsLive', False)
            status = 'live' if is_live else 'pregame'

            # Process start time - convert from Unix timestamp if needed
            start_time_raw = match_data.get('S', 0)
            if isinstance(start_time_raw, (int, float)) and start_time_raw > 0:
                # If it's a reasonable Unix timestamp (after 2020), keep as is
                # Otherwise convert to current time or handle appropriately
                if start_time_raw > 1577836800:  # 2020-01-01
                    start_time = int(start_time_raw)
                else:
                    start_time = int(datetime.now().timestamp())
            else:
                start_time = int(datetime.now().timestamp())

            # Fix period logic - only use meaningful period values
            if period and isinstance(period, (int, float)):
                # Only keep period if it's a reasonable value (1-10)
                if 1 <= int(period) <= 10:
                    final_period = int(period)
                else:
                    final_period = 1  # Default to 1
            else:
                final_period = 1

            return {
                'match_id': str(match_data.get('I', '')),
                'home_team': home_team.strip(),
                'away_team': away_team.strip(),
                'score': score,
                'status': status,
                'period': final_period,
                'tournament': tournament,
                'sport_id': str(match_data.get('SI', '')),
                'event_count': event_count,
                'start_time': start_time,
                'odds_home': odds_home,
                'odds_away': odds_away,
                'odds_draw': odds_draw,
                'raw_data': match_data  # Keep original for additional processing
            }

        except Exception as e:
            logging.error(f"Error processing match data: {e}")
            return None

    def _process_match_details(self, details: Dict) -> Dict:
        """Process detailed match information"""
        processed = {
            'odds': {},
            'statistics': {},
            'events': []
        }

        try:
            if 'Value' in details:
                value = details['Value']

                # Extract odds
                if 'E' in value:
                    for event in value['E']:
                        if 'G' in event and event['G'] == 1:  # Main odds
                            processed['odds'] = self._extract_odds(event)

                # Extract live statistics
                if 'SC' in value:
                    processed['statistics'] = self._extract_statistics(value['SC'])

        except Exception as e:
            logging.error(f"Error processing match details: {e}")

        return processed

    def _extract_odds(self, event_data: Dict) -> Dict:
        """Extract betting odds from event data"""
        odds = {}

        try:
            if 'P' in event_data:
                p_data = event_data['P']

                # Handle case where P is a list of participants
                if isinstance(p_data, list):
                    for participant in p_data:
                        if 'C' in participant:
                            coeff = participant['C']
                            if isinstance(coeff, (int, float)) and coeff > 1:
                                # Map common odds types
                                if participant.get('T') == 1:  # Home win
                                    odds['home_win'] = coeff
                                elif participant.get('T') == 2:  # Away win
                                    odds['away_win'] = coeff
                                elif participant.get('T') == 3:  # Draw
                                    odds['draw'] = coeff
                                elif participant.get('T') == 7:  # Alternative home win
                                    odds['home_win'] = coeff
                                elif participant.get('T') == 8:  # Alternative away win
                                    odds['away_win'] = coeff
                                elif participant.get('T') == 9:  # Alternative draw
                                    odds['draw'] = coeff
                # Handle case where P is a single value (coefficient)
                elif isinstance(p_data, (int, float)):
                    coeff = p_data
                    # Accept both positive and negative coefficients (odds can be < 1)
                    if abs(coeff) > 0.1:  # Filter out very small values
                        # Map different event types to odds
                        g = event_data.get('G')
                        t = event_data.get('T')

                        if g == 2:
                            if t == 7:  # Home win
                                odds['home_win'] = abs(coeff)
                            elif t == 8:  # Away win
                                odds['away_win'] = abs(coeff)
                            elif t == 9:  # Draw
                                odds['draw'] = abs(coeff)
                        elif g == 17:
                            if t == 9:  # Draw
                                odds['draw'] = abs(coeff)
                            elif t == 10:  # Likely away win (since draw is T=9)
                                odds['away_win'] = abs(coeff)
                        elif g == 15:
                            if t == 11:  # Possible home/away odds
                                if not odds.get('home_win'):
                                    odds['home_win'] = abs(coeff)
                                elif not odds.get('away_win'):
                                    odds['away_win'] = abs(coeff)
                            elif t == 12:  # Possible home/away odds
                                if not odds.get('home_win'):
                                    odds['home_win'] = abs(coeff)
                                elif not odds.get('away_win'):
                                    odds['away_win'] = abs(coeff)
                        elif g == 62:
                            if t == 13:  # Possible home/away odds
                                if not odds.get('home_win'):
                                    odds['home_win'] = abs(coeff)
                                elif not odds.get('away_win'):
                                    odds['away_win'] = abs(coeff)
                            elif t == 14:  # Possible home/away odds
                                if not odds.get('home_win'):
                                    odds['home_win'] = abs(coeff)
                                elif not odds.get('away_win'):
                                    odds['away_win'] = abs(coeff)
                        elif g == 1:
                            if t == 1:  # Home win
                                odds['home_win'] = abs(coeff)
                            elif t == 2:  # Away win
                                odds['away_win'] = abs(coeff)
                            elif t == 3:  # Draw
                                odds['draw'] = abs(coeff)

        except Exception as e:
            logging.error(f"Error extracting odds: {e}")

        return odds

    def _extract_statistics(self, score_data: Dict) -> Dict:
        """Extract live statistics from score data"""
        stats = {}

        try:
            if 'FS' in score_data:  # Final score
                stats['final_score'] = f"{score_data['FS'].get('S1', '')}:{score_data['FS'].get('S2', '')}"

            if 'CP' in score_data:  # Current period
                stats['current_period'] = score_data['CP']

            if 'PS' in score_data:  # Period scores
                period_scores = []
                for period in score_data['PS']:
                    if isinstance(period, dict):
                        period_scores.append(f"{period.get('S1', 0)}-{period.get('S2', 0)}")
                stats['period_scores'] = period_scores

        except Exception as e:
            logging.error(f"Error extracting statistics: {e}")

        return stats

    def get_request_stats(self) -> Dict:
        """Enhanced stats for 1xBet API"""
        base_stats = super().get_request_stats()
        base_stats.update({
            'sports_cached': len(self.sports_cache),
            'client_status': 'active' if self.client else 'inactive'
        })
        return base_stats