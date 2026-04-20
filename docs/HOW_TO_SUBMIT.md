# 🎯 How to Run the Scraper & Submit Your Predictions

## Quick Start (3 steps)

### Step 1: Run the Robust Scraper (Get all candidate names)
```bash
python src/myneta_robust_scraper.py
```

**What it does:**
- Scrapes ALL candidates from Myneta for 5 states
- Handles pagination automatically
- Saves to `outputs/myneta_candidates_cleaned.csv`
- Takes ~20-30 minutes

**Progress:** Check for lines like:
```
✓ Page 1: 100 candidates (Total: 100)
✓ Page 2: 100 candidates (Total: 200)
...
```

### Step 2: Merge candidates with predictions
```bash
python src/merge_myneta.py
```

**What it does:**
- Combines Myneta candidates with your model predictions
- Creates `outputs/final_submission_2026.csv` with candidate names
- Replaces party names with actual names where available

### Step 3: Create Excel submission file
```bash
python src/create_competition_submission.py
```

**What it does:**
- Converts CSV to Excel format
- Creates `India_Predicts_2026_SUBMISSION.xlsx`
- Ready to submit to competition!

---

## Full Process

### Phase 1: Data Collection (30 minutes)

**Run comprehensive scraper:**
```bash
python src/myneta_robust_scraper.py 2>&1 | tee myneta_full_scrape.log
```

This will:
- Connect to Myneta.info
- Go through each state (Kerala, Tamil Nadu, West Bengal, Assam, Puducherry)
- Fetch ALL candidates across all pages/constituencies
- Save raw data to `outputs/myneta_candidates_cleaned.csv`

**Expected output:**
- Kerala: ~860+ candidates
- Tamil Nadu: ~1700+ candidates
- West Bengal: ~2000+ candidates
- Assam: ~650+ candidates
- Puducherry: ~250+ candidates
- **TOTAL: ~5500+ candidates**

### Phase 2: Data Integration (1 minute)

**Merge with your predictions:**
```bash
python src/merge_myneta.py
```

This will:
- Match Myneta candidates to your predicted parties
- Fill in actual candidate names where available
- Keep party names as fallback where no candidates match
- Output: `outputs/final_submission_2026.csv` with 824 rows

**Expected result:**
- 824 rows (all constituencies)
- Column format: state | constituency | predicted_winner
- Value format: actual names (e.g., "Priji Kannan") instead of "INC", "BJP"

### Phase 3: Create Excel Submission (1 minute)

**Convert to competition format:**
```bash
python src/create_competition_submission.py
```

**Output:** `India_Predicts_2026_SUBMISSION.xlsx`
- Ready to submit
- Includes methodology template

---

## What You're Submitting

The competition requires TWO files:

### File 1: Excel Predictions (template provided)
**Location:** `India_Predicts_2026_SUBMISSION.xlsx`

Format:
```
State | Constituency | Predicted Winner
-------|-------------|------------------
Kerala | ADOOR (SC) | Priji Kannan
Kerala | ADOOR (SC) | Panalam Prathapan
...
West Bengal | Bishnupur | Tanmay Ghosh
```

### File 2: Methodology Note (150+ words)
**Create as:** `Methodology.pdf` or `Methodology.docx`

**Include:**
- Data sources used (Myneta, ECI, ADR, etc.)
- Your prediction model/logic
- Data preprocessing steps
- Feature engineering (if any)
- Model assumptions
- Strengths of your approach
- Limitations/weaknesses
- Why you chose certain states/data

**Example template:**
```
METHODOLOGY NOTE
================

Data Sources:
- Myneta.info for candidate information
- Previous election results from ECI
- ... [your other sources]

Approach:
I predicted winners by analyzing candidate voting patterns from Myneta 
and historical election data. My model considers:
1. Candidate background (criminal cases, education, assets)
2. Party strength in each state
3. Local constituency voting patterns
4. Demographic factors

Model Logic:
[Explain your prediction model in 150-300 words]

Strengths:
- Uses official Myneta data
- Incorporates multiple factors
- ...

Limitations:
- Limited historical data for new candidates
- Regional variations not fully captured
- ...
```

---

## Verification Steps

### Before Submission, Check:

1. **Candidate counts:**
```bash
python -c "import pandas as pd; df=pd.read_csv('outputs/final_submission_2026.csv'); print(f'Total: {len(df)}'); print(df['state'].value_counts().sort_index())"
```

Expected:
```
Total: 824
Assam:       126
Kerala:      140
Puducherry:   30
Tamil Nadu:  234
West Bengal: 294
```

2. **Sample data:**
```bash
python -c "import pandas as pd; print(pd.read_csv('outputs/final_submission_2026.csv').head(20))"
```

Check that:
- ✓ All states present
- ✓ Column names correct: state, constituency, predicted_winner
- ✓ Constituency names match official ECI names
- ✓ No party abbreviations (should be candidate names)

3. **File formats:**
- ✓ Excel file: `India_Predicts_2026_SUBMISSION.xlsx`
- ✓ Methodology: `Methodology.pdf` or `.docx` (150+ words)
- ✓ Both files in same folder

---

## Troubleshooting

### Scraper is slow/stuck
- It's normal - Myneta pages load slowly
- Takes 20-30 minutes for all states
- Check `myneta_full_scrape.log` for progress

### Get error "No module named selenium"
```bash
pip install selenium webdriver-manager
```

### Scraper stops mid-way
- Network issue or Myneta timeout
- Run again - it will continue
- You can restart: `python src/myneta_robust_scraper.py`

### Merge creates too many unmatched rows
- This is expected - not all prediction parties match Myneta candidates
- Party predictions are valid fallback
- Competition accepts both candidate names AND party names

### Excel file format wrong
- Make sure it has 3 columns: state, constituency, predicted_winner
- No extra columns, no headers modifications
- Save as .xlsx (not .xls or .csv)

---

## Competition Requirements Checklist

### Registration
- [ ] Filled Google Form: https://forms.gle/2kunspu9A7txkngQ9
- [ ] Confirmed eligibility (citizen, 18+, not employee, not contesting)
- [ ] Provided accurate details (will be verified)

### Submission Files
- [ ] Excel file with 824 predictions
- [ ] Methodology note (150+ words minimum)
- [ ] Both files ready

### Submission Process
1. Log in with registered email
2. Upload Excel file
3. Upload Methodology PDF/Word file
4. Note timestamp (for tiebreaker)
5. Up to 5 submissions allowed - last one counts

### Deadline
- **April 30, 2026 at 11:59 PM**
- Submit EARLY - no extensions!

### Evaluation
- Results benchmarked: May 4, 2026
- Accuracy = % of constituencies predicted correctly
- Prize tiers: 60%+ = Certificate; 75%+ = Eligible for prize
- Prizes: ₹1,00,000 (1st), ₹10,000 (2nd), ₹5,000 (3rd)

---

## Your Setup Summary

```
Project Structure:
├── outputs/
│   ├── myneta_candidates_cleaned.csv ← Scraper output
│   ├── final_submission_2026.csv     ← Merged candidates
│   └── India_Predicts_2026_SUBMISSION.xlsx ← Excel submission
├── src/
│   ├── myneta_robust_scraper.py     ← Run this first
│   ├── merge_myneta.py              ← Run this second
│   └── create_competition_submission.py ← Run this third
└── Methodology.pdf                   ← Create this
```

---

## Complete Command Sequence

```bash
# 1. Get all candidates from Myneta
python src/myneta_robust_scraper.py

# 2. Merge with predictions
python src/merge_myneta.py

# 3. Create Excel file
python src/create_competition_submission.py

# 4. Verify output
python -c "import pandas as pd; df=pd.read_csv('outputs/final_submission_2026.csv'); print(f'{len(df)} predictions ready'); print(df['state'].value_counts())"

# 5. Check Excel file
python -c "import openpyxl; wb=openpyxl.load_workbook('India_Predicts_2026_SUBMISSION.xlsx'); print(f'{wb.active.max_row-1} rows in Excel')"
```

---

## Ready? 🚀

Run Step 1 now:
```bash
python src/myneta_robust_scraper.py
```

Then continue with Steps 2 & 3 when scraper finishes.

Good luck! 🎯
