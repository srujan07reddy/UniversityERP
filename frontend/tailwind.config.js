/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          emerald: '#064E3B',
          'emerald-dark': '#043D2F',
          gold: '#C5A04B',
          'gold-dark': '#80621F',
          ivory: '#F7F8F5',
          charcoal: '#17251F',
          sage: '#E8EDE7',
        },
        dept: {
          cse: '#2563EB',
          aiml: '#7C3AED',
          quantum: '#0891B2',
          aids: '#D97706',
          ece: '#0F766E',
          mba: '#80621F',
          aviation: '#1E3A5F',
          biotech: '#16804A',
          sports: '#16803C',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
