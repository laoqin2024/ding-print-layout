(() => {
  // src/js/portal.js
  (function() {
    const boot = window.PORTAL_BOOT || {};
    const el = {
      statusText: document.getElementById("status-text"),
      statusDot: document.getElementById("status-dot"),
      userInfo: document.getElementById("user-info"),
      loading: document.getElementById("loading-state"),
      list: document.getElementById("list-container"),
      toolbar: document.getElementById("toolbar"),
      searchInput: document.getElementById("search-input"),
      sortSelect: document.getElementById("sort-select"),
      templateSelect: document.getElementById("template-select"),
      statusTabs: Array.from(document.querySelectorAll(".status-tab")),
      statAll: document.getElementById("stat-all"),
      statPending: document.getElementById("stat-pending"),
      statPass: document.getElementById("stat-pass"),
      statOther: document.getElementById("stat-other"),
      loadMoreWrap: document.getElementById("load-more-wrap"),
      loadMoreBtn: document.getElementById("load-more-btn"),
      empty: document.getElementById("empty-state"),
      refreshBtn: document.getElementById("refresh-btn")
    };
    const state = {
      rawList: [],
      filteredList: [],
      templates: {},
      userInfo: {},
      statusFilter: "all",
      templateFilter: "",
      keyword: "",
      sort: "desc",
      pageSize: 8,
      visibleCount: 8
    };
    function setStatus(state2, text) {
      el.statusText.textContent = text;
      const map = {
        loading: "bg-amber-400 animate-pulse",
        ok: "bg-emerald-500",
        empty: "bg-slate-300 dark:bg-slate-600",
        error: "bg-rose-500"
      };
      el.statusDot.className = `w-2.5 h-2.5 rounded-full mb-2 ${map[state2] || map.loading}`;
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
      return `text-[10px] font-black px-2 py-1 rounded-full border ${m[tone] || m.slate}`;
    }
    function templateChip(name) {
      return `<span class="text-[10px] font-black px-2 py-1 rounded-full border bg-blue-500/10 text-blue-700 dark:text-blue-300 border-blue-500/20">${escapeHtml(
        name || "\u672A\u547D\u540D\u6A21\u677F"
      )}</span>`;
    }
    function escapeHtml(s) {
      return String(s || "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
    }
    function cardHtml(item) {
      const st = normalizeStatus(item);
      const when = fmtTime(item.create_time);
      const href = `/print_view?id=${encodeURIComponent(item.id)}&p_code=${encodeURIComponent(item.p_code)}`;
      const approvalNo = item.approval_no || item.id || "";
      return `
      <div class="glass rounded-3xl p-5 border border-slate-200/20 dark:border-slate-700/30 active:scale-[0.99] transition will-change-transform">
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            ${templateChip(item.template_name)}
            <span class="${badgeClass(st.tone)}">${st.label}</span>
          </div>
          <div class="text-[10px] text-slate-500 dark:text-slate-400 font-semibold">${escapeHtml(when)}</div>
        </div>
        <div class="mt-3">
          <div class="text-slate-900 dark:text-slate-50 font-black text-sm leading-snug">${escapeHtml(item.title || "\uFF08\u65E0\u6807\u9898\uFF09")}</div>
          <div class="mt-1 text-[10px] text-slate-500 dark:text-slate-300 font-mono leading-tight">
            \u5BA1\u6279\u7F16\u53F7\uFF1A${escapeHtml(approvalNo)}
          </div>
        </div>
        <a href="${href}"
           class="mt-5 block w-full text-center py-3.5 rounded-2xl font-black text-xs bg-slate-900/90 dark:bg-white/90 text-white dark:text-slate-900 shadow-glass">
          \u786E\u8BA4\u9884\u89C8
        </a>
      </div>
    `;
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
      const visible = items.slice(0, state.visibleCount);
      el.list.innerHTML = visible.map(cardHtml).join("");
      el.loading.style.display = "none";
      el.toolbar.classList.remove("hidden");
      el.list.classList.remove("hidden");
      el.empty.classList.add("hidden");
      el.loadMoreWrap.classList.toggle("hidden", visible.length >= items.length);
      const nodes = Array.from(el.list.children);
      nodes.forEach((n, idx) => {
        n.classList.add("fade-up-enter");
        requestAnimationFrame(() => {
          n.classList.add("fade-up-enter-active");
          n.style.transitionDelay = `${Math.min(140, idx * 35)}ms`;
        });
      });
    }
    function showEmpty() {
      el.loading.style.display = "none";
      el.list.classList.add("hidden");
      el.toolbar.classList.add("hidden");
      el.loadMoreWrap.classList.add("hidden");
      el.empty.classList.remove("hidden");
      setStatus("empty", "\u65E0\u6570\u636E");
    }
    function showError(msg) {
      el.loading.style.display = "none";
      el.empty.classList.remove("hidden");
      setStatus("error", msg || "\u52A0\u8F7D\u5931\u8D25");
    }
    function applyFilters() {
      const kw = state.keyword.trim().toLowerCase();
      let items = [...state.rawList];
      if (state.templateFilter) {
        items = items.filter((item) => item.p_code === state.templateFilter);
      }
      if (state.statusFilter !== "all") {
        items = items.filter((item) => normalizeStatus(item).key === state.statusFilter);
      }
      if (kw) {
        items = items.filter((item) => {
          const text = `${item.title || ""} ${item.template_name || ""} ${item.approval_no || ""}`.toLowerCase();
          return text.includes(kw);
        });
      }
      items.sort((a, b) => {
        const av = Number(a.create_time || 0);
        const bv = Number(b.create_time || 0);
        return state.sort === "asc" ? av - bv : bv - av;
      });
      state.filteredList = items;
      if (items.length === 0) return showEmpty();
      const templateName = state.templateFilter ? state.templates[state.templateFilter] || "\u672A\u77E5\u6A21\u677F" : "\u5168\u90E8";
      setStatus("ok", `${templateName} \xB7 \u5171 ${items.length} \u6761`);
      mountList(items);
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
    async function fetchMyList(code) {
      try {
        const resp = await fetch(`/api/get_my_list?code=${encodeURIComponent(code)}`, { credentials: "same-origin" });
        const data = await resp.json();
        if (data.errcode === 0 && Array.isArray(data.list) && data.list.length > 0) {
          state.rawList = data.list;
          state.templates = data.templates || {};
          state.userInfo = data.user_info || {};
          if (state.userInfo.name) {
            const deptText = state.userInfo.dept_name ? ` \xB7 ${state.userInfo.dept_name}` : "";
            el.userInfo.textContent = `${state.userInfo.name}${deptText}`;
            el.userInfo.classList.remove("hidden");
          }
          if (el.templateSelect) {
            el.templateSelect.innerHTML = '<option value="">\u5168\u90E8\u6D41\u7A0B\u6A21\u677F</option>';
            const sortedTemplates = Object.entries(state.templates).sort(
              (a, b) => String(a[1]).localeCompare(String(b[1]), "zh-Hans-CN")
            );
            sortedTemplates.forEach(([code2, name]) => {
              const opt = document.createElement("option");
              opt.value = code2;
              opt.textContent = name || code2;
              el.templateSelect.appendChild(opt);
            });
          }
          updateStats(state.rawList);
          applyFilters();
        } else {
          showEmpty();
        }
      } catch (e) {
        showError("\u7F51\u7EDC\u5F02\u5E38\uFF0C\u8BF7\u7A0D\u540E\u91CD\u8BD5");
      }
    }
    function bootAuth() {
      setStatus("loading", "\u6B63\u5728\u6821\u9A8C\u8EAB\u4EFD...");
      if (!window.dd || !dd.ready) {
        showError("\u8BF7\u5728\u9489\u9489\u5185\u6253\u5F00\u6B64\u9875\u9762");
        return;
      }
      dd.ready(function() {
        dd.runtime.permission.requestAuthCode({
          corpId: boot.corpId,
          onSuccess: function(result) {
            fetchMyList(result.code);
          },
          onFail: function() {
            showError("\u8BF7\u5728\u9489\u9489\u79FB\u52A8\u7AEF\u6253\u5F00\u6B64\u9875\u9762");
          }
        });
      });
    }
    window.AppCore.onReady(function() {
      if (el.refreshBtn) el.refreshBtn.addEventListener("click", () => location.reload());
      if (el.searchInput) {
        el.searchInput.addEventListener("input", (e) => {
          state.keyword = e.target.value || "";
          state.visibleCount = state.pageSize;
          applyFilters();
        });
      }
      if (el.sortSelect) {
        el.sortSelect.addEventListener("change", (e) => {
          state.sort = e.target.value || "desc";
          state.visibleCount = state.pageSize;
          applyFilters();
        });
      }
      if (el.templateSelect) {
        el.templateSelect.addEventListener("change", (e) => {
          state.templateFilter = e.target.value || "";
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
          state.visibleCount += state.pageSize;
          mountList(state.filteredList);
        });
      }
      activateTab();
      bootAuth();
    });
  })();
})();
