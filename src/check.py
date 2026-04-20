import pandas as pd

# Load files
final = pd.read_csv("outputs/final_submission_2026.csv")
cand = pd.read_excel("data/raw/Candidate Name List with const.xlsx")

# Normalize columns
cand.columns = cand.columns.str.strip().str.lower()

# Rename for consistency
cand = cand.rename(columns={
    "candidate name": "candidate"
})

# Normalize values
import re

def clean(x):
    x = str(x).lower().strip()

    # remove special tags
    x = re.sub(r"\(.*?\)", "", x)   # remove (SC), (AC 255), etc
    x = re.sub(r"[^a-z0-9 ]", "", x)  # remove symbols
    x = re.sub(r"\s+", " ", x)  # normalize spaces

    return x
# FINAL RESULT
results = []

matched = 0
fallback = 0

for _, row in final.iterrows():
    state = row["state"]
    constituency = row["constituency"]
    predicted_party = str(row["predicted_winner"]).strip().lower()

    # filter candidates for that seat
    subset = cand[
        (cand["state"] == state) &
        (cand["constituency"] == constituency)
    ]

    # find matching party
    match = subset[
        subset["party"].str.lower() == predicted_party
    ]

    if len(match) > 0:
        candidate_name = match.iloc[0]["candidate"]
        matched += 1
    else:
        candidate_name = row["predicted_winner"]  # fallback
        fallback += 1

    results.append({
        "state": state.title(),
        "constituency": constituency.title(),
        "predicted_winner": candidate_name
    })

final_df = pd.DataFrame(results)

# Save
final_df.to_csv("outputs/final_submission_FINAL.csv", index=False)

print("\n=== FINAL OUTPUT ===")
print("Rows:", len(final_df))
print("Matched:", matched)
print("Fallback:", fallback)