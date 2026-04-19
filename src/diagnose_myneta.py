"""
Diagnose Myneta HTML structure to fix scraper selectors.
"""

import requests
from bs4 import BeautifulSoup
import json

def diagnose_myneta():
    """Analyze Myneta HTML structure to find correct selectors."""
    
    url = "https://www.myneta.info/Kerala2026/index.php?action=summary&subAction=constituency"
    
    print(f"\n{'='*70}")
    print(f"DIAGNOSING MYNETA HTML STRUCTURE")
    print(f"{'='*70}\n")
    print(f"URL: {url}\n")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print("Fetching page...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✓ Status: {response.status_code}\n")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save raw HTML for inspection
        with open('myneta_sample.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify()[:5000])  # First 5000 chars
        
        # Find all links
        print("Finding all links on page...")
        all_links = soup.find_all('a')
        print(f"Total links: {len(all_links)}\n")
        
        # Analyze link patterns
        link_patterns = {}
        constituency_links = []
        
        for i, link in enumerate(all_links[:30]):  # First 30 links
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if href and len(text) > 1:
                print(f"[{i+1}] Text: '{text}'")
                print(f"    URL: {href}\n")
                
                # Look for constituency patterns
                if 'const' in href.lower() or 'assembly' in text.lower():
                    constituency_links.append({
                        'text': text,
                        'href': href
                    })
        
        if constituency_links:
            print(f"\n{'='*70}")
            print(f"FOUND {len(constituency_links)} POTENTIAL CONSTITUENCY LINKS")
            print(f"{'='*70}\n")
            for link in constituency_links[:5]:
                print(f"- {link['text']}: {link['href']}\n")
        
        # Check for tables
        print(f"\n{'='*70}")
        print(f"CHECKING FOR TABLES")
        print(f"{'='*70}\n")
        
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables\n")
        
        if tables:
            table = tables[0]
            rows = table.find_all('tr')
            print(f"First table has {len(rows)} rows\n")
            
            # Show first few rows
            print("First 3 rows:")
            for i, row in enumerate(rows[:3]):
                cols = row.find_all(['td', 'th'])
                print(f"  Row {i}: {len(cols)} columns")
                if cols:
                    print(f"    Data: {cols[0].get_text(strip=True)[:50]}")
        
        # Find forms/select dropdowns
        print(f"\n{'='*70}")
        print(f"CHECKING FOR FORMS/SELECTORS")
        print(f"{'='*70}\n")
        
        selects = soup.find_all('select')
        print(f"Found {len(selects)} select dropdowns\n")
        
        if selects:
            for i, select in enumerate(selects[:2]):
                options = select.find_all('option')
                print(f"Select {i+1}: {len(options)} options")
                for opt in options[1:4]:  # Skip first blank option, show next 3
                    print(f"  - {opt.get_text(strip=True)} (value: {opt.get('value', 'N/A')})")
                print()
        
        # Check all valid selectors
        print(f"\n{'='*70}")
        print(f"TESTING SELECTORS")
        print(f"{'='*70}\n")
        
        selectors_to_test = [
            'a[href*="constituency"]',
            'a[href*="const"]',
            'a[href*="ac="]',
            'table a',
            'td a',
            'tr a',
            '.constituency',
            '[class*="constituency"]',
            'a[href*="action=candidate"]',
            'a[href*="subAction"]',
        ]
        
        for selector in selectors_to_test:
            found = soup.select(selector)
            if found:
                print(f"✓ '{selector}': Found {len(found)} elements")
                if found:
                    sample = found[0].get_text(strip=True)[:50]
                    print(f"  Sample: {sample}")
                print()
        
        # Print page title and meta info
        print(f"\n{'='*70}")
        print(f"PAGE INFO")
        print(f"{'='*70}\n")
        
        title = soup.find('title')
        print(f"Title: {title.get_text() if title else 'N/A'}")
        
        h1 = soup.find('h1')
        print(f"H1: {h1.get_text(strip=True) if h1 else 'N/A'}")
        
        h2 = soup.find('h2')
        print(f"H2: {h2.get_text(strip=True) if h2 else 'N/A'}")
        
        print(f"\n{'='*70}\n")
        print("✓ Diagnostic complete!")
        print(f"Check myneta_sample.html for first 5000 chars of HTML\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    diagnose_myneta()
