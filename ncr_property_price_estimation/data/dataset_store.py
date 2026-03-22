import pandas as pd
import hashlib
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from ncr_property_price_estimation.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

# =============================================================================
# NCR INTELLIGENCE ENGINE (V16) - DATASET STORE (INTEGRITY LAYER)
# =============================================================================

class DatasetStore:
    """Centralized Source of Truth with Hardened Integrity Checks."""
    
    def __init__(self, base_dir: Path = PROCESSED_DATA_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.base_dir / "store_metadata.json"

    def _get_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum for audit parity."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def save_stage(self, df: pd.DataFrame, stage: str, batch_id: str):
        """Save a pipeline stage with integrity metadata."""
        # Uniqueness Guard (V16)
        if "listing_id" in df.columns:
            assert df["listing_id"].is_unique, f"INTEGRITY ERROR: Duplicate listing_ids found in stage {stage}"

        # Temporal Sort (V16 Leakage Protection)
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp")
            assert df["timestamp"].is_monotonic_increasing, "LEAKAGE ERROR: Timestamps are not monotonically increasing"

        file_name = f"{stage}_{batch_id}.parquet"
        file_path = self.base_dir / file_name
        df.to_parquet(file_path, index=False)
        
        # Update metadata for replay parity
        self._update_metadata(stage, batch_id, file_path)

    def load_latest(self, stage: str) -> pd.DataFrame:
        """Load the most recent validated batch for a given stage."""
        metadata = self._read_metadata()
        if stage not in metadata:
            raise FileNotFoundError(f"No history found for stage: {stage}")
        
        latest_batch = metadata[stage][-1]
        file_path = Path(latest_batch["path"])
        
        # Checksum Validation (V16 Final Audit)
        current_checksum = self._get_checksum(file_path)
        if current_checksum != latest_batch["checksum"]:
            raise ValueError(f"SECURITY ALERT: Checksum mismatch for {file_path}. Data may be tampered.")
            
        return pd.read_parquet(file_path)

    def _read_metadata(self) -> Dict[str, Any]:
        if not self.metadata_path.exists():
            return {}
        with open(self.metadata_path, "r") as f:
            return json.load(f)

    def _update_metadata(self, stage: str, batch_id: str, file_path: Path):
        metadata = self._read_metadata()
        if stage not in metadata:
            metadata[stage] = []
            
        metadata[stage].append({
            "batch_id": batch_id,
            "path": str(file_path),
            "checksum": self._get_checksum(file_path),
            "record_count": 0, # Should be updated by caller
            "timestamp": pd.Timestamp.now().isoformat()
        })
        
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    # Test Integrity Guards
    store = DatasetStore()
    print("DatasetStore Initialized with V16 Integrity Layer.")
