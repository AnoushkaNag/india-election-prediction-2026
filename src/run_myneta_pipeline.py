"""
Main runner for Myneta scraper pipeline.

Orchestrates:
1. Scraping Myneta for all states
2. Cleaning and validating data
3. Merging with predictions
4. Final output generation
"""

import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main pipeline execution.
    """
    logger.info("\n" + "="*70)
    logger.info("MYNETA SCRAPER PIPELINE - 2026 ELECTIONS")
    logger.info("="*70)
    
    start_time = time.time()
    
    try:
        # ============================================================
        # STEP 1: SCRAPE MYNETA
        # ============================================================
        logger.info("\n[STEP 1] Scraping Myneta.info for 2026 elections...")
        
        from myneta_scraper import scrape_all_states
        
        raw_df = scrape_all_states()
        
        if raw_df.empty:
            logger.error("❌ Scraping failed - no data collected")
            return False
        
        logger.info(f"✓ Scraped {len(raw_df)} candidate records")
        
        # ============================================================
        # STEP 2: CLEAN DATA
        # ============================================================
        logger.info("\n[STEP 2] Cleaning and validating scraped data...")
        
        from myneta_cleaner import clean_myneta_data, validate_myneta_data, save_cleaned_data
        
        clean_df = clean_myneta_data(raw_df)
        report = validate_myneta_data(clean_df)
        
        if report['missing_states']:
            logger.error(f"❌ Missing states in scraped data: {report['missing_states']}")
            # Don't fail - continue with what we have
        
        save_cleaned_data(clean_df)
        logger.info(f"✓ Cleaned data saved")
        
        # ============================================================
        # STEP 3: MERGE WITH PREDICTIONS
        # ============================================================
        logger.info("\n[STEP 3] Merging Myneta data with prediction model...")
        
        from merge_myneta import load_data, merge_candidates, validate_merged_data, save_merged_data
        
        predictions, myneta = load_data(
            'outputs/final_submission.csv',
            'outputs/myneta_candidates_cleaned.csv'
        )
        
        merged, unmatched = merge_candidates(predictions, myneta)
        merge_report = validate_merged_data(merged, unmatched)
        
        save_merged_data(merged)
        logger.info(f"✓ Merged data saved")
        
        # ============================================================
        # STEP 4: FINAL SUMMARY
        # ============================================================
        elapsed_time = time.time() - start_time
        
        logger.info("\n" + "="*70)
        logger.info("PIPELINE COMPLETE")
        logger.info("="*70)
        logger.info(f"\nTiming:")
        logger.info(f"  Total time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
        logger.info(f"\nOutput files:")
        logger.info(f"  ✓ outputs/myneta_candidates_cleaned.csv ({len(clean_df)} rows)")
        logger.info(f"  ✓ outputs/final_submission_2026.csv ({len(merged)} rows)")
        logger.info(f"\nValidation:")
        logger.info(f"  Scraping: {report['status']}")
        logger.info(f"  Merging: {merge_report['status']}")
        
        # Final checks
        all_pass = (report['status'] == 'PASS' and merge_report['status'] == 'PASS')
        
        if not all_pass:
            logger.warning(f"\n⚠️  Some warnings found - review above")
        
        if len(merged) == 824 and merge_report['checks'].get('row_count') == 'PASS':
            logger.info(f"\n✅ READY FOR SUBMISSION: 824 rows with candidate names")
        else:
            logger.warning(f"\n⚠️  Output has {len(merged)} rows (expected 824)")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error(f"   Ensure all required modules are in src/ directory")
        return False
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        logger.error(f"   Ensure outputs/final_submission.csv exists")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
