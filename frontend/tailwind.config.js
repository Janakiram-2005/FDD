/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: "#0F172A",
        card: "rgba(30, 41, 59, 0.7)",
        accent: "#3B82F6",
        success: "#10B981",
        danger: "#EF4444"
      }
    },
  },
  plugins: [],
}
