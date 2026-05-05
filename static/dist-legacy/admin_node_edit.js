(() => {
  // src/js/admin_node_edit.js
  (function() {
    function parseJsonSafe(text, fallback) {
      try {
        const v = JSON.parse(text || "");
        return v;
      } catch (e) {
        return fallback;
      }
    }
    function fmtJson(el, fallback) {
      const v = parseJsonSafe(el.value, fallback);
      if (v === null || v === void 0) return false;
      el.value = JSON.stringify(v, null, 2);
      return true;
    }
    function toNum(v, dft) {
      const s = String(v != null ? v : "").trim();
      if (!s) return dft;
      const n = Number(s);
      return Number.isFinite(n) ? n : dft;
    }
    window.AppCore.onReady(function() {
      var _a, _b, _c, _d, _e, _f, _g;
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
        autoImportStatus: document.getElementById("auto-import-status")
      };
      function getZones() {
        var _a2;
        const v = parseJsonSafe(((_a2 = el.zones) == null ? void 0 : _a2.value) || "[]", []);
        return Array.isArray(v) ? v : [];
      }
      function setZones(v) {
        if (!el.zones) return;
        el.zones.value = JSON.stringify(v, null, 2);
      }
      function getProfiles() {
        var _a2;
        const v = parseJsonSafe(((_a2 = el.profiles) == null ? void 0 : _a2.value) || "{}", {});
        return v && typeof v === "object" && !Array.isArray(v) ? v : {};
      }
      function setProfiles(v) {
        if (!el.profiles) return;
        el.profiles.value = JSON.stringify(v, null, 2);
      }
      function baseZone(bindType) {
        var _a2, _b2, _c2, _d2, _e2, _f2, _g2;
        return {
          bind_type: bindType,
          name: bindType === "node_date" ? "\u4F1A\u7B7E\u5BA1\u6279\u65E5\u671F" : "\u4F1A\u7B7E\u7B7E\u5B57",
          page: -1,
          x: toNum((_a2 = el.qX) == null ? void 0 : _a2.value, 430),
          y: toNum((_b2 = el.qY) == null ? void 0 : _b2.value, bindType === "node_date" ? 548 : 510),
          w: toNum((_c2 = el.qW) == null ? void 0 : _c2.value, bindType === "node_date" ? 80 : 60),
          h: toNum((_d2 = el.qH) == null ? void 0 : _d2.value, bindType === "node_date" ? 16 : 35),
          activity_id: (((_e2 = el.qActivityId) == null ? void 0 : _e2.value) || "").trim(),
          match_by: (((_f2 = el.qMatchBy) == null ? void 0 : _f2.value) || "dept_name").trim(),
          match_rule: (((_g2 = el.qDeptRule) == null ? void 0 : _g2.value) || "").trim()
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
        const s = /* @__PURE__ */ new Set();
        (arr || []).forEach((x) => {
          const v = String(x || "").trim();
          if (v) s.add(v);
        });
        return Array.from(s);
      }
      async function autoImportRecent() {
        var _a2, _b2, _c2, _d2, _e2, _f2, _g2;
        const processCode = (((_a2 = document.getElementById("node-process-code")) == null ? void 0 : _a2.value) || "").trim();
        if (!processCode) return window.alert("\u8BF7\u5148\u586B\u5199\u6D41\u7A0B Code");
        const size = Math.max(1, Math.min(Number(((_b2 = el.autoImportSize) == null ? void 0 : _b2.value) || 1) || 1, 10));
        if (el.autoImportStatus) el.autoImportStatus.textContent = "\u6B63\u5728\u5BFC\u5165...";
        try {
          const resp = await fetch(`/admin/process_instances?process_code=${encodeURIComponent(processCode)}&size=${encodeURIComponent(String(size))}`);
          const data = await resp.json();
          if (!resp.ok || !data.ok) {
            if (el.autoImportStatus) el.autoImportStatus.textContent = data.msg || "\u5BFC\u5165\u5931\u8D25";
            return window.alert(data.msg || "\u8BFB\u53D6\u5B9E\u4F8B\u5931\u8D25");
          }
          const instances = Array.isArray(data.instances) ? data.instances : [];
          if (!instances.length) {
            if (el.autoImportStatus) el.autoImportStatus.textContent = "\u672A\u627E\u5230\u5B9E\u4F8B";
            return window.alert("\u672A\u627E\u5230\u6700\u8FD1\u5B9E\u4F8B");
          }
          const insId = instances[0].id;
          const [taskResp, sigResp] = await Promise.all([
            fetch(`/admin/instance_tasks?instance_id=${encodeURIComponent(insId)}`),
            fetch(`/admin/signature_components?instance_id=${encodeURIComponent(insId)}`)
          ]);
          const taskData = await taskResp.json();
          const sigData = await sigResp.json();
          if (!taskResp.ok || !taskData.ok) throw new Error(taskData.msg || "\u8BFB\u53D6 tasks \u5931\u8D25");
          if (!sigResp.ok || !sigData.ok) throw new Error(sigData.msg || "\u8BFB\u53D6\u7B7E\u5B57\u63A7\u4EF6\u5931\u8D25");
          const tasks = Array.isArray(taskData.tasks) ? taskData.tasks : [];
          const sigComps = Array.isArray(sigData.components) ? sigData.components : [];
          const signatureWidgetIds = sigComps.map((c) => String(c.id || "").trim()).filter(Boolean);
          const byActivity = groupByActivity(tasks);
          const activityIds = Object.keys(byActivity);
          if (!activityIds.length) {
            if (el.autoImportStatus) el.autoImportStatus.textContent = "\u672A\u53D1\u73B0\u5DF2\u5B8C\u6210\u8282\u70B9\u4EFB\u52A1";
            return window.alert("\u672A\u53D1\u73B0\u5DF2\u5B8C\u6210\u8282\u70B9\u4EFB\u52A1");
          }
          const x = toNum((_c2 = el.qX) == null ? void 0 : _c2.value, 430);
          const w = toNum((_d2 = el.qW) == null ? void 0 : _d2.value, 60);
          const ySig = toNum((_e2 = el.qY) == null ? void 0 : _e2.value, 510);
          const hSig = toNum((_f2 = el.qH) == null ? void 0 : _f2.value, 35);
          const yDate = toNum((_g2 = el.qY) == null ? void 0 : _g2.value, 548);
          const zones = [];
          const userProfiles = {};
          activityIds.forEach((aid, idx) => {
            const rows = byActivity[aid] || [];
            const userids = uniq(rows.map((r) => r.userid));
            zones.push({
              bind_type: "node_date",
              name: "\u4F1A\u7B7E\u5BA1\u6279\u65E5\u671F",
              page: -1,
              x,
              y: yDate,
              w: 80,
              h: 16,
              activity_id: aid,
              match_by: "userid",
              match_rule: userids,
              date_format: "YYYY-MM-DD",
              date_pick: "last"
            });
            const widgetId = signatureWidgetIds.length ? signatureWidgetIds[idx % signatureWidgetIds.length] : "";
            zones.push({
              bind_type: "node_signature",
              name: "\u4F1A\u7B7E\u7B7E\u5B57",
              page: -1,
              x,
              y: ySig,
              w,
              h: hSig,
              activity_id: aid,
              match_by: "userid",
              match_rule: userids,
              widget_id: widgetId || "",
              sign_pick: "last",
              fallback: true
            });
            userids.forEach((u) => {
              userProfiles[u] = userProfiles[u] || { dept_name: "", title: "", signature_widget_id: "" };
            });
          });
          el.zones.value = JSON.stringify(zones, null, 2);
          el.profiles.value = JSON.stringify(userProfiles, null, 2);
          if (el.autoImportStatus) el.autoImportStatus.textContent = `\u5DF2\u751F\u6210 ${zones.length} \u4E2A node_zone`;
          window.alert(`\u5DF2\u5BFC\u5165\u6700\u8FD1\u5B9E\u4F8B\uFF1A${insId}
\u751F\u6210 node_zones\uFF1A${zones.length}`);
        } catch (e) {
          if (el.autoImportStatus) el.autoImportStatus.textContent = "\u5BFC\u5165\u5931\u8D25";
          window.alert((e == null ? void 0 : e.message) || "\u5BFC\u5165\u5931\u8D25");
        }
      }
      (_a = el.qAddSign) == null ? void 0 : _a.addEventListener("click", function() {
        var _a2;
        const zones = getZones();
        const z = baseZone("node_signature");
        z.widget_id = (((_a2 = el.qWidgetId) == null ? void 0 : _a2.value) || "").trim();
        z.sign_pick = "last";
        zones.push(z);
        setZones(zones);
      });
      (_b = el.qAddDate) == null ? void 0 : _b.addEventListener("click", function() {
        const zones = getZones();
        const z = baseZone("node_date");
        z.date_format = "YYYY-MM-DD";
        z.date_pick = "last";
        zones.push(z);
        setZones(zones);
      });
      (_c = el.qAddFallback) == null ? void 0 : _c.addEventListener("click", function() {
        const zones = getZones();
        const z = baseZone("node_signature");
        z.name = "\u4F1A\u7B7E\u515C\u5E95";
        z.fallback = true;
        z.sign_pick = "last";
        delete z.match_by;
        delete z.match_rule;
        zones.push(z);
        setZones(zones);
      });
      (_d = el.qFmtZones) == null ? void 0 : _d.addEventListener("click", function() {
        if (!el.zones) return;
        if (!fmtJson(el.zones, [])) window.alert("node_zones_json \u4E0D\u662F\u5408\u6CD5 JSON");
      });
      (_e = el.qAddUser) == null ? void 0 : _e.addEventListener("click", function() {
        var _a2, _b2, _c2, _d2;
        const userid = (((_a2 = el.qUserid) == null ? void 0 : _a2.value) || "").trim();
        if (!userid) return window.alert("\u8BF7\u5148\u8F93\u5165 userid");
        const profiles = getProfiles();
        profiles[userid] = {
          dept_name: (((_b2 = el.qUserDept) == null ? void 0 : _b2.value) || "").trim(),
          title: (((_c2 = el.qUserTitle) == null ? void 0 : _c2.value) || "").trim(),
          signature_widget_id: (((_d2 = el.qUserWidgetId) == null ? void 0 : _d2.value) || "").trim()
        };
        setProfiles(profiles);
      });
      (_f = el.qFmtProfiles) == null ? void 0 : _f.addEventListener("click", function() {
        if (!el.profiles) return;
        if (!fmtJson(el.profiles, {})) window.alert("user_profiles_json \u4E0D\u662F\u5408\u6CD5 JSON");
      });
      (_g = el.autoImportBtn) == null ? void 0 : _g.addEventListener("click", autoImportRecent);
    });
  })();
})();
