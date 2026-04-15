import React from "react";

interface StatsRingProps {
  streak: number;
  mastered: number;
  dueToday: number;
}

export default function AgentTelemetry({ streak, mastered, dueToday }: StatsRingProps) {
  const masteryProgress = Math.min((mastered / 1200) * 100, 100);

  return (
    <div className="glass-panel p-8 h-full flex flex-col justify-between shadow-2xl relative overflow-hidden">
      {/* Background Grid Pattern */}
      <div className="absolute inset-x-0 top-0 h-40 bg-[radial-gradient(var(--bg-border)_1px,transparent_1px)] [background-size:20px_20px] [mask-image:linear-gradient(to_bottom,black,transparent)] opacity-20" />
      
      <div className="relative z-10">
        <header className="flex items-center justify-between mb-10">
          <h2 className="uppercase tracking-[0.3em] text-[10px] font-bold text-[var(--accent-gold)]">
            Core Operational Telemetry
          </h2>
          <div className="w-2 h-2 rounded-full bg-[var(--status-success)] animate-pulse shadow-[0_0_8px_var(--status-success)]" />
        </header>
        
        {/* Streak Core */}
        <div className="mb-12 group">
          <div className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] mb-2 font-bold group-hover:text-[var(--text-secondary)] transition-colors">
            Activity Continuity
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-7xl font-extralight text-[var(--text-primary)] tracking-tighter glow-gold">
              {streak}
            </span>
            <span className="text-xs uppercase tracking-[0.4em] text-[var(--accent-gold)]/60 font-medium">
              Cycles
            </span>
          </div>
        </div>

        {/* Progress Matrix */}
        <div className="space-y-8">
          {/* Mastery */}
          <div className="relative">
            <div className="flex justify-between items-end mb-3">
              <span className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] font-bold">
                Linguistic Mastery
              </span>
              <span className="text-[var(--accent-cyan)] font-mono text-sm tracking-tighter">
                {mastered.toString().padStart(4, '0')} / 1200
              </span>
            </div>
            <div className="h-[2px] w-full bg-[var(--bg-border)]/30 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-[var(--accent-cyan)] to-[var(--text-primary)] shadow-[0_0_15px_var(--accent-cyan-muted)] transition-all duration-1000 ease-out" 
                style={{ width: `${masteryProgress}%` }}
              />
            </div>
          </div>

          {/* Due Today */}
          <div className="relative">
            <div className="flex justify-between items-end mb-3">
              <span className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] font-bold">
                Review Queue
              </span>
              <span className={dueToday > 0 ? "text-[var(--status-error)] font-mono text-sm tracking-tighter" : "text-[var(--text-muted)] font-mono text-sm tracking-tighter"}>
                {dueToday.toString().padStart(2, '0')} INCOMING
              </span>
            </div>
            <div className="h-[2px] w-full bg-[var(--bg-border)]/30 rounded-full overflow-hidden">
              <div 
                className={`h-full ${dueToday > 0 ? "bg-[var(--status-error)]" : "bg-[var(--bg-border)]"} shadow-[0_0_15px_var(--status-error)/0.3] transition-all duration-1000 ease-out`}
                style={{ width: `${Math.min((dueToday / 10) * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="mt-12 p-5 glass-card border-[var(--bg-border)]/30">
        <p className="text-[10px] text-[var(--text-muted)] leading-relaxed tracking-wider uppercase">
          <span className="text-[var(--accent-gold)] font-bold">Edge Evaluation:</span> High-velocity Gemini Flash pipelines standing by for cycle completion at <span className="text-[var(--text-secondary)]">20:00 IST</span>.
        </p>
      </div>
    </div>
  );
}
