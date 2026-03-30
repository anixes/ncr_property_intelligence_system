"""
Product Interface — Unified CLI for the NCR Intelligence Engine.

Orchestrates the full lifecycle: Scrape → Process → Predict → Recommend.
Supports three modes: predict, recommend, analyze.
"""

import argparse
import json

import numpy as np
import pandas as pd

from ncr_property_price_estimation.config import MODELS_DIR, PROCESSED_DATA_DIR

# =============================================================================
# NCR INTELLIGENCE ENGINE - PRODUCT CLI
# =============================================================================

TIMEOUT_SECONDS = 30  # Latency guard for live scraping


class TimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutError("Scraping exceeded 30-second latency budget.")


class ProductEngine:
    """Unified orchestration layer for the NCR Intelligence Engine."""

    def __init__(self):
        self.model = None
        self.dataset = None
        self._load_model()
        self._load_dataset()

    def _load_model(self):
        """Load the trained Pure ML model from disk."""
        try:
            import joblib

            # Standardized on Sales pipeline for the unified CLI
            model_path = MODELS_DIR / "sales" / "pipeline_sales.joblib"
            if model_path.exists():
                self.model = joblib.load(model_path)
                print(f"✅ Pure ML Model loaded from {model_path}")
            else:
                print(f"⚠️  No trained model found at {model_path}. Run training first.")
        except Exception as e:
            print(f"⚠️  Model load failed: {e}")

    def _load_dataset(self):
        """Load the latest processed dataset for recommendations."""
        try:
            # Look for the latest parquet in processed/
            parquet_files = list(PROCESSED_DATA_DIR.glob("*.parquet"))
            if parquet_files:
                latest = max(parquet_files, key=lambda p: p.stat().st_mtime)
                self.dataset = pd.read_parquet(latest)
                print(f"✅ Dataset loaded: {len(self.dataset)} records from {latest.name}")
            else:
                # Fallback to CSV
                csv_files = list(PROCESSED_DATA_DIR.glob("*.csv"))
                if csv_files:
                    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
                    self.dataset = pd.read_csv(latest)
                    print(f"✅ Dataset loaded: {len(self.dataset)} records from {latest.name}")
                else:
                    print("⚠️  No processed dataset found. Run ingestion + processing first.")
        except Exception as e:
            print(f"⚠️  Dataset load failed: {e}")

    def predict(self, properties: dict) -> dict:
        """Predict price for a single property."""
        if self.model is None:
            return {"error": "No model loaded. Train first."}

        df = pd.DataFrame([properties])

        try:
            pred_log = self.model.predict(df)
            pred = np.expm1(pred_log)

            price_sqft = float(pred[0])
            area = properties.get("area", 1)

            return {
                "price_per_sqft": round(price_sqft, 2),
                "estimated_total_price": round(price_sqft * area, 2),
                "currency": "INR",
            }
        except Exception as e:
            return {"error": str(e)}

    def recommend(self, listing_id: str = None, properties: dict = None, top_k: int = 5) -> list:
        """Find similar properties from the dataset."""
        if self.dataset is None:
            return [{"error": "No dataset loaded."}]

        from ncr_property_price_estimation.modeling.recommender import RecommenderService

        recommender = RecommenderService()

        if listing_id and "listing_id" in self.dataset.columns:
            target_row = self.dataset[self.dataset["listing_id"] == listing_id]
            if len(target_row) == 0:
                return [{"error": f"Listing {listing_id} not found."}]
            target = target_row.iloc[0]
        elif properties:
            target = pd.Series(properties)
        else:
            return [{"error": "Provide listing_id or properties."}]

        similar = recommender.find_similar(target, self.dataset, top_k=top_k)

        results = []
        for _, row in similar.iterrows():
            explanation = recommender.explain_recommendation(target, row)
            results.append(
                {
                    "listing_id": row.get("listing_id", "N/A"),
                    "price": row.get("price", 0),
                    "area": row.get("area", 0),
                    "bhk": row.get("bhk", 0),
                    "society": row.get("society", "N/A"),
                    "similarity": round(row.get("similarity_score", 0), 3),
                    "deal_score": round(row.get("deal_score", 0), 3),
                    "is_strong_deal": bool(row.get("is_strong_deal", False)),
                    "why": explanation["explanations"],
                }
            )

        return results

    def analyze(self, properties: dict, top_k: int = 5) -> dict:
        """
        Unified Analysis Mode.

        Performs: Predict → Find Similar → Score Deals → Explain Why.

        Output:
        - Predicted price
        - Similar listings with explanations
        - Deal quality assessment
        """
        print("\n" + "=" * 60)
        print("🏠 NCR REAL ESTATE INTELLIGENCE ENGINE")
        print("=" * 60)

        # 1. Predict
        prediction = self.predict(properties)

        print("\n📊 PREDICTION:")
        print(f"   Predicted Price/sqft: ₹{prediction.get('price_per_sqft', 'N/A'):,.2f}")
        print(f"   Estimated Total:      ₹{prediction.get('estimated_total_price', 'N/A'):,.2f}")

        # 2. Find Similar
        similar = self.recommend(properties=properties, top_k=top_k)

        print(f"\n🔍 TOP {len(similar)} COMPARABLE PROPERTIES:")
        print("-" * 50)

        for i, rec in enumerate(similar, 1):
            deal_icon = "🔥" if rec.get("is_strong_deal") else "  "
            print(
                f"   {deal_icon} #{i} | {rec['society']} | {rec['bhk']}BHK | ₹{rec['price']:,.0f} | Score: {rec['similarity']}"
            )
            if rec["why"]:
                for reason in rec["why"]:
                    print(f"      → {reason}")

        # 3. Deal Assessment
        actual_price = properties.get("price", 0)
        predicted = prediction.get("estimated_total_price", 0)

        if actual_price > 0 and predicted > 0:
            underval = (predicted - actual_price) / predicted * 100
            print("\n💰 DEAL ASSESSMENT:")
            print(f"   Listed Price:    ₹{actual_price:,.0f}")
            print(f"   Predicted Value: ₹{predicted:,.0f}")
            if underval > 15:
                print(f"   Verdict:         🔥 STRONG DEAL ({underval:.1f}% below predicted)")
            elif underval > 5:
                print(f"   Verdict:         ✅ Fair Deal ({underval:.1f}% below predicted)")
            elif underval > -5:
                print("   Verdict:         ➡️  Fair Price (within 5% of predicted)")
            else:
                print(f"   Verdict:         ⚠️  Overpriced ({abs(underval):.1f}% above predicted)")

        print("\n" + "=" * 60)

        return {
            "prediction": prediction,
            "comparables": similar,
            "deal_assessment": {
                "listed_price": actual_price,
                "predicted_value": predicted,
                "undervaluation_pct": round(underval, 2)
                if actual_price > 0 and predicted > 0
                else None,
            },
        }


def main():
    parser = argparse.ArgumentParser(
        description="NCR Real Estate Intelligence Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Predict price for a 3BHK in Gurugram
  python product.py --mode predict --area 1200 --bhk 3 --city Gurugram --sector "Sector 50"
  
  # Full analysis with comparables and deal scoring
  python product.py --mode analyze --area 1500 --bhk 3 --city Noida --sector "Sector 150" --price 8500000
  
  # Find similar properties
  python product.py --mode recommend --area 1200 --bhk 2 --city Gurugram --sector "Sector 49"
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["predict", "recommend", "analyze"],
        default="analyze",
        help="Engine mode: predict, recommend, or analyze (default: analyze)",
    )
    parser.add_argument("--area", type=float, required=True, help="Area in sqft")
    parser.add_argument("--bhk", "--bedrooms", type=int, required=True, help="Number of bedrooms")
    parser.add_argument("--city", type=str, required=True, help="City (e.g., Gurugram, Noida)")
    parser.add_argument("--sector", type=str, required=True, help="Sector/Locality name")
    parser.add_argument("--price", type=float, default=0, help="Listed price (for deal scoring)")
    parser.add_argument("--bathrooms", type=int, default=None)
    parser.add_argument("--floor", type=int, default=None)
    parser.add_argument("--prop_type", type=str, default="Apartment")
    parser.add_argument("--furnished", type=str, default="Unknown")
    parser.add_argument("--facing", type=str, default="Unknown")
    parser.add_argument("--top_k", type=int, default=5, help="Number of recommendations")

    args = parser.parse_args()

    properties = {
        "area": args.area,
        "bedrooms": args.bhk,
        "bathrooms": args.bathrooms,
        "balcony": 0,
        "floor": args.floor,
        "prop_type": args.prop_type,
        "furnished": args.furnished,
        "facing": args.facing,
        "city": args.city,
        "sector": args.sector,
        "price": args.price,
        "bhk": args.bhk,
        "pooja_room": 0,
        "servant_room": 0,
        "store_room": 0,
        "pool": 0,
        "gym": 0,
        "lift": 0,
        "parking": 0,
        "vastu_compliant": 0,
    }

    engine = ProductEngine()

    if args.mode == "predict":
        result = engine.predict(properties)
        print(json.dumps(result, indent=2))
    elif args.mode == "recommend":
        results = engine.recommend(properties=properties, top_k=args.top_k)
        print(json.dumps(results, indent=2, default=str))
    elif args.mode == "analyze":
        engine.analyze(properties, top_k=args.top_k)


if __name__ == "__main__":
    main()
