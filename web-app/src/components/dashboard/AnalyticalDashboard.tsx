'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  Map as MapIcon, 
  ShieldCheck, 
  Activity, 
  Search, 
  LayoutDashboard,
  Layers,
  Settings,
  Bell,
  ArrowUpRight,
  ArrowDownRight,
  Globe,
  Database,
  ChevronDown,
  Info,
  Clock,
  Zap,
  BarChart3,
  LineChart,
  Target,
  Monitor,
  Menu,
  X
} from 'lucide-react';
import OpportunityHeatmap from './OpportunityHeatmap';
import LocalitiesView from './LocalitiesView';
import DiagnosticsView from './DiagnosticsView';
import api from '@/lib/api';

const CITIES = ['Entire NCR', 'Gurgaon', 'Noida', 'Greater Noida'];

const AnalyticalDashboard = () => {
  const [activeCity, setActiveCity] = useState('Entire NCR');
  const [activeView, setActiveView] = useState('Command Center');
  const [isCityOpen, setIsCityOpen] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  // Responsive Check
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    const fetchSummary = async () => {
      setIsLoading(true);
      try {
        const data = await api.getDashboardSummary(activeCity === 'Entire NCR' ? undefined : activeCity);
        setSummary(data);
      } catch (err) {
        console.error('Dashboard synchronization failure', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSummary();
  }, [activeCity]);

  // Main Dynamic View Controller (Desktop vs Mobile)
  const renderContent = () => {
    if (isMobile) return renderMobileHUD();
    return renderDesktopHUD();
  };

  const renderDesktopHUD = () => (
    <div className="flex h-screen bg-[#050505] text-[#E5E5E5] font-sans selection:bg-brand/30 selection:text-brand overflow-hidden">
      {/* Institutional Sidebar — "Sovereign Rail" */}
      <aside className="w-72 border-r border-white/[0.06] bg-black/40 backdrop-blur-3xl flex flex-col p-8 overflow-hidden hidden xl:flex shrink-0">
        <div className="flex items-center gap-4 mb-12 px-2 group cursor-pointer" onClick={() => setActiveView('Command Center')}>
          <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-[0_0_30px_-5px_var(--brand-purple-glow)] group-hover:scale-110 transition-transform">
            <ShieldCheck className="text-white" size={20} />
          </div>
          <span className="font-black tracking-[0.3em] text-[10px] text-white/40 uppercase group-hover:text-white transition-colors">
            Intel<br />Terminal
          </span>
        </div>

        <nav className="flex-1 space-y-2">
          <NavItem icon={<LayoutDashboard />} label="Command Center" active={activeView === 'Command Center'} onClick={() => setActiveView('Command Center')} />
          <NavItem icon={<MapIcon />} label="Spatial Index" active={activeView === 'Spatial Index'} onClick={() => setActiveView('Spatial Index')} />
          <NavItem icon={<Activity />} label="Valuation Engine" active={activeView === 'Valuation Engine'} onClick={() => setActiveView('Valuation Engine')} />
          <NavItem icon={<Globe />} label="Market Trends" active={activeView === 'Market Trends'} onClick={() => setActiveView('Market Trends')} />
          <div className="h-px bg-white/5 my-6" />
          <NavItem icon={<Layers />} label="Localities" active={activeView === 'Localities'} onClick={() => setActiveView('Localities')} />
          <NavItem icon={<TrendingUp />} label="ROI Analytics" disabled />
        </nav>

        <div className="pt-8 border-t border-white/5 space-y-6">
          <div className="px-5 py-4 bg-white/[0.02] rounded-2xl border border-white/5">
            <div className="flex justify-between items-center mb-3">
              <p className="text-[9px] font-black text-white/20 uppercase tracking-widest">Processing</p>
              <span className="text-[9px] font-black text-primary">42.8%</span>
            </div>
            <div className="h-1 bg-white/5 rounded-full overflow-hidden">
              <motion.div animate={{ width: '42.8%' }} className="h-full bg-primary" />
            </div>
          </div>
          <NavItem icon={<Settings />} label="Diagnostics" active={activeView === 'Diagnostics'} onClick={() => setActiveView('Diagnostics')} />
        </div>
      </aside>

      {/* Main Command Center */}
      <main className="flex-1 overflow-hidden flex flex-col relative">
        {/* Header Ticker Tier */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-black/20 backdrop-blur-xl shrink-0 z-50">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <span className="text-[10px] font-mono text-white/30 uppercase tracking-[0.2em] leading-none">Market Status:</span>
              <span className="flex items-center gap-2 text-[10px] font-mono text-green-400 font-bold tracking-widest">
                <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.5)]" />
                ACTIVE ENGINE
              </span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            
            <div className="relative">
              <button onClick={() => setIsCityOpen(!isCityOpen)} className="flex items-center gap-3 px-3 py-1.5 rounded-lg hover:bg-white/5 transition-all group">
                <div className="flex flex-col items-start text-left">
                  <span className="text-[8px] font-mono text-white/30 uppercase tracking-[0.2em] mb-1">Jurisdiction Set</span>
                  <span className="text-[10px] font-mono text-white/80 font-black tracking-[0.1em] uppercase flex items-center gap-2">
                    {activeCity} <ChevronDown className={`w-3 h-3 transition-transform duration-300 ${isCityOpen ? 'rotate-180' : ''}`} />
                  </span>
                </div>
              </button>
              <AnimatePresence>
                {isCityOpen && (
                  <motion.div initial={{ opacity: 0, y: 10, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 10, scale: 0.95 }} className="absolute top-full left-0 mt-2 w-48 bg-[#0A0A0A] border border-white/10 rounded-xl shadow-2xl z-[100] py-2 overflow-hidden backdrop-blur-2xl">
                    {CITIES.map((city) => (
                      <button key={city} onClick={() => { setActiveCity(city); setIsCityOpen(false); }} className={`w-full text-left px-4 py-2 text-[10px] uppercase tracking-widest font-bold transition-colors hover:bg-brand/10 ${activeCity === city ? 'text-brand' : 'text-white/40 hover:text-white/80'}`}>{city}</button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <h1 className="text-[10px] font-mono text-white/30 uppercase tracking-[0.3em] border-l border-white/10 pl-6 hidden lg:block">Module: <span className="text-white font-black">{activeView}</span></h1>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center border border-white/10 hover:border-brand/40 transition-all cursor-pointer"><Bell size={14} className="text-white/40" /></div>
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand to-brand/60 border border-white/20 p-[1.5px] cursor-pointer hover:scale-110 transition-transform">
                <div className="w-full h-full rounded-lg bg-black flex items-center justify-center overflow-hidden">
                  <img src="https://avatar.vercel.sh/admin" alt="Avatar" className="w-full h-full object-cover opacity-80" />
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
          <AnimatePresence mode="wait">
            {!isLoading && summary ? (
              <motion.div key={activeView + activeCity} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.3 }} className="h-full">
                {renderViewContent()}
              </motion.div>
            ) : (
              <LoadingView activeCity={activeCity} />
            )}
          </AnimatePresence>
        </div>

        <footer className="h-10 border-t border-white/5 bg-black/40 backdrop-blur-xl px-8 flex items-center justify-between shrink-0 z-50">
          <div className="flex items-center gap-6 text-[9px] font-mono font-bold tracking-widest text-white/40 uppercase">
            <span className="flex items-center gap-2 font-black tracking-widest uppercase"><div className="w-1.5 h-1.5 bg-green-500 rounded-full" /> SYSTEM READY</span>
            <span className="flex items-center gap-2 font-black tracking-widest uppercase"><div className="w-1.5 h-1.5 bg-brand rounded-full" /> {activeView} ACTIVE</span>
          </div>
          <p className="text-[9px] font-mono font-bold tracking-widest text-white/20 uppercase font-black">v3.4.2 | {activeCity}</p>
        </footer>
      </main>
    </div>
  );

  const renderMobileHUD = () => (
    <div className="flex flex-col h-screen bg-[#050505] text-[#E5E5E5] font-sans overflow-hidden">
      {/* Mobile Top HUD */}
      <header className="px-6 py-4 border-b border-white/5 bg-black/40 backdrop-blur-xl flex items-center justify-between z-50">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 bg-brand rounded flex items-center justify-center text-black font-black text-xs shadow-[0_0_15px_rgba(var(--brand-rgb),0.3)]">N</div>
          <span className="font-black tracking-widest text-[10px] uppercase">INTEL ENGINE</span>
        </div>
        <button onClick={() => setIsCityOpen(!isCityOpen)} className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-lg border border-white/10 text-[9px] font-mono font-black uppercase tracking-widest">
          {activeCity} <ChevronDown className={`w-3 h-3 transition-transform duration-300 ${isCityOpen ? 'rotate-180' : ''}`} />
        </button>
      </header>

      {/* Mobile Main Stack */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar pb-24">
        <AnimatePresence mode="wait">
          {!isLoading && summary ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              {/* Ticker for Mobile */}
              <div className="bg-brand/5 border border-brand/20 rounded-lg py-2 px-4 shadow-[0_0_15px_rgba(var(--brand-rgb),0.1)]">
                <div className="flex items-center gap-4 whitespace-nowrap animate-marquee font-mono text-[8.5px] font-black uppercase tracking-widest text-brand">
                  <span>MARKET SURGE: GURGAON SECTOR 58 (+14.2%)</span>
                  <span className="w-1 h-1 rounded-full bg-white/20" />
                  <span>ALERT: NOIDA SEC 150 INFLOW</span>
                  <span className="w-1 h-1 rounded-full bg-white/20" />
                  <span>BULLISH: GREATER NOIDA POOL ACTIVE</span>
                </div>
              </div>

              {/* Metrics vertical grid */}
              <div className="grid grid-cols-2 gap-4">
                <MetricCard label="Median Val" value={summary.median_asset_value} trend="+12.4%" up sparkline={[60, 80, 95]} />
                <MetricCard label="Velocity" value={summary.growth_index} trend="HI" up sparkline={[40, 85]} />
              </div>

              {/* Large Sentiment Gauge for Mobile */}
              <SentimentCard activeCity={activeCity} />

              {/* Performance List */}
              <section className="bg-white/[0.02] border border-white/5 rounded-2xl p-5 space-y-4 shadow-xl">
                <h3 className="font-bold text-white text-[9px] uppercase tracking-[0.3em] mb-4">Top Alpha Pockets</h3>
                <div className="space-y-3">
                  {summary.top_localities.slice(0, 5).map((loc: any, i: number) => (
                    <LocalityItem key={loc.name} {...loc} delay={i * 0.1} />
                  ))}
                </div>
              </section>

              {/* Large CTA / Desktop Lock */}
              <div className="bg-gradient-to-tr from-brand/5 to-transparent border border-white/5 rounded-2xl p-6 text-center space-y-3">
                <Monitor className="w-6 h-6 text-brand mx-auto opacity-40" />
                <p className="text-[10px] font-black uppercase tracking-widest text-white/80">Full Spatial Radar Locked</p>
                <p className="text-[8px] font-mono text-white/30 uppercase tracking-widest leading-relaxed">The H3 Spatial Grid requires a desktop resolution to render precision listing coordinates.</p>
              </div>
            </motion.div>
          ) : (
            <div className="h-[60vh] flex flex-col items-center justify-center gap-6">
              <div className="w-10 h-10 border-2 border-brand/20 border-t-brand rounded-full animate-spin" />
              <p className="text-[9px] font-mono tracking-[0.5em] text-brand uppercase animate-pulse">Syncing HUD...</p>
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Mobile Footer (City Modal integration) */}
      <AnimatePresence>
        {isCityOpen && (
          <div className="fixed inset-0 z-[100] flex items-end">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/80 backdrop-blur-lg" onClick={() => setIsCityOpen(false)} />
            <motion.div initial={{ y: 300 }} animate={{ y: 0 }} exit={{ y: 300 }} transition={{ type: 'spring', damping: 25 }} className="w-full bg-[#0A0A0A] border-t border-white/10 rounded-t-3xl p-8 pb-12 relative z-[101] shadow-2xl">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-white font-black text-xs uppercase tracking-widest">Select Jurisdiction</h3>
                <X className="text-white/40" onClick={() => setIsCityOpen(false)} />
              </div>
              <div className="flex flex-col gap-3">
                {CITIES.map((city) => (
                  <button key={city} onClick={() => { setActiveCity(city); setIsCityOpen(false); }} className={`w-full py-4 rounded-xl border font-black text-[10px] uppercase tracking-widest transition-all ${activeCity === city ? 'bg-brand text-black border-brand' : 'bg-white/5 text-white/60 border-white/5 hover:border-brand/30'}`}>{city}</button>
                ))}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );

  const renderViewContent = () => {
    if (activeView === 'Command Center') return renderCommandCenter();
    if (activeView === 'Spatial Index') return renderSpatialIndex();
    if (activeView === 'Valuation Engine') return renderValuationEngine();
    if (activeView === 'Market Trends') return renderMarketTrends();
    if (activeView === 'Localities') return <LocalitiesView city={activeCity === 'Entire NCR' ? 'Gurgaon' : activeCity} />;
    if (activeView === 'Diagnostics') return <DiagnosticsView />;
    return null;
  };

  const renderCommandCenter = () => (
    <div className="space-y-8">
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard label="Median Asset Value" value={summary.median_asset_value} trend="+12.4%" up sparkline={[60, 65, 80, 75, 90, 85, 95]} />
        <MetricCard label="Market Velocity" value={`${summary.growth_index}/100`} trend="ACCELERATING" up sparkline={[40, 50, 60, 75, 85, 88]} />
        <MetricCard label="Institutional Cells" value={summary.hotspots_count} trend="GLOBAL" up sparkline={[100, 100, 100, 100]} />
        <MetricCard label="Predict Integrity" value={`${summary.confidence || 98.4}%`} trend="PRECISION" up sparkline={[90, 95, 98, 98.4]} valueClass="text-primary" />
      </section>
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        <div className="lg:col-span-3 space-y-6">
          <section className="institutional-card group min-h-[550px] relative">
            <div className="p-6 border-b border-white/5 flex items-center justify-between absolute top-0 left-0 right-0 z-20 bg-black/60 backdrop-blur-xl">
              <div className="flex items-center gap-3">
                <MapIcon className="w-4 h-4 text-primary" />
                <h3 className="font-black text-white tracking-[0.2em] text-[9px] uppercase">Sovereign Spatial Grid</h3>
              </div>
              <button onClick={() => setActiveView('Spatial Index')} className="text-[9px] font-black text-primary border border-primary/20 px-3 py-1.5 rounded-lg hover:bg-primary/10 transition-all uppercase tracking-widest">
                Toggle Full Depth
              </button>
            </div>
            <div className="h-[550px] relative">
              <OpportunityHeatmap city={activeCity === 'Entire NCR' ? undefined : activeCity} />
            </div>
          </section>
          
          <section className="bg-primary/5 border border-primary/20 rounded-2xl py-4 px-8 overflow-hidden relative">
            <div className="flex items-center gap-12 whitespace-nowrap animate-marquee hover:pause cursor-default">
              <TickerItem label="HOTSPOT" value="SECTOR 58 GURGAON: +14.2% ROI TARGET" />
              <TickerItem label="ALERT" value="NOIDA SEC 150: INSTITUTIONAL INFLOW DETECTED" />
              <TickerItem label="SENTIMENT" value="GREATER NOIDA: BULLISH (8.2/10)" />
              <TickerItem label="LIQUIDITY" value="FARIDABAD: STAGNANT" />
              <TickerItem label="HOTSPOT" value="SECTOR 79 GURGAON: HIGH YIELD CELL RENDERED" />
            </div>
          </section>
        </div>
        <div className="space-y-6">
          <section className="institutional-card p-8 space-y-8">
            <div className="flex items-center justify-between border-b border-white/5 pb-4">
              <h3 className="font-black text-white text-[9px] uppercase tracking-[0.3em]">Alpha Performers</h3>
              <Activity className="w-4 h-4 text-primary" />
            </div>
            <div className="space-y-3">
              {summary.top_localities.slice(0, 6).map((loc: any, i: number) => (
                <LocalityItem key={loc.name} {...loc} delay={i * 0.1} />
              ))}
            </div>
          </section>
          <SentimentCard activeCity={activeCity} />
        </div>
      </div>
    </div>
  );

  const renderSpatialIndex = () => (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-[75vh] relative rounded-2xl overflow-hidden border border-white/10 shadow-3xl bg-black"><div className="absolute top-6 left-6 z-20 flex flex-col gap-2"><h2 className="text-white font-black text-xl tracking-[0.2em] mb-4 uppercase">SPATIAL HUD</h2><div className="p-4 bg-black/80 backdrop-blur-xl border border-white/10 rounded-xl space-y-4 w-64 shadow-2xl"><div><p className="text-[8px] text-white/40 uppercase font-mono tracking-widest mb-2">Cell Resolution</p><div className="grid grid-cols-2 gap-2"><button className="px-2 py-1 bg-brand text-black text-[9px] font-bold rounded uppercase">Res-8</button><button className="px-2 py-1 bg-white/5 text-white/40 text-[9px] font-bold rounded uppercase">Res-9</button></div></div><button className="w-full py-2 bg-white/5 text-white text-[9px] font-bold rounded border border-white/10 uppercase hover:bg-white/10 transition-all">Download Lat/Long Pool</button></div></div><div className="w-full h-full grayscale-[0.5]"><OpportunityHeatmap city={activeCity === 'Entire NCR' ? undefined : activeCity} /></div></motion.div>);
  const renderValuationEngine = () => (<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 lg:grid-cols-2 gap-8"><div className="bg-white/[0.02] border border-white/5 rounded-2xl p-10 space-y-8"><div className="space-y-2"><h2 className="text-2xl font-black text-white uppercase tracking-tighter">Valuation HUD</h2><p className="text-white/40 text-xs font-medium">Predictive asset valuation via spatial tensor analysis.</p></div><div className="space-y-4"><div className="p-4 bg-white/5 rounded-xl border border-white/10 space-y-2"><p className="text-[9px] font-mono text-white/40 uppercase tracking-widest">Selected City</p><p className="text-lg font-bold text-white">{activeCity}</p></div><div className="grid grid-cols-2 gap-4"><div className="p-4 bg-white/5 rounded-xl border border-white/10 space-y-2"><p className="text-[9px] font-mono text-white/40 uppercase tracking-widest">Market Alpha</p><p className="text-xl font-bold text-brand">+2.4%</p></div><div className="p-4 bg-white/5 rounded-xl border border-white/10 space-y-2"><p className="text-[9px] font-mono text-white/40 uppercase tracking-widest">Absorption</p><p className="text-xl font-bold text-white">HI-VOL</p></div></div></div><button className="w-full py-5 bg-brand text-black font-black uppercase tracking-[0.3em] rounded-2xl shadow-xl shadow-brand/20 hover:scale-[1.02] active:scale-[0.98] transition-all">Initialize Batch Valuation</button></div><div className="bg-black/40 border border-white/5 rounded-2xl p-10 flex flex-col items-center justify-center text-center space-y-6"><div className="w-24 h-24 border-2 border-brand/20 border-t-brand rounded-full animate-spin flex items-center justify-center"><Target className="w-8 h-8 text-brand animate-pulse" /></div><div className="space-y-2"><p className="text-[10px] font-mono text-brand uppercase tracking-[0.5em] animate-pulse">Scanning Price Tensors...</p><p className="text-white/20 text-[9px] uppercase tracking-widest">Aggregating Listing Deltas for {activeCity}</p></div></div></motion.div>);
  const renderMarketTrends = () => (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8"><div className="grid grid-cols-1 md:grid-cols-3 gap-6"><div className="bg-white/[0.02] border border-white/5 p-6 rounded-2xl space-y-4"><LineChart className="text-brand mb-2" /><h3 className="text-white font-black text-xs uppercase tracking-widest">Volume Momentum</h3><div className="flex items-end gap-2 h-20">{[40, 60, 55, 75, 45, 90, 85, 100].map((h, i) => (<div key={i} className="flex-1 bg-brand/20 rounded-t-sm" style={{ height: `${h}%` }} />))}</div><p className="text-[9px] text-white/40 uppercase tracking-widest font-mono font-black">+18% YOY Growth</p></div><div className="bg-white/[0.02] border border-white/5 p-6 rounded-2xl space-y-4"><BarChart3 className="text-[#CBFF00] mb-2" /><h3 className="text-white font-black text-xs uppercase tracking-widest">Investor Sentiment</h3><div className="flex items-end gap-2 h-20">{[80, 70, 75, 60, 65, 50, 45, 42].map((h, i) => (<div key={i} className="flex-1 bg-white/10 rounded-t-sm" style={{ height: `${h}%` }} />))}</div><p className="text-[9px] text-white/40 uppercase tracking-widest font-mono font-black">Consolidating</p></div><div className="bg-white/[0.02] border border-white/5 p-6 rounded-2xl space-y-4"><Activity className="text-blue-500 mb-2" /><h3 className="text-white font-black text-xs uppercase tracking-widest">Absorption Velocity</h3><div className="flex items-end gap-2 h-20">{[30, 40, 45, 60, 80, 85, 95, 100].map((h, i) => (<div key={i} className="flex-1 bg-blue-500/20 rounded-t-sm" style={{ height: `${h}%` }} />))}</div><p className="text-[9px] text-white/40 uppercase tracking-widest font-mono font-black">Institutional Demand</p></div></div><div className="bg-white/[0.02] border border-white/5 rounded-2xl p-8 overflow-hidden"><h3 className="text-white font-black text-[10px] uppercase tracking-[0.3em] mb-8">Competitive ROI Matrix</h3><table className="w-full text-left"><thead><tr className="border-b border-white/10 text-[9px] font-mono text-white/20 uppercase tracking-widest"><th className="pb-4">Market Jurisdiction</th><th className="pb-4">Avg. Asset ROI</th><th className="pb-4">Volatility</th><th className="pb-4">Verdict</th></tr></thead><tbody className="text-[11px] font-bold text-white/60">{CITIES.map(city => (<tr key={city} className="border-b border-white/5 hover:bg-white/[0.02] transition-all group font-black"><td className="py-4 group-hover:text-brand transition-colors uppercase tracking-widest">{city}</td><td className="py-4 font-mono">{(8 + Math.random() * 5).toFixed(2)}%</td><td className="py-4 tracking-widest text-[9px]">LOW</td><td className="py-4 text-brand tracking-widest text-[9px]">ACCUMULATE</td></tr>))}</tbody></table></div></motion.div>);

  return renderContent();
};

const LoadingView = ({ activeCity }: { activeCity: string }) => (
  <div className="flex-1 h-[70vh] flex flex-col items-center justify-center gap-8">
    <div className="relative w-20 h-20">
      <motion.div animate={{ rotate: 360 }} transition={{ duration: 4, repeat: Infinity, ease: 'linear' }} className="absolute inset-0 border-2 border-brand/20 border-t-brand rounded-full" />
      <motion.div animate={{ rotate: -360 }} transition={{ duration: 3, repeat: Infinity, ease: 'linear' }} className="absolute inset-4 border-2 border-white/5 border-b-white/40 rounded-full" />
    </div>
    <div className="text-center space-y-4">
      <h2 className="text-lg font-black text-white uppercase tracking-[0.8em] animate-pulse">Syncing Intelligence</h2>
      <p className="text-[9px] font-mono text-white/30 uppercase tracking-[0.3em] font-black">Jurisdiction: {activeCity}</p>
    </div>
  </div>
);

const NavItem = ({ icon, label, active = false, onClick, disabled = false }: any) => (
  <button 
    onClick={!disabled ? onClick : undefined}
    disabled={disabled}
    className={`
    w-full flex items-center gap-4 px-4 py-3 rounded-xl text-[11px] font-bold transition-all group border border-transparent uppercase tracking-[0.2cm]
    ${disabled ? 'opacity-20 cursor-not-allowed' : 'cursor-pointer'}
    ${active 
      ? 'bg-brand/10 text-brand border-brand/20 shadow-[0_0_20px_rgba(var(--brand-rgb),0.1)]' 
      : 'text-white/20 hover:text-white/70 hover:bg-white/[0.04]'}
  `}>
    <span className={`w-4 h-4 transition-transform duration-300 group-hover:scale-110 ${active ? 'text-brand' : 'text-white/30 group-hover:text-white/60'}`}>
      {React.cloneElement(icon as React.ReactElement, { size: 14, strokeWidth: 2.5 })}
    </span>
    {label}
  </button>
);

const SentimentCard = ({ activeCity }: { activeCity: string }) => (
  <section className="bg-white/[0.02] border border-white/5 rounded-2xl p-6 shadow-2xl relative overflow-hidden group">
    <div className="absolute top-0 right-0 w-32 h-32 bg-brand/10 blur-[60px] group-hover:bg-brand/20 transition-all" />
    <h3 className="font-bold text-white text-[10px] uppercase tracking-[0.3em] mb-6">Market Sentiment</h3>
    <div className="flex flex-col items-center gap-4 py-4">
      <div className="relative w-28 h-28">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="56" cy="56" r="48" fill="transparent" stroke="currentColor" strokeWidth="6" className="text-white/5" />
          <motion.circle cx="56" cy="56" r="48" fill="transparent" stroke="currentColor" strokeWidth="6" className="text-brand" strokeDasharray="301.59" initial={{ strokeDashoffset: 301.59 }} animate={{ strokeDashoffset: 301.59 * (1 - 0.82) }} transition={{ duration: 2 }} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-black text-white">82</span>
          <span className="text-[10px] font-mono text-brand font-black">BULLISH</span>
        </div>
      </div>
      <p className="text-[9px] text-white/30 text-center uppercase tracking-widest leading-relaxed font-black">Signal confidence for {activeCity}</p>
    </div>
  </section>
);

const MetricCard = ({ label, value, trend, up = false, sparkline, valueClass = "" }: any) => (
  <motion.div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6 group hover:border-brand/40 transition-all duration-700 relative overflow-hidden shadow-2xl">
    <div className="absolute inset-0 bg-gradient-to-br from-brand/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
    <p className="text-[9px] text-white/20 font-mono uppercase tracking-[0.3em] mb-4 leading-none font-black">{label}</p>
    <div className="flex items-end justify-between gap-4 relative z-10">
      <div>
        <h4 className={`text-xl font-black tracking-tight text-white mb-2 leading-none font-black ${valueClass}`}>{value}</h4>
        <div className={`text-[8px] font-mono font-black flex items-center gap-1.5 px-2 py-0.5 rounded-full ${up ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
          {up ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />} {trend}
        </div>
      </div>
      <div className="flex items-end gap-1 h-8">
        {sparkline.map((val: number, i: number) => (
          <div key={i} className="w-[2px] bg-brand/30 rounded-t-full transition-all group-hover:bg-brand" style={{ height: `${(val / Math.max(...sparkline)) * 100}%`, opacity: 0.2 + (i / sparkline.length) * 0.8 }} />
        ))}
      </div>
    </div>
  </motion.div>
);

const LocalityItem = ({ name, city, score, delta, growth, delay = 0 }: any) => (
  <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay }} className="flex items-center justify-between p-4 rounded-xl bg-white/[0.01] border border-white/5 hover:bg-white/[0.04] hover:border-brand/20 transition-all cursor-pointer group">
    <div className="flex items-center gap-3"><div className={`w-8 h-8 rounded-lg bg-black/40 border border-white/10 flex items-center justify-center text-[10px] font-mono font-black ${score > 90 ? 'text-brand' : 'text-white/30'}`}>{score}</div><div><p className="text-[10px] font-black text-white group-hover:text-brand transition-colors uppercase tracking-wider font-black">{name}</p><p className="text-[8px] text-white/20 uppercase tracking-widest leading-none font-black">{city}</p></div></div>
    <div className="text-right"><p className={`text-[9px] font-mono font-black ${growth === 'surge' ? 'text-green-400' : 'text-white/40'}`}>{delta}</p><div className="w-12 h-1 bg-white/5 rounded-full mt-2 overflow-hidden"><div className={`h-full ${score > 90 ? 'bg-brand' : 'bg-white/20'}`} style={{ width: `${score}%` }} /></div></div>
  </motion.div>
);

const TickerItem = ({ label, value }: { label: string, value: string }) => (
  <div className="flex items-center gap-3 mr-12 group cursor-default"><span className="text-[9px] font-mono font-black text-brand bg-brand/10 px-2 py-0.5 rounded border border-brand/20 uppercase">{label}</span><span className="text-[10px] font-bold text-white/60 group-hover:text-white transition-colors tracking-widest uppercase font-black">{value}</span></div>
);

export default AnalyticalDashboard;
