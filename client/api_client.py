import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TrickestClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }

    def get(self, endpoint: str) -> Dict[str, Any]:
        url = f'{self.base_url}/{endpoint}'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise