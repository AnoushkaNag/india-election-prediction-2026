import pandas as pd

df = pd.read_csv("all_states_wiki_raw.csv")

def clean_row(row):
    col1, col2, col3, col4 = row["raw_col1"], row["raw_col2"], row["raw_col3"], row["raw_col4"]
    
    col1 = str(col1).strip() if pd.notna(col1) else ""
    col2 = str(col2).strip() if pd.notna(col2) else ""
    col3 = str(col3).strip() if pd.notna(col3) else ""
    col4 = str(col4).strip() if pd.notna(col4) else ""

    if col2:  # district header row — constituency is in col2
        constituency = col2
        party = col4  # party is in col4
        candidate = ""  # MISSING — will fill with party name as fallback
    else:  # normal row
        constituency = col1
        party = col3
        candidate = col4

    return pd.Series({
        "state": row["state"],
        "constituency": constituency,
        "party": party,
        "candidate": candidate if candidate else f"[{party} candidate]"
    })

cleaned = df.apply(clean_row, axis=1)

# Drop rows with no party (the empty duplicate rows)
cleaned = cleaned[cleaned["party"].str.strip() != ""]
cleaned = cleaned[cleaned["constituency"].str.strip() != ""]

# Drop duplicates — keep first occurrence per state+constituency
cleaned = cleaned.drop_duplicates(subset=["state", "constituency"], keep="first")

# Summary
print(cleaned.groupby("state")["constituency"].count())
print(f"\nTotal constituencies: {len(cleaned)}")
print(cleaned.head(20).to_string())

cleaned.to_csv("candidates_cleaned.csv", index=False)
print("\nSaved to candidates_cleaned.csv")