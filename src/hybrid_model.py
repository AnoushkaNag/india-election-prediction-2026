import pandas as pd
from sklearn.metrics import accuracy_score


def hybrid_prediction(df, ml_weight=0.7, rule_weight=0.3, threshold=0.55):
    # Normalize rule score (-2 to +2 → 0 to 1)
    df["rule_score_norm"] = (df["rule_score"] + 2) / 4

    # Combine ML + rules
    df["final_score"] = (
        ml_weight * df["ml_probability"]
        + rule_weight * df["rule_score_norm"]
    )

    # Final prediction
    df["prediction"] = df["final_score"].apply(
        lambda x: 1 if x > threshold else 0
    )

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_with_ml.csv")

    df = hybrid_prediction(df)

    # Evaluate hybrid accuracy
    acc = accuracy_score(df["target"], df["prediction"])
    print(f"\nHybrid Accuracy: {acc:.4f}")

    df.to_csv("data/processed/final_predictions.csv", index=False)

    print("\nHybrid predictions complete!")
    print(df.head())