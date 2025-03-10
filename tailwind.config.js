/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/templates/**/*.html',    // Flask HTML templates
    './src/static/js/**/*.js',        // Static JS files
    './src/static/js/**/*.js',        // React files
  ],
  theme: {
    extend: {
      colors: {
        'dark-forest': '#171F1E',
        'sage': '#334545',
        'taupe': '#DFCAB2',
        'cream': '#FEFEFD',
        'golden': '#B6882C',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  variants: {
    extend: {
      placeholderColor: ['focus', 'hover', 'active', 'responsive'],
    },
  },
}
