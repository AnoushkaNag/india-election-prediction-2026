"""
Myneta Scraper using Selenium for JavaScript-rendered content.
Extracts all 2026 candidate data from Myneta.info
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
STATE_CONFIGS = {
    'Kerala': {
        'url': 'https://www.myneta.info/Kerala2026/index.php?action=summary&subAction=candidates',
        'expected': 863
    },
    'Tamil Nadu': {
        'url': 'https://www.myneta.info/TamilNadu2026/index.php?action=summary&subAction=candidates',
        'expected': 1700
    },
    'West Bengal': {
        'url': 'https://www.myneta.info/WestBengal2026/index.php?action=summary&subAction=candidates',
        'expected': 2000
    },
    'Assam': {
        'url': 'https://www.myneta.info/Assam2026/index.php?action=summary&subAction=candidates',
        'expected': 650
    },
    'Puducherry': {
        'url': 'https://www.myneta.info/Puducherry2026/index.php?action=summary&subAction=candidates',
        'expected': 250
    },
}


def setup_driver():
    """Setup Selenium Chrome driver."""
    logger.info("Setting up Chrome driver...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Optional: Run headless (no UI)
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    logger.info("✓ Chrome driver ready\n")
    return driver


def extract_candidates_from_page(driver, state_name):
    """Extract candidates from Myneta page using Selenium with pagination."""
    candidates = []
    page_num = 0
    
    try:
        while True:
            page_num += 1
            logger.info(f"Extracting page {page_num}...")
            
            # Wait for table to load (max 30 seconds)
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
            )
            
            # Get page source and parse with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find the candidate table
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            # Usually the data table is one of the middle tables
            # We look for a table with S.no, Candidate, Constituency, Party columns
            page_candidates = 0
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                
                if len(rows) < 2:
                    continue
                
                # Check header row
                header_row = rows[0]
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                
                # Look for table with these columns
                if any('Candidate' in h for h in headers) and any('Constituency' in h or 'Party' in h for h in headers):
                    logger.info(f"✓ Found candidate table at index {table_idx}")
                    if page_num == 1:
                        logger.info(f"  Headers: {headers[:5]}")
                    
                    # Extract candidate rows
                    for row_idx, row in enumerate(rows[1:]):
                        try:
                            cols = row.find_all('td')
                            
                            if len(cols) >= 4:
                                # Extract: S.No | Candidate | Constituency | Party | ...
                                candidate_name = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                                constituency = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                                party = cols[3].get_text(strip=True) if len(cols) > 3 else ''
                                
                                # Clean up data
                                candidate_name = candidate_name.strip()
                                constituency = constituency.strip()
                                party = party.strip() or 'Unknown'
                                
                                # Filter valid entries
                                if len(candidate_name) > 2 and len(constituency) > 2:
                                    candidates.append({
                                        'state': state_name,
                                        'constituency': constituency,
                                        'candidate_name': candidate_name,
                                        'party': party
                                    })
                                    page_candidates += 1
                        
                        except Exception as e:
                            logger.debug(f"Error parsing row {row_idx}: {e}")
                            continue
                    
                    logger.info(f"✓ Page {page_num}: {page_candidates} candidates")
                    break
            
            # Check for pagination - look for "Next" button
            try:
                # Find pagination links
                next_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next')]")
                
                if next_buttons and len(next_buttons) > 0:
                    next_button = next_buttons[0]
                    # Check if it's disabled
                    if 'class' in next_button.get_attribute('outerHTML'):
                        if 'disabled' in next_button.get_attribute('class'):
                            logger.info(f"No more pages")
                            break
                    
                    # Click next
                    logger.info(f"Clicking Next button...")
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)  # Wait for next page to load
                else:
                    logger.info(f"No Next button found - end of pagination")
                    break
            
            except Exception as e:
                logger.info(f"No more pages or pagination error: {e}")
                break
        
        logger.info(f"✓ Total extracted: {len(candidates)} candidates from {page_num} pages\n")
    
    except Exception as e:
        logger.error(f"Error extracting candidates: {e}")
    
    return candidates


def scrape_all_states():
    """Scrape all states using Selenium."""
    
    logger.info("\n" + "="*70)
    logger.info("MYNETA SCRAPER (SELENIUM) - 2026 STATE ASSEMBLY ELECTIONS")
    logger.info("="*70 + "\n")
    
    driver = setup_driver()
    all_candidates = []
    
    try:
        for state, config in STATE_CONFIGS.items():
            url = config['url']
            expected = config['expected']
            
            logger.info(f"\n{'='*70}")
            logger.info(f"Scraping {state} (expecting ~{expected} candidates)")
            logger.info(f"{'='*70}")
            logger.info(f"URL: {url}\n")
            
            try:
                # Navigate to page
                logger.info("Loading page...")
                driver.get(url)
                
                # Wait for page to load
                time.sleep(3)
                
                # Extract candidates
                candidates = extract_candidates_from_page(driver, state)
                all_candidates.extend(candidates)
                
                logger.info(f"✓ {state}: {len(candidates)} candidates\n")
                
                # Rate limiting
                time.sleep(2)
            
            except Exception as e:
                logger.error(f"Error scraping {state}: {e}\n")
                continue
    
    finally:
        # Close driver
        driver.quit()
        logger.info("✓ Driver closed")
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"SCRAPING COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Total candidates: {len(all_candidates)}\n")
    
    if all_candidates:
        df = pd.DataFrame(all_candidates)
        
        logger.info("State distribution:")
        state_counts = df['state'].value_counts().sort_index()
        for state, count in state_counts.items():
            logger.info(f"  {state:20s}: {count:4d}")
        
        logger.info(f"\nTotal unique constituencies: {df['constituency'].nunique()}")
        logger.info(f"Total unique parties: {df['party'].nunique()}")
        
        return df
    
    return pd.DataFrame()


def clean_and_save(df):
    """Clean data and save to outputs folder."""
    
    if df.empty:
        logger.error("No data to clean")
        return False
    
    logger.info(f"\n{'='*70}")
    logger.info("CLEANING DATA")
    logger.info(f"{'='*70}\n")
    
    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=['state', 'constituency', 'candidate_name', 'party'])
    after = len(df)
    logger.info(f"Removed {before - after} duplicates")
    
    # Remove missing values
    before = len(df)
    df = df.dropna(subset=['state', 'constituency', 'candidate_name', 'party'])
    after = len(df)
    logger.info(f"Removed {before - after} rows with missing values")
    
    # Save
    output_path = 'outputs/myneta_candidates_cleaned.csv'
    df.to_csv(output_path, index=False)
    logger.info(f"\n✓ Saved {len(df)} records to {output_path}")
    
    return True


if __name__ == '__main__':
    # Scrape
    df = scrape_all_states()
    
    # Clean and save
    if not df.empty:
        clean_and_save(df)
        
        logger.info(f"\n✅ Pipeline complete!")
        logger.info(f"Next: Run merge_myneta.py to integrate with predictions")
    else:
        logger.error("\n❌ No data scraped")
