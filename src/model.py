import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def prepare_data(df):
    # Target (keep this simple)
    df["target"] = df["margin"].apply(lambda x: 1 if x > 0.08 else 0)

    # ❌ REMOVE leakage features
    # margin, vote_share_winner, vote_share_runner

    # ✅ CLEAN feature set (no leakage)
    features = [
        "swing_risk",
        "dominant_win",
        "incumbent",
        "margin_change",
        "flip_probability"
    ]

    return df, features


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_with_rules.csv")

    df, features = prepare_data(df)

    # Train on 2016, test on 2021
    train_df = df[df["year"] == 2016].copy()
    test_df = df[df["year"] == 2021].copy()

    X_train = train_df[features]
    y_train = train_df["target"]

    X_test = test_df[features]
    y_test = test_df["target"]

    # Regularized model to avoid overfitting and improve generalization
    model = RandomForestClassifier(
        n_estimators=80,
        max_depth=4,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    model.fit(X_train, y_train)

    test_df["ml_probability"] = model.predict_proba(X_test)[:, 1]
    test_df["ml_prediction"] = model.predict(X_test)

    acc = accuracy_score(y_test, test_df["ml_prediction"])
    print(f"\nML Accuracy: {acc:.4f}")

    test_df.to_csv("data/processed/final_with_ml.csv", index=False)