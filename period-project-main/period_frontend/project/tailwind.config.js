/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef2f3',
          100: '#fde6e7',
          200: '#fbd0d5',
          300: '#f7aab2',
          400: '#f27a8a',
          500: '#e63956',
          600: '#d31f3c',
          700: '#b21530',
          800: '#95152d',
          900: '#7f162a',
        },
      },
    },
  },
  plugins: [],
}
