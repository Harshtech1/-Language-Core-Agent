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
    <main className="min-h-screen relative overflow-hidden">
      <ThreeBackground />
      
      <div className="relative z-10 p-8">
        <header className="flex justify-between items-center mb-12 border-b border-bg-border pb-4">
          <h1 className="text-3xl tracking-tight font-light text-accent-gold">
            Language Core // 730 Days
          </h1>
          <div className="text-sm uppercase tracking-widest text-text-secondary">
            Agent Status: Active
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="col-span-1">
            <StatsRing
              streak={stats.streak}
              mastered={stats.mastered}
              dueToday={stats.due_today}
            />
          </div>

          <div className="col-span-2">
            {todayWord ? (
              <WordCard word={todayWord} />
            ) : (
              <div className="bg-bg-surface rounded-lg p-8 border border-bg-border">
                <p className="text-text-secondary">No word scheduled for today.</p>
              </div>
            )}
          </div>
        </div>

        <section>
          <h2 className="text-xl text-accent-cyan mb-4">Mastery Tree</h2>
          <MasteryTree />
        </section>
      </div>
    </main>
  );
}