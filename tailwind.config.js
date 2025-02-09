/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/templates/**/*.html', './src/static/**/*.js'],
  theme: {
    extend: {
      colors: {
        'dark-forest': '#171F1E',
        'sage': '#334545',
        'taupe': '#C6A98B',
        'cream': '#FEFEFD',
        'golden': '#B6882C',
      },
    },
  },
  plugins: [],
}