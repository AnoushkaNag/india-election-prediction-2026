import pandas as pd
import numpy as np

def create_features(df):
    """Create features including existing and new historical features."""
    
    # Ensure data is sorted by state, constituency, and year
    df = df.sort_values(['state', 'constituency', 'year']).reset_index(drop=True)
    
    # Vote share
    df["vote_share_winner"] = df["winner_votes"] / df["total_votes"]
    df["vote_share_runner"] = df["runner_up_votes"] / df["total_votes"]

    # Margin
    df["margin"] = df["vote_share_winner"] - df["vote_share_runner"]

    # Swing risk
    df["swing_risk"] = df["margin"].apply(lambda x: 1 if x < 0.05 else 0)

    # Dominance
    df["dominant_win"] = df["margin"].apply(lambda x: 1 if x > 0.15 else 0)

    # ============================================
    # HISTORICAL FEATURES (Multi-year)
    # ============================================
    
    # Shift operations work on sorted data
    df["prev_winner"] = df.groupby(['state', 'constituency'])['winner_party'].shift(1)
    df["prev_margin"] = df.groupby(['state', 'constituency'])['margin'].shift(1)
    
    # Incumbent: 1 if same party as previous year, 0 otherwise
    df["incumbent"] = (df["winner_party"] == df["prev_winner"]).astype(int)
    # For first year (where prev_winner is NaN), set incumbent to 0
    df["incumbent"] = df["incumbent"].fillna(0).astype(int)
    
    # Margin change: current margin - previous margin
    df["margin_change"] = df["margin"] - df["prev_margin"]
    # For first year (where prev_margin is NaN), set margin_change to 0
    df["margin_change"] = df["margin_change"].fillna(0)
    
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_dataset.csv")

    df = create_features(df)

    df.to_csv("data/processed/final_features.csv", index=False)

    print("Feature engineering complete!")
    print(df.head())