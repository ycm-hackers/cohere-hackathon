crawler.py

from omegaconf import OmegaConf, DictConfig
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from typing import Set, Optional, List, Any
from core.indexer import Indexer
from core.utils import binary_extensions, doc_extensions
from slugify import slugify

get_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

def recursive_crawl(url: str, depth: int, url_regex: List[Any], visited: Optional[Set[str]]=None, session: Optional[requests.Session]=None) -> Set[str]:
    if depth <= 0:
        return set() if visited is None else set(visited)

    if visited is None:
        visited = set()
    if session is None:
        session = requests.Session()

    url_without_fragment = url.split("#")[0]
    if any([url_without_fragment.endswith(ext) for ext in binary_extensions]):
        return visited
    visited.add(url)
    if any([url_without_fragment.endswith(ext) for ext in doc_extensions]):
        return visited

    try:
        response = session.get(url, headers=get_headers)
        soup = BeautifulSoup(response.content, "html.parser")

        new_urls = [urljoin(url, link["href"]) for link in soup.find_all("a") if "href" in link.attrs]
        new_urls = [u for u in new_urls if u not in visited and u.startswith('http') and any([r.match(u) for r in url_regex])]
        new_urls = list(set(new_urls))
        visited.update(new_urls)
        for new_url in new_urls:
            visited = recursive_crawl(new_url, depth-1, url_regex, visited, session)
    except Exception as e:
        logging.info(f"Error {e} in recursive_crawl for {url}")
        pass

    return set(visited)


class Crawler(object):
    def __init__(self, cfg: OmegaConf) -> None:
        self.cfg: DictConfig = DictConfig(cfg)
        self.indexer = Indexer(cfg)

    def crawl(self, urls: List[str]) -> None:
        for url in urls:
            self.indexer.index_url(url)