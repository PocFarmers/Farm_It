/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,jsx}",
    ],
    theme: {
        extend: {
            colors: {
                'farm-dark': '#2d5016',
                'farm-darker': '#1a3a0f',
                'farm-green': '#8bc34a',
                'farm-light': '#c5e1a5',
            }
        },
    },
    plugins: [],
}
