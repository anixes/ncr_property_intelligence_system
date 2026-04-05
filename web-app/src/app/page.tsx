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

  const POOL_CITIES = ['GURUGRAM SEC. 65', 'NOIDA SEC. 150', 'DWARKA EXPY', 'GOLF COURSE RD', 'SOUTHERN PERIPHERAL', 'YAMUNA EXPY'];

  React.useEffect(() => {
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
              <span className="text-white font-headline font-black text-lg group-hover:text-primary transition-colors leading-tight">Market<br/>Analyzer</span>
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

        {/* === SPATIAL INTELLIGENCE === */}
        <div className="premium-card shadow-3xl flex flex-col md:flex-row overflow-hidden border border-white/5 bg-[#131314]/40 h-[600px]">
          <div className="p-7 sm:p-12 w-full md:w-1/3 flex flex-col justify-center">
             <span className="text-[10px] text-primary uppercase font-black tracking-widest mb-2">Find Where Value Grows</span>
             <h2 className="font-headline text-3xl sm:text-5xl font-black mb-6 leading-tight">Spatial<br/>Intelligence</h2>
             <p className="text-white/60 mb-8 max-w-sm text-sm sm:text-base leading-relaxed">See exactly where the best deals are in NCR. Use our map to spot rising price zones and hot property clusters before everyone else.</p>
             <Link href="/discovery">
               <button className="border border-white/10 bg-[#1a1a1c] text-[10px] font-black uppercase tracking-widest px-8 py-4 rounded-full w-fit hover:bg-white/5 transition-all hover:scale-105 active:scale-95 shadow-lg shadow-black/20">
                 Launch Map Analysis
               </button>
             </Link>
          </div>
          
          <div className="w-full md:w-2/3 h-full relative bg-[#0e0e0f] border-t md:border-t-0 md:border-l border-white/5 overflow-hidden">
            <div className="absolute inset-0 z-0">
                <MapComponent />
            </div>
            <div className="absolute inset-0 bg-gradient-to-r from-[#131314] via-transparent to-transparent z-10 hidden md:block pointer-events-none" />
            <div className="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-[#131314] to-transparent z-10 md:hidden pointer-events-none" />
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
