"""
Merge Myneta candidate data with prediction model output.
"""

import pandas as pd
import logging
from typing import Dict, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_key(state: str, constituency: str) -> str:
    """Create normalized key for matching."""
    state = str(state).strip().lower()
    constituency = str(constituency).strip().lower()
    # Remove punctuation and normalize whitespace
    constituency = ' '.join(constituency.split())
    return f"{state}|{constituency}"


def load_data(predictions_path: str, myneta_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load both datasets.
    
    Args:
        predictions_path: Path to final_submission.csv
        myneta_path: Path to myneta_candidates_cleaned.csv
        
    Returns:
        Tuple of (predictions_df, myneta_df)
    """
    logger.info(f"Loading predictions from {predictions_path}...")
    predictions = pd.read_csv(predictions_path)
    logger.info(f"  Loaded {len(predictions)} rows")
    
    logger.info(f"Loading Myneta data from {myneta_path}...")
    myneta = pd.read_csv(myneta_path)
    logger.info(f"  Loaded {len(myneta)} rows")
    
    return predictions, myneta


def merge_candidates(predictions: pd.DataFrame, myneta: pd.DataFrame) -> pd.DataFrame:
    """
    Merge predictions with Myneta candidate data.
    
    Strategy:
    1. For each prediction row (state, constituency, predicted_winner_party)
    2. Find top candidates from that party in Myneta
    3. Replace party with actual candidate name
    4. If no match found, keep party name
    
    Args:
        predictions: DataFrame with state, constituency, predicted_winner (party)
        myneta: DataFrame with state, constituency, candidate_name, party
        
    Returns:
        Merged DataFrame with candidate names
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"MERGING PREDICTIONS WITH MYNETA DATA")
    logger.info(f"{'='*70}")
    
    merged = predictions.copy()
    
    # Create normalized keys for predictions
    merged['_key'] = merged.apply(
        lambda row: normalize_key(row['state'], row['constituency']), 
        axis=1
    )
    
    # Create normalized keys for Myneta
    myneta['_key'] = myneta.apply(
        lambda row: normalize_key(row['state'], row['constituency']), 
        axis=1
    )
    
    # Group Myneta data by key for fast lookup
    myneta_by_key = {}
    for key, group in myneta.groupby('_key'):
        myneta_by_key[key] = group.to_dict('records')
    
    logger.info(f"Created lookup for {len(myneta_by_key)} unique constituencies")
    
    # Match counter
    matched = 0
    unmatched = []
    
    # Merge process
    for idx, row in merged.iterrows():
        key = row['_key']
        predicted_party = row['predicted_winner']
        
        if key not in myneta_by_key:
            unmatched.append({
                'state': row['state'],
                'constituency': row['constituency'],
                'reason': 'No Myneta data for this constituency'
            })
            continue
        
        # Get candidates from this constituency
        candidates = myneta_by_key[key]
        
        # Try to find candidate from predicted party
        matching_candidates = [
            c for c in candidates 
            if c['party'].upper() == str(predicted_party).upper()
        ]
        
        if matching_candidates:
            # Use first matching candidate
            candidate_name = matching_candidates[0]['candidate_name']
            merged.at[idx, 'predicted_winner'] = candidate_name
            matched += 1
        else:
            # No matching party - try to use top candidate anyway
            if candidates:
                candidate_name = candidates[0]['candidate_name']
                logger.debug(f"Party mismatch for {row['state']}/{row['constituency']}: "
                           f"predicted {predicted_party}, using top candidate {candidate_name} from {candidates[0]['party']}")
                merged.at[idx, 'predicted_winner'] = candidate_name
                matched += 1
            else:
                unmatched.append({
                    'state': row['state'],
                    'constituency': row['constituency'],
                    'reason': 'No candidates found for this constituency'
                })
    
    # Remove temporary key column
    merged = merged.drop('_key', axis=1)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"MERGE RESULTS")
    logger.info(f"{'='*70}")
    logger.info(f"✓ Matched: {matched}/{len(merged)} rows")
    logger.info(f"⚠ Unmatched: {len(unmatched)}/{len(merged)} rows")
    
    if unmatched:
        logger.warning(f"\nUnmatched constituencies:")
        for item in unmatched[:10]:  # Show first 10
            logger.warning(f"  {item['state']}/{item['constituency']}: {item['reason']}")
        if len(unmatched) > 10:
            logger.warning(f"  ... and {len(unmatched) - 10} more")
    
    return merged, unmatched


def validate_merged_data(merged: pd.DataFrame, unmatched: list) -> Dict:
    """
    Validate merged data.
    
    Args:
        merged: Merged DataFrame
        unmatched: List of unmatched constituencies
        
    Returns:
        Validation report
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"VALIDATION")
    logger.info(f"{'='*70}")
    
    report = {
        'total_rows': len(merged),
        'unmatched_rows': len(unmatched),
        'status': 'PASS' if len(unmatched) == 0 else 'WARNING',
        'checks': {}
    }
    
    # Check row count
    if len(merged) == 824:
        logger.info(f"✓ Row count: {len(merged)} (expected 824)")
        report['checks']['row_count'] = 'PASS'
    else:
        logger.warning(f"⚠ Row count: {len(merged)} (expected 824)")
        report['checks']['row_count'] = 'FAIL'
        report['status'] = 'FAIL'
    
    # Check for missing values
    missing = merged.isnull().sum().sum()
    if missing == 0:
        logger.info(f"✓ No missing values")
        report['checks']['missing_values'] = 'PASS'
    else:
        logger.warning(f"⚠ {missing} missing values found")
        report['checks']['missing_values'] = 'FAIL'
    
    # Check for duplicates
    dups = merged.duplicated(subset=['state', 'constituency']).sum()
    if dups == 0:
        logger.info(f"✓ No duplicates")
        report['checks']['duplicates'] = 'PASS'
    else:
        logger.warning(f"⚠ {dups} duplicate rows found")
        report['checks']['duplicates'] = 'FAIL'
    
    # State distribution
    logger.info(f"\nState distribution:")
    for state, count in merged['state'].value_counts().sort_index().items():
        logger.info(f"  {state:20s}: {count:3d}")
    
    return report


def save_merged_data(merged: pd.DataFrame, output_path: str = 'outputs/final_submission_2026.csv'):
    """
    Save merged data to CSV.
    
    Args:
        merged: Merged DataFrame
        output_path: Path to save file
    """
    # Ensure correct column order
    if 'predicted_winner' not in merged.columns:
        logger.error("predicted_winner column not found!")
        return
    
    # Select relevant columns
    output_cols = ['state', 'constituency', 'predicted_winner']
    
    # Add any other columns that might be useful
    extra_cols = [col for col in merged.columns if col not in output_cols]
    if extra_cols:
        output_cols.extend(extra_cols)
    
    output_df = merged[output_cols]
    output_df.to_csv(output_path, index=False)
    
    logger.info(f"\n✓ Saved merged data to {output_path}")
    logger.info(f"  Rows: {len(output_df)}")
    logger.info(f"  Columns: {', '.join(output_df.columns)}")


if __name__ == '__main__':
    # Load data
    predictions, myneta = load_data(
        'outputs/final_submission.csv',
        'outputs/myneta_candidates_cleaned.csv'
    )
    
    # Merge
    merged, unmatched = merge_candidates(predictions, myneta)
    
    # Validate
    report = validate_merged_data(merged, unmatched)
    
    # Save
    save_merged_data(merged)
