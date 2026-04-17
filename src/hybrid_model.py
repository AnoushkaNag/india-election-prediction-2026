import pandas as pd

def hybrid_prediction(df):
    # Normalize rule score (-2 to +2 → 0 to 1)
    df["rule_score_norm"] = (df["rule_score"] + 2) / 4

    # Combine ML + rules
    df["final_score"] = (0.6 * df["ml_probability"]) + (0.4 * df["rule_score_norm"])

    # Final decision
    df["prediction"] = df["final_score"].apply(lambda x: 1 if x > 0.5 else 0)

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_with_ml.csv")

    df = hybrid_prediction(df)

    df.to_csv("data/processed/final_predictions.csv", index=False)

    print("Hybrid predictions complete!")
    print(df.head())