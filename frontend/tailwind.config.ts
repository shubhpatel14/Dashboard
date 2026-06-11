import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#FFFFFF",
        canvas: "#F8FAFC",
        line: "#E5E7EB",
        ink: "#111827",
        muted: "#6B7280",
        positive: "#16A34A",
        negative: "#DC2626",
        neutral: "#D97706"
      },
      boxShadow: {
        terminal: "0 1px 2px rgba(17, 24, 39, 0.06)"
      }
    }
  },
  plugins: [require("@tailwindcss/forms")]
};

export default config;
