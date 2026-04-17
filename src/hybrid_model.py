import pandas as pd
from sklearn.metrics import accuracy_score


def hybrid_prediction(df, ml_weight=0.6, rule_weight=0.4, threshold=0.6):
    """Combine ML predictions with rule-based scores for hybrid predictions.
    
    Args:
        df: DataFrame with ml_probability and rule_score columns
        ml_weight: Weight for ML predictions (default 0.6)
        rule_weight: Weight for rule-based scores (default 0.4)
        threshold: Decision threshold for final prediction (default 0.6)
    
    Returns:
        DataFrame with hybrid predictions and scores
    """
    # Normalize rule score from [-2, 2] to [0, 1]
    df["rule_score_norm"] = (df["rule_score"] + 2) / 4

    # Combine ML and rule-based scores
    df["final_score"] = (
        ml_weight * df["ml_probability"]
        + rule_weight * df["rule_score_norm"]
    )

    # Make hybrid prediction
    df["prediction"] = df["final_score"].apply(
        lambda x: 1 if x > threshold else 0
    )

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_with_ml.csv")

    df = hybrid_prediction(df)

    # Evaluate hybrid model
    acc = accuracy_score(df["target"], df["prediction"])
    print(f"\nHybrid Model Results:")
    print(f"  Accuracy: {acc:.4f}")
    print(f"  Weight (ML): 0.6")
    print(f"  Weight (Rules): 0.4")
    print(f"  Threshold: 0.6")
    print(f"  Predictions distribution:")
    print(f"    Retain (1): {(df['prediction'] == 1).sum()}")
    print(f"    Flip (0): {(df['prediction'] == 0).sum()}")

    df.to_csv("data/processed/final_predictions.csv", index=False)

    print("\nHybrid predictions complete!")