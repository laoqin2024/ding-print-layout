(() => {
  // src/js/core.js
  (function() {
    window.AppCore = {
      onReady(fn) {
        if (document.readyState === "loading") {
          document.addEventListener("DOMContentLoaded", fn);
        } else {
          fn();
        }
      }
    };
  })();
})();
