export default function MasteryTree() {
  return (
    <div className="bg-bg-surface border border-bg-border rounded-2xl p-8 shadow-xl min-h-[300px] flex items-center justify-center relative overflow-hidden group">
      {/* Subtle grid background */}
      <div 
        className="absolute inset-0 opacity-10" 
        style={{ backgroundImage: 'radial-gradient(var(--text-secondary) 1px, transparent 1px)', backgroundSize: '24px 24px' }}
      ></div>
      
      <div className="text-center relative z-10 p-6 backdrop-blur-sm bg-bg-base/30 rounded-xl border border-bg-border/50 transition-all duration-500 group-hover:bg-bg-base/50">
        <h3 className="text-lg text-text-primary mb-2">Neural Node Visualization Offline</h3>
        <p className="text-sm text-text-secondary max-w-sm mx-auto">
          The mastery tree is currently accumulating data points. As you engage with the Telegram bot and complete evening evaluations, clusters of vocabulary nodes will begin to form here.
        </p>
      </div>
    </div>
  );
}
