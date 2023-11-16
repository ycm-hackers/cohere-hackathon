# ingest.py

import logging
import json
import requests
import time
import argparse
from omegaconf import OmegaConf, DictConfig
import sys
import os
from typing import Any
from dotenv import load_dotenv

import importlib
from core.crawler import Crawler

def instantiate_crawler(base_class, folder_name: str, class_name: str, *args, **kwargs) -> Any:   # type: ignore
    sys.path.insert(0, os.path.abspath(folder_name))

    crawler_name = class_name.split('Crawler')[0]
    module_name = f"{folder_name}.{crawler_name.lower()}_crawler"  # Construct the full module path
    module = importlib.import_module(module_name)
    
    class_ = getattr(module, class_name)

    # Ensure the class is a subclass of the base class
    if not issubclass(class_, base_class):
        raise TypeError(f"{class_name} is not a subclass of {base_class.__name__}")

    # Instantiate the class and return the instance
    return class_(*args, **kwargs)

def main(ticker):
    """
    Main function that runs the web crawler based on environment variables.
    
    Reads the necessary environment variables and sets up the web crawler
    accordingly. Starts the crawl loop and logs the progress and errors.
    """

    config_name = "config/edgar.yaml"

    # process arguments 
    cfg: DictConfig = DictConfig(OmegaConf.load(config_name))
    
    # load environment variables
    load_dotenv()

    # get environment variables
    cohere_api_key = os.getenv("COHERE_API_KEY")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL")

    # update config with environment variables
    OmegaConf.update(cfg, 'cohere.api_key', cohere_api_key)
    OmegaConf.update(cfg, 'weaviate.api_key', weaviate_api_key)
    OmegaConf.update(cfg, 'weaviate.url', weaviate_url)

    # Set the ticker in the cfg
    OmegaConf.update(cfg, 'edgar_crawler.tickers', [ticker.upper()])

    crawler_type = cfg.crawling.crawler_type

    # instantiate the crawler
    crawler = instantiate_crawler(Crawler, 'crawlers', f'{crawler_type.capitalize()}Crawler', cfg)

    logging.info(f"Starting crawl of type {crawler_type}...")
    crawler.crawl()
    logging.info(f"Finished crawl of type {crawler_type}...")

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