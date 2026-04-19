"""
Myneta Constituency-Based Scraper
Instead of paginating global lists, scrapes each constituency directly
This gets ALL candidates for each constituency in one request
"""

import pandas as pd
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import urllib.parse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Myneta constituency ID mappings (manual - will expand)
CONSTITUENCY_URLS = {
    'Kerala': 'Kerala2026',
    'Tamil Nadu': 'TamilNadu2026',
    'West Bengal': 'WestBengal2026',
    'Assam': 'Assam2026',
    'Puducherry': 'Puducherry2026',
}

def setup_driver():
    """Setup Selenium Chrome driver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_state_candidates(driver, state_name, state_code):
    """
    Scrape ALL candidates from a state by trying pagination with extended wait times
    """
    candidates = []
    page_num = 0
    max_pages = 50  # Safety limit
    
    while page_num < max_pages:
        page_num += 1
        
        # Try pageNo parameter first
        url = f'https://www.myneta.info/{state_code}/index.php?action=summary&subAction=candidates&pageNo={page_num}'
        
        logger.info(f"State: {state_name} | Page {page_num}")
        logger.info(f"  URL: {url}")
        
        try:
            driver.get(url)
            
            # Wait for page to fully load (extended wait)
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
            )
            
            time.sleep(2)  # Extra wait for AJAX
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tables = soup.find_all('table')
            
            page_candidates = 0
            found_table = False
            
            # Find candidate table
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                # Check headers
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                if any('Candidate' in h for h in headers):
                    found_table = True
                    
                    # Extract candidates from this page
                    for row in rows[1:]:
                        try:
                            cols = row.find_all('td')
                            if len(cols) >= 4:
                                sno = cols[0].get_text(strip=True)
                                candidate = cols[1].get_text(strip=True)
                                constituency = cols[2].get_text(strip=True)
                                party = cols[3].get_text(strip=True) or 'Unknown'
                                
                                # Validate
                                if len(candidate) > 2 and len(constituency) > 2:
                                    # Check for exact duplicates
                                    dup_key = (candidate.lower(), constituency.lower(), party.lower())
                                    if not any((c['candidate_name'].lower(), c['constituency'].lower(), c['party'].lower()) == dup_key for c in candidates):
                                        candidates.append({
                                            'state': state_name,
                                            'constituency': constituency,
                                            'candidate_name': candidate,
                                            'party': party
                                        })
                                        page_candidates += 1
                        except Exception as e:
                            pass
                    
                    break
            
            if not found_table:
                logger.info(f"  ✗ No candidate table found on page {page_num}")
                break
            
            if page_candidates == 0:
                logger.info(f"  ✗ No candidates on page {page_num} - stopping pagination")
                break
            
            logger.info(f"  ✓ Page {page_num}: {page_candidates} candidates (Total: {len(candidates)})")
            time.sleep(1)
            
        except Exception as e:
            logger.info(f"  ✗ Error on page {page_num}: {str(e)[:50]}")
            break
    
    return candidates


def scrape_all_states_with_pagination():
    """Scrape all states with improved pagination."""
    
    logger.info("\n" + "="*70)
    logger.info("MYNETA SCRAPER - CONSTITUENCY-BASED (ALL PAGES)")
    logger.info("="*70 + "\n")
    
    driver = setup_driver()
    all_candidates = []
    
    try:
        for state_name, state_code in CONSTITUENCY_URLS.items():
            logger.info(f"\n{'='*70}")
            logger.info(f"SCRAPING {state_name.upper()}")
            logger.info(f"{'='*70}\n")
            
            candidates = scrape_state_candidates(driver, state_name, state_code)
            all_candidates.extend(candidates)
            
            logger.info(f"\n✓ {state_name}: {len(candidates)} total candidates\n")
            time.sleep(3)
    
    finally:
        driver.quit()
    
    # Save and report
    logger.info(f"\n{'='*70}")
    logger.info("SCRAPING COMPLETE")
    logger.info(f"{'='*70}\n")
    
    logger.info(f"Total candidates scraped: {len(all_candidates)}")
    
    if all_candidates:
        df = pd.DataFrame(all_candidates)
        
        logger.info("\nState distribution:")
        for state, count in df['state'].value_counts().sort_index().items():
            logger.info(f"  {state:20s}: {count:5d} candidates")
        
        logger.info(f"\nUnique constituencies: {df['constituency'].nunique()}")
        logger.info(f"Unique parties: {df['party'].nunique()}")
        
        # Remove duplicates and save
        df = df.drop_duplicates(subset=['candidate_name', 'constituency', 'state'])
        
        output_path = 'outputs/myneta_candidates_cleaned.csv'
        df.to_csv(output_path, index=False)
        logger.info(f"\n✓ Saved {len(df)} unique records to {output_path}")
        
        # Show sample
        logger.info("\nSample candidates:")
        for idx, row in df.head(5).iterrows():
            logger.info(f"  {row['state']:15s} | {row['constituency']:25s} | {row['candidate_name']:20s} | {row['party']}")
        
        return df
    
    return pd.DataFrame()


if __name__ == '__main__':
    df = scrape_all_states_with_pagination()
