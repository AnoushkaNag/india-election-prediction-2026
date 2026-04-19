# Setup & Usage Guide - Myneta Scraper Pipeline

## 📦 Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `requests` - HTTP requests for scraping
- `beautifulsoup4` - HTML parsing
- `scikit-learn` - ML utilities
- `numpy` - Numerical computing

### 2. Verify Installation
```bash
python -c "import requests; import bs4; print('✓ Dependencies installed')"
```

## 🚀 Quick Start

### Run Complete Pipeline
```bash
python src/run_myneta_pipeline.py
```

This will:
1. Scrape Myneta for all 5 states (~45 minutes)
2. Clean and validate data
3. Merge with existing predictions
4. Generate final_submission_2026.csv

### Expected Output
```
[STEP 1] Scraping Myneta.info for 2026 elections...
  ✓ Scraped 824 candidate records

[STEP 2] Cleaning and validating scraped data...
  ✓ Cleaned data saved

[STEP 3] Merging Myneta data with prediction model...
  ✓ Matched: 824/824 rows

PIPELINE COMPLETE
✅ READY FOR SUBMISSION: 824 rows with candidate names
```

## 🔧 Individual Components

### 1. Scraper Only
```python
from myneta_scraper import scrape_all_states

# Scrape all states
df = scrape_all_states()

# Save raw data
df.to_csv('raw_myneta.csv', index=False)
```

### 2. Single State
```python
from myneta_scraper import scrape_state

# Scrape Kerala only
kerala_data = scrape_state('Kerala')
print(f"Scraped {len(kerala_data)} records for Kerala")
```

### 3. Clean Data
```python
from myneta_cleaner import clean_myneta_data, validate_myneta_data
import pandas as pd

# Load raw data
raw_df = pd.read_csv('raw_myneta.csv')

# Clean
clean_df = clean_myneta_data(raw_df)

# Validate
report = validate_myneta_data(clean_df)
print(report['status'])
```

### 4. Merge with Predictions
```python
from merge_myneta import load_data, merge_candidates

# Load both datasets
predictions, myneta = load_data(
    'outputs/final_submission.csv',
    'outputs/myneta_candidates_cleaned.csv'
)

# Merge
merged, unmatched = merge_candidates(predictions, myneta)
print(f"Matched: {len(merged) - len(unmatched)}")
print(f"Unmatched: {len(unmatched)}")
```

## 📊 File Structure

```
outputs/
├── final_submission.csv           (input - party predictions)
├── final_submission_2026.csv      (output - candidate names)
├── myneta_candidates_cleaned.csv  (intermediate - cleaned candidate data)
└── final_predictions.csv          (reference - model predictions)

src/
├── myneta_scraper.py              (scraping logic)
├── myneta_cleaner.py              (data cleaning)
├── merge_myneta.py                (merging logic)
└── run_myneta_pipeline.py         (orchestrator)
```

## ⚙️ Advanced Usage

### Custom State Configuration
```python
# Modify STATE_CONFIGS in myneta_scraper.py
STATE_CONFIGS = {
    'YourState': {
        'url': 'https://www.myneta.info/YourState2026/...',
        'expected_count': 100
    }
}
```

### Adjust Rate Limiting
```python
# In myneta_scraper.py, modify:
time.sleep(1)  # Change to 2-5 seconds for slower connections
```

### Custom Logging
```python
import logging

# Set log level
logging.getLogger('myneta_scraper').setLevel(logging.DEBUG)

# Or redirect to file
handler = logging.FileHandler('myneta_pipeline.log')
logging.getLogger().addHandler(handler)
```

## 🔍 Validation & Verification

### Check Scraper Output
```python
import pandas as pd

df = pd.read_csv('outputs/myneta_candidates_cleaned.csv')
print(f"Total records: {len(df)}")
print(f"\nBy state:")
print(df['state'].value_counts().sort_index())
print(f"\nCheck for missing:")
print(df.isnull().sum())
```

### Verify Merge
```python
merged = pd.read_csv('outputs/final_submission_2026.csv')

# Check all are candidate names (not parties)
print(merged['predicted_winner'].head(20))

# Check no parties remain
parties = ['BJP', 'Congress', 'DMK', 'AITC', 'INC', 'BJD']
for party in parties:
    count = (merged['predicted_winner'] == party).sum()
    if count > 0:
        print(f"⚠️ Found {count} rows with party '{party}' instead of candidate")
```

## ⏱️ Performance

### Timing Breakdown
- **Scraping**: ~45 minutes (5 states × ~9 min each)
  - ~12 requests per state (1 sec delay each)
  - ~140-300 pages per state
  - ~1 sec per page processing

- **Cleaning**: ~5 seconds

- **Merging**: ~30 seconds

- **Total**: ~50 minutes

### Optimization Tips
- Increase rate limiting if network is slow: `time.sleep(2)`
- Decrease for faster networks: `time.sleep(0.5)` (risky)
- Use proxy/VPN if blocked

## 🐛 Troubleshooting

### Connection Issues
```python
# Check if Myneta is accessible
import requests
response = requests.get('https://www.myneta.info')
print(response.status_code)  # Should be 200
```

### Missing Data
```python
# Check which states have data
df = pd.read_csv('outputs/myneta_candidates_cleaned.csv')
print("States in data:", df['state'].unique())
print("\nMissing states:", set(['Kerala', 'Tamil Nadu', 'West Bengal', 'Assam', 'Puducherry']) - set(df['state'].unique()))
```

### Merge Failures
```python
# Check if files exist
import os
files = [
    'outputs/final_submission.csv',
    'outputs/myneta_candidates_cleaned.csv'
]
for f in files:
    print(f"{f}: {'✓' if os.path.exists(f) else '✗'}")
```

## 📋 Checklist

Before running pipeline:

- [ ] `outputs/final_submission.csv` exists (824 rows)
- [ ] Internet connection working
- [ ] All requirements installed (`pip install -r requirements.txt`)
- [ ] At least 1GB free disk space
- [ ] Python 3.10+

Before deployment:

- [ ] Validation passed (status = PASS)
- [ ] 824 rows in final output
- [ ] No missing constituencies
- [ ] Sample check: Verify candidate names look correct
- [ ] Git commit with versions

## 📞 Support & Debugging

### Enable Verbose Logging
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Then run pipeline
python src/run_myneta_pipeline.py
```

### Save Full Logs
```bash
python src/run_myneta_pipeline.py 2>&1 | tee myneta_pipeline.log
```

### Check Individual State
```bash
python -c "from myneta_scraper import scrape_state; data = scrape_state('Kerala'); print(f'Kerala: {len(data)} records')"
```

## 🎯 Expected Results

After successful run:

```
final_submission_2026.csv should contain:

State          | Count | Sample Candidates
--------------|-------|-------------------
Kerala         | 140   | "Pinarayi Vijayan", "Shashi Tharoor", ...
Tamil Nadu     | 234   | "Stalin", "Jayalalithaa", ...
West Bengal    | 294   | "Mamata Banerjee", "Suvendu Adhikari", ...
Assam          | 126   | "Himanta Biswa Sarma", "Debabrata Saikia", ...
Puducherry     | 30    | "...names from Puducherry...", ...
--------------|-------|
TOTAL          | 824   |
```

All rows should have actual candidate names, not party abbreviations like "BJP" or "Congress".

---

**Last Updated:** April 19, 2026
