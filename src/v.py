import pandas as pd

# Load cleaned candidate data
df = pd.read_csv("candidates_cleaned.csv")

print("\n================ BASIC INFO ================\n")
print(df.head())
print("\nTotal rows:", len(df))

# ----------------------------------------
# 1. STATE-WISE COUNT CHECK
# ----------------------------------------

print("\n================ STATE COUNTS ================\n")

state_counts = df.groupby("state")["constituency"].nunique()
print(state_counts)

expected_counts = {
    "Kerala": 140,
    "Tamil Nadu": 234,
    "West Bengal": 294,
    "Assam": 126,
    "Puducherry": 30
}

print("\nChecking against expected values:\n")

for state, expected in expected_counts.items():
    actual = state_counts.get(state, 0)
    status = "✓" if actual == expected else "❌"
    print(f"{state}: {actual} (expected {expected}) {status}")

print(f"\nTOTAL EXPECTED: {sum(expected_counts.values())}")
print(f"TOTAL ACTUAL: {len(df)}")

# ----------------------------------------
# 2. DUPLICATE CHECK
# ----------------------------------------

print("\n================ DUPLICATES ================\n")

duplicates = df[df.duplicated(subset=["state", "constituency"], keep=False)]
print(f"Duplicate rows found: {len(duplicates)}")

if len(duplicates) > 0:
    print(duplicates.sort_values(["state", "constituency"]))

# ----------------------------------------
# 3. MISSING DATA CHECK
# ----------------------------------------

print("\n================ MISSING VALUES ================\n")

print("Missing candidates:", df["candidate"].isna().sum())
print("Missing parties:", df["party"].isna().sum())
print("Empty candidate strings:", (df["candidate"].str.strip() == "").sum())

# Show problematic rows
missing_rows = df[df["candidate"].str.strip() == ""]
if len(missing_rows) > 0:
    print("\nRows with missing candidate names:")
    print(missing_rows.head(10))

# ----------------------------------------
# 4. CONSTITUENCY NORMALIZATION
# ----------------------------------------

print("\n================ NORMALIZATION TEST ================\n")

def normalize(text):
    return str(text).strip().lower()\
        .replace(" (sc)", "")\
        .replace(" (st)", "")\
        .replace(".", "")\
        .replace(",", "")

df["constituency_clean"] = df["constituency"].apply(normalize)

# Check for collisions after cleaning
collision_check = df[df.duplicated(subset=["state", "constituency_clean"], keep=False)]

print(f"Post-normalization duplicates: {len(collision_check)}")

if len(collision_check) > 0:
    print(collision_check.sort_values(["state", "constituency_clean"]))

# ----------------------------------------
# 5. PARTY DISTRIBUTION (SANITY CHECK)
# ----------------------------------------

print("\n================ PARTY DISTRIBUTION ================\n")

print(df["party"].value_counts().head(20))

# ----------------------------------------
# 6. FINAL CLEAN DATA PREVIEW
# ----------------------------------------

print("\n================ FINAL SAMPLE ================\n")
print(df.sample(10))

print("\n================ VERIFICATION COMPLETE ================\n")