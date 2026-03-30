class ScoringEngine:
    @staticmethod
    def calculate_unified_score(
        yield_pct: float,
        overvaluation_pct: float,
        is_near_metro: bool,
        risk_index: float,
        demand_index: float = 5.0,
    ) -> float:
        """
        Calculates a stable, normalized Unified Score (0–10) as approved in V2.
        Formula: (Yield*0.35) + (Price*0.25) + (Metro*0.15) + (Demand*0.15) + (Risk*0.10)
        Normalized to 0–10 before weighting.
        """
        # 1. Yield Score (0-10): Normalizing 8% yield as the 'perfect' score
        yield_score = min((yield_pct / 8) * 10, 10)

        # 2. Price Score (0-10): Normalizing overvaluation (0% overvaluation = 10)
        price_score = max(0, 10 - (overvaluation_pct / 5))

        # 3. Metro Score (0-10)
        metro_score = 10.0 if is_near_metro else 0.0

        # 4. Demand Score (0-10) - Defaulted to 5 if not available
        demand_score = min(max(demand_index, 0), 10)

        # 5. Risk Score (0-10): Inverted for V2 logic (10 - raw_risk_index)
        # Note: Risk is assumed to be normalized 0-10 before inversion here
        # If it's 0-100, we use (100 - risk_index) / 10
        risk_score = 10 - min(max(risk_index, 0), 10)

        unified_score = (
            yield_score * 0.35
            + price_score * 0.25
            + metro_score * 0.15
            + demand_score * 0.15
            + risk_score * 0.10
        )

        return round(max(0, min(10, unified_score)), 2)
