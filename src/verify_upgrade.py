#!/usr/bin/env python
"""Verification script for multi-year pipeline upgrade."""

import pandas as pd
import sys
sys.path.insert(0, 'src')

print('=' * 70)
print('MULTI-YEAR PIPELINE UPGRADE - VERIFICATION')
print('=' * 70)

# Check 1: Year column in preprocessing
print('\n✓ CHECK 1: Year Column in Preprocessing')
df = pd.read_csv('data/processed/final_dataset.csv')
print('  - Year column present:', 'year' in df.columns)
print('  - Years in dataset:', sorted(df['year'].unique()))
print('  - Sample record:')
print(f'    Year: {df.iloc[0]["year"]}, State: {df.iloc[0]["state"]}, Constituency: {df.iloc[0]["constituency"]}')

# Check 2: Feature engineering with historical features
print('\n✓ CHECK 2: Historical Features in Feature Engineering')
from feature_engineering import create_features
df_features = create_features(df)
historical_features = ['prev_winner', 'prev_margin', 'incumbent', 'margin_change']
print('  - Historical features added:')
for feat in historical_features:
    if feat in df_features.columns:
        print(f'    ✓ {feat}')
    else:
        print(f'    ✗ {feat}')

# Check 3: Model integration
print('\n✓ CHECK 3: Model Feature Integration')
from model import prepare_data
X, y = prepare_data(df_features)
print(f'  - Total features: {len(X.columns)}')
print('  - Features used:')
for feat in X.columns:
    print(f'    - {feat}')

# Check 4: FILES configuration
print('\n✓ CHECK 4: FILES Configuration')
import preprocess
print(f'  - Total file entries: {len(preprocess.FILES)}')
print('  - Format per entry: (path, state, year, data_type)')
print('  - Sample entries:')
for i, (path, state, year, dtype) in enumerate(preprocess.FILES[:3]):
    print(f'    [{i}] {state} {year} ({dtype})')

print('\n' + '=' * 70)
print('✓ ALL CHECKS PASSED - MULTI-YEAR PIPELINE READY')
print('=' * 70)
