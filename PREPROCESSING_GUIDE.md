# Indian Election Data Preprocessing Pipeline

## Overview

This document describes the preprocessing pipeline that transforms raw ECI (Election Commission of India) election results into a clean, analysis-ready dataset.

## Input Data

**Source**: ECI Detailed Results Excel Files
- Located in: `data/raw/` directory
- 9 states covered:
  - **Target States** (5): Kerala, Tamil Nadu, Assam, West Bengal, Puducherry
  - **Extra States** (4): Andhra Pradesh, Odisha, Delhi, Jharkhand

**File Format**: 
- Excel (.xlsx) files with ECI-standard structure
- Headers located at row 3 (0-indexed)
- Contains: Constituency, Candidate Name, Party, Vote Counts, etc.

## Processing Steps

### 1. **Column Detection & Normalization**
- Standardizes column names (lowercase, spaces→underscores)
- Flexibly detects columns using keyword matching:
  - Constituency: `AC_NAME`, `AC_NO`, `CONSTITUENCY`
  - Party: `PARTY`, `POLITICAL_PARTY`
  - Votes: `TOTAL`, `VOTES`
- Gracefully handles missing columns with detailed logging

### 2. **Top 2 Candidates Extraction**
For each constituency:
- Groups candidates by constituency name
- Sorts candidates by vote count (descending)
- Extracts the top 2 candidates (winner and runner-up)
- Skips constituencies with fewer than 2 candidates

### 3. **Vote Count Processing**
- Converts vote counts to integers with error handling
- Calculates derived metrics:
  - **Vote Margin**: Difference between winner and runner-up votes
  - **Total Votes**: Sum of top 2 candidates' votes
  - **Vote Share %**: Percentage of votes for each candidate

### 4. **Data Validation**
- Removes rows with invalid vote counts
- Logs warnings for data quality issues
- Provides detailed error reporting by state

### 5. **Output Generation**
Generates two output formats:
- **CSV**: Single file with all data (`final_dataset.csv`)
- **Excel**: Multi-sheet workbook (`final_dataset.xlsx`)
  - Sheet 1: All Data
  - Sheet 2: Target States Only
  - Sheet 3: Extra States Only

## Output Schema

### Dataset: `final_dataset.csv`

| Column | Type | Description |
|--------|------|-------------|
| `state` | string | State/UT name |
| `constituency` | string | Constituency/AC name |
| `winner_party` | string | Party of the candidate with most votes |
| `runner_up_party` | string | Party of the 2nd candidate |
| `winner_votes` | integer | Votes received by top candidate |
| `runner_up_votes` | integer | Votes received by 2nd candidate |
| `vote_margin` | integer | Difference in votes (winner - runner-up) |
| `total_votes` | integer | Combined votes of top 2 candidates |
| `vote_share_winner` | float | Winner's vote share percentage |
| `vote_share_runner` | float | Runner-up's vote share percentage |
| `data_type` | string | 'target' or 'extra' |

## Dataset Statistics

**Total Records**: 1,296 constituencies
- Target States: 823 constituencies (63.5%)
- Extra States: 473 constituencies (36.5%)

**Vote Share Distribution**:
- Minimum: 50.01% (competitive races)
- Maximum: 93.20% (dominant performances)
- Mean: 57.65%

**Average Total Votes by State**:
- Andhra Pradesh: 182,517
- Assam: 134,120
- Delhi: 123,089
- Jharkhand: 182,317
- Kerala: 126,877
- Odisha: 143,614
- Puducherry: 23,904
- Tamil Nadu: 168,263
- West Bengal: 179,010

## Usage

### Run the Full Pipeline

```bash
cd src
python preprocess.py
```

### Expected Output

The script will:
1. Load all Excel files from `data/raw/`
2. Process each state with detailed logging
3. Generate CSV and Excel files in `data/processed/`
4. Display dataset statistics
5. Provide processing summary

### Example Output

```
Processing Kerala (target)...
  Loaded 1241 rows from Excel
  Detected columns - constituency: ac_name, party: party, votes: total
  Extracted 140 constituencies
  ✓ Successfully processed Kerala

...

Final dataset: 1296 rows across 9 states
✓ Saved CSV: data/processed/final_dataset.csv
✓ Saved Excel: data/processed/final_dataset.xlsx
```

## Error Handling

The pipeline includes robust error handling:

1. **Missing Files**: Logs and skips missing Excel files
2. **Missing Columns**: Gracefully handles varying column names with fallback matching
3. **Invalid Data**: Removes rows with non-numeric vote counts
4. **Edge Cases**: Skips constituencies with fewer than 2 candidates
5. **Data Type Conversion**: Safely converts vote counts with error recovery

### Logging

All operations are logged with severity levels:
- **INFO**: Successful operations, state processing
- **WARNING**: Skipped records, data quality issues
- **ERROR**: Fatal errors that prevent processing

## Features

✅ **Flexible Column Detection**: Works with various ECI file formats
✅ **Missing Data Handling**: Gracefully handles incomplete data
✅ **Data Validation**: Removes invalid entries automatically
✅ **Comprehensive Logging**: Detailed processing information
✅ **Multi-Format Output**: Both CSV and Excel formats
✅ **Statistics Generation**: Automatic summary calculations
✅ **Error Recovery**: Continues processing even when individual records fail

## Customization

### Modify Input Files

Edit the `FILES` configuration in `src/preprocess.py`:

```python
FILES = [
    ("../data/raw/state_detailed.xlsx", "State Name", "target"),
    # Add more states here
]
```

### Adjust Column Detection

Modify keyword lists in `detect_columns()`:

```python
constituency_keywords = ['ac_name', 'your_keyword', ...]
party_keywords = ['party', 'your_keyword', ...]
votes_keywords = ['total', 'your_keyword', ...]
```

### Change Output Location

Modify in `process_all()`:

```python
output_dir = os.path.join(os.path.dirname(__file__), "../your/custom/path")
```

## Troubleshooting

### Issue: "No data processed! Pipeline halted."

**Causes**:
- Excel files not found in `data/raw/`
- Column names don't match expected keywords

**Solution**:
1. Verify Excel files exist in `data/raw/`
2. Check the log output for which columns were detected
3. Adjust keyword lists in `detect_columns()` if needed

### Issue: Low constituency count for a state

**Possible causes**:
- Some constituencies have only 1 candidate
- Data quality issues in source file

**Check**: Review logs for state-specific warnings

### Issue: Columns not being detected

**Solution**:
1. Inspect the Excel file directly
2. Identify actual column names
3. Add keywords to the detection lists

## Dependencies

- `pandas`: Data manipulation
- `openpyxl`: Excel file reading/writing

Install with:
```bash
pip install -r requirements.txt
```

## Future Enhancements

Potential improvements for the pipeline:
- [ ] Add candidate name extraction
- [ ] Include candidate demographics (age, gender, category)
- [ ] Add historical election comparison
- [ ] Implement data quality scoring
- [ ] Add data visualization reports
- [ ] Support for additional states
- [ ] Incremental processing for large datasets
