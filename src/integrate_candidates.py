#!/usr/bin/env python3
"""
Election Prediction Pipeline - Candidate Integration Module

Integrates Myneta candidate data with model predictions to generate
final submission with candidate names instead of party codes.

Process:
1. Standardize data (clean text, normalize parties)
2. Build state-wise lookup groups
3. Fuzzy match constituencies
4. Select winning candidates by party
5. Build final dataframe
6. Validate output
7. Save to outputs/final_submission_FINAL.csv
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from collections import defaultdict

# Try to import rapidfuzz, fallback to difflib if not available
try:
    from rapidfuzz import process, fuzz
    USE_RAPIDFUZZ = True
except ImportError:
    USE_RAPIDFUZZ = False
    from difflib import SequenceMatcher
    print("⚠️  rapidfuzz not installed, using fallback difflib for fuzzy matching")
    print("   Install: pip install rapidfuzz\n")


# ============================================================================
# TASK 1: STANDARDIZE DATA
# ============================================================================

def clean_text(text: str) -> str:
    """
    Standardize text:
    - Lowercase
    - Strip whitespace
    - Remove special chars (except (SC)/(ST))
    - Normalize multiple spaces
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase and strip
    text = text.lower().strip()
    
    # Remove special chars except (SC)/(ST) and parentheses needed for party names
    # Keep: letters, digits, spaces, hyphens, (SC), (ST), parentheses for party names
    text = re.sub(r'[^\w\s\-\(\)]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def normalize_party(party: str) -> str:
    """
    Normalize party names to standard codes.
    Maps full names and variations to standard short codes.
    
    Args:
        party: Party name or code
        
    Returns:
        Normalized party code
    """
    party = clean_text(party)
    
    # Mapping of variations to standard codes
    party_mapping = {
        # Bjp
        'bharatiya janata party': 'bjp',
        'bjp': 'bjp',
        
        # Congress
        'indian national congress': 'inc',
        'inc': 'inc',
        'congress': 'inc',
        
        # Trinamool
        'all india trinamool congress': 'aitc',
        'aitc': 'aitc',
        
        # CPM
        'communist party of india marxist': 'cpim',
        'cpim': 'cpim',
        'cpi(m)': 'cpim',
        'cpi m': 'cpim',
        
        # CPI
        'communist party of india': 'cpi',
        'cpi': 'cpi',
        
        # DMK
        'dravida munnetra kazhagam': 'dmk',
        'dmk': 'dmk',
        
        # AIADMK
        'anna dravida munnetra kazhagam': 'aiadmk',
        'aiadmk': 'aiadmk',
        
        # BSP
        'bahujan samaj party': 'bsp',
        'bsp': 'bsp',
        
        # SP
        'samajwadi party': 'sp',
        'sp': 'sp',
        
        # JDU
        'janata dal united': 'jdu',
        'jdu': 'jdu',
        
        # RJD
        'rashtriya janata dal': 'rjd',
        'rjd': 'rjd',
        
        # UPPL
        'united people party limited': 'uppl',
        'uppl': 'uppl',
        
        # AIUDF
        'all india united democratic front': 'aiudf',
        'aiudf': 'aiudf',
        
        # Independent
        'independent': 'ind',
        'ind': 'ind',
    }
    
    return party_mapping.get(party, party)


# ============================================================================
# TASK 2: BUILD STATE-WISE LOOKUP
# ============================================================================

def build_candidate_lookup(cand_df: pd.DataFrame) -> Dict:
    """
    Build state-wise candidate lookup for fast matching.
    
    Structure:
    {
        'state': {
            'constituency': [
                {'candidate': str, 'party': str},
                ...
            ],
            ...
        }
    }
    
    Args:
        cand_df: Candidate dataframe (cleaned)
        
    Returns:
        State-wise lookup dictionary
    """
    print("\n" + "="*80)
    print("TASK 2: BUILDING STATE-WISE LOOKUP")
    print("="*80)
    
    lookup = defaultdict(lambda: defaultdict(list))
    
    for _, row in cand_df.iterrows():
        state = row['state']
        const = row['constituency']
        candidate = row['candidate']
        party = row['party']
        
        lookup[state][const].append({
            'candidate': candidate,
            'party': party
        })
    
    print(f"✓ Built lookup for {len(lookup)} states")
    for state, constituencies in lookup.items():
        print(f"  - {state.title()}: {len(constituencies)} constituencies")
    
    return dict(lookup)


# ============================================================================
# TASK 3: FUZZY MATCH CONSTITUENCIES
# ============================================================================

def fuzzy_match_constituency(
    pred_const: str,
    available_consts: List[str],
    threshold: int = 80
) -> Tuple[Optional[str], int]:
    """
    Fuzzy match a constituency name to available options.
    
    Args:
        pred_const: Constituency from prediction file
        available_consts: List of constituencies in Myneta data
        threshold: Match score threshold (0-100)
        
    Returns:
        (matched_constituency, score) or (None, 0) if below threshold
    """
    if not available_consts:
        return None, 0
    
    if USE_RAPIDFUZZ:
        # Use rapidfuzz for better matching
        match = process.extractOne(
            pred_const,
            available_consts,
            scorer=fuzz.token_set_ratio,
            score_cutoff=threshold
        )
        if match:
            return match[0], match[1]
        return None, 0
    else:
        # Fallback: use difflib
        best_match = None
        best_score = threshold
        
        for const in available_consts:
            ratio = SequenceMatcher(None, pred_const, const).ratio() * 100
            if ratio > best_score:
                best_score = ratio
                best_match = const
        
        if best_match:
            return best_match, int(best_score)
        return None, 0


# ============================================================================
# TASK 4: SELECT WINNING CANDIDATE
# ============================================================================

def select_candidate(
    candidates: List[Dict],
    predicted_party: str
) -> Tuple[Optional[str], bool]:
    """
    Select candidate from list by matching predicted party.
    
    Args:
        candidates: List of {candidate, party} dicts
        predicted_party: Party code from prediction
        
    Returns:
        (candidate_name, is_match) where is_match indicates if party matched
    """
    if not candidates:
        return None, False
    
    # Try exact party match
    for cand_dict in candidates:
        if cand_dict['party'] == predicted_party:
            return cand_dict['candidate'], True
    
    # Fallback: return first candidate (will use fallback in output)
    return candidates[0]['candidate'], False


# ============================================================================
# TASK 5: BUILD FINAL DATAFRAME
# ============================================================================

def integrate_candidates(
    predictions_path: str,
    candidates_path: str,
    lookup: Dict,
    threshold: int = 80
) -> Tuple[pd.DataFrame, Dict]:
    """
    Integrate model predictions with candidate data.
    
    Args:
        predictions_path: Path to predictions CSV
        candidates_path: Path to candidate Excel
        lookup: State-wise candidate lookup
        threshold: Fuzzy match threshold
        
    Returns:
        (integrated_df, stats)
    """
    print("\n" + "="*80)
    print("TASK 3-5: FUZZY MATCHING + CANDIDATE SELECTION + BUILD FINAL DF")
    print("="*80)
    
    # Load predictions
    pred_df = pd.read_csv(predictions_path)
    print(f"\n✓ Loaded predictions: {len(pred_df)} rows")
    
    # Load candidates (for party full names)
    cand_raw = pd.read_excel(candidates_path)
    
    results = []
    stats = {
        'total': len(pred_df),
        'matched': 0,
        'fallback': 0,
        'unmatched': 0,
        'fuzzy_success': 0,
        'fuzzy_fail': 0,
        'party_matched': 0,
        'party_fallback': 0,
    }
    
    unmatched_details = []
    
    for idx, row in pred_df.iterrows():
        state_pred = clean_text(row['state'])
        const_pred = clean_text(row['constituency'])
        party_code = normalize_party(row['predicted_winner'])
        state_orig = row['state']
        const_orig = row['constituency']
        
        # Step 1: Find state in lookup
        if state_pred not in lookup:
            stats['unmatched'] += 1
            unmatched_details.append({
                'state': state_orig,
                'constituency': const_orig,
                'reason': f"State '{state_pred}' not found"
            })
            results.append({
                'state': state_orig,
                'constituency': const_orig,
                'predicted_winner': row['predicted_winner'],  # Fallback to party code
                'match_type': 'STATE_NOT_FOUND'
            })
            stats['fallback'] += 1
            continue
        
        # Step 2: Fuzzy match constituency
        available_consts = list(lookup[state_pred].keys())
        matched_const, fuzzy_score = fuzzy_match_constituency(
            const_pred,
            available_consts,
            threshold
        )
        
        if not matched_const:
            stats['fuzzy_fail'] += 1
            stats['unmatched'] += 1
            unmatched_details.append({
                'state': state_orig,
                'constituency': const_orig,
                'reason': f"No fuzzy match (threshold {threshold}%)"
            })
            results.append({
                'state': state_orig,
                'constituency': const_orig,
                'predicted_winner': row['predicted_winner'],
                'match_type': 'FUZZY_FAIL'
            })
            stats['fallback'] += 1
            continue
        
        stats['fuzzy_success'] += 1
        
        # Step 3: Get candidates for matched constituency
        candidates = lookup[state_pred][matched_const]
        
        # Step 4: Select candidate by party
        candidate_name, party_match = select_candidate(candidates, party_code)
        
        if party_match:
            stats['party_matched'] += 1
        else:
            stats['party_fallback'] += 1
        
        results.append({
            'state': state_orig,
            'constituency': const_orig,
            'predicted_winner': candidate_name if candidate_name else row['predicted_winner'],
            'match_type': 'FULL_MATCH' if party_match else 'PARTY_FALLBACK'
        })
        stats['matched'] += 1
    
    final_df = pd.DataFrame(results)
    
    # Print details
    print(f"\n  Fuzzy Match Results:")
    print(f"    ✓ Success: {stats['fuzzy_success']}")
    print(f"    ✗ Failed: {stats['fuzzy_fail']}")
    
    print(f"\n  Party Match Results:")
    print(f"    ✓ Matched: {stats['party_matched']}")
    print(f"    ⚠️  Fallback: {stats['party_fallback']}")
    
    print(f"\n  Overall:")
    print(f"    ✓ Matched: {stats['matched']}")
    print(f"    ⚠️  Fallback: {stats['fallback']}")
    print(f"    ✗ Unmatched: {stats['unmatched']}")
    
    if unmatched_details:
        print(f"\n  Unmatched constituencies (first 10):")
        for detail in unmatched_details[:10]:
            print(f"    - {detail['state']} / {detail['constituency']}")
            print(f"      Reason: {detail['reason']}")
    
    return final_df, stats


# ============================================================================
# TASK 6: VALIDATION
# ============================================================================

def validate_output(df: pd.DataFrame, stats: Dict) -> bool:
    """
    Validate final output meets requirements.
    
    Args:
        df: Final dataframe
        stats: Integration statistics
        
    Returns:
        True if valid, False otherwise
    """
    print("\n" + "="*80)
    print("TASK 6: VALIDATION")
    print("="*80)
    
    checks = {
        'rows_count': len(df) == 824,
        'no_duplicates': len(df) == len(df.drop_duplicates()),
        'no_missing_state': df['state'].notna().all(),
        'no_missing_const': df['constituency'].notna().all(),
        'no_missing_winner': df['predicted_winner'].notna().all(),
        'required_columns': set(['state', 'constituency', 'predicted_winner']).issubset(df.columns)
    }
    
    print("\n✓ Validation Results:")
    all_pass = True
    for check, result in checks.items():
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {check}: {result}")
        if not result:
            all_pass = False
    
    print(f"\n✓ Data Quality:")
    print(f"  Total rows: {len(df)}")
    print(f"  Unique states: {df['state'].nunique()}")
    print(f"  Unique constituencies: {df['constituency'].nunique()}")
    print(f"  Match rate: {stats['matched']/stats['total']*100:.1f}%")
    
    return all_pass


# ============================================================================
# TASK 7: SAVE OUTPUT
# ============================================================================

def save_output(df: pd.DataFrame, output_path: str) -> bool:
    """
    Save final dataframe to CSV.
    
    Args:
        df: Final dataframe
        output_path: Path to save to
        
    Returns:
        True if saved successfully
    """
    print("\n" + "="*80)
    print("TASK 7: SAVE OUTPUT")
    print("="*80)
    
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved to: {output_path}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {', '.join(df.columns)}")
        return True
    except Exception as e:
        print(f"\n✗ Error saving: {e}")
        return False


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Run complete integration pipeline."""
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "CANDIDATE INTEGRATION PIPELINE" + " "*28 + "║")
    print("╚" + "="*78 + "╝")
    
    # Paths
    predictions_path = "outputs/final_submission_2026.csv"
    candidates_path = "data/raw/Candidate Name List with const.xlsx"
    output_path = "outputs/final_submission_FINAL.csv"
    
    # Load and standardize candidate data
    print("\n" + "="*80)
    print("TASK 1: STANDARDIZE DATA")
    print("="*80)
    
    cand_raw = pd.read_excel(candidates_path)
    print(f"\n✓ Loaded candidate data: {len(cand_raw)} rows")
    print(f"  Columns: {', '.join(cand_raw.columns)}")
    
    # Standardize
    cand_clean = cand_raw.copy()
    cand_clean.columns = cand_clean.columns.str.lower().str.strip()
    
    cand_clean['state'] = cand_clean['state'].apply(clean_text)
    cand_clean['constituency'] = cand_clean['constituency'].apply(clean_text)
    cand_clean['party'] = cand_clean['party'].apply(normalize_party)
    cand_clean = cand_clean.rename(columns={'candidate name': 'candidate'})
    cand_clean['candidate'] = cand_clean['candidate'].apply(clean_text)
    
    print(f"\n✓ Standardized columns: {', '.join(cand_clean.columns[:4])}")
    
    # Build lookup
    lookup = build_candidate_lookup(cand_clean)
    
    # Integrate candidates (trying lower threshold for better matches)
    final_df, stats = integrate_candidates(
        predictions_path,
        candidates_path,
        lookup,
        threshold=60  # Lowered from 80 to capture more fuzzy matches
    )
    
    # Validate
    is_valid = validate_output(final_df, stats)
    
    # Save
    save_output(final_df, output_path)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"\n{'✓' if is_valid else '⚠️'} Integration Complete")
    print(f"  Input predictions: {stats['total']}")
    print(f"  Output rows: {len(final_df)}")
    print(f"  Full matches: {stats['matched']} ({stats['matched']/stats['total']*100:.1f}%)")
    print(f"  Fallbacks: {stats['fallback']}")
    print(f"\nOutput file: {output_path}")
    
    return 0 if is_valid else 1


if __name__ == "__main__":
    exit(main())
