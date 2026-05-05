/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "media",
  content: [
    "../templates/**/*.html",
    "./src/js/**/*.js",
    "./src/styles/**/*.css",
  ],
  theme: {
    extend: {
      boxShadow: {
        glass: "0 20px 60px rgba(0,0,0,0.15)",
      },
      backdropBlur: {
        glass: "20px",
      },
    },
  },
  plugins: [],
  // 主按钮常用色：避免模板里新写的 solid 类未参与扫描时整站 CSS 缺规则（表现为白字无底色）
  safelist: [
    "bg-blue-600",
    "hover:bg-blue-700",
    "bg-blue-500",
    "hover:bg-blue-600",
    "bg-indigo-600",
    "hover:bg-indigo-700",
  ],
};

