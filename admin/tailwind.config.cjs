/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: "jit",
  content: ["./src/**/*.{tsx,html,ts}"],
  theme: {
    extend: {
      colors: {},
    },
    screens: {
      // 设置PC端优先
      sm: { max: "768px" },
    },
  },
};
