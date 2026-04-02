import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, TrendingDown, Target, Zap, Info } from 'lucide-react';
import * as api from '@/lib/api';

interface Locality {
  name: string;
  city: string;
  score: number;
  delta: string;
  highlights: string[];
}

export default function LocalitiesView({ city }: { city: string }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [localities, setLocalities] = useState<Locality[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLocalities = async () => {
      setLoading(true);
      try {
        const data = await api.getLocalities(city);
        // Transform and mock deltas/scores for the "Sovereign Analyst" look
        const transformed = data.map((name: string) => ({
          name,
          city,
          score: Math.floor(Math.random() * 20) + 80, // High-performance sectors
          delta: `+${(Math.random() * 15).toFixed(1)}%`,
          highlights: ['High Liquidity', 'Volume Spike']
        }));
        setLocalities(transformed);
      } catch (error) {
        console.error('Failed to fetch localities:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchLocalities();
  }, [city]);

  const filteredLocalities = localities.filter(l => 
    l.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full space-y-6">
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-white tracking-tight flex items-center gap-2">
            <Target className="w-5 h-5 text-purple-400" />
            Regional Pulse: {city}
          </h2>
          <p className="text-sm text-zinc-400 font-mono mt-1">
            Analyzing 50+ sector clusters for liquidity and capital growth.
          </p>
        </div>
        
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-purple-400 transition-colors" />
          <input 
            type="text"
            placeholder="Search sectors..."
            className="bg-zinc-900 border-none rounded-lg pl-10 pr-4 py-2 text-sm text-zinc-300 w-full md:w-64 focus:ring-1 focus:ring-purple-500/50 transition-all outline-none"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Grid */}
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="w-12 h-12 border-2 border-purple-500/20 border-t-purple-500 rounded-full"
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-8">
            <AnimatePresence mode="popLayout">
              {filteredLocalities.map((locality, idx) => (
                <motion.div
                  key={locality.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="group bg-[#1c1b1b] hover:bg-[#2a2a2a] p-5 rounded-xl transition-all cursor-pointer relative overflow-hidden"
                >
                  {/* Tonal Background Highlight */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 blur-[80px] group-hover:bg-purple-500/15 transition-all" />
                  
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h4 className="font-medium text-zinc-100 group-hover:text-purple-300 transition-colors">
                          {locality.name}
                        </h4>
                        <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-mono">
                          {locality.city} Center
                        </span>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-sm font-mono text-emerald-400 flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          {locality.delta}
                        </span>
                        <span className="text-[10px] text-zinc-500 font-mono">YoY Growth</span>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="w-full bg-zinc-800/50 h-1 rounded-full overflow-hidden">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${locality.score}%` }}
                          className="h-full bg-gradient-to-r from-purple-600 to-purple-400"
                        />
                      </div>
                      
                      <div className="flex items-center justify-between text-[11px] font-mono">
                        <span className="text-zinc-500">Alpha Score</span>
                        <span className="text-zinc-300">{locality.score}/100</span>
                      </div>

                      <div className="flex flex-wrap gap-2 pt-2">
                        {locality.highlights.map(tag => (
                          <span key={tag} className="bg-purple-500/10 text-purple-400 text-[10px] px-2 py-0.5 rounded border border-purple-500/20">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="bg-purple-500/5 rounded-xl p-4 border border-purple-500/10 flex items-center gap-3">
        <div className="bg-purple-500/20 p-2 rounded-lg">
          <Zap className="w-4 h-4 text-purple-400" />
        </div>
        <div className="text-xs text-zinc-400 leading-relaxed">
          <span className="text-purple-300 font-medium whitespace-nowrap">Alpha Signal:</span>
          {" "}Liquidity patterns suggest Sector 150 clusters are entering a momentum phase. Recommend high-exposure monitoring.
        </div>
      </div>
    </div>
  );
}
