"""
Sports prediction engine using historical data and statistical analysis
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date
from collections import defaultdict

from storage.database import DatabaseManager

class MatchPredictor:
    """Predicts match outcomes using historical data and statistical models"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.team_stats_cache = {}
        self.cache_expiry = 3600  # 1 hour

    def predict_match_outcome(self, home_team: str, away_team: str, sport: str = 'soccer') -> Dict:
        """Predict the outcome of a match between two teams"""
        try:
            # Get historical data for both teams
            home_stats = self.get_team_statistics(home_team, sport, days=30)
            away_stats = self.get_team_statistics(away_team, sport, days=30)

            # Get head-to-head statistics
            h2h_stats = self.get_head_to_head_stats(home_team, away_team, sport, days=365)

            # Calculate prediction using multiple factors
            prediction = self._calculate_prediction(home_stats, away_stats, h2h_stats)

            return {
                'home_team': home_team,
                'away_team': away_team,
                'prediction': prediction,
                'confidence': self._calculate_confidence(home_stats, away_stats, h2h_stats),
                'factors': {
                    'home_form': home_stats.get('win_rate', 0),
                    'away_form': away_stats.get('win_rate', 0),
                    'head_to_head': h2h_stats.get('home_win_rate', 0.5)
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Error predicting match {home_team} vs {away_team}: {e}")
            return self._default_prediction(home_team, away_team)

    def get_team_statistics(self, team_name: str, sport: str, days: int = 30) -> Dict:
        """Get comprehensive statistics for a team"""
        cache_key = f"{team_name}_{sport}_{days}"

        # Check cache first
        if cache_key in self.team_stats_cache:
            cached_data = self.team_stats_cache[cache_key]
            if (datetime.now() - cached_data['timestamp']).seconds < self.cache_expiry:
                return cached_data['stats']

        # Calculate statistics from historical data
        matches = self.db.get_recent_matches(sport, days)

        # Filter matches involving this team
        team_matches = []
        for match in matches:
            if (match['home_team'].lower() == team_name.lower() or
                match['away_team'].lower() == team_name.lower()):
                team_matches.append(match)

        if not team_matches:
            return self._empty_team_stats(team_name)

        # Calculate statistics
        stats = self._calculate_team_stats(team_matches, team_name)

        # Cache the results
        self.team_stats_cache[cache_key] = {
            'stats': stats,
            'timestamp': datetime.now()
        }

        return stats

    def _calculate_team_stats(self, matches: List[Dict], team_name: str) -> Dict:
        """Calculate detailed statistics for a team"""
        total_matches = len(matches)
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        clean_sheets = 0

        for match in matches:
            is_home = match['home_team'].lower() == team_name.lower()
            score = match.get('score', '')

            if ':' in score:
                try:
                    home_score, away_score = map(int, score.split(':'))
                    team_score = home_score if is_home else away_score
                    opponent_score = away_score if is_home else home_score

                    goals_for += team_score
                    goals_against += opponent_score

                    if team_score > opponent_score:
                        wins += 1
                    elif team_score == opponent_score:
                        draws += 1
                    else:
                        losses += 1

                    if opponent_score == 0:
                        clean_sheets += 1

                except (ValueError, IndexError):
                    continue

        return {
            'team_name': team_name,
            'total_matches': total_matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': wins / total_matches if total_matches > 0 else 0,
            'draw_rate': draws / total_matches if total_matches > 0 else 0,
            'loss_rate': losses / total_matches if total_matches > 0 else 0,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_difference': goals_for - goals_against,
            'goals_per_game': goals_for / total_matches if total_matches > 0 else 0,
            'clean_sheets': clean_sheets,
            'clean_sheet_rate': clean_sheets / total_matches if total_matches > 0 else 0
        }

    def get_head_to_head_stats(self, home_team: str, away_team: str, sport: str, days: int = 365) -> Dict:
        """Get head-to-head statistics between two teams"""
        matches = self.db.get_recent_matches(sport, days)

        h2h_matches = []
        for match in matches:
            home_match = match['home_team'].lower() == home_team.lower()
            away_match = match['away_team'].lower() == away_team.lower()

            if home_match and away_match:
                h2h_matches.append(match)

        if not h2h_matches:
            return {'total_matches': 0, 'home_wins': 0, 'away_wins': 0, 'draws': 0}

        home_wins = 0
        away_wins = 0
        draws = 0

        for match in h2h_matches:
            score = match.get('score', '')
            if ':' in score:
                try:
                    home_score, away_score = map(int, score.split(':'))
                    if home_score > away_score:
                        home_wins += 1
                    elif away_score > home_score:
                        away_wins += 1
                    else:
                        draws += 1
                except (ValueError, IndexError):
                    continue

        total = len(h2h_matches)
        return {
            'total_matches': total,
            'home_wins': home_wins,
            'away_wins': away_wins,
            'draws': draws,
            'home_win_rate': home_wins / total if total > 0 else 0,
            'away_win_rate': away_wins / total if total > 0 else 0,
            'draw_rate': draws / total if total > 0 else 0
        }

    def _calculate_prediction(self, home_stats: Dict, away_stats: Dict, h2h_stats: Dict) -> str:
        """Calculate match prediction using weighted factors"""
        # Weights for different factors
        weights = {
            'home_form': 0.3,
            'away_form': 0.3,
            'head_to_head': 0.4
        }

        # Home advantage factor
        home_advantage = 0.55

        # Calculate scores
        home_score = (
            home_stats.get('win_rate', 0) * weights['home_form'] * home_advantage +
            (1 - away_stats.get('win_rate', 0)) * weights['away_form'] +
            h2h_stats.get('home_win_rate', 0.5) * weights['head_to_head']
        )

        away_score = (
            away_stats.get('win_rate', 0) * weights['away_form'] * (1 - home_advantage) +
            (1 - home_stats.get('win_rate', 0)) * weights['home_form'] +
            h2h_stats.get('away_win_rate', 0.5) * weights['head_to_head']
        )

        draw_score = h2h_stats.get('draw_rate', 0.3) * 0.5

        # Determine outcome
        max_score = max(home_score, away_score, draw_score)

        if max_score == home_score:
            return 'home_win'
        elif max_score == away_score:
            return 'away_win'
        else:
            return 'draw'

    def _calculate_confidence(self, home_stats: Dict, away_stats: Dict, h2h_stats: Dict) -> float:
        """Calculate confidence level of the prediction"""
        # Base confidence on data availability and consistency
        confidence_factors = []

        # Factor 1: Data availability
        total_matches = (home_stats.get('total_matches', 0) +
                        away_stats.get('total_matches', 0) +
                        h2h_stats.get('total_matches', 0))
        data_confidence = min(total_matches / 20, 1.0)  # Max confidence with 20+ matches
        confidence_factors.append(data_confidence)

        # Factor 2: Form consistency (lower variance = higher confidence)
        home_form = home_stats.get('win_rate', 0)
        away_form = away_stats.get('win_rate', 0)
        form_spread = abs(home_form - away_form)
        consistency_confidence = 1.0 - min(form_spread, 0.5)  # Less spread = more confidence
        confidence_factors.append(consistency_confidence)

        # Factor 3: Head-to-head data
        h2h_confidence = min(h2h_stats.get('total_matches', 0) / 10, 1.0)
        confidence_factors.append(h2h_confidence)

        # Calculate weighted average
        weights = [0.4, 0.4, 0.2]
        confidence = sum(f * w for f, w in zip(confidence_factors, weights))

        return round(confidence * 100, 1)

    def _empty_team_stats(self, team_name: str) -> Dict:
        """Return default stats for teams with no data"""
        return {
            'team_name': team_name,
            'total_matches': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'win_rate': 0.5,  # Neutral assumption
            'draw_rate': 0.2,
            'loss_rate': 0.3,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0,
            'goals_per_game': 0,
            'clean_sheets': 0,
            'clean_sheet_rate': 0
        }

    def _default_prediction(self, home_team: str, away_team: str) -> Dict:
        """Return default prediction when calculation fails"""
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prediction': 'unknown',
            'confidence': 0.0,
            'factors': {'error': 'insufficient_data'},
            'timestamp': datetime.now().isoformat()
        }

    def predict_score(self, home_team: str, away_team: str, sport: str = 'soccer') -> Dict:
        """Predict the exact score of a match"""
        try:
            home_stats = self.get_team_statistics(home_team, sport, days=30)
            away_stats = self.get_team_statistics(away_team, sport, days=30)

            # Simple Poisson distribution-based score prediction
            home_attack = home_stats.get('goals_per_game', 1.5)
            away_defense = away_stats.get('goals_against', 0) / max(away_stats.get('total_matches', 1), 1)

            away_attack = away_stats.get('goals_per_game', 1.2)
            home_defense = home_stats.get('goals_against', 0) / max(home_stats.get('total_matches', 1), 1)

            # Expected goals
            expected_home_goals = (home_attack + away_defense) / 2
            expected_away_goals = (away_attack + home_defense) / 2

            # Most likely score (simplified)
            home_goals = round(expected_home_goals)
            away_goals = round(expected_away_goals)

            return {
                'home_team': home_team,
                'away_team': away_team,
                'predicted_score': f"{home_goals}:{away_goals}",
                'expected_home_goals': round(expected_home_goals, 2),
                'expected_away_goals': round(expected_away_goals, 2),
                'confidence': min(self._calculate_confidence(home_stats, away_stats, {}), 70.0),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Error predicting score for {home_team} vs {away_team}: {e}")
            return {
                'home_team': home_team,
                'away_team': away_team,
                'predicted_score': 'unknown',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }