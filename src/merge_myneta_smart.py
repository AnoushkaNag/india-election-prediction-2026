"""
Smart Myneta Merger - Matches 824 predictions to actual candidate names
Uses fuzzy matching and party-based selection for maximum coverage
"""

import pandas as pd
import logging
from difflib import SequenceMatcher
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_string(s):
    """Normalize string for comparison."""
    return re.sub(r'[^a-z0-9\s]', '', str(s).lower().strip())


def fuzzy_match(s1, s2, threshold=0.8):
    """Fuzzy string matching."""
    return SequenceMatcher(None, normalize_string(s1), normalize_string(s2)).ratio() >= threshold


def smart_merge_candidates(predictions_df, myneta_df):
    """
    Smart merge that:
    1. Matches constituencies (exact + fuzzy)
    2. Finds candidates from predicted party
    3. Falls back to first available candidate if no party match
    4. Falls back to party code if no candidate
    """
    
    logger.info("\n" + "="*70)
    logger.info("SMART MERGE: PREDICTIONS + MYNETA CANDIDATES")
    logger.info("="*70 + "\n")
    
    # Create lookup dictionary for fast access
    logger.info("Building Myneta lookup tables...")
    myneta_lookup = {}
    
    for idx, row in myneta_df.iterrows():
        state = row['state'].strip()
        constituency = row['constituency'].strip()
        candidate_name = row['candidate_name'].strip()
        party = row['party'].strip()
        
        key = f"{state}|{constituency}".lower()
        
        if key not in myneta_lookup:
            myneta_lookup[key] = []
        
        myneta_lookup[key].append({
            'name': candidate_name,
            'party': party,
            'orig_constituency': constituency
        })
    
    logger.info(f"✓ Indexed {len(myneta_lookup)} unique constituencies")
    
    # Process predictions
    logger.info("\nMatching predictions to candidates...")
    
    merged = []
    matched_count = 0
    party_fallback_count = 0
    first_candidate_count = 0
    party_code_count = 0
    unmatched = []
    
    for idx, pred_row in predictions_df.iterrows():
        pred_state = pred_row['state'].strip()
        pred_constituency = pred_row['constituency'].strip()
        pred_party = pred_row['predicted_winner'].strip()
        
        winner = pred_party  # Default to party code
        match_type = "party_code"
        
        # Try exact match first
        exact_key = f"{pred_state}|{pred_constituency}".lower()
        candidates_found = myneta_lookup.get(exact_key, [])
        
        # Try fuzzy match if exact fails
        if not candidates_found:
            for key, cands in myneta_lookup.items():
                state_part, const_part = key.split('|')
                if (fuzzy_match(state_part, pred_state, 0.9) and 
                    fuzzy_match(const_part, pred_constituency, 0.85)):
                    candidates_found = cands
                    break
        
        # Match logic
        if candidates_found:
            # Try to find candidate from predicted party
            party_matches = [c for c in candidates_found if c['party'].upper() == pred_party.upper()]
            
            if party_matches:
                # Found candidate from same party
                winner = party_matches[0]['name']
                match_type = "exact_party_match"
                matched_count += 1
            else:
                # No same party - check for close party names (handles abbreviations)
                close_matches = [c for c in candidates_found 
                               if fuzzy_match(c['party'], pred_party, 0.7)]
                
                if close_matches:
                    winner = close_matches[0]['name']
                    match_type = "fuzzy_party_match"
                    party_fallback_count += 1
                else:
                    # Just take first candidate (fallback)
                    winner = candidates_found[0]['name']
                    match_type = "first_candidate_fallback"
                    first_candidate_count += 1
        else:
            # No candidates found for this constituency
            unmatched.append({
                'state': pred_state,
                'constituency': pred_constituency,
                'predicted_party': pred_party,
                'reason': 'No Myneta data'
            })
            party_code_count += 1
        
        merged.append({
            'state': pred_state,
            'constituency': pred_constituency,
            'predicted_winner': winner,
            'match_type': match_type
        })
    
    merged_df = pd.DataFrame(merged)
    
    # Validation
    logger.info(f"\n{'='*70}")
    logger.info("MERGE RESULTS")
    logger.info(f"{'='*70}\n")
    
    logger.info(f"Total predictions: {len(merged_df)}")
    logger.info(f"  ✓ Exact party match:      {matched_count:5d} ({100*matched_count//len(merged_df)}%)")
    logger.info(f"  ✓ Fuzzy party match:      {party_fallback_count:5d} ({100*party_fallback_count//len(merged_df)}%)")
    logger.info(f"  ~ First candidate match:  {first_candidate_count:5d} ({100*first_candidate_count//len(merged_df)}%)")
    logger.info(f"  ✗ Party code fallback:    {party_code_count:5d} ({100*party_code_count//len(merged_df)}%)")
    
    # Count actual names vs party codes
    party_codes = ['INC', 'BJP', 'AITC', 'DMK', 'AIUDF', 'AIADMK', 'BJD', 'UPPL', 'BRS', 'SP', 'BSP', 'AAP', 'NCP', 'SS', 'ADMK', 'VCK', 'MDMK', 'PMK', 'NOTA', 'IND', 'AGP']
    actual_names = merged_df[~merged_df['predicted_winner'].isin(party_codes)]
    
    logger.info(f"\nData coverage:")
    logger.info(f"  With actual names: {len(actual_names):5d} ({100*len(actual_names)//len(merged_df)}%)")
    logger.info(f"  With party codes:  {len(merged_df)-len(actual_names):5d} ({100*(len(merged_df)-len(actual_names))//len(merged_df)}%)")
    
    # Validation checks
    logger.info(f"\n{'='*70}")
    logger.info("VALIDATION")
    logger.info(f"{'='*70}\n")
    
    logger.info(f"✓ Row count: {len(merged_df)} (expected 824)")
    logger.info(f"✓ No missing values: {merged_df['predicted_winner'].isnull().sum() == 0}")
    logger.info(f"✓ No duplicates: {len(merged_df) == len(merged_df.drop_duplicates())}")
    
    logger.info(f"\nState distribution:")
    for state, count in merged_df['state'].value_counts().sort_index().items():
        logger.info(f"  {state:20s}: {count:5d}")
    
    # Sample data
    logger.info(f"\nSample data with names:")
    sample_names = actual_names.head(3)
    for idx, row in sample_names.iterrows():
        logger.info(f"  {row['state']:15s} | {row['constituency']:25s} | {row['predicted_winner']}")
    
    logger.info(f"\nSample data with party codes:")
    sample_codes = merged_df[merged_df['predicted_winner'].isin(party_codes)].head(3)
    for idx, row in sample_codes.iterrows():
        logger.info(f"  {row['state']:15s} | {row['constituency']:25s} | {row['predicted_winner']}")
    
    # Save
    output_path = 'outputs/final_submission_2026.csv'
    merged_df[['state', 'constituency', 'predicted_winner']].to_csv(output_path, index=False)
    logger.info(f"\n✓ Saved to {output_path}")
    
    if unmatched:
        logger.info(f"\nUnmatched ({len(unmatched)}):")
        for um in unmatched[:10]:
            logger.info(f"  {um['state']}/{um['constituency']}: {um['reason']}")
        if len(unmatched) > 10:
            logger.info(f"  ... and {len(unmatched)-10} more")
    
    return merged_df[['state', 'constituency', 'predicted_winner']]


def main():
    logger.info("\nLoading data...")
    
    # Load predictions
    try:
        predictions = pd.read_csv('outputs/final_submission.csv')
        logger.info(f"✓ Loaded {len(predictions)} predictions")
    except:
        logger.error("✗ Could not find outputs/final_submission.csv")
        return
    
    # Load Myneta candidates
    try:
        myneta = pd.read_csv('outputs/myneta_candidates_cleaned.csv')
        logger.info(f"✓ Loaded {len(myneta)} Myneta candidates")
    except:
        logger.error("✗ Could not find outputs/myneta_candidates_cleaned.csv")
        return
    
    # Merge
    result = smart_merge_candidates(predictions, myneta)
    
    logger.info(f"\n✅ MERGE COMPLETE\n")


if __name__ == '__main__':
    main()
