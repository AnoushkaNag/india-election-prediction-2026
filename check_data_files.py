#!/usr/bin/env python
"""Check which file has 2016 data."""

import pandas as pd

print('final_with_rules.csv:')
try:
    df1 = pd.read_csv('data/processed/final_with_rules.csv')
    print(f'  Total rows: {len(df1)}')
    print(f'  Years: {sorted(df1["year"].unique())}')
    print(f'  2016 rows: {len(df1[df1["year"] == 2016])}')
except Exception as e:
    print(f'  Error: {e}')

print()

print('final_features.csv:')
try:
    df2 = pd.read_csv('data/processed/final_features.csv')
    print(f'  Total rows: {len(df2)}')
    print(f'  Years: {sorted(df2["year"].unique())}')
    print(f'  2016 rows: {len(df2[df2["year"] == 2016])}')
except Exception as e:
    print(f'  Error: {e}')
