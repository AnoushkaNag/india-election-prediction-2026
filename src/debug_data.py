#!/usr/bin/env python3
import pandas as pd

# Load data
submission = pd.read_csv('outputs/final_submission_FINAL_clean.csv')
candidates_df = pd.read_excel('data/raw/Candidate Name List with const.xlsx')

# Normalize
def normalize(text):
    if pd.isna(text):
        return ''
    return str(text).lower().strip()

candidates_df['norm_state'] = candidates_df['State'].apply(normalize)
candidates_df['norm_const'] = candidates_df['Constituency'].apply(normalize)

# Check which constituencies have data
constituencies_with_data = set()
for idx, row in submission.iterrows():
    norm_state = normalize(row['state'])
    norm_const = normalize(row['constituency'])
    
    has_data = len(candidates_df[
        (candidates_df['norm_state'] == norm_state) &
        (candidates_df['norm_const'] == norm_const)
    ]) > 0
    
    if has_data:
        constituencies_with_data.add((norm_state, norm_const))

print(f'Constituencies WITH Myneta data: {len(constituencies_with_data)}')
print(f'Constituencies WITHOUT Myneta data: {824 - len(constituencies_with_data)}')
print()
print('Sample of constituencies WITHOUT data:')
count = 0
for idx, row in submission.iterrows():
    norm_state = normalize(row['state'])
    norm_const = normalize(row['constituency'])
    
    if (norm_state, norm_const) not in constituencies_with_data:
        print(f"  {row['state']:<20s} | {row['constituency']:<30s}")
        count += 1
        if count >= 10:
            break
