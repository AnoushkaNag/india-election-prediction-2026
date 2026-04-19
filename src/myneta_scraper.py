"""
Myneta Scraper for 2026 State Assembly Elections

Scrapes candidate information from Myneta.info for Indian state elections.
Handles multi-level navigation: State → Constituencies → Candidates
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Tuple
from urllib.parse import urljoin
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# State configurations with correct Myneta URLs for 2026
STATE_CONFIGS = {
    'Kerala': {
        'url': 'https://www.myneta.info/Kerala2026/index.php?action=summary&subAction=constituency',
        'expected_count': 140
    },
    'Tamil Nadu': {
        'url': 'https://www.myneta.info/TamilNadu2026/index.php?action=summary&subAction=constituency',
        'expected_count': 234
    },
    'West Bengal': {
        'url': 'https://www.myneta.info/WestBengal2026/index.php?action=summary&subAction=constituency',
        'expected_count': 294
    },
    'Assam': {
        'url': 'https://www.myneta.info/Assam2026/index.php?action=summary&subAction=constituency',
        'expected_count': 126
    },
    'Puducherry': {
        'url': 'https://www.myneta.info/Puducherry2026/index.php?action=summary&subAction=constituency',
        'expected_count': 30
    }
}

# HTTP headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_page(url: str, retry_count: int = 3) -> BeautifulSoup:
    """
    Fetch a page with retry logic and error handling.
    
    Args:
        url: URL to fetch
        retry_count: Number of retries on failure
        
    Returns:
        BeautifulSoup object or None if failed
    """
    for attempt in range(retry_count):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retry_count - 1:
                time.sleep(2)  # Wait before retry
            else:
                logger.error(f"Failed to fetch {url} after {retry_count} attempts")
                return None
    return None


def get_constituency_links(state_page: BeautifulSoup, base_url: str, state_name: str) -> List[Tuple[str, str]]:
    """
    Extract constituency links from state index page.
    
    Args:
        state_page: BeautifulSoup object of state page
        base_url: Base URL for resolving relative links
        state_name: Name of state (for logging)
        
    Returns:
        List of (constituency_name, url) tuples
    """
    constituency_links = []
    
    try:
        # Try multiple selectors to find constituency links
        selectors = [
            'a[href*="constituency"]',
            'a[href*="const"]',
            'table a',
            'td a'
        ]
        
        links_found = []
        for selector in selectors:
            links_found = state_page.select(selector)
            if links_found:
                logger.debug(f"Found {len(links_found)} links using selector: {selector}")
                break
        
        if not links_found:
            logger.warning(f"No constituency links found for {state_name}")
            return []
        
        # Extract unique constituency links
        seen_urls = set()
        for link in links_found:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if href and text and 'logout' not in href.lower():
                full_url = urljoin(base_url, href)
                
                # Avoid duplicates
                if full_url not in seen_urls and text:
                    constituency_links.append((text, full_url))
                    seen_urls.add(full_url)
        
        logger.info(f"{state_name}: Found {len(constituency_links)} constituency links")
        return constituency_links
        
    except Exception as e:
        logger.error(f"Error extracting constituency links for {state_name}: {e}")
        return []


def extract_candidates_from_constituency(constituency_page: BeautifulSoup, 
                                         constituency_name: str, 
                                         state_name: str) -> List[Dict]:
    """
    Extract candidate information from constituency page.
    
    Args:
        constituency_page: BeautifulSoup object of constituency page
        constituency_name: Name of constituency
        state_name: Name of state
        
    Returns:
        List of dictionaries with candidate info
    """
    candidates = []
    
    try:
        # Find candidate table(s)
        tables = constituency_page.find_all('table')
        
        if not tables:
            logger.debug(f"No tables found in {state_name}/{constituency_name}")
            return []
        
        # Parse tables for candidate data
        for table in tables:
            rows = table.find_all('tr')
            
            if len(rows) < 2:  # Need header + at least 1 data row
                continue
            
            # Try to identify header row
            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(['th', 'td'])]
            
            # Look for candidate name and party columns
            candidate_idx = None
            party_idx = None
            
            for idx, header in enumerate(headers):
                if any(keyword in header for keyword in ['name', 'candidate', 'cand']):
                    candidate_idx = idx
                elif any(keyword in header for keyword in ['party', 'partie']):
                    party_idx = idx
            
            # If we found relevant columns, extract data
            if candidate_idx is not None:
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) > candidate_idx:
                        candidate_name = cells[candidate_idx].get_text(strip=True)
                        party = cells[party_idx].get_text(strip=True) if party_idx is not None and len(cells) > party_idx else 'Unknown'
                        
                        # Filter out non-candidate rows
                        if candidate_name and len(candidate_name) > 1 and 'S.No' not in candidate_name:
                            candidates.append({
                                'state': state_name,
                                'constituency': constituency_name,
                                'candidate_name': candidate_name.strip(),
                                'party': party.strip()
                            })
        
        if candidates:
            logger.debug(f"{state_name}/{constituency_name}: Extracted {len(candidates)} candidates")
        
        return candidates
        
    except Exception as e:
        logger.error(f"Error extracting candidates from {state_name}/{constituency_name}: {e}")
        return []


def scrape_state(state_name: str) -> List[Dict]:
    """
    Scrape all candidates for a state.
    
    Args:
        state_name: Name of state to scrape
        
    Returns:
        List of candidate dictionaries
    """
    if state_name not in STATE_CONFIGS:
        logger.error(f"Unknown state: {state_name}")
        return []
    
    config = STATE_CONFIGS[state_name]
    base_url = config['url']
    expected_count = config['expected_count']
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Scraping {state_name} (expecting {expected_count} constituencies)")
    logger.info(f"{'='*70}")
    
    all_candidates = []
    
    # Step 1: Fetch state index page
    logger.info(f"Fetching state index for {state_name}...")
    state_page = fetch_page(base_url)
    
    if not state_page:
        logger.error(f"Failed to fetch state page for {state_name}")
        return []
    
    # Step 2: Get constituency links
    constituency_links = get_constituency_links(state_page, base_url, state_name)
    
    if not constituency_links:
        logger.error(f"No constituencies found for {state_name}")
        return []
    
    logger.info(f"Processing {len(constituency_links)} constituencies for {state_name}...")
    
    # Step 3: Visit each constituency and extract candidates
    for idx, (constituency_name, const_url) in enumerate(constituency_links, 1):
        logger.info(f"  [{idx}/{len(constituency_links)}] {constituency_name}...")
        
        # Rate limiting
        time.sleep(1)
        
        # Fetch constituency page
        const_page = fetch_page(const_url)
        
        if not const_page:
            logger.warning(f"  Failed to fetch page for {constituency_name}")
            continue
        
        # Extract candidates
        candidates = extract_candidates_from_constituency(const_page, constituency_name, state_name)
        all_candidates.extend(candidates)
    
    logger.info(f"Scraped {len(all_candidates)} candidate records for {state_name}")
    
    if len(all_candidates) == 0:
        logger.warning(f"⚠️  No candidates found for {state_name}!")
    
    return all_candidates


def scrape_all_states() -> pd.DataFrame:
    """
    Scrape all states and combine into single DataFrame.
    
    Returns:
        DataFrame with all candidate data
    """
    all_data = []
    
    logger.info("\n" + "="*70)
    logger.info("MYNETA SCRAPER - 2026 STATE ASSEMBLY ELECTIONS")
    logger.info("="*70)
    
    for state_name in STATE_CONFIGS.keys():
        try:
            state_data = scrape_state(state_name)
            all_data.extend(state_data)
        except Exception as e:
            logger.error(f"Error scraping {state_name}: {e}")
            continue
    
    df = pd.DataFrame(all_data)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"SCRAPING COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Unique constituencies: {df['constituency'].nunique()}")
    logger.info(f"State distribution:\n{df['state'].value_counts().sort_index()}")
    
    return df


if __name__ == '__main__':
    # Test scraper
    df = scrape_all_states()
    print(f"\nScraped data shape: {df.shape}")
    print(f"\nFirst few rows:")
    print(df.head(10))
