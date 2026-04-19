import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Wikipedia has 2026 candidate data per constituency
URLS = {
    "Kerala":       "https://en.wikipedia.org/wiki/2026_Kerala_Legislative_Assembly_election",
    "TamilNadu":    "https://en.wikipedia.org/wiki/2026_Tamil_Nadu_Legislative_Assembly_election",
    "WestBengal":   "https://en.wikipedia.org/wiki/2026_West_Bengal_Legislative_Assembly_election",
    "Assam":        "https://en.wikipedia.org/wiki/2026_Assam_Legislative_Assembly_election",
    "Puducherry":   "https://en.wikipedia.org/wiki/2026_Puducherry_Legislative_Assembly_election",
}

all_rows = []

for state, url in URLS.items():
    print(f"\nScraping {state}...")
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    tables = soup.find_all("table", {"class": "wikitable"})
    print(f"  Found {len(tables)} wikitables")

    for table in tables:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        # Look for tables that have constituency + candidate/party columns
        if any(h in headers for h in ["constituency", "seat", "member"]):
            for tr in table.find_all("tr")[1:]:
                cols = [td.get_text(strip=True) for td in tr.find_all("td")]
                if len(cols) >= 2:
                    all_rows.append({
                        "state": state,
                        "raw_col1": cols[0],
                        "raw_col2": cols[1] if len(cols) > 1 else "",
                        "raw_col3": cols[2] if len(cols) > 2 else "",
                        "raw_col4": cols[3] if len(cols) > 3 else "",
                    })

df = pd.DataFrame(all_rows)
df.to_csv("all_states_wiki_raw.csv", index=False)
print(f"\nDone! {len(df)} rows saved to all_states_wiki_raw.csv")
print(df.head(20))