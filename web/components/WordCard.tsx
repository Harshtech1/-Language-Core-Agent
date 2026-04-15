"use client";

interface WordData {
  hanzi: string;
  pinyin: string;
  meaning_core: string;
  etymology?: string;
  cultural_note?: string;
  example_sentences?: { zh: string; pinyin: string; en: string }[];
}

export default function WordCard({ word }: { word: WordData }) {
  return (
    <div className="glass-panel p-10 relative overflow-hidden group">
      {/* Decorative Gradient Glow */}
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-[var(--accent-gold)]/5 rounded-full blur-[120px] group-hover:bg-[var(--accent-gold)]/10 transition-all duration-1000" />
      
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-10">
        {/* Main Content: Hanzi & Pinyin */}
        <div className="lg:col-span-12 xl:col-span-5 flex flex-col justify-center border-b xl:border-b-0 xl:border-r border-[var(--bg-border)]/50 pb-8 xl:pb-0 xl:pr-10">
          <div className="relative">
            <span className="absolute -top-6 -left-2 text-[10px] uppercase tracking-[0.4em] text-[var(--accent-gold)] font-bold opacity-60">
              Today's Archetype
            </span>
            <h2 
              className="text-[12rem] xl:text-[14rem] leading-none font-medium text-[var(--accent-gold)] glow-gold select-none"
              style={{ fontFamily: '"Noto Sans SC", sans-serif' }}
            >
              {word.hanzi}
            </h2>
          </div>
          
          <div className="mt-4">
            <p className="text-4xl text-[var(--accent-cyan)] font-light tracking-wider drop-shadow-sm uppercase">
              {word.pinyin}
            </p>
            <p className="text-lg text-[var(--text-secondary)] mt-2 font-medium tracking-widest uppercase">
              {word.meaning_core}
            </p>
          </div>
        </div>

        {/* Details: Etymology & Usage */}
        <div className="lg:col-span-12 xl:col-span-7 space-y-8 py-2">
          {/* Etymology & Culture */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {word.etymology && (
              <div className="glass-card p-5 hover:border-[var(--accent-gold)]/30">
                <h3 className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] mb-3 font-bold">
                  Historical Roots
                </h3>
                <p className="text-sm text-[var(--text-primary)]/90 leading-relaxed font-light italic">
                  "{word.etymology}"
                </p>
              </div>
            )}
            {word.cultural_note && (
              <div className="glass-card p-5 hover:border-[var(--accent-cyan)]/30">
                <h3 className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] mb-3 font-bold">
                  Cultural Resonance
                </h3>
                <p className="text-sm text-[var(--text-primary)]/90 leading-relaxed font-light">
                  {word.cultural_note}
                </p>
              </div>
            )}
          </div>

          {/* Dynamic Example Usage */}
          {word.example_sentences && word.example_sentences.length > 0 && (
            <div className="pt-4">
              <h3 className="text-[10px] uppercase tracking-[0.3em] text-[var(--text-muted)] mb-6 font-bold flex items-center gap-2">
                <span className="w-8 h-[1px] bg-[var(--bg-border)]" />
                Contextual Integration
              </h3>
              <div className="space-y-6">
                {word.example_sentences.map((ex, i) => (
                  <div 
                    key={i} 
                    className="group/ex relative pl-6 transition-all duration-300 border-l border-[var(--bg-border)] hover:border-[var(--accent-gold)]"
                  >
                    <p 
                      className="text-2xl text-[var(--text-primary)] group-hover/ex:text-[var(--accent-gold)] transition-colors duration-300" 
                      style={{ fontFamily: '"Noto Sans SC", sans-serif' }}
                    >
                      {ex.zh}
                    </p>
                    <div className="flex flex-wrap items-baseline gap-x-4 mt-2">
                      <p className="text-sm text-[var(--accent-cyan)]/80 font-medium">
                        {ex.pinyin}
                      </p>
                      <p className="text-sm text-[var(--text-muted)] font-light">
                        {ex.en}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
