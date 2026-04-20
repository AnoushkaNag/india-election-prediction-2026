#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('outputs/final_submission_TEMPLATE_FORMAT.csv')

# Find constituencies with multiple W outcomes
w_by_const = df[df['Predicted Outcome'] == 'W'].groupby('Constituency').size()
multi_w = w_by_const[w_by_const > 1]

print(f'Constituencies with multiple W outcomes: {len(multi_w)}')
print()
for const, count in multi_w.items():
    print(f'{const}: {count} W outcomes')
    
    # Show the rows
    rows = df[(df['Constituency'] == const) & (df['Predicted Outcome'] == 'W')]
    for idx, row in rows.iterrows():
        print(f"  - {row['Candidate Name']:<40s} ({row['Party']})")
