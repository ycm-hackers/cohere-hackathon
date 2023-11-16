# ingest.py

import logging
import argparse
from omegaconf import OmegaConf, DictConfig
import sys
import os
from dotenv import load_dotenv
import importlib
from core.crawler import Crawler

def instantiate_crawler(base_class, folder_name: str, class_name: str, cfg: DictConfig):
    logging.info(f"Instantiating crawler {class_name} from {folder_name}")
    sys.path.insert(0, os.path.abspath(folder_name))

    crawler_name = class_name.split('Crawler')[0]
    module_name = f"{folder_name}.{crawler_name.lower()}_crawler"
    module = importlib.import_module(module_name)
    
    class_ = getattr(module, class_name)

    if not issubclass(class_, base_class):
        raise TypeError(f"{class_name} is not a subclass of {base_class.__name__}")

    logging.info(f"{class_name} found and instantiated.")
    return class_(cfg)

def main(ticker):
    logging.info(f"Initializing main function for ticker: {ticker}")

    config_name = "config/edgar.yaml"
    cfg: DictConfig = DictConfig(OmegaConf.load(config_name))
    load_dotenv()

    cohere_api_key = os.getenv("COHERE_API_KEY")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL")

    OmegaConf.update(cfg, 'cohere.api_key', cohere_api_key)
    OmegaConf.update(cfg, 'weaviate.api_key', weaviate_api_key)
    OmegaConf.update(cfg, 'weaviate.url', weaviate_url)

    OmegaConf.update(cfg, 'edgar_crawler.tickers', [ticker.upper()])

    crawler_type = cfg.crawling.crawler_type
    logging.info(f"Crawler type set to: {crawler_type}")

    crawler = instantiate_crawler(Crawler, 'crawlers', f'{crawler_type.capitalize()}Crawler', cfg)

    logging.info(f"Starting crawl of type {crawler_type}...")
    crawler.crawl()
    logging.info(f"Finished crawl of type {crawler_type}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ticker', help='The ticker for the company you want to crawl')
    args = parser.parse_args()

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    main(args.ticker)