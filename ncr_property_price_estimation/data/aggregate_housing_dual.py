import json
import pandas as pd
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

def aggregate_dual_mode(raw_data_dir: str):
    """
    Scans JSON batch files and splits them into Sale and Rental RAW CSVs.
    """
    raw_path = Path(raw_data_dir)
    buy_records = []
    rent_records = []
    
    json_files = list(raw_path.rglob("*.json"))
    json_files = [f for f in json_files if "checkpoint" not in f.name]
    
    logger.info(f"📂 Scanning {len(json_files)} JSON batch files for Dual-Sorting...")
    
    for f in json_files:
        try:
            with open(f, 'r', encoding='utf-8') as jfile:
                batch = json.load(jfile)
                
                for record in batch.get('data', []):
                    # Basic sanity cleaning
                    if 'debug_html' in record: continue
                    
                    # 1. Determine Mode (Priority: record level -> batch level)
                    # Note: We prioritize the record's intrinsic field if it exists
                    ltype = record.get('listing_type', '').lower()
                    
                    if 'rent' in ltype:
                        rent_records.append(record)
                    else:
                        buy_records.append(record)
                        
        except Exception as e:
            logger.error(f"  ❌ Skipping {f.name}: {e}")

    # Save to dedicated CSVs
    output_dir = Path("d:/DATA SCIENCE/ncr_property_price_estimation/data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if buy_records:
        df_buy = pd.DataFrame(buy_records)
        df_buy.to_csv(output_dir / "raw_ncr_buy.csv", index=False, encoding='utf-8-sig')
        logger.info(f"✅ Created SALE dataset: {len(buy_records)} records -> raw_ncr_buy.csv")
        
    if rent_records:
        df_rent = pd.DataFrame(rent_records)
        df_rent.to_csv(output_dir / "raw_ncr_rent.csv", index=False, encoding='utf-8-sig')
        logger.info(f"✅ Created RENTAL dataset: {len(rent_records)} records -> raw_ncr_rent.csv")

if __name__ == "__main__":
    aggregate_dual_mode("d:/DATA SCIENCE/ncr_property_price_estimation/data/external")
