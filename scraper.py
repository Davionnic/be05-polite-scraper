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
from typing import Optional, List, Set
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
    
    def extract_book_urls(self, html: str, source_page_url: str) -> List[str]:
        """Extract all book detail page URLs from a catalogue page."""
        soup = BeautifulSoup(html, 'html.parser')
        book_urls = []
        
        # Find all book product containers
        for article in soup.find_all('article', class_='product_pod'):
            # Look for the link to the book detail page
            link = article.find('h3').find('a') if article.find('h3') else None
            if link and link.get('href'):
                # Convert relative URL to absolute
                book_url = urljoin(source_page_url, link['href'])
                book_urls.append(book_url)
        
        return book_urls
    
    def find_next_page_url(self, html: str, current_page_url: str) -> Optional[str]:
        """Find the URL of the next catalogue page."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for next page link
        next_link = soup.find('li', class_='next')
        if next_link:
            link = next_link.find('a')
            if link and link.get('href'):
                return urljoin(current_page_url, link['href'])
        
        return None
    
    def discover_catalogue_pages(self, max_pages: int = 3) -> tuple[List[str], List[str]]:
        """
        Discover catalogue pages and extract all book URLs.
        Returns: (catalogue_page_urls, all_book_urls)
        """
        catalogue_pages = []
        all_book_urls = []
        unique_book_urls = set()
        
        # Start with the first page
        current_url = BASE_URL
        
        for page_num in range(1, max_pages + 1):
            print(f"\nProcessing catalogue page {page_num}: {current_url}")
            
            # Fetch the catalogue page
            html, was_cached = self.fetch_page(current_url)
            catalogue_pages.append(current_url)
            
            # Extract book URLs from this page
            book_urls = self.extract_book_urls(html, current_url)
            print(f"Found {len(book_urls)} books on page {page_num}")
            
            # Add to our collections (dedupe with set)
            for url in book_urls:
                if url not in unique_book_urls:
                    unique_book_urls.add(url)
                    all_book_urls.append(url)
            
            # Find next page (unless we're on the last requested page)
            if page_num < max_pages:
                next_url = self.find_next_page_url(html, current_url)
                if next_url:
                    current_url = next_url
                else:
                    print(f"No next page found after page {page_num}")
                    break
        
        return catalogue_pages, all_book_urls

def stage1():
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

def stage2():
    """Stage 2: Discover three catalogue pages."""
    scraper = PoliteScraper()
    
    # Discover catalogue pages and extract book URLs
    catalogue_pages, book_urls = scraper.discover_catalogue_pages(max_pages=3)
    
    print(f"\nStage 2 Complete:")
    print(f"catalogue_pages={len(catalogue_pages)} discovered={len(book_urls)} unique_urls={len(book_urls)}")
    print(f"\nCatalogue pages discovered:")
    for i, url in enumerate(catalogue_pages, 1):
        print(f"  {i}. {url}")
    
    return catalogue_pages, book_urls

def main():
    """Main entry point - runs the appropriate stage."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stage1":
        stage1()
    elif len(sys.argv) > 1 and sys.argv[1] == "stage2":
        stage2()
    else:
        # Default: run stage 2 for now
        stage2()

if __name__ == "__main__":
    main()