import pandas as pd
import numpy as np
import os
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
        0.6 * df["ml_probability"]
        + 0.4 * df["rule_score_norm"]
    )

    # Add controlled flip bias penalty (reduces confidence in unstable seats)
    df["final_score"] = df["final_score"] - (0.10 * df["flip_probability"])

    # Add slight randomness for generalization and realistic variation
    df["final_score"] += np.random.uniform(-0.01, 0.01, len(df))

    # PART 2: Add state-level political priors
    # Kerala (alternating pattern → push flips)
    df.loc[df["state"] == "Kerala", "final_score"] -= 0.08

    # Tamil Nadu (anti-incumbency strong)
    df.loc[df["state"] == "Tamil Nadu", "final_score"] -= 0.07

    # West Bengal (dominant party stability)
    df.loc[df["state"] == "West Bengal", "final_score"] += 0.08

    # Assam (moderate incumbency advantage)
    df.loc[df["state"] == "Assam", "final_score"] += 0.04

    # Puducherry (volatile → slight randomness)
    mask = df["state"] == "Puducherry"
    df.loc[mask, "final_score"] += np.random.uniform(-0.03, 0.03, mask.sum())

    # PART 3: ML confidence override
    df.loc[df["ml_probability"] > 0.8, "prediction"] = 1
    df.loc[df["ml_probability"] < 0.2, "prediction"] = 0

    # PART 4: Final prediction based on threshold
    df["prediction"] = (df["final_score"] > 0.6).astype(int)

    # PART 5: Safe seat locking (margin > 0.15 → retain winner)
    df.loc[df["margin"] > 0.15, "prediction"] = 1

    return df


if __name__ == "__main__":
    # Ensure outputs folder exists
    os.makedirs("outputs", exist_ok=True)
    
    df = pd.read_csv("data/processed/final_with_ml.csv")

    df = hybrid_prediction(df)

    # DEBUG: Check before saving
    print("\nDEBUG: df shape before save:", df.shape)
    print(f"DEBUG: df has {len(df)} rows")
    
    if len(df) == 0:
        raise ValueError("ERROR: DataFrame is empty before saving final_predictions.csv")

    # Evaluate hybrid model
    acc = accuracy_score(df["target"], df["prediction"])
    print(f"\nHybrid Model Results:")
    print(f"  Accuracy: {acc:.4f}")
    print(f"  Weight (ML): 0.6")
    print(f"  Weight (Rules): 0.4")
    print(f"  Flip penalty: 0.10")
    print(f"  Threshold: 0.6")
    print(f"  Predictions distribution:")
    print(f"    Retain (1): {(df['prediction'] == 1).sum()}")
    print(f"    Flip (0): {(df['prediction'] == 0).sum()}")

    # Save to outputs folder
    output_path = "outputs/final_predictions.csv"
    df.to_csv(output_path, index=False)
    
    print(f"\nSaved {output_path} successfully")
    print(f"File size: {len(df)} rows")
    
    # Also save to processed for backward compatibility
    df.to_csv("data/processed/final_predictions.csv", index=False)
    print("Hybrid predictions complete!")