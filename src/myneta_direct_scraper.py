"""
Myneta Direct Search Scraper
Instead of pagination, searches each constituency directly
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

def setup_driver():
    """Setup Selenium Chrome driver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_by_direct_search():
    """
    Direct approach: Load state pages and extract ALL candidates from first page
    Don't try pagination - just get everything visible
    """
    
    logger.info("\n" + "="*70)
    logger.info("MYNETA DIRECT SCRAPER - ALL VISIBLE CANDIDATES")
    logger.info("="*70 + "\n")
    
    states = {
        'Kerala': 'Kerala2026',
        'Tamil Nadu': 'TamilNadu2026',
        'West Bengal': 'WestBengal2026',
        'Assam': 'Assam2026',
        'Puducherry': 'Puducherry2026',
    }
    
    driver = setup_driver()
    all_candidates = []
    
    try:
        for state_name, state_code in states.items():
            logger.info(f"\n{'='*70}")
            logger.info(f"SCRAPING {state_name.upper()}")
            logger.info(f"{'='*70}\n")
            
            # Try to load page with increased rows per page using display parameter
            urls_to_try = [
                f'https://www.myneta.info/{state_code}/index.php?action=summary&subAction=candidates&display=500',
                f'https://www.myneta.info/{state_code}/index.php?action=summary&subAction=candidates&display=1000',
                f'https://www.myneta.info/{state_code}/index.php?action=summary&subAction=candidates',
            ]
            
            candidates_found = 0
            
            for url in urls_to_try:
                try:
                    logger.info(f"Trying: {url}")
                    driver.get(url)
                    
                    # Wait for table
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
                    )
                    
                    time.sleep(2)
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    tables = soup.find_all('table')
                    
                    # Find candidate table
                    for table in tables:
                        rows = table.find_all('tr')
                        if len(rows) < 2:
                            continue
                        
                        headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                        
                        if any('Candidate' in h for h in headers):
                            logger.info(f"  ✓ Found table with {len(rows)-1} rows")
                            
                            # Extract all candidates
                            for row in rows[1:]:
                                try:
                                    cols = row.find_all('td')
                                    if len(cols) >= 4:
                                        candidate = cols[1].get_text(strip=True)
                                        constituency = cols[2].get_text(strip=True)
                                        party = cols[3].get_text(strip=True) or 'Unknown'
                                        
                                        if len(candidate) > 2 and len(constituency) > 2:
                                            # Check for duplicates
                                            if not any(c['candidate_name'] == candidate and c['constituency'] == constituency for c in all_candidates):
                                                all_candidates.append({
                                                    'state': state_name,
                                                    'constituency': constituency,
                                                    'candidate_name': candidate,
                                                    'party': party
                                                })
                                                candidates_found += 1
                                except:
                                    pass
                            break
                
                except Exception as e:
                    logger.info(f"  ✗ Failed: {str(e)[:60]}")
                    continue
                
                if candidates_found > 0:
                    break
            
            logger.info(f"✓ {state_name}: {candidates_found} candidates\n")
            time.sleep(2)
    
    finally:
        driver.quit()
    
    # Save
    logger.info(f"\n{'='*70}")
    logger.info("SCRAPING COMPLETE")
    logger.info(f"{'='*70}\n")
    
    logger.info(f"Total candidates: {len(all_candidates)}")
    
    if all_candidates:
        df = pd.DataFrame(all_candidates)
        df = df.drop_duplicates(subset=['candidate_name', 'constituency', 'state'])
        
        logger.info("\nState distribution:")
        for state, count in df['state'].value_counts().sort_index().items():
            logger.info(f"  {state}: {count}")
        
        output_path = 'outputs/myneta_candidates_cleaned.csv'
        df.to_csv(output_path, index=False)
        logger.info(f"\n✓ Saved to {output_path}")
        
        return df
    
    return pd.DataFrame()


if __name__ == '__main__':
    df = scrape_by_direct_search()
