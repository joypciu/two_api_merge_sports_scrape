"""
Base API class for sports data providers
"""
import requests
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class BaseAPI(ABC):
    """Abstract base class for sports data API providers"""

    def __init__(self, base_url: str, rate_limit: int = 50, timeout: int = 30):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window = 60  # seconds

        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def _rate_limit_wait(self):
        """Implement rate limiting"""
        current_time = time.time()

        # Reset counter if window has passed
        if current_time - self.last_request_time > self.rate_limit_window:
            self.request_count = 0
            self.last_request_time = current_time

        # Wait if we've hit the rate limit
        if self.request_count >= self.rate_limit:
            wait_time = self.rate_limit_window - (current_time - self.last_request_time)
            if wait_time > 0:
                logging.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
                self.request_count = 0

        self.request_count += 1
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None,
                     method: str = 'GET', **kwargs) -> Optional[Dict]:
        """Make HTTP request with error handling and rate limiting"""
        self._rate_limit_wait()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=params, timeout=self.timeout, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
            return None
        except ValueError as e:
            logging.error(f"JSON parsing failed for {url}: {e}")
            return None

    @abstractmethod
    def get_sports_list(self) -> List[Dict]:
        """Get list of available sports"""
        pass

    @abstractmethod
    def get_live_matches(self, sport_id: str) -> List[Dict]:
        """Get live matches for a specific sport"""
        pass

    @abstractmethod
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get detailed information for a specific match"""
        pass

    @abstractmethod
    def get_odds(self, match_id: str) -> Optional[Dict]:
        """Get betting odds for a match"""
        pass

    def health_check(self) -> bool:
        """Check if API is responding"""
        try:
            # Simple health check - override in subclasses for specific endpoints
            response = self.session.get(self.base_url, timeout=10)
            return response.status_code == 200
        except:
            return False

    def get_request_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            'request_count': self.request_count,
            'last_request_time': self.last_request_time,
            'rate_limit': self.rate_limit,
            'healthy': self.health_check()
        }