import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Get API token from environment variables
API_TOKEN = os.getenv('MARKETAUX_API_TOKEN')

# Constants

class MarketauxTool:
    def __init__(self):
        token = os.getenv('MARKETAUX_API_TOKEN')

        if token is None:
            raise Exception('MARKETAUX_API_TOKEN is not a defined environment variable')
        self.token = token

    def get_market_news(self, tickers: str):
        """Fetch market news and return a summary."""
        params = {
            "symbols": tickers,
            "filter_entities": True,
            "language": "en",
            "api_token": self.token
        }
        data = self._fetch_data("https://api.marketaux.com/v1/news/all", params)
        
        if data and "data" in data:
            return self._data_parser(data["data"], tickers)
        else:
            print("Unexpected API response data.")
            return None
        
    def _fetch_data(self, url, params = {}):
        """Fetch data from API and return as JSON."""
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception if invalid response
            return response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            raise e
        
    def _data_parser(self, feed, tickers):
        feed_summary = []
        for f in feed:
            article = {
                "summary": f"{f.get('title')}. {f.get('description')}",
                "article_url": f.get('url'),
            }

            entites = []
            for e in f.get('entities'):
                symbol = e.get('symbol')

                if symbol in tickers:
                    entites.append({
                        "symbol": symbol,
                        "highlights": [h.get('highlight') for h in e.get('highlights')]
                    })

            article["entities"] = entites
            feed_summary.append(article)
        return feed_summary