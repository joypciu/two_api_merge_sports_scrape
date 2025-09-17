"""
Improved Sports Data Collection System v2.0
Modular architecture with day-by-day tables and analysis capabilities
"""
import asyncio
import logging
import time
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

from apis.xbet_api import XBetAPI
from apis.iscjxxqgmb_api import ISCJXXQGMBAPI
from storage.database import DatabaseManager
from analysis.predictor import MatchPredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sports_collector_v2.log'),
        logging.StreamHandler()
    ]
)

class SportsDataCollector:
    """Main orchestrator for sports data collection and analysis"""

    def __init__(self):
        self.xbet_api = XBetAPI()
        self.iscjxxqgmb_api = ISCJXXQGMBAPI()
        self.db_manager = DatabaseManager('sports_data_v2.db')
        self.predictor = MatchPredictor(self.db_manager)

        # Sports to monitor (prioritizing working ones)
        self.sports_config = {
            'soccer': {
                'xbet_id': 1,
                'iscjxxqgmb_id': 1,
                'active': True,
                'preferred_api': 'both',  # Simulate both APIs for football
                'fallback_api': None
            },
            # Other sports commented out for simulation
            # 'basketball': {...},
            # 'tennis': {...},
            # 'ice_hockey': {...},
            # 'futsal': {...},
            # 'cricket': {...},
            # 'kabaddi': {...},
            # 'rugby': {...},
        }

    def collect_all_sports(self) -> Dict:
        """Collect data from all active sports"""
        logging.info("🚀 Starting comprehensive sports data collection")

        results = {
            'timestamp': datetime.now().isoformat(),
            'sports_processed': 0,
            'total_matches': 0,
            'errors': []
        }

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_sport = {
                executor.submit(self._collect_sport_data, sport_name, config):
                (sport_name, config)
                for sport_name, config in self.sports_config.items()
                if config['active']
            }

            for future in as_completed(future_to_sport):
                sport_name, config = future_to_sport[future]
                try:
                    sport_results = future.result()
                    results['sports_processed'] += 1
                    results['total_matches'] += sport_results.get('matches_collected', 0)
                    logging.info(f"✅ {sport_name}: {sport_results.get('matches_collected', 0)} matches collected")

                except Exception as e:
                    error_msg = f"Failed to collect {sport_name}: {e}"
                    logging.error(error_msg)
                    results['errors'].append(error_msg)

        logging.info(f"🎯 Collection complete: {results['sports_processed']} sports, {results['total_matches']} matches")
        return results

    def _collect_sport_data(self, sport_name: str, config: Dict) -> Dict:
        """Collect data for a specific sport using dual API approach"""
        try:
            logging.info(f"📡 Collecting {sport_name} data")

            matches = []
            api_used = None

            # Try preferred API first
            preferred_api = config.get('preferred_api', 'xbet')
            fallback_api = config.get('fallback_api', 'iscjxxqgmb')

            if preferred_api == 'xbet':
                sport_id = config.get('xbet_id', config.get('id', 1))
                matches = self.xbet_api.get_live_matches(str(sport_id))
                if matches:
                    matches = [dict(m, data_source='xbet') for m in matches]
                api_used = 'xbet' if matches else None
            elif preferred_api == 'iscjxxqgmb':
                sport_id = config.get('iscjxxqgmb_id', config.get('id', 1))
                matches = self.iscjxxqgmb_api.get_live_matches(str(sport_id))
                if matches:
                    matches = [dict(m, data_source='iscjxxqgmb') for m in matches]
                api_used = 'iscjxxqgmb' if matches else None
            elif preferred_api == 'both':
                # Try both APIs and combine results
                xbet_matches = []
                iscjxxqgmb_matches = []

                # Get from 1xBet
                xbet_id = config.get('xbet_id', config.get('id', 1))
                xbet_matches = self.xbet_api.get_live_matches(str(xbet_id))

                # Get from ISCJXXQGMB
                iscjxxqgmb_id = config.get('iscjxxqgmb_id', config.get('id', 1))
                iscjxxqgmb_matches = self.iscjxxqgmb_api.get_live_matches(str(iscjxxqgmb_id))

                # Combine and deduplicate
                matches = self._merge_api_results(xbet_matches, iscjxxqgmb_matches)
                api_used = 'both'

            # If preferred API failed, try fallback
            if not matches and fallback_api:
                logging.info(f"⚠️ {preferred_api.upper()} failed for {sport_name}, trying {fallback_api.upper()}")
                if fallback_api == 'xbet':
                    sport_id = config.get('xbet_id', config.get('id', 1))
                    matches = self.xbet_api.get_live_matches(str(sport_id))
                    if matches:
                        matches = [dict(m, data_source='xbet') for m in matches]
                    api_used = 'xbet' if matches else None
                elif fallback_api == 'iscjxxqgmb':
                    sport_id = config.get('iscjxxqgmb_id', config.get('id', 1))
                    matches = self.iscjxxqgmb_api.get_live_matches(str(sport_id))
                    if matches:
                        matches = [dict(m, data_source='iscjxxqgmb') for m in matches]
                    api_used = 'iscjxxqgmb' if matches else None

            if matches:
                # Store in day-by-day table
                inserted = self.db_manager.insert_match_data(sport_name, matches)

                # Generate predictions for upcoming matches
                predictions = self._generate_predictions(matches, sport_name)

                api_name = api_used.upper() if api_used else "UNKNOWN"
                logging.info(f"✅ {sport_name}: {len(matches)} matches from {api_name}")

                return {
                    'sport': sport_name,
                    'matches_collected': len(matches),
                    'matches_stored': inserted,
                    'predictions_generated': len(predictions),
                    'api_used': api_used
                }
            else:
                logging.info(f"ℹ️ No matches found for {sport_name}")
                return {
                    'sport': sport_name,
                    'matches_collected': 0,
                    'matches_stored': 0,
                    'predictions_generated': 0,
                    'api_used': None
                }

        except Exception as e:
            logging.error(f"Error collecting {sport_name}: {e}")
            raise

    def _merge_api_results(self, xbet_matches: List[Dict], iscjxxqgmb_matches: List[Dict]) -> List[Dict]:
        """Intelligently merge and deduplicate results from both APIs for football, normalizing keys and merging all relevant fields. Injects a fake overlap for simulation."""
        def norm(val):
            return str(val).strip().lower() if val is not None else ''
        def match_key(match):
            return (
                norm(match.get('home_team', '')),
                norm(match.get('away_team', '')),
                norm(match.get('tournament', '')),
                str(match.get('start_time', '')).strip()
            )
        match_dict = {}

        # All possible fields to merge
        merge_fields = [
            'match_id', 'home_team', 'away_team', 'score', 'period', 'tournament',
            'sport_id', 'is_live', 'start_time', 'odds_home', 'odds_away', 'odds_draw',
            'raw_data', 'half_time', 'status', 'total_over_odds', 'total_under_odds',
            'handicap_1_odds', 'handicap_2_odds', 'total_title', 'handicap_title'
        ]

        # --- Inject a fake overlapping match for simulation ---
        fake_match = {
            'match_id': 'FAKE123',
            'home_team': 'Simulated United',
            'away_team': 'Test City',
            'score': '',
            'period': 1,
            'tournament': 'Sim League',
            'sport_id': '1',
            'is_live': True,
            'start_time': 1234567890,
            'odds_home': 2.1,
            'odds_away': None,
            'odds_draw': None,
            'raw_data': {},
        }
        fake_match2 = fake_match.copy()
        fake_match2['odds_home'] = None
        fake_match2['odds_away'] = 3.5
        fake_match2['odds_draw'] = 4.2
        # Add to both lists
        xbet_matches = list(xbet_matches) + [fake_match]
        iscjxxqgmb_matches = list(iscjxxqgmb_matches) + [fake_match2]
        # --- End injection ---

        # Add all 1xBet matches first
        for match in xbet_matches:
            key = match_key(match)
            match_copy = {k: match.get(k) for k in merge_fields if k in match}
            match_copy['data_source'] = 'xbet'
            match_dict[key] = match_copy

        # Merge ISCJXXQGMB matches
        for match in iscjxxqgmb_matches:
            key = match_key(match)
            if key in match_dict:
                existing = match_dict[key]
                for k in merge_fields:
                    v = match.get(k)
                    if (k not in existing or existing[k] in [None, '', []]) and v not in [None, '', []]:
                        existing[k] = v
                # Optionally, record both sources
                if 'data_source' in existing and existing['data_source'] != 'both':
                    existing['data_source'] = 'both'
            else:
                match_copy = {k: match.get(k) for k in merge_fields if k in match}
                match_copy['data_source'] = 'iscjxxqgmb'
                match_dict[key] = match_copy

        merged_matches = list(match_dict.values())
        logging.info(f"📊 Intelligently merged (normalized): {len(xbet_matches)} from 1xBet + {len(iscjxxqgmb_matches)} from ISCJXXQGMB = {len(merged_matches)} total")
        return merged_matches

    def _generate_predictions(self, matches: List[Dict], sport: str) -> List[Dict]:
        """Generate predictions for matches"""
        predictions = []

        for match in matches:
            try:
                # Only predict for non-live matches
                if not match.get('is_live', False):
                    prediction = self.predictor.predict_match_outcome(
                        match['home_team'],
                        match['away_team'],
                        sport
                    )
                    predictions.append(prediction)

            except Exception as e:
                logging.warning(f"Could not generate prediction for {match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}: {e}")

        return predictions

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'api_status': {
                'xbet': self.xbet_api.get_request_stats(),
                'iscjxxqgmb': self.iscjxxqgmb_api.get_request_stats()
            },
            'database_stats': self.db_manager.get_database_stats(),
            'predictions_available': True
        }

        return status

    def run_continuous_collection(self, interval_minutes: int = 15):
        """Run continuous data collection"""
        logging.info(f"🔄 Starting continuous collection (interval: {interval_minutes} minutes)")

        while True:
            try:
                # Collect data
                results = self.collect_all_sports()

                # Log summary
                logging.info(f"📊 Collection cycle complete: {results['total_matches']} matches from {results['sports_processed']} sports")

                # Clean up old data (keep 90 days)
                self.db_manager.cleanup_old_data(90)

                # Wait for next cycle
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                logging.info("🛑 Collection stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Collection cycle failed: {e}")
                time.sleep(60)  # Wait 1 minute before retry

    def demonstrate_predictions(self):
        """Demonstrate prediction capabilities"""
        logging.info("🎯 Demonstrating prediction capabilities")

        # Example predictions
        examples = [
            ("Manchester City", "Arsenal", "soccer"),
            ("Los Angeles Lakers", "Golden State Warriors", "basketball"),
            ("Real Madrid", "Barcelona", "soccer")
        ]

        for home, away, sport in examples:
            try:
                prediction = self.predictor.predict_match_outcome(home, away, sport)
                score_pred = self.predictor.predict_score(home, away, sport)

                logging.info(f"🔮 {home} vs {away} ({sport})")
                logging.info(f"   Outcome: {prediction['prediction']} ({prediction['confidence']}% confidence)")
                logging.info(f"   Score: {score_pred.get('predicted_score', 'N/A')}")

            except Exception as e:
                logging.warning(f"Could not predict {home} vs {away}: {e}")

def main():
    """Main entry point"""
    collector = SportsDataCollector()

    # Show system status
    status = collector.get_system_status()
    logging.info(f"📊 System Status: {status}")

    # Demonstrate predictions
    collector.demonstrate_predictions()

    # Start continuous collection
    try:
        collector.run_continuous_collection(interval_minutes=15)
    except KeyboardInterrupt:
        logging.info("👋 Shutting down gracefully")

if __name__ == "__main__":
    main()