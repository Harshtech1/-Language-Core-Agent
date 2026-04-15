"use client";

import { useEffect, useRef } from "react";

const HANZI_CHARS = "的一是不了在人有我他这个们中来上大为和国地到以说时要就出会可也你對生能而子那得于着下自之年过发后作里用道行所然家种事成方多经么去法学如都同现当起看定天分还进好小部其些主样理心她本前开但因只";

interface Particle {
  x: number;
  y: number;
  z: number;  // depth layer 0.0–1.0
  char: string;
  speed: number;
  opacity: number;
  size: number;
}

export default function ThreeBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const frameRef = useRef<number>(0);
  const particles = useRef<Particle[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Initialize particles only on client
    if (particles.current.length === 0) {
      for (let i = 0; i < 120; i++) {
        const z = Math.random();
        particles.current.push({
          x: Math.random() * window.innerWidth,
          y: Math.random() * window.innerHeight,
          z,
          char: HANZI_CHARS[Math.floor(Math.random() * HANZI_CHARS.length)],
          speed: (0.08 + Math.random() * 0.18) * (1 - z * 0.6), // far particles move slower
          opacity: 0.04 + (1 - z) * 0.14,
          size: 12 + (1 - z) * 20,
        });
      }
    }

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const onMouseMove = (e: MouseEvent) => {
      mouseRef.current = {
        x: (e.clientX / window.innerWidth - 0.5) * 2,  // -1 to 1
        y: (e.clientY / window.innerHeight - 0.5) * 2,
      };
    };
    window.addEventListener("mousemove", onMouseMove);

    let lastTime = 0;
    const draw = (time: number) => {
      const delta = Math.min((time - lastTime) / 16, 3); // cap at 3x speed
      lastTime = time;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const mx = mouseRef.current.x;
      const my = mouseRef.current.y;

      for (const p of particles.current) {
        // Parallax offset: near particles (low z) shift more with mouse
        const parallaxStrength = (1 - p.z) * 18;
        const px = p.x + mx * parallaxStrength;
        const py = p.y + my * parallaxStrength;

        // Drift upward
        p.y -= p.speed * delta;
        if (p.y < -40) {
          p.y = canvas.height + 20;
          p.x = Math.random() * canvas.width;
          p.char = HANZI_CHARS[Math.floor(Math.random() * HANZI_CHARS.length)];
        }

        ctx.save();
        ctx.font = `${p.size}px "Noto Sans SC", sans-serif`;
        ctx.fillStyle = `oklch(0.72 0.04 260 / ${p.opacity})`;
        ctx.fillText(p.char, px, py);
        ctx.restore();
      }

      frameRef.current = requestAnimationFrame(draw);
    };

    frameRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(frameRef.current);
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", onMouseMove);
    };
  }, []);

  return (
    <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden">
      {/* Vignette overlay */}
      <div
        className="absolute inset-0 z-10 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 40%, oklch(0.18 0.02 260 / 0.8) 100%)",
        }}
      />
      {/* Bottom fade so content is always readable */}
      <div
        className="absolute bottom-0 left-0 right-0 h-48 z-10 pointer-events-none"
        style={{
          background: "linear-gradient(to bottom, transparent, oklch(0.18 0.02 260))",
        }}
      />
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
    </div>
  );
}
