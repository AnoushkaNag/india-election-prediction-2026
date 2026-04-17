import pandas as pd


def generate_predictions(df):
    final_winners = []

    for _, row in df.iterrows():

        if row["prediction"] == 1:
            # retain → same party
            winner = row["winner_party"]

        else:
            # smarter flip logic
            if row["margin"] < 0.03:
                winner = row["runner_up_party"]
            else:
                winner = row["winner_party"]

        final_winners.append(winner)

    df["predicted_winner"] = final_winners

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/final_predictions.csv")

    df = generate_predictions(df)

    submission = df[["state", "constituency", "predicted_winner"]]

    submission.to_excel("outputs/final_submission.xlsx", index=False)

    print("\nSubmission file ready!")
    print(submission.head())