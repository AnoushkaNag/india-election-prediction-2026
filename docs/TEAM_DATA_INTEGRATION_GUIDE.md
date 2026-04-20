# 🎯 Team Candidate Data Integration Guide

## 📥 Step 1: Your Team Prepares Data

**What they need to do:**
1. Go to Myneta.info for each state
2. Extract all candidate names for each constituency
3. Create Excel/CSV with columns:
   - **Column A:** State (e.g., "Tamil Nadu")
   - **Column B:** Candidate Name (e.g., "Anandhakumar R.")
   - **Column C:** Constituency (e.g., "Chennai Central")
   - **Column D (optional):** Party

**Example format:**
```
State        | Candidate Name              | Constituency
─────────────┼─────────────────────────────┼──────────────────────────
Tamil Nadu   | Anandhakumar R.             | Chennai Central
Tamil Nadu   | Azhagesan V.R.              | Desiya Makkal Sakthi Katchi
Kerala       | Priji Kannan                | ADOOR (SC)
...          | ...                         | ...
```

**Total rows needed:** 824 (one per constituency)

---

## 📤 Step 2: Upload the File

Once your team creates the file, save it as:
- **`Candidate_Names_From_Myneta.xlsx`** (recommended)
- OR `Candidate_Names_From_Myneta.csv`
- OR `candidate_data.xlsx`
- OR `candidate_data.csv`

**Upload location:** Root of your project folder
```
India-Election-Prediction-2026/
├── Candidate_Names_From_Myneta.xlsx ← PUT FILE HERE
├── src/
├── outputs/
└── ...
```

---

## ⚙️ Step 3: Run Integration (1 minute)

Once file is uploaded, run:
```bash
cd c:\Users\KIIT0001\Desktop\India-Election-Prediction-2026
python src/integrate_team_candidates.py
```

**What it does:**
1. ✓ Loads your 824 predictions
2. ✓ Loads team's candidate names
3. ✓ Matches by State + Constituency (exact + fuzzy)
4. ✓ Creates final submission with actual names
5. ✓ Generates `India_Predicts_2026_SUBMISSION.xlsx`

---

## 📊 Expected Output

```
====================================================================
TEAM CANDIDATE DATA INTEGRATION
====================================================================

Loading predictions...
✓ Loaded 824 predictions

Loading team data from: Candidate_Names_From_Myneta.xlsx
✓ Loaded 824 candidates
  Columns: ['State', 'Candidate Name', 'Constituency']

✓ Using file: Candidate_Names_From_Myneta.xlsx

✓ Detected columns:
  State: state
  Candidate: candidate name
  Constituency: constituency

Building candidate lookup...
✓ Indexed 824 candidates

Merging predictions with candidate data...

====================================================================
MERGE RESULTS
====================================================================

Total predictions: 824
  ✓ Matched to candidate names: 824 (100%)
  ✗ Fell back to party codes: 0 (0%)

Data composition:
  With actual names: 824 (100%)
  With party codes:    0 (0%)

====================================================================
VALIDATION
====================================================================

✓ Total rows: 824 (expected 824)
✓ No missing values: True
✓ No duplicates: True

State distribution:
  Assam         : 126
  Kerala        : 140
  Puducherry    :  30
  Tamil Nadu    : 234
  West Bengal   : 294

✓ Saved to outputs/final_submission_2026.csv

Creating Excel submission...
✓ Saved to India_Predicts_2026_SUBMISSION.xlsx

====================================================================
✅ INTEGRATION COMPLETE
====================================================================

Final submission ready: India_Predicts_2026_SUBMISSION.xlsx
```

---

## ✅ Step 4: Verify & Submit

Check your final file:
```bash
python -c "
import pandas as pd
df = pd.read_csv('outputs/final_submission_2026.csv')
print(f'✓ Final submission: {len(df)} rows')
print(f'✓ All actual names: {(~df[\"predicted_winner\"].isin([\"INC\",\"BJP\",\"AITC\"])).sum()}/824')
print(df.head(5))
"
```

Then:
1. ✅ Verify Excel file exists: `India_Predicts_2026_SUBMISSION.xlsx`
2. ✅ Write your 150-word methodology
3. ✅ Submit both files before April 30

---

## 🔧 Troubleshooting

**Error: "No team candidate file found!"**
- Check file is in root project folder
- Verify file name matches one of:
  - `Candidate_Names_From_Myneta.xlsx`
  - `Candidate_Names_From_Myneta.csv`
  - `candidate_data.xlsx`
  - `candidate_data.csv`

**Error: "Could not find required columns!"**
- Ensure columns are exactly: State, Candidate Name, Constituency
- Column names are case-insensitive but must contain those keywords

**Some predictions still show party codes?**
- Team data might be missing those constituencies
- Check: `outputs/final_submission_2026.csv` for which ones
- Have team add those missing rows

---

## 📋 Team Instructions (Copy for your teammates)

Send this to your team:

---

### **TASK: Extract Candidate Names from Myneta**

**Deadline:** ASAP (within 3-5 days ideally)

**What to do:**
1. Go to https://www.myneta.info
2. For each state (Kerala, Tamil Nadu, West Bengal, Assam, Puducherry):
   - Click on state name
   - Go to "Candidates" section
   - Copy all candidate names for all constituencies
3. Create Excel file with columns: State | Candidate Name | Constituency
4. Fill all 824 rows:
   - 140 Kerala constituencies
   - 234 Tamil Nadu constituencies
   - 294 West Bengal constituencies
   - 126 Assam constituencies
   - 30 Puducherry constituencies

**File format:**
```
State        | Candidate Name         | Constituency
─────────────┼────────────────────────┼──────────────
Kerala       | Priji Kannan           | ADOOR (SC)
Kerala       | P.P.Chitharanjan       | ALAPPUZHA
Tamil Nadu   | Anandhakumar R.        | Chennai Central
```

**Save as:** `Candidate_Names_From_Myneta.xlsx`

**Upload to:** Project root folder

---

## 💡 Why This Approach Works

✅ **Reliable:** Manual curation > web scraping
✅ **Complete:** Get all 824 actual names
✅ **Fast:** Team can parallelize data collection
✅ **Accurate:** Names verified directly from Myneta
✅ **Efficient:** 10 days is plenty of time

---

## 📅 Timeline

- **Day 1-2:** Team collects data
- **Day 3:** Data uploaded
- **Day 4:** Run integration (1 min)
- **Day 5-9:** Write methodology, verify
- **Day 10 (Apr 30):** SUBMIT! ✅

---

## 🎯 Final Result

```
✓ 824 predictions with actual candidate names
✓ 100% data coverage
✓ Excel submission ready
✓ Competitive for competition 🏆
```

**Once team uploads, just run:**
```bash
python src/integrate_team_candidates.py
```

**Done!** 🚀
