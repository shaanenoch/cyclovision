import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Detection from './pages/Detection';
import Prediction from './pages/Prediction';
import Datasets from './pages/Datasets';
import Analytics from './pages/Analytics';
import About from './pages/About';
import { ShieldAlert, Terminal, Heart } from 'lucide-react';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [isDemoMode, setIsDemoMode] = useState(true);

  const renderActivePage = () => {
    switch (currentTab) {
      case 'dashboard':
        return <Dashboard onNavigateToTab={(tab) => setCurrentTab(tab)} />;
      case 'detection':
        return <Detection />;
      case 'prediction':
        return <Prediction />;
      case 'datasets':
        return <Datasets />;
      case 'analytics':
        return <Analytics />;
      case 'about':
        return <About />;
      default:
        return <Dashboard onNavigateToTab={(tab) => setCurrentTab(tab)} />;
    }
  };

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100 flex flex-col justify-between selection:bg-cyan-500 selection:text-navy-950">
      
      {/* Top Fixed Command Navbar */}
      <Navbar 
        currentTab={currentTab} 
        onSelectTab={(tab) => setCurrentTab(tab)} 
        isDemo={isDemoMode}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {renderActivePage()}
      </main>

      {/* Footer */}
      <footer className="border-t border-navy-800/80 bg-navy-950/90 py-6 px-4 sm:px-8 mt-12 text-xs font-mono text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-center sm:text-left">
            <span className="font-bold text-cyan-400">CycloneAI</span>
            <span>• Smart India Hackathon (SIH) Prototype</span>
          </div>

          <div className="text-[11px] text-slate-400 text-center">
            Research prototype for cyclone analysis. Forecast outputs must not replace official meteorological warnings.
          </div>

          <div className="flex items-center gap-1.5 text-slate-400">
            <span>FastAPI • PyTorch • React</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
