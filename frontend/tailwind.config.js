/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        handwriting: ['Caveat', 'cursive'],
        decorative: ['Cinzel Decorative', 'serif'],
      },
    },
  },
  plugins: [],
}
