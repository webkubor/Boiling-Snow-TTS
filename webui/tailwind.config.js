/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ember: {
          50: '#fff7ed',
          100: '#ffedd5',
          500: '#f97316',
          700: '#c2410c',
          900: '#7c2d12'
        }
      },
      fontFamily: {
        title: ['"ZCOOL XiaoWei"', 'serif'],
        body: ['"Noto Sans SC"', 'sans-serif']
      },
      boxShadow: {
        flame: '0 20px 45px rgba(124, 45, 18, 0.35)'
      }
    }
  },
  plugins: []
}
