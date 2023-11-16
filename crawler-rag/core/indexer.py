#indexer.py

import logging
import json
import os
from typing import Tuple, Dict, Any, List, Optional

import time
from slugify import slugify

from bs4 import BeautifulSoup

from omegaconf import OmegaConf
from nbconvert import HTMLExporter
import nbformat
import markdown
import docutils.core

from core.utils import html_to_text, detect_language, get_file_size_in_MB, create_session_with_retries
from core.extract import get_content_and_title

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from unstructured.partition.auto import partition
import unstructured as us

import cohere
from weaviate import Client, AuthClientPassword

class Indexer(object):
    def __init__(self, cfg: OmegaConf, reindex: bool = True, remove_code: bool = True) -> None:
        self.cfg = cfg
        self.reindex = reindex
        self.remove_code = remove_code
        self.timeout = cfg.get("timeout", 30)
        self.detected_language: Optional[str] = None

        self.setup()

    def setup(self):
        self.session = create_session_with_retries()
        self.p = sync_playwright().start()
        self.browser = self.p.firefox.launch(headless=True)
        self.cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))
        self.weaviate_client = Client(os.getenv('WEAVIATE_URL'), AuthClientPassword(os.getenv('WEAVIATE_API_KEY')))

    def fetch_content_with_timeout(self, url: str) -> Tuple[str, str] :
        page = context = None
        try:
            context = self.browser.new_context()
            page = context.new_page()
            page.route("**/*", lambda route: route.abort() 
                if route.request.resource_type == "image" 
                else route.continue_() 
            ) 
            page.goto(url, timeout=self.timeout*1000)
            content = page.content()
            out_url = page.url
        except PlaywrightTimeoutError:
            logging.info(f"Page loading timed out for {url}")
            return '', ''
        except Exception as e:
            logging.info(f"Page loading failed for {url} with exception '{e}'")
            content = ''
            out_url = ''
            if not self.browser.is_connected():
                self.browser = self.p.firefox.launch(headless=True)
        finally:
            if context:
                context.close()
            if page:
                page.close()
        return out_url, content

    def index_segments(self, doc_id: str, parts: List[str], metadatas: List[Dict[str, Any]], doc_metadata: Dict[str, Any], title: str) -> bool:
        for part in parts:
            # Generate embedding for each part using Cohere
            embedding_response = self.cohere_client.embed(texts=[part])
            embedding = embedding_response.embeddings[0] if embedding_response.embeddings else None

            # Create a data object for Weaviate
            data_object = {
                "text": part,
                "embedding": embedding,
                # Include other metadata as needed
            }

            # Store the data object in Weaviate
            try:
                self.weaviate_client.data_object().create(data_object, class_name="Document")
            except Exception as e:
                logging.error(f"Failed to index document part in Weaviate: {e}")
                return False

        return True

    def index_url(self, url: str, metadata: Dict[str, Any] = {}) -> bool:
        st = time.time()
        actual_url, html_content = self.fetch_content_with_timeout(url)
        if html_content:
            try:
                url = actual_url
                text, extracted_title = get_content_and_title(html_content, url, self.detected_language, self.remove_code)
                parts = [text]
                logging.info(f"retrieving content took {time.time()-st:.2f} seconds")
            except Exception as e:
                import traceback
                logging.info(f"Failed to crawl {url}, skipping due to error {e}, traceback={traceback.format_exc()}")
                return False

        succeeded = self.index_segments(doc_id=slugify(url), parts=parts, metadatas=[{}]*len(parts), 
                                        doc_metadata=metadata, title=extracted_title)
        return succeeded