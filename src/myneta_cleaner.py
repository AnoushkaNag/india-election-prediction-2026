"""
Data cleaning and validation for Myneta scraper output.
"""

import pandas as pd
import logging
from typing import Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Expected counts for each state
EXPECTED_COUNTS = {
    'Kerala': 140,
    'Tamil Nadu': 234,
    'West Bengal': 294,
    'Assam': 126,
    'Puducherry': 30
}

# State name mapping
STATE_NAME_MAP = {
    'TamilNadu': 'Tamil Nadu',
    'WestBengal': 'West Bengal',
    'Kerala': 'Kerala',
    'Assam': 'Assam',
    'Puducherry': 'Puducherry'
}


def normalize_state_name(state: str) -> str:
    """Normalize state names to standard format."""
    if pd.isna(state):
        return ''
    
    state = str(state).strip()
    
    # Check mapping
    if state in STATE_NAME_MAP:
        return STATE_NAME_MAP[state]
    
    # Try to find best match
    for key, value in STATE_NAME_MAP.items():
        if key.lower() == state.lower() or value.lower() == state.lower():
            return value
    
    return state


def normalize_constituency(const: str) -> str:
    """Normalize constituency names."""
    if pd.isna(const):
        return ''
    
    const = str(const).strip()
    # Remove extra whitespace but preserve (SC), (ST) markers
    const = ' '.join(const.split())
    return const


def normalize_candidate(name: str) -> str:
    """Normalize candidate names."""
    if pd.isna(name):
        return ''
    
    name = str(name).strip()
    # Remove extra whitespace
    name = ' '.join(name.split())
    return name


def normalize_party(party: str) -> str:
    """Normalize party names."""
    if pd.isna(party):
        return 'Unknown'
    
    party = str(party).strip()
    if not party or party.lower() == 'unknown':
        return 'Unknown'
    
    return party


def clean_myneta_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate Myneta scraper data.
    
    Args:
        df: Raw DataFrame from scraper
        
    Returns:
        Cleaned DataFrame
    """
    logger.info(f"\nCleaning Myneta data...")
    logger.info(f"Input shape: {df.shape}")
    
    df = df.copy()
    
    # Remove rows with missing critical columns
    df = df.dropna(subset=['state', 'constituency', 'candidate_name', 'party'])
    logger.info(f"After removing missing values: {df.shape[0]} rows")
    
    # Normalize state names
    df['state'] = df['state'].apply(normalize_state_name)
    logger.info(f"After normalizing states: {df['state'].nunique()} unique states")
    
    # Normalize constituency names
    df['constituency'] = df['constituency'].apply(normalize_constituency)
    
    # Normalize candidate names
    df['candidate_name'] = df['candidate_name'].apply(normalize_candidate)
    
    # Normalize party names
    df['party'] = df['party'].apply(normalize_party)
    
    # Remove empty rows
    df = df[(df['state'] != '') & (df['constituency'] != '') & (df['candidate_name'] != '')]
    logger.info(f"After removing empty rows: {df.shape[0]} rows")
    
    # Remove duplicates, keeping first occurrence
    initial_count = len(df)
    df = df.drop_duplicates(subset=['state', 'constituency', 'candidate_name', 'party'], keep='first')
    removed_dups = initial_count - len(df)
    if removed_dups > 0:
        logger.info(f"Removed {removed_dups} duplicate records")
    
    # Sort for better readability
    df = df.sort_values(['state', 'constituency', 'candidate_name']).reset_index(drop=True)
    
    return df


def validate_myneta_data(df: pd.DataFrame) -> Dict:
    """
    Validate Myneta data against expected counts.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        Validation report dictionary
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"VALIDATION REPORT")
    logger.info(f"{'='*70}")
    
    report = {
        'total_rows': len(df),
        'state_counts': df['state'].value_counts().to_dict(),
        'status': 'PASS',
        'warnings': [],
        'missing_states': []
    }
    
    # Check each state
    for state, expected_count in EXPECTED_COUNTS.items():
        actual_count = len(df[df['state'] == state])
        
        if actual_count != expected_count:
            report['status'] = 'WARNING'
            report['warnings'].append(
                f"{state}: Expected {expected_count} constituencies, got {actual_count}"
            )
        
        if actual_count == 0:
            report['missing_states'].append(state)
        
        logger.info(f"{state:20s}: {actual_count:3d}/{expected_count:3d}")
    
    # Check for missing values
    missing_summary = df.isnull().sum()
    if missing_summary.sum() > 0:
        report['status'] = 'WARNING'
        report['warnings'].append(f"Found {missing_summary.sum()} missing values")
        logger.warning(f"Missing values:\n{missing_summary[missing_summary > 0]}")
    
    # Check for duplicates
    dup_count = df.duplicated(subset=['state', 'constituency', 'candidate_name']).sum()
    if dup_count > 0:
        report['status'] = 'WARNING'
        report['warnings'].append(f"Found {dup_count} duplicate records")
    
    # Log warnings
    if report['warnings']:
        logger.warning(f"\nWarnings found:")
        for warning in report['warnings']:
            logger.warning(f"  - {warning}")
    
    if report['missing_states']:
        logger.error(f"Missing states: {report['missing_states']}")
    
    logger.info(f"\nStatus: {report['status']}")
    
    return report


def save_cleaned_data(df: pd.DataFrame, output_path: str = 'outputs/myneta_candidates_cleaned.csv'):
    """
    Save cleaned data to CSV.
    
    Args:
        df: Cleaned DataFrame
        output_path: Path to save file
    """
    df.to_csv(output_path, index=False)
    logger.info(f"\n✓ Saved cleaned data to {output_path}")
    logger.info(f"  Rows: {len(df)}")
    logger.info(f"  Columns: {', '.join(df.columns)}")


if __name__ == '__main__':
    # Example usage
    from myneta_scraper import scrape_all_states
    
    # Scrape data
    raw_df = scrape_all_states()
    
    # Clean data
    clean_df = clean_myneta_data(raw_df)
    
    # Validate
    report = validate_myneta_data(clean_df)
    
    # Save
    save_cleaned_data(clean_df)
    
    print(f"\nFinal shape: {clean_df.shape}")
