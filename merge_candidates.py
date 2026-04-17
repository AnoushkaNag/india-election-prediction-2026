import pandas as pd
import os

# Ensure outputs folder exists
os.makedirs("outputs", exist_ok=True)

# ========================================
# CHECK AND LOAD PREDICTION FILE
# ========================================
print("\n" + "=" * 60)
print("LOADING AND MERGING DATA")
print("=" * 60 + "\n")

if not os.path.exists("outputs/final_predictions.csv"):
    raise FileNotFoundError("outputs/final_predictions.csv not found — run hybrid_model.py first")

if os.stat("outputs/final_predictions.csv").st_size == 0:
    raise ValueError("outputs/final_predictions.csv is empty — run hybrid_model.py first")

pred_df = pd.read_csv("outputs/final_predictions.csv")
print(f"✓ Loaded predictions: {len(pred_df)} rows")

# Try to load myneta data (optional)
myneta_df = None
if os.path.exists("candidates_cleaned.csv"):
    myneta_df = pd.read_csv("candidates_cleaned.csv")
    print(f"✓ Loaded candidates: {len(myneta_df)} rows")
else:
    print("⚠ candidates_cleaned.csv not found — using party names as fallback")

# ========================================
# FIX STATE NAME MISMATCHES
# ========================================
state_map = {
    "TamilNadu": "Tamil Nadu",
    "WestBengal": "West Bengal"
}

pred_df["state"] = pred_df["state"].replace(state_map)

if myneta_df is not None:
    myneta_df["state"] = myneta_df["state"].replace(state_map)

# ========================================
# NORMALIZE CONSTITUENCIES (KEEP SC/ST)
# ========================================
def normalize(text):
    return str(text).strip().lower()\
        .replace(".", "")\
        .replace(",", "")

pred_df["constituency_clean"] = pred_df["constituency"].apply(normalize)

if myneta_df is not None:
    myneta_df["constituency_clean"] = myneta_df["constituency"].apply(normalize)
    myneta_df["party"] = myneta_df["party"].str.strip()

# ========================================
# FUNCTION TO GET WINNER NAME
# ========================================
def get_candidate(row):
    """Get candidate name using myneta data or fallback to party names."""
    
    # If myneta data is not available, use party names
    if myneta_df is None:
        if row["prediction"] == 1:
            return row.get("winner_name", row["winner_party"])
        else:
            return row.get("runner_up_name", row["runner_up_party"])
    
    state = row["state"]
    const = row["constituency_clean"]
    
    # Determine predicted party
    if row["prediction"] == 1:
        party = row["winner_party"]
    else:
        party = row["runner_up_party"]
    
    party = str(party).strip()
    
    # Case 1: Exact match (state + constituency + party)
    candidates = myneta_df[
        (myneta_df["state"] == state) &
        (myneta_df["constituency_clean"] == const) &
        (myneta_df["party"] == party)
    ]
    
    if len(candidates) > 0:
        name = candidates.iloc[0]["candidate"]
        if str(name).strip() != "":
            return name
    
    # Case 2: Fallback to any candidate in same constituency
    fallback = myneta_df[
        (myneta_df["state"] == state) &
        (myneta_df["constituency_clean"] == const)
    ]
    
    if len(fallback) > 0:
        return fallback.iloc[0]["candidate"]
    
    # Case 3: Final fallback → 2021 data (winner_name/runner_up_name)
    if row["prediction"] == 1:
        return row.get("winner_name", row["winner_party"])
    else:
        return row.get("runner_up_name", row["runner_up_party"])

# ========================================
# APPLY CANDIDATE MAPPING
# ========================================
pred_df["predicted_winner"] = pred_df.apply(get_candidate, axis=1)

# ========================================
# FINAL CLEANUP AND FILTERING
# ========================================
submission = pred_df[[
    "state",
    "constituency",
    "predicted_winner"
]].copy()

# Filter only required states
target_states = ["Kerala", "Tamil Nadu", "West Bengal", "Assam", "Puducherry"]
submission = submission[submission["state"].isin(target_states)]

# Remove duplicates
submission = submission.drop_duplicates(subset=["state", "constituency"])

# Sort by state and constituency
submission = submission.sort_values(by=["state", "constituency"])

# Reset index for clean output
submission = submission.reset_index(drop=True)

# ========================================
# VALIDATION AND FINAL OUTPUT
# ========================================
print("\n" + "=" * 60)
print("FINAL SUBMISSION VALIDATION")
print("=" * 60 + "\n")

print(f"Total rows: {len(submission)}")
print(f"Expected: 823-824 rows")
print(f"Status: {'✓ PASS' if 823 <= len(submission) <= 824 else '✗ FAIL'}\n")

print("State distribution:")
state_counts = submission["state"].value_counts().sort_index()
for state, count in state_counts.items():
    print(f"  {state}: {count}")
print(f"Total states: {len(state_counts)} (expected: 5)")
print(f"Status: {'✓ PASS' if len(state_counts) == 5 else '✗ FAIL'}\n")

print("Missing values:")
missing = submission.isnull().sum()
for col, count in missing.items():
    if count > 0:
        print(f"  {col}: {count}")
if missing.sum() == 0:
    print("  None (all values present)")
print(f"Total missing: {missing.sum()} (expected: 0)")
print(f"Status: {'✓ PASS' if missing.sum() == 0 else '✗ FAIL'}\n")

# ========================================
# SAVE RESULTS
# ========================================
print("Saving submissions...")
submission.to_csv("outputs/final_submission.csv", index=False)
print("✓ Saved: outputs/final_submission.csv")

try:
    submission.to_excel("outputs/final_submission.xlsx", index=False)
    print("✓ Saved: outputs/final_submission.xlsx")
except PermissionError:
    print("⚠ Excel file is locked — saving as CSV only")
    print("  The CSV file (final_submission.csv) is ready for use")

print("\n" + "=" * 60)
print("SUBMISSION COMPLETE - READY FOR COMPETITION")
print("=" * 60 + "\n")