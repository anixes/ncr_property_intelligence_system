'use client'

import React from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Search, ArrowRight, BarChart3, Compass, Globe, Shield } from 'lucide-react'
import dynamic from 'next/dynamic'

// Render the embedded interactive map inside the Spatial Intelligence card
const MapComponent = dynamic(() => import('@/components/map/SpatialMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-[#0e0e0f] flex items-center justify-center flex-col gap-2">
      <div className="w-8 h-8 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
      <span className="text-[8px] font-black tracking-widest text-primary uppercase">Hydrating Map...</span>
    </div>
  )
})

export default function Home() {
  const [activeCity, setActiveCity] = React.useState('GURUGRAM SEC. 65');
  const [alphaScore, setAlphaScore] = React.useState('94.2');
  const [feedItems, setFeedItems] = React.useState<any[]>([]);
  const [featuredAssets, setFeaturedAssets] = React.useState<any[]>([]);

  const FALLBACK_ASSETS = [
    { name: "Magnolia Skyline", yield: "6.8%", growth: "+12.4%", risk: "Low", tag: "Premium", image: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" },
    { name: "Sector 150 Matrix", yield: "7.1%", growth: "+18.2%", risk: "Med", tag: "Growth", image: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" },
    { name: "Golf Course Ext.", yield: "5.5%", growth: "+9.1%", risk: "Very Low", tag: "Stable", image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" }
  ];
  const POOL_CITIES = ['GURUGRAM SEC. 65', 'NOIDA SEC. 150', 'DWARKA EXPY', 'GOLF COURSE RD', 'SOUTHERN PERIPHERAL', 'YAMUNA EXPY'];
  const POOL_ALERTS = [
    { icon: <BarChart3 className="w-4 h-4" />, category: "NOIDA", title: "Expressway Extension: Premium Yields", desc: "Infrastructure completion tokens detected. Projected 7.2% rental yield ceiling for Sector 150 assets..." },
    { icon: <Shield className="w-4 h-4" />, category: "NCR REGION", title: "RERA 2.0 Compliance: Alpha Impact", desc: "Institutional directives prioritizing project velocity. Reducing liquidity risk in stalled corridor assets..." },
    { icon: <BarChart3 className="w-4 h-4" />, category: "MARKETS", title: "Capital Flight: Luxury Segment Shift", desc: "Institutional investors reallocating from core Delhi to premium Gurugram gated assets..." },
    { icon: <Globe className="w-4 h-4" />, category: "INFRA", title: "Metrolink Expansion: Yield Catalyst", desc: "New station approvals in Southern Peripheral Road expected to trigger 12% rent premium..." },
    { icon: <Shield className="w-4 h-4" />, category: "POLICY", title: "Institutional Land Bank Audit", desc: "Government audit of stalled institutional plots signals upcoming supply squeeze in Noida..." }
  ];

  React.useEffect(() => {
    setFeedItems(POOL_ALERTS.slice(0, 3));
    
    // Fetch Dynamic Featured Assets
    const fetchAssets = async () => {
      try {
        const res = await fetch('/api/discovery?listing_type=buy');
        const data = await res.json();
        if (data.featured && data.featured.length > 0) {
          const mapped = data.featured.slice(0, 3).map((item: any) => ({
            name: item.property_name || item.name,
            yield: item.yield_rate || "N/A",
            growth: item.growth_index || "+--%",
            risk: item.risk_profile || "Med",
            tag: item.asset_tag || "New",
            image: item.image_url || "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
          }));
          setFeaturedAssets(mapped);
        } else {
          setFeaturedAssets(FALLBACK_ASSETS);
        }
      } catch (e) {
        setFeaturedAssets(FALLBACK_ASSETS);
      }
    };
    fetchAssets();
    
    // Cycle target zone and scores for "live" feel
    let cityIdx = 0;
    const interval = setInterval(() => {
      cityIdx = (cityIdx + 1) % POOL_CITIES.length;
      setActiveCity(POOL_CITIES[cityIdx]);
      setAlphaScore((Math.random() * (98 - 92) + 92).toFixed(1));
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-[100dvh] bg-[#0e0e0f] relative w-full overflow-hidden antialiased selection:bg-primary/30 selection:text-white pb-24">
      {/* Hero Background Image with Overlay */}
      <div className="absolute inset-0 z-0 h-[100dvh]">
        <img 
          src="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80" 
          className="w-full h-full object-cover opacity-20 filter grayscale"
          alt="NCR Skyline Background"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0e0e0f] via-transparent to-[#0e0e0f]" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#0e0e0f] via-transparent to-transparent" />
      </div>

      {/* Background Ambience */}
      <div className="absolute inset-x-0 -top-40 h-[800px] opacity-10 pointer-events-none flex justify-center overflow-hidden z-0">
        <div className="w-[1200px] h-[1200px] bg-primary/20 rounded-full blur-[180px]" />
      </div>

      <div className="relative z-10 max-w-[1400px] mx-auto px-4 sm:px-8 xl:px-12 pt-32 space-y-20">
        
        {/* === HERO SECTION === */}
        <div className="flex justify-between items-end">
          <div className="max-w-2xl space-y-6">
            <span className="text-[#bd9dff] font-black uppercase tracking-widest text-[10px] sm:text-xs">Institutional Intelligence Portal</span>
            <h1 className="font-headline text-4xl sm:text-6xl lg:text-7xl font-black text-white leading-[0.95] tracking-tight">NCR Property<br/>Intelligence.</h1>
            <p className="text-white/60 text-lg leading-relaxed max-w-lg">The smartest way to navigate NCR real estate. AI-powered tools to help you find and price the perfect home.</p>
          </div>
          
          <div className="hidden lg:flex gap-8 items-end">
            <HudStat label="Active Nodes" value="18,204" color="text-[#10b981]" active />
            <HudStat label="Network Alpha" value={alphaScore} color="text-[#bd9dff]" active />
            <HudStat label="Target Zone" value={activeCity} active />
          </div>
        </div>

        {/* === PRIMARY NAVIGATION CARDS === */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link href="/dashboard" className="group relative glass-panel-luxe rounded-[2rem] p-5 flex items-center gap-4 border border-white/10 hover:border-primary/40 transition-all duration-500 overflow-hidden no-underline shadow-3xl active:scale-[0.97] min-h-[96px]">
            <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
              <BarChart3 className="text-primary w-5 h-5" />
            </div>
            <div className="flex flex-col text-left">
              <span className="text-white font-headline font-black text-lg group-hover:text-primary transition-colors leading-tight">Price<br/>Estimator</span>
            </div>
            <ArrowRight className="w-5 h-5 text-white/20 group-hover:text-primary group-hover:translate-x-2 transition-all ml-auto" />
          </Link>

          <Link href="/discovery" className="group relative glass-panel-luxe rounded-[2rem] p-5 flex items-center gap-4 border border-white/10 hover:border-white/30 transition-all duration-500 overflow-hidden no-underline shadow-3xl active:scale-[0.97] min-h-[96px]">
            <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
              <Compass className="text-white w-5 h-5" />
            </div>
            <div className="flex flex-col text-left">
              <span className="text-white font-headline font-black text-lg leading-tight">Property<br/>Search</span>
            </div>
            <ArrowRight className="w-5 h-5 text-white/20 group-hover:text-white group-hover:translate-x-2 transition-all ml-auto" />
          </Link>
        </div>

        {/* === ASSET MATRIX (VALUE CARDS) === */}
        <div className="space-y-8">
           <div className="flex justify-between items-end">
             <h2 className="font-headline text-3xl sm:text-4xl font-black">Featured Assets</h2>
           </div>
           
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 min-h-[320px]">
             {featuredAssets.length > 0 ? featuredAssets.map((asset, i) => (
                <ValueCard 
                  key={i}
                  image={asset.image}
                  tag={asset.tag} tagColor={asset.tag === 'Premium' ? "text-[#bd9dff] bg-[#bd9dff]/10 border border-[#bd9dff]/30" : "text-[#10b981] bg-[#10b981]/10 border border-[#10b981]/30"}
                  name={asset.name} yieldRate={asset.yield} growth={asset.growth} risk={asset.risk}
                />
             )) : (
              <div className="col-span-3 h-48 flex items-center justify-center border border-white/5 bg-white/5 rounded-[2rem]">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-white/40">Discovering High-Alpha Assets...</span>
                </div>
              </div>
             )}
           </div>
        </div>

        {/* === SPATIAL INTELLIGENCE & FEED === */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Spatial Intelligence block */}
          <div className="premium-card shadow-3xl flex flex-col md:flex-row overflow-hidden border border-white/5 bg-[#131314]/40 h-[480px]">
            <div className="p-7 sm:p-12 w-full md:w-1/2 flex flex-col justify-center">
               <span className="text-[10px] text-primary uppercase font-black tracking-widest mb-2">Tactical Visuals</span>
               <h2 className="font-headline text-3xl sm:text-4xl font-black mb-6">Spatial<br/>Intelligence</h2>
               <p className="text-white/60 mb-8 max-w-sm text-sm sm:text-base leading-relaxed">Cross-reference high-alpha assets with regional development corridors. Live NCR map integration.</p>
               <button className="border border-white/10 bg-[#1a1a1c] text-[10px] font-black uppercase tracking-widest px-6 py-3 rounded-full w-fit hover:bg-white/5 transition-colors">
                 Launch Map Analysis
               </button>
            </div>
            
            <div className="w-full md:w-1/2 h-[240px] md:h-full relative bg-[#0e0e0f] border-t md:border-t-0 md:border-l border-white/5 overflow-hidden">
              <div className="absolute inset-0 z-0">
                  <MapComponent />
              </div>
              <div className="absolute inset-0 bg-gradient-to-r from-[#131314] via-transparent to-transparent z-10 hidden md:block pointer-events-none" />
              <div className="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-[#131314] to-transparent z-10 md:hidden pointer-events-none" />
            </div>
          </div>

          {/* Institutional Feed */}
          <div className="premium-card p-7 sm:p-12 shadow-3xl space-y-8 flex flex-col border border-white/5 bg-[#131314]/40 h-[480px]">
            <div className="flex items-center justify-between">
              <h2 className="font-headline text-xl sm:text-2xl font-black">Institutional Feed</h2>
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse shadow-[0_0_12px_#bd9dff]" />
            </div>
            <div className="space-y-6 sm:space-y-8 flex-1 overflow-hidden">
              {feedItems.map((item, idx) => (
                <React.Fragment key={idx}>
                  <FeedItem {...item} time={idx === 0 ? "LIVE" : idx === 1 ? "1H AGO" : "3H AGO"} />
                  {idx < feedItems.length - 1 && <div className="h-[1px] bg-white/10" />}
                </React.Fragment>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

function HudStat({ label, value, color = "text-white", active = false }: any) {
  return (
    <div className={`flex flex-col gap-1.5 ${active ? "opacity-100" : "opacity-60"} min-w-[120px]`}>
      <span className="text-[10px] text-white/40 font-black uppercase tracking-[0.2em]">{label}</span>
      <span className={`text-base sm:text-lg font-black tracking-widest truncate ${color} drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]`}>{value}</span>
    </div>
  )
}

function ValueCard({ image, tag, tagColor, name, yieldRate, growth, risk }: any) {
  return (
    <motion.div
      whileHover={{ y: -8 }}
      className="group relative bg-[#131314] rounded-[2rem] overflow-hidden border border-white/5 shadow-2xl flex flex-col h-[320px] sm:h-[400px]"
    >
      <div className="relative h-[180px] sm:h-[220px] overflow-hidden">
        <div className="absolute top-5 left-5 z-20">
          <span className={`${tagColor} text-[10px] font-black uppercase tracking-widest px-4 py-2 rounded-full backdrop-blur-md`}>
            {tag}
          </span>
        </div>
        <img src={image} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 brightness-75 group-hover:brightness-100" alt={name} />
      </div>
      <div className="p-6 sm:p-8 space-y-4 flex-1 flex flex-col justify-between bg-[#131314]">
        <div className="space-y-2">
          <h3 className="font-headline text-xl sm:text-2xl font-black text-white group-hover:text-primary transition-colors tracking-tight">{name}</h3>
          <div className="flex items-center gap-2 text-[#3d3d3f]">
            <Compass className="w-3 h-3" />
            <span className="text-[10px] font-black uppercase tracking-widest">NCR Premium Prime</span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3 pt-4 border-t border-white/5">
          <StatBox label="Yield" value={yieldRate} />
          <StatBox label="Growth" value={growth} color="text-primary" />
          <StatBox label="Risk" value={risk} />
        </div>
      </div>
    </motion.div>
  )
}

function StatBox({ label, value, color = "text-white" }: any) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-[9px] text-white/30 font-black uppercase tracking-widest">{label}</span>
      <span className={`text-sm sm:text-base font-black tracking-widest ${color}`}>{value}</span>
    </div>
  )
}

function FeedItem({ icon, category, title, desc, time }: any) {
  return (
    <div className="flex gap-4 group">
       <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0 group-hover:border-primary/50 group-hover:text-primary transition-colors">
         {icon}
       </div>
       <div className="flex-1 space-y-1">
         <div className="flex justify-between items-center">
            <span className="text-[9px] text-primary font-black uppercase tracking-widest">{category}</span>
            <span className="text-[9px] text-white/30 font-black uppercase tracking-widest">{time}</span>
         </div>
         <h4 className="font-bold text-white text-[13px] sm:text-sm group-hover:text-primary transition-colors">{title}</h4>
         <p className="text-white/50 text-[11px] sm:text-xs leading-relaxed line-clamp-2 md:line-clamp-1 lg:line-clamp-2">{desc}</p>
       </div>
    </div>
  )
}
