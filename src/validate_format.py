#!/usr/bin/env python3
"""
Validate submission format against template requirements.
"""

import pandas as pd
from pathlib import Path
import openpyxl

def check_csv_format():
    """Check if CSV submission meets template requirements."""
    print("\n" + "="*80)
    print("CSV SUBMISSION FORMAT VALIDATION")
    print("="*80)
    
    csv_path = "outputs/final_submission_FINAL_clean.csv"
    
    if not Path(csv_path).exists():
        print(f"✗ File not found: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path)
    
    print(f"\n✓ File loaded: {csv_path}")
    print(f"  Rows: {len(df)} (expected: 824)")
    print(f"  Columns: {list(df.columns)}")
    
    # Check requirements
    checks = {
        'Exactly 824 rows': len(df) == 824,
        'Has "state" column': 'state' in df.columns,
        'Has "constituency" column': 'constituency' in df.columns,
        'Has "predicted_winner" column': 'predicted_winner' in df.columns,
        'No missing values': df.isnull().sum().sum() == 0,
        'No duplicate rows': len(df) == len(df.drop_duplicates()),
        'All states present': df['state'].nunique() == 5,
        'Column case correct': list(df.columns) == ['state', 'constituency', 'predicted_winner']
    }
    
    print("\n✓ Format Checks:")
    all_pass = True
    for check, result in checks.items():
        symbol = "[OK]" if result else "[FAIL]"
        print(f"  {symbol} {check}")
        if not result:
            all_pass = False
    
    if all_pass:
        print("\n✅ CSV FORMAT VALID - Ready for submission")
    else:
        print("\n❌ CSV FORMAT ISSUES - See above")
    
    return all_pass

def check_excel_format():
    """Check if Excel submission meets template requirements."""
    print("\n" + "="*80)
    print("EXCEL SUBMISSION FORMAT VALIDATION")
    print("="*80)
    
    # Try to load template to understand format
    template_path = "Submission Template.xlsx"  # From attachment
    
    if not Path(template_path).exists():
        print(f"\n⚠️  Template file not found: {template_path}")
        print("(This file should be in your project directory)")
        print("\nExpected Excel format should have:")
        print("  - Sheet: 'Predictions' or 'Data'")
        print("  - Columns: State | Constituency | Predicted Winner")
        print("  - Rows: 824 (one per constituency)")
        print("  - No headers except column names")
        return None
    
    print(f"\n✓ Template file found: {template_path}")
    
    try:
        # Read template
        wb = openpyxl.load_workbook(template_path)
        sheet_names = wb.sheetnames
        print(f"  Sheet names: {sheet_names}")
        
        # Try to read with pandas
        template_df = pd.read_excel(template_path)
        print(f"  Template structure:")
        print(f"    Columns: {list(template_df.columns)}")
        print(f"    Sample rows: {len(template_df)}")
        
        # Now create matching Excel file
        csv_df = pd.read_csv("outputs/final_submission_FINAL_clean.csv")
        
        # Save as Excel matching template format
        excel_path = "outputs/final_submission_FINAL.xlsx"
        csv_df.to_excel(excel_path, sheet_name='Predictions', index=False)
        print(f"\n✓ Created Excel submission: {excel_path}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error reading template: {e}")
        return False

def main():
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "SUBMISSION FORMAT VALIDATOR" + " "*31 + "║")
    print("╚" + "="*78 + "╝")
    
    # Check CSV
    csv_valid = check_csv_format()
    
    # Check Excel (if template available)
    excel_valid = check_excel_format()
    
    # Summary
    print("\n" + "="*80)
    print("SUBMISSION READY STATUS")
    print("="*80)
    
    if csv_valid:
        print("\n✅ CSV SUBMISSION: READY")
        print("   File: outputs/final_submission_FINAL_clean.csv")
    else:
        print("\n❌ CSV SUBMISSION: NEEDS FIXES")
    
    if excel_valid:
        print("\n✅ EXCEL SUBMISSION: CREATED")
        print("   File: outputs/final_submission_FINAL.xlsx")
    elif excel_valid is None:
        print("\n⚠️  EXCEL SUBMISSION: Template not found")
        print("   Please place Submission Template.xlsx in project root")
    else:
        print("\n❌ EXCEL SUBMISSION: ERROR")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
