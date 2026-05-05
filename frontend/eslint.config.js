const js = require("@eslint/js");
const importPlugin = require("eslint-plugin-import");
const globals = require("globals");

module.exports = [
  js.configs.recommended,
  {
    files: ["src/js/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        dd: "readonly",
      },
    },
    plugins: {
      import: importPlugin,
    },
    rules: {
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "no-undef": "error",
      "import/no-unresolved": "off",
    },
  },
];

