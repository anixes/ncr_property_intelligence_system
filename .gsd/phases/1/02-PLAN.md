---
phase: 1
plan: 2
wave: 2
depends_on: ["01-PLAN.md"]
files_modified:
  - web-app/src/components/dashboard/ValuationHUD.tsx
  - web-app/src/components/dashboard/RoiAnalyticsView.tsx
  - web-app/src/components/dashboard/AnalyticalDashboard.tsx
autonomous: true
must_haves:
  truths:
    - "Valuation HUD is clickable and links to property analyzer"
    - "ROI Analysis shows a comparative chart for NCR cities"
  artifacts:
    - "web-app/src/components/dashboard/ValuationHUD.tsx exists"
    - "web-app/src/components/dashboard/RoiAnalyticsView.tsx exists"
---

# Plan 1.2: Valuation HUD & ROI Analytics

<objective>
Enable the key analytical modules — ROI comparative metrics and the Valuation Engine portal. This ensures the dashboard provides predictive value beyond static metrics.
</objective>

<context>
Load for context:
- SPEC.md
- web-app/src/components/dashboard/AnalyticalDashboard.tsx
- web-app/src/lib/api.ts
- web-app/src/app/analyzer/page.tsx
- ncr_property_price_estimation/routes/predict.py
</context>

<tasks>

<task type="auto">
  <name>Create ValuationHUD Functional Component</name>
  <files>web-app/src/components/dashboard/ValuationHUD.tsx</files>
  <action>
    Convert the current `renderValuationEngine` mockup into a reusable `ValuationHUD` component.
    - Implement a minimal quick-valuation input (Area, Sector, City).
    - On submission, route to `/analyzer` with query parameters OR call `api.predict` locally and show a quick result.
    - Use the established "Scanning Price Tensors" animation while loading.
    - Use high-fidelity inputs and buttons.
    AVOID: Complex full forms; keep it as a 'Quick Scan' portal.
  </action>
  <verify>Submitting the quick form produces a price prediction or routes to analyzer.</verify>
  <done>Valuation Engine is functional and integrated with backend.</done>
</task>

<task type="auto">
  <name>Create RoiAnalyticsView Component</name>
  <files>web-app/src/components/dashboard/RoiAnalyticsView.tsx</files>
  <action>
    Implement a comprehensive ROI analytics view using `Recharts`.
    - Create a BarChart comparing Average Yield/ROI across 'Gurgaon', 'Noida', 'Greater Noida'.
    - Implement an "Investment Alpha" signal generator (mocked based on city selection).
    - Use the `MetricCard` pattern to show 'Top Yield Sector' and 'Risk Factor' for the selected city.
    - Visuals must be institutional (primary/brand color accents on dark BG).
  </action>
  <verify>View renders a bar chart for city-wide ROI comparisons.</verify>
  <done>Comparative ROI analytics are functional and visualized.</done>
</task>

<task type="auto">
  <name>Integrate ROI and Valuation Navigation</name>
  <files>
    - web-app/src/components/dashboard/AnalyticalDashboard.tsx
  </files>
  <action>
    1. Import `ValuationHUD` and `RoiAnalyticsView` into `AnalyticalDashboard.tsx`.
    2. Enable 'Valuation Engine' and 'ROI Analytics' NavItems.
    3. Update `renderViewContent` to switch to these new components.
    4. Remove the inline `renderValuationEngine` function previously used as a placeholder.
  </action>
  <verify>Navigation works for all functional tabs.</verify>
  <done>All major analytical modules are enabled.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] "Valuation Engine" tab has a functional quick-prediction form.
- [ ] "ROI Analytics" tab renders the comparative Recharts view.
- [ ] Navigation transitions are smooth.
</verification>

<success_criteria>
- [ ] All ROI and Valuation tabs are fully functional.
- [ ] backend connection for predictions verified.
</success_criteria>
