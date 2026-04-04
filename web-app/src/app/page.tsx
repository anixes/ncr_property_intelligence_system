'use client';

import React from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Search, ArrowRight, MapPin, Activity, Globe, Shield } from 'lucide-react'

export default function Home() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.15, delayChildren: 0.2 }
    }
  }

  const itemVariants: any = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } }
  }

  return (
    <div className="bg-background text-on-background min-h-screen overflow-x-hidden">
      
      {/* 🚀 ADAPTIVE HERO (PC: IMMERSIVE | MOBILE: TACTICAL) */}
      <section className="relative overflow-hidden min-h-[90vh] flex items-center">
        
        {/* PC ONLY: IMMERSIVE BACKGROUND */}
        <div className="absolute inset-0 z-0 hidden lg:block pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0e0e0f]/80 to-[#0e0e0f] z-10" />
          <motion.img 
            initial={{ scale: 1.1, opacity: 0 }}
            animate={{ scale: 1.05, opacity: 1 }}
            transition={{ duration: 2.5, ease: "easeOut" }}
            className="w-full h-full object-cover" 
            src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop" 
            alt="Institutional Architecture" 
          />
        </div>

        {/* BACKGROUND AMBIENCE (Pulse) */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-[120px] animate-pulse z-0 pointer-events-none" />

        <motion.div 
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="w-full max-w-7xl mx-auto px-6 sm:px-10 lg:px-12 relative z-20"
        >
          <div className="py-20 lg:py-32">
            
            <div className="flex flex-col lg:items-center lg:text-center space-y-10 lg:space-y-16">
              
              {/* Core Intel */}
              <motion.div variants={itemVariants} className="space-y-6 lg:max-w-4xl lg:mx-auto">
                <div className="flex items-center lg:justify-center gap-3">
                  <span className="w-8 h-[1px] bg-primary/40 hidden sm:block" />
                  <span className="text-primary text-[10px] sm:text-xs font-black tracking-[0.5em] uppercase block">Institutional Gateway</span>
                  <span className="w-8 h-[1px] bg-primary/40 hidden sm:block" />
                </div>
                <h1 className="font-headline text-5xl sm:text-7xl lg:text-9xl font-black tracking-tightest leading-[0.85] text-white">
                  NCR <span className="text-primary text-glow-primary">Intelligence.</span>
                </h1>
                <p className="text-[#adaaab] text-lg sm:text-xl lg:text-2xl max-w-3xl lg:mx-auto leading-relaxed font-body font-light">
                  The definitive editorial perspective on the National Capital Region's real estate frontier. Powered by institutional-grade spatial analytics.
                </p>
              </motion.div>
              
              {/* Search HUD (Responsive Width) */}
              <motion.div variants={itemVariants} className="w-full lg:max-w-3xl">
                <div className="relative glass-panel-luxe rounded-[2.5rem] p-2 border border-white/10 shadow-3xl hover:border-primary/30 transition-all duration-500">
                  <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                    <div className="flex items-center flex-1 px-5 h-14 sm:h-16">
                      <Search className="text-primary w-6 h-6 flex-shrink-0" />
                      <input 
                        className="w-full bg-transparent border-none focus:ring-0 text-white placeholder:text-[#3d3d3f] px-5 font-body outline-none text-lg sm:text-xl" 
                        placeholder="Search Sector, H3, or Society..." 
                        type="text" 
                      />
                    </div>
                    <Link href="/dashboard" className="bg-primary text-black px-12 py-4 sm:py-5 rounded-[2rem] font-black text-xs uppercase tracking-widest transition-all hover:brightness-110 active:scale-95 no-underline text-center flex items-center justify-center shadow-[0_0_20px_rgba(189,157,255,0.4)]">
                      Analyze Strategy
                    </Link>
                  </div>
                </div>
              </motion.div>

              {/* TACTICAL HUD (Mobile Cards / PC HUD) */}
              <motion.div variants={itemVariants} className="w-full">
                 <div className="grid grid-cols-2 lg:flex lg:items-center lg:justify-center gap-4 sm:gap-8 lg:gap-12 text-[10px] sm:text-xs font-black uppercase tracking-widest text-[#adaaab]">
                    <HudStat label="Live Context" value="GURUGRAM SEC. 45" active />
                    <HudStat label="Alpha Index" value="94.2" />
                    <HudStat label="Vol. Premium" value="High" color="text-primary" />
                    <HudStat label="Market Status" value="Bullish" color="text-green-400" />
                 </div>
              </motion.div>

            </div>
          </div>
        </motion.div>
      </section>

      {/* 🏙️ MAIN CONTENT HUB (Atmospheric Spacing Applied) */}
      <div className="w-full max-w-7xl mx-auto px-6 sm:px-10 lg:px-12 py-20 sm:py-32 space-y-32 sm:space-y-48">
        
        {/* Top Value Picks */}
        <section className="space-y-16">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-10">
            <div className="space-y-4">
              <span className="text-primary text-[10px] font-black tracking-[0.5em] uppercase block">Market Extraction</span>
              <h2 className="font-headline text-4xl sm:text-5xl font-black tracking-tightest leading-none">Institutional <br className="sm:hidden"/> Selection.</h2>
            </div>
            <button className="text-[#adaaab] hover:text-primary transition-all text-xs font-black uppercase tracking-widest flex items-center gap-4 group h-14 px-8 border border-white/5 rounded-full hover:bg-white/5">
              Access Full Terminal
              <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-12 lg:gap-16 items-stretch">
            <ValueCard 
              image="https://images.unsplash.com/photo-1545324418-f1d3ac157304?q=80&w=1935&auto=format&fit=crop"
              tag="High Alpha"
              tagColor="bg-primary/20 text-primary"
              name="Magnolia Skyline"
              yieldRate="8.4%"
              growth="+12%"
              risk="Low"
            />
            <ValueCard 
              image="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop"
              tag="Infrastructure"
              tagColor="bg-white/10 text-white"
              name="MBM Tech-Nexus"
              yieldRate="6.1%"
              growth="+24%"
              risk="Med"
            />
            <ValueCard 
              image="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=2070&auto=format&fit=crop"
              tag="Premium Core"
              tagColor="bg-primary/20 text-primary"
              name="Global Plaza 45"
              yieldRate="5.8%"
              growth="+9.5%"
              risk="Low"
            />
          </div>
        </section>

        {/* Spatial Intelligence & Feed */}
        <div className="grid grid-cols-1 lg:grid-cols-[1.3fr_0.7fr] gap-8 sm:gap-12 lg:gap-16">
          
          {/* Spatial Card */}
          <div className="premium-card overflow-hidden flex flex-col md:flex-row shadow-3xl items-stretch min-h-[500px]">
            <div className="w-full md:w-1/2 p-10 sm:p-14 flex flex-col justify-center space-y-8">
              <div className="space-y-4">
                <span className="text-primary text-[10px] font-black tracking-[0.5em] uppercase">Tactical Visuals</span>
                <h2 className="font-headline text-4xl font-black leading-[0.95] tracking-tightest">Spatial <br /> Intelligence</h2>
              </div>
              <p className="text-[#adaaab] text-sm sm:text-base font-body leading-relaxed font-light">
                Cross-reference property performance with regional economic heatmaps and corridor development signals. 
              </p>
              <Link href="/discovery" className="w-full sm:w-max bg-white/5 text-white px-10 py-5 rounded-full text-xs font-black uppercase tracking-widest hover:bg-primary hover:text-black transition-all no-underline border border-white/10 text-center flex items-center justify-center">
                Launch Map Analysis
              </Link>
            </div>
            <div className="w-full md:w-1/2 h-[300px] md:h-auto relative bg-[#0e0e0f] border-l border-white/5">
                <div className="absolute inset-0 bg-gradient-to-r from-[#131314] via-transparent to-transparent z-10 hidden md:block" />
                <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-[#131314] to-transparent z-10 md:hidden" />
                <div className="absolute inset-0 flex items-center justify-center z-20">
                  <div className="w-24 h-24 bg-primary/10 rounded-full animate-ping flex items-center justify-center border border-primary/20 opacity-30" />
                  <div className="absolute w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center border border-primary/50 shadow-[0_0_30px_rgba(189,157,255,0.5)]">
                    <MapPin className="text-primary w-6 h-6" />
                  </div>
                </div>
                <img className="w-full h-full object-cover grayscale opacity-10 contrast-150 brightness-50" src="https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=2074&auto=format&fit=crop" alt="Spatial Plot" />
            </div>
          </div>

          {/* Institutional Feed */}
          <div className="premium-card p-10 sm:p-14 shadow-3xl space-y-12 flex flex-col">
            <div className="flex items-center justify-between">
              <h2 className="font-headline text-2xl font-black uppercase tracking-tight">Intelligence Feed</h2>
              <div className="w-2.5 h-2.5 bg-primary rounded-full animate-pulse shadow-[0_0_15px_#bd9dff]" />
            </div>
            <div className="space-y-12 flex-1">
              <FeedItem icon={<Globe className="w-4 h-4" />} time="2h ago" category="Markets" title="Fed rates steady: Implications for NCR Assets." desc="Institutional lenders maintain conservative LTV ratios despite liquidity surge..." />
              <div className="h-[1px] bg-white/5" />
              <FeedItem icon={<Activity className="w-4 h-4" />} time="5h ago" category="Hotspots" title="Dwarka Expressway: Q2 Appreciation Delta." desc="Infrastructure signals point to sustained 12% premium in high-density corridors..." />
              <div className="h-[1px] bg-white/5" />
              <FeedItem icon={<Shield className="w-4 h-4" />} time="Yesterday" category="Policy" title="RERA 2.0: Impact on stalled projects." desc="New directives prioritize completion velocity over initial capital deployment..." />
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

const HudStat = ({ label, value, active, color = "text-white" }: any) => (
  <div className="flex flex-col gap-1">
    <span className="opacity-40 text-[9px] tracking-[0.2em]">{label}</span>
    <div className="flex items-center gap-2">
      {active && <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />}
      <span className={`${color}`}>{value}</span>
    </div>
  </div>
)

const ValueCard = ({ image, tag, tagColor, name, yieldRate, growth, risk }: any) => (
  <motion.div 
    whileHover={{ y: -10 }}
    className="group relative premium-card overflow-hidden h-full flex flex-col"
  >
    <div className="h-64 sm:h-72 relative overflow-hidden">
      <img className="w-full h-full object-cover transition-transform duration-[1.5s] group-hover:scale-110" src={image} alt={name} />
      <div className="absolute inset-0 bg-gradient-to-t from-[#131314] via-transparent to-transparent opacity-80"></div>
      <div className={`absolute top-8 left-8 px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-widest ${tagColor} bg-opacity-90 backdrop-blur-md`}>
        {tag}
      </div>
    </div>
    <div className="p-10 space-y-8 flex flex-col flex-1 justify-between">
      <h3 className="font-headline text-2xl sm:text-3xl font-black tracking-tightest leading-tight text-white">{name}</h3>
      <div className="grid grid-cols-3 gap-6 pt-10 border-t border-white/10">
        <DataPoint label="Yield" value={yieldRate} color="text-primary text-xl" />
        <DataPoint label="Growth" value={growth} color="text-white text-xl" />
        <DataPoint label="Risk" value={risk} color="text-[#bd9dff] text-xl" />
      </div>
    </div>
  </motion.div>
)

const DataPoint = ({ label, value, color }: any) => (
  <div>
    <span className="text-[#3d3d3f] text-[9px] uppercase font-black tracking-widest block mb-2">{label}</span>
    <span className={`${color} font-black font-headline`}>{value}</span>
  </div>
)

const FeedItem = ({ icon, time, category, title, desc }: any) => (
  <div className="group cursor-pointer space-y-4">
    <div className="flex items-center gap-3">
      <div className="text-primary/50">{icon}</div>
      <span className="text-[10px] text-primary/70 font-black uppercase tracking-[0.2em] block">{time} • {category}</span>
    </div>
    <div className="space-y-2">
      <h4 className="text-base sm:text-lg font-black font-headline text-white group-hover:text-primary transition-colors leading-tight">{title}</h4>
      <p className="text-xs sm:text-sm text-[#adaaab] font-body line-clamp-2 leading-relaxed font-light">{desc}</p>
    </div>
  </div>
)
