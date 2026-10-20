import type { Config } from "tailwindcss";
export default { content: ["./index.html", "./src/**/*.{ts,tsx}"], theme: { extend: { colors: { parchment: "#FAF6EE", ink: "#1F1A17", saffron: "#C8741A", indigo: "#2E3A59" }, fontFamily: { display: ["Cormorant Garamond", "serif"], sans: ["Inter", "sans-serif"], devanagari: ["Noto Serif Devanagari", "serif"] } } }, plugins: [] } satisfies Config;
