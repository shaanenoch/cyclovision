import React from 'react';
import { HelpCircle, Wind, Gauge, Shield, Zap } from 'lucide-react';

export default function StatusCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  badge, 
  badgeColor = 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  tooltip,
  trend,
  highlightColor = 'border-cyan-500/30'
}) {
  return (
    <div className={`relative overflow-hidden rounded-2xl bg-navy-900/80 border ${highlightColor} p-4 sm:p-5 shadow-lg backdrop-blur-md transition-all duration-300 hover:shadow-glow-blue group`}>
      {/* Background ambient glow */}
      <div className="absolute -right-8 -top-8 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl group-hover:bg-cyan-500/10 transition-colors pointer-events-none" />

      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2 text-slate-400 text-xs font-medium uppercase tracking-wider">
          <span>{title}</span>
          {tooltip && (
            <div className="relative group/tooltip">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400 hover:text-cyan-300 cursor-help" />
              <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover/tooltip:block w-48 p-2 rounded-lg bg-navy-950 border border-navy-750 text-[11px] font-normal text-slate-200 shadow-xl z-50 text-center normal-case">
                {tooltip}
                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-navy-950" />
              </div>
            </div>
          )}
        </div>

        {Icon && (
          <div className="p-2 rounded-xl bg-navy-800/80 border border-navy-700/60 text-cyan-400">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-3">
        <span className="text-xl sm:text-2xl font-bold tracking-tight text-white font-mono">
          {value}
        </span>
        {badge && (
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${badgeColor}`}>
            {badge}
          </span>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="mt-2 flex items-center justify-between text-xs text-slate-400 font-mono">
          <span>{subtitle}</span>
          {trend && (
            <span className="text-cyan-400 font-medium">
              {trend}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
