from typing import Any

import numpy as np


class RiskEngine:
    @staticmethod
    def calculate_risk_score(
        predicted_price: float,
        reference_median: float,
        geo_confidence: float = 1.0,
        intent: str = "buy",
    ) -> dict[str, Any]:
        """
        Detect over/under-pricing vs. the locality reference median.
        """
        if reference_median <= 0 or np.isnan(reference_median):
            return {"score": 50, "label": "Unknown (Low Data)"}

        # Z-Score relative to micro-market median
        z_score = (predicted_price - reference_median) / (reference_median + 1e-9)

        # Risk score: 50 = fair value baseline ± z-score scaled to 0-100
        base_score = 50 + (z_score * 50)
        final_score = float(np.clip(base_score, 0, 100))

        if intent == "rent":
            if final_score < 35:
                label = "High Affordability"
            elif final_score < 65:
                label = "Market Standard"
            elif final_score < 85:
                label = "Premium Utility"
            else:
                label = "Inflated / Low Value"
        else:
            if final_score < 35:
                label = "Value Pick"
            elif final_score < 65:
                label = "Fair Value"
            elif final_score < 85:
                label = "Premium Area"
            else:
                label = "High Risk / Overvalued"

        return {"score": round(final_score, 1), "label": label}
