#!/usr/bin/env python
"""Verify final dataset after preprocessing improvements."""

import pandas as pd

df = pd.read_csv('data/processed/final_dataset.csv')

print('FINAL DATASET VERIFICATION')
print('=' * 60)
print(f'Total rows: {len(df)}')
print(f'Total states: {df["state"].nunique()}')
print(f'Years covered: {sorted(df["year"].unique())}')

print('\nRows per year:')
print(df['year'].value_counts().sort_index())

print('\nData types:')
print(df['data_type'].value_counts())

print('\nSample rows:')
print(df[['year', 'state', 'constituency', 'winner_party', 'winner_votes', 
          'runner_up_party', 'runner_up_votes']].head(10).to_string())

print('\n' + '=' * 60)
print('QUALITY CHECKS')
print('=' * 60)
print(f'Missing values in winner_votes: {df["winner_votes"].isna().sum()}')
print(f'Missing values in runner_up_votes: {df["runner_up_votes"].isna().sum()}')
print(f'All votes are positive: {(df["winner_votes"] > 0).all() and (df["runner_up_votes"] > 0).all()}')
print(f'Vote margin is consistent: {(df["vote_margin"] == df["winner_votes"] - df["runner_up_votes"]).all()}')
print(f'Total votes is consistent: {(df["total_votes"] == df["winner_votes"] + df["runner_up_votes"]).all()}')
