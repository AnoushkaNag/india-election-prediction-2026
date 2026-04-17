# Preprocessing Robustness Improvements

## Summary

Successfully fixed preprocessing to handle inconsistent Excel formats from Election Commission of India (ECI). All 14 input files now process successfully, including all 5 previously failing 2016 files.

**Results:**
- ✅ **Total rows:** 2,118 constituencies
- ✅ **2016 data:** 822 rows (all 5 target states)
- ✅ **2021 data:** 1,296 rows (9 states including 4 extra)
- ✅ **Data quality:** 0 missing values, all calculations consistent

## Key Changes

### 1. Multi-Header Detection

**Problem:** ECI files have headers at different row indices
- 2021 files: Header at row 3
- 2016 files: Header at row 2 (Kerala, Tamil Nadu, Assam, West Bengal) or row 1 (Puducherry)

**Solution:** Try multiple header values automatically:
```python
headers_to_try = [3, 2, 1, 0]

for header_row in headers_to_try:
    df = pd.read_excel(abs_path, sheet_name=0, header=header_row)
    # Process data...
    if successful:
        break
```

**Implementation in:** `src/preprocess.py`, lines 209-232

### 2. Type-Safe Column Handling

**Problem:** 
- 2021 files have string column names ('AC NAME', 'PARTY')
- 2016 files have numeric column names (1, 2, 3) causing `.strip()` errors
- Text values may be NaN or improperly typed

**Solution:** Added robust type conversions in `extract_top2()`:
```python
# Convert text columns to strings, strip whitespace, handle NaN
df[constituency_col] = df[constituency_col].astype(str).str.strip()
df[party_col] = df[party_col].astype(str).str.strip()

# Remove rows with NaN or 'nan' string values
df = df[df[constituency_col] != 'nan']
df = df[df[party_col] != 'nan']
df = df[df[constituency_col].notna()]
df = df[df[party_col].notna()]
```

**Implementation in:** `src/preprocess.py`, lines 120-130

### 3. Safe Vote Conversion

**Problem:**
- Vote values may be NaN, strings, or floats
- Direct int() conversion could fail
- Need to skip invalid rows gracefully

**Solution:** Enhanced vote handling with multi-stage validation:
```python
# Convert votes column to numeric first
group[votes_col] = pd.to_numeric(group[votes_col], errors='coerce')

# Extract winner and runner votes
winner_votes = pd.to_numeric(winner[votes_col], errors='coerce')
runner_votes = pd.to_numeric(runner[votes_col], errors='coerce')

# Skip if NaN
if pd.isna(winner_votes) or pd.isna(runner_votes):
    logger.debug(f"Invalid vote counts...")
    continue

# Convert to int
winner_votes = int(winner_votes)
runner_votes = int(runner_votes)

# Skip if zero or negative
if winner_votes <= 0 or runner_votes <= 0:
    logger.debug(f"Skipping... Zero or negative votes")
    continue
```

**Implementation in:** `src/preprocess.py`, lines 141-165

### 4. Enhanced Debug Logging

**Added logging for:**
- Detected columns for each file (constituency, party, votes columns)
- First few rows if column detection fails
- Vote conversion issues
- Zero or negative vote counts
- Header row used for successful processing

Example output:
```
2026-04-17 22:50:32,905 - INFO - Kerala: Extracted 140 constituencies
2026-04-17 22:50:32,905 - INFO - ✓ Successfully processed Kerala 2016 (header at row 2)
```

**Updated functions:**
- `detect_columns()`: Added `debug=True` parameter, logs available columns and sample rows
- `extract_top2()`: Added per-row debugging for vote conversions
- `process_all()`: Logs header row used for each successful file

**Implementation in:** `src/preprocess.py`, lines 93-115, 120-180, 209-250

## Processing Flow

```
For each Excel file:
  1. Try header at row 3 (2021 format)
     ├─ If columns detected → Process and extract top 2 candidates → Success
     └─ If columns not detected → Continue to next header
  
  2. Try header at row 2 (2016 format - most states)
     ├─ If columns detected → Process and extract → Success
     └─ If columns not detected → Continue
  
  3. Try header at row 1 (2016 format - Puducherry)
     ├─ If columns detected → Process and extract → Success
     └─ If columns not detected → Continue
  
  4. Try header at row 0 (fallback)
     ├─ If columns detected → Process and extract → Success
     └─ File failed (log error)

For each constituency in a file:
  1. Clean text columns (convert to string, strip, remove NaN)
  2. Convert vote column to numeric (errors='coerce')
  3. Sort by votes descending
  4. Extract top 2 candidates
  5. Validate vote counts (must be > 0 and not NaN)
  6. Calculate metrics (margins, vote share)
  7. Add to results
```

## Test Results

### Files Processed

**Successfully Processed: 14/14**

**2021 Files (9 states + 4 extra):**
- ✓ Kerala 2021: 140 constituencies (header row 3)
- ✓ Tamil Nadu 2021: 234 constituencies (header row 3)
- ✓ Assam 2021: 126 constituencies (header row 3)
- ✓ West Bengal 2021: 293 constituencies (header row 3)
- ✓ Puducherry 2021: 30 constituencies (header row 3)
- ✓ Andhra Pradesh 2021: 175 constituencies (header row 3)
- ✓ Odisha 2021: 147 constituencies (header row 3)
- ✓ Delhi 2021: 70 constituencies (header row 3)
- ✓ Jharkhand 2021: 81 constituencies (header row 3)

**2016 Files (5 target states):**
- ✓ Kerala 2016: 140 constituencies (header row 2) — **FIXED**
- ✓ Tamil Nadu 2016: 232 constituencies (header row 2) — **FIXED**
- ✓ Assam 2016: 126 constituencies (header row 2) — **FIXED**
- ✓ West Bengal 2016: 294 constituencies (header row 2) — **FIXED**
- ✓ Puducherry 2016: 30 constituencies (header row 1) — **FIXED**

### Data Quality Verification

```
✓ Total rows: 2,118 (822 from 2016 + 1,296 from 2021)
✓ Total states: 9
✓ Missing values in vote counts: 0
✓ All votes are positive: True
✓ Vote margin calculations: Consistent
✓ Total vote calculations: Consistent
```

### Vote Statistics

- **Minimum vote share:** 50.01%
- **Maximum vote share:** 93.20%
- **Average vote share:** 57.30%
- **Average votes per constituency:**
  - Kerala: 123,097
  - Tamil Nadu: 159,334
  - Assam: 120,546
  - West Bengal: 168,281
  - Puducherry: 22,412
  - Andhra Pradesh: 182,517
  - Odisha: 143,614
  - Delhi: 123,089
  - Jharkhand: 182,317

## Code Changes

### File: `src/preprocess.py`

**Function 1: `detect_columns()` (lines 86-115)**
- Added `debug=True` parameter
- Logs available columns when detection fails
- Logs first 2 rows if detection fails (for debugging)

**Function 2: `extract_top2()` (lines 118-187)**
- Added safe type conversion for text columns (lines 128-135)
- NaN handling for critical columns (lines 132-135)
- Multi-stage numeric conversion for votes (lines 145-152)
- Validation for positive vote counts (lines 157-160)
- Enhanced error logging at debug level

**Function 3: `process_all()` (lines 209-250)**
- Multi-header retry loop (lines 217-232)
- Try headers [3, 2, 1, 0] in sequence
- Log which header was successful
- Graceful skip to next file if all headers fail

## Backward Compatibility

✅ **No breaking changes:**
- All existing 2021 file processing unchanged (still uses header=3)
- Output structure identical (same columns and order)
- Grouping logic unchanged
- Pipeline orchestration unchanged
- Feature engineering compatible

## Testing

Run verification script:
```bash
python verify_final_dataset.py
```

Re-run full pipeline:
```bash
python src/preprocess.py
```

## Benefits

1. **Robustness:** Automatically handles different ECI file formats
2. **Data Quality:** Prevents invalid data from entering pipeline
3. **Debugging:** Enhanced logging shows exactly what's happening
4. **Completeness:** All 2016 files now processed successfully
5. **Maintainability:** Clear error messages for future troubleshooting
