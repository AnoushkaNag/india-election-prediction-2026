#!/usr/bin/env python3
"""Verify final submission file meets all quality requirements."""

import pandas as pd

df = pd.read_csv('outputs/final_submission_FINAL_clean.csv')

print('=' * 80)
print('FINAL SUBMISSION FILE VERIFICATION')
print('=' * 80)
print()
print('FILE: outputs/final_submission_FINAL_clean.csv')
print()
print('DIMENSIONS:')
print(f'  Rows: {len(df)} (expected: 824)')
print(f'  Columns: {len(df.columns)} (expected: 3)')
print()
print('COLUMNS:')
for i, col in enumerate(df.columns, 1):
    print(f'  {i}. {col}')
print()
print('DATA QUALITY:')
print(f'  Missing values: {df.isnull().sum().sum()} (expected: 0)')
print(f'  Duplicate rows: {len(df) - len(df.drop_duplicates())} (expected: 0)')
print(f'  Unique states: {df["state"].nunique()} (expected: 5)')
print(f'  Unique constituencies: {df["constituency"].nunique()} (expected: 824)')
print()
print('STATE DISTRIBUTION:')
for state in sorted(df['state'].unique()):
    count = len(df[df['state'] == state])
    print(f'  {state:15s}: {count:3d} constituencies')
print()
print('SAMPLE DATA (First 5 rows):')
print(df.head().to_string(index=False))
print()
print('VERIFICATION RESULT:')
checks = [
    ('Row count', len(df) == 824),
    ('Column count', len(df.columns) == 3),
    ('No missing values', df.isnull().sum().sum() == 0),
    ('No duplicates', len(df) == len(df.drop_duplicates())),
    ('5 states', df['state'].nunique() == 5),
    ('824 unique constituencies', df['constituency'].nunique() == 824),
]
all_pass = all(result for _, result in checks)
for check_name, result in checks:
    symbol = '[OK]' if result else '[FAIL]'
    print(f'  {symbol} {check_name}')
print()
if all_pass:
    print('[SUCCESS] File is ready for submission!')
else:
    print('[ERROR] File has issues - review above')
