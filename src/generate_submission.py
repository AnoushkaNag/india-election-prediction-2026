import pandas as pd

def generate_predictions(df):
    final_winners = []

    for _, row in df.iterrows():

        if row["prediction"] == 1:
            # retain → same party
            winner = row["winner_party"]
        else:
            # flip → runner-up becomes winner
            winner = row["runner_up_party"]

        final_winners.append(winner)

    df["predicted_winner"] = final_winners

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_predictions.csv")

    df = generate_predictions(df)

    # Keep only required columns
    submission = df[["state", "constituency", "predicted_winner"]]

    submission.to_excel("outputs/final_submission.xlsx", index=False)

    print("Submission file ready!")
    print(submission.head())