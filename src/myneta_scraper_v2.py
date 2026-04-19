"""
Simplified Myneta scraper that directly fetches candidate data.
Uses pagination and direct URLs instead of relying on link extraction.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# State configurations with direct candidate list URLs
STATE_URLS = {
    'Kerala': 'https://www.myneta.info/Kerala2026/index.php?action=summary&subAction=candidates',
    'Tamil Nadu': 'https://www.myneta.info/TamilNadu2026/index.php?action=summary&subAction=candidates',
    'West Bengal': 'https://www.myneta.info/WestBengal2026/index.php?action=summary&subAction=candidates',
    'Assam': 'https://www.myneta.info/Assam2026/index.php?action=summary&subAction=candidates',
    'Puducherry': 'https://www.myneta.info/Puducherry2026/index.php?action=summary&subAction=candidates',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_page(url, retry_count=3):
    """Fetch page with retry logic."""
    for attempt in range(retry_count):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if attempt < retry_count - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt+1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch after {retry_count} attempts: {e}")
                return None
    return None


def extract_candidates(html, state_name):
    """Extract candidate data from HTML."""
    if not html:
        return []
    
    candidates = []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the main data table
        tables = soup.find_all('table')
        logger.debug(f"Found {len(tables)} tables")
        
        if not tables:
            logger.warning(f"No tables found for {state_name}")
            return []
        
        # Try each table to find one with candidate data
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            logger.debug(f"Table {table_idx} has {len(rows)} rows")
            
            if len(rows) < 2:
                continue
            
            # Check if this table has candidate data
            headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])[:5]]
            logger.debug(f"Headers: {headers}")
            
            # Look for headers that suggest candidate data
            if any('candidate' in h.lower() or 'name' in h.lower() for h in headers):
                logger.info(f"Found candidate table in table {table_idx}")
                
                # Extract candidate rows
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        # Try to extract: candidate name, constituency, party
                        candidate_link = cols[0].find('a')
                        if candidate_link:
                            name_text = candidate_link.get_text(strip=True)
                            
                            # Get other columns
                            constituency = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                            party = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                            
                            if name_text and len(name_text) > 2:  # Filter out empty/junk
                                candidates.append({
                                    'state': state_name,
                                    'constituency': constituency,
                                    'candidate_name': name_text,
                                    'party': party or 'Unknown'
                                })
                
                logger.info(f"Extracted {len(candidates)} candidates from {state_name}")
                break
        
        if not candidates:
            logger.warning(f"No candidates extracted from {state_name} tables")
    
    except Exception as e:
        logger.error(f"Error extracting candidates: {e}")
    
    return candidates


def scrape_all_states():
    """Scrape all states."""
    logger.info("\n" + "="*70)
    logger.info("MYNETA SCRAPER (SIMPLIFIED) - 2026 STATE ASSEMBLY ELECTIONS")
    logger.info("="*70 + "\n")
    
    all_candidates = []
    
    for state, url in STATE_URLS.items():
        logger.info(f"\nScraping {state}...")
        logger.info(f"URL: {url}\n")
        
        html = fetch_page(url)
        if html:
            candidates = extract_candidates(html, state)
            all_candidates.extend(candidates)
            logger.info(f"✓ {state}: {len(candidates)} candidates")
            time.sleep(1)  # Rate limiting
        else:
            logger.error(f"✗ {state}: Failed to fetch page")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"SCRAPING COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Total candidates: {len(all_candidates)}")
    
    if all_candidates:
        df = pd.DataFrame(all_candidates)
        logger.info(f"\nState distribution:")
        print(df['state'].value_counts().to_string())
        return df
    
    return pd.DataFrame()


if __name__ == '__main__':
    df = scrape_all_states()
    if not df.empty:
        df.to_csv('candidates_raw.csv', index=False)
        logger.info(f"\n✓ Saved to candidates_raw.csv")
        print("\nSample data:")
        print(df.head(10))
    else:
        logger.error("\nNo data scraped")
