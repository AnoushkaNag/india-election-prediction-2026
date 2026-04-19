"""
Robust Myneta Scraper - Uses direct API/URL parameters instead of pagination clicking
This approach fetches candidates by appending page/limit parameters to the URL
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# State configurations
STATES = {
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
    options.add_argument('--headless')  # Run headless
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_candidates_all_pages(driver, state_name, state_code):
    """Scrape all candidates from all pages for a state."""
    candidates = []
    page = 0
    
    while True:
        page += 1
        
        # Try both with and without limit parameter
        url = f'https://www.myneta.info/{state_code}/index.php?action=summary&subAction=candidates&pageNo={page}'
        
        logger.info(f"Fetching page {page} for {state_name}...")
        logger.info(f"URL: {url}")
        
        try:
            driver.get(url)
            time.sleep(2)
            
            # Wait for table
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tables = soup.find_all('table')
            
            page_candidates = 0
            found_data = False
            
            # Find candidate table
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                # Check headers
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                if any('Candidate' in h for h in headers):
                    found_data = True
                    
                    # Extract candidates
                    for row in rows[1:]:
                        try:
                            cols = row.find_all('td')
                            if len(cols) >= 4:
                                candidate = cols[1].get_text(strip=True)
                                constituency = cols[2].get_text(strip=True)
                                party = cols[3].get_text(strip=True) or 'Unknown'
                                
                                if len(candidate) > 2 and len(constituency) > 2:
                                    # Check for duplicates
                                    if not any(c['candidate_name'] == candidate and 
                                             c['constituency'] == constituency 
                                             for c in candidates):
                                        candidates.append({
                                            'state': state_name,
                                            'constituency': constituency,
                                            'candidate_name': candidate,
                                            'party': party
                                        })
                                        page_candidates += 1
                        except:
                            pass
                    
                    break
            
            if not found_data or page_candidates == 0:
                logger.info(f"No more candidates found. Total for {state_name}: {len(candidates)}")
                break
            
            logger.info(f"✓ Page {page}: {page_candidates} candidates (Total: {len(candidates)})")
            time.sleep(1)
            
        except Exception as e:
            logger.info(f"End of pagination or error on page {page}: {e}")
            break
    
    return candidates


def scrape_all_states():
    """Scrape all states."""
    logger.info("\n" + "="*70)
    logger.info("MYNETA SCRAPER (ROBUST) - ALL CANDIDATES")
    logger.info("="*70 + "\n")
    
    driver = setup_driver()
    all_candidates = []
    
    try:
        for state_name, state_code in STATES.items():
            logger.info(f"\n{'='*70}")
            logger.info(f"Scraping {state_name}")
            logger.info(f"{'='*70}\n")
            
            candidates = scrape_candidates_all_pages(driver, state_name, state_code)
            all_candidates.extend(candidates)
            
            logger.info(f"✓ {state_name}: {len(candidates)} candidates\n")
            time.sleep(2)
    
    finally:
        driver.quit()
    
    # Results
    logger.info(f"\n{'='*70}")
    logger.info(f"SCRAPING COMPLETE")
    logger.info(f"{'='*70}\n")
    logger.info(f"Total candidates: {len(all_candidates)}")
    
    if all_candidates:
        df = pd.DataFrame(all_candidates)
        
        logger.info("\nState distribution:")
        for state, count in df['state'].value_counts().sort_index().items():
            logger.info(f"  {state}: {count}")
        
        # Save
        output_path = 'outputs/myneta_candidates_cleaned.csv'
        df.to_csv(output_path, index=False)
        logger.info(f"\n✓ Saved to {output_path}")
        
        return df
    
    return pd.DataFrame()


if __name__ == '__main__':
    df = scrape_all_states()
