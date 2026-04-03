import React from 'react'
import Link from 'next/link'
import { Search, ArrowRight, MapPin } from 'lucide-react'

export default function Home() {
  return (
    <div className="bg-background text-on-background min-h-screen">
      
      {/* 🚀 ADAPTIVE HERO (PC: IMMERSIVE | MOBILE: TACTICAL) */}
      <section className="relative">
        
        {/* PC ONLY: IMMERSIVE BACKGROUND */}
        <div className="absolute inset-0 z-0 hidden lg:block pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0e0e0f]/80 to-[#0e0e0f] z-10" />
          <img 
            className="w-full h-full object-cover scale-105" 
            src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop" 
            alt="Institutional Architecture" 
          />
        </div>

        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-20">
          <div className="pt-16 pb-20 lg:py-32">
            
            {/* Split logic: Center on PC, Stack on Mobile */}
            <div className="flex flex-col lg:items-center lg:text-center space-y-12 lg:space-y-16">
              
              {/* Core Intel */}
              <div className="space-y-6 lg:max-w-4xl lg:mx-auto">
                <span className="text-primary text-[10px] sm:text-xs font-black tracking-[0.4em] uppercase block">Institutional Gateway</span>
                <h1 className="font-headline text-4xl sm:text-6xl lg:text-8xl font-black tracking-tightest leading-[0.9] text-white">
                  NCR Property <br className="hidden sm:block"/>
                  <span className="text-primary">Intelligence.</span>
                </h1>
                <p className="text-[#adaaab] text-base sm:text-lg lg:text-xl max-w-2xl lg:mx-auto leading-relaxed font-body">
                  An institutional-grade editorial perspective on the National Capital Region. Direct access to the FastAPI intelligence engine.
                </p>
              </div>
              
              {/* Search HUD (Responsive Width) */}
              <div className="w-full lg:max-w-2xl group">
                <div className="relative flex flex-col sm:flex-row items-stretch sm:items-center bg-[#131314] rounded-2xl sm:rounded-full p-2 border border-white/10 shadow-3xl gap-2">
                  <div className="flex items-center flex-1 px-4">
                    <Search className="text-[#adaaab] w-5 h-5 flex-shrink-0" />
                    <input 
                      className="w-full bg-transparent border-none focus:ring-0 text-white placeholder:text-[#adaaab] px-4 py-4 font-body outline-none text-base sm:text-lg min-h-[44px]" 
                      placeholder="Explore Sector or H3 Index..." 
                      type="text" 
                    />
                  </div>
                  <Link href="/dashboard" className="bg-primary text-black px-10 py-4 rounded-xl sm:rounded-full font-black text-[10px] sm:text-xs uppercase tracking-widest transition-all hover:brightness-110 active:scale-95 no-underline text-center min-h-[44px] flex items-center justify-center whitespace-nowrap">
                    Analyze Region
                  </Link>
                </div>
              </div>

              {/* MOBILE ONLY: TACTICAL IMAGE CARD */}
              <div className="lg:hidden relative w-full h-[250px] sm:h-[400px] rounded-[32px] sm:rounded-[40px] overflow-hidden border border-white/5 shadow-2xl group">
                <div className="absolute inset-0 bg-gradient-to-t from-[#0e0e0f] via-transparent to-transparent z-10" />
                <img 
                  className="w-full h-full object-cover transition-transform duration-[2000ms] group-hover:scale-110" 
                  src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop" 
                  alt="NCR Skyline" 
                />
                <div className="absolute bottom-6 left-6 z-20 space-y-1">
                  <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary">Live Context</span>
                  <div className="flex items-center gap-2 text-white text-[10px] font-black">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
                    GURUGRAM SECTOR 45
                  </div>
                </div>
              </div>

              {/* PC ONLY: CONTEXT HUD */}
              <div className="hidden lg:flex items-center gap-6 text-[10px] font-black uppercase tracking-[0.3em] text-[#adaaab]">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse shadow-[0_0_8px_#bd9dff]" />
                  LIVE CONTEXT: GURUGRAM SECTOR 45
                </div>
                <span className="opacity-10 text-white">|</span>
                <div className="flex items-center gap-2">
                  ALPHA INDEX: <span className="text-white">94.2</span>
                </div>
                <span className="opacity-10 text-white">|</span>
                <div className="flex items-center gap-2">
                  VOL: <span className="text-white">HIGH</span>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

      {/* 🏙️ MAIN CONTENT HUB */}
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20 lg:py-24 space-y-24 md:space-y-32">
        
        {/* Top Value Picks */}
        <section className="space-y-12">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-6">
            <div className="space-y-2">
              <span className="text-primary text-[10px] font-black tracking-[0.4em] uppercase block">Market Alpha</span>
              <h2 className="font-headline text-3xl sm:text-4xl font-black tracking-tightest">Top Value Picks</h2>
            </div>
            <button className="text-[#adaaab] hover:text-primary transition-all text-[10px] font-black uppercase tracking-widest flex items-center gap-3 group min-h-[44px]">
              View All Intelligence
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-10 items-stretch">
            <ValueCard 
              image="https://images.unsplash.com/photo-1545324418-f1d3ac157304?q=80&w=1935&auto=format&fit=crop"
              tag="High Yield"
              tagColor="bg-primary/20 text-primary"
              name="Magnolia Skyline Tower"
              yieldRate="8.4%"
              growth="+12%"
              risk="Low"
            />
            <ValueCard 
              image="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop"
              tag="Tech District"
              tagColor="bg-white/10 text-white"
              name="MBM Tech-Nexus Center"
              yieldRate="6.1%"
              growth="+24%"
              risk="Medium"
            />
            <ValueCard 
              image="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=2070&auto=format&fit=crop"
              tag="Premium Core"
              tagColor="bg-primary/20 text-primary"
              name="Centurion Global Plaza"
              yieldRate="5.8%"
              growth="+9.5%"
              risk="Low"
            />
          </div>
        </section>

        {/* Spatial Intelligence & Feed */}
        <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-6 lg:gap-10">
          
          {/* Spatial Card */}
          <div className="bg-[#131314] rounded-[32px] sm:rounded-[48px] overflow-hidden flex flex-col md:flex-row shadow-2xl border border-white/5 items-stretch">
            <div className="w-full md:w-2/5 p-8 sm:p-12 flex flex-col justify-center space-y-6 sm:space-y-8">
              <div className="space-y-4">
                <span className="text-primary text-[10px] font-black tracking-[0.4em] uppercase">Visual Hub</span>
                <h2 className="font-headline text-3xl font-black leading-tight">Spatial <br className="hidden md:block"/> Intelligence</h2>
              </div>
              <p className="text-[#adaaab] text-xs sm:text-sm font-body leading-relaxed">
                Cross-reference property performance with regional economic heatmaps and infrastructure signals.
              </p>
              <Link href="/discovery" className="w-full sm:w-max bg-white/[0.03] text-white px-8 py-4 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-white/[0.07] transition-all no-underline border border-white/5 text-center min-h-[44px] flex items-center justify-center">
                Launch Map Analysis
              </Link>
            </div>
            <div className="w-full md:w-3/5 min-h-[250px] sm:min-h-[300px] relative bg-[#0e0e0f]">
               <div className="absolute inset-0 bg-gradient-to-r from-[#131314] via-transparent to-transparent z-10" />
               <div className="absolute inset-0 flex items-center justify-center z-20">
                  <div className="w-20 h-20 bg-primary/10 rounded-full animate-pulse flex items-center justify-center border border-primary/20">
                    <MapPin className="text-primary w-6 h-6" />
                  </div>
               </div>
               <img className="w-full h-full object-cover grayscale opacity-20 contrast-125" src="https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=2074&auto=format&fit=crop" alt="Spatial Plot" />
            </div>
          </div>

          {/* Institutional Feed */}
          <div className="bg-[#131314] rounded-[32px] sm:rounded-[48px] p-8 sm:p-12 shadow-2xl border border-white/5 space-y-10 flex flex-col justify-between">
            <div className="space-y-10">
              <div className="flex items-center justify-between">
                <h2 className="font-headline text-lg sm:text-xl font-black uppercase tracking-tight">Institutional Feed</h2>
                <div className="w-2 h-2 bg-primary rounded-full animate-pulse shadow-[0_0_10px_#bd9dff]" />
              </div>
              <div className="space-y-10">
                <FeedItem time="2h ago" category="Markets" title="Fed rates steady: Implications for Class-A assets." desc="Institutional lenders maintain conservative LTV ratios..." />
                <div className="h-px bg-white/5" />
                <FeedItem time="5h ago" category="Regional" title="Tech corridor expansion: Austin and Phoenix lead." desc="Secondary markets seeing record-high yield premiums..." />
                <div className="h-px bg-white/5" />
                <FeedItem time="Yesterday" category="Alpha" title="NCR Metro Phase 4: Local appreciation index." desc="Infrastructure signals point to 15% upside in Sector 80-102..." />
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

const ValueCard = ({ image, tag, tagColor, name, yieldRate, growth, risk }: any) => (
  <div className="group relative bg-[#131314] rounded-[32px] sm:rounded-[40px] overflow-hidden shadow-2xl transition-all duration-700 hover:-translate-y-2 border border-white/5 flex flex-col h-full">
    <div className="aspect-[4/3] md:aspect-auto h-56 sm:h-64 relative overflow-hidden">
      <img className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110" src={image} alt={name} />
      <div className="absolute inset-0 bg-gradient-to-t from-[#131314] via-transparent to-transparent"></div>
      <div className={`absolute top-6 left-6 px-3 py-1 rounded-full text-[8px] font-black uppercase tracking-widest ${tagColor}`}>
        {tag}
      </div>
    </div>
    <div className="p-8 space-y-6 flex flex-col flex-1 justify-between">
      <h3 className="font-headline text-xl sm:text-2xl font-black tracking-tight leading-tight text-white">{name}</h3>
      <div className="grid grid-cols-3 gap-4 pt-6 border-t border-white/5">
        <div>
          <span className="text-[#adaaab] text-[8px] uppercase font-black tracking-widest block mb-1">Yield</span>
          <span className="text-primary text-base sm:text-lg font-black font-headline">{yieldRate}</span>
        </div>
        <div>
          <span className="text-[#adaaab] text-[8px] uppercase font-black tracking-widest block mb-1">Growth</span>
          <span className="text-white text-base sm:text-lg font-black font-headline">{growth}</span>
        </div>
        <div>
          <span className="text-[#adaaab] text-[8px] uppercase font-black tracking-widest block mb-1">Risk</span>
          <span className="text-[#bd9dff] text-base sm:text-lg font-black font-headline">{risk}</span>
        </div>
      </div>
    </div>
  </div>
)

const FeedItem = ({ time, category, title, desc }: any) => (
  <div className="group cursor-pointer space-y-2">
    <span className="text-[9px] text-primary font-black uppercase tracking-widest block">{time} • {category}</span>
    <h4 className="text-sm font-black font-headline text-white group-hover:text-primary transition-colors leading-tight">{title}</h4>
    <p className="text-[11px] text-[#adaaab] font-body line-clamp-2 leading-relaxed font-light">{desc}</p>
  </div>
)
