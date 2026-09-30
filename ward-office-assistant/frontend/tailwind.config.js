/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // TODO: swap in the ward's actual brand colors once available
        ward: {
          primary: "#1e3a8a",
          accent: "#f59e0b",
        },
      },
    },
  },
  plugins: [],
};
