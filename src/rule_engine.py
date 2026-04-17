import pandas as pd

def apply_rules(df):
    scores = []

    for _, row in df.iterrows():
        score = 0

        # Rule 1: Close contest → likely flip
        if row["margin"] < 0.05:
            score -= 2

        # Rule 2: Strong win → likely retain
        if row["margin"] > 0.15:
            score += 2

        # Rule 3: Medium margin
        if 0.05 <= row["margin"] <= 0.15:
            score += 0.5

        scores.append(score)

    df["rule_score"] = scores

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_features.csv")

    df = apply_rules(df)

    df.to_csv("data/processed/final_with_rules.csv", index=False)

    print("Rule engine applied!")
    print(df.head())