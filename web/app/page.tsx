import ThreeBackground from "@/components/ThreeBackground";
import MasteryTree from "@/components/MasteryTree";
import WordCard from "@/components/WordCard";
import StatsRing from "@/components/StatsRing";

async function getTodayWord() {
  try {
    const res = await fetch(
      `${process.env.API_URL || "http://localhost:8000"}/vocab/today`,
      { next: { revalidate: 0 } }
    );
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getStats() {
  try {
    const res = await fetch(
      `${process.env.API_URL || "http://localhost:8000"}/stats/overview`,
      { next: { revalidate: 0 } }
    );
    if (!res.ok) return { streak: 0, mastered: 0, due_today: 0 };
    const data = await res.json();
    return {
      streak: data.streak ?? 0,
      mastered: data.mastered ?? 0,
      due_today: data.due_today ?? 0,
    };
  } catch {
    return { streak: 0, mastered: 0, due_today: 0 };
  }
}

export default async function Dashboard() {
  const [todayWord, stats] = await Promise.all([getTodayWord(), getStats()]);

  return (
    <main className="min-h-screen relative overflow-hidden bg-[var(--bg-base)]">
      <ThreeBackground />
      
      <div className="relative z-10 max-w-[1600px] mx-auto p-6 md:p-12 lg:p-16">
        {/* Professional Luxury Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-20 gap-6">
          <div className="space-y-2">
            <h1 className="text-4xl tracking-[-0.04em] font-extralight text-[var(--accent-gold)] glow-gold">
              Language Core <span className="text-[var(--text-muted)] font-thin mx-2">/</span> <span className="tracking-[0.2em] font-normal uppercase text-sm">Autonomous Agent</span>
            </h1>
            <p className="text-[10px] uppercase tracking-[0.5em] text-[var(--text-muted)] font-bold">
              Operational Sequence: 730-Day Mastery Loop
            </p>
          </div>
          
          <div className="glass-card px-6 py-3 flex items-center gap-4 border-[var(--bg-border)]/40 hover:border-[var(--accent-gold)]/30 transition-all cursor-default">
            <div className="w-2 h-2 rounded-full bg-[var(--status-success)] shadow-[0_0_10px_var(--status-success)]" />
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] font-bold">System Status</span>
              <span className="text-xs font-mono text-[var(--text-primary)]">ACTIVE_OPERATIONAL</span>
            </div>
          </div>
        </header>

        {/* Tactical Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-16">
          <div className="lg:col-span-4 xl:col-span-3 h-full">
            <StatsRing
              streak={stats.streak}
              mastered={stats.mastered}
              dueToday={stats.due_today}
            />
          </div>

          <div className="lg:col-span-8 xl:col-span-9 h-full">
            {todayWord ? (
              <WordCard word={todayWord} />
            ) : (
              <div className="glass-panel p-20 flex flex-col items-center justify-center text-center">
                <div className="w-12 h-12 border-2 border-[var(--bg-border)] border-t-[var(--accent-gold)] rounded-full animate-spin mb-6" />
                <h3 className="text-xl font-light text-[var(--text-secondary)] tracking-widest uppercase mb-2">Idle Sequence</h3>
                <p className="text-sm text-[var(--text-muted)] uppercase tracking-widest">Awaiting daily vocabulary injection at 08:00 IST</p>
              </div>
            )}
          </div>
        </div>

        {/* Knowledge Base Section */}
        <section className="mt-20">
          <div className="flex items-center gap-6 mb-12">
            <h2 className="text-2xl font-light tracking-tight text-[var(--text-primary)]">
              Conceptual <span className="text-[var(--accent-cyan)] uppercase text-xs tracking-[0.3em] font-bold ml-2">Mapping</span>
            </h2>
            <div className="h-[1px] flex-grow bg-gradient-to-r from-[var(--bg-border)] to-transparent" />
          </div>
          
          <div className="glass-panel p-2 min-h-[400px]">
            <MasteryTree />
          </div>
        </section>
      </div>
    </main>
  );
}