import pandas as pd

def apply_rules(df):
    """Apply rule-based scoring using structural features."""
    scores = []

    for _, row in df.iterrows():
        score = 0

        # Rule 1: Incumbent advantage
        if row["incumbent"] == 1:
            score += 1

        # Rule 2: Close contest → likely flip risk
        if row["close_contest"] == 1:
            score -= 1

        # Rule 3: Safe seat → likely retain
        if row["safe_seat"] == 1:
            score += 2

        # Rule 4: Anti-incumbency → flip risk
        if row["margin_change"] < 0:
            score -= 1

        scores.append(score)

    df["rule_score"] = scores

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_features.csv")

    df = apply_rules(df)

    df.to_csv("data/processed/final_with_rules.csv", index=False)

    print("Rule engine applied!")
    print(df.head())