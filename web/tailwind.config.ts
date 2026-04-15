import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          base: "oklch(0.18 0.02 260)",
          surface: "oklch(0.22 0.02 260)",
          border: "oklch(0.28 0.02 260)",
        },
        accent: {
          gold: "oklch(0.85 0.12 85)",
          cyan: "oklch(0.80 0.14 200)",
          red: "oklch(0.65 0.20 25)",
        },
        text: {
          primary: "oklch(0.95 0.01 260)",
          secondary: "oklch(0.65 0.02 260)",
        },
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans SC", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;