# SPEC: Finalizing the Institutional Frontend WebApp

## 🎯 Objective
Complete the remaining functional modules of the Next.js `web-app` to transform it from a high-fidelity mockup into a fully operational institutional-grade real estate intelligence portal.

## 🏗️ Core Features to Implement

### 1. Dashboard Module Completion (`AnalyticalDashboard.tsx`)
The dashboard currently has several sections that are either disabled in the navigation or contain placeholder content.
- [ ] **Localities Index**: Implement a searchable, filterable grid of all NCR localities with their corresponding value scores and growth deltas.
- [ ] **ROI Analytics**: Create a dedicated view for comparative ROI across cities and property types using Recharts.
- [ ] **Diagnostics HUD**: Implement a system health view showing API status, model versions (from `/intelligence/model-info`), and processing latency.
- [ ] **Valuation Engine (Functional)**: Transition the "Valuation Engine" tab from a placeholder scanning animation to a functional UI that links to the existing `/analyzer` or provides a quick-valuation input.
- [ ] **Market Trends**: Implement data-driven charts for volume momentum, investor sentiment, and absorption velocity based on the `dashboard-summary`.

### 2. Global Navigation & Polish
- [ ] Enable all sidebar navigation items.
- [ ] Ensure seamless view transitions using `AnimatePresence`.
- [ ] Standardize the "Market Status" and "Jurisdiction Set" across all views.

## 🛠️ Technical Constraints
- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS (Dark/Institutional Theme)
- **State Management**: React `useState`/`useEffect` (Local) and `SWR` or custom hooks for API syncing.
- **Visuals**: Framer Motion for micro-interactions; Recharts for ROI and Trends.
- **Responsiveness**: All new views must maintain the "Mobile HUD" pattern for smaller screens.

## ✅ Success Criteria
1. No navigation items in the `AnalyticalDashboard` are disabled.
2. Every tab under `renderViewContent()` displays live or logic-consistent data.
3. The "Valuation Engine" tab integrates with the backend `/predict` logic.
4. The application passes a basic "Verification" run against the local FastAPI backend.
