#!/usr/bin/env python3
"""
FlyRank BE-05: The Polite Scraper
A respectful web scraper for books.toscrape.com practice sandbox.
"""

import os
import time
import hashlib
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup

# Configuration
USER_AGENT = "FlyRankBE05Bot/1.0 (Davionnic; educational)"
REQUEST_TIMEOUT = 10
MIN_DELAY = 0.5  # 500ms minimum delay between requests
BASE_URL = "https://books.toscrape.com/"

class PoliteScraper:
    """A polite web scraper with caching and rate limiting."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.last_request_time = 0
        self.cache_dir = Path("cache")
        self.output_dir = Path("output")
        self.cache_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def _wait_politely(self):
        """Ensure minimum delay between requests."""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < MIN_DELAY:
            time.sleep(MIN_DELAY - time_since_last)
    
    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path for a URL."""
        # Create a safe filename from URL
        parsed = urlparse(url)
        path_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        if parsed.path == "/" or parsed.path == "":
            filename = f"index-{path_hash}.html"
        else:
            # Clean path for filename
            clean_path = parsed.path.strip("/").replace("/", "-")
            if parsed.query:
                clean_path += f"-{hashlib.md5(parsed.query.encode()).hexdigest()[:8]}"
            filename = f"{clean_path}-{path_hash}.html"
        return self.cache_dir / filename
    
    def fetch_page(self, url: str, force_fetch: bool = False) -> tuple[str, bool]:
        """
        Fetch a page with caching support.
        Returns: (html_content, was_cache_hit)
        """
        cache_path = self._get_cache_path(url)
        
        # Check cache first
        if not force_fetch and cache_path.exists():
            html = cache_path.read_text(encoding='utf-8')
            size = len(html)
            print(f"CACHE HIT: {url} ({size:,} bytes)")
            return html, True
        
        # Fetch from web
        self._wait_politely()
        
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            html = response.text
            size = len(html)
            
            # Cache the result
            cache_path.write_text(html, encoding='utf-8')
            
            print(f"FETCH: {url} ({size:,} bytes)")
            self.last_request_time = time.time()
            
            return html, False
            
        except requests.RequestException as e:
            print(f"ERROR fetching {url}: {e}")
            raise

def main():
    """Stage 1: Fetch and cache catalogue page 1."""
    scraper = PoliteScraper()
    
    # Fetch first catalogue page (main page is catalogue page 1)
    catalogue_url = BASE_URL
    html, was_cached = scraper.fetch_page(catalogue_url)
    
    # Also save with the expected filename for stage requirement
    cache_file = Path("cache/catalogue-page-1.html")
    cache_file.write_text(html, encoding='utf-8')
    
    print(f"\nStage 1 Complete:")
    print(f"- Cached catalogue page 1: {len(html):,} bytes")
    print(f"- Cache status: {'HIT' if was_cached else 'MISS'}")
    print(f"- File saved: {cache_file}")

if __name__ == "__main__":
    main()