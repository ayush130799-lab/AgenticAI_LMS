import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          blue: "#2563eb",
          "blue-dark": "#1d4ed8",
          cyan: "#06b6d4",
          "cyan-dark": "#0891b2",
          magenta: "#d946ef",
          purple: "#7c3aed",
          amber: "#f59e0b",
        },
        surface: {
          tint: "#eff9fb",
          "tint-blue": "#eef6ff",
          DEFAULT: "#ffffff",
          page: "#f8fafc",
        },
        ink: {
          900: "#0f172a",
          700: "#334155",
          500: "#475569",
          400: "#64748b",
          200: "#e2e8f0",
          100: "#f1f5f9",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        soft: "0 10px 30px -10px rgba(15, 23, 42, 0.15)",
        card: "0 1px 3px 0 rgba(15, 23, 42, 0.08), 0 1px 2px -1px rgba(15, 23, 42, 0.06)",
      },
      backgroundImage: {
        "mastery-gradient":
          "linear-gradient(90deg, #f59e0b 0%, #06b6d4 55%, #2563eb 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
