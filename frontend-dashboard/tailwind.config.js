/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'severity-low': '#22c55e',
        'severity-moderate': '#eab308',
        'severity-high': '#f97316',
        'severity-critical': '#ef4444',
      }
    },
  },
  plugins: [],
}
