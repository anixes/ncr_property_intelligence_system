---
phase: 1
plan: 1
wave: 1
depends_on: []
files_modified:
  - web-app/src/components/dashboard/LocalitiesView.tsx
  - web-app/src/components/dashboard/DiagnosticsView.tsx
  - web-app/src/components/dashboard/AnalyticalDashboard.tsx
autonomous: true
must_haves:
  truths:
    - "Localities Tab displays a grid of all NCR sectors with data"
    - "Diagnostics Tab shows live API health and model metadata"
  artifacts:
    - "web-app/src/components/dashboard/LocalitiesView.tsx exists"
    - "web-app/src/components/dashboard/DiagnosticsView.tsx exists"
---

# Plan 1.1: Localities & Diagnostics HUD

<objective>
Enable the foundation for the Locality Index and System Diagnostics views within the Analytical Dashboard. This transforms the navigation from placeholders to functional modules.
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
  <name>Create LocalitiesView Component</name>
  <files>web-app/src/components/dashboard/LocalitiesView.tsx</files>
  <action>
    Implement a searchable grid/list component that fetches all localities for the current city using `api.getLocalities(city)`. 
    For each locality, display:
    - Name and City.
    - A visual "Match Score" (mocked for now based on sector name hash or default 85+).
    - A "Growth Delta" (e.g., +12.4%).
    Use the `LocalityItem` pattern already defined in `AnalyticalDashboard.tsx`.
    AVOID: Large monolithic lists; use a simple scrollable container with a search filter at the top.
  </action>
  <verify>Component renders a list of sectors when a city is selected.</verify>
  <done>Locality list is filterable and displays scores/deltas.</done>
</task>

<task type="auto">
  <name>Create DiagnosticsView Component</name>
  <files>web-app/src/components/dashboard/DiagnosticsView.tsx</files>
  <action>
    Implement a system health dashboard that:
    - Calls `api.getHealth()` for core connectivity status.
    - Calls `api.getModelMetadata()` (needs to be added to api.ts or use `/intelligence/model-info`) for versioning.
    - Displays:
      - API Latency (mocked or measured via axios interceptor).
      - Model Versions (Sales/Rentals).
      - Discovery Pool Size.
    Use high-fidelity "Intel Terminal" styling (monospaced fonts, green glows for 'Active').
  </action>
  <verify>View shows 'healthy' status and specific model versions.</verify>
  <done>Live connection status and model metadata are visible.</done>
</task>

<task type="auto">
  <name>Integrate and Enable Navigation</name>
  <files>
    - web-app/src/components/dashboard/AnalyticalDashboard.tsx
    - web-app/src/lib/api.ts
  </files>
  <action>
    1. Update `web-app/src/lib/api.ts` to include `getModelMetadata` (v1/intelligence/model-info).
    2. Import `LocalitiesView` and `DiagnosticsView` into `AnalyticalDashboard.tsx`.
    3. Enable the 'Localities' and 'Diagnostics' NavItems (remove `disabled` and add `onClick`).
    4. Update `renderViewContent` to include:
       `if (activeView === 'Localities') return <LocalitiesView city={activeCity} />;`
       `if (activeView === 'Diagnostics') return <DiagnosticsView />;`
  </action>
  <verify>Sidebar items are clickable and switch to the new views.</verify>
  <done>Navigation is fully functional for these two modules.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Clicking "Localities" shows the searchable sectory grid.
- [ ] Clicking "Diagnostics" shows the system health HUD.
- [ ] No console errors during view switching.
</verification>

<success_criteria>
- [ ] All 3 tasks verified.
- [ ] Localities and Diagnostics tabs are active and data-mapped.
</success_criteria>
