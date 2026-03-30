"""
V16 Recommendation Engine — H3-Based Similarity with Diversity Constraints.

Finds comparable properties using spatial proximity, feature similarity,
and undervaluation scoring with confidence weighting.
"""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# =============================================================================
# NCR INTELLIGENCE ENGINE (V16) - RECOMMENDER SERVICE
# =============================================================================


class RecommenderService:
    """H3-Proximity Recommender with Diversity and Confidence-Weighted Deals."""

    MAX_PER_SOCIETY = 2  # Diversity constraint
    PRICE_BAND_THRESHOLD = 0.30  # Only compare within 30% price range
    EPSILON = 1e-6  # Stability guard

    SIMILARITY_FEATURES = ["area", "bhk", "price_per_sqft"]

    def __init__(self):
        self.scaler = StandardScaler()

    def find_similar(
        self,
        target: pd.Series,
        dataset: pd.DataFrame,
        top_k: int = 5,
        model_uncertainty: float = None,
    ) -> pd.DataFrame:
        """
        Find top-K comparable properties with diversity and deal scoring (V16).

        Steps:
        1. H3 Proximity Filter (k-ring=1)
        2. Price Band Filter (30%)
        3. Cosine Similarity on normalized features
        4. Diversity Constraint (max 2 per society)
        5. Deal Scoring with confidence weighting
        """
        if len(dataset) == 0:
            return pd.DataFrame()

        # 1. Spatial Filter — H3 Neighbors (k=1)
        candidates = self._filter_h3_neighbors(target, dataset)

        if len(candidates) == 0:
            # Fallback: use city-level if H3 is too sparse
            candidates = dataset[dataset.get("city", "") == target.get("city", "")].copy()

        if len(candidates) == 0:
            return pd.DataFrame()

        # 2. Price Band Filter (V16)
        target_price = target.get("price", 0)
        if target_price > 0:
            candidates = candidates[
                (candidates["price"] / target_price).between(
                    1 - self.PRICE_BAND_THRESHOLD, 1 + self.PRICE_BAND_THRESHOLD
                )
            ].copy()

        if len(candidates) == 0:
            return pd.DataFrame()

        # 3. Cosine Similarity on normalized features
        available_features = [
            f for f in self.SIMILARITY_FEATURES if f in candidates.columns and f in target.index
        ]

        if not available_features:
            return candidates.head(top_k)

        feature_matrix = candidates[available_features].fillna(0).values
        target_vector = target[available_features].fillna(0).values.reshape(1, -1)

        # Normalize (V16: prevents area from dominating)
        all_vectors = np.vstack([feature_matrix, target_vector])
        if len(all_vectors) > 1:
            self.scaler.fit(all_vectors)
            feature_matrix_scaled = self.scaler.transform(feature_matrix)
            target_scaled = self.scaler.transform(target_vector)
        else:
            feature_matrix_scaled = feature_matrix
            target_scaled = target_vector

        # Cosine similarity
        dot_products = np.dot(feature_matrix_scaled, target_scaled.T).flatten()
        norms_a = np.linalg.norm(feature_matrix_scaled, axis=1)
        norm_b = np.linalg.norm(target_scaled)

        similarities = dot_products / (norms_a * norm_b + self.EPSILON)
        candidates = candidates.copy()
        candidates["similarity_score"] = similarities

        # 4. Rank Stability (V16): stable sort to prevent jitter
        candidates = candidates.sort_values("similarity_score", ascending=False, kind="mergesort")

        # 5. Diversity Constraint (V16): max 2 per society
        if "society" in candidates.columns:
            diverse = []
            society_counts = {}
            for _, row in candidates.iterrows():
                soc = row.get("society", "Unknown")
                count = society_counts.get(soc, 0)
                if count < self.MAX_PER_SOCIETY:
                    diverse.append(row)
                    society_counts[soc] = count + 1
                if len(diverse) >= top_k * 2:  # Collect extra for deal scoring
                    break
            candidates = pd.DataFrame(diverse)

        # 6. Deal Scoring (V16 Confidence-Weighted)
        candidates = self._score_deals(candidates, model_uncertainty)

        return candidates.head(top_k)

    def _filter_h3_neighbors(self, target: pd.Series, dataset: pd.DataFrame) -> pd.DataFrame:
        """Filter dataset to listings within H3 k-ring=1 of target."""
        target_h3 = target.get("h3_res8", None)

        if not target_h3 or "h3_res8" not in dataset.columns:
            return dataset.copy()

        try:
            import h3

            neighbors = h3.k_ring(target_h3, 1)
            return dataset[dataset["h3_res8"].isin(neighbors)].copy()
        except ImportError:
            return dataset[dataset["h3_res8"] == target_h3].copy()

    def _score_deals(self, df: pd.DataFrame, model_uncertainty: float = None) -> pd.DataFrame:
        """
        Confidence-Weighted Deal Scoring (V16).

        deal_score = undervaluation / (uncertainty + epsilon)

        Strong Deal: > 0.15
        """
        if "predicted_price" not in df.columns or "price" not in df.columns:
            df["deal_score"] = 0.0
            df["is_strong_deal"] = False
            return df

        df = df.copy()
        undervaluation = (df["predicted_price"] - df["price"]) / (
            df["predicted_price"] + self.EPSILON
        )

        uncertainty = (
            model_uncertainty if model_uncertainty else df.get("prediction_uncertainty", 0.1)
        )
        if isinstance(uncertainty, (int, float)):
            uncertainty = max(uncertainty, self.EPSILON)

        df["deal_score"] = undervaluation / (uncertainty + self.EPSILON)
        df["is_strong_deal"] = df["deal_score"] > 0.15

        return df

    def explain_recommendation(self, target: pd.Series, comparable: pd.Series) -> dict[str, Any]:
        """
        Generate "Why" explanation for a recommendation (V16 XAI).

        Compares structural, spatial, and amenity differences.
        """
        explanations = []

        # Area comparison
        if "area" in target.index and "area" in comparable.index:
            area_diff = (comparable["area"] - target["area"]) / target["area"] * 100
            if abs(area_diff) > 5:
                direction = "larger" if area_diff > 0 else "smaller"
                explanations.append(
                    f"Area is {abs(area_diff):.1f}% {direction} ({comparable['area']:.0f} vs {target['area']:.0f} sqft)"
                )

        # Price comparison
        if "price" in target.index and "price" in comparable.index:
            price_diff = (comparable["price"] - target["price"]) / target["price"] * 100
            if abs(price_diff) > 5:
                direction = "higher" if price_diff > 0 else "lower"
                explanations.append(f"Price is {abs(price_diff):.1f}% {direction}")

        # H3 proximity
        if "h3_res8" in target.index and "h3_res8" in comparable.index:
            if target["h3_res8"] == comparable["h3_res8"]:
                explanations.append("Same H3 hexagonal zone (very close)")
            else:
                explanations.append("Adjacent H3 zone (nearby)")

        # Deal quality
        deal_score = comparable.get("deal_score", 0)
        if deal_score > 0.15:
            explanations.append(f"🔥 Strong Deal (score: {deal_score:.2f})")
        elif deal_score > 0:
            explanations.append(f"Fair Deal (score: {deal_score:.2f})")

        return {
            "similarity_score": comparable.get("similarity_score", 0),
            "explanations": explanations,
        }
