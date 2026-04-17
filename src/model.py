import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def prepare_data(df):
    # Target: 1 = retain, 0 = flip
    df["target"] = df["margin"].apply(lambda x: 1 if x > 0.08 else 0)

    features = [
        "vote_share_winner",
        "vote_share_runner",
        "margin",
        "swing_risk",
        "dominant_win"
    ]

    X = df[features]
    y = df["target"]

    return X, y

def train_model(X, y):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def apply_model(model, X):
    probs = model.predict_proba(X)

    if probs.shape[1] == 1:
        return [1.0] * len(X)  # fallback

    return probs[:, 1]


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_with_rules.csv")

    X, y = prepare_data(df)

    model = train_model(X, y)

    df["ml_probability"] = apply_model(model, X)

    df.to_csv("data/processed/final_with_ml.csv", index=False)

    print("ML model applied!")
    print(df.head())