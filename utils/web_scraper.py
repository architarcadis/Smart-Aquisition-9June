import trafilatura
import requests
from urllib.parse import urljoin, urlparse
import time

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.

    Some common website to crawl information from:
    MLB scores: https://www.mlb.com/scores/YYYY-MM-DD
    """
    try:
        # Send a request to the website with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Use trafilatura's fetch_url which includes better handling
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded is None:
            # Fallback to requests if trafilatura fails
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            downloaded = response.text
        
        # Extract clean text content
        text = trafilatura.extract(downloaded)
        
        if text is None:
            # If extraction fails, try with different settings
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
        
        return text or ""
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error accessing {url}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error extracting content from {url}: {str(e)}")

def get_internal_links(url: str, content: str, max_links: int = 10) -> list:
    """
    Extract internal links from the webpage content for crawl depth functionality
    """
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        base_domain = urlparse(url).netloc
        
        internal_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                full_url = urljoin(url, href)
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = urljoin(url, href)
            
            # Check if it's an internal link
            link_domain = urlparse(full_url).netloc
            if link_domain == base_domain and full_url != url:
                internal_links.append(full_url)
                
                if len(internal_links) >= max_links:
                    break
        
        return internal_links
        
    except Exception as e:
        return []

def crawl_with_depth(starting_urls: list, max_depth: int = 1, delay: float = 1.0) -> dict:
    """
    Crawl websites with specified depth
    Returns a dictionary with URLs as keys and content as values
    """
    crawled_content = {}
    urls_to_process = [(url, 0) for url in starting_urls]  # (url, current_depth)
    processed_urls = set()
    
    while urls_to_process:
        current_url, current_depth = urls_to_process.pop(0)
        
        if current_url in processed_urls or current_depth > max_depth:
            continue
        
        processed_urls.add(current_url)
        
        try:
            # Get content for current URL
            content = get_website_text_content(current_url)
            crawled_content[current_url] = content
            
            # If we haven't reached max depth, get internal links
            if current_depth < max_depth:
                # Get the raw HTML for link extraction
                downloaded = trafilatura.fetch_url(current_url)
                if downloaded:
                    internal_links = get_internal_links(current_url, downloaded)
                    
                    # Add internal links to processing queue
                    for link in internal_links:
                        if link not in processed_urls:
                            urls_to_process.append((link, current_depth + 1))
            
            # Politeness delay
            if delay > 0:
                time.sleep(delay)
                
        except Exception as e:
            # Log error but continue with other URLs
            crawled_content[current_url] = f"Error: {str(e)}"
    
    return crawled_content
