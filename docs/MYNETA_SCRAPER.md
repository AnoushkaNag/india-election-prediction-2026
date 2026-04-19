# Myneta Scraper Pipeline - 2026 Elections

Robust scraper and integration pipeline for extracting 2026 candidate data from Myneta.info and merging with election predictions.

## 📋 Overview

This pipeline:
1. **Scrapes** Myneta.info for all 2026 state assembly election candidates
2. **Cleans** and validates the scraped data
3. **Merges** candidate names with party predictions
4. **Validates** data integrity and consistency
5. **Generates** final submission with actual candidate names

## 📊 Coverage

**States:** 5  
**Constituencies:** 824

| State | Constituencies |
|-------|-----------------|
| Kerala | 140 |
| Tamil Nadu | 234 |
| West Bengal | 294 |
| Assam | 126 |
| Puducherry | 30 |

## 🚀 Quick Start

```bash
# Run complete pipeline
python src/run_myneta_pipeline.py
```

This generates:
- `outputs/myneta_candidates_cleaned.csv` - Cleaned candidate database
- `outputs/final_submission_2026.csv` - Final predictions with candidate names

## 📁 Files

### Scraper
**`src/myneta_scraper.py`**
- Multi-level navigation (State → Constituencies → Candidates)
- Handles inconsistent HTML structures
- Rate limiting (1 second between requests)
- Retry logic for failed requests

### Data Cleaning  
**`src/myneta_cleaner.py`**
- Removes duplicates and empty rows
- Normalizes state/constituency names
- Validates against expected counts
- Generates validation report

### Merge Logic
**`src/merge_myneta.py`**
- Matches candidates by state + constituency
- Resolves party + name mapping
- Fallback to first candidate if party not found
- Validates output integrity

### Runner
**`src/run_myneta_pipeline.py`**
- Orchestrates entire pipeline
- Progress logging
- Error handling and recovery

## 🔧 Key Features

### Robust HTML Parsing
- Multiple selector fallbacks
- Handles missing/inconsistent tables
- Extracts relative URLs properly
- Gracefully skips broken pages

### Rate Limiting
```python
time.sleep(1)  # Between requests
time.sleep(2)  # On retry
```

### Error Handling
- Retry logic (3 attempts)
- Try/except logging
- Continues on partial failures
- Detailed error reports

### Data Validation
- Duplicate detection
- Missing value checking
- State count verification
- Unmatched constituency reporting

## 📊 Output Format

### myneta_candidates_cleaned.csv
```csv
state,constituency,candidate_name,party
Kerala,Thiruvananthapuram,ABC DEF,NOTA
...
```

### final_submission_2026.csv
```csv
state,constituency,predicted_winner
Kerala,Thiruvananthapuram,ABC DEF
...
```

## ⚙️ Technical Details

### Dependencies
- requests: HTTP requests
- beautifulsoup4: HTML parsing
- pandas: Data manipulation

### Myneta URLs
Each state has format:
```
https://www.myneta.info/{State}{Year}/index.php?action=summary&subAction=constituency
```

Examples:
- Kerala2026: https://www.myneta.info/Kerala2026/...
- TamilNadu2026: https://www.myneta.info/TamilNadu2026/...
- WestBengal2026: https://www.myneta.info/WestBengal2026/...

### Matching Strategy

1. **Fetch state page** → Get constituency links
2. **Visit each constituency** → Extract candidate table
3. **Parse candidates** → Extract name, party
4. **Match with predictions** → Find candidate for predicted party
5. **Fallback** → Use top candidate if party not found

## 🔍 Validation Checks

| Check | Pass Criteria |
|-------|---|
| Row Count | 824 rows |
| Duplicates | 0 rows |
| Missing Values | 0 cells |
| Kerala | 140 constituencies |
| Tamil Nadu | 234 constituencies |
| West Bengal | 294 constituencies |
| Assam | 126 constituencies |
| Puducherry | 30 constituencies |

## 📝 Logging

The pipeline provides detailed logging:

```
[STEP 1] Scraping Myneta.info for 2026 elections...
  Kerala: Found 140 constituency links
  Processing 140 constituencies for Kerala...
    [1/140] Thiruvananthapuram...
    [2/140] Attingal...
    ...

[STEP 2] Cleaning and validating scraped data...
  Input shape: (824, 4)
  After removing missing values: 824 rows
  After normalizing states: 5 unique states
  ...

[STEP 3] Merging Myneta data with prediction model...
  MERGE RESULTS
  ✓ Matched: 824/824 rows
  ⚠ Unmatched: 0/824 rows
  ...

PIPELINE COMPLETE
Total time: 45.2 seconds (0.8 minutes)

✅ READY FOR SUBMISSION: 824 rows with candidate names
```

## 🛠️ Troubleshooting

### No candidates found for state
- Check Myneta URL is accessible
- Verify constituency links are being extracted
- Check HTML structure hasn't changed

### Unmatched constituencies
- Party name mismatch (case sensitivity handled)
- No candidates scraped from that page
- Candidate page structure different

### Missing states
- Network timeout - retry
- Myneta server issue - check status
- URL structure changed - update STATE_CONFIGS

## 📌 Notes

- **No Selenium**: Uses requests + BeautifulSoup only
- **Rate Limiting**: 1 second between requests
- **Graceful Degradation**: Continues on partial failures
- **Logging**: All operations logged to console + file
- **Reproducible**: Same seed-based randomness handling

## 🚦 Status Codes

- **PASS**: All validations successful
- **WARNING**: Minor issues, but pipeline completes
- **FAIL**: Critical error, check logs

## 📞 Support

For issues:
1. Check logs for error messages
2. Verify Myneta.info is accessible
3. Ensure outputs/final_submission.csv exists
4. Check Internet connection

---

**Last Updated:** April 19, 2026  
**Pipeline Version:** 1.0  
**Python Version:** 3.10+
