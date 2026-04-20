"""
Comprehensive Audit and Validation Script
Election Prediction Project - Submission Readiness Check
"""

import pandas as pd
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

CANDIDATE_FILE = 'data/raw/Candidate Name List with const.xlsx'
PREDICTION_FILE = 'outputs/final_submission.csv'
OUTPUT_FILE = 'outputs/final_submission_FINAL.csv'

# Expected constituency counts per state
EXPECTED_CONSTITUENCIES = {
    'Kerala': 140,
    'Tamil Nadu': 234,
    'West Bengal': 294,
    'Assam': 126,
    'Puducherry': 30
}

TOTAL_EXPECTED_ROWS = 824


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title):
    """Print formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_result(label, value, status=None):
    """Print labeled result with optional status."""
    if status == 'PASS':
        print(f"  ✓ {label}: {value}")
    elif status == 'FAIL':
        print(f"  ✗ {label}: {value}")
    else:
        print(f"  • {label}: {value}")


def normalize_string(s):
    """Normalize string: lowercase, strip whitespace."""
    if pd.isna(s):
        return None
    return str(s).lower().strip()


def get_column_by_name(df, keyword):
    """Find column name by keyword (case-insensitive)."""
    keyword_lower = keyword.lower()
    for col in df.columns:
        if keyword_lower in col.lower():
            return col
    return None


def create_key(state, constituency):
    """Create unique key from state and constituency."""
    return f"{normalize_string(state)}|{normalize_string(constituency)}"


# ============================================================================
# TASK 1: LOAD DATA
# ============================================================================

def load_data():
    """Load candidate and prediction data."""
    print_header("TASK 1: LOADING DATA")
    
    try:
        print("Loading candidate data from:", CANDIDATE_FILE)
        candidate_df = pd.read_excel(CANDIDATE_FILE)
        print_result("✓ Candidate file loaded", f"{len(candidate_df)} rows")
        
    except FileNotFoundError:
        print(f"  ✗ ERROR: Candidate file not found: {CANDIDATE_FILE}")
        return None, None
    except Exception as e:
        print(f"  ✗ ERROR loading candidate file: {e}")
        return None, None
    
    try:
        print("Loading prediction data from:", PREDICTION_FILE)
        pred_df = pd.read_csv(PREDICTION_FILE)
        print_result("✓ Prediction file loaded", f"{len(pred_df)} rows")
        
    except FileNotFoundError:
        print(f"  ✗ ERROR: Prediction file not found: {PREDICTION_FILE}")
        return None, None
    except Exception as e:
        print(f"  ✗ ERROR loading prediction file: {e}")
        return None, None
    
    return candidate_df, pred_df


# ============================================================================
# TASK 2: BASIC DATA AUDIT (CANDIDATE FILE)
# ============================================================================

def audit_candidate_data(candidate_df):
    """Audit candidate dataset for basic issues."""
    print_header("TASK 2: BASIC DATA AUDIT - CANDIDATE FILE")
    
    # Total rows
    print_result("Total rows", len(candidate_df))
    
    # Column names
    print_result("Column names", list(candidate_df.columns))
    
    required_cols = ['state', 'constituency', 'candidate', 'party']
    found_cols = [get_column_by_name(candidate_df, col) for col in required_cols]
    has_required = all(col is not None for col in found_cols)
    print_result("Has required columns", "YES" if has_required else "NO", 
                 status='PASS' if has_required else 'FAIL')
    
    # Only check core columns (not the extra unnamed ones)
    core_cols = [col for col in candidate_df.columns if not col.startswith('Unnamed')]
    
    # Missing values
    print("\n  Missing values per column:")
    missing = candidate_df[core_cols].isnull().sum()
    for col, count in missing.items():
        if count > 0:
            print(f"    - {col}: {count} ({100*count/len(candidate_df):.1f}%)")
    if missing.sum() == 0:
        print(f"    ✓ No missing values")
    
    # Empty strings
    print("\n  Empty strings per column:")
    empty_count = 0
    for col in core_cols:
        empty = (candidate_df[col].astype(str).str.strip() == '').sum()
        if empty > 0:
            print(f"    - {col}: {empty}")
            empty_count += empty
    if empty_count == 0:
        print(f"    ✓ No empty strings")
    
    # Duplicate rows (check on core columns only)
    dup_count = candidate_df[core_cols].duplicated().sum()
    print_result("Duplicate rows (full)", dup_count, 
                 status='PASS' if dup_count == 0 else 'FAIL')
    
    return has_required, found_cols


# ============================================================================
# TASK 3: STATE-WISE VALIDATION
# ============================================================================

def validate_states(candidate_df):
    """Validate state and constituency counts."""
    print_header("TASK 3: STATE-WISE VALIDATION")
    
    # Get column names
    state_col = get_column_by_name(candidate_df, 'state')
    const_col = get_column_by_name(candidate_df, 'constituency')
    
    if not (state_col and const_col):
        print("  ✗ ERROR: Could not find state or constituency columns")
        return False
    
    # Get unique constituency counts per state
    actual_counts = candidate_df.groupby(state_col)[const_col].nunique().to_dict()
    
    all_pass = True
    print("Expected vs Actual constituencies:\n")
    
    for state in sorted(EXPECTED_CONSTITUENCIES.keys()):
        expected = EXPECTED_CONSTITUENCIES[state]
        actual = actual_counts.get(state, 0)
        match = expected == actual
        status = 'PASS' if match else 'FAIL'
        
        symbol = '✓' if match else '✗'
        print(f"  {symbol} {state:20s}: Expected {expected:3d}, Actual {actual:3d}", end='')
        
        if not match:
            all_pass = False
            diff = actual - expected
            print(f" (Diff: {diff:+d})")
        else:
            print()
    
    # Check for unexpected states
    unexpected = set(actual_counts.keys()) - set(EXPECTED_CONSTITUENCIES.keys())
    if unexpected:
        print(f"\n  ⚠ Unexpected states found: {unexpected}")
        all_pass = False
    
    # Summary
    print_result("\nAll states match expected count", "YES" if all_pass else "NO", 
                 status='PASS' if all_pass else 'FAIL')
    
    return all_pass


# ============================================================================
# TASK 4: DATA CLEANING CHECK
# ============================================================================

def check_data_quality(candidate_df):
    """Check for duplicates after normalization."""
    print_header("TASK 4: DATA CLEANING CHECK")
    
    # Get column names
    state_col = get_column_by_name(candidate_df, 'state')
    const_col = get_column_by_name(candidate_df, 'constituency')
    cand_col = get_column_by_name(candidate_df, 'candidate')
    party_col = get_column_by_name(candidate_df, 'party')
    
    # Create normalized copy (only core columns)
    df_norm = candidate_df[[state_col, const_col, cand_col, party_col]].copy()
    df_norm['state_norm'] = df_norm[state_col].apply(normalize_string)
    df_norm['constituency_norm'] = df_norm[const_col].apply(normalize_string)
    df_norm['candidate_norm'] = df_norm[cand_col].apply(normalize_string)
    df_norm['party_norm'] = df_norm[party_col].apply(normalize_string)
    
    # Check duplicates: (state, constituency, candidate)
    dup_full = df_norm.duplicated(subset=['state_norm', 'constituency_norm', 'candidate_norm']).sum()
    print_result("Duplicate (state, constituency, candidate)", dup_full,
                 status='PASS' if dup_full == 0 else 'FAIL')
    
    # Check duplicates: (state, constituency, party)
    dup_party = df_norm.duplicated(subset=['state_norm', 'constituency_norm', 'party_norm']).sum()
    print_result("Duplicate (state, constituency, party)", dup_party,
                 status='PASS' if dup_party == 0 else 'FAIL')
    
    # Check duplicates: (state, constituency) only
    dup_key = df_norm.duplicated(subset=['state_norm', 'constituency_norm']).sum()
    print_result("Multiple candidates per constituency", dup_key,
                 status='INFO')
    
    return df_norm


# ============================================================================
# TASK 5: MERGE VALIDATION
# ============================================================================

def validate_merge(candidate_df, pred_df, df_norm):
    """Validate merge between candidate and prediction data."""
    print_header("TASK 5: MERGE VALIDATION")
    
    # Get column names from original files
    state_col_c = get_column_by_name(candidate_df, 'state')
    const_col_c = get_column_by_name(candidate_df, 'constituency')
    state_col_p = get_column_by_name(pred_df, 'state')
    const_col_p = get_column_by_name(pred_df, 'constituency')
    
    # Create merge keys
    df_norm['merge_key'] = df_norm.apply(
        lambda row: create_key(row[state_col_c], row[const_col_c]), axis=1
    )
    
    pred_df_copy = pred_df.copy()
    pred_df_copy['merge_key'] = pred_df_copy.apply(
        lambda row: create_key(row[state_col_p], row[const_col_p]), axis=1
    )
    
    # Attempt merge
    merged = pd.merge(
        pred_df_copy,
        df_norm[['merge_key', 'candidate_norm', 'party_norm']],
        on='merge_key',
        how='left'
    )
    
    print_result("Prediction rows", len(pred_df_copy))
    print_result("Candidate rows", len(df_norm))
    print_result("Merged rows", len(merged))
    
    # Check match rate
    matched = merged['candidate_norm'].notna().sum()
    unmatched = merged['candidate_norm'].isna().sum()
    match_rate = 100 * matched / len(merged)
    
    print_result("Successfully matched", matched, status='PASS' if matched > 0 else 'FAIL')
    print_result("Unmatched constituencies", unmatched)
    print_result("Match rate", f"{match_rate:.1f}%")
    
    if unmatched > 0:
        print("\n  Unmatched constituencies (first 15):")
        unmatched_rows = merged[merged['candidate_norm'].isna()]
        for idx, row in unmatched_rows.head(15).iterrows():
            print(f"    - {row.get(state_col_p, 'N/A')} / {row.get(const_col_p, 'N/A')}")
        if len(unmatched_rows) > 15:
            print(f"    ... and {len(unmatched_rows) - 15} more")
    
    return merged, matched, unmatched


# ============================================================================
# TASK 6: FINAL MAPPING CHECK
# ============================================================================

def check_final_mapping(merged, pred_df):
    """Simulate final selection logic."""
    print_header("TASK 6: FINAL MAPPING CHECK")
    
    # Get prediction column
    winner_col = get_column_by_name(pred_df, 'predicted')
    if not winner_col:
        winner_col = get_column_by_name(pred_df, 'winner')
    if not winner_col:
        winner_col = pred_df.columns[2]
    
    # Simulate selection
    has_real_candidate = merged['candidate_norm'].notna()
    
    fallback_used = (~has_real_candidate).sum()
    real_used = has_real_candidate.sum()
    
    print_result("Real candidates used", real_used, status='PASS' if real_used > 0 else 'FAIL')
    print_result("Fallback to predictions", fallback_used)
    print_result("Fallback percentage", f"{100*fallback_used/len(merged):.1f}%")
    
    return real_used, fallback_used


# ============================================================================
# TASK 7: FINAL OUTPUT VALIDATION
# ============================================================================

def validate_final_output(merged):
    """Validate final output dataset."""
    print_header("TASK 7: FINAL OUTPUT VALIDATION")
    
    # Expected total rows
    row_check = len(merged) == TOTAL_EXPECTED_ROWS
    print_result("Total rows = 824", len(merged), 
                 status='PASS' if row_check else 'FAIL')
    
    # Get column names
    state_col = get_column_by_name(merged, 'state')
    const_col = get_column_by_name(merged, 'constituency')
    
    # No duplicate (state, constituency)
    dup_key = merged.duplicated(subset=[state_col, const_col]).sum()
    print_result("No duplicate (state, constituency)", dup_key, 
                 status='PASS' if dup_key == 0 else 'FAIL')
    
    # No missing values in key columns
    missing = merged[[state_col, const_col]].isnull().sum().sum()
    print_result("No missing state or constituency", missing,
                 status='PASS' if missing == 0 else 'FAIL')
    
    # All 5 states present
    unique_states = merged[state_col].nunique()
    print_result("All 5 states present", unique_states,
                 status='PASS' if unique_states == 5 else 'FAIL')
    
    all_valid = row_check and dup_key == 0 and missing == 0 and unique_states == 5
    
    return all_valid


# ============================================================================
# TASK 8: REPORT SUMMARY
# ============================================================================

def print_summary_report(candidate_df, pred_df, merged, match_count, unmatched_count,
                         real_used, fallback_used, all_valid):
    """Print comprehensive summary report."""
    print_header("TASK 8: FINAL SUBMISSION READINESS REPORT")
    
    # Get core columns only
    core_cols = [col for col in candidate_df.columns if not col.startswith('Unnamed')]
    
    print("DATA VOLUME:")
    print_result("  Candidate records", len(candidate_df))
    print_result("  Prediction records", len(pred_df))
    print_result("  Final merged records", len(merged))
    
    print("\nDATA QUALITY:")
    missing_total = candidate_df[core_cols].isnull().sum().sum()
    dup_total = candidate_df[core_cols].duplicated().sum()
    print_result("  Missing values", missing_total, status='PASS' if missing_total == 0 else 'FAIL')
    print_result("  Duplicate rows", dup_total, status='PASS' if dup_total == 0 else 'FAIL')
    
    print("\nMERGE RESULTS:")
    match_rate = 100 * match_count / len(merged)
    print_result("  Successfully matched", match_count, status='PASS' if match_count > 0 else 'FAIL')
    print_result("  Unmatched", unmatched_count)
    print_result("  Match rate", f"{match_rate:.1f}%", 
                 status='PASS' if match_rate >= 75 else 'FAIL')
    
    print("\nMAP SELECTION:")
    print_result("  Real candidates used", real_used)
    print_result("  Fallback predictions", fallback_used)
    
    print("\nFINAL VERDICT:")
    if all_valid:
        print(f"\n  ✅ READY FOR SUBMISSION")
        print(f"\n  All validation checks passed. The dataset is ready for final submission.")
    else:
        print(f"\n  ⚠️  NEEDS FIXES")
        print(f"\n  Some validation checks failed. Please review the issues above.")
    
    print(f"\n{'='*80}\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete audit."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  ELECTION PREDICTION PROJECT - SUBMISSION READINESS AUDIT".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Task 1: Load
    candidate_df, pred_df = load_data()
    if candidate_df is None or pred_df is None:
        print("\n  ✗ FAILED: Could not load required files")
        sys.exit(1)
    
    # Task 2: Basic audit
    has_required, found_cols = audit_candidate_data(candidate_df)
    if not has_required:
        print("\n  ✗ FAILED: Missing required columns")
        sys.exit(1)
    
    # Task 3: State validation
    states_valid = validate_states(candidate_df)
    
    # Task 4: Data quality
    df_norm = check_data_quality(candidate_df)
    
    # Task 5: Merge validation
    merged, matched, unmatched = validate_merge(candidate_df, pred_df, df_norm)
    
    # Task 6: Final mapping
    real_used, fallback_used = check_final_mapping(merged, pred_df)
    
    # Task 7: Final output
    all_valid = validate_final_output(merged)
    
    # Task 8: Summary
    print_summary_report(candidate_df, pred_df, merged, matched, unmatched,
                        real_used, fallback_used, all_valid)
    
    # Exit code
    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()
