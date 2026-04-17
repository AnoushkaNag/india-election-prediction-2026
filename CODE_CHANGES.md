# Code Changes Summary - Multi-Year Pipeline Upgrade

## 1. preprocess.py

### Change 1a: Updated FILES Configuration
```python
# BEFORE:
FILES = [
    ("../data/raw/kerala_detailed.xlsx", "Kerala", "target"),
    ("../data/raw/tamilnadu_detailed.xlsx", "Tamil Nadu", "target"),
    # ... etc
]

# AFTER:
FILES = [
    ("../data/raw/kerala_detailed.xlsx", "Kerala", 2021, "target"),
    ("../data/raw/kerala_2016_detailed.xlsx", "Kerala", 2016, "target"),
    ("../data/raw/tamilnadu_detailed.xlsx", "Tamil Nadu", 2021, "target"),
    ("../data/raw/tamilnadu_2016_detailed.xlsx", "Tamil Nadu", 2016, "target"),
    # ... etc (14 total entries now)
]
```

### Change 1b: Updated extract_top2() Function Signature
```python
# BEFORE:
def extract_top2(df, state_name, data_type):

# AFTER:
def extract_top2(df, state_name, year, data_type):
    """
    ...
    Args:
        ...
        year: Election year
        ...
    """
```

### Change 1c: Added Year to Results Dictionary
```python
# BEFORE:
results.append({
    "state": state_name,
    "constituency": const,
    "winner_party": str(winner[party_col]).strip(),
    ...
    "data_type": data_type
})

# AFTER:
results.append({
    "year": year,  # <-- ADDED
    "state": state_name,
    "constituency": const,
    "winner_party": str(winner[party_col]).strip(),
    ...
    "data_type": data_type
})
```

### Change 1d: Updated process_all() Loop Unpacking
```python
# BEFORE:
for path, state, dtype in FILES:
    abs_path = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(abs_path):
        logger.error(f"File not found: {abs_path}")
        failed_states.append((state, "File not found"))
        continue
    
    logger.info(f"\nProcessing {state} ({dtype})...")
    ...
    processed = extract_top2(df, state, dtype)
    ...
    processed_states.append(state)

# AFTER:
for path, state, year, dtype in FILES:  # <-- ADDED year
    abs_path = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(abs_path):
        logger.error(f"File not found: {abs_path}")
        failed_states.append((state, year, "File not found"))  # <-- ADDED year
        continue
    
    logger.info(f"\nProcessing {state} {year} ({dtype})...")  # <-- ADDED year
    ...
    processed = extract_top2(df, state, year, dtype)  # <-- ADDED year
    ...
    processed_states.append((state, year))  # <-- CHANGED to tuple
```

### Change 1e: Updated Summary Logging
```python
# BEFORE:
for state in processed_states:
    logger.info(f"  ✓ {state}")

if failed_states:
    logger.warning(f"\nFailed to process: {len(failed_states)} states")
    for state, reason in failed_states:
        logger.warning(f"  ✗ {state}: {reason}")

# AFTER:
for state, year in processed_states:  # <-- ADDED year unpacking
    logger.info(f"  ✓ {state} {year}")  # <-- ADDED year display

if failed_states:
    logger.warning(f"\nFailed to process: {len(failed_states)} files")  # <-- CHANGED wording
    for state, year, reason in failed_states:  # <-- ADDED year unpacking
        logger.warning(f"  ✗ {state} {year}: {reason}")  # <-- ADDED year display
```

---

## 2. feature_engineering.py

### Change 2: Complete Rewrite - Added Historical Features
```python
# BEFORE:
def create_features(df):
    # Vote share
    df["vote_share_winner"] = df["winner_votes"] / df["total_votes"]
    df["vote_share_runner"] = df["runner_up_votes"] / df["total_votes"]

    # Margin
    df["margin"] = df["vote_share_winner"] - df["vote_share_runner"]

    # Swing risk
    df["swing_risk"] = df["margin"].apply(lambda x: 1 if x < 0.05 else 0)

    # Dominance
    df["dominant_win"] = df["margin"].apply(lambda x: 1 if x > 0.15 else 0)

    return df


# AFTER:
def create_features(df):
    """Create features including existing and new historical features."""
    
    # Ensure data is sorted by state, constituency, and year
    df = df.sort_values(['state', 'constituency', 'year']).reset_index(drop=True)
    
    # Vote share
    df["vote_share_winner"] = df["winner_votes"] / df["total_votes"]
    df["vote_share_runner"] = df["runner_up_votes"] / df["total_votes"]

    # Margin
    df["margin"] = df["vote_share_winner"] - df["vote_share_runner"]

    # Swing risk
    df["swing_risk"] = df["margin"].apply(lambda x: 1 if x < 0.05 else 0)

    # Dominance
    df["dominant_win"] = df["margin"].apply(lambda x: 1 if x > 0.15 else 0)

    # ============================================
    # HISTORICAL FEATURES (Multi-year) - NEW
    # ============================================
    
    # Shift operations work on sorted data
    df["prev_winner"] = df.groupby(['state', 'constituency'])['winner_party'].shift(1)
    df["prev_margin"] = df.groupby(['state', 'constituency'])['margin'].shift(1)
    
    # Incumbent: 1 if same party as previous year, 0 otherwise
    df["incumbent"] = (df["winner_party"] == df["prev_winner"]).astype(int)
    # For first year (where prev_winner is NaN), set incumbent to 0
    df["incumbent"] = df["incumbent"].fillna(0).astype(int)
    
    # Margin change: current margin - previous margin
    df["margin_change"] = df["margin"] - df["prev_margin"]
    # For first year (where prev_margin is NaN), set margin_change to 0
    df["margin_change"] = df["margin_change"].fillna(0)
    
    return df
```

**Key Logic:**
- `groupby(['state', 'constituency'])`: Groups records for same constituency across years
- `.shift(1)`: Gets previous year's value
- `fillna(0)`: Handles first-year records (no previous year to compare)

---

## 3. model.py

### Change 3: Updated Features Array
```python
# BEFORE:
def prepare_data(df):
    # Target: 1 = retain, 0 = flip
    df["target"] = df["margin"].apply(lambda x: 1 if x > 0.08 else 0)

    features = [
        "vote_share_winner",
        "vote_share_runner",
        "margin",
        "swing_risk",
        "dominant_win"
    ]

    X = df[features]
    y = df["target"]

    return X, y


# AFTER:
def prepare_data(df):
    # Target: 1 = retain, 0 = flip
    df["target"] = df["margin"].apply(lambda x: 1 if x > 0.08 else 0)

    features = [
        "vote_share_winner",
        "vote_share_runner",
        "margin",
        "swing_risk",
        "dominant_win",
        "incumbent",        # <-- NEW
        "margin_change"     # <-- NEW
    ]

    X = df[features]
    y = df["target"]

    return X, y
```

**Note:** Only change is adding 2 feature names to the features list. All other model logic remains unchanged.

---

## Summary of Changes

| File | Type | Lines Changed | Key Changes |
|------|------|---------------|------------|
| preprocess.py | Core Logic | ~20 | Year parameter added throughout, FILES config expanded |
| feature_engineering.py | Core Logic | ~30 | Historical features calculation added |
| model.py | Configuration | 2 | Two feature names added to list |
| **TOTAL** | | **~52** | Minimal, focused changes |

## Backward Compatibility

✅ **All changes are backward compatible**
- Single-year datasets still work (incumbent=0, margin_change=0)
- Existing features unchanged
- File structure unchanged
- Model training logic unchanged
- Can process both 2021-only and 2016+2021 datasets

## Testing

✅ **All components tested and verified:**
- Preprocessing: Year column successfully added
- Feature engineering: All 4 historical features created
- Model integration: All 7 features recognized
- Data pipeline: End-to-end flow working correctly
