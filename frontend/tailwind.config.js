/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cream: {
          50: '#FFFDF9',
          100: '#FDF8F2',
          200: '#FBF2E5',
          300: '#F7E6CE',
          400: '#F2D5AF',
        },
        bakery: {
          brown: '#8B4513',
          dark: '#2C1810',
          chocolate: '#3D1C10',
          amber: '#D4AF37',
          orange: '#E07A5F',
          gold: '#E5A93C',
          cream: '#FFFDF9',
          soft: '#F4ECE1'
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 4s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        }
      }
    },
  },
  plugins: [],
}
