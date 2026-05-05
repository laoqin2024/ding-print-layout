(function () {
  function parseJsonSafe(text, fallback) {
    try {
      const v = JSON.parse(text || "");
      return v;
    } catch {
      return fallback;
    }
  }

  function fmtJson(el, fallback) {
    const v = parseJsonSafe(el.value, fallback);
    if (v === null || v === undefined) return false;
    el.value = JSON.stringify(v, null, 2);
    return true;
  }

  function toNum(v, dft) {
    const s = String(v ?? "").trim();
    if (!s) return dft;
    const n = Number(s);
    return Number.isFinite(n) ? n : dft;
  }

  window.AppCore.onReady(function () {
    const el = {
      zones: document.getElementById("node-zones-json"),
      profiles: document.getElementById("user-profiles-json"),
      qActivityId: document.getElementById("quick-activity-id"),
      qWidgetId: document.getElementById("quick-widget-id"),
      qDeptRule: document.getElementById("quick-dept-rule"),
      qMatchBy: document.getElementById("quick-match-by"),
      qX: document.getElementById("quick-x"),
      qY: document.getElementById("quick-y"),
      qW: document.getElementById("quick-w"),
      qH: document.getElementById("quick-h"),
      qAddSign: document.getElementById("quick-add-sign-zone"),
      qAddDate: document.getElementById("quick-add-date-zone"),
      qAddFallback: document.getElementById("quick-add-fallback-zone"),
      qFmtZones: document.getElementById("quick-format-zones"),
      qUserid: document.getElementById("quick-userid"),
      qUserDept: document.getElementById("quick-user-dept"),
      qUserTitle: document.getElementById("quick-user-title"),
      qUserWidgetId: document.getElementById("quick-user-widget-id"),
      qAddUser: document.getElementById("quick-add-user-profile"),
      qFmtProfiles: document.getElementById("quick-format-profiles"),

      autoImportSize: document.getElementById("auto-import-size"),
      autoImportBtn: document.getElementById("auto-import-recent"),
      autoImportStatus: document.getElementById("auto-import-status"),
    };

    function getZones() {
      const v = parseJsonSafe(el.zones?.value || "[]", []);
      return Array.isArray(v) ? v : [];
    }

    function setZones(v) {
      if (!el.zones) return;
      el.zones.value = JSON.stringify(v, null, 2);
    }

    function getProfiles() {
      const v = parseJsonSafe(el.profiles?.value || "{}", {});
      return v && typeof v === "object" && !Array.isArray(v) ? v : {};
    }

    function setProfiles(v) {
      if (!el.profiles) return;
      el.profiles.value = JSON.stringify(v, null, 2);
    }

    function baseZone(bindType) {
      return {
        bind_type: bindType,
        name: bindType === "node_date" ? "会签审批日期" : "会签签字",
        page: -1,
        x: toNum(el.qX?.value, 430),
        y: toNum(el.qY?.value, bindType === "node_date" ? 548 : 510),
        w: toNum(el.qW?.value, bindType === "node_date" ? 80 : 60),
        h: toNum(el.qH?.value, bindType === "node_date" ? 16 : 35),
        activity_id: (el.qActivityId?.value || "").trim(),
        match_by: (el.qMatchBy?.value || "dept_name").trim(),
        match_rule: (el.qDeptRule?.value || "").trim(),
      };
    }

    function groupByActivity(tasks) {
      const out = {};
      (tasks || []).forEach((t) => {
        const aid = String(t.activity_id || "").trim();
        if (!aid) return;
        out[aid] = out[aid] || [];
        out[aid].push(t);
      });
      return out;
    }

    function uniq(arr) {
      const s = new Set();
      (arr || []).forEach((x) => {
        const v = String(x || "").trim();
        if (v) s.add(v);
      });
      return Array.from(s);
    }

    async function autoImportRecent() {
      const processCode = (document.getElementById("node-process-code")?.value || "").trim();
      if (!processCode) return window.alert("请先填写流程 Code");
      const size = Math.max(1, Math.min(Number(el.autoImportSize?.value || 1) || 1, 10));
      if (el.autoImportStatus) el.autoImportStatus.textContent = "正在导入...";
      try {
        const resp = await fetch(`/admin/process_instances?process_code=${encodeURIComponent(processCode)}&size=${encodeURIComponent(String(size))}`);
        const data = await resp.json();
        if (!resp.ok || !data.ok) {
          if (el.autoImportStatus) el.autoImportStatus.textContent = data.msg || "导入失败";
          return window.alert(data.msg || "读取实例失败");
        }
        const instances = Array.isArray(data.instances) ? data.instances : [];
        if (!instances.length) {
          if (el.autoImportStatus) el.autoImportStatus.textContent = "未找到实例";
          return window.alert("未找到最近实例");
        }
        const insId = instances[0].id;
        const [taskResp, sigResp] = await Promise.all([
          fetch(`/admin/instance_tasks?instance_id=${encodeURIComponent(insId)}`),
          fetch(`/admin/signature_components?instance_id=${encodeURIComponent(insId)}`),
        ]);
        const taskData = await taskResp.json();
        const sigData = await sigResp.json();
        if (!taskResp.ok || !taskData.ok) throw new Error(taskData.msg || "读取 tasks 失败");
        if (!sigResp.ok || !sigData.ok) throw new Error(sigData.msg || "读取签字控件失败");

        const tasks = Array.isArray(taskData.tasks) ? taskData.tasks : [];
        const sigComps = Array.isArray(sigData.components) ? sigData.components : [];
        const signatureWidgetIds = sigComps.map((c) => String(c.id || "").trim()).filter(Boolean);

        const byActivity = groupByActivity(tasks);
        const activityIds = Object.keys(byActivity);
        if (!activityIds.length) {
          if (el.autoImportStatus) el.autoImportStatus.textContent = "未发现已完成节点任务";
          return window.alert("未发现已完成节点任务");
        }

        const x = toNum(el.qX?.value, 430);
        const w = toNum(el.qW?.value, 60);
        const ySig = toNum(el.qY?.value, 510);
        const hSig = toNum(el.qH?.value, 35);
        const yDate = toNum(el.qY?.value, 548);

        const zones = [];
        const userProfiles = {};

        activityIds.forEach((aid, idx) => {
          const rows = byActivity[aid] || [];
          const userids = uniq(rows.map((r) => r.userid));

          // date zone
          zones.push({
            bind_type: "node_date",
            name: "会签审批日期",
            page: -1,
            x: x,
            y: yDate,
            w: 80,
            h: 16,
            activity_id: aid,
            match_by: "userid",
            match_rule: userids,
            date_format: "YYYY-MM-DD",
            date_pick: "last",
          });

          // signature zone (widget_id left as placeholder; user can map later)
          const widgetId = signatureWidgetIds.length ? signatureWidgetIds[idx % signatureWidgetIds.length] : "";
          zones.push({
            bind_type: "node_signature",
            name: "会签签字",
            page: -1,
            x: x,
            y: ySig,
            w: w,
            h: hSig,
            activity_id: aid,
            match_by: "userid",
            match_rule: userids,
            widget_id: widgetId || "",
            sign_pick: "last",
            fallback: true,
          });

          userids.forEach((u) => {
            userProfiles[u] = userProfiles[u] || { dept_name: "", title: "", signature_widget_id: "" };
          });
        });

        el.zones.value = JSON.stringify(zones, null, 2);
        el.profiles.value = JSON.stringify(userProfiles, null, 2);
        if (el.autoImportStatus) el.autoImportStatus.textContent = `已生成 ${zones.length} 个 node_zone`;
        window.alert(`已导入最近实例：${insId}\n生成 node_zones：${zones.length}`);
      } catch (e) {
        if (el.autoImportStatus) el.autoImportStatus.textContent = "导入失败";
        window.alert(e?.message || "导入失败");
      }
    }

    el.qAddSign?.addEventListener("click", function () {
      const zones = getZones();
      const z = baseZone("node_signature");
      z.widget_id = (el.qWidgetId?.value || "").trim();
      z.sign_pick = "last";
      zones.push(z);
      setZones(zones);
    });

    el.qAddDate?.addEventListener("click", function () {
      const zones = getZones();
      const z = baseZone("node_date");
      z.date_format = "YYYY-MM-DD";
      z.date_pick = "last";
      zones.push(z);
      setZones(zones);
    });

    el.qAddFallback?.addEventListener("click", function () {
      const zones = getZones();
      const z = baseZone("node_signature");
      z.name = "会签兜底";
      z.fallback = true;
      z.sign_pick = "last";
      delete z.match_by;
      delete z.match_rule;
      zones.push(z);
      setZones(zones);
    });

    el.qFmtZones?.addEventListener("click", function () {
      if (!el.zones) return;
      if (!fmtJson(el.zones, [])) window.alert("node_zones_json 不是合法 JSON");
    });

    el.qAddUser?.addEventListener("click", function () {
      const userid = (el.qUserid?.value || "").trim();
      if (!userid) return window.alert("请先输入 userid");
      const profiles = getProfiles();
      profiles[userid] = {
        dept_name: (el.qUserDept?.value || "").trim(),
        title: (el.qUserTitle?.value || "").trim(),
        signature_widget_id: (el.qUserWidgetId?.value || "").trim(),
      };
      setProfiles(profiles);
    });

    el.qFmtProfiles?.addEventListener("click", function () {
      if (!el.profiles) return;
      if (!fmtJson(el.profiles, {})) window.alert("user_profiles_json 不是合法 JSON");
    });

    el.autoImportBtn?.addEventListener("click", autoImportRecent);
  });
})();
