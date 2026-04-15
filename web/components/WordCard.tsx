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
    <div className="bg-bg-surface/60 backdrop-blur-md rounded-2xl p-8 border border-bg-border shadow-2xl relative overflow-hidden group">
      {/* Glow effect */}
      <div className="absolute -top-32 -right-32 w-64 h-64 bg-accent-gold/10 rounded-full blur-3xl group-hover:bg-accent-gold/20 transition-all duration-700"></div>
      
      <div className="relative z-10">
        <div className="flex items-end gap-6 mb-6">
          <h2 className="text-8xl font-medium text-accent-gold tracking-tight" style={{ fontFamily: '"Noto Sans SC", sans-serif' }}>
            {word.hanzi}
          </h2>
          <div className="pb-2">
            <p className="text-3xl text-accent-cyan tracking-wide font-light mb-1">{word.pinyin}</p>
            <p className="text-xl text-text-primary/80 uppercase tracking-widest text-sm">{word.meaning_core}</p>
          </div>
        </div>

        <div className="space-y-6 mt-8">
          {word.etymology && (
            <div className="bg-bg-base/50 p-4 rounded-xl border border-bg-border/50">
              <h3 className="text-xs uppercase tracking-widest text-text-secondary mb-2">Etymology</h3>
              <p className="text-text-primary/90 leading-relaxed font-light">{word.etymology}</p>
            </div>
          )}

          {word.cultural_note && (
            <div className="bg-bg-base/50 p-4 rounded-xl border border-bg-border/50">
              <h3 className="text-xs uppercase tracking-widest text-text-secondary mb-2">Cultural Context</h3>
              <p className="text-text-primary/90 leading-relaxed font-light">{word.cultural_note}</p>
            </div>
          )}

          {word.example_sentences && word.example_sentences.length > 0 && (
            <div className="mt-6">
              <h3 className="text-xs uppercase tracking-widest text-text-secondary mb-3">Example Usage</h3>
              <div className="space-y-4">
                {word.example_sentences.map((ex, i) => (
                  <div key={i} className="pl-4 border-l-2 border-bg-border hover:border-accent-gold transition-colors duration-300">
                    <p className="text-lg text-text-primary" style={{ fontFamily: '"Noto Sans SC", sans-serif' }}>{ex.zh}</p>
                    <p className="text-sm text-accent-cyan/80 mt-1">{ex.pinyin}</p>
                    <p className="text-sm text-text-secondary mt-1 italic">{ex.en}</p>
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
