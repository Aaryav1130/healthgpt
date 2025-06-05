/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        medical: {
          blue: "#0EA5E9",
          green: "#10B981",
          red: "#EF4444",
          dark: "#0F172A",
        }
      }
    },
  },
  plugins: [require("@tailwindcss/typography")],
}