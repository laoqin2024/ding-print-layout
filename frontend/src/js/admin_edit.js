import $ from "jquery";
import "select2";

window.$ = window.jQuery = $;

(function () {
  const boot = window.ADMIN_EDIT_BOOT || {};
  const els = {
    procSearch: document.getElementById("proc-search"),
    historyBtn: document.getElementById("history-btn"),
    pCode: document.getElementById("p_code"),
    pName: document.getElementById("p_name"),
    orientRadios: Array.from(document.querySelectorAll("input[name='orientation']")),
    pdfSelect: document.getElementById("pdf-select"),
    jsonInput: document.getElementById("json-input"),
    beautifyBtn: document.getElementById("beautify-btn"),
    clearBtn: document.getElementById("clear-btn"),
    undoBtn: document.getElementById("undo-btn"),
    redoBtn: document.getElementById("redo-btn"),
    versionSelect: document.getElementById("version-select"),
    versionActionFilter: document.getElementById("version-action-filter"),
    versionKeyword: document.getElementById("version-keyword"),
    rollbackBtn: document.getElementById("rollback-btn"),
    versionReason: document.getElementById("version-reason"),
    versionDetail: document.getElementById("version-detail"),
    versionDetailTitle: document.getElementById("version-detail-title"),
    versionDetailMeta: document.getElementById("version-detail-meta"),
    instanceIdInput: document.getElementById("instance-id-input"),
    instanceUseridInput: document.getElementById("instance-userid-input"),
    instanceSelect: document.getElementById("instance-select"),
    loadInstancesBtn: document.getElementById("load-instances-btn"),
    loadComponentsBtn: document.getElementById("load-components-btn"),
    componentSelect: document.getElementById("component-select"),
    bindComponentBtn: document.getElementById("bind-component-btn"),
    bindHint: document.getElementById("bind-hint"),
    zoomLabel: document.getElementById("zoom-label"),
    bg: document.getElementById("bg"),
    boxes: document.getElementById("boxes"),
    dragLayer: document.getElementById("drag-layer"),
    canvasTransform: document.getElementById("canvas-transform"),
    workspace: document.getElementById("workspace"),
  };

  const state = {
    orient: "p",
    pdfFile: "",
    scale: 1,
    panX: 0,
    panY: 0,
    zones: [],
    creating: null,
    dragging: null,
    minScale: 0.35,
    maxScale: 3.5,
    undoStack: [],
    redoStack: [],
    versions: Array.isArray(boot.versions) ? boot.versions : [],
    versionFilterAction: "all",
    versionKeyword: "",
    selectedZoneId: null,
    loadedComponents: [],
    loadedInstances: [],
  };

  const LS = {
    historyKey: "dingtalk_print_admin_proc_history_v1",
    loadHistory() {
      try {
        const raw = localStorage.getItem(this.historyKey);
        const arr = JSON.parse(raw || "[]");
        return Array.isArray(arr) ? arr : [];
      } catch {
        return [];
      }
    },
    pushHistory(item) {
      const arr = this.loadHistory();
      const id = String(item.id || "").trim();
      const text = String(item.text || "").trim();
      if (!id) return;
      const next = [{ id, text, t: Date.now() }, ...arr.filter((x) => x && x.id !== id)].slice(0, 12);
      localStorage.setItem(this.historyKey, JSON.stringify(next));
    },
  };

  function getOrient() {
    const checked = els.orientRadios.find((r) => r.checked);
    return checked ? checked.value : "p";
  }
  function clamp(n, a, b) {
    return Math.max(a, Math.min(b, n));
  }
  function uuid() {
    return "z_" + Math.random().toString(16).slice(2) + "_" + Date.now().toString(16);
  }
  function pxToCanvasPoint(clientX, clientY) {
    const rect = els.canvasTransform.getBoundingClientRect();
    return { x: (clientX - rect.left) / state.scale, y: (clientY - rect.top) / state.scale };
  }
  function setTransform() {
    els.canvasTransform.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.scale})`;
    if (els.zoomLabel) els.zoomLabel.textContent = `${Math.round(state.scale * 100)}%`;
  }
  function safeParseZones(text) {
    try {
      const v = JSON.parse(text || "[]");
      return Array.isArray(v) ? v : [];
    } catch {
      return null;
    }
  }
  function normalizeZone(z) {
    const out = { ...z };
    out.x = Number(out.x ?? 0);
    out.y = Number(out.y ?? 0);
    out.w = Number(out.w ?? 0);
    out.h = Number(out.h ?? 0);
    if (out.page === undefined || out.page === null || out.page === "") out.page = 0;
    out.page = Number(out.page);
    out.name = out.name ?? "";
    return out;
  }
  function zonesToText(zones) {
    return JSON.stringify(zones, null, 4);
  }
  function syncTextFromZones() {
    els.jsonInput.value = zonesToText(
      state.zones.map((z) => {
        const rest = { ...z };
        delete rest.__id;
        return rest;
      })
    );
  }
  function snapshotText() {
    return els.jsonInput.value || "[]";
  }
  function pushUndoSnapshot() {
    const snap = snapshotText();
    if (state.undoStack.length === 0 || state.undoStack[state.undoStack.length - 1] !== snap) {
      state.undoStack.push(snap);
      if (state.undoStack.length > 80) state.undoStack.shift();
    }
    state.redoStack = [];
    refreshUndoRedoButtons();
  }
  function refreshUndoRedoButtons() {
    if (els.undoBtn) els.undoBtn.disabled = state.undoStack.length <= 1;
    if (els.redoBtn) els.redoBtn.disabled = state.redoStack.length === 0;
  }
  function applySnapshotText(text) {
    els.jsonInput.value = text;
    if (syncZonesFromText()) render();
  }
  function doUndo() {
    if (state.undoStack.length <= 1) return;
    const current = state.undoStack.pop();
    if (current) state.redoStack.push(current);
    const previous = state.undoStack[state.undoStack.length - 1];
    applySnapshotText(previous);
    refreshUndoRedoButtons();
  }
  function doRedo() {
    if (state.redoStack.length === 0) return;
    const next = state.redoStack.pop();
    if (!next) return;
    state.undoStack.push(next);
    applySnapshotText(next);
    refreshUndoRedoButtons();
  }
  function syncZonesFromText() {
    const parsed = safeParseZones(els.jsonInput.value);
    if (!parsed) return false;
    state.zones = parsed.map((z, i) => {
      const nz = normalizeZone(z);
      nz.__id = state.zones[i] && state.zones[i].__id ? state.zones[i].__id : uuid();
      return nz;
    });
    return true;
  }
  function clearBoxes() {
    els.boxes.innerHTML = "";
    els.dragLayer.innerHTML = "";
  }
  function render() {
    clearBoxes();
    state.zones.forEach((z, idx) => {
      const box = document.createElement("div");
      const selected = state.selectedZoneId && z.__id === state.selectedZoneId;
      box.className = selected
        ? "absolute rounded-xl border-2 border-blue-500/70 bg-blue-500/15 text-blue-700 dark:text-blue-300 shadow-glass"
        : "absolute rounded-xl border border-rose-500/40 bg-rose-500/10 text-rose-700 dark:text-rose-300 shadow-glass";
      box.dataset.zoneId = z.__id;
      box.style.left = `${z.x}px`;
      box.style.top = `${z.y}px`;
      box.style.width = `${z.w}px`;
      box.style.height = `${z.h}px`;
      box.style.cursor = "move";

      const label = document.createElement("div");
      label.className =
        "absolute -top-3 left-2 px-2 py-0.5 rounded-full text-[10px] font-black border border-rose-500/25 bg-white/70 dark:bg-slate-950/60";
      label.textContent = `${(z.match_role || z.name || "区域").toString().slice(0, 10)}${idx + 1}`;
      box.appendChild(label);

      const handle = document.createElement("div");
      handle.className = "absolute right-1 bottom-1 w-3 h-3 rounded bg-rose-500/70 border border-white/60 cursor-se-resize";
      handle.dataset.handle = "se";
      box.appendChild(handle);
      els.boxes.appendChild(box);
    });
  }

  function currentPageForPreview() {
    const zones = safeParseZones(els.jsonInput.value) || [];
    const p = zones[0] && zones[0].page;
    const page = Number.isFinite(Number(p)) ? Number(p) : 0;
    return Math.max(0, Math.floor(page));
  }

  function refreshBg() {
    const file = els.pdfSelect.value;
    state.pdfFile = file;
    state.orient = getOrient();
    const w = state.orient === "l" ? 842 : 595;
    const h = state.orient === "l" ? 595 : 842;
    els.bg.style.width = w + "px";
    els.bg.style.height = h + "px";
    els.canvasTransform.style.width = w + "px";
    els.canvasTransform.style.height = h + "px";
    els.dragLayer.style.width = w + "px";
    els.dragLayer.style.height = h + "px";
    if (!file) {
      els.bg.removeAttribute("src");
      return;
    }
    const page = currentPageForPreview();
    const url = `/admin/pdf_render/${encodeURIComponent(file)}?page=${encodeURIComponent(page)}&orient=${encodeURIComponent(
      state.orient
    )}&v=${Date.now()}`;
    els.bg.onerror = function () {
      if (els.bindHint) els.bindHint.textContent = "底图预览失败，请检查模板文件与页码";
      // fallback: retry first page once
      if (page !== 0) {
        els.bg.src = `/admin/pdf_render/${encodeURIComponent(file)}?page=0&orient=${encodeURIComponent(state.orient)}&v=${Date.now()}`;
      }
    };
    els.bg.onload = function () {
      if (els.bindHint) els.bindHint.textContent = "底图加载成功";
    };
    els.bg.src = url;
  }

  function startCreate(e) {
    if (e.button !== 0) return;
    if (e.target && e.target.closest && e.target.closest("[data-zone-id]")) return;
    if (!state.pdfFile) return;
    const p = pxToCanvasPoint(e.clientX, e.clientY);
    state.creating = { x0: p.x, y0: p.y, x1: p.x, y1: p.y };
    const ghost = document.createElement("div");
    ghost.id = "create-ghost";
    ghost.className = "absolute rounded-xl border border-blue-500/50 bg-blue-500/10";
    ghost.style.left = `${p.x}px`;
    ghost.style.top = `${p.y}px`;
    ghost.style.width = "1px";
    ghost.style.height = "1px";
    els.dragLayer.appendChild(ghost);
  }
  function moveCreate(e) {
    if (!state.creating) return;
    const p = pxToCanvasPoint(e.clientX, e.clientY);
    state.creating.x1 = p.x;
    state.creating.y1 = p.y;
    const x = Math.min(state.creating.x0, state.creating.x1);
    const y = Math.min(state.creating.y0, state.creating.y1);
    const w = Math.abs(state.creating.x1 - state.creating.x0);
    const h = Math.abs(state.creating.y1 - state.creating.y0);
    const ghost = document.getElementById("create-ghost");
    if (ghost) {
      ghost.style.left = `${x}px`;
      ghost.style.top = `${y}px`;
      ghost.style.width = `${w}px`;
      ghost.style.height = `${h}px`;
    }
  }
  function endCreate() {
    if (!state.creating) return;
    const x = Math.min(state.creating.x0, state.creating.x1);
    const y = Math.min(state.creating.y0, state.creating.y1);
    const w = Math.abs(state.creating.x1 - state.creating.x0);
    const h = Math.abs(state.creating.y1 - state.creating.y0);
    const ghost = document.getElementById("create-ghost");
    if (ghost) ghost.remove();
    state.creating = null;
    if (w < 6 || h < 6) return;
    const zone = normalizeZone({ name: "签名", page: currentPageForPreview(), x: Math.round(x), y: Math.round(y), w: Math.round(w), h: Math.round(h) });
    zone.__id = uuid();
    state.zones.push(zone);
    state.selectedZoneId = zone.__id;
    syncTextFromZones();
    pushUndoSnapshot();
    render();
  }

  function populateComponentSelect() {
    if (!els.componentSelect) return;
    els.componentSelect.innerHTML = `<option value="">-- 选择签名控件 --</option>`;
    state.loadedComponents.forEach((c, idx) => {
      const opt = document.createElement("option");
      opt.value = String(idx);
      opt.textContent = `${c.name || "未命名"} · ${c.component_type} · ${c.id}`;
      els.componentSelect.appendChild(opt);
    });
  }

  async function loadSignatureComponents() {
    const instanceId = (els.instanceIdInput?.value || "").trim();
    if (!instanceId) return window.alert("请先输入审批实例ID");
    try {
      const resp = await fetch(`/admin/signature_components?instance_id=${encodeURIComponent(instanceId)}`);
      const data = await resp.json();
      if (!resp.ok || !data.ok) return window.alert(data.msg || "读取控件失败");
      state.loadedComponents = Array.isArray(data.components) ? data.components : [];
      populateComponentSelect();
      if (els.bindHint) {
        els.bindHint.textContent =
          state.loadedComponents.length > 0
            ? `已读取 ${state.loadedComponents.length} 个签名控件`
            : "未找到签名控件";
      }
    } catch {
      window.alert("读取控件失败，请检查网络或实例ID");
    }
  }

  function fmtInstanceTime(ts) {
    const n = Number(ts || 0);
    if (!n) return "-";
    const d = new Date(n);
    const pad = (x) => String(x).padStart(2, "0");
    return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function populateInstanceSelect() {
    if (!els.instanceSelect) return;
    els.instanceSelect.innerHTML = `<option value="">-- 选择审批实例 --</option>`;
    state.loadedInstances.forEach((x, idx) => {
      const opt = document.createElement("option");
      opt.value = String(idx);
      const title = (x.title || "（无标题）").toString().slice(0, 36);
      opt.textContent = `${fmtInstanceTime(x.create_time)} · ${title}`;
      els.instanceSelect.appendChild(opt);
    });
  }

  async function loadRecentInstances() {
    const processCode = (els.pCode?.value || "").trim();
    if (!processCode) return window.alert("请先填写流程ID（ProcessCode）");

    let userid = (els.instanceUseridInput?.value || "").trim();
    if (!userid && window.dd && dd.ready && boot.corpId) {
      userid = await Promise.race([
        new Promise((resolve) => {
          dd.ready(function () {
            dd.runtime.permission.requestAuthCode({
              corpId: boot.corpId,
              onSuccess: async function (ret) {
                try {
                  const resp = await fetch(`/admin/userid_by_authcode?code=${encodeURIComponent(ret.code)}`);
                  const data = await resp.json();
                  if (resp.ok && data.ok && data.userid) resolve(data.userid);
                  else resolve("");
                } catch {
                  resolve("");
                }
              },
              onFail: function () {
                resolve("");
              },
            });
          });
        }),
        new Promise((resolve) => setTimeout(() => resolve(""), 2500)),
      ]);
      if (userid && els.instanceUseridInput) els.instanceUseridInput.value = userid;
    }
    const query = new URLSearchParams({ process_code: processCode, size: "20" });
    if (userid) query.set("userid", userid);

    try {
      const resp = await fetch(`/admin/process_instances?${query.toString()}`);
      const data = await resp.json();
      if (!resp.ok || !data.ok) return window.alert(data.msg || "读取实例失败");
      state.loadedInstances = Array.isArray(data.instances) ? data.instances : [];
      populateInstanceSelect();
      if (els.bindHint) {
        els.bindHint.textContent =
          state.loadedInstances.length > 0
            ? `已读取 ${state.loadedInstances.length} 条实例，选择后会自动加载控件`
            : "未找到最近实例";
      }
    } catch {
      window.alert("读取实例失败，请检查网络");
    }
  }

  function bindSelectedComponentToZone() {
    const idx = Number(els.componentSelect?.value || -1);
    if (!Number.isInteger(idx) || idx < 0 || idx >= state.loadedComponents.length) {
      return window.alert("请先选择签名控件");
    }
    if (!state.selectedZoneId) return window.alert("请先点击右侧某个区域");
    const zone = state.zones.find((z) => z.__id === state.selectedZoneId);
    if (!zone) return window.alert("选中区域不存在，请重试");

    const c = state.loadedComponents[idx];
    zone.widget_id = String(c.id || "");
    zone.match_role = String(c.name || "");
    if (!zone.name) zone.name = String(c.name || "签名");
    syncTextFromZones();
    pushUndoSnapshot();
    render();
    if (els.bindHint) els.bindHint.textContent = `已绑定：${c.name || c.id}`;
  }

  async function loadProcessOptions(keyword) {
    const q = (keyword || "").trim();
    const resp = await fetch(`/admin/search_processes?q=${encodeURIComponent(q)}`);
    const data = await resp.json();
    return Array.isArray(data.results) ? data.results : [];
  }

  function bindNativeSearchFallback() {
    if (!els.procSearch) return;
    const fill = async (keyword = "") => {
      try {
        const list = await loadProcessOptions(keyword);
        els.procSearch.innerHTML = `<option value="">-- 选择流程 --</option>`;
        list.forEach((item) => {
          const opt = document.createElement("option");
          opt.value = item.id || "";
          opt.textContent = `${item.text || ""}  ${item.id || ""}`;
          els.procSearch.appendChild(opt);
        });
      } catch {
        // keep current options
      }
    };
    fill("");
    els.procSearch.addEventListener("change", function () {
      const code = els.procSearch.value || "";
      const text = (els.procSearch.options[els.procSearch.selectedIndex] || {}).textContent || "";
      els.pCode.value = code;
      els.pName.value = text.trim();
      if (code) LS.pushHistory({ id: code, text: text.trim() });
    });
  }

  function bindSelect2() {
    if (!els.procSearch) return;
    try {
      if (!window.$ || !$.fn || typeof $.fn.select2 !== "function") throw new Error("select2 unavailable");
      $(els.procSearch)
        .select2({
          ajax: {
            url: "/admin/search_processes",
            dataType: "json",
            delay: 250,
            processResults: (data) => ({ results: (data && data.results) || [] }),
          },
          placeholder: "输入流程名称关键字...",
          width: "100%",
        })
        .on("select2:select", function (e) {
          const item = e.params.data || {};
          els.pCode.value = item.id || "";
          els.pName.value = item.text || "";
          LS.pushHistory(item);
        });
    } catch {
      bindNativeSearchFallback();
      if (els.bindHint) els.bindHint.textContent = "流程搜索已切换兼容模式";
    }

    els.historyBtn?.addEventListener("click", function () {
      const hist = LS.loadHistory();
      if (!hist.length) return window.alert("暂无历史记录");
      const lines = hist.map((h, i) => `${i + 1}. ${h.text || "（未命名）"}  ${h.id}`).join("\n");
      const idx = window.prompt("选择历史记录序号：\n" + lines, "1");
      const n = Number(idx);
      if (!Number.isFinite(n) || n < 1 || n > hist.length) return;
      const pick = hist[n - 1];
      els.pCode.value = pick.id || "";
      els.pName.value = pick.text || "";
    });
  }

  function formatTime(ms) {
    const ts = Number(ms || 0);
    if (!ts) return "-";
    const d = new Date(ts);
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function actionLabel(action) {
    const a = String(action || "").toLowerCase();
    if (a === "save") return "保存";
    if (a === "delete") return "删除";
    if (a === "rollback") return "回滚";
    return action || "未知";
  }

  function renderVersionOptions() {
    if (!els.versionSelect) return;
    const current = els.versionSelect.value;
    els.versionSelect.innerHTML = `<option value="">-- 选择历史版本 --</option>`;
    const filtered = state.versions.filter((v) => {
      const actionOk = state.versionFilterAction === "all" || String(v.action || "") === state.versionFilterAction;
      if (!actionOk) return false;
      const kw = state.versionKeyword.trim().toLowerCase();
      if (!kw) return true;
      const hay = `${v.id || ""} ${v.reason || ""} ${v.operator || ""}`.toLowerCase();
      return hay.includes(kw);
    });
    filtered.forEach((v) => {
      const op = (v && v.operator) || "unknown";
      const opt = document.createElement("option");
      opt.value = v.id;
      opt.textContent = `${actionLabel(v.action)} · ${formatTime(v.saved_at_ms)} · ${op}`;
      els.versionSelect.appendChild(opt);
    });
    if (current && filtered.some((v) => v.id === current)) els.versionSelect.value = current;
    else els.versionSelect.value = "";
  }

  function showVersionDetail(versionId) {
    if (!els.versionDetail) return;
    if (!versionId) {
      els.versionDetail.classList.add("hidden");
      return;
    }
    const v = state.versions.find((x) => x.id === versionId);
    if (!v) {
      els.versionDetail.classList.add("hidden");
      return;
    }
    const reason = (v.reason || "").trim();
    if (els.versionDetailTitle) {
      els.versionDetailTitle.textContent = `${actionLabel(v.action)} · ${v.id}`;
    }
    if (els.versionDetailMeta) {
      els.versionDetailMeta.textContent = `时间：${formatTime(v.saved_at_ms)} ｜ 操作人：${v.operator || "unknown"}${
        reason ? ` ｜ 说明：${reason}` : ""
      }`;
    }
    els.versionDetail.classList.remove("hidden");
  }

  async function loadVersions() {
    const processCode = (els.pCode?.value || "").trim();
    if (!processCode) {
      state.versions = [];
      renderVersionOptions();
      showVersionDetail("");
      return;
    }
    try {
      const resp = await fetch(`/admin/versions?code=${encodeURIComponent(processCode)}`);
      const data = await resp.json();
      state.versions = Array.isArray(data.versions) ? data.versions : [];
      renderVersionOptions();
      showVersionDetail(els.versionSelect?.value || "");
    } catch {
      // keep current options silently
    }
  }

  window.AppCore.onReady(function () {
    bindSelect2();
    renderVersionOptions();
    showVersionDetail("");
    els.beautifyBtn?.addEventListener("click", () => {
      const parsed = safeParseZones(els.jsonInput.value);
      if (!parsed) return window.alert("JSON 格式错误");
      els.jsonInput.value = zonesToText(parsed);
      syncZonesFromText();
      pushUndoSnapshot();
      render();
    });
    els.clearBtn?.addEventListener("click", () => {
      state.zones = [];
      syncTextFromZones();
      pushUndoSnapshot();
      render();
    });
    els.undoBtn?.addEventListener("click", doUndo);
    els.redoBtn?.addEventListener("click", doRedo);
    els.rollbackBtn?.addEventListener("click", async () => {
      const processCode = (els.pCode?.value || "").trim();
      const versionId = (els.versionSelect?.value || "").trim();
      if (!processCode || !versionId) return window.alert("请先选择流程和版本");
      const ok = window.confirm(`确认回滚到版本 ${versionId} 吗？`);
      if (!ok) return;
      const body = new URLSearchParams({ process_code: processCode, version_id: versionId });
      const resp = await fetch("/admin/rollback", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
        body: body.toString(),
      });
      const data = await resp.json();
      if (!resp.ok || !data.ok) return window.alert(data.msg || "回滚失败");
      window.alert("回滚成功，正在刷新版本列表");
      await loadVersions();
    });
    els.versionSelect?.addEventListener("change", () => {
      showVersionDetail(els.versionSelect.value || "");
    });
    els.loadComponentsBtn?.addEventListener("click", loadSignatureComponents);
    els.loadInstancesBtn?.addEventListener("click", loadRecentInstances);
    els.instanceSelect?.addEventListener("change", async (e) => {
      const idx = Number(e.target.value || -1);
      if (!Number.isInteger(idx) || idx < 0 || idx >= state.loadedInstances.length) return;
      const ins = state.loadedInstances[idx];
      if (els.instanceIdInput) els.instanceIdInput.value = ins.id || "";
      await loadSignatureComponents();
    });
    els.bindComponentBtn?.addEventListener("click", bindSelectedComponentToZone);
    els.versionActionFilter?.addEventListener("change", (e) => {
      state.versionFilterAction = e.target.value || "all";
      renderVersionOptions();
      showVersionDetail(els.versionSelect.value || "");
    });
    els.versionKeyword?.addEventListener("input", (e) => {
      state.versionKeyword = e.target.value || "";
      renderVersionOptions();
      showVersionDetail(els.versionSelect.value || "");
    });
    els.pCode?.addEventListener("blur", loadVersions);

    els.pdfSelect?.addEventListener("change", () => {
      refreshBg();
      if (syncZonesFromText()) render();
    });
    els.orientRadios.forEach((r) => r.addEventListener("change", refreshBg));
    els.jsonInput?.addEventListener("input", () => {
      if (syncZonesFromText()) {
        pushUndoSnapshot();
        render();
      }
    });
    window.addEventListener("keydown", (e) => {
      const z = e.key.toLowerCase() === "z";
      if (!z || !(e.ctrlKey || e.metaKey)) return;
      e.preventDefault();
      if (e.shiftKey) doRedo();
      else doUndo();
    });

    els.canvasTransform?.addEventListener("mousedown", startCreate);
    window.addEventListener("mousemove", (e) => moveCreate(e));
    window.addEventListener("mouseup", () => endCreate());
    els.boxes?.addEventListener("click", (e) => {
      const box = e.target && e.target.closest && e.target.closest("[data-zone-id]");
      if (!box) return;
      state.selectedZoneId = box.getAttribute("data-zone-id");
      render();
      if (els.bindHint) els.bindHint.textContent = "已选中区域，可绑定控件";
    });
    els.workspace?.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        const next = clamp(state.scale * (e.deltaY > 0 ? 0.92 : 1.08), state.minScale, state.maxScale);
        state.scale = next;
        setTransform();
      },
      { passive: false }
    );

    state.orient = getOrient();
    setTransform();
    refreshBg();
    if (syncZonesFromText()) render();
    pushUndoSnapshot();
    refreshUndoRedoButtons();
    loadVersions();
  });
})();

