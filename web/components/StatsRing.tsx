import React from "react";

interface StatsRingProps {
  streak: number;
  mastered: number;
  dueToday: number;
}

export default function StatsRing({ streak, mastered, dueToday }: StatsRingProps) {
  return (
    <div className="bg-bg-surface border border-bg-border rounded-2xl p-6 h-full flex flex-col justify-between shadow-xl">
      <div>
        <h2 className="uppercase tracking-widest text-xs text-text-secondary mb-8">Agent Telemetry</h2>
        
        <div className="mb-8">
          <div className="text-sm text-text-secondary mb-1">Active Streak</div>
          <div className="text-5xl font-light text-accent-gold flex items-baseline gap-2">
            {streak} <span className="text-lg text-text-primary/40 uppercase tracking-widest">Days</span>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-text-secondary">Words Mastered</span>
              <span className="text-accent-cyan">{mastered} / 1200</span>
            </div>
            <div className="h-1 bg-bg-base rounded-full overflow-hidden">
              <div 
                className="h-full bg-accent-cyan shadow-[0_0_10px_rgba(11,216,214,0.5)] transition-all duration-1000 ease-out" 
                style={{ width: `${Math.min((mastered / 1200) * 100, 100)}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-text-secondary">Due Today (Evening Eval)</span>
              <span className="text-accent-red">{dueToday}</span>
            </div>
            <div className="h-1 bg-bg-base rounded-full overflow-hidden">
              <div 
                className="h-full bg-accent-red shadow-[0_0_10px_rgba(255,87,87,0.5)] transition-all duration-1000 ease-out" 
                style={{ width: `${Math.min((dueToday / 20) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 p-4 bg-bg-base/50 rounded-xl border border-bg-border/30 backdrop-blur-sm">
        <p className="text-xs text-text-secondary leading-relaxed">
          <span className="text-accent-gold">System Note:</span> Evening evaluations will be delivered via Telegram at 20:00 local time. Use the budget Flash Lite model for reviews to maintain cost constraints.
        </p>
      </div>
    </div>
  );
}
