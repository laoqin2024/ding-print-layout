(() => {
  // src/js/portal.js
  (function() {
    const boot = window.PORTAL_BOOT || {};
    const el = {
      statusText: document.getElementById("status-text"),
      statusDot: document.getElementById("status-dot"),
      userInfo: document.getElementById("user-info"),
      userName: document.getElementById("user-name"),
      userDept: document.getElementById("user-dept"),
      loading: document.getElementById("loading-state"),
      templatesView: document.getElementById("templates-view"),
      templatesGrid: document.getElementById("templates-grid"),
      templatesEmpty: document.getElementById("templates-empty"),
      templateCount: document.getElementById("template-count"),
      refreshTemplatesBtn: document.getElementById("refresh-templates-btn"),
      instancesView: document.getElementById("instances-view"),
      instancesEmpty: document.getElementById("instances-empty"),
      backToTemplatesBtn: document.getElementById("back-to-templates-btn"),
      currentTemplateName: document.getElementById("current-template-name"),
      instanceCount: document.getElementById("instance-count"),
      list: document.getElementById("list-container"),
      toolbar: document.getElementById("toolbar"),
      searchInput: document.getElementById("search-input"),
      sortSelect: document.getElementById("sort-select"),
      statusTabs: Array.from(document.querySelectorAll(".status-tab")),
      statAll: document.getElementById("stat-all"),
      statPending: document.getElementById("stat-pending"),
      statPass: document.getElementById("stat-pass"),
      statOther: document.getElementById("stat-other"),
      loadMoreWrap: document.getElementById("load-more-wrap"),
      loadMoreBtn: document.getElementById("load-more-btn")
    };
    const state = {
      view: "templates",
      currentTemplate: null,
      templates: [],
      instances: [],
      filteredInstances: [],
      userInfo: {},
      statusFilter: "all",
      keyword: "",
      sort: "desc",
      pageSize: 12,
      visibleCount: 12
    };
    function setStatus(statusState, text) {
      el.statusText.textContent = text;
      const map = {
        loading: "bg-amber-400 animate-pulse",
        ok: "bg-emerald-500",
        empty: "bg-slate-300 dark:bg-slate-600",
        error: "bg-rose-500"
      };
      el.statusDot.className = `w-3 h-3 rounded-full ${map[statusState] || map.loading}`;
    }
    function escapeHtml(s) {
      return String(s || "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
    }
    function fmtTime(ts) {
      if (!ts) return "";
      const d = new Date(ts);
      const pad = (n) => String(n).padStart(2, "0");
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    }
    function normalizeStatus(item) {
      const rawStatus = (item.status || "").toString().toUpperCase();
      const rawResult = (item.result || "").toString().toLowerCase();
      if (rawStatus.includes("TERMINATE") || rawResult.includes("revoke") || rawResult.includes("cancel")) {
        return { label: "\u5DF2\u64A4\u56DE", tone: "slate", key: "revoke" };
      }
      if (rawResult.includes("refuse") || rawResult.includes("reject")) {
        return { label: "\u5DF2\u62D2\u7EDD", tone: "rose", key: "reject" };
      }
      if (rawStatus.includes("COMPLETED") || rawResult.includes("agree") || rawResult.includes("pass")) {
        return { label: "\u5DF2\u901A\u8FC7", tone: "emerald", key: "pass" };
      }
      return { label: "\u5BA1\u6279\u4E2D", tone: "amber", key: "pending" };
    }
    function badgeClass(tone) {
      const m = {
        amber: "bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/25",
        emerald: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/25",
        rose: "bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/25",
        slate: "bg-slate-500/15 text-slate-700 dark:text-slate-300 border-slate-500/25"
      };
      return `text-xs font-black px-3 py-1.5 rounded-full border ${m[tone] || m.slate}`;
    }
    function templateCardHtml(template) {
      const iconMap = { "p": "\u{1F4C4}", "l": "\u{1F4CB}" };
      const icon = iconMap[template.orientation] || "\u{1F4C4}";
      return `<div class="glass rounded-3xl p-6 shadow-md hover:shadow-xl transition-all duration-300 hover:scale-[1.02] cursor-pointer border border-slate-200/20 dark:border-slate-700/30" onclick="window.portalApp.loadInstances('${escapeHtml(template.p_code)}')"><div class="flex items-start gap-4"><div class="w-14 h-14 rounded-2xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-3xl flex-shrink-0">${icon}</div><div class="flex-1 min-w-0"><h3 class="font-black text-slate-800 dark:text-slate-200 text-base mb-2 leading-tight break-words">${escapeHtml(template.name)}</h3><p class="text-xs text-slate-600 dark:text-slate-400 font-mono break-all">${escapeHtml(template.p_code)}</p></div><div class="text-blue-600 dark:text-blue-400 flex-shrink-0"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></div></div></div>`;
    }
    function instanceCardHtml(item) {
      const st = normalizeStatus(item);
      const when = fmtTime(item.create_time);
      const href = `/print_view?id=${encodeURIComponent(item.id)}&p_code=${encodeURIComponent(item.p_code)}`;
      const approvalNo = item.approval_no || item.id || "";
      return `<div class="glass rounded-3xl p-6 border border-slate-200/20 dark:border-slate-700/30 hover:shadow-lg transition-all"><div class="flex items-center justify-between gap-3 mb-4"><span class="${badgeClass(st.tone)}">${st.label}</span><div class="text-xs text-slate-500 dark:text-slate-400 font-semibold">${escapeHtml(when)}</div></div><div class="mb-4"><div class="text-slate-900 dark:text-slate-50 font-black text-base leading-snug mb-2">${escapeHtml(item.title || "\uFF08\u65E0\u6807\u9898\uFF09")}</div><div class="text-xs text-slate-500 dark:text-slate-300 font-mono">\u5BA1\u6279\u7F16\u53F7\uFF1A${escapeHtml(approvalNo)}</div></div><a href="${href}" class="block w-full text-center py-3 rounded-2xl font-black text-sm bg-slate-900/90 dark:bg-white/90 text-white dark:text-slate-900 hover:shadow-lg transition-all">\u786E\u8BA4\u9884\u89C8</a></div>`;
    }
    function getAuthCode() {
      return new Promise((resolve, reject) => {
        if (!window.dd || !dd.ready) {
          reject(new Error("\u8BF7\u5728\u9489\u9489\u5185\u6253\u5F00\u6B64\u9875\u9762"));
          return;
        }
        dd.runtime.permission.requestAuthCode({
          corpId: boot.corpId,
          onSuccess: function(result) {
            resolve(result.code);
          },
          onFail: function(err) {
            reject(new Error("\u83B7\u53D6\u6388\u6743\u5931\u8D25"));
          }
        });
      });
    }
    async function loadTemplates() {
      setStatus("loading", "\u6B63\u5728\u52A0\u8F7D\u6A21\u677F...");
      try {
        const authCode = await getAuthCode();
        const resp = await fetch(`/api/get_templates?code=${encodeURIComponent(authCode)}`, { credentials: "same-origin" });
        const data = await resp.json();
        if (data.errcode === 0) {
          state.templates = data.templates || [];
          state.userInfo = data.user_info || {};
          if (state.userInfo.name && el.userName) {
            el.userName.textContent = state.userInfo.name;
            if (state.userInfo.dept_name && el.userDept) el.userDept.textContent = state.userInfo.dept_name;
            el.userInfo.classList.remove("hidden");
          }
          renderTemplates();
        } else {
          showError(data.errmsg || "\u52A0\u8F7D\u6A21\u677F\u5931\u8D25");
        }
      } catch (err) {
        console.error("Load templates error:", err);
        showError(err.message || "\u7F51\u7EDC\u5F02\u5E38\uFF0C\u8BF7\u7A0D\u540E\u91CD\u8BD5");
      }
    }
    function renderTemplates() {
      el.loading.style.display = "none";
      if (state.templates.length === 0) {
        el.templatesView.classList.remove("hidden");
        el.templatesGrid.classList.add("hidden");
        el.templatesEmpty.classList.remove("hidden");
        setStatus("empty", "\u6682\u65E0\u6A21\u677F");
        return;
      }
      el.templatesView.classList.remove("hidden");
      el.templatesGrid.classList.remove("hidden");
      el.templatesEmpty.classList.add("hidden");
      el.instancesView.classList.add("hidden");
      if (el.templateCount) el.templateCount.textContent = state.templates.length;
      el.templatesGrid.innerHTML = state.templates.map(templateCardHtml).join("");
      setStatus("ok", `\u5DF2\u52A0\u8F7D ${state.templates.length} \u4E2A\u6A21\u677F`);
      const cards = Array.from(el.templatesGrid.children);
      cards.forEach((card, idx) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        setTimeout(() => {
          card.style.transition = "all 0.3s ease";
          card.style.opacity = "1";
          card.style.transform = "translateY(0)";
        }, idx * 50);
      });
    }
    async function loadInstances(pCode) {
      state.currentTemplate = pCode;
      state.view = "instances";
      el.templatesView.classList.add("hidden");
      el.instancesView.classList.remove("hidden");
      el.loading.style.display = "grid";
      setStatus("loading", "\u6B63\u5728\u52A0\u8F7D\u5BA1\u6279\u5217\u8868...");
      try {
        const authCode = await getAuthCode();
        const resp = await fetch(`/api/get_template_instances?code=${encodeURIComponent(authCode)}&p_code=${encodeURIComponent(pCode)}`, { credentials: "same-origin" });
        const data = await resp.json();
        if (data.errcode === 0) {
          state.instances = data.list || [];
          if (el.currentTemplateName) el.currentTemplateName.textContent = data.template_name || pCode;
          renderInstances();
        } else {
          showError(data.errmsg || "\u52A0\u8F7D\u5BA1\u6279\u5217\u8868\u5931\u8D25");
        }
      } catch (err) {
        console.error("Load instances error:", err);
        showError(err.message || "\u7F51\u7EDC\u5F02\u5E38\uFF0C\u8BF7\u7A0D\u540E\u91CD\u8BD5");
      }
    }
    function renderInstances() {
      el.loading.style.display = "none";
      if (state.instances.length === 0) {
        el.toolbar.classList.add("hidden");
        el.list.classList.add("hidden");
        el.instancesEmpty.classList.remove("hidden");
        el.loadMoreWrap.classList.add("hidden");
        if (el.instanceCount) el.instanceCount.textContent = "0";
        setStatus("empty", "\u6682\u65E0\u5BA1\u6279\u8BB0\u5F55");
        return;
      }
      applyFilters();
    }
    function applyFilters() {
      const kw = state.keyword.trim().toLowerCase();
      let items = [...state.instances];
      if (state.statusFilter !== "all") {
        items = items.filter((item) => normalizeStatus(item).key === state.statusFilter);
      }
      if (kw) {
        items = items.filter((item) => {
          const text = `${item.title || ""} ${item.approval_no || ""}`.toLowerCase();
          return text.includes(kw);
        });
      }
      items.sort((a, b) => {
        const av = Number(a.create_time || 0);
        const bv = Number(b.create_time || 0);
        return state.sort === "asc" ? av - bv : bv - av;
      });
      state.filteredInstances = items;
      if (items.length === 0) {
        el.toolbar.classList.remove("hidden");
        el.list.classList.add("hidden");
        el.instancesEmpty.classList.remove("hidden");
        el.loadMoreWrap.classList.add("hidden");
        setStatus("empty", "\u65E0\u5339\u914D\u7ED3\u679C");
        return;
      }
      updateStats(items);
      if (el.instanceCount) el.instanceCount.textContent = state.instances.length;
      mountList(items);
      setStatus("ok", `\u663E\u793A ${items.length} \u6761\uFF0C\u5DF2\u52A0\u8F7D ${state.instances.length} \u6761`);
    }
    function updateStats(items) {
      const stats = { all: items.length, pending: 0, pass: 0, other: 0 };
      items.forEach((item) => {
        const key = normalizeStatus(item).key;
        if (key === "pending") stats.pending += 1;
        else if (key === "pass") stats.pass += 1;
        else stats.other += 1;
      });
      if (el.statAll) el.statAll.textContent = String(stats.all);
      if (el.statPending) el.statPending.textContent = String(stats.pending);
      if (el.statPass) el.statPass.textContent = String(stats.pass);
      if (el.statOther) el.statOther.textContent = String(stats.other);
    }
    function mountList(items) {
      el.list.innerHTML = items.map(instanceCardHtml).join("");
      el.toolbar.classList.remove("hidden");
      el.list.classList.remove("hidden");
      el.instancesEmpty.classList.add("hidden");
      if (state.hasMore && !state.keyword && state.statusFilter === "all") {
        el.loadMoreWrap.classList.remove("hidden");
        el.loadMoreBtn.textContent = state.isLoading ? "\u52A0\u8F7D\u4E2D..." : "\u52A0\u8F7D\u66F4\u591A";
        el.loadMoreBtn.disabled = state.isLoading;
      } else {
        el.loadMoreWrap.classList.add("hidden");
      }
      const cards = Array.from(el.list.children);
      cards.forEach((card, idx) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        setTimeout(() => {
          card.style.transition = "all 0.3s ease";
          card.style.opacity = "1";
          card.style.transform = "translateY(0)";
        }, idx * 30);
      });
    }
    function backToTemplates() {
      state.view = "templates";
      state.currentTemplate = null;
      state.instances = [];
      state.filteredInstances = [];
      state.statusFilter = "all";
      state.keyword = "";
      state.visibleCount = state.pageSize;
      el.instancesView.classList.add("hidden");
      el.templatesView.classList.remove("hidden");
      if (el.searchInput) el.searchInput.value = "";
      activateTab();
      setStatus("ok", `\u5DF2\u52A0\u8F7D ${state.templates.length} \u4E2A\u6A21\u677F`);
    }
    function activateTab() {
      el.statusTabs.forEach((btn) => {
        const active = btn.dataset.status === state.statusFilter;
        if (active) {
          btn.style.background = "rgba(37, 99, 235, 0.9)";
          btn.style.color = "white";
          btn.classList.add("shadow-sm");
        } else {
          btn.style.background = "";
          btn.style.color = "";
          btn.classList.remove("shadow-sm");
        }
      });
    }
    function showError(msg) {
      el.loading.style.display = "none";
      setStatus("error", msg || "\u52A0\u8F7D\u5931\u8D25");
      if (state.view === "templates") {
        el.templatesView.classList.remove("hidden");
        el.templatesEmpty.classList.remove("hidden");
        el.templatesGrid.classList.add("hidden");
      } else {
        el.instancesEmpty.classList.remove("hidden");
        el.list.classList.add("hidden");
        el.toolbar.classList.add("hidden");
      }
    }
    function bootAuth() {
      setStatus("loading", "\u6B63\u5728\u6821\u9A8C\u8EAB\u4EFD...");
      if (!window.dd || !dd.ready) {
        showError("\u8BF7\u5728\u9489\u9489\u5185\u6253\u5F00\u6B64\u9875\u9762");
        return;
      }
      dd.ready(function() {
        loadTemplates();
      });
    }
    function initEvents() {
      if (el.backToTemplatesBtn) el.backToTemplatesBtn.addEventListener("click", backToTemplates);
      if (el.refreshTemplatesBtn) el.refreshTemplatesBtn.addEventListener("click", () => loadTemplates());
      if (el.searchInput) {
        let searchTimeout;
        el.searchInput.addEventListener("input", (e) => {
          state.keyword = e.target.value || "";
          clearTimeout(searchTimeout);
          if (state.keyword.trim()) {
            searchTimeout = setTimeout(() => {
              performBackendSearch();
            }, 500);
          } else {
            state.visibleCount = state.pageSize;
            applyFilters();
          }
        });
      }
      if (el.sortSelect) {
        el.sortSelect.addEventListener("change", (e) => {
          state.sort = e.target.value || "desc";
          state.visibleCount = state.pageSize;
          applyFilters();
        });
      }
      el.statusTabs.forEach((btn) => {
        btn.addEventListener("click", () => {
          state.statusFilter = btn.dataset.status || "all";
          state.visibleCount = state.pageSize;
          activateTab();
          applyFilters();
        });
      });
      if (el.loadMoreBtn) {
        el.loadMoreBtn.addEventListener("click", () => {
          loadMoreInstances();
        });
      }
    }
    window.portalApp = {
      loadInstances,
      backToTemplates
    };
    window.AppCore.onReady(function() {
      initEvents();
      activateTab();
      bootAuth();
    });
  })();
})();
