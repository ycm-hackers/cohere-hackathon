import logging
import pandas as pd
import urllib
import time
from omegaconf import OmegaConf
import datetime
from bs4 import BeautifulSoup 
from ratelimiter import RateLimiter
import cohere
from weaviate import Client, AuthClientPassword
import os

from core.crawler import Crawler
from core.utils import create_session_with_retries

from typing import Dict, List

def download_ticker_data(url, retries=3, delay=5):
    """Attempt to download ticker data with retries."""
    for attempt in range(retries):
        try:
            df = pd.read_csv(url, sep='\t', names=['ticker', 'cik'], dtype=str)
            return df
        except urllib.error.HTTPError as e:
            logging.error(f"HTTP Error when accessing {url}: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error("Max retries reached. Unable to download ticker data.")
    return None

# Replace the direct pd.read_csv call with a call to download_ticker_data
url = 'https://www.sec.gov/include/ticker.txt'
df = download_ticker_data(url)

if df is None:
    logging.error("Failed to download ticker data.")
    # Handle the case where data could not be downloaded
    # For example, load a local backup copy of the file

ticker_dict = dict(zip(df.ticker.map(lambda x: str(x).upper()), df.cik))

def get_headers() -> Dict[str, str]:
    """
    Get a set of headers to use for HTTP requests.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" 
    }
    return headers

def get_filings(cik: str, start_date_str: str, end_date_str: str, filing_type: str = "10-Q") -> List[Dict[str, str]]:
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        "action": "getcompany", "CIK": cik, "type": filing_type, "dateb": "", "owner": "exclude", 
        "start": "", "output": "atom", "count": "100"
    }
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    
    filings: List[Dict[str, str]] = []
    current_start = 0
    rate_limiter = RateLimiter(max_calls=1, period=1)
    session = create_session_with_retries()

    while True:
        params["start"] = str(current_start)
        with rate_limiter:
            response = session.get(base_url, params=params, headers=get_headers())
        if response.status_code != 200:
            logging.warning(f"Error: status code {response.status_code} for {cik}")
            return filings
        soup = BeautifulSoup(response.content, 'lxml-xml')
        entries = soup.find_all("entry")
        if len(entries) == 0:
            break
        for entry in entries:
            filing_date_str = entry.find("filing-date").text
            filing_date = datetime.datetime.strptime(filing_date_str, '%Y-%m-%d')
            if start_date <= filing_date <= end_date:
                try:
                    url = entry.link["href"]
                    with rate_limiter:
                        soup = BeautifulSoup(session.get(url, headers=get_headers()).content, "html.parser")
                    l = soup.select_one('td:-soup-contains("10-Q") + td a')
                    html_url = "https://www.sec.gov" + str(l["href"])
                    l = soup.select_one('td:-soup-contains("Complete submission text file") + td a')
                    submission_url = "https://www.sec.gov" + str(l["href"])
                    filings.append({"date": filing_date_str, "submission_url": submission_url, "html_url": html_url})
                except Exception as e:
                    pass
            elif filing_date < start_date:
                                logging.info(f"Error: filing date {filing_date_str} is before start date {start_date}")
                return filings
        current_start += len(entries)
    return filings

class EdgarCrawler(Crawler):
    def __init__(self, cfg: OmegaConf, endpoint: str, customer_id: str, corpus_id: int, api_key: str) -> None:
        super().__init__(cfg, endpoint, customer_id, corpus_id, api_key)
        self.tickers = self.cfg.edgar_crawler.tickers
        self.start_date = self.cfg.edgar_crawler.start_date
        self.end_date = self.cfg.edgar_crawler.end_date
        self.cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))
        self.weaviate_client = Client(os.getenv('WEAVIATE_URL'), AuthClientPassword(os.getenv('WEAVIATE_API_KEY')))

    def fetch_document_content(self, url):
        # Implement this method to fetch and return the content of the document from the given URL
        pass

    def crawl(self) -> None:
        rate_limiter = RateLimiter(max_calls=1, period=1)
        for ticker in self.tickers:
            logging.info(f"downloading 10-Qs for {ticker}")
            cik = ticker_dict[ticker]
            filings = get_filings(cik, self.start_date, self.end_date, '10-Q')
            if len(filings) == 0:
                logging.info(f"For {ticker}, no filings found in search universe")
                continue
            for filing in filings:
                url = filing['html_url']
                title = ticker + '-' + filing['date'] + '-' + filing['html_url'].split("/")[-1].split(".")[0]
                logging.info(f"indexing document {url}")
                metadata = {'source': 'edgar', 'url': url, 'title': title}
                with rate_limiter:
                    # Fetch the document content
                    document_content = self.fetch_document_content(url)
                    # Generate embeddings for the document using Cohere
                    embedding_response = self.cohere_client.embed(texts=[document_content])
                    embedding = embedding_response.embeddings[0] if embedding_response.embeddings else None
                    # Store the embedding in Weaviate
                    if embedding is not None:
                        succeeded = self.weaviate_client.data_object().create({"embedding": embedding, "metadata": metadata})
                    else:
                        logging.error(f"Failed to generate embedding for url {url}")
                        succeeded = False
                if not succeeded:
                    logging.info(f"Indexing failed for url {url}")
                time.sleep(1)