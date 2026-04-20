#!/usr/bin/env python3
"""
Convert submission to template format handling missing candidate data.
For constituencies WITH candidates in Myneta: use all candidates
For constituencies WITHOUT candidates: use predicted winner as single entry
"""

import pandas as pd
from pathlib import Path

def normalize(text):
    """Normalize text for comparison."""
    if pd.isna(text):
        return ""
    return str(text).lower().strip()

def convert_with_fallback():
    """
    Convert predictions to W/L/O format with fallback for missing candidates.
    """
    
    print("\n" + "="*80)
    print("CONVERTING TO TEMPLATE FORMAT WITH FALLBACK FOR MISSING DATA")
    print("="*80)
    
    # Load files
    submission = pd.read_csv("outputs/final_submission_FINAL_clean.csv")
    candidates_df = pd.read_excel("data/raw/Candidate Name List with const.xlsx")
    
    print(f"\n✓ Loaded {len(submission)} predictions")
    print(f"✓ Loaded {len(candidates_df)} candidates from {len(candidates_df['Constituency'].unique())} constituencies")
    
    # Normalize for matching
    candidates_df['norm_state'] = candidates_df['State'].apply(normalize)
    candidates_df['norm_const'] = candidates_df['Constituency'].apply(normalize)
    submission['norm_state'] = submission['state'].apply(normalize)
    submission['norm_const'] = submission['constituency'].apply(normalize)
    submission['norm_winner'] = submission['predicted_winner'].apply(normalize)
    
    # Build output
    output_rows = []
    constituencies_with_data = set(
        zip(candidates_df['norm_state'], candidates_df['norm_const'])
    )
    
    print("\n" + "="*80)
    print("PROCESSING PREDICTIONS")
    print("="*80)
    
    processed = 0
    with_candidates = 0
    without_candidates = 0
    
    for idx, pred_row in submission.iterrows():
        state = pred_row['state']
        constituency = pred_row['constituency']
        predicted_winner = pred_row['predicted_winner']
        
        key = (pred_row['norm_state'], pred_row['norm_const'])
        
        # Get candidates for this constituency
        const_candidates = candidates_df[
            (candidates_df['norm_state'] == pred_row['norm_state']) &
            (candidates_df['norm_const'] == pred_row['norm_const'])
        ]
        
        if len(const_candidates) > 0:
            # Case 1: We have candidate data
            with_candidates += 1
            
            found_winner = False
            for cand_idx, cand_row in const_candidates.iterrows():
                candidate_name = cand_row['Candidate Name']
                party = cand_row['Party']
                
                # Check if this is the predicted winner (only mark first match as W)
                norm_candidate = normalize(candidate_name)
                is_winner = (not found_winner) and (norm_candidate == pred_row['norm_winner'])
                
                if is_winner:
                    found_winner = True
                
                outcome = 'W' if is_winner else 'L'
                
                output_rows.append({
                    'State/UT': state,
                    'Phase': 1,
                    'Constituency': constituency,
                    'Candidate Name': candidate_name,
                    'Party': party,
                    'Predicted Outcome': outcome
                })
            
            # If predicted winner not found in Myneta candidates, add them as W
            if not found_winner:
                output_rows.append({
                    'State/UT': state,
                    'Phase': 1,
                    'Constituency': constituency,
                    'Candidate Name': predicted_winner,
                    'Party': 'UNKNOWN',
                    'Predicted Outcome': 'W'
                })
        else:
            # Case 2: No candidate data - add predicted winner as single entry
            without_candidates += 1
            
            output_rows.append({
                'State/UT': state,
                'Phase': 1,
                'Constituency': constituency,
                'Candidate Name': predicted_winner,
                'Party': 'UNKNOWN',
                'Predicted Outcome': 'W'
            })
        
        processed += 1
        if processed % 100 == 0:
            print(f"  ✓ Processed {processed}/824 ({with_candidates} with data, {without_candidates} fallback)")
    
    # Create output dataframe
    output_df = pd.DataFrame(output_rows)
    
    print(f"\n✓ Generated {len(output_df)} candidate predictions")
    print(f"  - {with_candidates} constituencies with candidate data")
    print(f"  - {without_candidates} constituencies with fallback (no Myneta data)")
    
    # Verify
    print("\n" + "="*80)
    print("OUTPUT VERIFICATION")
    print("="*80)
    
    print(f"\nRows per state:")
    for state in sorted(output_df['State/UT'].unique()):
        count = len(output_df[output_df['State/UT'] == state])
        print(f"  {state:20s}: {count:5d} rows")
    
    print(f"\nOutcome distribution:")
    for outcome, count in sorted(output_df['Predicted Outcome'].value_counts().items()):
        pct = count / len(output_df) * 100
        print(f"  {outcome}: {count:5d} ({pct:5.1f}%)")
    
    w_count = len(output_df[output_df['Predicted Outcome'] == 'W'])
    unique_const = output_df['Constituency'].nunique()
    
    print(f"\n✓ Total rows: {len(output_df)}")
    print(f"✓ Unique constituencies: {unique_const} (expected: 824)")
    print(f"✓ 'W' (Win) predictions: {w_count} (expected: 824)")
    
    if unique_const == 824 and w_count == 824:
        print("\n✅ PERFECT! All 824 constituencies have exactly one 'W' prediction")
    else:
        print("\n⚠️  Warning: Mismatch detected")
    
    # Save files
    output_path_xlsx = "outputs/final_submission_TEMPLATE_FORMAT.xlsx"
    output_path_csv = "outputs/final_submission_TEMPLATE_FORMAT.csv"
    
    output_df.to_excel(output_path_xlsx, sheet_name='Predictions', index=False)
    output_df.to_csv(output_path_csv, index=False)
    
    print(f"\n✓ Saved to: {output_path_xlsx}")
    print(f"✓ Saved to: {output_path_csv}")
    
    return output_df

if __name__ == "__main__":
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*12 + "CONVERT TO CHALLENGE TEMPLATE (HANDLES MISSING CANDIDATES)" + " "*5 + "║")
    print("╚" + "="*78 + "╝")
    
    df = convert_with_fallback()
    
    print("\n" + "="*80)
    print("✅ READY FOR SUBMISSION")
    print("="*80)
    
    print("\nYour submission files:")
    print("  📊 outputs/final_submission_TEMPLATE_FORMAT.xlsx (UPLOAD THIS)")
    print("  📋 outputs/final_submission_TEMPLATE_FORMAT.csv (Backup)")
    
    print("\nTemplate format:")
    print("  Column A: State/UT")
    print("  Column B: Phase (1)")
    print("  Column C: Constituency")
    print("  Column D: Candidate Name")
    print("  Column E: Party")
    print("  Column F: Predicted Outcome (W/L/O)")
    
    print("\nTotal predictions: ", len(df))
    print("Submission deadline: April 30, 2026")
    print("\n" + "="*80)
