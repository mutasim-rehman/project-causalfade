import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-ibm-plex-mono)", "ui-monospace", "monospace"],
        serif: ["var(--font-newsreader)", "Georgia", "serif"],
      },
      colors: {
        obs: {
          bg: "var(--bg-app)",
          surface: "var(--bg-surface)",
          elevated: "var(--bg-elevated)",
          border: "var(--border-subtle)",
          text: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
        },
        sci: {
          causal: "#55D6BE",
          observational: "#60A5FA",
          arithmetic: "#A78BFA",
          caution: "#FBBF24",
          error: "#F87171",
          verified: "#34D399",
        },
      },
    },
  },
  plugins: [],
};

export default config;
