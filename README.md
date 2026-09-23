# FlyRank BE-05: The Polite Scraper

A respectful web scraper implementation for educational purposes, targeting the books.toscrape.com practice sandbox.

## Project Classification

### Target Site Analysis
- **URL**: https://books.toscrape.com
- **Type**: Practice sandbox (explicitly labeled "Books to Scrape - Sandbox")
- **Purpose**: Educational web scraping practice site
- **Robots.txt**: Not found (404) - no explicit restrictions
- **Meta robots**: `NOARCHIVE,NOCACHE` - prevents search engine caching but doesn't restrict scraping
- **Scope**: First 3 catalogue pages (~60 unique books)

### Data Scope
The scraper extracts book information including:
- Title, price, availability, rating
- Product URLs and descriptions
- Source page tracking and fetch timestamps
- Normalized pricing (GBP) and validation

### Robots.txt Analysis
**Result**: No robots.txt file found (HTTP 404)
- **Implication**: No explicit crawling restrictions
- **Interpretation**: As a practice sandbox, the site appears designed for scraping exercises
- **Documented at**: 2026-09-23 10:23 UTC

### Ethics Statement
This scraper follows ethical guidelines:

1. **Educational Purpose**: Designed for learning web scraping techniques
2. **Sandbox Target**: Uses a site explicitly created for practice
3. **Respectful Rate Limiting**: Minimum 500ms delays between requests
4. **Proper Identification**: Clear User-Agent identifying educational purpose
5. **Reasonable Scope**: Limited to 60 books across 3 pages
6. **Caching Strategy**: Reduces server load through intelligent caching
7. **Error Handling**: Respects HTTP status codes and implements retry limits

### Technical Approach
- **Language**: Python 3.10+
- **Libraries**: requests, beautifulsoup4, pydantic
- **Caching**: HTML files stored under `cache/` (gitignored)
- **Output**: Structured data in `output/` directory
- **Politeness**: User-Agent, timeouts, status checks, rate limiting