#!/usr/bin/env python3
"""
Diagnostic script to analyze prediction quality and identify potential issues.
"""

import pandas as pd
from collections import Counter
from pathlib import Path

def analyze_predictions():
    """Analyze prediction patterns for potential issues."""
    
    csv_path = "outputs/final_submission_FINAL_clean.csv"
    
    print("\n" + "="*80)
    print("PREDICTION QUALITY DIAGNOSTIC REPORT")
    print("="*80)
    
    df = pd.read_csv(csv_path)
    
    # 1. State-wise distribution
    print("\n📊 STATE-WISE PREDICTION DISTRIBUTION")
    print("-" * 80)
    state_dist = df['state'].value_counts().sort_index()
    for state, count in state_dist.items():
        print(f"  {state:20s}: {count:3d} constituencies ({count/len(df)*100:5.1f}%)")
    
    # 2. Party distribution
    print("\n🎯 PREDICTED WINNER DISTRIBUTION (Top 20)")
    print("-" * 80)
    party_dist = df['predicted_winner'].value_counts().head(20)
    for i, (winner, count) in enumerate(party_dist.items(), 1):
        pct = count/len(df)*100
        print(f"  {i:2d}. {winner:30s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\n  Total unique predicted winners: {df['predicted_winner'].nunique()}")
    
    # 3. Extract and analyze party names
    print("\n🏛️  PARTY-LEVEL ANALYSIS")
    print("-" * 80)
    
    def extract_party(name):
        """Extract likely party abbreviation/name."""
        if not name or pd.isna(name):
            return "Unknown"
        name = str(name).upper()
        
        # Try common party patterns
        if any(x in name for x in ['BJP', 'BHARATIYA', 'JANATA']):
            return "BJP"
        elif any(x in name for x in ['INC', 'CONGRESS', 'GANDHI']):
            return "INC"
        elif any(x in name for x in ['DRAVIDA', 'DMK', 'AIADMK']):
            return "DMK/AIADMK"
        elif any(x in name for x in ['TATA', 'TRINAMOOL', 'TMC']):
            return "TMC"
        elif any(x in name for x in ['CPM', 'CPIM', 'COMMUNIST']):
            return "CPM"
        elif any(x in name for x in ['REGIONAL', 'REGIONAL']):
            return "Regional"
        else:
            return "Other/Independent"
    
    df['party'] = df['predicted_winner'].apply(extract_party)
    party_analysis = df['party'].value_counts()
    
    for party, count in party_analysis.items():
        pct = count/len(df)*100
        print(f"  {party:20s}: {count:3d} ({pct:5.1f}%)")
    
    # 4. State-Party cross-tabulation
    print("\n🗺️  STATE × PARTY PREDICTIONS")
    print("-" * 80)
    
    crosstab = pd.crosstab(df['state'], df['party'], margins=True)
    print(crosstab.to_string())
    
    # 5. Check for potential issues
    print("\n⚠️  POTENTIAL ISSUES TO INVESTIGATE")
    print("-" * 80)
    
    issues = []
    
    # Check for dominant candidate
    top_winner = df['predicted_winner'].value_counts().iloc[0]
    if top_winner > 50:
        issues.append(f"⚠️  Dominant prediction: '{df['predicted_winner'].value_counts().index[0]}' appears {top_winner} times")
    
    # Check for low diversity
    unique_winners = df['predicted_winner'].nunique()
    if unique_winners < 50:
        issues.append(f"⚠️  Low diversity: Only {unique_winners} unique candidates predicted (expected 200+)")
    
    # Check for missing party indicators
    party_unknown = (df['party'] == 'Other/Independent').sum()
    pct_unknown = party_unknown/len(df)*100
    if pct_unknown > 20:
        issues.append(f"⚠️  High unknown party ratio: {party_unknown} ({pct_unknown:.1f}%)")
    
    # Check state balances
    for state in df['state'].unique():
        state_data = df[df['state'] == state]
        state_party = state_data['party'].value_counts()
        
        if len(state_party) > 0:
            top_party_pct = state_party.iloc[0] / len(state_data) * 100
            if top_party_pct > 80:
                issues.append(f"⚠️  {state}: Single party dominance ({state_party.index[0]} {top_party_pct:.0f}%)")
    
    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  ✓ No obvious issues detected")
    
    # 6. Statistics
    print("\n📈 QUICK STATISTICS")
    print("-" * 80)
    print(f"  Total predictions: {len(df)}")
    print(f"  Unique states: {df['state'].nunique()}")
    print(f"  Unique constituencies: {df['constituency'].nunique()}")
    print(f"  Unique predicted winners: {df['predicted_winner'].nunique()}")
    print(f"  Missing values: {df.isnull().sum().sum()}")
    print(f"  Duplicate rows: {len(df) - len(df.drop_duplicates())}")
    
    # 7. Data quality
    print("\n✅ DATA QUALITY")
    print("-" * 80)
    
    quality_checks = {
        'Valid count (824)': len(df) == 824,
        'No missing values': df.isnull().sum().sum() == 0,
        'No duplicates': len(df) == len(df.drop_duplicates()),
        'All states valid': df['state'].nunique() == 5,
        'All constituencies unique': len(df) == len(df['constituency'].unique()),
        'Candidate names not empty': (df['predicted_winner'].str.strip() != '').all(),
    }
    
    for check, result in quality_checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}")
    
    # 8. Export sample predictions for manual review
    print("\n📋 SAMPLE PREDICTIONS (First 10)")
    print("-" * 80)
    sample = df.head(10)[['state', 'constituency', 'predicted_winner']]
    for idx, row in sample.iterrows():
        print(f"  {row['state']:20s} | {row['constituency']:25s} | {row['predicted_winner']}")
    
    print("\n" + "="*80)

def main():
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*18 + "PREDICTION QUALITY DIAGNOSTIC ANALYZER" + " "*22 + "║")
    print("╚" + "="*78 + "╝")
    
    analyze_predictions()
    
    print("\n💡 NEXT STEPS:")
    print("  1. Once 2026 election results are available:")
    print("     $ python src/check_accuracy.py")
    print("")
    print("  2. Upload your submission file:")
    print("     - CSV: outputs/final_submission_FINAL_clean.csv")
    print("     - Excel: outputs/final_submission_FINAL.xlsx")
    print("")
    print("  3. Deadline: April 30, 2026 (10 days remaining)")
    print("")

if __name__ == "__main__":
    main()
