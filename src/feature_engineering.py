import pandas as pd

def create_features(df):
    # Vote share
    df["vote_share_winner"] = df["winner_votes"] / df["total_votes"]
    df["vote_share_runner"] = df["runner_up_votes"] / df["total_votes"]

    # Margin
    df["margin"] = df["vote_share_winner"] - df["vote_share_runner"]

    # Swing risk
    df["swing_risk"] = df["margin"].apply(lambda x: 1 if x < 0.05 else 0)

    # Dominance
    df["dominant_win"] = df["margin"].apply(lambda x: 1 if x > 0.15 else 0)

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_dataset.csv")

    df = create_features(df)

    df.to_csv("data/processed/final_features.csv", index=False)

    print("Feature engineering complete!")
    print(df.head())