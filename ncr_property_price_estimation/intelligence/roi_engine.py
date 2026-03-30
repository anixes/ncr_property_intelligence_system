class ROIEngine:
    @staticmethod
    def calculate_yield(total_price: float, monthly_rent: float) -> float:
        """
        Calculate Annualized Gross Rental Yield.
        Yield % = (Monthly Rent * 12) / Total Value * 100
        """
        if total_price <= 0:
            return 0.0
        return round((monthly_rent * 12) / total_price * 100, 2)

    @staticmethod
    def calculate_annual_rent(monthly_rent: float) -> float:
        """
        Calculate total annual rent expected.
        """
        return round(monthly_rent * 12, 2)
