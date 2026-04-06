from fastapi import APIRouter, HTTPException

from ncr_property_price_estimation import state
from ncr_property_price_estimation.intelligence.engine import IntelligenceEngine
from ncr_property_price_estimation.schemas import DiscoverRequest

router = APIRouter(prefix="/discover", tags=["Property Discovery"])
_intelligence = IntelligenceEngine()


@router.post("")
def discover_properties(req: DiscoverRequest):
    """Factual discovery of real-world property listings based on institutional filters."""
    if state.discovery_pool.empty:
        raise HTTPException(status_code=503, detail="Discovery assets not hydrated.")

    results = _intelligence.discover_properties(
        pool_df=state.discovery_pool, locality_index=state.locality_index, req=req
    )
    return results


@router.get("/hotspots")
async def get_market_hotspots(listing_type: str = "buy", city: str = None):
    """Institutional hotspots and featured assets across NCR."""
    f = state.featured_cache.get(listing_type, [])
    h = state.hotspots_cache.get(listing_type, [])

    if city and city != "Entire NCR":
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(city, city)
        f = [x for x in f if x.get("city") == db_city]
        h = [x for x in h if x.get("city") == db_city]

    return {"status": "success", "listing_type": listing_type, "hotspots": h, "featured": f}
