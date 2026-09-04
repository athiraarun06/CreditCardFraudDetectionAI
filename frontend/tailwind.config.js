/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#05050a",
        panel: "rgba(255,255,255,0.04)",
        accent1: "#7c3aed",
        accent2: "#2563eb",
      },
      backgroundImage: {
        "gradient-fintech": "linear-gradient(135deg, #7c3aed 0%, #2563eb 100%)",
      },
    },
  },
  plugins: [],
};
