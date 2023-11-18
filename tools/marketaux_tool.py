import os
from dotenv import load_dotenv
import requests
import json
from typing import Optional, Type
from langchain.tools.base import BaseTool, BaseModel
from langchain.pydantic_v1 import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

# Load environment variables
load_dotenv()

# Get API token from environment variables
API_TOKEN = os.getenv('MARKETAUX_API_TOKEN')

class MarketauxToolSchema(BaseModel):
    tikers: str = Field(description="A string of financial securities ticker symbols seperated by commas")

class MarketauxTool(BaseTool):
    name = "Marketaux"
    description = """
        Use to retrieve the latest market news on securities.
        Returns a JSON of article summaries with highlights and article URLs for requesting more information.
        Only use this tool once.
        """
    args_schema: Type[MarketauxToolSchema] = MarketauxToolSchema

    def _run(
        self,
        tickers: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        search_wrapper = MarketauxToolAPI()
        print(tickers)
        return search_wrapper.get_market_news(tickers)

    async def _arun(
        self,
        tickers: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("MarketauxTool does not support async")

# Constants
class MarketauxToolAPI:
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
            res = self._data_parser(data["data"], tickers)
            return res
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

            print(feed_summary)
        return feed_summary