import pandas as pd

final = pd.read_csv("outputs/final_submission_final.csv")
truth = pd.read_csv("data/processed/final_dataset.csv")

truth_2021 = truth[truth["year"] == 2021][["state","constituency","winner_party"]]

# If your final file has candidate names, map back to party
# (simple fallback: use winner_party from predictions file)

pred = pd.read_csv("outputs/final_predictions.csv")

df = final.merge(
    pred[["state","constituency","winner_party"]],
    on=["state","constituency"],
    how="left"
)

df = df.merge(truth_2021, on=["state","constituency"], how="left")

accuracy = (df["winner_party_x"] == df["winner_party_y"]).mean()

print("Corrected Accuracy:", round(accuracy, 4))