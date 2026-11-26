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
          causal: "rgb(var(--sci-causal) / <alpha-value>)",
          observational: "rgb(var(--sci-observational) / <alpha-value>)",
          arithmetic: "rgb(var(--sci-arithmetic) / <alpha-value>)",
          caution: "rgb(var(--sci-caution) / <alpha-value>)",
          error: "rgb(var(--sci-error) / <alpha-value>)",
          verified: "rgb(var(--sci-verified) / <alpha-value>)",
        },
      },
    },
  },
  plugins: [],
};

export default config;
