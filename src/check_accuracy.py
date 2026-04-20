#!/usr/bin/env python3
"""
Election Prediction Accuracy Checker

Compares your predictions against actual election results.
Calculates accuracy metrics at different levels:
- Overall accuracy
- State-wise accuracy
- Party-wise breakdown
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_data(predictions_path, actual_path):
    """Load predictions and actual results."""
    try:
        predictions = pd.read_csv(predictions_path)
        print(f"✓ Loaded predictions: {len(predictions)} rows")
        
        actual = pd.read_csv(actual_path)
        print(f"✓ Loaded actual results: {len(actual)} rows")
        
        return predictions, actual
    except FileNotFoundError as e:
        print(f"✗ File not found: {e}")
        return None, None


def normalize_data(df):
    """Normalize state and constituency names for comparison."""
    df = df.copy()
    
    if 'state' in df.columns:
        df['state'] = df['state'].str.lower().str.strip()
    
    if 'constituency' in df.columns:
        df['constituency'] = df['constituency'].str.lower().str.strip()
    
    # Normalize winner column
    for col in ['predicted_winner', 'actual_winner', 'winner']:
        if col in df.columns:
            df[col] = df[col].str.lower().str.strip()
    
    return df


def merge_results(predictions, actual):
    """Merge predictions with actual results."""
    
    # Normalize both datasets
    pred_norm = normalize_data(predictions.copy())
    actual_norm = normalize_data(actual.copy())
    
    # Create merge keys
    pred_norm['key'] = pred_norm['state'] + '|' + pred_norm['constituency']
    actual_norm['key'] = actual_norm['state'] + '|' + actual_norm['constituency']
    
    # Merge on key
    merged = pred_norm.merge(
        actual_norm,
        on='key',
        how='left',
        suffixes=('_pred', '_actual')
    )
    
    print(f"\n✓ Merged: {len(merged)} rows")
    print(f"  Matched: {merged['actual_winner'].notna().sum()}")
    print(f"  Unmatched: {merged['actual_winner'].isna().sum()}")
    
    return merged


def calculate_accuracy(merged_df):
    """Calculate accuracy metrics."""
    
    print("\n" + "="*80)
    print("ACCURACY METRICS")
    print("="*80)
    
    # Overall accuracy
    matched = merged_df[merged_df['actual_winner'].notna()].copy()
    
    if len(matched) == 0:
        print("\n✗ No matched data to calculate accuracy")
        return None
    
    correct = (
        matched['predicted_winner'] == matched['actual_winner']
    ).sum()
    
    total = len(matched)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"\nOVERALL ACCURACY:")
    print(f"  Correct: {correct}/{total}")
    print(f"  Accuracy: {accuracy:.2f}%")
    
    return {
        'correct': correct,
        'total': total,
        'accuracy': accuracy,
        'merged': matched
    }


def state_wise_accuracy(merged_df):
    """Calculate accuracy by state."""
    
    matched = merged_df[merged_df['actual_winner'].notna()].copy()
    
    if len(matched) == 0:
        return None
    
    print(f"\n" + "="*80)
    print("STATE-WISE ACCURACY")
    print("="*80 + "\n")
    
    state_accuracy = []
    
    for state in sorted(matched['state_pred'].unique()):
        state_data = matched[matched['state_pred'] == state]
        correct = (
            state_data['predicted_winner'] == state_data['actual_winner']
        ).sum()
        total = len(state_data)
        acc = (correct / total * 100) if total > 0 else 0
        
        state_accuracy.append({
            'state': state.title(),
            'correct': correct,
            'total': total,
            'accuracy': acc
        })
        
        print(f"{state.title():15s}: {correct:3d}/{total:3d} = {acc:6.2f}%")
    
    return pd.DataFrame(state_accuracy)


def party_analysis(merged_df):
    """Analyze predictions by party."""
    
    matched = merged_df[merged_df['actual_winner'].notna()].copy()
    
    if len(matched) == 0:
        return None
    
    print(f"\n" + "="*80)
    print("PARTY-WISE BREAKDOWN")
    print("="*80 + "\n")
    
    print("Predictions by party (top 10):")
    pred_counts = matched['predicted_winner'].value_counts().head(10)
    for party, count in pred_counts.items():
        print(f"  {party:20s}: {count:3d}")
    
    print(f"\nActual winners by party (top 10):")
    actual_counts = matched['actual_winner'].value_counts().head(10)
    for party, count in actual_counts.items():
        print(f"  {party:20s}: {count:3d}")


def save_results(merged_df, output_path):
    """Save detailed results for review."""
    
    # Save all results
    merged_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved detailed results: {output_path}")
    
    # Also save mismatches only
    mismatches = merged_df[
        (merged_df['actual_winner'].notna()) & 
        (merged_df['predicted_winner'] != merged_df['actual_winner'])
    ]
    
    mismatch_path = output_path.replace('.csv', '_mismatches.csv')
    mismatches.to_csv(mismatch_path, index=False)
    print(f"✓ Saved mismatches ({len(mismatches)} rows): {mismatch_path}")


def main():
    """Main accuracy checking pipeline."""
    
    print("\n" + "="*80)
    print("ELECTION PREDICTION ACCURACY CHECKER")
    print("="*80 + "\n")
    
    # Paths
    predictions_path = "outputs/final_submission_FINAL_clean.csv"
    actual_path = "data/raw/actual_results.csv"  # You need to provide this!
    
    # Check if actual results exist
    if not Path(actual_path).exists():
        print(f"✗ Actual results file not found: {actual_path}")
        print("\nTo check accuracy, you need to:")
        print("1. Get the actual 2026 election results")
        print("2. Save as CSV with columns: state, constituency, actual_winner")
        print(f"3. Place at: {actual_path}")
        print("\nExample format:")
        print("  state,constituency,actual_winner")
        print("  Assam,ABHAYAPURI NORTH,Pradip Sarkar")
        print("  Assam,ABHAYAPURI SOUTH,Nizamur Rahman")
        return
    
    # Load data
    predictions, actual = load_data(predictions_path, actual_path)
    if predictions is None or actual is None:
        return
    
    # Merge results
    merged = merge_results(predictions, actual)
    
    # Calculate accuracy
    acc_results = calculate_accuracy(merged)
    if not acc_results:
        return
    
    # State-wise accuracy
    state_acc = state_wise_accuracy(merged)
    
    # Party analysis
    party_analysis(merged)
    
    # Save results
    output_path = "reports/accuracy_detailed.csv"
    save_results(merged, output_path)
    
    # Summary
    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal predictions: {len(predictions)}")
    print(f"Matched with actual: {acc_results['total']}")
    print(f"Correct predictions: {acc_results['correct']}")
    print(f"\n>>> ACCURACY: {acc_results['accuracy']:.2f}% <<<\n")


if __name__ == "__main__":
    main()
