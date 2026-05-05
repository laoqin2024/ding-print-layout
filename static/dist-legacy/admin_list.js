(() => {
  // src/js/admin_list.js
  (function() {
    function confirmDelete(code) {
      const ok = window.confirm(`\u786E\u5B9A\u8981\u5220\u9664\u914D\u7F6E [${code}] \u5417\uFF1F`);
      if (!ok) return;
      window.location.href = "/admin/delete/" + encodeURIComponent(code);
    }
    window.AppCore.onReady(function() {
      document.addEventListener("click", function(e) {
        const btn = e.target && e.target.closest && e.target.closest("[data-del-code]");
        if (!btn) return;
        const code = btn.getAttribute("data-del-code") || "";
        if (!code) return;
        confirmDelete(code);
      });
      const uploadInput = document.getElementById("upload-input");
      const uploadForm = document.getElementById("upload-form");
      if (uploadInput && uploadForm) {
        uploadInput.addEventListener("change", function() {
          if (uploadInput.files && uploadInput.files.length > 0 && window.innerWidth < 640) {
            uploadForm.submit();
          }
        });
      }
    });
  })();
})();
