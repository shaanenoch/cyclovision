import React from 'react';
import { Activity, Radio, Satellite, Compass, Database, BarChart3, Info, AlertTriangle } from 'lucide-react';

export default function Navbar({ currentTab, onSelectTab, isDemo = true }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'detection', label: 'Cyclone Detection', icon: Satellite },
    { id: 'prediction', label: 'Track Prediction', icon: Compass },
    { id: 'datasets', label: 'Datasets', icon: Database },
    { id: 'analytics', label: 'Model Analytics', icon: BarChart3 },
    { id: 'about', label: 'About', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 bg-navy-900/90 backdrop-blur-md border-b border-navy-750 px-4 lg:px-8 py-3 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo */}
        <div 
          onClick={() => onSelectTab('dashboard')} 
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="relative w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-glow-cyan">
            <Radio className="w-5 h-5 text-white animate-spin-slow" />
            <div className="absolute inset-0 rounded-xl border border-cyan-400/40" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-cyan-200 to-cyan-400 bg-clip-text text-transparent">
                CycloneAI
              </span>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-700/50">
                SIH Prototype
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono tracking-tight hidden sm:block">
              Multi-Source Satellite Intelligence & Forecast
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-navy-950/60 p-1.5 rounded-xl border border-navy-800">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Status Indicators & Demo Badge */}
        <div className="flex items-center gap-3">
          {isDemo && (
            <div className="flex items-center gap-1.5 bg-amber-950/40 border border-amber-600/40 text-amber-400 px-2.5 py-1 rounded-full text-xs font-medium shadow-sm">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden sm:inline">Demonstration Dataset</span>
              <span className="sm:hidden">Demo</span>
            </div>
          )}

          <div className="flex items-center gap-2 bg-navy-950/80 border border-navy-800 px-3 py-1.5 rounded-lg">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
            </span>
            <div className="flex flex-col text-left">
              <span className="text-[10px] text-slate-400 leading-none">Model Status</span>
              <span className="text-xs font-mono font-semibold text-cyan-300 leading-tight">Online</span>
            </div>
          </div>
        </div>

      </div>

      {/* Mobile Nav Bar */}
      <div className="md:hidden flex items-center justify-around mt-2 pt-2 border-t border-navy-800/80 overflow-x-auto gap-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex flex-col items-center gap-1 px-2.5 py-1 rounded-md text-[11px] whitespace-nowrap ${
                isActive ? 'text-cyan-300 font-semibold' : 'text-slate-400'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
