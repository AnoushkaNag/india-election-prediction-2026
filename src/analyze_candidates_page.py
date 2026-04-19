"""
Deep analysis of Myneta candidates page structure.
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.myneta.info/Kerala2026/index.php?action=summary&subAction=candidates"

print(f"Fetching: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.text, 'html.parser')

# Save full HTML to file for inspection
with open('candidates_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("✓ Saved full HTML to candidates_page.html\n")

# Analyze structure
tables = soup.find_all('table')
print(f"Total tables: {len(tables)}\n")

for i, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f"Table {i}: {len(rows)} rows")
    
    # Show first few rows
    for j, row in enumerate(rows[:3]):
        cols = row.find_all(['td', 'th'])
        if cols:
            text = " | ".join([c.get_text(strip=True)[:30] for c in cols])
            print(f"  Row {j}: {text}")
    print()

# Check for divs/sections
divs = soup.find_all('div', class_=True)
print(f"\nTotal divs with class: {len(divs)}")

# Check for data attributes
print("\nChecking for script/data sections...")
scripts = soup.find_all('script')
print(f"Found {len(scripts)} script tags")

for i, script in enumerate(scripts):
    text = script.get_text()[:200]
    if 'data' in text.lower() or 'candidate' in text.lower():
        print(f"\nScript {i} contains data:")
        print(text)

print("\n✓ Analysis complete")
