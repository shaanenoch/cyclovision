import React, { useState } from 'react';
import { Search, MapPin, Navigation, Compass, AlertCircle, X, ShieldAlert } from 'lucide-react';
import api from '../services/api';

export default function SearchBar({ onSelectLocation, activeCyclone }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  const quickSearches = [
    "Bay of Bengal",
    "Odisha",
    "Visakhapatnam",
    "Chennai",
    "15.2, 84.7"
  ];

  const handleSearch = async (searchTerm) => {
    const term = searchTerm || query;
    if (!term || term.trim().length === 0) return;

    setLoading(true);
    setIsOpen(true);
    try {
      const data = await api.search(term);
      setResults(data);
    } catch (err) {
      console.error("Search error:", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleSelect = (item) => {
    if (onSelectLocation) {
      onSelectLocation(item);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto my-4 z-40">
      {/* Search Input Box */}
      <div className="relative flex items-center shadow-2xl rounded-2xl bg-navy-900/90 border border-navy-700/80 focus-within:border-cyan-500/80 focus-within:ring-2 focus-within:ring-cyan-500/20 transition-all">
        <div className="pl-4 text-cyan-400">
          <Search className="w-5 h-5" />
        </div>
        
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (e.target.value.length > 2) handleSearch(e.target.value);
          }}
          onKeyDown={handleKeyDown}
          placeholder="Search cyclone, location, latitude or longitude..."
          className="w-full py-3.5 pl-3 pr-10 bg-transparent text-sm text-slate-100 placeholder-slate-400 focus:outline-none"
        />

        {query && (
          <button 
            onClick={() => { setQuery(''); setResults([]); setIsOpen(false); }}
            className="p-2 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <button
          onClick={() => handleSearch()}
          disabled={loading}
          className="mr-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-navy-950 font-semibold text-xs tracking-wide shadow-glow-cyan transition-all"
        >
          {loading ? 'Searching...' : 'Explore'}
        </button>
      </div>

      {/* Quick Suggestions Chips */}
      <div className="flex flex-wrap items-center gap-2 mt-2 px-1 text-xs text-slate-400">
        <span className="font-mono text-[11px] text-slate-400 flex items-center gap-1">
          <Navigation className="w-3 h-3 text-cyan-400" /> Quick Jump:
        </span>
        {quickSearches.map((chip) => (
          <button
            key={chip}
            onClick={() => {
              setQuery(chip);
              handleSearch(chip);
            }}
            className="px-2.5 py-1 rounded-lg bg-navy-850/80 hover:bg-navy-800 border border-navy-750 text-slate-300 hover:text-cyan-300 transition-colors font-medium text-[11px]"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Dropdown Results Box */}
      {isOpen && results.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-2 bg-navy-900 border border-navy-700/90 rounded-2xl shadow-2xl overflow-hidden z-50 divide-y divide-navy-800">
          <div className="p-2.5 bg-navy-950/60 flex items-center justify-between text-[11px] text-slate-400 px-4">
            <span>Search Results ({results.length})</span>
            <span className="text-cyan-400">Click to focus on interactive map</span>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {results.map((item, idx) => (
              <div
                key={idx}
                onClick={() => handleSelect(item)}
                className="p-3.5 hover:bg-navy-800/80 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2.5">
                    <div className="mt-0.5 p-1.5 rounded-lg bg-cyan-950/60 border border-cyan-800/50 text-cyan-400">
                      <MapPin className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-100">{item.title}</h4>
                      <p className="text-xs text-slate-400 font-mono mt-0.5">{item.subtitle}</p>
                    </div>
                  </div>

                  <div className="text-right font-mono text-xs text-slate-400 whitespace-nowrap">
                    {item.lat.toFixed(2)}°N, {item.lon.toFixed(2)}°E
                  </div>
                </div>

                {item.estimated_path_note && (
                  <div className="mt-2.5 ml-9 p-2 rounded-lg bg-navy-950/80 border border-navy-800 text-[11px] text-cyan-200/90 flex items-start gap-1.5">
                    <Compass className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-cyan-300">Trajectory Estimation: </span>
                      <span>{item.estimated_path_note}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Landfall Disclaimer */}
          <div className="p-2.5 bg-navy-950/90 text-center text-[11px] text-slate-400 flex items-center justify-center gap-1.5 border-t border-navy-800">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
            <span>Advisory: Displays <strong>estimated path</strong> based on numerical modeling — not an official warning.</span>
          </div>
        </div>
      )}
    </div>
  );
}
