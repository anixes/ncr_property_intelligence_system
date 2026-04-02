---
phase: 1
plan: 3
wave: 3
depends_on: ["02-PLAN.md"]
files_modified:
  - web-app/src/components/dashboard/MarketTrendsView.tsx
  - web-app/src/components/dashboard/AnalyticalDashboard.tsx
autonomous: true
must_haves:
  truths:
    - "Market Trends shows investor sentiment and volume momentum"
  artifacts:
    - "web-app/src/components/dashboard/MarketTrendsView.tsx exists"
---

# Plan 1.3: Market Trends & Polish

<objective>
Enable the final analytical module (Market Trends) and perform a comprehensive aesthetic and responsiveness audit to ensure a premium user experience across all devices.
</objective>

<context>
Load for context:
- SPEC.md
- web-app/src/components/dashboard/AnalyticalDashboard.tsx
- web-app/src/lib/api.ts
- ncr_property_price_estimation/routes/intelligence.py
</context>

<tasks>

<task type="auto">
  <name>Create MarketTrendsView Component</name>
  <files>web-app/src/components/dashboard/MarketTrendsView.tsx</files>
  <action>
    Implement the 3-column trends summary for the "Market Trends" tab.
    - Create a Volume Momentum chart using Recharts.
    - Create an Investor Sentiment gauge.
    - Create an Absorption Velocity indicator.
    - This data should be derived from `api.getDashboardSummary(city)` where possible or reasonably mocked for city-specific trends.
    - Visuals: Use sleek, glowing gradients for the charts to match the "Intel Terminal" feel.
    AVOID: Standard browser chart colors; use `primary` and `accent` colors.
  </action>
  <verify>View renders charts and sentiment gauges for city-wide trends.</verify>
  <done>Market trends dashboard is functional and animated.</done>
</task>

<task type="auto">
  <name>Final Responsive Audit & Polish</name>
  <files>
    - web-app/src/components/dashboard/AnalyticalDashboard.tsx
    - web-app/src/app/globals.css
  </files>
  <action>
    1. Ensure all new views (Localities, ROI, Trends) render correctly on mobile using the `renderMobileHUD` or a consistent 'vertical grid' pattern.
    2. Add `AnimatePresence` to `AnalyticalDashboard` view switching for smooth "sliding" or "fading" transitions.
    3. Update the "Market Status" ticker to be truly dynamic (periodically fetching status OR cycling hardcoded signals).
    4. Fix Any 'disabled' items that were missed in earlier waves.
  </action>
  <verify>Navigating through all tabs is smooth and responsive on all viewport sizes.</verify>
  <done>Application UI is fully operational and polished.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Market Trends tab is functional.
- [ ] All NavItems are enabled and functional.
- [ ] Visual transitions are premium.
- [ ] Mobile view works for all new tabs.
</verification>

<success_criteria>
- [ ] No placeholders remain in the Analytical Dashboard.
- [ ] 100% feature parity with SPEC.md.
</success_criteria>
