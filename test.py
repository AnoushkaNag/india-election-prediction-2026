import pandas as pd

sub = pd.read_csv("outputs/final_submission.csv")

print("Before:", len(sub))

# Remove duplicates PROPERLY
sub = sub.drop_duplicates(subset=["state", "constituency"], keep="first")

print("After removing duplicates:", len(sub))

sub.to_csv("outputs/final_submission.csv", index=False)