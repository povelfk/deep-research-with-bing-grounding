# common/utils_scraping.py
import trafilatura
import hashlib
from typing import Dict, Optional
from agents import function_tool # Import the decorator

@function_tool
def scrape_web_page(url: str, max_content_length: int = 4000) -> Dict:
    """
    Fetches a URL, extracts the main content, calculates its hash,
    and returns structured data.

    Args:
        url (str): The URL to scrape.
        max_content_length (int): Maximum characters to return for main_content.

    Returns:
        Dict: A dictionary containing scraped data (url, title, main_content,
              content_hash, source, published_date, scrape_error).
    """
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return {
            "url": url,
            "title": "",
            "main_content": "",
            "content_hash": None,
            "source": "",
            "published_date": "",
            "scrape_error": "Failed to fetch URL"
        }

    # Extract content, title, source, date using trafilatura
    main_content = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
        output_format='txt',
        favor_recall=True
    )

    metadata = trafilatura.extract_metadata(downloaded)
    title = metadata.title if metadata and metadata.title else ""
    source = metadata.sitename if metadata and metadata.sitename else ""
    published_date = metadata.date if metadata and metadata.date else ""

    # Truncate content if it exceeds the limit
    if len(main_content) > max_content_length:
        main_content = main_content[:max_content_length] + "..."

    return {
        "url": url,
        "title": title,
        "main_content": main_content,
        "source": source,
        "published_date": published_date,
        "scrape_error": None
    }
