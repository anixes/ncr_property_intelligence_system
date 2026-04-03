# Phase 1: Logic Mapping & Skeleton Construction

## Objective
Migrate the core intelligence from Streamlit to Next.js 16 while maintaining strict data parity and institutional reliability.

## Tasks
1. [x] **Core Infrastructure**:
   - Define TypeScript schemas (src/types/index.ts).
   - Implement API Client abstraction (src/lib/api.ts).
2. [w] **Market Analyzer Intelligence**:
   - Build ValuationHUD for high-intensity metric display.
   - Implement AnalysisPage state for multi-param valuation search.
   - [ ] Add ROI and Yield calculation logic mapping.
3. [ ] **Discovery Engine Intelligence**:
   - Build DiscoveryPage for secondary research (Recommender).
   - Implement filtering logic (BHK, Luxury, Vastu).
   - Create PropertyCard skeleton for results.
4. [ ] **Spatial Intelligence**:
   - Integrate H3 spatial mapping logic.
   - Create a placeholder MapTerminal for hotspot visualization.
5. [ ] **Empirical Verification**:
   - Test data connectivity with local/remote FastAPI backend.
   - Ensure mobile-first responsiveness (44px targets).

## Success Criteria
- Property features sent to /predict return a valid ValuationResult.
- UI updates statefully without reloading.
- Mobile view presents a single-column \"HUD\" without horizontal overflow.
