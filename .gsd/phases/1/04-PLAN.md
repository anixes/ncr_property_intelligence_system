# GSD Phase 4: Mobile Excellence & Rendering Performance

## <objective>
Achieve 1:1 mobile fidelity with the Stitch reference. Fix rendering blackout of property cards on mobile viewports and calibrate typography for fluid scaling.
</objective>

## <context>
User's mobile screenshots show 'broken' vertical rhythm: stats are too large (Blowout), property cards are invisible (Rendering Trigger Failure), and footer links are colliding.
</context>

## <tasks>
<task>
<name>Fluid Typography Scaling</name>
<files>
- web-app/src/app/page.tsx
</files>
<action>
Replace fixed rem sizes (e.g. text-[4rem]) with clamp() e.g. text-[clamp(2rem,10vw,4rem)] for Bento stats (8.2K Cr, 12ms).
</action>
<verify>
Stats fit within the width of a mobile screen without wrapping or blowing out the container.
</verify>
</task>

<task>
<name>Fix Mobile Rendering (Hotspots)</name>
<files>
- web-app/src/app/page.tsx
</files>
<action>
Adjust motion.div whileInView triggers. Add 'viewport={{ once: true, amount: 0.1 }}' to ensure cards load even on high-speed mobile scrolling.
</action>
<verify>
Institutional Hotspots cards are visible on mobile upon scroll.
</verify>
</task>

<task>
<name>Compact Mobile Layout (Navbar/Footer/Hero)</name>
<files>
- web-app/src/app/page.tsx
- web-app/src/components/layout/Navbar.tsx
</files>
<action>
- Hero: Reduce 'Search Porter' h1 font-size for mobile.
- Bento: Reduce min-h for Spatial card on mobile.
- Footer: Change gap-10 to gap-6 and flex-wrap for mobile links.
- Navbar: Shorten brand text on mobile if necessary.
</action>
<verify>
Visual components are vertically centered with intentional negative space on mobile devices.
</verify>
</task>
</tasks>

## <verification>
<done>
- All Bento stats are legible on mobile.
- No 'Black Space' where Hotspot cards should be.
- Footer links do not collide.
</done>
</verification>
