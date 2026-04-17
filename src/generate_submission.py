import pandas as pd


def generate_predictions(df):
    predictions = []

    for _, row in df.iterrows():

        if row["prediction"] == 1:
            # retain
            winner = row["winner_party"]

        else:
            # flip logic
            if row["margin"] < 0.03:
                winner = row["runner_up_party"]
            else:
                winner = row["winner_party"]

        predictions.append(winner)

    df["predicted_winner"] = predictions

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_predictions.csv")

    df = generate_predictions(df)

    # 🎯 FILTER ONLY REQUIRED STATES
    target_states = [
        "Kerala",
        "Tamil Nadu",
        "West Bengal",
        "Assam",
        "Puducherry"
    ]

    # Filter only target states
    submission = df[df["state"].isin(target_states)]

    # Keep only required columns
    submission = submission[
        ["state", "constituency", "predicted_winner"]
    ]

    # Remove duplicates by state and constituency
    submission = submission.drop_duplicates(
        subset=["state", "constituency"], keep="first"
    )

    # Sort by state then constituency
    submission = submission.sort_values(["state", "constituency"])

    # Verify state distribution
    print("\nState distribution:")
    print(submission["state"].value_counts().sort_index())

    print(f"\nTotal rows: {len(submission)}")
    original_count = len(df[df["state"].isin(target_states)])
    duplicates_removed = original_count - len(submission)
    if duplicates_removed > 0:
        print(f"Duplicates removed: {duplicates_removed}")

    # Save to Excel
    try:
        submission.to_excel("outputs/final_submission.xlsx", index=False)
        print("\nSubmission file ready: outputs/final_submission.xlsx")
    except PermissionError:
        # If Excel file is locked, save as CSV instead
        submission.to_csv("outputs/final_submission.csv", index=False)
        print("\nSubmission file ready: outputs/final_submission.csv")
        print("(Excel file was locked, saved as CSV instead)")

    print("\nFirst 10 rows:")
    print(submission.head(10))