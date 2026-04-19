# Myneta Scraper - Quick Reference

## 🚀 In 30 Seconds

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run pipeline
python src/run_myneta_pipeline.py

# 3. Check output
ls -la outputs/final_submission_2026.csv
```

## 📁 What Gets Created

| File | Rows | Purpose |
|------|------|---------|
| `outputs/myneta_candidates_cleaned.csv` | 824 | Raw candidate data |
| `outputs/final_submission_2026.csv` | 824 | **Final submission with names** |

## 🎯 Expected Output Structure

```csv
state,constituency,predicted_winner
Kerala,Thiruvananthapuram,"CANDIDATE NAME 1"
Kerala,Attingal,"CANDIDATE NAME 2"
Tamil Nadu,Chennai Central,"CANDIDATE NAME 3"
...
```

**Key:** All rows have ACTUAL CANDIDATE NAMES, not party abbreviations.

## 🔍 Validation Checks

Pipeline validates:
- ✅ 824 total rows
- ✅ No duplicates  
- ✅ No missing values
- ✅ Correct state distribution (KL:140, TN:234, WB:294, AS:126, PY:30)
- ✅ All candidates matched from Myneta

## ⏱️ Timing

| Step | Time |
|------|------|
| Scraping (5 states) | ~45 min |
| Cleaning | ~5 sec |
| Merging | ~30 sec |
| **Total** | **~50 min** |

## 📋 Checklist Before Running

```
[ ] Internet connection working
[ ] Python 3.10+ installed
[ ] requirements.txt installed (pip install -r requirements.txt)
[ ] outputs/final_submission.csv exists (824 rows)
[ ] ~1GB disk space available
```

## 📊 Component Files

| Module | Purpose | Lines |
|--------|---------|-------|
| `src/myneta_scraper.py` | Fetch data from Myneta | 396 |
| `src/myneta_cleaner.py` | Clean & validate | 250+ |
| `src/merge_myneta.py` | Merge with predictions | 280+ |
| `src/run_myneta_pipeline.py` | Orchestrator | 130 |

## 🛠️ Manual Operations

### Scrape only
```python
python -c "from myneta_scraper import scrape_all_states; scrape_all_states().to_csv('test.csv')"
```

### Clean only
```python
python -c "from myneta_cleaner import clean_myneta_data; import pandas as pd; df = pd.read_csv('test.csv'); clean_myneta_data(df).to_csv('clean.csv')"
```

### Check state data
```python
python -c "import pandas as pd; df = pd.read_csv('outputs/myneta_candidates_cleaned.csv'); print(df['state'].value_counts())"
```

## 📞 Troubleshooting

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: requests" | `pip install -r requirements.txt` |
| Connection timeout | Increase `time.sleep()` in scraper to 2-3 sec |
| Missing states | Check Myneta.info accessibility |
| Merge failures | Ensure `outputs/final_submission.csv` exists |

## ✅ Success Indicators

After running pipeline, you should see:

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

## 📖 Documentation

- **Full details**: `docs/MYNETA_SCRAPER.md`
- **Setup guide**: `docs/MYNETA_SETUP_GUIDE.md`
- **This file**: Quick reference

## 🔗 URLs Used

- Kerala: https://www.myneta.info/Kerala2026/...
- Tamil Nadu: https://www.myneta.info/TamilNadu2026/...
- West Bengal: https://www.myneta.info/WestBengal2026/...
- Assam: https://www.myneta.info/Assam2026/...
- Puducherry: https://www.myneta.info/Puducherry2026/...

## 💡 Tips

1. **First run?** Start with scraping to see if Myneta is accessible
2. **Slow network?** Increase rate limit to 2-5 seconds
3. **Testing?** Run on single state first: `scrape_state('Kerala')`
4. **Debugging?** Check logs: `python src/run_myneta_pipeline.py | tee pipeline.log`

---

**One Command to Rule Them All:**
```bash
python src/run_myneta_pipeline.py
```

Done! ✅
