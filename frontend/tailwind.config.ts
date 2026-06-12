import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "rgb(var(--surface) / <alpha-value>)",
        canvas: "rgb(var(--canvas) / <alpha-value>)",
        line: "rgb(var(--line) / <alpha-value>)",
        ink: "rgb(var(--ink) / <alpha-value>)",
        muted: "rgb(var(--muted) / <alpha-value>)",
        positive: "#16A34A",
        negative: "#DC2626",
        neutral: "#D97706",
        terminal: "rgb(var(--terminal) / <alpha-value>)"
      },
      boxShadow: {
        terminal: "0 1px 2px rgba(17, 24, 39, 0.06)"
      }
    }
  },
  plugins: [require("@tailwindcss/forms")]
};

export default config;
