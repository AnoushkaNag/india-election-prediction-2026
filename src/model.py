import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def prepare_data(df):
    # Target: 1 = retain (strong margin), 0 = weak/flip
    df["target"] = df["margin"].apply(lambda x: 1 if x > 0.08 else 0)

    features = [
        "vote_share_winner",
        "vote_share_runner",
        "margin",
        "swing_risk",
        "dominant_win",
        "incumbent",
        "margin_change"
    ]

    return df, features


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_with_rules.csv")

    df, features = prepare_data(df)

    # 🔥 TRAIN = 2016, TEST = 2021
    train_df = df[df["year"] == 2016].copy()
    test_df = df[df["year"] == 2021].copy()

    X_train = train_df[features]
    y_train = train_df["target"]

    X_test = test_df[features]
    y_test = test_df["target"]

    # Model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predictions
    test_df["ml_probability"] = model.predict_proba(X_test)[:, 1]
    test_df["ml_prediction"] = model.predict(X_test)

    # Accuracy
    acc = accuracy_score(y_test, test_df["ml_prediction"])
    print(f"\nML Accuracy: {acc:.4f}")

    # Save only TEST (2021)
    test_df.to_csv("data/processed/final_with_ml.csv", index=False)