/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Custom palette inspired by minimal aesthetic
        chat: {
          bg: '#ffffff',
          sidebar: '#f7f7f8', // Very light grey for sidebar
          input: '#ffffff',
          bubble: '#eef1f5', // Blue-ish grey for user
          text: '#374151',
          border: '#e5e7eb',
        }
      }
    },
  },
  plugins: [],
}
