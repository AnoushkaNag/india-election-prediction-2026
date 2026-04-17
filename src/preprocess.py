import pandas as pd
import os
import logging
from pathlib import Path

# =========================
# LOGGING SETUP
# =========================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# CONFIG
# =========================

FILES = [
    # Kerala
    ("../data/raw/kerala_detailed.xlsx", "Kerala", 2021, "target"),
    ("../data/raw/kerala_2016_detailed.xlsx", "Kerala", 2016, "target"),

    # Tamil Nadu
    ("../data/raw/tamilnadu_detailed.xlsx", "Tamil Nadu", 2021, "target"),
    ("../data/raw/tamilnadu_2016_detailed.xlsx", "Tamil Nadu", 2016, "target"),

    # Assam
    ("../data/raw/assam_detailed.xlsx", "Assam", 2021, "target"),
    ("../data/raw/Assam_2016_detailed.xlsx", "Assam", 2016, "target"),

    # West Bengal
    ("../data/raw/wb_detailed.xlsx", "West Bengal", 2021, "target"),
    ("../data/raw/westbengal_2016_detailed.xlsx", "West Bengal", 2016, "target"),

    # Puducherry
    ("../data/raw/puducherry_detailed.xlsx", "Puducherry", 2021, "target"),
    ("../data/raw/Puducherry_2016_detailed.xlsx", "Puducherry", 2016, "target"),

    # Extra states (2021 only)
    ("../data/raw/andhra_pradesh_detailed.xlsx", "Andhra Pradesh", 2021, "extra"),
    ("../data/raw/odisha_detailed.xlsx", "Odisha", 2021, "extra"),
    ("../data/raw/delhi_detailed.xlsx", "Delhi", 2021, "extra"),
    ("../data/raw/jharkhand_detailed.xlsx", "Jharkhand", 2021, "extra"),
]

# =========================
# HELPER FUNCTIONS
# =========================

def standardize_columns(df):
    """Normalize column names: lowercase, strip whitespace, replace spaces with underscores."""
    # Convert column names to string first to handle numeric column names (e.g., from 2016 data)
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
    return df

def find_column(df, keywords):
    """
    Flexibly find a column containing any of the keywords.
    
    Args:
        df: DataFrame with standardized column names
        keywords: List of keywords to search for
        
    Returns:
        Column name if found, None otherwise
    """
    cols = df.columns
    for keyword in keywords:
        matching = [c for c in cols if keyword in c]
        if matching:
            return matching[0]
    return None

def detect_columns(df, state_name, debug=False):
    """
    Detect relevant columns with graceful fallback handling.
    ECI format: STATE/UT NAME, AC NAME, CANDIDATE NAME, PARTY, TOTAL (votes)
    
    Args:
        df: DataFrame with ECI election data
        state_name: State name for logging
        debug: If True, print first few rows if detection fails
        
    Returns:
        Tuple of (constituency_col, party_col, votes_col, df) or (None, None, None, df) if detection fails
    """
    df = standardize_columns(df)
    
    # Try multiple keyword variations (ECI format uses specific names)
    constituency_keywords = ['ac_name', 'ac_no', 'constituency', 'parliamentary', 'const']
    party_keywords = ['party', 'political_party']
    votes_keywords = ['total', 'votes']
    
    constituency_col = find_column(df, constituency_keywords)
    party_col = find_column(df, party_keywords)
    votes_col = find_column(df, votes_keywords)
    
    # Log detection results
    if all([constituency_col, party_col, votes_col]):
        logger.info(f"{state_name}: Detected columns - constituency: {constituency_col}, party: {party_col}, votes: {votes_col}")
    else:
        logger.warning(f"{state_name}: Failed to detect some columns")
        logger.warning(f"  Available columns: {list(df.columns)}")
        if not constituency_col:
            logger.warning(f"  Could not find constituency column (tried: {constituency_keywords})")
        if not party_col:
            logger.warning(f"  Could not find party column (tried: {party_keywords})")
        if not votes_col:
            logger.warning(f"  Could not find votes column (tried: {votes_keywords})")
        
        # Debug: Show first few rows if detection fails
        if debug and len(df) > 0:
            logger.debug(f"  First few rows of data:")
            for idx, row in df.head(2).iterrows():
                logger.debug(f"    Row {idx}: {dict(row)}")
    
    return constituency_col, party_col, votes_col, df

# =========================
# CORE LOGIC
# =========================

def extract_top2(df, state_name, year, data_type):
    """
    Extract top 2 candidates per constituency.
    Handles NaN values, type conversions, and invalid data gracefully.
    
    Args:
        df: Raw DataFrame from Excel file
        state_name: State name
        year: Election year
        data_type: 'target' or 'extra'
        
    Returns:
        DataFrame with top 2 candidates and vote counts per constituency
    """
    constituency_col, party_col, votes_col, df = detect_columns(df, state_name, debug=True)
    
    # Graceful handling of missing columns
    if not all([constituency_col, party_col, votes_col]):
        logger.error(f"Skipping {state_name}: Could not detect all required columns")
        return pd.DataFrame()
    
    # Ensure text columns are strings (handle NaN properly)
    try:
        df[constituency_col] = df[constituency_col].astype(str).str.strip()
        df[party_col] = df[party_col].astype(str).str.strip()
        # Remove rows with NaN or 'nan' values in critical columns
        df = df[df[constituency_col] != 'nan']
        df = df[df[party_col] != 'nan']
        df = df[df[constituency_col].notna()]
        df = df[df[party_col].notna()]
    except Exception as e:
        logger.warning(f"Error converting text columns for {state_name}: {e}")
    
    results = []
    
    # Group by constituency
    try:
        grouped = df.groupby(constituency_col, as_index=False)
    except Exception as e:
        logger.error(f"Failed to group by constituency for {state_name}: {e}")
        return pd.DataFrame()
    
    for const, group in grouped:
        # Skip rows with NaN values
        group = group.dropna(subset=[votes_col])
        
        if len(group) == 0:
            continue
        
        # Sort by votes in descending order
        try:
            # Convert votes to numeric first
            group[votes_col] = pd.to_numeric(group[votes_col], errors='coerce')
            group = group.sort_values(by=votes_col, ascending=False, na_position='last')
        except Exception as e:
            logger.warning(f"Failed to sort votes for {state_name}/{const}: {e}")
            continue
        
        # Skip constituencies with less than 2 candidates
        if len(group) < 2:
            logger.debug(f"Skipping {state_name}/{const}: Less than 2 candidates")
            continue
        
        try:
            winner = group.iloc[0]
            runner = group.iloc[1]
            
            # Safely convert votes to integers
            winner_votes = pd.to_numeric(winner[votes_col], errors='coerce')
            runner_votes = pd.to_numeric(runner[votes_col], errors='coerce')
            
            # Skip if vote conversion failed or values are NaN
            if pd.isna(winner_votes) or pd.isna(runner_votes):
                logger.debug(f"Invalid vote counts for {state_name}/{const}: winner={winner_votes}, runner={runner_votes}")
                continue
            
            # Convert to int
            winner_votes = int(winner_votes)
            runner_votes = int(runner_votes)
            
            # Skip if either vote count is 0
            if winner_votes <= 0 or runner_votes <= 0:
                logger.debug(f"Skipping {state_name}/{const}: Zero or negative votes")
                continue
            
            results.append({
                "year": year,
                "state": state_name,
                "constituency": const,
                "winner_party": str(winner[party_col]).strip(),
                "runner_up_party": str(runner[party_col]).strip(),
                "winner_votes": winner_votes,
                "runner_up_votes": runner_votes,
                "vote_margin": winner_votes - runner_votes,
                "total_votes": winner_votes + runner_votes,
                "vote_share_winner": round(100 * winner_votes / (winner_votes + runner_votes), 2) if (winner_votes + runner_votes) > 0 else 0,
                "vote_share_runner": round(100 * runner_votes / (winner_votes + runner_votes), 2) if (winner_votes + runner_votes) > 0 else 0,
                "data_type": data_type
            })
        except Exception as e:
            logger.debug(f"Error processing {state_name}/{const}: {e}")
            continue
    
    result_df = pd.DataFrame(results)
    logger.info(f"{state_name}: Extracted {len(result_df)} constituencies")
    
    return result_df

# =========================
# MAIN PIPELINE
# =========================

def process_all():
    """
    Main pipeline: Load all Excel files, process them, and generate clean dataset.
    """
    logger.info("=" * 60)
    logger.info("Starting preprocessing pipeline...")
    logger.info("=" * 60)
    
    all_data = []
    processed_states = []
    failed_states = []

    for path, state, year, dtype in FILES:
        # Convert relative path to absolute path
        abs_path = os.path.join(os.path.dirname(__file__), path)
        
        if not os.path.exists(abs_path):
            logger.error(f"File not found: {abs_path}")
            failed_states.append((state, year, "File not found"))
            continue

        logger.info(f"\nProcessing {state} {year} ({dtype})...")

        # Try multiple header row values
        df = None
        headers_to_try = [3, 2, 1, 0]
        
        for header_row in headers_to_try:
            try:
                df = pd.read_excel(abs_path, sheet_name=0, header=header_row)
                logger.info(f"  Loaded {len(df)} rows from Excel (header at row {header_row})")
                
                # Try to process with this header
                processed = extract_top2(df, state, year, dtype)
                
                if not processed.empty:
                    all_data.append(processed)
                    processed_states.append((state, year))
                    logger.info(f"  ✓ Successfully processed {state} {year} (header at row {header_row})")
                    df = None  # Mark as successful
                    break
                else:
                    # This header didn't work, try next
                    logger.debug(f"  Header row {header_row}: No data extracted, trying next...")
                    continue
                    
            except Exception as e:
                logger.debug(f"  Header row {header_row}: Error - {e}")
                continue
        
        # If no header worked, record failure
        if df is not None or all([len(all_data) == 0 or processed_states[-1] != (state, year)]):
            # Check if this was actually added to processed states
            if (state, year) not in processed_states:
                logger.warning(f"  ✗ No data extracted from {state} {year}")
                failed_states.append((state, year, "No valid header found or no data extracted"))

    # Generate output
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Successfully processed: {len(processed_states)}/{len(FILES)}")
    for state, year in processed_states:
        logger.info(f"  ✓ {state} {year}")
    
    if failed_states:
        logger.warning(f"\nFailed to process: {len(failed_states)} files")
        for state, year, reason in failed_states:
            logger.warning(f"  ✗ {state} {year}: {reason}")

    if len(all_data) == 0:
        logger.error("No data processed! Pipeline halted.")
        return

    # Combine all data
    final_df = pd.concat(all_data, ignore_index=True)
    
    logger.info(f"\nFinal dataset: {len(final_df)} rows across {len(processed_states)} states")
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "../data/processed")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as CSV
    output_csv = os.path.join(output_dir, "final_dataset.csv")
    final_df.to_csv(output_csv, index=False)
    logger.info(f"\n✓ Saved CSV: {output_csv}")
    
    # Save as Excel with multiple sheets (one per data type)
    output_excel = os.path.join(output_dir, "final_dataset.xlsx")
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        final_df.to_excel(writer, sheet_name='All Data', index=False)
        
        # Create separate sheets for target and extra data
        if 'target' in final_df['data_type'].values:
            target_df = final_df[final_df['data_type'] == 'target']
            target_df.to_excel(writer, sheet_name='Target States', index=False)
        
        if 'extra' in final_df['data_type'].values:
            extra_df = final_df[final_df['data_type'] == 'extra']
            extra_df.to_excel(writer, sheet_name='Extra States', index=False)
    
    logger.info(f"✓ Saved Excel: {output_excel}")
    
    # Display summary statistics
    logger.info("\n" + "=" * 60)
    logger.info("DATASET STATISTICS")
    logger.info("=" * 60)
    logger.info(f"Total constituencies: {len(final_df)}")
    logger.info(f"States covered: {final_df['state'].nunique()}")
    logger.info(f"\nAverage votes per constituency:")
    logger.info(final_df[['state', 'total_votes']].groupby('state')['total_votes'].mean().round(0))
    logger.info(f"\nVote share distribution:")
    logger.info(f"  Min: {final_df['vote_share_winner'].min():.2f}%")
    logger.info(f"  Max: {final_df['vote_share_winner'].max():.2f}%")
    logger.info(f"  Mean: {final_df['vote_share_winner'].mean():.2f}%")
    
    logger.info("\nFirst few rows:")
    logger.info(final_df.head())
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ Preprocessing pipeline completed successfully!")
    logger.info("=" * 60)

# =========================

if __name__ == "__main__":
    process_all()