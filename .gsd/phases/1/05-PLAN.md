# GSD Phase 5: Sovereign Intelligence Optimization

## <objective>
Elevate the mobile experience with 'Intelligence-Grade' interactions, hydration-safe UI branching, and gesture-driven layout patterns (Snap-Scroll).
</objective>

## <context>
While Phase 4 fixed rendering, Phase 5 aims for 'Professional Polish'. Mobile users expect tactile feedback (Haptics) and horizontal navigation for dense data blocks to minimize vertical scroll fatigue.
</context>

## <tasks>
<task>
<name>Hydration-Safe Mobile Hook</name>
<files>
- web-app/src/hooks/useIsMobile.ts
- web-app/src/components/layout/Navbar.tsx
</files>
<action>
Implement a high-performance useIsMobile hook that correctly handles server-side rendering (SSR) to prevent layout flickering during hydration.
</action>
<verify>
Component logic split between Phone/PC does not cause hydration mismatch warnings in the console.
</verify>
</task>

<task>
<name>Haptic Tactile Feedback (Active States)</name>
<files>
- web-app/src/app/page.tsx
- web-app/src/components/layout/Navbar.tsx
</files>
<action>
Add 'active:scale-95 transition-transform' to all mobile search buttons, navigation links, and property cards. This mimics iOS/Android haptic response visually.
</action>
<verify>
Touching an element on a mobile simulator provides immediate physical feedback.
</verify>
</task>

<task>
<name>Snap-Scroll Bento Calibration</name>
<files>
- web-app/src/app/page.tsx
</files>
<action>
Transform the 'Institutional Hotspots' grid into a 'snap-x mandatory' horizontal scroll on mobile devices (sm: and below). Keep it a 3-column grid on desktop.
</action>
<verify>
Property cards can be horizontally swiped on phone viewports with a snap-to-center effect, saving 1200px of vertical space.
</verify>
</task>

<task>
<name>Mobile Metadata Audit</name>
<files>
- web-app/src/app/layout.tsx
</files>
<action>
Verify viewport settings for maximum scale inhibition (preventing accidental 'pinch-zoom' blowout of your terminal).
</action>
<verify>
Terminal remains at 1.0 scale even if the user taps rapidly in the search bar.
</verify>
</task>
</tasks>

## <verification>
<done>
- Hydration-safe useIsMobile hook deployed.
- Haptic tactile feedback (active:scale-95) integrated globally.
- Horizontal Snap-Scroll implemented for Hotspot cards on mobile.
- Viewport scaling locked for terminal-grade stability.
- Navbar branding adjusted for mobile density.
</done>
</verification>
