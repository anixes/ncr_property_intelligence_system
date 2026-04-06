class ScoringEngine:
    @staticmethod
    def calculate_unified_score(
        yield_pct: float,
        overvaluation_pct: float,
        is_near_metro: bool,
        risk_index: float,
        demand_index: float = 5.0,
        intent: str = "buy",
    ) -> float:
        """
        Calculates a stable, normalized Unified Score (0–10) as approved in V2.
        Pivots weighting based on persona 'intent'.
        """
        # 1. Yield Score (0-10): Normalizing 8% yield as the 'perfect' score
        yield_score = min((yield_pct / 8) * 10, 10)

        # 2. Price Score (0-10): Normalizing overvaluation (0% overvaluation = 10)
        # For rent: price_score reflects affordability vs. locality median rent
        price_score = max(0, 10 - (overvaluation_pct / 5))

        # 3. Metro Score (0-10)
        metro_score = 10.0 if is_near_metro else 0.0

        # 4. Demand Score (0-10) - Defaulted to 5 if not available
        demand_score = min(max(demand_index, 0), 10)

        # 5. Risk Score (0-10): Inverted for V2 logic (10 - raw_risk_index)
        risk_score = 10 - min(max(risk_index, 0), 10)

        if intent == "rent":
            # Renter Focus: Utility + Affordability (Metro, Demand, Price)
            unified_score = (
                metro_score * 0.35  # Commute ease is primary
                + demand_score * 0.25  # Lifestyle density and interest
                + price_score * 0.20  # Affordability vs local market
                + risk_score * 0.15  # Safety/Reliability
                + yield_score * 0.05  # Owner's yield is mostly irrelevant to renter
            )
        else:
            # Buyer Focus: ROI + Market Position (Yield, Price, Growth)
            unified_score = (
                yield_score * 0.35  # Annualized return
                + price_score * 0.25  # Capital entry point (Buy low)
                + metro_score * 0.15  # Infrastructure growth pull
                + demand_score * 0.15  # Organic market heat
                + risk_score * 0.10  # Liquidity/Valuation safety
            )

        return round(max(0, min(10, unified_score)), 2)
