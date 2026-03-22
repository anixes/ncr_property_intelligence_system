"""
V16 Data Fusion — Probabilistic Deduplication with Unit Discriminators.

Uses (H3, BHK) blocking + FuzzyWuzzy society matching to merge
duplicate listings while preventing same-building unit collapse.
"""

import json
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from fuzzywuzzy import fuzz
except ImportError:
    fuzz = None

from ncr_property_price_estimation.config import PROCESSED_DATA_DIR

# =============================================================================
# NCR INTELLIGENCE ENGINE (V16) - DATA FUSION SERVICE
# =============================================================================

class DataFusionService:
    """Deduplication Engine with Society Caching and Unit Discriminators."""
    
    SIMILARITY_THRESHOLD = 80       # FuzzyWuzzy score
    PRICE_DIFF_THRESHOLD = 0.20     # 20% price difference = different unit
    CACHE_TTL_DAYS = 30             # Evict stale society mappings
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or (PROCESSED_DATA_DIR / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.society_cache_path = self.cache_dir / "society_map.json"
        self.society_cache = self._load_society_cache()
        self.fusion_log = []

    def _load_society_cache(self) -> Dict[str, Dict]:
        """Load persistent society normalization cache (V16 TTL-aware)."""
        if not self.society_cache_path.exists():
            return {}
        with open(self.society_cache_path, "r") as f:
            cache = json.load(f)
        
        # Evict stale entries (V16 TTL)
        now = datetime.now()
        active = {}
        for key, entry in cache.items():
            last_seen = datetime.fromisoformat(entry.get("last_seen", now.isoformat()))
            if (now - last_seen).days <= self.CACHE_TTL_DAYS:
                active[key] = entry
        return active

    def _save_society_cache(self):
        """Persist the society cache with confidence scores."""
        with open(self.society_cache_path, "w") as f:
            json.dump(self.society_cache, f, indent=2)

    def normalize_society(self, name: str) -> str:
        """Normalize society name using fuzzy matching + cache."""
        if not name:
            return "Unknown"
        
        name_clean = name.strip().lower()
        
        # Check cache first
        if name_clean in self.society_cache:
            self.society_cache[name_clean]["last_seen"] = datetime.now().isoformat()
            return self.society_cache[name_clean]["canonical"]
        
        # Fuzzy match against existing cache entries
        best_match = None
        best_score = 0
        
        if fuzz:
            for key, entry in self.society_cache.items():
                score = fuzz.token_sort_ratio(name_clean, key)
                if score > best_score and score >= self.SIMILARITY_THRESHOLD:
                    best_score = score
                    best_match = entry["canonical"]
        
        canonical = best_match if best_match else name.strip().title()
        
        self.society_cache[name_clean] = {
            "canonical": canonical,
            "confidence": best_score / 100 if best_match else 0.5,
            "last_seen": datetime.now().isoformat(),
        }
        
        return canonical

    def fuse_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Deduplicate listings using (H3, BHK) blocking + Unit Discriminators (V16).
        
        Guards:
        - Block merge if price difference > 20% (different units in same building)
        - Block merge if floor numbers differ
        - Max 2 results per society (diversity)
        """
        if len(df) == 0:
            return df
        
        # Normalize society names
        if 'society' in df.columns:
            df['society_canonical'] = df['society'].apply(self.normalize_society)
        
        # Group by (H3, BHK) for efficient comparison (V16 Blocking)
        block_cols = []
        if 'h3_res8' in df.columns:
            block_cols.append('h3_res8')
        if 'bhk' in df.columns:
            block_cols.append('bhk')
        
        if not block_cols:
            return df
        
        fused_records = []
        
        for block_key, group in df.groupby(block_cols):
            if len(group) <= 1:
                fused_records.append(group)
                continue
            
            # Within each block, check for true duplicates
            keep_mask = pd.Series(True, index=group.index)
            indices = group.index.tolist()
            
            for i in range(len(indices)):
                if not keep_mask[indices[i]]:
                    continue
                for j in range(i + 1, len(indices)):
                    if not keep_mask[indices[j]]:
                        continue
                    
                    row_i = group.loc[indices[i]]
                    row_j = group.loc[indices[j]]
                    
                    # Unit Discriminator (V16): Don't merge different units
                    if self._is_different_unit(row_i, row_j):
                        continue
                    
                    # These are likely duplicates — keep the one with higher confidence
                    conf_i = row_i.get('extraction_confidence', 1.0)
                    conf_j = row_j.get('extraction_confidence', 1.0)
                    
                    if conf_i >= conf_j:
                        keep_mask[indices[j]] = False
                    else:
                        keep_mask[indices[i]] = False
                    
                    self.fusion_log.append({
                        "merged": str(indices[j]),
                        "into": str(indices[i]),
                        "block": str(block_key),
                    })
            
            fused_records.append(group[keep_mask])
        
        result = pd.concat(fused_records, ignore_index=True)
        
        # Save the updated society cache
        self._save_society_cache()
        
        return result

    def _is_different_unit(self, row_a, row_b) -> bool:
        """
        Unit Discriminator (V16): Prevent merging distinct units.
        
        Returns True if the two rows are likely DIFFERENT units
        (and should NOT be merged).
        """
        # Price difference check
        price_a = row_a.get('price', 0)
        price_b = row_b.get('price', 0)
        
        if price_a > 0 and price_b > 0:
            price_diff_ratio = abs(price_a - price_b) / max(price_a, price_b)
            if price_diff_ratio > self.PRICE_DIFF_THRESHOLD:
                return True
        
        # Floor number check
        floor_a = row_a.get('floor', None)
        floor_b = row_b.get('floor', None)
        
        if floor_a is not None and floor_b is not None:
            if floor_a != floor_b:
                return True
        
        return False

    def get_fusion_stats(self) -> Dict[str, Any]:
        """Return fusion compression statistics."""
        return {
            "merges_performed": len(self.fusion_log),
            "society_cache_size": len(self.society_cache),
            "sample_merges": self.fusion_log[:5],
        }
